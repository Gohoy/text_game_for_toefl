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


def test_collect_visible_item_adds_it_to_inventory() -> None:
    engine = GameEngine.new_game(build_biology_realm())
    engine.handle("go north")

    result = engine.handle("I want to collect the fungus sample")

    assert result.success
    assert "fungus sample" in engine.state.player.inventory
    assert "fungus sample" not in engine.state.current_room.items
    assert "fungus" in engine.state.mastered_words


def test_use_microscope_requires_sample() -> None:
    engine = GameEngine.new_game(build_biology_realm())
    engine.handle("go east")

    result = engine.handle("I want to use the microscope")

    assert not result.success
    assert "fungus sample" in result.message


def test_use_microscope_with_sample_practices_words() -> None:
    engine = GameEngine.new_game(build_biology_realm())
    engine.handle("go north")
    engine.handle("I want to collect the fungus sample")
    engine.handle("go south")
    engine.handle("go east")

    result = engine.handle("I want to use the microscope")

    assert result.success
    assert {"fungus", "microscope", "bacteria", "strain"} <= engine.state.mastered_words
