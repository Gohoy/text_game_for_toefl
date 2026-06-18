from __future__ import annotations

from dataclasses import dataclass, field

from toefl_rpg.content.schema import Room, World


@dataclass
class Player:
    hp: int = 30
    max_hp: int = 30
    xp: int = 0
    inventory: list[str] = field(default_factory=list)


@dataclass
class GameState:
    world: World
    current_room_id: str
    player: Player = field(default_factory=Player)
    mastered_words: set[str] = field(default_factory=set)
    completed_tasks: set[str] = field(default_factory=set)

    @property
    def current_room(self) -> Room:
        return self.world.room(self.current_room_id)


@dataclass(frozen=True)
class TurnResult:
    success: bool
    message: str
    english_feedback: str = ""
    should_quit: bool = False
