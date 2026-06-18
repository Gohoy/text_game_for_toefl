from __future__ import annotations

from rich.console import Console
from rich.console import Group
from rich.panel import Panel
from rich.table import Table

from toefl_rpg.engine.state import GameState, TurnResult


class Renderer:
    def __init__(self, console: Console) -> None:
        self.console = console

    def show_welcome(self) -> None:
        self.console.print(
            Panel(
                "Type full English sentences such as [bold]I want to inspect the microscope[/] "
                "or short commands such as [bold]go east[/]. Type [bold]quit[/] to leave.",
                title="TOEFL Text RPG",
                border_style="green",
            )
        )

    def show_state(self, state: GameState) -> None:
        room = state.current_room
        exits = ", ".join(f"{direction}: {target}" for direction, target in room.exits.items())
        visible = ", ".join(room.items + room.npcs) or "nothing notable"
        mastered = ", ".join(sorted(state.mastered_words)) or "none yet"

        table = Table.grid(padding=(0, 2))
        table.add_column(style="bold")
        table.add_column()
        table.add_row("Location", room.name)
        table.add_row("Exits", exits or "none")
        table.add_row("Visible", visible)
        table.add_row("XP", str(state.player.xp))
        table.add_row("Mastered", mastered)

        body = Group(room.description, "", table)
        self.console.print(Panel(body, title=state.world.title, border_style="blue"))

    def show_result(self, result: TurnResult) -> None:
        style = "yellow" if not result.success else "green"
        self.console.print(Panel(result.message, title="Result", border_style=style))
        if result.english_feedback:
            self.console.print(
                Panel(result.english_feedback, title="English Feedback", border_style="magenta")
            )
