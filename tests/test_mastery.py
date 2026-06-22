from datetime import datetime, timezone

from toefl_rpg.content.sample_world import build_biology_realm
from toefl_rpg.engine.mastery import LearningEvent
from toefl_rpg.engine.mastery import record_learning_event
from toefl_rpg.engine.mastery import record_rewardable_usage
from toefl_rpg.engine.mastery import response_fingerprint
from toefl_rpg.engine.mastery import select_due_vocabulary
from toefl_rpg.engine.rules import GameEngine
from toefl_rpg.engine.state import GameState, VocabularyMastery


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


def test_rewardable_usage_suppresses_duplicate_fingerprint() -> None:
    state = GameState(
        world=build_biology_realm(),
        current_room_id="research_camp",
    )

    first = record_rewardable_usage(
        state,
        "organism",
        "room:research_camp",
        "The organism can evolve.",
    )
    duplicate = record_rewardable_usage(
        state,
        "organism",
        "room:research_camp",
        "The organism can evolve.",
    )
    new_context = record_rewardable_usage(
        state,
        "organism",
        "quest:biology:explain_organism",
        "The organism can evolve.",
    )

    record = state.vocabulary_mastery["organism"]
    assert first is True
    assert duplicate is False
    assert new_context is True
    assert record.correct_use_count == 2
    assert record.mastery_points == 2
    assert record.distinct_context_ids == {
        "room:research_camp",
        "quest:biology:explain_organism",
    }


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


def test_duplicate_contextual_sentence_does_not_award_again() -> None:
    engine = new_test_engine()
    engine.handle("go north")

    first_result = engine.handle("The fungus is vital for the old forest.")
    xp_after_first = engine.state.player.xp
    duplicate_result = engine.handle("The fungus is vital for the old forest.")

    fungus = engine.state.vocabulary_mastery["fungus"]
    assert first_result.success
    assert duplicate_result.success
    assert xp_after_first == 16
    assert engine.state.player.xp == xp_after_first
    assert fungus.correct_use_count == 1
    assert fungus.mastery_points == 1


def test_same_word_can_be_rewarded_in_a_new_context() -> None:
    engine = new_test_engine()
    engine.handle("go north")

    sentence_result = engine.handle("The fungus is vital for the old forest.")
    collect_result = engine.handle("I want to collect the fungus sample")

    fungus = engine.state.vocabulary_mastery["fungus"]
    assert sentence_result.success
    assert collect_result.success
    assert engine.state.player.xp == 31
    assert fungus.correct_use_count == 2
    assert fungus.mastery_points == 2
    assert {
        "room:fungus_grove",
        "collect:fungus_sample",
    } <= fungus.distinct_context_ids


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


def test_due_vocabulary_selector_orders_due_words_stably() -> None:
    state = GameState(
        world=build_biology_realm(),
        current_room_id="research_camp",
        vocabulary_mastery={
            "vital": VocabularyMastery(
                word="vital",
                encounter_count=1,
                review_stage=2,
                next_review_at="2026-06-22T08:00:00+00:00",
            ),
            "fungus": VocabularyMastery(
                word="fungus",
                correct_use_count=1,
                review_stage=1,
                next_review_at="2026-06-22T07:00:00Z",
            ),
            "bacteria": VocabularyMastery(
                word="bacteria",
                correct_use_count=1,
                review_stage=0,
                next_review_at="2026-06-22T08:00:00+00:00",
            ),
            "microscope": VocabularyMastery(
                word="microscope",
                correct_use_count=1,
                next_review_at="2026-06-23T08:00:00+00:00",
            ),
        },
    )

    due_words = select_due_vocabulary(
        state,
        datetime(2026, 6, 22, 8, 30, tzinfo=timezone.utc),
    )

    assert due_words == ["fungus", "bacteria", "vital"]


def test_due_vocabulary_selector_supports_limit_and_naive_clock() -> None:
    state = GameState(
        world=build_biology_realm(),
        current_room_id="research_camp",
        vocabulary_mastery={
            "fungus": VocabularyMastery(
                word="fungus",
                correct_use_count=1,
                next_review_at="2026-06-22T07:00:00+00:00",
            ),
            "vital": VocabularyMastery(
                word="vital",
                correct_use_count=1,
                next_review_at="2026-06-22T08:00:00+00:00",
            ),
        },
    )

    due_words = select_due_vocabulary(state, datetime(2026, 6, 22, 9, 0), limit=1)

    assert due_words == ["fungus"]


def test_due_vocabulary_selector_ignores_unseen_words() -> None:
    state = GameState(
        world=build_biology_realm(),
        current_room_id="research_camp",
        vocabulary_mastery={
            "fungus": VocabularyMastery(
                word="fungus",
                next_review_at="2026-06-21T08:00:00+00:00",
            ),
            "vital": VocabularyMastery(
                word="vital",
                encounter_count=1,
                next_review_at=None,
            ),
            "strain": VocabularyMastery(
                word="strain",
                correct_use_count=1,
                next_review_at="not-a-date",
            ),
        },
    )

    due_words = select_due_vocabulary(
        state,
        datetime(2026, 6, 22, 8, 0, tzinfo=timezone.utc),
    )

    assert due_words == []


def test_review_flow_prompts_due_word_and_advances_on_full_sentence() -> None:
    now = datetime(2026, 6, 22, 8, 0, tzinfo=timezone.utc)
    engine = GameEngine.new_game(
        build_biology_realm(),
        use_deterministic_feedback=True,
        clock=lambda: now,
    )
    engine.handle("go north")
    engine.handle("The fungus is vital for the old forest.")

    prompt_result = engine.handle("review")

    assert prompt_result.success
    assert "Review due: fungus, vital" in prompt_result.message
    assert engine.state.active_review_word == "fungus"

    review_result = engine.handle("A fungus can be vital for forest metabolism.")

    fungus = engine.state.vocabulary_mastery["fungus"]
    assert review_result.success
    assert "Review complete" in review_result.message
    assert engine.state.active_review_word is None
    assert fungus.review_stage == 1
    assert fungus.mastery_points == 2
    assert fungus.correct_use_count == 2
    assert fungus.last_practiced_at == "2026-06-22T08:00:00+00:00"
    assert fungus.next_review_at == "2026-06-23T08:00:00+00:00"
    assert engine.state.player.xp == 26


def test_review_flow_keeps_word_active_after_incorrect_sentence() -> None:
    now = datetime(2026, 6, 22, 8, 0, tzinfo=timezone.utc)
    engine = GameEngine.new_game(
        build_biology_realm(),
        use_deterministic_feedback=True,
        clock=lambda: now,
    )
    engine.handle("go north")
    engine.handle("The fungus is vital for the old forest.")
    engine.handle("review")

    result = engine.handle("It matters.")

    fungus = engine.state.vocabulary_mastery["fungus"]
    assert not result.success
    assert engine.state.active_review_word == "fungus"
    assert fungus.review_stage == 0
    assert fungus.incorrect_use_count == 1
    assert fungus.next_review_at == "2026-06-22T08:10:00+00:00"
