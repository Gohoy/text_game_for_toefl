import json
import subprocess
from pathlib import Path

import pytest

from toefl_rpg.ai.codex_cli import CodexCliProvider
from toefl_rpg.ai.codex_cli import CodexCliProviderError
from toefl_rpg.ai.contract import AIProviderUnavailable
from toefl_rpg.ai.contract import NPCDialogueRequest
from toefl_rpg.ai.contract import PlayerSentenceInterpretationRequest
from toefl_rpg.ai.contract import RoomNarrationRequest
from toefl_rpg.ai.contract import TurnFeedbackRequest
from toefl_rpg.ai.contract import VocabularyExplanationRequest


def test_codex_cli_provider_builds_bounded_exec_command(tmp_path) -> None:
    calls = []

    def fake_runner(command, **kwargs):
        calls.append((command, kwargs))
        output_path = Path(command[command.index("--output-last-message") + 1])
        schema_path = Path(command[command.index("--output-schema") + 1])
        assert schema_path.exists()
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

    assert "fungus" in response.narration
    assert response.focus_hint == "The fungus sample is ready to collect."
    assert response.vocabulary_notes == ["symbiosis: living together."]


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
