import pytest
from pydantic import ValidationError

from toefl_rpg.ai.contract import AIProviderUnavailable
from toefl_rpg.ai.contract import ContentDraftRequest
from toefl_rpg.ai.contract import FakeAIProvider
from toefl_rpg.ai.contract import TurnFeedback
from toefl_rpg.ai.contract import TurnFeedbackRequest
from toefl_rpg.ai.contract import VocabularyExplanationRequest
from toefl_rpg.ai.contract import require_ai_provider


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


def test_ai_turn_feedback_requires_player_facing_text() -> None:
    with pytest.raises(ValidationError):
        TurnFeedback(
            narration="",
            sentence_feedback="",
            suggested_sentence="",
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
