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


def test_biology_quest_progress_awards_xp_once() -> None:
    engine = GameEngine.new_game(build_biology_realm())
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
    engine = GameEngine.new_game(build_biology_realm())
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
    engine = GameEngine.new_game(build_biology_realm())

    result = engine.handle("The microscope shows a bacterial strain.")

    assert not result.success
    assert "microscope" not in engine.state.mastered_words


def test_engine_returns_specific_english_feedback() -> None:
    engine = GameEngine.new_game(build_biology_realm())

    result = engine.handle("I want go east")

    assert result.english_feedback == "Better English: I want to go ..."
