from __future__ import annotations

from dataclasses import dataclass


PLAYER_ATTACK = 7
PLAYER_DEFENSE = 1


@dataclass(frozen=True)
class CombatRound:
    player_damage: int
    enemy_damage: int
    enemy_defeated: bool


def calculate_damage(attack: int, defense: int) -> int:
    return max(1, attack - defense)
