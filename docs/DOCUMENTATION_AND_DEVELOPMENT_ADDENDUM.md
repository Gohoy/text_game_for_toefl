# Documentation and Development Addendum

This addendum describes how the existing project documents should be reorganized for reliable scheduled development.

## Recommended Document Roles

### `README.md`

Audience: players and contributors.

Keep:

- one-paragraph product description
- installation and run commands
- current user-visible commands
- short development/test commands
- link to the overview

Remove:

- internal automation policy
- speculative future architecture
- long progress histories

### `AGENTS.md`

Audience: all coding agents.

Make it the single canonical operational contract. Keep stable product invariants, deterministic/AI boundaries, the required run protocol, quality expectations, documentation ownership, and Git safety.

Do not maintain a second full copy in `CLAUDE.md`.

### `CLAUDE.md`

Audience: Claude-specific entry point.

Keep it as a short pointer to `AGENTS.md` and the required reading order.

### `docs/OVERVIEW_STRUCTURE_PLAN.md`

Audience: product and architecture readers.

Keep:

- product goal and core gameplay loop
- world/category mapping
- system boundaries
- target architecture
- milestone sequence

Remove or avoid:

- per-run progress notes
- rapidly changing task status
- duplicated test commands

Link to specialist documents for world schema and learning rules.

### `docs/ROADMAP.md`

Audience: scheduled agents and maintainers.

Make it the only source of truth for current execution status. Use machine-scannable tasks with state, priority, scope, acceptance criteria, verification, non-goals, and dependencies.

Do not use it as an unlimited diary. Retain only recent completions.

### `docs/QUALITY_GATES.md`

Audience: implementers and CI.

Store exact commands and the definition of a green run. This prevents each agent from inventing a different verification standard.

### `docs/AUTOMATION_RUNBOOK.md`

Audience: the scheduled Codex task.

Store task selection, dirty-worktree behavior, failure handling, scope limits, documentation updates, commit/push steps, and final reporting.

### `docs/WORLD_SCHEMA.md`

Audience: content and engine developers.

Own the declarative content contract, stable IDs, reference validation, and schema evolution.

### `docs/LANGUAGE_LEARNING_DESIGN.md`

Audience: language-system and gameplay developers.

Own mastery events, reward rules, anti-farming, review scheduling, and feedback contracts.

### `docs/DECISIONS.md`

Audience: future maintainers and agents.

Record only durable architectural decisions. Do not add routine implementation notes.

## Recommended Development Sequence

1. Protect current Biology behavior with tests.
2. Define a minimal typed world schema.
3. Load one handcrafted Biology JSON world pack.
4. Add cross-reference validation.
5. Add versioned, persisted vocabulary mastery.
6. Add bounded rewards and anti-farming.
7. Add deterministic review scheduling and one playable review flow.
8. Add an end-to-end Biology completion test.
9. Improve language feedback behind stable interfaces.
10. Add optional AI adapters with deterministic fallback.
11. Add a second world only after the Biology loop is complete.

This sequence minimizes rework: content expansion follows stable rules, rather than forcing rules to chase generated content.
