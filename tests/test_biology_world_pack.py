from pathlib import Path

from toefl_rpg.content.loader import load_world_pack
from toefl_rpg.content.sample_world import BIOLOGY_WORLD_PACK_PATH
from toefl_rpg.content.sample_world import build_biology_realm
from toefl_rpg.engine.quests import BIOLOGY_STEPS


BIOLOGY_PACK_PATH = Path("src/toefl_rpg/data/worlds/biology_realm_01.json")


def test_runtime_biology_world_uses_repository_pack() -> None:
    assert BIOLOGY_WORLD_PACK_PATH.samefile(BIOLOGY_PACK_PATH)


def test_biology_world_pack_matches_current_runtime_world() -> None:
    pack = load_world_pack(BIOLOGY_PACK_PATH)
    packed_world = pack.to_world()
    runtime_world = build_biology_realm()

    assert packed_world.world_id == runtime_world.world_id
    assert packed_world.title == runtime_world.title
    assert packed_world.source_category == runtime_world.source_category
    assert packed_world.difficulty == runtime_world.difficulty
    assert packed_world.start_room_id == runtime_world.start_room_id
    assert packed_world.core_words == runtime_world.core_words
    assert set(packed_world.rooms) == set(runtime_world.rooms)
    assert set(packed_world.enemies) == set(runtime_world.enemies)

    for room_id, runtime_room in runtime_world.rooms.items():
        packed_room = packed_world.room(room_id)
        assert packed_room.name == runtime_room.name
        assert packed_room.exits == runtime_room.exits
        assert packed_room.items == runtime_room.items
        assert packed_room.npcs == runtime_room.npcs
        assert packed_room.enemies == runtime_room.enemies
        assert packed_room.target_words == runtime_room.target_words

    for enemy_id, runtime_enemy in runtime_world.enemies.items():
        packed_enemy = packed_world.enemy(enemy_id)
        assert packed_enemy.name == runtime_enemy.name
        assert packed_enemy.hp == runtime_enemy.hp
        assert packed_enemy.attack == runtime_enemy.attack
        assert packed_enemy.defense == runtime_enemy.defense
        assert packed_enemy.xp == runtime_enemy.xp
        assert packed_enemy.target_words == runtime_enemy.target_words


def test_biology_world_pack_matches_current_quest_steps() -> None:
    pack = load_world_pack(BIOLOGY_PACK_PATH)

    assert [(step.id, step.title, step.objective, step.xp) for step in pack.quest_steps] == [
        (step.id, step.title, step.objective, step.xp) for step in BIOLOGY_STEPS
    ]
