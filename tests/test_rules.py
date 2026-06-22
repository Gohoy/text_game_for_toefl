from copy import deepcopy
from datetime import datetime, timezone

import pytest

from toefl_rpg.ai.contract import AIProviderUnavailable
from toefl_rpg.ai.contract import FakeAIProvider
from toefl_rpg.content.sample_world import build_biology_realm
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


def test_failed_ai_feedback_does_not_mutate_game_state() -> None:
    class FailingAIProvider:
        def generate_turn_feedback(self, request):
            raise RuntimeError("invalid provider output")

    engine = GameEngine.new_game(build_biology_realm(), ai_provider=FailingAIProvider())
    engine.state.current_room_id = "fungus_grove"

    with pytest.raises(RuntimeError, match="invalid provider output"):
        engine.handle("I want to collect the fungus sample")

    assert engine.state.current_room_id == "fungus_grove"
    assert engine.state.player.inventory == []
    assert "fungus sample" in engine.state.current_room.items
    assert engine.state.player.xp == 0
    assert engine.state.completed_tasks == set()
    assert engine.state.mastered_words == set()


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
