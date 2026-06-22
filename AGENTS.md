# Agent Instructions

## Canonical Status

This is the canonical instruction file for all coding agents working in this repository.
Agent-specific files such as `CLAUDE.md` should point here instead of duplicating these rules.

## Mission

Build a complete, locally playable CLI text RPG that teaches TOEFL vocabulary through themed worlds, full-sentence English input, quests, combat, exploration, feedback, and spaced review.

The repository must remain runnable after every coherent change.

## Product Invariants

- The game runs in a terminal.
- The player should usually type full English sentences rather than only choose numbered options.
- Vocabulary is taught through context, action, memory, and consequence.
- Each world explores one subject deeply before the project expands to another subject.
- Text-native presentation is preferred: Rich panels, tables, ASCII maps, and concise descriptions.
- The core game must not require a paid AI service or network access.
- The full source vocabulary file must not be committed to this repository.

Primary local vocabulary source:

```text
/Users/gaohongyu1/Downloads/TOEFLiBT  词以类记2.0.txt
```

Importer tests must use small repository fixtures and must not depend on this user-local path.

## Deterministic Boundary

AI may propose or generate:

- narrative descriptions
- NPC dialogue
- grammar feedback drafts
- vocabulary explanations and examples
- quest and world-pack drafts

Deterministic code owns:

- HP, damage, XP, levels, and rewards
- inventory, item existence, and item use
- map movement and locked exits
- quest state and completion
- vocabulary mastery and review scheduling
- save/load and schema migration
- content validation and cross-reference checks

Rule: **AI may suggest; code decides.**

## Repository Direction

Preferred stack:

- Python
- Rich
- Pydantic
- Pytest
- JSON world packs and JSON saves

Preferred package shape:

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

Do not force this shape through a broad rewrite. Move toward it in small, behavior-preserving increments.

## Required Reading Order

At the start of each automated run:

1. Read this file.
2. Read `docs/ROADMAP.md`.
3. Read `docs/QUALITY_GATES.md`.
4. Read `docs/AUTOMATION_RUNBOOK.md`.
5. Read `docs/OVERVIEW_STRUCTURE_PLAN.md` when the task affects product or architecture.
6. Read the task-relevant design document, such as `docs/WORLD_SCHEMA.md` or `docs/LANGUAGE_LEARNING_DESIGN.md`.

Do not scan every file by default. Inspect the selected task, its tests, and the directly related implementation first.

## Mandatory Run Protocol

1. Run `git status --short --branch`.
2. Preserve all existing user changes.
3. Select exactly one ready, unblocked task from `docs/ROADMAP.md`.
4. If a task is too large for one run, split it before coding and implement only the first independently useful slice.
5. Inspect existing behavior and tests before editing.
6. Prefer a regression or characterization test before a behavior change.
7. Implement the smallest coherent vertical slice.
8. Run focused tests, then the required quality gates.
9. Update the appropriate documentation according to the documentation matrix below.
10. Commit only coherent, verified work.
11. Push when the remote is available and authentication succeeds.

Scheduled runs must not wait for broad clarification. When details are ambiguous, choose the smallest conservative implementation that preserves current behavior. If no safe implementation is possible, mark the task blocked with a precise unblock condition and stop.

## Work-Unit Rules

A normal automated run should:

- complete one task, not several unrelated tasks
- change one behavior or one internal seam
- avoid broad renames, formatting sweeps, and speculative abstractions
- avoid adding a dependency unless the selected task explicitly requires it
- keep public behavior backward compatible unless the roadmap task says otherwise
- prefer fewer than roughly 300 net changed lines, excluding generated fixtures and lockfiles

The line guideline is a scope signal, not a target. Split work when reviewability declines.

## Definition of Done

A task is done only when all applicable conditions hold:

- acceptance criteria in `docs/ROADMAP.md` are satisfied
- focused tests pass
- required quality gates pass
- the CLI remains runnable when relevant
- save compatibility is preserved or migrated explicitly
- malformed content fails with a useful error
- no local vocabulary source or secrets are committed
- user-visible behavior is documented
- roadmap status and next task are accurate

Do not mark a partially implemented feature done. Keep incomplete behavior behind an internal interface or mark the task `in_progress` or `blocked`.

## Documentation Ownership Matrix

| File | Purpose | Update Trigger |
| --- | --- | --- |
| `README.md` | User-facing setup, commands, and currently available gameplay | User-visible behavior or setup changes |
| `AGENTS.md` | Stable agent contract | Workflow invariant changes only |
| `CLAUDE.md` | Pointer to canonical agent rules | Rarely |
| `docs/OVERVIEW_STRUCTURE_PLAN.md` | Stable product vision and architecture direction | Product or architecture changes |
| `docs/ROADMAP.md` | Executable current queue and phase status | Every successful or blocked automation run |
| `docs/QUALITY_GATES.md` | Exact verification commands and definition of green | Tooling or test-command changes |
| `docs/AUTOMATION_RUNBOOK.md` | Scheduled-run procedure and failure handling | Automation-process changes |
| `docs/WORLD_SCHEMA.md` | World-pack contracts and content rules | Schema or content-contract changes |
| `docs/LANGUAGE_LEARNING_DESIGN.md` | Mastery, feedback, and review rules | Learning-rule changes |
| `docs/DECISIONS.md` | Short architecture decision records | Durable or hard-to-reverse decisions |

Do not copy status text between several documents. `ROADMAP.md` owns current execution status. Git history owns detailed historical chronology.

## Git Safety

Remote target:

```text
git@github.com:Gohoy/text_game_for_toefl.git
```

Rules:

- never use destructive reset, checkout, restore, clean, or history-rewrite commands on user work
- never force-push
- never commit unrelated changes
- never hide a failing test
- use small conventional commits containing the roadmap task ID when possible

Examples:

```text
test(content): characterize biology world data [T-110]
feat(content): load world packs from JSON [T-112]
fix(language): prevent duplicate mastery rewards [T-122]
docs(roadmap): split review milestone [T-123]
```
