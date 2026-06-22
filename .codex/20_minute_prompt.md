# Codex 20-Minute Continuation Prompt

Continue building the TOEFL CLI text RPG in this repository:

```text
/Users/gaohongyu1/project/text_game_for_toefl
```

## Required Startup

1. Read `CLAUDE.md`.
2. Read `AGENTS.md` if it exists.
3. Read `docs/OVERVIEW_STRUCTURE_PLAN.md`.
4. Read `docs/ROADMAP.md`.
5. Check `git status --short --branch`.

Preserve user changes. Do not use destructive git commands.

## Product Direction

Build a complete playable terminal RPG for learning TOEFL vocabulary. The player should normally type English sentences, not only choose menu options.

Keep the core rule boundary strict:

- Deterministic code controls HP, damage, XP, inventory, map movement, item existence, quest completion, vocabulary mastery, save/load, and schema validation.
- AI or future generated content may suggest narrative, dialogue, explanations, examples, and world-pack drafts, but generated content must pass structured validation before use.

Preferred stack:

- Python
- Rich
- Pydantic
- Pytest
- JSON world packs and saves

## Run Strategy

Pick the smallest coherent milestone that moves the game toward a complete playable state. Prefer finishing one vertical slice over starting several partial systems.

Good next milestones include:

- improve the Biology Realm end-to-end play path
- add deterministic review or mastery mechanics
- add schema validation for world content
- add content loading from validated JSON
- improve parser coverage for natural English sentences
- add tests around rules, saves, content validation, and language feedback

Avoid large rewrites. Keep the game runnable after every run.

## Verification

Run focused tests for the changed area. If the change affects gameplay, also run a short manual smoke check with `PYTHONPATH=src python3 -m toefl_rpg` from a temporary directory so local save files do not affect the result.

Before finishing:

1. Update `docs/ROADMAP.md` with a short progress note.
2. Run `python3 -m pytest` when practical.
3. If the repository is coherent and verification passes, commit with a clear message and push to `origin/main`.
4. Leave the working tree clean unless there is a clear blocker.
