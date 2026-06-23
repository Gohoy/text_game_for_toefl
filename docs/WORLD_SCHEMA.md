# World Pack Schema

## Purpose

World packs are declarative content. They describe places, characters, items, enemies, quests, and target vocabulary. They do not own mutable runtime state or execute arbitrary rules.

All world packs must be validated before gameplay starts.

## Top-Level Contract

A minimal world pack contains:

```json
{
  "schema_version": 1,
  "world_id": "biology_realm_01",
  "title": "Biology Realm",
  "source_category": "生物",
  "difficulty": "A2-B1",
  "start_room_id": "field_station",
  "core_words": ["organism", "symbiosis", "metabolism"],
  "items": ["field notebook"],
  "item_descriptions": {
    "field notebook": "A notebook with field observations."
  },
  "npcs": ["Dr. Lin"],
  "rooms": [],
  "enemies": [],
  "quest_task_ids": ["collect_sample"],
  "quests": []
}
```

The current minimal Pydantic pack contract is implemented by `WorldPack`, `WorldPackRoom`, `WorldPackEnemy`, and `WorldPackQuestStep` in `src/toefl_rpg/content/schema.py`. It also includes simple top-level item, NPC, and quest task ID namespaces so room placements and quest steps can be checked before runtime conversion. This document explains the stable contract and validation rules.

## Stable ID Rules

- IDs use lowercase ASCII snake case.
- IDs are stable across prose edits.
- Each namespace has unique IDs.
- Saves and quest state reference IDs, not list positions or copied content objects.
- Renaming an ID requires an explicit save/content migration.

Suggested namespaces:

```text
world
room
npc
item
enemy
quest
objective
word_group
```

## Room Contract

A room should support:

```text
room_id
title
description
exits: direction → room_id
visible_item_ids
npc_ids
enemy_ids
target_words
tags
```

Runtime changes such as collected items or defeated enemies belong in player/world state, not by mutating the source JSON.

Current implementation note: room `items` and `npcs` are references to top-level string namespaces. They preserve the current runtime display names for compatibility. Optional top-level `item_descriptions` entries provide deterministic inspection details for known item IDs. A future schema can promote them to object records with separate stable IDs, names, descriptions, and tags.

## Item Contract

An item should support:

```text
item_id
name
description
portable
tags
usable_in_context_ids
```

An item effect should map to a deterministic rule or known effect type. World JSON must not contain executable Python or arbitrary expressions.

## NPC Contract

An NPC should support:

```text
npc_id
name
description
room_id or placement reference
dialogue/topic IDs
target_words
tags
```

AI may draft dialogue, but dialogue cannot directly complete a quest without a deterministic condition.

## Enemy Contract

An enemy should support:

```text
enemy_id
name
description
max_hp
damage or deterministic combat profile
target_words
tags
```

Combat rules, random policy, rewards, and defeat state remain in deterministic engine code.

## Quest Contract

A quest should support:

```text
quest_id
title
description
objective IDs
reward definition
```

Each objective must use a known deterministic condition type, for example:

```text
collect_item
use_item_in_room
defeat_enemy
visit_room
talk_to_npc
practice_word_in_context
```

Quest content supplies IDs and parameters. Engine code evaluates completion.

Current implementation note: `quest_task_ids` declares the deterministic quest task namespace, and every `quest_steps[].id` must reference that namespace.

## Cross-Reference Validation

Validation must reject:

- exits pointing to missing rooms
- placements pointing to missing items, NPCs, or enemies
- item descriptions pointing to missing item IDs
- quest steps pointing to missing quest task IDs
- duplicate IDs
- start rooms that do not exist
- core or room target words that violate the word format contract
- unsupported condition or effect types

Errors should identify:

```text
source object → field → invalid target
```

Example:

```text
rooms[river_bank].exits.east references missing room "old_lab"
```

The pack model validates required fields, forbids runtime-state fields, rejects duplicate room, item, NPC, enemy, quest task, and quest-step IDs, and rejects missing start-room, exit, placement, item-description, and quest-task references.

World packs are loaded through `load_world_pack(path)` in `src/toefl_rpg/content/loader.py`. Loader failures are reported as `WorldPackLoadError` with messages for missing files, invalid JSON locations, and schema validation details.

The Biology startup path uses `src/toefl_rpg/data/worlds/biology_realm_01.json` as the source of truth through `build_biology_realm()`. The legacy Python builder remains as a compatibility entry point, but it no longer owns hardcoded room or enemy content.

AI-generated world-pack drafts are not runtime content until they pass
`validate_world_pack_draft()` or `draft_world_pack()` in
`src/toefl_rpg/ai/drafts.py`. Those helpers accept only `world_pack` drafts and
reuse the `WorldPack` model, including duplicate-ID, missing-reference, and
runtime-state-field rejection.

## Schema Evolution

Every world pack has `schema_version`.

Rules:

- additive optional fields may retain the current version
- required-field changes or semantic changes require a version increment
- loaders either migrate supported old versions or reject them clearly
- save compatibility is considered before changing stable IDs
- generated content must target an explicit schema version

## Content Authoring Rules

- Start with one handcrafted Biology world.
- Validate all generated drafts before review or use.
- Keep descriptions concise enough for terminal play.
- Do not require exact prose in gameplay tests.
- Keep the full TOEFL vocabulary source outside the repository.
- Derived content should be small, traceable, and relevant to the selected world.
