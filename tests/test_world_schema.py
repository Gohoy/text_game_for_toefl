import pytest
from pydantic import ValidationError

from toefl_rpg.content.schema import WorldPack


def minimal_world_pack_data() -> dict:
    return {
        "schema_version": 1,
        "world_id": "test_world",
        "title": "Test World",
        "source_category": "生物",
        "difficulty": "A2",
        "start_room_id": "start_room",
        "core_words": ["organism"],
        "rooms": [
            {
                "id": "start_room",
                "name": "Start Room",
                "description": "A room for schema tests.",
                "exits": {},
                "items": ["field notebook"],
                "npcs": ["Dr. Lin"],
                "enemies": ["test_enemy"],
                "target_words": ["organism"],
            }
        ],
        "enemies": [
            {
                "id": "test_enemy",
                "name": "Test Enemy",
                "description": "An enemy for schema tests.",
                "hp": 5,
                "attack": 1,
                "defense": 0,
                "xp": 3,
                "target_words": ["organism"],
            }
        ],
        "quest_steps": [
            {
                "id": "collect_sample",
                "title": "Collect a sample",
                "objective": "Collect the sample.",
                "xp": 10,
            }
        ],
    }


def test_valid_minimal_world_pack_converts_to_runtime_world() -> None:
    pack = WorldPack.model_validate(minimal_world_pack_data())

    world = pack.to_world()

    assert world.world_id == "test_world"
    assert world.start_room_id == "start_room"
    assert list(world.rooms) == ["start_room"]
    assert world.room("start_room").items == ["field notebook"]
    assert world.room("start_room").enemies == ["test_enemy"]
    assert world.enemy("test_enemy").hp == 5


def test_world_pack_requires_room_id() -> None:
    data = minimal_world_pack_data()
    del data["rooms"][0]["id"]

    with pytest.raises(ValidationError) as exc_info:
        WorldPack.model_validate(data)

    assert "rooms.0.id" in str(exc_info.value)


def test_world_pack_rejects_duplicate_room_ids() -> None:
    data = minimal_world_pack_data()
    data["rooms"].append({**data["rooms"][0], "name": "Duplicate Start Room"})

    with pytest.raises(ValidationError, match="duplicate room id: start_room"):
        WorldPack.model_validate(data)


def test_world_pack_rejects_duplicate_enemy_ids() -> None:
    data = minimal_world_pack_data()
    data["enemies"].append({**data["enemies"][0], "name": "Duplicate Enemy"})

    with pytest.raises(ValidationError, match="duplicate enemy id: test_enemy"):
        WorldPack.model_validate(data)


def test_world_pack_rejects_duplicate_quest_step_ids() -> None:
    data = minimal_world_pack_data()
    data["quest_steps"].append({**data["quest_steps"][0], "title": "Duplicate Quest Step"})

    with pytest.raises(ValidationError, match="duplicate quest step id: collect_sample"):
        WorldPack.model_validate(data)


def test_world_pack_rejects_runtime_state_fields() -> None:
    data = minimal_world_pack_data()
    data["player"] = {"hp": 30}

    with pytest.raises(ValidationError) as exc_info:
        WorldPack.model_validate(data)

    assert "Extra inputs are not permitted" in str(exc_info.value)
