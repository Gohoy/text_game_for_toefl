from __future__ import annotations

import os
from pathlib import Path

from toefl_rpg.ai.codex_cli import CodexCliProvider
from toefl_rpg.ai.codex_cli import CodexCliProviderError
from toefl_rpg.ai.contract import AIProvider
from toefl_rpg.ai.contract import AIProviderUnavailable
from toefl_rpg.ai.contract import FakeAIProvider
from toefl_rpg.cli.renderer import Renderer, create_console
from toefl_rpg.content.sample_world import build_biology_realm
from toefl_rpg.engine.rules import GameEngine
from toefl_rpg.engine.storage import DEFAULT_SAVE_PATH, load_game, save_game


SAVE_PATH_ENV_VAR = "TOEFL_RPG_SAVE_PATH"


def build_ai_provider_from_env() -> AIProvider:
    provider_name = os.environ.get("TOEFL_RPG_AI_PROVIDER", "codex").strip().lower()
    if provider_name == "fake":
        return FakeAIProvider()
    if provider_name not in {"", "codex"}:
        raise ValueError(
            "Unsupported TOEFL_RPG_AI_PROVIDER. Use 'codex' for normal play or 'fake' for smoke tests."
        )
    executable = os.environ.get("TOEFL_RPG_CODEX_EXECUTABLE", "codex")
    timeout = int(os.environ.get("TOEFL_RPG_CODEX_TIMEOUT", "60"))
    return CodexCliProvider(executable=executable, timeout_seconds=timeout)


def save_path_from_env() -> Path:
    configured_path = os.environ.get(SAVE_PATH_ENV_VAR, "").strip()
    if configured_path:
        return Path(configured_path)
    return DEFAULT_SAVE_PATH


def main() -> None:
    console = create_console()
    world = build_biology_realm()
    save_path = save_path_from_env()
    state = load_game(world, save_path)
    try:
        ai_provider = build_ai_provider_from_env()
    except ValueError as exc:
        console.print(f"AI provider error: {exc}")
        return
    engine = (
        GameEngine(state, ai_provider=ai_provider)
        if state is not None
        else GameEngine.new_game(world, ai_provider=ai_provider)
    )
    renderer = Renderer(console)

    renderer.show_welcome(loaded=state is not None)
    while True:
        renderer.show_state(engine.state)
        command = console.input("[bold cyan]> [/]").strip()
        if not command:
            continue
        try:
            result = engine.handle(command)
        except (AIProviderUnavailable, CodexCliProviderError) as exc:
            console.print(f"AI provider error: {exc}")
            break
        save_game(engine.state, save_path)
        renderer.show_result(result)
        if result.should_quit:
            break
