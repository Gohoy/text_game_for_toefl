from toefl_rpg.content.sample_world import build_biology_realm
from toefl_rpg.engine.mastery import LearningEvent
from toefl_rpg.engine.mastery import record_learning_event
from toefl_rpg.engine.mastery import response_fingerprint
from toefl_rpg.engine.rules import GameEngine
from toefl_rpg.engine.state import GameState


def new_test_engine() -> GameEngine:
    return GameEngine.new_game(
        build_biology_realm(),
        use_deterministic_feedback=True,
    )


def test_learning_events_have_distinct_deterministic_effects() -> None:
    state = GameState(
        world=build_biology_realm(),
        current_room_id="research_camp",
    )

    record_learning_event(
        state,
        LearningEvent.WORD_ENCOUNTERED,
        "organism",
        "room:research_camp",
    )
    record_learning_event(
        state,
        LearningEvent.USAGE_INCORRECT,
        "organism",
        "room:research_camp",
        "bad sentence|organism|room:research_camp",
    )
    record_learning_event(
        state,
        LearningEvent.USAGE_CORRECT,
        "organism",
        "room:research_camp",
        "the organism can evolve|organism|room:research_camp",
    )

    record = state.vocabulary_mastery["organism"]
    assert record.status == "learning"
    assert record.encounter_count == 1
    assert record.incorrect_use_count == 1
    assert record.correct_use_count == 1
    assert record.mastery_points == 1
    assert record.distinct_context_ids == {"room:research_camp"}
    assert record.recent_response_fingerprints == [
        "bad sentence|organism|room:research_camp",
        "the organism can evolve|organism|room:research_camp",
    ]


def test_new_game_and_movement_record_room_encounters_without_xp() -> None:
    engine = new_test_engine()

    assert engine.state.player.xp == 0
    assert engine.state.vocabulary_mastery["organism"].status == "encountered"
    assert engine.state.vocabulary_mastery["organism"].encounter_count == 1
    assert engine.state.vocabulary_mastery["organism"].mastery_points == 0

    engine.handle("go north")

    fungus = engine.state.vocabulary_mastery["fungus"]
    assert engine.state.player.xp == 0
    assert fungus.status == "encountered"
    assert fungus.encounter_count == 1
    assert fungus.distinct_context_ids == {"room:fungus_grove"}


def test_correct_contextual_use_updates_mastery_record() -> None:
    engine = new_test_engine()
    engine.handle("go north")

    result = engine.handle("The fungus is vital for the old forest.")

    assert result.success
    fungus = engine.state.vocabulary_mastery["fungus"]
    vital = engine.state.vocabulary_mastery["vital"]
    assert fungus.status == "learning"
    assert fungus.encounter_count == 1
    assert fungus.correct_use_count == 1
    assert fungus.mastery_points == 1
    assert vital.correct_use_count == 1
    assert vital.mastery_points == 1


def test_incorrect_contextual_attempt_updates_mastery_without_reward() -> None:
    engine = new_test_engine()
    sentence = "The microscope shows a bacterial strain."

    result = engine.handle(sentence)

    assert not result.success
    assert engine.state.player.xp == 0
    assert engine.state.mastered_words == set()
    microscope = engine.state.vocabulary_mastery["microscope"]
    assert microscope.status == "new"
    assert microscope.incorrect_use_count == 1
    assert microscope.correct_use_count == 0
    assert microscope.mastery_points == 0
    assert microscope.distinct_context_ids == {"room:research_camp"}
    assert microscope.recent_response_fingerprints == [
        response_fingerprint(sentence, "microscope", "room:research_camp")
    ]
