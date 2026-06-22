from __future__ import annotations

from enum import Enum
from typing import Optional

from toefl_rpg.engine.state import GameState, VocabularyMastery


class LearningEvent(str, Enum):
    WORD_ENCOUNTERED = "word_encountered"
    USAGE_CORRECT = "usage_correct"
    USAGE_INCORRECT = "usage_incorrect"


def record_learning_event(
    state: GameState,
    event: LearningEvent,
    word: str,
    context_id: str,
    response_fingerprint: Optional[str] = None,
) -> VocabularyMastery:
    record = state.vocabulary_mastery.setdefault(word, VocabularyMastery(word=word))

    if event == LearningEvent.WORD_ENCOUNTERED:
        record.encounter_count += 1
        record.distinct_context_ids.add(context_id)
    elif event == LearningEvent.USAGE_CORRECT:
        record.correct_use_count += 1
        record.mastery_points += 1
        record.distinct_context_ids.add(context_id)
        if response_fingerprint:
            record.recent_response_fingerprints.append(response_fingerprint)
    elif event == LearningEvent.USAGE_INCORRECT:
        record.incorrect_use_count += 1
        record.distinct_context_ids.add(context_id)
        if response_fingerprint:
            record.recent_response_fingerprints.append(response_fingerprint)

    record.status = _derive_status(record)
    return record


def record_room_encounter(state: GameState) -> None:
    context_id = room_context_id(state.current_room_id)
    for word in state.current_room.target_words:
        record_learning_event(
            state,
            LearningEvent.WORD_ENCOUNTERED,
            word,
            context_id,
        )


def room_context_id(room_id: str) -> str:
    return f"room:{room_id}"


def response_fingerprint(sentence: str, word: str, context_id: str) -> str:
    normalized = " ".join(sentence.lower().split())
    return f"{normalized}|{word.lower()}|{context_id}"


def _derive_status(record: VocabularyMastery) -> str:
    if record.mastery_points >= 4 and record.review_stage > 0:
        return "mastered"
    if record.mastery_points > 0 or record.correct_use_count > 0:
        return "learning"
    if record.encounter_count > 0:
        return "encountered"
    return "new"
