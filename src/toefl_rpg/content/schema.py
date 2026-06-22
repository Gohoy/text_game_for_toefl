from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, model_validator


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


class WorldPackRoom(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    description: str = Field(min_length=1)
    exits: dict[str, str] = Field(default_factory=dict)
    items: list[str] = Field(default_factory=list)
    npcs: list[str] = Field(default_factory=list)
    enemies: list[str] = Field(default_factory=list)
    target_words: list[str] = Field(default_factory=list)


class WorldPackEnemy(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    description: str = Field(min_length=1)
    hp: int = Field(gt=0)
    attack: int = Field(ge=0)
    defense: int = Field(ge=0)
    xp: int = Field(ge=0)
    target_words: list[str] = Field(default_factory=list)


class WorldPackQuestStep(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    objective: str = Field(min_length=1)
    xp: int = Field(ge=0)


class WorldPack(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: int = Field(default=1, ge=1)
    world_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    source_category: str = Field(min_length=1)
    difficulty: str = Field(min_length=1)
    start_room_id: str = Field(min_length=1)
    core_words: list[str] = Field(min_length=1)
    items: list[str] = Field(default_factory=list)
    npcs: list[str] = Field(default_factory=list)
    rooms: list[WorldPackRoom] = Field(min_length=1)
    enemies: list[WorldPackEnemy] = Field(default_factory=list)
    quest_task_ids: list[str] = Field(default_factory=list)
    quest_steps: list[WorldPackQuestStep] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_content_references(self) -> "WorldPack":
        _reject_duplicate_ids("room", [room.id for room in self.rooms])
        _reject_duplicate_ids("item", self.items)
        _reject_duplicate_ids("NPC", self.npcs)
        _reject_duplicate_ids("enemy", [enemy.id for enemy in self.enemies])
        _reject_duplicate_ids("quest task", self.quest_task_ids)
        _reject_duplicate_ids("quest step", [step.id for step in self.quest_steps])

        room_ids = {room.id for room in self.rooms}
        item_ids = set(self.items)
        npc_ids = set(self.npcs)
        enemy_ids = {enemy.id for enemy in self.enemies}
        quest_task_ids = set(self.quest_task_ids)

        if self.start_room_id not in room_ids:
            raise ValueError(
                f'world.start_room_id references missing room "{self.start_room_id}"'
            )

        for room in self.rooms:
            _reject_missing_targets(
                f"rooms[{room.id}].exits",
                "room",
                room.exits.items(),
                room_ids,
                include_key=True,
            )
            _reject_missing_targets(
                f"rooms[{room.id}].items",
                "item",
                ((None, item_id) for item_id in room.items),
                item_ids,
            )
            _reject_missing_targets(
                f"rooms[{room.id}].npcs",
                "NPC",
                ((None, npc_id) for npc_id in room.npcs),
                npc_ids,
            )
            _reject_missing_targets(
                f"rooms[{room.id}].enemies",
                "enemy",
                ((None, enemy_id) for enemy_id in room.enemies),
                enemy_ids,
            )

        for step in self.quest_steps:
            if step.id not in quest_task_ids:
                raise ValueError(
                    f'quest_steps[{step.id}].id references missing quest task "{step.id}"'
                )

        return self

    def to_world(self) -> World:
        return World(
            world_id=self.world_id,
            title=self.title,
            source_category=self.source_category,
            difficulty=self.difficulty,
            start_room_id=self.start_room_id,
            core_words=list(self.core_words),
            rooms={
                room.id: Room(
                    id=room.id,
                    name=room.name,
                    description=room.description,
                    exits=dict(room.exits),
                    items=list(room.items),
                    npcs=list(room.npcs),
                    enemies=list(room.enemies),
                    target_words=list(room.target_words),
                )
                for room in self.rooms
            },
            enemies={
                enemy.id: Enemy(
                    id=enemy.id,
                    name=enemy.name,
                    description=enemy.description,
                    hp=enemy.hp,
                    attack=enemy.attack,
                    defense=enemy.defense,
                    xp=enemy.xp,
                    target_words=list(enemy.target_words),
                )
                for enemy in self.enemies
            },
        )


def _reject_duplicate_ids(namespace: str, ids: list[str]) -> None:
    seen: set[str] = set()
    for content_id in ids:
        if content_id in seen:
            raise ValueError(f"duplicate {namespace} id: {content_id}")
        seen.add(content_id)


def _reject_missing_targets(
    source: str,
    target_type: str,
    references,
    valid_targets: set[str],
    include_key: bool = False,
) -> None:
    for source_key, target_id in references:
        if target_id in valid_targets:
            continue
        source_path = f"{source}.{source_key}" if include_key else source
        raise ValueError(
            f'{source_path} references missing {target_type} "{target_id}"'
        )
