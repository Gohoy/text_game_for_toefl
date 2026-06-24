import json
import subprocess
from pathlib import Path

import pytest

from toefl_rpg.ai.codex_cli import CodexCliProvider
from toefl_rpg.ai.codex_cli import CodexCliProviderError
from toefl_rpg.ai.contract import AIProviderUnavailable
from toefl_rpg.ai.contract import ContentDraftRequest
from toefl_rpg.ai.contract import NPCDialogueRequest
from toefl_rpg.ai.contract import PlayerSentenceInterpretationRequest
from toefl_rpg.ai.contract import ReviewAnswerEvaluationRequest
from toefl_rpg.ai.contract import RoomNarrationRequest
from toefl_rpg.ai.contract import SentenceQualityRequest
from toefl_rpg.ai.contract import TurnFeedbackRequest
from toefl_rpg.ai.contract import VocabularyExplanationRequest


def test_codex_cli_provider_builds_bounded_exec_command(tmp_path) -> None:
    calls = []

    def fake_runner(command, **kwargs):
        calls.append((command, kwargs))
        output_path = Path(command[command.index("--output-last-message") + 1])
        schema_path = Path(command[command.index("--output-schema") + 1])
        assert schema_path.exists()
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        assert schema["additionalProperties"] is False
        assert set(schema["required"]) == set(schema["properties"])
        output_path.write_text(
            json.dumps(
                {
                    "narration": "You collect the sample carefully.",
                    "sentence_feedback": "Use 'to collect' after 'want'.",
                    "suggested_sentence": "I want to collect the fungus sample.",
                    "vocabulary_notes": ["fungus: a simple organism."],
                }
            ),
            encoding="utf-8",
        )
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

    provider = CodexCliProvider(
        executable="codex-test",
        timeout_seconds=7,
        cwd=tmp_path,
        runner=fake_runner,
    )
    request = TurnFeedbackRequest(
        player_sentence="I want collect the fungus sample.",
        location_id="fungus_grove",
        deterministic_action="collect",
        deterministic_result="You collect fungus sample.",
        target_words=["fungus"],
        practiced_words=["fungus"],
    )

    response = provider.generate_turn_feedback(request)

    command, kwargs = calls[0]
    assert command[:2] == ["codex-test", "exec"]
    assert "--output-schema" in command
    assert "--output-last-message" in command
    assert "--sandbox" in command
    assert "read-only" in command
    assert "--ask-for-approval" not in command
    assert kwargs["timeout"] == 7
    assert kwargs["cwd"] == str(tmp_path)
    assert kwargs["input"].startswith("You are the required AI agent")
    assert response.suggested_sentence == "I want to collect the fungus sample."


def test_codex_cli_provider_parses_stdout_when_output_file_is_absent() -> None:
    def fake_runner(command, **kwargs):
        return subprocess.CompletedProcess(
            command,
            0,
            stdout=json.dumps(
                {
                    "word": "mimicry",
                    "plain_meaning": "copying another living thing's appearance",
                    "example_sentence": "The insect uses mimicry to survive.",
                    "memory_hint": "Mimicry means imitate.",
                }
            ),
            stderr="",
        )

    provider = CodexCliProvider(runner=fake_runner)

    response = provider.explain_vocabulary(
        VocabularyExplanationRequest(word="mimicry", theme="biology")
    )

    assert response.word == "mimicry"
    assert response.memory_hint


def test_codex_cli_provider_supports_player_sentence_interpretation() -> None:
    def fake_runner(command, **kwargs):
        assert "structured player sentence interpretation" in kwargs["input"]
        assert '"visible_items": [' in kwargs["input"]
        return subprocess.CompletedProcess(
            command,
            0,
            stdout=json.dumps(
                {
                    "action": "collect",
                    "target": "fungus sample",
                    "confidence": 0.82,
                    "reason": "The player asks to collect the visible sample.",
                }
            ),
            stderr="",
        )

    provider = CodexCliProvider(runner=fake_runner)
    request = PlayerSentenceInterpretationRequest(
        player_sentence="I want collect a sample with the microscope.",
        location_id="fungus_grove",
        room_name="Fungus Grove",
        exits={"south": "research_camp"},
        visible_items=["fungus sample"],
        visible_npcs=[],
        visible_enemies=[],
        target_words=["fungus", "symbiosis", "vital"],
    )

    response = provider.interpret_player_sentence(request)

    assert response.action == "collect"
    assert response.target == "fungus sample"
    assert response.confidence == 0.82


def test_codex_cli_provider_supports_sentence_quality_precheck() -> None:
    def fake_runner(command, **kwargs):
        assert "sentence quality pre-check" in kwargs["input"]
        assert '"player_sentence": "go north"' in kwargs["input"]
        return subprocess.CompletedProcess(
            command,
            0,
            stdout=json.dumps(
                {
                    "is_complete_and_correct": False,
                    "explanation": "This is a command fragment, not a complete sentence.",
                    "suggested_sentence": "I go north to the fungus grove.",
                }
            ),
            stderr="",
        )

    provider = CodexCliProvider(runner=fake_runner)
    request = SentenceQualityRequest(
        player_sentence="go north",
        location_id="research_camp",
        room_name="Research Camp",
        target_words=["organism", "species", "evolve"],
    )

    response = provider.evaluate_sentence_quality(request)

    assert response.is_complete_and_correct is False
    assert response.suggested_sentence == "I go north to the fungus grove."


def test_codex_cli_provider_supports_npc_dialogue() -> None:
    def fake_runner(command, **kwargs):
        assert "NPC dialogue" in kwargs["input"]
        assert '"quest_progress": "Biology Investigation 0/3"' in kwargs["input"]
        return subprocess.CompletedProcess(
            command,
            0,
            stdout=json.dumps(
                {
                    "speaker": "Dr. Lin",
                    "line": "Start with the fungus sample, then use the microscope.",
                    "vocabulary_notes": ["fungus: a living growth."],
                }
            ),
            stderr="",
        )

    provider = CodexCliProvider(runner=fake_runner)
    request = NPCDialogueRequest(
        npc_name="Dr. Lin",
        location_id="research_camp",
        room_name="Research Camp",
        quest_progress="Biology Investigation 0/3",
        visible_items=["field notebook"],
        visible_npcs=["Dr. Lin"],
        visible_enemies=[],
        target_words=["organism", "species", "evolve"],
    )

    response = provider.generate_npc_dialogue(request)

    assert response.speaker == "Dr. Lin"
    assert "fungus sample" in response.line
    assert response.vocabulary_notes == ["fungus: a living growth."]


def test_codex_cli_provider_supports_room_narration() -> None:
    def fake_runner(command, **kwargs):
        assert "room narration" in kwargs["input"]
        assert '"room_description": "Pale mushrooms cover old roots."' in kwargs["input"]
        return subprocess.CompletedProcess(
            command,
            0,
            stdout=json.dumps(
                {
                    "location_id": "fungus_grove",
                    "narration": "Pale fungus threads wind around the roots.",
                    "focus_hint": "The fungus sample is ready to collect.",
                    "vocabulary_notes": ["symbiosis: living together."],
                }
            ),
            stderr="",
        )

    provider = CodexCliProvider(runner=fake_runner)
    request = RoomNarrationRequest(
        location_id="fungus_grove",
        room_name="Fungus Grove",
        room_description="Pale mushrooms cover old roots.",
        quest_progress="Biology Investigation 0/3",
        exits={"south": "research_camp"},
        visible_items=["fungus sample"],
        visible_npcs=[],
        visible_enemies=[],
        target_words=["fungus", "symbiosis", "vital"],
    )

    response = provider.generate_room_narration(request)

    assert response.location_id == "fungus_grove"
    assert "fungus" in response.narration
    assert response.focus_hint == "The fungus sample is ready to collect."
    assert response.vocabulary_notes == ["symbiosis: living together."]


def test_codex_cli_provider_supports_review_answer_evaluation() -> None:
    def fake_runner(command, **kwargs):
        assert "review answer evaluation" in kwargs["input"]
        assert '"word": "fungus"' in kwargs["input"]
        return subprocess.CompletedProcess(
            command,
            0,
            stdout=json.dumps(
                {
                    "uses_target_meaningfully": True,
                    "explanation": "The sentence uses fungus as a biological organism.",
                    "suggested_sentence": "A fungus can recycle nutrients in a forest.",
                }
            ),
            stderr="",
        )

    provider = CodexCliProvider(runner=fake_runner)
    request = ReviewAnswerEvaluationRequest(
        word="fungus",
        learner_sentence="A fungus can recycle nutrients in a forest.",
        theme="Biology Realm",
        review_stage=0,
    )

    response = provider.evaluate_review_answer(request)

    assert response.uses_target_meaningfully
    assert "biological organism" in response.explanation


def test_codex_cli_provider_uses_strict_schema_for_content_drafts(tmp_path) -> None:
    captured_schema: dict[str, object] = {}

    def fake_runner(command, **kwargs):
        assert "structured content draft" in kwargs["input"]
        assert '"purpose": "room_draft"' in kwargs["input"]
        schema_path = Path(command[command.index("--output-schema") + 1])
        captured_schema.update(json.loads(schema_path.read_text(encoding="utf-8")))
        return subprocess.CompletedProcess(
            command,
            0,
            stdout=json.dumps(
                {
                    "draft_type": "room_draft",
                    "payload": {
                        "theme": "biology",
                        "required_words": ["fungus", "symbiosis"],
                    },
                }
            ),
            stderr="",
        )

    provider = CodexCliProvider(cwd=tmp_path, runner=fake_runner)
    request = ContentDraftRequest(
        theme="biology",
        required_words=["fungus", "symbiosis"],
        purpose="room_draft",
    )

    response = provider.draft_content(request)

    assert captured_schema["additionalProperties"] is False
    assert set(captured_schema["required"]) == set(captured_schema["properties"])
    assert captured_schema["properties"]["payload"]["type"] == "object"
    assert response.draft_type == "room_draft"
    assert response.payload == {
        "theme": "biology",
        "required_words": ["fungus", "symbiosis"],
    }


def test_codex_cli_provider_reports_missing_executable() -> None:
    def fake_runner(command, **kwargs):
        raise FileNotFoundError("missing")

    provider = CodexCliProvider(executable="missing-codex", runner=fake_runner)

    with pytest.raises(AIProviderUnavailable, match="missing-codex"):
        provider.generate_turn_feedback(
            TurnFeedbackRequest(
                player_sentence="I go north.",
                location_id="research_camp",
                deterministic_action="move",
                deterministic_result="You go north.",
            )
        )


def test_codex_cli_provider_reports_timeout() -> None:
    def fake_runner(command, **kwargs):
        raise subprocess.TimeoutExpired(command, timeout=kwargs["timeout"])

    provider = CodexCliProvider(timeout_seconds=1, runner=fake_runner)

    with pytest.raises(CodexCliProviderError, match="timed out"):
        provider.generate_turn_feedback(
            TurnFeedbackRequest(
                player_sentence="I go north.",
                location_id="research_camp",
                deterministic_action="move",
                deterministic_result="You go north.",
            )
        )


def test_codex_cli_provider_rejects_invalid_structured_output() -> None:
    def fake_runner(command, **kwargs):
        return subprocess.CompletedProcess(command, 0, stdout="{}", stderr="")

    provider = CodexCliProvider(runner=fake_runner)

    with pytest.raises(CodexCliProviderError, match="invalid structured output"):
        provider.generate_turn_feedback(
            TurnFeedbackRequest(
                player_sentence="I go north.",
                location_id="research_camp",
                deterministic_action="move",
                deterministic_result="You go north.",
            )
        )
