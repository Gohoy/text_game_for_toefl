from __future__ import annotations

from toefl_rpg.cli.renderer import Renderer, create_console
from toefl_rpg.content.sample_world import build_biology_realm
from toefl_rpg.engine.rules import GameEngine
from toefl_rpg.engine.storage import DEFAULT_SAVE_PATH, load_game, save_game


def main() -> None:
    console = create_console()
    world = build_biology_realm()
    state = load_game(world, DEFAULT_SAVE_PATH)
    engine = GameEngine(state) if state is not None else GameEngine.new_game(world)
    renderer = Renderer(console)

    renderer.show_welcome(loaded=state is not None)
    while True:
        renderer.show_state(engine.state)
        command = console.input("[bold cyan]> [/]").strip()
        if not command:
            continue
        result = engine.handle(command)
        save_game(engine.state, DEFAULT_SAVE_PATH)
        renderer.show_result(result)
        if result.should_quit:
            break
