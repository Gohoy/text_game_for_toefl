from __future__ import annotations

from pydantic import BaseModel, Field


class Room(BaseModel):
    id: str
    name: str
    description: str
    exits: dict[str, str] = Field(default_factory=dict)
    items: list[str] = Field(default_factory=list)
    npcs: list[str] = Field(default_factory=list)
    enemies: list[str] = Field(default_factory=list)
    target_words: list[str] = Field(default_factory=list)


class Enemy(BaseModel):
    id: str
    name: str
    description: str
    hp: int
    attack: int
    defense: int
    xp: int
    target_words: list[str] = Field(default_factory=list)


class World(BaseModel):
    world_id: str
    title: str
    source_category: str
    difficulty: str
    start_room_id: str
    core_words: list[str]
    rooms: dict[str, Room]
    enemies: dict[str, Enemy] = Field(default_factory=dict)

    def room(self, room_id: str) -> Room:
        return self.rooms[room_id]

    def enemy(self, enemy_id: str) -> Enemy:
        return self.enemies[enemy_id]
