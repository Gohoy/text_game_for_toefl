from datetime import datetime, timezone

from toefl_rpg.ai.contract import FakeAIProvider
from toefl_rpg.content.sample_world import build_biology_realm
from toefl_rpg.engine.quests import (
    ANALYZE_FUNGUS_SAMPLE,
    CLEAR_INVASIVE_VINE,
    COLLECT_FUNGUS_SAMPLE,
)
from toefl_rpg.engine.rules import GameEngine
from toefl_rpg.engine.storage import load_game, save_game


def test_biology_quest_review_save_and_reload_end_to_end(tmp_path) -> None:
    now = datetime(2026, 6, 22, 8, 0, tzinfo=timezone.utc)
    provider = FakeAIProvider()
    engine = GameEngine.new_game(
        build_biology_realm(),
        ai_provider=provider,
        clock=lambda: now,
    )

    assert engine.handle("go north").success
    practice_result = engine.handle("The fungus is vital for the old forest.")
    review_prompt = engine.handle("review")
    review_result = engine.handle("A fungus can be vital for forest metabolism.")

    assert practice_result.success
    assert review_prompt.success
    assert review_result.success
    assert engine.state.active_review_word is None

    assert engine.handle("I want to collect the fungus sample").success
    assert engine.handle("go south").success
    assert engine.handle("go east").success
    assert engine.handle("I want to use the microscope").success
    assert engine.handle("go west").success
    assert engine.handle("go north").success
    assert engine.handle("go north").success
    assert engine.handle("I attack the invasive vine").success
    assert engine.handle("I attack the invasive vine").success
    assert engine.handle("I attack the invasive vine").success

    assert engine.state.completed_tasks == {
        COLLECT_FUNGUS_SAMPLE,
        ANALYZE_FUNGUS_SAMPLE,
        CLEAR_INVASIVE_VINE,
    }
    assert "invasive_vine" in engine.state.defeated_enemies
    assert engine.state.live_enemy_ids_in_current_room() == []
    assert "fungus sample" in engine.state.player.inventory

    fungus = engine.state.vocabulary_mastery["fungus"]
    assert fungus.review_stage == 1
    assert fungus.mastery_points >= 3
    assert fungus.next_review_at == "2026-06-23T08:00:00+00:00"
    assert {"fungus", "vital", "microscope", "bacteria", "strain"} <= engine.state.mastered_words
    assert provider.turn_feedback_requests

    save_path = tmp_path / "slot1.json"
    save_game(engine.state, save_path)
    loaded = load_game(build_biology_realm(), save_path)

    assert loaded is not None
    assert loaded.current_room_id == "mimicry_trail"
    assert loaded.completed_tasks == engine.state.completed_tasks
    assert loaded.player.inventory == engine.state.player.inventory
    assert loaded.defeated_enemies == {"invasive_vine"}
    assert loaded.active_review_word is None
    assert loaded.vocabulary_mastery["fungus"].review_stage == 1
    assert loaded.vocabulary_mastery["fungus"].next_review_at == "2026-06-23T08:00:00+00:00"
    assert "fungus sample" not in loaded.world.room("fungus_grove").items

    loaded_engine = GameEngine(
        loaded,
        ai_provider=FakeAIProvider(),
        clock=lambda: now,
    )
    status_result = loaded_engine.handle("status")

    assert status_result.success
    assert "Biology Investigation 3/3" in status_result.message
    assert "quest complete" in status_result.message
