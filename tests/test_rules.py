from toefl_rpg.content.sample_world import build_biology_realm
from toefl_rpg.engine.rules import GameEngine


def test_move_between_rooms() -> None:
    engine = GameEngine.new_game(build_biology_realm())

    result = engine.handle("I want to go to the east")

    assert result.success
    assert engine.state.current_room_id == "microscope_tent"


def test_inspecting_core_word_grants_xp_once_per_turn() -> None:
    engine = GameEngine.new_game(build_biology_realm())
    engine.handle("go east")

    result = engine.handle("I want to inspect the microscope")

    assert result.success
    assert engine.state.player.xp == 5
    assert "microscope" in engine.state.mastered_words

