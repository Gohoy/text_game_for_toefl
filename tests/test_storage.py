from toefl_rpg.content.sample_world import build_biology_realm
from toefl_rpg.engine.rules import GameEngine
from toefl_rpg.engine.storage import load_game, save_game


def test_save_and_load_restores_progress(tmp_path) -> None:
    save_path = tmp_path / "slot1.json"
    engine = GameEngine.new_game(build_biology_realm())
    engine.handle("go north")
    engine.handle("I want to collect the fungus sample")
    engine.handle("go south")

    save_game(engine.state, save_path)
    loaded = load_game(build_biology_realm(), save_path)

    assert loaded is not None
    assert loaded.current_room_id == "research_camp"
    assert loaded.player.xp == engine.state.player.xp
    assert loaded.player.inventory == ["fungus sample"]
    assert "fungus" in loaded.mastered_words
    assert "collect_fungus_sample" in loaded.completed_tasks
    assert "fungus sample" not in loaded.world.room("fungus_grove").items


def test_load_missing_save_returns_none(tmp_path) -> None:
    loaded = load_game(build_biology_realm(), tmp_path / "missing.json")

    assert loaded is None
