from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from toefl_rpg.content.schema import Room, World


@dataclass
class Player:
    hp: int = 30
    max_hp: int = 30
    xp: int = 0
    inventory: list[str] = field(default_factory=list)


@dataclass
class VocabularyMastery:
    word: str
    status: str = "new"
    mastery_points: int = 0
    encounter_count: int = 0
    correct_use_count: int = 0
    incorrect_use_count: int = 0
    review_stage: int = 0
    last_practiced_at: Optional[str] = None
    next_review_at: Optional[str] = None
    distinct_context_ids: set[str] = field(default_factory=set)
    recent_response_fingerprints: list[str] = field(default_factory=list)


@dataclass
class GameState:
    world: World
    current_room_id: str
    player: Player = field(default_factory=Player)
    mastered_words: set[str] = field(default_factory=set)
    vocabulary_mastery: dict[str, VocabularyMastery] = field(default_factory=dict)
    active_review_word: Optional[str] = None
    completed_tasks: set[str] = field(default_factory=set)
    enemy_hp: dict[str, int] = field(default_factory=dict)
    defeated_enemies: set[str] = field(default_factory=set)

    @property
    def current_room(self) -> Room:
        return self.world.room(self.current_room_id)

    def live_enemy_ids_in_current_room(self) -> list[str]:
        return [
            enemy_id
            for enemy_id in self.current_room.enemies
            if enemy_id not in self.defeated_enemies
        ]


@dataclass(frozen=True)
class TurnResult:
    success: bool
    message: str
    english_feedback: str = ""
    should_quit: bool = False
