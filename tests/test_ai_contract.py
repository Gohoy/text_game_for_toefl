import pytest
from pydantic import ValidationError

from toefl_rpg.ai.contract import AIProviderUnavailable
from toefl_rpg.ai.contract import ContentDraftRequest
from toefl_rpg.ai.contract import FakeAIProvider
from toefl_rpg.ai.contract import NPCDialogue
from toefl_rpg.ai.contract import NPCDialogueRequest
from toefl_rpg.ai.contract import PlayerSentenceInterpretation
from toefl_rpg.ai.contract import PlayerSentenceInterpretationRequest
from toefl_rpg.ai.contract import ReviewAnswerEvaluation
from toefl_rpg.ai.contract import ReviewAnswerEvaluationRequest
from toefl_rpg.ai.contract import RoomNarration
from toefl_rpg.ai.contract import RoomNarrationRequest
from toefl_rpg.ai.contract import StructuredContentDraft
from toefl_rpg.ai.contract import TurnFeedback
from toefl_rpg.ai.contract import TurnFeedbackRequest
from toefl_rpg.ai.contract import VocabularyExplanation
from toefl_rpg.ai.contract import VocabularyExplanationRequest
from toefl_rpg.ai.contract import require_ai_provider
from toefl_rpg.engine.actions import DETERMINISTIC_ACTIONS


def test_missing_ai_provider_fails_clearly() -> None:
    with pytest.raises(AIProviderUnavailable, match="AI provider is required"):
        require_ai_provider(None)


def test_fake_ai_provider_generates_valid_turn_feedback() -> None:
    provider = FakeAIProvider()
    request = TurnFeedbackRequest(
        player_sentence="I want to collect the fungus sample.",
        location_id="fungus_grove",
        deterministic_action="collect",
        deterministic_result="You collect fungus sample.",
        target_words=["fungus", "vital"],
        practiced_words=["fungus"],
    )

    response = require_ai_provider(provider).generate_turn_feedback(request)

    assert response.narration
    assert response.sentence_feedback.startswith("AI feedback:")
    assert response.suggested_sentence == request.player_sentence
    assert provider.turn_feedback_requests == [request]


def test_turn_feedback_request_rejects_extra_state_mutation_fields() -> None:
    with pytest.raises(ValidationError) as exc_info:
        TurnFeedbackRequest(
            player_sentence="I want to collect the fungus sample.",
            location_id="fungus_grove",
            deterministic_action="collect",
            deterministic_result="You collect fungus sample.",
            xp=100,
            inventory=["fungus sample"],
            save_path="/tmp/player-save.json",
        )

    message = str(exc_info.value)
    assert "xp" in message
    assert "inventory" in message
    assert "save_path" in message
    assert "Extra inputs are not permitted" in message


def test_ai_turn_feedback_requires_player_facing_text() -> None:
    with pytest.raises(ValidationError):
        TurnFeedback(
            narration="",
            sentence_feedback="",
            suggested_sentence="",
        )


def test_turn_feedback_rejects_extra_state_mutation_fields() -> None:
    with pytest.raises(ValidationError):
        TurnFeedback(
            narration="You move carefully.",
            sentence_feedback="Use a clear verb.",
            suggested_sentence="I go north.",
            xp=100,
        )


def test_fake_ai_provider_supports_vocabulary_explanations() -> None:
    provider = FakeAIProvider()
    request = VocabularyExplanationRequest(
        word="mimicry",
        theme="biology",
        learner_sentence="The creature uses mimicry.",
    )

    response = provider.explain_vocabulary(request)

    assert response.word == "mimicry"
    assert "biology" in response.plain_meaning
    assert response.example_sentence
    assert response.memory_hint


def test_vocabulary_explanation_request_rejects_extra_state_mutation_fields() -> None:
    with pytest.raises(ValidationError) as exc_info:
        VocabularyExplanationRequest(
            word="mimicry",
            theme="biology",
            learner_sentence="The creature uses mimicry.",
            mastered=True,
            xp=100,
            inventory=["field notebook"],
        )

    message = str(exc_info.value)
    assert "mastered" in message
    assert "xp" in message
    assert "inventory" in message
    assert "Extra inputs are not permitted" in message


def test_vocabulary_explanation_rejects_extra_state_mutation_fields() -> None:
    with pytest.raises(ValidationError):
        VocabularyExplanation(
            word="fungus",
            plain_meaning="A living growth.",
            example_sentence="A fungus grows in the forest.",
            memory_hint="Think of forest growth.",
            mastered=True,
        )


def test_fake_ai_provider_supports_structured_content_drafts() -> None:
    provider = FakeAIProvider()
    request = ContentDraftRequest(
        theme="biology",
        required_words=["fungus", "symbiosis"],
        purpose="room_draft",
    )

    response = provider.draft_content(request)

    assert response.draft_type == "room_draft"
    assert response.payload == {
        "theme": "biology",
        "required_words": ["fungus", "symbiosis"],
    }


def test_content_draft_request_rejects_extra_state_mutation_fields() -> None:
    with pytest.raises(ValidationError) as exc_info:
        ContentDraftRequest(
            theme="biology",
            required_words=["fungus", "symbiosis"],
            purpose="world_pack",
            xp=100,
            inventory=["field notebook"],
            save_path="/tmp/player-save.json",
        )

    message = str(exc_info.value)
    assert "xp" in message
    assert "inventory" in message
    assert "save_path" in message
    assert "Extra inputs are not permitted" in message


def test_structured_content_draft_rejects_extra_state_mutation_fields() -> None:
    with pytest.raises(ValidationError):
        StructuredContentDraft(
            draft_type="room_draft",
            payload={"theme": "biology"},
            xp=100,
        )


def test_player_facing_response_schemas_are_strict_for_codex() -> None:
    response_models = [
        TurnFeedback,
        VocabularyExplanation,
        PlayerSentenceInterpretation,
        NPCDialogue,
        RoomNarration,
        ReviewAnswerEvaluation,
        StructuredContentDraft,
    ]

    for response_model in response_models:
        schema = response_model.model_json_schema()
        assert schema["additionalProperties"] is False


def test_fake_ai_provider_supports_player_sentence_interpretation() -> None:
    provider = FakeAIProvider()
    request = PlayerSentenceInterpretationRequest(
        player_sentence="I want collect a sample with the microscope.",
        location_id="research_camp",
        room_name="Research Camp",
        exits={"north": "fungus_grove", "east": "microscope_tent"},
        visible_items=["field notebook"],
        visible_npcs=["Dr. Lin"],
        visible_enemies=[],
        target_words=["organism", "species", "evolve"],
    )

    response = provider.interpret_player_sentence(request)

    assert response.action == "unknown"
    assert response.target == ""
    assert response.confidence == 0
    assert provider.interpretation_requests == [request]


def test_sentence_interpretation_request_rejects_extra_state_mutation_fields() -> None:
    with pytest.raises(ValidationError) as exc_info:
        PlayerSentenceInterpretationRequest(
            player_sentence="Please finish the biology quest for me.",
            location_id="research_camp",
            room_name="Research Camp",
            exits={"north": "fungus_grove"},
            visible_items=["field notebook"],
            visible_npcs=["Dr. Lin"],
            visible_enemies=[],
            target_words=["organism", "species"],
            xp=100,
            inventory=["fungus sample"],
            quest_completed=True,
        )

    message = str(exc_info.value)
    assert "xp" in message
    assert "inventory" in message
    assert "quest_completed" in message
    assert "Extra inputs are not permitted" in message


def test_interpretation_response_rejects_unknown_actions() -> None:
    with pytest.raises(ValidationError):
        PlayerSentenceInterpretation(
            action="teleport",
            target="fungus_grove",
            confidence=0.9,
            reason="The action is not part of the deterministic contract.",
        )


def test_interpretation_response_accepts_shared_deterministic_actions() -> None:
    for action in DETERMINISTIC_ACTIONS:
        response = PlayerSentenceInterpretation(
            action=action,
            target="",
            confidence=0.9,
            reason="The action is part of the deterministic contract.",
        )
        assert response.action == action


def test_interpretation_response_rejects_extra_state_mutation_fields() -> None:
    with pytest.raises(ValidationError):
        PlayerSentenceInterpretation(
            action="move",
            target="north",
            confidence=0.9,
            reason="The learner asks to move north.",
            xp=100,
        )


def test_fake_ai_provider_supports_npc_dialogue() -> None:
    provider = FakeAIProvider()
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
    assert response.line
    assert response.vocabulary_notes
    assert provider.dialogue_requests == [request]


def test_npc_dialogue_request_rejects_extra_state_mutation_fields() -> None:
    with pytest.raises(ValidationError) as exc_info:
        NPCDialogueRequest(
            npc_name="Dr. Lin",
            location_id="research_camp",
            room_name="Research Camp",
            quest_progress="Biology Investigation 0/3",
            visible_items=["field notebook"],
            visible_npcs=["Dr. Lin"],
            visible_enemies=[],
            target_words=["organism", "species", "evolve"],
            xp=100,
            inventory=["fungus sample"],
            quest_completed=True,
        )

    message = str(exc_info.value)
    assert "xp" in message
    assert "inventory" in message
    assert "quest_completed" in message
    assert "Extra inputs are not permitted" in message


def test_npc_dialogue_rejects_extra_state_mutation_fields() -> None:
    with pytest.raises(ValidationError):
        NPCDialogue(
            speaker="Dr. Lin",
            line="Collect the fungus sample.",
            vocabulary_notes=["fungus: a growth."],
            completed_tasks=["collect_fungus_sample"],
        )


def test_fake_ai_provider_supports_room_narration() -> None:
    provider = FakeAIProvider()
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
    assert response.narration
    assert response.focus_hint
    assert response.vocabulary_notes
    assert provider.room_narration_requests == [request]


def test_room_narration_request_rejects_extra_state_mutation_fields() -> None:
    with pytest.raises(ValidationError) as exc_info:
        RoomNarrationRequest(
            location_id="fungus_grove",
            room_name="Fungus Grove",
            room_description="Pale mushrooms cover old roots.",
            quest_progress="Biology Investigation 0/3",
            exits={"south": "research_camp"},
            visible_items=["fungus sample"],
            visible_npcs=[],
            visible_enemies=[],
            target_words=["fungus", "symbiosis"],
            xp=100,
            inventory=["fungus sample"],
            quest_completed=True,
        )

    message = str(exc_info.value)
    assert "xp" in message
    assert "inventory" in message
    assert "quest_completed" in message
    assert "Extra inputs are not permitted" in message


def test_room_narration_rejects_extra_state_mutation_fields() -> None:
    with pytest.raises(ValidationError):
        RoomNarration(
            location_id="fungus_grove",
            narration="The grove changes shape.",
            focus_hint="Collect the sample.",
            vocabulary_notes=["fungus: a growth."],
            room_id="new_room",
        )


def test_fake_ai_provider_supports_review_answer_evaluation() -> None:
    provider = FakeAIProvider()
    request = ReviewAnswerEvaluationRequest(
        word="fungus",
        learner_sentence="A fungus can be vital for forest metabolism.",
        theme="Biology Realm",
        review_stage=0,
    )

    response = provider.evaluate_review_answer(request)

    assert response.uses_target_meaningfully
    assert response.explanation
    assert response.suggested_sentence == request.learner_sentence
    assert provider.review_evaluation_requests == [request]


def test_review_answer_evaluation_rejects_extra_state_mutation_fields() -> None:
    with pytest.raises(ValidationError):
        ReviewAnswerEvaluation(
            uses_target_meaningfully=True,
            explanation="The sentence uses fungus correctly.",
            suggested_sentence="A fungus can be vital for forest metabolism.",
            xp=100,
        )
