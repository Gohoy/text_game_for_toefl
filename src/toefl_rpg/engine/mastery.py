from __future__ import annotations

from datetime import datetime, timezone
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


def record_rewardable_usage(
    state: GameState,
    word: str,
    context_id: str,
    sentence: str,
) -> bool:
    fingerprint = response_fingerprint(sentence, word, context_id)
    record = state.vocabulary_mastery.setdefault(word, VocabularyMastery(word=word))
    if fingerprint in record.recent_response_fingerprints:
        return False

    record_learning_event(
        state,
        LearningEvent.USAGE_CORRECT,
        word,
        context_id,
        fingerprint,
    )
    return True


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


def select_due_vocabulary(
    state: GameState,
    now: datetime,
    limit: Optional[int] = None,
) -> list[str]:
    normalized_now = _normalize_datetime(now)
    due_records = [
        record
        for record in state.vocabulary_mastery.values()
        if _is_due_for_review(record, normalized_now)
    ]
    due_records.sort(
        key=lambda record: (
            _parse_review_time(record.next_review_at),
            record.review_stage,
            record.word,
        )
    )
    due_words = [record.word for record in due_records]
    return due_words[:limit] if limit is not None else due_words


def _derive_status(record: VocabularyMastery) -> str:
    if record.mastery_points >= 4 and record.review_stage > 0:
        return "mastered"
    if record.mastery_points > 0 or record.correct_use_count > 0:
        return "learning"
    if record.encounter_count > 0:
        return "encountered"
    return "new"


def _is_due_for_review(record: VocabularyMastery, now: datetime) -> bool:
    if record.encounter_count == 0 and record.correct_use_count == 0:
        return False
    review_time = _parse_review_time(record.next_review_at)
    return review_time is not None and review_time <= now


def _parse_review_time(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return _normalize_datetime(parsed)


def _normalize_datetime(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)
