from __future__ import annotations

from typing import Literal


DeterministicAction = Literal[
    "help",
    "move",
    "look",
    "inspect",
    "collect",
    "use",
    "talk",
    "attack",
    "review",
    "explain",
    "inventory",
    "status",
    "quit",
    "unknown",
]

DETERMINISTIC_ACTIONS: tuple[DeterministicAction, ...] = (
    "help",
    "move",
    "look",
    "inspect",
    "collect",
    "use",
    "talk",
    "attack",
    "review",
    "explain",
    "inventory",
    "status",
    "quit",
    "unknown",
)
