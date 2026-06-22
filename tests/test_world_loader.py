import json

import pytest

from tests.test_world_schema import minimal_world_pack_data
from toefl_rpg.content.loader import WorldPackLoadError
from toefl_rpg.content.loader import load_world_pack


def test_load_world_pack_returns_typed_schema(tmp_path) -> None:
    path = tmp_path / "world.json"
    path.write_text(json.dumps(minimal_world_pack_data()), encoding="utf-8")

    pack = load_world_pack(path)

    assert pack.world_id == "test_world"
    assert pack.to_world().room("start_room").name == "Start Room"


def test_load_world_pack_missing_file_has_actionable_message(tmp_path) -> None:
    path = tmp_path / "missing.json"

    with pytest.raises(WorldPackLoadError, match="World pack file not found"):
        load_world_pack(path)


def test_load_world_pack_invalid_json_has_location(tmp_path) -> None:
    path = tmp_path / "broken.json"
    path.write_text('{"world_id": ', encoding="utf-8")

    with pytest.raises(WorldPackLoadError) as exc_info:
        load_world_pack(path)

    message = str(exc_info.value)
    assert "Invalid JSON" in message
    assert "line 1" in message
    assert "column" in message


def test_load_world_pack_schema_error_includes_path_and_field(tmp_path) -> None:
    data = minimal_world_pack_data()
    del data["rooms"][0]["id"]
    path = tmp_path / "invalid_schema.json"
    path.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(WorldPackLoadError) as exc_info:
        load_world_pack(path)

    message = str(exc_info.value)
    assert "Invalid world pack schema" in message
    assert str(path) in message
    assert "rooms.0.id" in message
