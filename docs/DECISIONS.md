# Architecture Decisions

This file records durable decisions that future agents should not casually reverse.

Use a short ADR format. Add an entry only when a decision is difficult to reverse, affects several modules, or resolves a recurring ambiguity.

## Template

```md
## D-xxx — Title

- **Status:** accepted | superseded
- **Date:** YYYY-MM-DD
- **Context:** Why a decision is needed.
- **Decision:** What the project will do.
- **Consequences:** Benefits, costs, and constraints.
- **Supersedes:** D-xxx or none.
```

## D-001 — Deterministic code owns game state

- **Status:** accepted
- **Date:** 2026-06-22
- **Context:** Narrative generation and language assistance may be probabilistic, but RPG progression and learning state must be testable.
- **Decision:** HP, damage, XP, inventory, movement, quest state, mastery, review scheduling, saves, and validation are controlled by deterministic code.
- **Consequences:** AI output can enrich presentation but cannot mutate authoritative state directly.
- **Supersedes:** none.

## D-002 — World content uses validated JSON packs

- **Status:** accepted
- **Date:** 2026-06-22
- **Context:** Hardcoded worlds are difficult to expand and unsafe for generated content.
- **Decision:** Handcrafted or generated world content is represented as JSON and validated through typed schemas before use.
- **Consequences:** Content IDs and cross-references become stable contracts; runtime state remains outside content files.
- **Supersedes:** none.

## D-003 — The full TOEFL source remains external

- **Status:** accepted
- **Date:** 2026-06-22
- **Context:** The source file is large, local, and should not be copied into the repository.
- **Decision:** Import tools read the external file and produce small validated derived fixtures or world content.
- **Consequences:** Tests use small repository fixtures and remain portable.
- **Supersedes:** none.

## D-004 — Complete Biology before adding another world

- **Status:** accepted
- **Date:** 2026-06-22
- **Context:** Expanding content before the game loop and schema stabilize would multiply rework.
- **Decision:** The Biology world must complete a validated quest, combat, mastery, save, and review loop before a second world is implemented.
- **Consequences:** Early work prioritizes depth, schema stability, and test coverage over content volume.
- **Supersedes:** none.

## D-005 — Superseded optional-AI direction

- **Status:** superseded
- **Date:** 2026-06-22
- **Context:** The project should be locally playable and testable without paid services or credentials.
- **Decision:** The former direction treated AI as an additive layer rather than a required runtime collaborator.
- **Consequences:** This direction is no longer active; D-006 is the current AI architecture decision.
- **Supersedes:** none.

## D-006 — AI agent is required for the target game

- **Status:** accepted
- **Date:** 2026-06-22
- **Context:** The intended product is an AI-centered TOEFL RPG where live narration, rich sentence feedback, vocabulary explanation, and content drafting are core to the learning experience.
- **Decision:** The player-facing runtime requires a configured AI agent, with Codex CLI or an equivalent local agent bridge as the primary target. Tests may use fake providers, but the product should not permanently substitute deterministic-only feedback for AI interaction.
- **Consequences:** AI integration moves ahead of broader data migration work. Deterministic code still owns authoritative state changes, validation, HP, XP, quests, mastery, and saves. Missing AI configuration must fail clearly in runtime paths.
- **Supersedes:** D-005.
