from __future__ import annotations

from toefl_rpg.cli.renderer import Renderer, create_console
from toefl_rpg.content.sample_world import build_biology_realm
from toefl_rpg.engine.rules import GameEngine


def main() -> None:
    console = create_console()
    world = build_biology_realm()
    engine = GameEngine.new_game(world)
    renderer = Renderer(console)

    renderer.show_welcome()
    while True:
        renderer.show_state(engine.state)
        command = console.input("[bold cyan]> [/]").strip()
        if not command:
            continue
        result = engine.handle(command)
        renderer.show_result(result)
        if result.should_quit:
            break
