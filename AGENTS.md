# Agent Instructions

## Project

This repository contains a CLI text RPG for learning TOEFL vocabulary through themed worlds, free-form English input, quests, combat, and review.

Primary vocabulary source:

```text
/Users/gaohongyu1/Downloads/TOEFLiBT  词以类记2.0.txt
```

Do not copy the full source vocabulary file into the repository unless the user explicitly asks. Build import tools that can read the local file and produce validated, smaller game content.

## Product Principles

- The game must be playable from the terminal.
- The player should usually type full English sentences, not only select numbered choices.
- The game should teach vocabulary through context, action, memory, and consequence.
- Each world should focus on one topic deeply.
- Text-native visuals are preferred: ASCII maps, tables, panels, and concise room descriptions.
- Do not require paid image generation or OpenAI API image calls.

## AI Boundary

Use AI for:

- narrative descriptions
- NPC dialogue
- grammar feedback
- vocabulary explanations
- example sentences
- structured world-pack drafts
- quest ideas

Use deterministic code for:

- HP
- damage
- XP
- levels
- inventory
- map movement
- item existence
- quest completion
- vocabulary mastery
- save/load
- schema validation

Rule: AI may suggest; code decides.

## Architecture Direction

Preferred stack:

- Python
- Rich for terminal rendering
- Pydantic for structured world/content validation
- Pytest for tests
- JSON files for world packs and saves

Expected package shape:

```text
src/toefl_rpg/
├── __main__.py
├── app.py
├── cli/
├── engine/
├── language/
├── content/
├── ai/
└── data/
```

## Development Workflow

Before making changes:

1. Read `docs/OVERVIEW_STRUCTURE_PLAN.md`.
2. Check `git status --short --branch`.
3. Inspect existing code before editing.
4. Choose the smallest useful change that moves the game toward playability.

After making changes:

1. Run focused tests.
2. Run the game manually if relevant.
3. Update `docs/ROADMAP.md` with a short progress note.
4. Commit and push if the work is coherent.

Keep every commit small enough to review.

## Continuous Automation Instructions

Recurring Codex runs should continue the project without waiting for broad clarification. Use this priority order:

1. Create or repair the minimal playable CLI.
2. Add deterministic game systems.
3. Add vocabulary import and categorization.
4. Add one complete Biology Realm world.
5. Add language feedback and mastery tracking.
6. Add tests around rules and content validation.
7. Expand content only after the core game loop is stable.

Each automation run should leave the repository in a runnable state. If a run cannot finish a feature, hide incomplete work behind a clear interface and keep tests passing.

## Git Rules

- Remote target: `git@github.com:Gohoy/text_game_for_toefl.git`
- Preserve user changes.
- Do not use destructive git commands.
- Do not rewrite history unless the user explicitly asks.
- Commit only coherent work.
- Push after successful verification when possible.

