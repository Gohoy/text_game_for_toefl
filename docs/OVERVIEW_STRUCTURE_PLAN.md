# TOEFL Text RPG Overview Structure Plan

## Goal

Build a complete playable CLI text RPG for TOEFL vocabulary learning. The player explores themed worlds, types full English sentences as actions, receives AI-agent language feedback, and masters TOEFL words through quests, combat, exploration, and review.

The game is AI-agent-first but not AI-chaotic:

- A local AI agent is required for the intended player experience.
- AI generates live narrative text, NPC dialogue, sentence feedback, vocabulary examples, explanations, and structured world content drafts.
- Code owns deterministic game rules such as HP, damage, XP, inventory, quest state, vocabulary mastery, save/load, and validation.

## Source Vocabulary

Primary vocabulary source:

```text
/Users/gaohongyu1/Downloads/TOEFLiBT  词以类记2.0.txt
```

The file is already grouped by subject and semantic categories. Subject categories should become RPG worlds. Semantic categories should become quest modifiers, character traits, dialogue styles, and skill challenges.

Initial subject worlds:

| Source Category | Game World | Gameplay Theme |
| --- | --- | --- |
| 生物 | Biology Realm | organisms, evolution, immunity, metabolism |
| 动物 | Animal Wildlands | predators, prey, migration, habitats |
| 地理 | Geography Frontier | terrain, maps, rivers, settlements |
| 环境与能源 | Ecology Crisis Zone | pollution, restoration, resources |
| 地质 | Geology Caverns | rocks, fossils, minerals, erosion |
| 医学 | Medical Citadel | symptoms, diagnosis, treatment |
| 经济 | Economy City | trade, markets, scarcity, policy |
| 天文 | Astronomy Observatory | planets, stars, orbit, exploration |

## Core Product Shape

```text
text_game_for_toefl/
├── CLAUDE.md
├── README.md
├── pyproject.toml
├── src/
│   └── toefl_rpg/
│       ├── __main__.py
│       ├── app.py
│       ├── cli/
│       │   ├── renderer.py
│       │   ├── prompt.py
│       │   └── commands.py
│       ├── engine/
│       │   ├── state.py
│       │   ├── rules.py
│       │   ├── combat.py
│       │   ├── movement.py
│       │   ├── inventory.py
│       │   └── quests.py
│       ├── language/
│       │   ├── evaluator.py
│       │   ├── parser.py
│       │   ├── feedback.py
│       │   └── spaced_review.py
│       ├── content/
│       │   ├── schema.py
│       │   ├── loader.py
│       │   ├── validator.py
│       │   └── importer.py
│       ├── ai/
│       │   ├── prompts.py
│       │   ├── structured_generation.py
│       │   └── cache.py
│       └── data/
│           ├── worlds/
│           ├── saves/
│           └── cache/
├── tests/
│   ├── test_combat.py
│   ├── test_vocab_importer.py
│   ├── test_world_schema.py
│   └── test_quest_progress.py
└── docs/
    ├── OVERVIEW_STRUCTURE_PLAN.md
    ├── GAME_DESIGN.md
    ├── WORLD_SCHEMA.md
    └── ROADMAP.md
```

## Gameplay Loop

```text
1. Show current room, visible NPCs/items/enemies, active task, and mini-map.
2. Player types a full English sentence.
3. Parser extracts a basic deterministic intent when possible.
4. AI agent interprets open-ended language, drafts feedback, and proposes narration in a structured format.
5. Rule engine validates whether the action is possible.
6. Deterministic systems update state: HP, XP, inventory, quest flags, mastery.
7. Validated AI feedback and narration are printed with the deterministic result.
8. Save progress automatically.
```

Example:

```text
> I want collect a sample from the polluted river.

Action understood: collect a sample from the river.
Better English: I want to collect a sample from the polluted river.
Result: You fill a glass tube with cloudy water.
XP +10
Words practiced: sample, polluted
```

## AI-Agent Boundary

AI is required to generate or enrich:

- room descriptions
- NPC dialogue
- quest text
- example sentences
- grammar feedback
- vocabulary definitions
- world packs in JSON
- combat narration after code calculates results

AI must not be the final authority for:

- damage numbers
- hit chance
- XP totals
- level thresholds
- whether an item exists
- whether the player can move through a locked exit
- whether a quest is completed
- save state mutations

## Structured Content Model

World content should be JSON and validated before use.

Minimum world pack:

```json
{
  "world_id": "biology_realm_01",
  "title": "Biology Realm",
  "source_category": "生物",
  "difficulty": "A2-B1",
  "core_words": ["parasite", "mimicry", "symbiosis", "organism"],
  "rooms": [],
  "npcs": [],
  "items": [],
  "enemies": [],
  "quests": []
}
```

The first data-driven version should include one handcrafted world pack before relying on generated world packs. This keeps content validation testable while the AI-agent runtime is added.

## First Playable Milestone

Scope:

- Python package with `python -m toefl_rpg`
- Rich-based CLI renderer
- one playable Biology Realm world
- movement between at least five rooms
- free-text sentence input for common actions
- deterministic combat
- three quests
- ten target words
- vocabulary mastery tracking
- save/load
- tests for rules and content validation

Initial Biology words:

```text
parasite
parasitic
mimicry
symbiosis
symbiotic
creature
organism
strain
species
vital
evolve
extinction
reproduction
respiration
immune
metabolism
microscope
bacteria
vaccine
fungus
```

## Continuous Codex Work Strategy

A recurring Codex automation should continue the project in small, verifiable increments. Each run should:

1. Read `CLAUDE.md` and this plan.
2. Check `git status`.
3. Pick the next smallest incomplete milestone.
4. Implement code or tests.
5. Run relevant tests.
6. Commit changes with a clear message.
7. Push to `git@github.com:Gohoy/text_game_for_toefl.git`.
8. Leave a short progress note in `docs/ROADMAP.md`.

The automation should avoid large rewrites and should keep the game playable after every run.
