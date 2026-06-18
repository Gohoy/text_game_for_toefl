from __future__ import annotations

try:
    from rich.console import Console
    from rich.console import Group
    from rich.panel import Panel
    from rich.table import Table
except ModuleNotFoundError:
    Console = None
    Group = None
    Panel = None
    Table = None

from toefl_rpg.engine.state import GameState, TurnResult


class PlainConsole:
    def print(self, value: object = "") -> None:
        print(value)

    def input(self, prompt: str = "") -> str:
        clean_prompt = prompt.replace("[bold cyan]", "").replace("[/]", "")
        return input(clean_prompt)


def create_console() -> object:
    if Console is None:
        return PlainConsole()
    return Console()


class Renderer:
    def __init__(self, console: object) -> None:
        self.console = console

    def show_welcome(self) -> None:
        if Panel is None:
            self.console.print("=== TOEFL Text RPG ===")
            self.console.print(
                "Type full English sentences such as I want to inspect the microscope "
                "or short commands such as go east. Type quit to leave."
            )
            return

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
        vocabulary = ", ".join(room.target_words) or "none"
        inventory = ", ".join(state.player.inventory) or "empty"
        mastered = ", ".join(sorted(state.mastered_words)) or "none yet"

        if Table is None or Panel is None or Group is None:
            self.console.print("")
            self.console.print(f"=== {state.world.title}: {room.name} ===")
            self.console.print(room.description)
            self.console.print(f"Exits: {exits or 'none'}")
            self.console.print(f"Visible: {visible}")
            self.console.print(f"Vocabulary: {vocabulary}")
            self.console.print(f"Inventory: {inventory}")
            self.console.print(f"XP: {state.player.xp}")
            self.console.print(f"Mastered: {mastered}")
            return

        table = Table.grid(padding=(0, 2))
        table.add_column(style="bold")
        table.add_column()
        table.add_row("Location", room.name)
        table.add_row("Exits", exits or "none")
        table.add_row("Visible", visible)
        table.add_row("Vocabulary", vocabulary)
        table.add_row("Inventory", inventory)
        table.add_row("XP", str(state.player.xp))
        table.add_row("Mastered", mastered)

        body = Group(room.description, "", table)
        self.console.print(Panel(body, title=state.world.title, border_style="blue"))

    def show_result(self, result: TurnResult) -> None:
        if Panel is None:
            self.console.print(f"Result: {result.message}")
            if result.english_feedback:
                self.console.print(f"English Feedback: {result.english_feedback}")
            return

        style = "yellow" if not result.success else "green"
        self.console.print(Panel(result.message, title="Result", border_style=style))
        if result.english_feedback:
            self.console.print(
                Panel(result.english_feedback, title="English Feedback", border_style="magenta")
            )
