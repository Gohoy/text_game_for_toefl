from pathlib import Path

from toefl_rpg.app import SAVE_PATH_ENV_VAR
from toefl_rpg.app import save_path_from_env
from toefl_rpg.engine.storage import DEFAULT_SAVE_PATH


def test_save_path_from_env_defaults_to_normal_slot(monkeypatch) -> None:
    monkeypatch.delenv(SAVE_PATH_ENV_VAR, raising=False)

    assert save_path_from_env() == DEFAULT_SAVE_PATH


def test_save_path_from_env_uses_configured_path(monkeypatch, tmp_path) -> None:
    save_path = tmp_path / "smoke-slot.json"
    monkeypatch.setenv(SAVE_PATH_ENV_VAR, str(save_path))

    assert save_path_from_env() == Path(save_path)
