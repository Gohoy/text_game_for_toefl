from __future__ import annotations

from pydantic import BaseModel, Field


class Room(BaseModel):
    id: str
    name: str
    description: str
    exits: dict[str, str] = Field(default_factory=dict)
    items: list[str] = Field(default_factory=list)
    npcs: list[str] = Field(default_factory=list)
    target_words: list[str] = Field(default_factory=list)


class World(BaseModel):
    world_id: str
    title: str
    source_category: str
    difficulty: str
    start_room_id: str
    core_words: list[str]
    rooms: dict[str, Room]

    def room(self, room_id: str) -> Room:
        return self.rooms[room_id]

