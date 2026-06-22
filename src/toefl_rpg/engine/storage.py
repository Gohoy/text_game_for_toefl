from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

from toefl_rpg.content.schema import World
from toefl_rpg.engine.state import GameState, Player, VocabularyMastery


DEFAULT_SAVE_PATH = Path("data/saves/slot1.json")
SAVE_VERSION = 1
MASTERY_VERSION = 1


def save_game(state: GameState, path: Path = DEFAULT_SAVE_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "version": SAVE_VERSION,
        "world_id": state.world.world_id,
        "current_room_id": state.current_room_id,
        "player": {
            "hp": state.player.hp,
            "max_hp": state.player.max_hp,
            "xp": state.player.xp,
            "inventory": state.player.inventory,
        },
        "mastered_words": sorted(state.mastered_words),
        "mastery": _mastery_payload(state),
        "active_review_word": state.active_review_word,
        "completed_tasks": sorted(state.completed_tasks),
        "enemy_hp": state.enemy_hp,
        "defeated_enemies": sorted(state.defeated_enemies),
        "room_items": {
            room_id: list(room.items) for room_id, room in state.world.rooms.items()
        },
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def load_game(world: World, path: Path = DEFAULT_SAVE_PATH) -> Optional[GameState]:
    if not path.exists():
        return None

    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("version") != SAVE_VERSION:
        return None
    if payload.get("world_id") != world.world_id:
        return None

    current_room_id = _string_value(payload, "current_room_id", world.start_room_id)
    if current_room_id not in world.rooms:
        current_room_id = world.start_room_id

    player_payload = payload.get("player", {})
    if not isinstance(player_payload, dict):
        player_payload = {}

    player = Player(
        hp=_int_value(player_payload, "hp", 30),
        max_hp=_int_value(player_payload, "max_hp", 30),
        xp=_int_value(player_payload, "xp", 0),
        inventory=_string_list(player_payload.get("inventory")),
    )

    mastered_words = set(_string_list(payload.get("mastered_words")))

    _restore_room_items(world, payload.get("room_items"))
    return GameState(
        world=world,
        current_room_id=current_room_id,
        player=player,
        mastered_words=mastered_words,
        vocabulary_mastery=_mastery_records(
            payload.get("mastery"),
            mastered_words,
        ),
        active_review_word=_optional_string(payload.get("active_review_word")),
        completed_tasks=set(_string_list(payload.get("completed_tasks"))),
        enemy_hp=_enemy_hp(payload.get("enemy_hp"), world),
        defeated_enemies=set(_valid_enemy_ids(payload.get("defeated_enemies"), world)),
    )


def _restore_room_items(world: World, room_items: Any) -> None:
    if not isinstance(room_items, dict):
        return
    for room_id, items in room_items.items():
        if room_id in world.rooms:
            world.rooms[room_id].items = _string_list(items)


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]


def _string_value(payload: dict[str, Any], key: str, default: str) -> str:
    value = payload.get(key)
    return value if isinstance(value, str) else default


def _int_value(payload: dict[str, Any], key: str, default: int) -> int:
    value = payload.get(key)
    return value if isinstance(value, int) else default


def _enemy_hp(value: Any, world: World) -> dict[str, int]:
    if not isinstance(value, dict):
        return {}
    restored: dict[str, int] = {}
    for enemy_id, hp in value.items():
        if isinstance(enemy_id, str) and enemy_id in world.enemies and isinstance(hp, int):
            restored[enemy_id] = max(0, min(hp, world.enemy(enemy_id).hp))
    return restored


def _valid_enemy_ids(value: Any, world: World) -> list[str]:
    return [enemy_id for enemy_id in _string_list(value) if enemy_id in world.enemies]


def _mastery_payload(state: GameState) -> dict[str, Any]:
    records = dict(state.vocabulary_mastery)
    for word in state.mastered_words:
        records.setdefault(word, _legacy_practiced_record(word))
    return {
        "version": MASTERY_VERSION,
        "words": {
            word: _mastery_record_payload(record)
            for word, record in sorted(records.items())
        },
    }


def _mastery_record_payload(record: VocabularyMastery) -> dict[str, Any]:
    return {
        "word": record.word,
        "status": record.status,
        "mastery_points": record.mastery_points,
        "encounter_count": record.encounter_count,
        "correct_use_count": record.correct_use_count,
        "incorrect_use_count": record.incorrect_use_count,
        "review_stage": record.review_stage,
        "last_practiced_at": record.last_practiced_at,
        "next_review_at": record.next_review_at,
        "distinct_context_ids": sorted(record.distinct_context_ids),
        "recent_response_fingerprints": list(record.recent_response_fingerprints),
    }


def _mastery_records(value: Any, mastered_words: set[str]) -> dict[str, VocabularyMastery]:
    records: dict[str, VocabularyMastery] = {}
    if isinstance(value, dict) and value.get("version") == MASTERY_VERSION:
        words_payload = value.get("words")
        if isinstance(words_payload, dict):
            for word, record_payload in words_payload.items():
                if isinstance(word, str) and isinstance(record_payload, dict):
                    records[word] = _mastery_record_from_payload(word, record_payload)

    for word in mastered_words:
        records.setdefault(word, _legacy_practiced_record(word))
    return records


def _mastery_record_from_payload(
    word: str,
    payload: dict[str, Any],
) -> VocabularyMastery:
    saved_word = payload.get("word")
    return VocabularyMastery(
        word=saved_word if isinstance(saved_word, str) else word,
        status=_string_value(payload, "status", "new"),
        mastery_points=max(0, _int_value(payload, "mastery_points", 0)),
        encounter_count=max(0, _int_value(payload, "encounter_count", 0)),
        correct_use_count=max(0, _int_value(payload, "correct_use_count", 0)),
        incorrect_use_count=max(0, _int_value(payload, "incorrect_use_count", 0)),
        review_stage=max(0, _int_value(payload, "review_stage", 0)),
        last_practiced_at=_optional_string(payload.get("last_practiced_at")),
        next_review_at=_optional_string(payload.get("next_review_at")),
        distinct_context_ids=set(_string_list(payload.get("distinct_context_ids"))),
        recent_response_fingerprints=_string_list(
            payload.get("recent_response_fingerprints")
        ),
    )


def _legacy_practiced_record(word: str) -> VocabularyMastery:
    return VocabularyMastery(
        word=word,
        status="learning",
        mastery_points=1,
        correct_use_count=1,
    )


def _optional_string(value: Any) -> Optional[str]:
    return value if isinstance(value, str) else None
