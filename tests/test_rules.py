from copy import deepcopy
from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from toefl_rpg.ai.contract import AIProviderUnavailable
from toefl_rpg.ai.contract import FakeAIProvider
from toefl_rpg.ai.contract import NPCDialogue
from toefl_rpg.ai.contract import PlayerSentenceInterpretation
from toefl_rpg.ai.contract import ReviewAnswerEvaluation
from toefl_rpg.ai.contract import RoomNarration
from toefl_rpg.ai.contract import TurnFeedback
from toefl_rpg.ai.contract import VocabularyExplanation
from toefl_rpg.content.sample_world import build_biology_realm
from toefl_rpg.engine.mastery import response_fingerprint
from toefl_rpg.engine.mastery import review_context_id
from toefl_rpg.engine.rules import GameEngine


def new_test_engine() -> GameEngine:
    return GameEngine.new_game(
        build_biology_realm(),
        use_deterministic_feedback=True,
    )


def test_move_between_rooms() -> None:
    engine = new_test_engine()

    result = engine.handle("I want to go to the east")

    assert result.success
    assert engine.state.current_room_id == "microscope_tent"


def test_verbose_movement_sentence_uses_deterministic_exits() -> None:
    engine = new_test_engine()

    result = engine.handle("I go north to the fungus grove.")

    assert result.success
    assert engine.state.current_room_id == "fungus_grove"


def test_verbose_movement_rejects_unavailable_exit() -> None:
    engine = new_test_engine()

    result = engine.handle("I go west to the river.")

    assert not result.success
    assert "cannot go west" in result.message
    assert engine.state.current_room_id == "research_camp"


def test_runtime_requires_ai_provider_for_turn_feedback() -> None:
    engine = GameEngine.new_game(build_biology_realm())

    with pytest.raises(AIProviderUnavailable):
        engine.handle("look")


def test_engine_uses_ai_feedback_for_runtime_sentence_feedback() -> None:
    provider = FakeAIProvider()
    engine = GameEngine.new_game(build_biology_realm(), ai_provider=provider)

    result = engine.handle("I want to go north")

    assert result.success
    assert "AI feedback:" in result.english_feedback
    assert "Good: you used a full sentence." not in result.english_feedback
    assert provider.turn_feedback_requests[0].deterministic_action == "move"
    assert provider.turn_feedback_requests[0].deterministic_result == "You go north."
    assert provider.turn_feedback_requests[0].location_id == "research_camp"


def test_ai_turn_feedback_display_keeps_coaching_sections_distinct() -> None:
    class StructuredFeedbackProvider(FakeAIProvider):
        def generate_turn_feedback(self, request):
            self.turn_feedback_requests.append(request)
            return TurnFeedback(
                narration="The grove stays damp while you collect the sample.",
                sentence_feedback="Use a clear verb after 'I want'.",
                suggested_sentence="I want to collect the fungus sample.",
                vocabulary_notes=[
                    "fungus: a growth that can affect an ecosystem.",
                    "vital: necessary for survival.",
                ],
            )

    provider = StructuredFeedbackProvider()
    engine = GameEngine.new_game(build_biology_realm(), ai_provider=provider)
    engine.state.current_room_id = "fungus_grove"

    result = engine.handle("I want to collect fungus sample")

    assert result.success
    assert "You collect fungus sample." in result.message
    assert result.message not in result.english_feedback
    assert result.english_feedback.splitlines() == [
        "Narration: The grove stays damp while you collect the sample.",
        "Feedback: Use a clear verb after 'I want'.",
        "Try: I want to collect the fungus sample.",
        "Vocabulary: fungus: a growth that can affect an ecosystem.",
        "Vocabulary: vital: necessary for survival.",
    ]
    assert provider.turn_feedback_requests[0].deterministic_result == result.message


def test_low_confidence_ai_interpretation_shows_retry_guidance_without_state_change() -> None:
    class LowConfidenceProvider(FakeAIProvider):
        def interpret_player_sentence(self, request):
            self.interpretation_requests.append(request)
            return PlayerSentenceInterpretation(
                action="collect",
                target="fungus sample",
                confidence=0.2,
                reason="The request is too vague to map safely.",
            )

    provider = LowConfidenceProvider()
    engine = GameEngine.new_game(build_biology_realm(), ai_provider=provider)
    engine.handle("go north")
    before_state = deepcopy(engine.state)

    result = engine.handle("Could you handle the thing for me?")

    assert not result.success
    assert (
        result.message
        == "I could not confidently turn that sentence into a game action. "
        "Try a clearer sentence for collect."
    )
    assert engine.state == before_state
    assert provider.turn_feedback_requests[-1].deterministic_action == "unknown"
    assert provider.turn_feedback_requests[-1].deterministic_result == result.message


def test_ai_feedback_request_includes_reviewed_word() -> None:
    provider = FakeAIProvider()
    now = datetime(2026, 6, 22, 8, 0, tzinfo=timezone.utc)
    engine = GameEngine.new_game(
        build_biology_realm(),
        ai_provider=provider,
        clock=lambda: now,
    )
    engine.handle("go north")
    engine.handle("The fungus is vital for the old forest.")
    engine.handle("review")

    result = engine.handle("A fungus can be vital for forest metabolism.")

    assert result.success
    assert provider.turn_feedback_requests[-1].practiced_words == ["fungus"]


def test_review_answer_uses_ai_quality_judgment_before_reward() -> None:
    provider = FakeAIProvider()
    now = datetime(2026, 6, 22, 8, 0, tzinfo=timezone.utc)
    engine = GameEngine.new_game(
        build_biology_realm(),
        ai_provider=provider,
        clock=lambda: now,
    )
    engine.handle("go north")
    engine.handle("The fungus is vital for the old forest.")
    engine.handle("review")

    result = engine.handle("A fungus can be vital for forest metabolism.")

    fungus = engine.state.vocabulary_mastery["fungus"]
    assert result.success
    assert "AI advice: Fake AI review evaluation" in result.message
    assert "Try: A fungus can be vital for forest metabolism." in result.message
    assert "Result: Review complete for 'fungus'." in result.message
    assert "Review stage 1. XP +10." in result.message
    assert engine.state.active_review_word is None
    assert fungus.review_stage == 1
    assert fungus.mastery_points == 2
    assert engine.state.player.xp == 26
    assert provider.review_evaluation_requests[0].word == "fungus"
    assert (
        provider.review_evaluation_requests[0].learner_sentence
        == "A fungus can be vital for forest metabolism."
    )


def test_review_answer_ai_rejection_keeps_word_active_without_reward() -> None:
    class RejectingReviewProvider(FakeAIProvider):
        def evaluate_review_answer(self, request):
            self.review_evaluation_requests.append(request)
            return ReviewAnswerEvaluation(
                uses_target_meaningfully=False,
                explanation="The sentence names the word but does not show its meaning.",
                suggested_sentence="A fungus can decompose wood in a forest.",
            )

    provider = RejectingReviewProvider()
    now = datetime(2026, 6, 22, 8, 0, tzinfo=timezone.utc)
    engine = GameEngine.new_game(
        build_biology_realm(),
        ai_provider=provider,
        clock=lambda: now,
    )
    engine.handle("go north")
    engine.handle("The fungus is vital for the old forest.")
    engine.handle("review")

    result = engine.handle("The word fungus appears in my sentence.")

    fungus = engine.state.vocabulary_mastery["fungus"]
    assert not result.success
    assert "AI advice: The sentence names the word" in result.message
    assert "Try: A fungus can decompose wood in a forest." in result.message
    assert "Result: Review needs another try." in result.message
    assert "No XP awarded; 'fungus' remains active for review." in result.message
    assert engine.state.active_review_word == "fungus"
    assert fungus.review_stage == 0
    assert fungus.mastery_points == 1
    assert fungus.incorrect_use_count == 1
    assert engine.state.player.xp == 16


def test_duplicate_review_answer_has_distinct_message_without_reward() -> None:
    provider = FakeAIProvider()
    now = datetime(2026, 6, 22, 8, 0, tzinfo=timezone.utc)
    sentence = "A fungus can be vital for forest metabolism."
    engine = GameEngine.new_game(
        build_biology_realm(),
        ai_provider=provider,
        clock=lambda: now,
    )
    engine.handle("go north")
    engine.handle("The fungus is vital for the old forest.")
    engine.handle("review")
    fungus = engine.state.vocabulary_mastery["fungus"]
    duplicate_fingerprint = response_fingerprint(
        sentence,
        "fungus",
        review_context_id(engine.state.world.world_id, "fungus", fungus.review_stage),
    )
    fungus.recent_response_fingerprints.append(duplicate_fingerprint)
    before_xp = engine.state.player.xp
    before_stage = fungus.review_stage
    before_mastery_points = fungus.mastery_points

    result = engine.handle(sentence)

    assert result.success
    assert "already completed this review" in result.message
    assert "Result: Review complete" not in result.message
    assert "Result: Review needs another try" not in result.message
    assert "AI advice:" not in result.message
    assert engine.state.active_review_word is None
    assert engine.state.player.xp == before_xp
    assert fungus.review_stage == before_stage
    assert fungus.mastery_points == before_mastery_points
    assert provider.review_evaluation_requests == []


def test_invalid_ai_review_evaluation_preserves_state() -> None:
    class InvalidReviewProvider(FakeAIProvider):
        def evaluate_review_answer(self, request):
            self.review_evaluation_requests.append(request)
            return {"explanation": "Missing the required judgment."}

    provider = InvalidReviewProvider()
    now = datetime(2026, 6, 22, 8, 0, tzinfo=timezone.utc)
    engine = GameEngine.new_game(
        build_biology_realm(),
        ai_provider=provider,
        clock=lambda: now,
    )
    engine.handle("go north")
    engine.handle("The fungus is vital for the old forest.")
    engine.handle("review")
    before_state = deepcopy(engine.state)

    with pytest.raises(AIProviderUnavailable, match="AI review evaluation failed"):
        engine.handle("A fungus can be vital for forest metabolism.")

    assert engine.state == before_state
    assert provider.review_evaluation_requests[0].word == "fungus"


@pytest.mark.parametrize("empty_field", ["explanation", "suggested_sentence"])
def test_empty_ai_review_evaluation_fields_preserve_active_review_state(
    empty_field: str,
) -> None:
    class EmptyReviewProvider(FakeAIProvider):
        def evaluate_review_answer(self, request):
            self.review_evaluation_requests.append(request)
            evaluation = {
                "uses_target_meaningfully": True,
                "explanation": "The sentence connects the word to its role in nature.",
                "suggested_sentence": "A fungus can be vital for forest metabolism.",
            }
            evaluation[empty_field] = ""
            return evaluation

    provider = EmptyReviewProvider()
    now = datetime(2026, 6, 22, 8, 0, tzinfo=timezone.utc)
    engine = GameEngine.new_game(
        build_biology_realm(),
        ai_provider=provider,
        clock=lambda: now,
    )
    engine.handle("go north")
    engine.handle("The fungus is vital for the old forest.")
    engine.handle("review")
    before_state = deepcopy(engine.state)

    with pytest.raises(AIProviderUnavailable, match="AI review evaluation failed"):
        engine.handle("A fungus can be vital for forest metabolism.")

    assert engine.state == before_state
    assert engine.state.active_review_word == "fungus"
    assert provider.review_evaluation_requests[0].word == "fungus"


def test_malformed_ai_review_evaluation_judgment_preserves_active_review_state() -> None:
    class MalformedReviewProvider(FakeAIProvider):
        def evaluate_review_answer(self, request):
            self.review_evaluation_requests.append(request)
            return {
                "uses_target_meaningfully": "yes",
                "explanation": "The sentence connects the word to its role in nature.",
                "suggested_sentence": "A fungus can be vital for forest metabolism.",
            }

    provider = MalformedReviewProvider()
    now = datetime(2026, 6, 22, 8, 0, tzinfo=timezone.utc)
    engine = GameEngine.new_game(
        build_biology_realm(),
        ai_provider=provider,
        clock=lambda: now,
    )
    engine.handle("go north")
    engine.handle("The fungus is vital for the old forest.")
    engine.handle("review")
    before_state = deepcopy(engine.state)

    with pytest.raises(AIProviderUnavailable, match="AI review evaluation failed"):
        engine.handle("A fungus can be vital for forest metabolism.")

    assert engine.state == before_state
    assert engine.state.active_review_word == "fungus"
    assert provider.review_evaluation_requests[0].word == "fungus"


def test_explain_visible_vocabulary_uses_ai_without_mutating_state() -> None:
    provider = FakeAIProvider()
    engine = GameEngine.new_game(build_biology_realm(), ai_provider=provider)
    engine.handle("go north")
    before_state = deepcopy(engine.state)

    result = engine.handle("Please explain the word fungus")

    assert result.success
    assert "fungus:" in result.message
    assert "Example:" in result.message
    assert "Memory hint:" in result.message
    assert engine.state == before_state
    assert provider.vocabulary_requests[0].word == "fungus"
    assert provider.vocabulary_requests[0].theme == "Biology Realm"
    assert (
        provider.vocabulary_requests[0].learner_sentence
        == "Please explain the word fungus"
    )


def test_vocabulary_explanation_keeps_learning_sections_distinct() -> None:
    class StructuredExplanationProvider(FakeAIProvider):
        def explain_vocabulary(self, request):
            self.vocabulary_requests.append(request)
            return VocabularyExplanation(
                word=request.word,
                plain_meaning="A fungus is a living growth such as mold or mushrooms.",
                example_sentence="A fungus can recycle nutrients in a forest.",
                memory_hint="Connect fungus with forest mushrooms.",
            )

    provider = StructuredExplanationProvider()
    engine = GameEngine.new_game(build_biology_realm(), ai_provider=provider)
    engine.handle("go north")
    before_state = deepcopy(engine.state)

    result = engine.handle("explain fungus")

    assert result.success
    assert result.message.splitlines() == [
        "fungus: A fungus is a living growth such as mold or mushrooms.",
        "Example: A fungus can recycle nutrients in a forest.",
        "Memory hint: Connect fungus with forest mushrooms.",
    ]
    assert engine.state == before_state
    assert provider.vocabulary_requests[0].word == "fungus"


def test_vocabulary_explanation_rejects_mismatched_ai_word_without_mutating_state() -> None:
    class MismatchedExplanationProvider(FakeAIProvider):
        def explain_vocabulary(self, request):
            self.vocabulary_requests.append(request)
            return VocabularyExplanation(
                word="enzyme",
                plain_meaning="A protein that speeds up a chemical reaction.",
                example_sentence="An enzyme helps digestion.",
                memory_hint="Enzyme sounds like inside chemistry.",
            )

    provider = MismatchedExplanationProvider()
    engine = GameEngine.new_game(build_biology_realm(), ai_provider=provider)
    engine.handle("go north")
    before_state = deepcopy(engine.state)

    with pytest.raises(AIProviderUnavailable, match="different word"):
        engine.handle("explain fungus")

    assert engine.state == before_state
    assert provider.vocabulary_requests[0].word == "fungus"


def test_explain_practiced_vocabulary_can_work_outside_current_room() -> None:
    provider = FakeAIProvider()
    engine = GameEngine.new_game(build_biology_realm(), ai_provider=provider)
    engine.handle("go north")
    engine.handle("The fungus is vital for the old forest.")
    engine.handle("go south")

    result = engine.handle("explain fungus")

    assert result.success
    assert provider.vocabulary_requests[-1].word == "fungus"


def test_explain_rejects_unknown_word_before_ai_call() -> None:
    provider = FakeAIProvider()
    engine = GameEngine.new_game(build_biology_realm(), ai_provider=provider)
    before_state = deepcopy(engine.state)

    result = engine.handle("explain astronomy")

    assert not result.success
    assert "not a Biology Realm vocabulary word" in result.message
    assert engine.state == before_state
    assert provider.vocabulary_requests == []


def test_ai_interpretation_fallback_collects_visible_item() -> None:
    class CollectingProvider(FakeAIProvider):
        def interpret_player_sentence(self, request):
            self.interpretation_requests.append(request)
            return PlayerSentenceInterpretation(
                action="collect",
                target="fungus sample",
                confidence=0.82,
                reason="The player is asking to pick up the visible specimen.",
            )

    provider = CollectingProvider()
    engine = GameEngine.new_game(build_biology_realm(), ai_provider=provider)
    engine.handle("go north")

    result = engine.handle("Could you grab the specimen for my research?")

    assert result.success
    assert "fungus sample" in engine.state.player.inventory
    assert "fungus sample" not in engine.state.current_room.items
    request = provider.interpretation_requests[0]
    assert request.location_id == "fungus_grove"
    assert request.visible_items == ["fungus sample"]
    assert request.visible_npcs == []
    assert set(request.target_words) == {"fungus", "symbiosis", "vital"}
    assert provider.turn_feedback_requests[-1].deterministic_action == "collect"


def test_ai_interpretation_cannot_invent_unavailable_target() -> None:
    class InventingProvider(FakeAIProvider):
        def interpret_player_sentence(self, request):
            self.interpretation_requests.append(request)
            return PlayerSentenceInterpretation(
                action="collect",
                target="crystal sample",
                confidence=0.9,
                reason="The player asks for a sample that is not in the room.",
            )

    provider = InventingProvider()
    engine = GameEngine.new_game(build_biology_realm(), ai_provider=provider)
    engine.handle("go north")
    before_state = deepcopy(engine.state)

    result = engine.handle("Could you grab the crystal sample?")

    assert not result.success
    assert "cannot collect crystal sample here" in result.message
    assert engine.state == before_state


def test_invalid_ai_interpretation_preserves_state() -> None:
    class InvalidInterpretationProvider(FakeAIProvider):
        def interpret_player_sentence(self, request):
            self.interpretation_requests.append(request)
            return {"action": "collect"}

    provider = InvalidInterpretationProvider()
    engine = GameEngine.new_game(build_biology_realm(), ai_provider=provider)
    engine.handle("go north")
    before_state = deepcopy(engine.state)

    with pytest.raises(AIProviderUnavailable, match="AI sentence interpretation failed"):
        engine.handle("Could you grab the specimen for my research?")

    assert engine.state == before_state
    assert provider.interpretation_requests[0].location_id == "fungus_grove"


@pytest.mark.parametrize("empty_field", ["action", "reason"])
def test_empty_ai_interpretation_required_fields_preserve_state(
    empty_field: str,
) -> None:
    class EmptyInterpretationProvider(FakeAIProvider):
        def interpret_player_sentence(self, request):
            self.interpretation_requests.append(request)
            interpretation = {
                "action": "collect",
                "target": "fungus sample",
                "confidence": 0.9,
                "reason": "The learner asks for the visible specimen.",
            }
            interpretation[empty_field] = ""
            return interpretation

    provider = EmptyInterpretationProvider()
    engine = GameEngine.new_game(build_biology_realm(), ai_provider=provider)
    engine.handle("go north")
    before_state = deepcopy(engine.state)

    with pytest.raises(AIProviderUnavailable, match="AI sentence interpretation failed"):
        engine.handle("Could you grab the specimen for my research?")

    assert engine.state == before_state
    assert provider.interpretation_requests[0].location_id == "fungus_grove"


def test_ai_interpretation_extra_fields_preserve_state() -> None:
    class ExtraFieldInterpretationProvider(FakeAIProvider):
        def interpret_player_sentence(self, request):
            self.interpretation_requests.append(request)
            return {
                "action": "collect",
                "target": "fungus sample",
                "confidence": 0.9,
                "reason": "The learner asks for the visible specimen.",
                "inventory": ["fungus sample"],
                "xp": 100,
            }

    provider = ExtraFieldInterpretationProvider()
    engine = GameEngine.new_game(build_biology_realm(), ai_provider=provider)
    engine.handle("go north")
    before_state = deepcopy(engine.state)

    with pytest.raises(AIProviderUnavailable, match="AI sentence interpretation failed"):
        engine.handle("Could you grab the specimen for my research?")

    assert engine.state == before_state
    assert provider.interpretation_requests[0].location_id == "fungus_grove"


def test_ai_interpretation_is_not_used_when_parser_matches() -> None:
    provider = FakeAIProvider()
    engine = GameEngine.new_game(build_biology_realm(), ai_provider=provider)
    engine.handle("go north")

    result = engine.handle("I want to collect the fungus sample")

    assert result.success
    assert provider.interpretation_requests == []


def test_talk_to_visible_npc_uses_ai_dialogue_without_mutating_state() -> None:
    provider = FakeAIProvider()
    engine = GameEngine.new_game(build_biology_realm(), ai_provider=provider)
    before_state = deepcopy(engine.state)

    result = engine.handle("talk to Dr. Lin")

    assert result.success
    assert "Dr. Lin says:" in result.message
    assert "Dialogue vocabulary:" in result.message
    assert engine.state == before_state
    request = provider.dialogue_requests[0]
    assert request.npc_name == "Dr. Lin"
    assert request.location_id == "research_camp"
    assert request.quest_progress.startswith("Biology Investigation 0/3")
    assert request.visible_items == ["field notebook"]
    assert set(request.target_words) == {"organism", "species", "evolve"}


def test_look_uses_ai_room_narration_without_mutating_state() -> None:
    provider = FakeAIProvider()
    engine = GameEngine.new_game(build_biology_realm(), ai_provider=provider)
    engine.handle("go north")
    before_state = deepcopy(engine.state)

    result = engine.handle("look")

    assert result.success
    assert "Focus:" in result.message
    assert "Room vocabulary:" in result.message
    assert engine.state == before_state
    request = provider.room_narration_requests[0]
    assert request.location_id == "fungus_grove"
    assert request.room_name == "Fungus Grove"
    assert "Pale mushrooms" in request.room_description
    assert request.exits == {"south": "research_camp", "north": "mimicry_trail"}
    assert request.visible_items == ["fungus sample"]
    assert request.visible_npcs == []
    assert set(request.target_words) == {"fungus", "symbiosis", "vital"}


def test_invalid_ai_room_narration_preserves_state() -> None:
    class InvalidRoomNarrationProvider(FakeAIProvider):
        def generate_room_narration(self, request):
            self.room_narration_requests.append(request)
            return {"focus_hint": "Look around."}

    provider = InvalidRoomNarrationProvider()
    engine = GameEngine.new_game(build_biology_realm(), ai_provider=provider)
    engine.handle("go north")
    before_state = deepcopy(engine.state)

    with pytest.raises(AIProviderUnavailable, match="AI room narration failed"):
        engine.handle("look")

    assert engine.state == before_state
    assert provider.room_narration_requests[0].location_id == "fungus_grove"


def test_ai_room_narration_rejects_empty_required_fields_without_mutating_state() -> None:
    class EmptyRoomNarrationProvider(FakeAIProvider):
        def generate_room_narration(self, request):
            self.room_narration_requests.append(request)
            return RoomNarration(
                location_id=request.location_id,
                narration="",
                focus_hint="",
                vocabulary_notes=[],
            )

    provider = EmptyRoomNarrationProvider()
    engine = GameEngine.new_game(build_biology_realm(), ai_provider=provider)
    engine.handle("go north")
    before_state = deepcopy(engine.state)

    with pytest.raises(AIProviderUnavailable, match="AI room narration failed"):
        engine.handle("look")

    assert engine.state == before_state
    assert provider.room_narration_requests[0].location_id == "fungus_grove"


def test_ai_room_narration_rejects_mismatched_room_without_mutating_state() -> None:
    class MismatchedRoomNarrationProvider(FakeAIProvider):
        def generate_room_narration(self, request):
            self.room_narration_requests.append(request)
            return RoomNarration(
                location_id="research_camp",
                narration="This narration describes a different room.",
                focus_hint="Return to camp.",
                vocabulary_notes=["organism: a living thing."],
            )

    provider = MismatchedRoomNarrationProvider()
    engine = GameEngine.new_game(build_biology_realm(), ai_provider=provider)
    engine.handle("go north")
    before_state = deepcopy(engine.state)

    with pytest.raises(AIProviderUnavailable, match="different room"):
        engine.handle("look")

    assert engine.state == before_state
    assert provider.room_narration_requests[0].location_id == "fungus_grove"


def test_malformed_ai_room_narration_vocabulary_notes_preserve_state() -> None:
    class MalformedVocabularyNotesProvider(FakeAIProvider):
        def generate_room_narration(self, request):
            self.room_narration_requests.append(request)
            return {
                "location_id": request.location_id,
                "narration": "Fungus threads stretch across the shaded roots.",
                "focus_hint": "Compare the healthy and weakened trees.",
                "vocabulary_notes": [{"word": "symbiosis"}],
            }

    provider = MalformedVocabularyNotesProvider()
    engine = GameEngine.new_game(build_biology_realm(), ai_provider=provider)
    engine.handle("go north")
    before_state = deepcopy(engine.state)

    with pytest.raises(AIProviderUnavailable, match="AI room narration failed"):
        engine.handle("look")

    assert engine.state == before_state
    assert provider.room_narration_requests[0].location_id == "fungus_grove"


def test_ai_room_narration_cannot_return_state_mutation_fields() -> None:
    with pytest.raises(ValidationError):
        RoomNarration(
            location_id="fungus_grove",
            narration="You discover a shortcut.",
            focus_hint="Go east.",
            vocabulary_notes=[],
            exits={"east": "hidden_room"},
        )


def test_talk_rejects_absent_npc_before_dialogue_ai_call() -> None:
    provider = FakeAIProvider()
    engine = GameEngine.new_game(build_biology_realm(), ai_provider=provider)
    before_state = deepcopy(engine.state)

    result = engine.handle("talk to invisible guide")

    assert not result.success
    assert "invisible guide is not here" in result.message
    assert engine.state == before_state
    assert provider.dialogue_requests == []


def test_invalid_ai_dialogue_preserves_state() -> None:
    class InvalidDialogueProvider(FakeAIProvider):
        def generate_npc_dialogue(self, request):
            self.dialogue_requests.append(request)
            return {"speaker": request.npc_name}

    provider = InvalidDialogueProvider()
    engine = GameEngine.new_game(build_biology_realm(), ai_provider=provider)
    before_state = deepcopy(engine.state)

    with pytest.raises(AIProviderUnavailable, match="AI NPC dialogue failed"):
        engine.handle("talk to Dr. Lin")

    assert engine.state == before_state
    assert provider.dialogue_requests[0].npc_name == "Dr. Lin"


def test_ai_dialogue_rejects_mismatched_speaker_without_mutating_state() -> None:
    class MismatchedSpeakerProvider(FakeAIProvider):
        def generate_npc_dialogue(self, request):
            self.dialogue_requests.append(request)
            return NPCDialogue(
                speaker="Professor Vega",
                line="This line came from the wrong visible NPC.",
                vocabulary_notes=["organism: a living thing."],
            )

    provider = MismatchedSpeakerProvider()
    engine = GameEngine.new_game(build_biology_realm(), ai_provider=provider)
    before_state = deepcopy(engine.state)

    with pytest.raises(AIProviderUnavailable, match="different speaker"):
        engine.handle("talk to Dr. Lin")

    assert engine.state == before_state
    assert provider.dialogue_requests[0].npc_name == "Dr. Lin"


@pytest.mark.parametrize("empty_field", ["speaker", "line"])
def test_empty_ai_dialogue_fields_preserve_state(empty_field: str) -> None:
    class EmptyDialogueProvider(FakeAIProvider):
        def generate_npc_dialogue(self, request):
            self.dialogue_requests.append(request)
            dialogue = {
                "speaker": request.npc_name,
                "line": "Use respiration clues to track the organism.",
                "vocabulary_notes": ["respiration: the process of using oxygen."],
            }
            dialogue[empty_field] = ""
            return dialogue

    provider = EmptyDialogueProvider()
    engine = GameEngine.new_game(build_biology_realm(), ai_provider=provider)
    before_state = deepcopy(engine.state)

    with pytest.raises(AIProviderUnavailable, match="AI NPC dialogue failed"):
        engine.handle("talk to Dr. Lin")

    assert engine.state == before_state
    assert provider.dialogue_requests[0].npc_name == "Dr. Lin"


def test_malformed_ai_dialogue_vocabulary_notes_preserve_state() -> None:
    class MalformedVocabularyNotesProvider(FakeAIProvider):
        def generate_npc_dialogue(self, request):
            self.dialogue_requests.append(request)
            return {
                "speaker": request.npc_name,
                "line": "Use respiration clues to track the organism.",
                "vocabulary_notes": [{"word": "respiration"}],
            }

    provider = MalformedVocabularyNotesProvider()
    engine = GameEngine.new_game(build_biology_realm(), ai_provider=provider)
    before_state = deepcopy(engine.state)

    with pytest.raises(AIProviderUnavailable, match="AI NPC dialogue failed"):
        engine.handle("talk to Dr. Lin")

    assert engine.state == before_state
    assert provider.dialogue_requests[0].npc_name == "Dr. Lin"


def test_ai_dialogue_extra_fields_preserve_state() -> None:
    class ExtraFieldDialogueProvider(FakeAIProvider):
        def generate_npc_dialogue(self, request):
            self.dialogue_requests.append(request)
            return {
                "speaker": request.npc_name,
                "line": "Use respiration clues to track the organism.",
                "vocabulary_notes": ["respiration: the process of using oxygen."],
                "completed_tasks": ["collect_fungus_sample"],
                "xp": 100,
            }

    provider = ExtraFieldDialogueProvider()
    engine = GameEngine.new_game(build_biology_realm(), ai_provider=provider)
    before_state = deepcopy(engine.state)

    with pytest.raises(AIProviderUnavailable, match="AI NPC dialogue failed"):
        engine.handle("talk to Dr. Lin")

    assert engine.state == before_state
    assert provider.dialogue_requests[0].npc_name == "Dr. Lin"


def test_ai_dialogue_cannot_return_state_mutation_fields() -> None:
    with pytest.raises(ValidationError):
        NPCDialogue(
            speaker="Dr. Lin",
            line="Quest complete.",
            vocabulary_notes=[],
            xp=100,
        )


def test_invalid_ai_explanation_preserves_state() -> None:
    class InvalidExplanationProvider(FakeAIProvider):
        def explain_vocabulary(self, request):
            self.vocabulary_requests.append(request)
            return {"word": request.word}

    provider = InvalidExplanationProvider()
    engine = GameEngine.new_game(build_biology_realm(), ai_provider=provider)
    engine.handle("go north")
    before_state = deepcopy(engine.state)

    with pytest.raises(AIProviderUnavailable, match="AI vocabulary explanation failed"):
        engine.handle("explain fungus")

    assert engine.state == before_state
    assert provider.vocabulary_requests[0].word == "fungus"


@pytest.mark.parametrize(
    "empty_field",
    ["plain_meaning", "example_sentence", "memory_hint"],
)
def test_empty_ai_vocabulary_explanation_fields_preserve_state(
    empty_field: str,
) -> None:
    class EmptyExplanationProvider(FakeAIProvider):
        def explain_vocabulary(self, request):
            self.vocabulary_requests.append(request)
            explanation = {
                "word": request.word,
                "plain_meaning": "A fungus is a living growth such as mold or mushrooms.",
                "example_sentence": "A fungus can recycle nutrients in a forest.",
                "memory_hint": "Connect fungus with forest mushrooms.",
            }
            explanation[empty_field] = ""
            return explanation

    provider = EmptyExplanationProvider()
    engine = GameEngine.new_game(build_biology_realm(), ai_provider=provider)
    engine.handle("go north")
    before_state = deepcopy(engine.state)

    with pytest.raises(AIProviderUnavailable, match="AI vocabulary explanation failed"):
        engine.handle("explain fungus")

    assert engine.state == before_state
    assert provider.vocabulary_requests[0].word == "fungus"


def test_ai_vocabulary_explanation_extra_fields_preserve_state() -> None:
    class ExtraFieldExplanationProvider(FakeAIProvider):
        def explain_vocabulary(self, request):
            self.vocabulary_requests.append(request)
            return {
                "word": request.word,
                "plain_meaning": "A fungus is a living growth such as mold or mushrooms.",
                "example_sentence": "A fungus can recycle nutrients in a forest.",
                "memory_hint": "Connect fungus with forest mushrooms.",
                "mastered": True,
                "xp": 100,
            }

    provider = ExtraFieldExplanationProvider()
    engine = GameEngine.new_game(build_biology_realm(), ai_provider=provider)
    engine.handle("go north")
    before_state = deepcopy(engine.state)

    with pytest.raises(AIProviderUnavailable, match="AI vocabulary explanation failed"):
        engine.handle("explain fungus")

    assert engine.state == before_state
    assert provider.vocabulary_requests[0].word == "fungus"


def test_invalid_ai_turn_feedback_preserves_state() -> None:
    class InvalidTurnFeedbackProvider(FakeAIProvider):
        def generate_turn_feedback(self, request):
            self.turn_feedback_requests.append(request)
            return {"narration": "Missing required feedback fields."}

    provider = InvalidTurnFeedbackProvider()
    engine = GameEngine.new_game(build_biology_realm(), ai_provider=provider)
    engine.state.current_room_id = "fungus_grove"
    before_state = deepcopy(engine.state)

    with pytest.raises(AIProviderUnavailable, match="AI turn feedback failed"):
        engine.handle("I want to collect the fungus sample")

    assert engine.state == before_state
    assert provider.turn_feedback_requests[0].deterministic_action == "collect"


@pytest.mark.parametrize(
    "empty_field",
    ["narration", "sentence_feedback", "suggested_sentence"],
)
def test_empty_ai_turn_feedback_required_fields_preserve_state_after_state_change(
    empty_field: str,
) -> None:
    class EmptyTurnFeedbackProvider(FakeAIProvider):
        def generate_turn_feedback(self, request):
            self.turn_feedback_requests.append(request)
            feedback = {
                "narration": "The grove reacts to your careful fieldwork.",
                "sentence_feedback": "Your sentence clearly states the intended action.",
                "suggested_sentence": "I want to collect the fungus sample.",
                "vocabulary_notes": [],
            }
            feedback[empty_field] = ""
            return feedback

    provider = EmptyTurnFeedbackProvider()
    engine = GameEngine.new_game(build_biology_realm(), ai_provider=provider)
    engine.state.current_room_id = "fungus_grove"
    before_state = deepcopy(engine.state)

    with pytest.raises(AIProviderUnavailable, match="AI turn feedback failed"):
        engine.handle("I want to collect the fungus sample")

    assert engine.state == before_state
    assert provider.turn_feedback_requests[0].deterministic_action == "collect"
    assert provider.turn_feedback_requests[0].deterministic_result.startswith(
        "You collect fungus sample."
    )


def test_malformed_ai_turn_feedback_vocabulary_notes_preserve_state_after_state_change() -> None:
    class MalformedVocabularyNotesProvider(FakeAIProvider):
        def generate_turn_feedback(self, request):
            self.turn_feedback_requests.append(request)
            return {
                "narration": "The grove reacts to your careful fieldwork.",
                "sentence_feedback": "Your sentence clearly states the intended action.",
                "suggested_sentence": "I want to collect the fungus sample.",
                "vocabulary_notes": [{"word": "fungus"}],
            }

    provider = MalformedVocabularyNotesProvider()
    engine = GameEngine.new_game(build_biology_realm(), ai_provider=provider)
    engine.state.current_room_id = "fungus_grove"
    before_state = deepcopy(engine.state)

    with pytest.raises(AIProviderUnavailable, match="AI turn feedback failed"):
        engine.handle("I want to collect the fungus sample")

    assert engine.state == before_state
    assert provider.turn_feedback_requests[0].deterministic_action == "collect"
    assert provider.turn_feedback_requests[0].deterministic_result.startswith(
        "You collect fungus sample."
    )


def test_inspecting_core_word_grants_xp_once_per_turn() -> None:
    engine = new_test_engine()
    engine.handle("go east")

    result = engine.handle("I want to inspect the microscope")

    assert result.success
    assert engine.state.player.xp == 5
    assert "microscope" in engine.state.mastered_words


def test_collect_visible_item_adds_it_to_inventory() -> None:
    engine = new_test_engine()
    engine.handle("go north")

    result = engine.handle("I want to collect the fungus sample")

    assert result.success
    assert "fungus sample" in engine.state.player.inventory
    assert "fungus sample" not in engine.state.current_room.items
    assert "fungus" in engine.state.mastered_words


def test_use_microscope_requires_sample() -> None:
    engine = new_test_engine()
    engine.handle("go east")

    result = engine.handle("I want to use the microscope")

    assert not result.success
    assert "fungus sample" in result.message


def test_use_microscope_with_sample_practices_words() -> None:
    engine = new_test_engine()
    engine.handle("go north")
    engine.handle("I want to collect the fungus sample")
    engine.handle("go south")
    engine.handle("go east")

    result = engine.handle("I want to use the microscope")

    assert result.success
    assert {"fungus", "microscope", "bacteria", "strain"} <= engine.state.mastered_words


def test_biology_quest_progress_awards_xp_once() -> None:
    engine = new_test_engine()
    engine.handle("go north")

    collect_result = engine.handle("I want to collect the fungus sample")

    assert collect_result.success
    assert "Quest updated" in collect_result.message
    assert "collect_fungus_sample" in engine.state.completed_tasks

    engine.handle("go south")
    engine.handle("go east")
    analyze_result = engine.handle("I want to use the microscope")
    xp_after_first_analysis = engine.state.player.xp
    repeat_result = engine.handle("I want to use the microscope")

    assert analyze_result.success
    assert "analyze_fungus_sample" in engine.state.completed_tasks
    assert "Quest updated" in analyze_result.message
    assert "Quest updated" not in repeat_result.message
    assert engine.state.player.xp == xp_after_first_analysis


def test_freeform_sentence_practices_contextual_room_words_once() -> None:
    engine = new_test_engine()
    engine.handle("go north")

    result = engine.handle("The fungus is vital for the old forest.")
    xp_after_first_sentence = engine.state.player.xp
    repeat_result = engine.handle("The fungus is vital for the old forest.")

    assert result.success
    assert "fungus" in engine.state.mastered_words
    assert "vital" in engine.state.mastered_words
    assert xp_after_first_sentence == 16
    assert repeat_result.success
    assert engine.state.player.xp == xp_after_first_sentence


def test_freeform_sentence_must_use_current_room_vocabulary() -> None:
    engine = new_test_engine()

    result = engine.handle("The microscope shows a bacterial strain.")

    assert not result.success
    assert "microscope" not in engine.state.mastered_words


def test_engine_returns_specific_english_feedback() -> None:
    engine = new_test_engine()

    result = engine.handle("I want go east")

    assert result.english_feedback == "Better English: I want to go ..."


def test_attack_visible_enemy_uses_deterministic_damage() -> None:
    engine = new_test_engine()
    engine.handle("go north")
    engine.handle("go north")

    result = engine.handle("I attack the invasive vine")

    assert result.success
    assert "6 damage" in result.message
    assert engine.state.enemy_hp["invasive_vine"] == 7
    assert engine.state.player.hp == 28


def test_defeating_enemy_awards_xp_and_practices_words_once() -> None:
    engine = new_test_engine()
    engine.handle("go north")
    engine.handle("go north")

    engine.handle("I attack the invasive vine")
    engine.handle("I attack the invasive vine")
    result = engine.handle("I attack the invasive vine")
    xp_after_defeat = engine.state.player.xp
    repeat_result = engine.handle("I attack the invasive vine")

    assert result.success
    assert "defeat" in result.message
    assert "Quest updated" in result.message
    assert "invasive_vine" in engine.state.defeated_enemies
    assert "clear_invasive_vine" in engine.state.completed_tasks
    assert {"mimicry", "creature", "extinction"} <= engine.state.mastered_words
    assert xp_after_defeat == 42
    assert not repeat_result.success
    assert engine.state.player.xp == xp_after_defeat


def test_cannot_attack_enemy_from_another_room() -> None:
    engine = new_test_engine()

    result = engine.handle("I attack the invasive vine")

    assert not result.success
    assert "do not see" in result.message


def test_full_biology_quest_can_be_completed() -> None:
    engine = new_test_engine()

    engine.handle("go north")
    engine.handle("I want to collect the fungus sample")
    engine.handle("go south")
    engine.handle("go east")
    engine.handle("I want to use the microscope")
    engine.handle("go west")
    engine.handle("go north")
    engine.handle("go north")
    engine.handle("I attack the invasive vine")
    engine.handle("I attack the invasive vine")
    engine.handle("I attack the invasive vine")
    result = engine.handle("status")

    assert result.success
    assert "Biology Investigation 3/3" in result.message
    assert "quest complete" in result.message
