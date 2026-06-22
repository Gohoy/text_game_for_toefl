from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

from toefl_rpg.content.schema import World
from toefl_rpg.engine.state import GameState, Player


DEFAULT_SAVE_PATH = Path("data/saves/slot1.json")
SAVE_VERSION = 1


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

    _restore_room_items(world, payload.get("room_items"))
    return GameState(
        world=world,
        current_room_id=current_room_id,
        player=player,
        mastered_words=set(_string_list(payload.get("mastered_words"))),
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
