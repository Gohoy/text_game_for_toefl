from pathlib import Path

from toefl_rpg.ai.codex_cli import CodexCliProvider
from toefl_rpg.app import CODEX_TIMEOUT_ENV_VAR
from toefl_rpg.app import DEFAULT_CODEX_TIMEOUT_SECONDS
from toefl_rpg.app import SAVE_PATH_ENV_VAR
from toefl_rpg.app import build_ai_provider_from_env
from toefl_rpg.app import save_path_from_env
from toefl_rpg.engine.storage import DEFAULT_SAVE_PATH


def test_save_path_from_env_defaults_to_normal_slot(monkeypatch) -> None:
    monkeypatch.delenv(SAVE_PATH_ENV_VAR, raising=False)

    assert save_path_from_env() == DEFAULT_SAVE_PATH


def test_save_path_from_env_uses_configured_path(monkeypatch, tmp_path) -> None:
    save_path = tmp_path / "smoke-slot.json"
    monkeypatch.setenv(SAVE_PATH_ENV_VAR, str(save_path))

    assert save_path_from_env() == Path(save_path)


def test_codex_provider_from_env_uses_longer_default_timeout(monkeypatch) -> None:
    monkeypatch.delenv("TOEFL_RPG_AI_PROVIDER", raising=False)
    monkeypatch.delenv(CODEX_TIMEOUT_ENV_VAR, raising=False)

    provider = build_ai_provider_from_env()

    assert isinstance(provider, CodexCliProvider)
    assert provider.timeout_seconds == DEFAULT_CODEX_TIMEOUT_SECONDS


def test_codex_provider_from_env_uses_configured_timeout(monkeypatch) -> None:
    monkeypatch.delenv("TOEFL_RPG_AI_PROVIDER", raising=False)
    monkeypatch.setenv(CODEX_TIMEOUT_ENV_VAR, "240")

    provider = build_ai_provider_from_env()

    assert isinstance(provider, CodexCliProvider)
    assert provider.timeout_seconds == 240
