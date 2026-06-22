# Roadmap

## How This File Is Used

This is the executable queue for humans and scheduled agents. It is not a chronological diary.

Allowed task states:

```text
planned | ready | in_progress | blocked | done
```

Rules:

- at most one task may be `in_progress`
- a scheduled run completes or advances only one task
- every task needs acceptance criteria and verification
- dependencies must be explicit
- tasks that cannot fit one run must be split
- only the most recent completed items are retained here; Git history is the long-term record

## Current Phase

**Phase 1 — Stabilize an AI-centered Biology learning loop**

The project already has a playable Biology CLI with movement, items, a three-step quest, deterministic combat, autosave, vocabulary sentence practice, XP, and AI-backed turn feedback through a required provider.

The current goal is to make AI-agent interaction a required core part of the Biology loop while preserving deterministic authority over game state, rewards, saves, and validation.

## Phase 1 Exit Criteria

Phase 1 is complete when:

- current Biology behavior is protected by characterization or integration tests
- a required AI-agent interface exists for narration, sentence feedback, vocabulary explanations, and structured content drafts
- missing AI-agent configuration fails clearly in player runtime paths
- tests can use fake AI providers without network or paid API access
- Biology world content loads from a validated JSON world pack
- content references are checked deterministically
- vocabulary mastery has an explicit persisted model
- repeated identical actions cannot farm unlimited mastery rewards
- at least one deterministic delayed-review flow exists
- a new game can complete the Biology quest and review loop end to end
- saves remain compatible or have an explicit schema migration

## Current Capabilities

- terminal startup through `python -m toefl_rpg`
- Rich-based room presentation
- five-room Biology world
- full-sentence action parsing for common actions
- movement, inspection, inventory, collect, and use
- deterministic combat
- a three-step Biology Investigation quest
- contextual target-word practice
- AI-backed turn narration and sentence feedback through Codex CLI or the explicit fake test provider
- deterministic placeholder English corrections retained only for tests/development
- JSON autosave and load
- external vocabulary importer
- focused tests for several existing systems

## Latest Player-Role Assessment

2026-06-22 assessment: the current Biology quest is playable and now routes turn feedback through the AI-provider boundary, but it is not yet a complete TOEFL learning loop.

Evidence from an in-memory playthrough:

- the three-step Biology quest can be completed through movement, collecting the fungus sample, using the microscope, and defeating the invasive vine
- the game rewards contextual sentences such as `The harmless creature uses mimicry to avoid extinction.`
- sentence feedback now comes from a configured provider in normal runtime, with fake-provider smoke coverage for automation
- vocabulary learning is mostly word spotting; the game does not ask the player to prove meaning, choose a correct usage, compare wrong/right examples, or recall words later
- narrative and NPC text are static, so repeated play does not feel conversational or adaptive
- one ambiguous learner sentence, `I want collect a sample with the microscope`, was interpreted as collecting the microscope, showing that open-ended input needs AI interpretation plus deterministic validation

Conclusion: continue with T-111 next. The next development work should move current Biology content toward a validated world-pack schema before adding more content. AI feedback is now wired into the turn loop, while deterministic code remains the authority for state changes and rewards.

## Required AI Direction

AI is not optional for the target product. The game should use Codex CLI or an equivalent local AI-agent bridge for live narration, rich sentence feedback, vocabulary explanations, NPC dialogue, and structured content drafting. Deterministic code remains the final authority for parser fallbacks, rule validation, HP, XP, inventory, quest completion, mastery, save/load, and schema validation.

## Active Task

None.

## Ready Queue

### T-110 — Characterize the current Biology world

- **State:** done
- **Priority:** P0
- **Goal:** Protect current world behavior before moving content out of code.
- **Scope:** Add focused tests or fixtures that capture room IDs, exits, item placement, enemy placement, target words, and the three quest steps.
- **Acceptance criteria:**
  - tests fail if a required current room or quest step disappears
  - tests do not depend on exact prose
  - existing behavior remains unchanged
- **Verification:**
  - `python3 -m pytest -q`
- **Non-goals:** No JSON migration and no schema redesign.
- **Dependencies:** None.

## Planned Queue

### T-105 — Define the required AI-agent runtime contract

- **State:** done
- **Priority:** P0
- **Goal:** Establish the required AI-agent interface before wiring live Codex CLI calls into gameplay.
- **Scope:** Add documentation and testable interface contracts for AI narration, sentence feedback, vocabulary explanation, and structured response validation.
- **Acceptance criteria:**
  - runtime design states that AI is required for player-facing narration and feedback
  - tests can use a fake provider without network or paid API calls
  - missing provider behavior is specified as a clear runtime configuration error, not silent deterministic fallback
  - deterministic rule engine remains authoritative for game-state changes
- **Verification:**
  - documentation path checks
  - focused interface tests if code is added
  - `python3 -m pytest -q`
- **Non-goals:** No live subprocess call to Codex CLI in this task.
- **Dependencies:** T-110.

### T-106 — Add a Codex CLI AI provider

- **State:** done
- **Priority:** P0
- **Goal:** Call the local Codex CLI through a structured provider for narration and feedback.
- **Acceptance criteria:**
  - provider invokes Codex CLI through a bounded subprocess adapter
  - output is parsed as structured data and validated before display
  - timeouts and missing executable errors are user-readable
  - tests cover command construction and validation with fakes
- **Verification:** focused provider tests and full suite.
- **Dependencies:** T-105.

### T-107 — Use AI feedback in the gameplay loop

- **State:** done
- **Priority:** P0
- **Goal:** Replace placeholder English feedback in normal play with required AI-agent feedback while preserving deterministic rewards.
- **Acceptance criteria:**
  - player sentence feedback comes from the AI provider in runtime
  - deterministic fallback grammar rules are retained only for tests or explicit development mode
  - invalid AI output does not mutate game state
  - CLI smoke documents AI configuration requirements
- **Verification:** parser/feedback tests, provider tests, CLI smoke with fake provider.
- **Dependencies:** T-106.

### T-111 — Define the minimal world-pack schema

- **State:** done
- **Priority:** P0
- **Goal:** Add Pydantic models for the fields already required by the current Biology world.
- **Acceptance criteria:**
  - valid minimal world data loads
  - missing required IDs and duplicate IDs fail clearly
  - schema does not embed runtime state
- **Verification:**
  - focused schema tests
  - full test suite
- **Non-goals:** Cross-reference validation and generated world content.
- **Dependencies:** T-107.

### T-112 — Add a JSON world-pack loader

- **State:** done
- **Priority:** P0
- **Goal:** Load and validate a world pack from a repository JSON file.
- **Acceptance criteria:**
  - loader returns the typed schema model
  - missing file, invalid JSON, and schema errors have actionable messages
  - no gameplay path changes yet
- **Verification:** loader tests and full suite.
- **Dependencies:** T-111.

### T-113 — Encode the current Biology world as JSON

- **State:** ready
- **Priority:** P0
- **Goal:** Create one handcrafted Biology world pack matching current behavior.
- **Acceptance criteria:**
  - content passes schema validation
  - room IDs, exits, items, enemies, words, and quest steps match T-110
  - no full TOEFL source file is copied
- **Verification:** schema/content tests.
- **Dependencies:** T-112.

### T-114 — Switch Biology startup to the JSON loader

- **State:** planned
- **Priority:** P0
- **Goal:** Use the validated world pack at runtime without changing player-visible behavior.
- **Acceptance criteria:**
  - characterization tests remain green
  - CLI smoke test passes
  - old hardcoded content is removed only when no longer referenced
- **Verification:** focused tests, full suite, CLI smoke.
- **Dependencies:** T-113.

### T-115 — Validate cross-references

- **State:** planned
- **Priority:** P0
- **Goal:** Reject exits, item references, enemy references, and quest references that point to missing IDs.
- **Acceptance criteria:**
  - each invalid reference type has a focused test
  - error messages identify the source object and bad target ID
- **Verification:** schema/validator tests and full suite.
- **Dependencies:** T-114.

### T-120 — Add a persisted vocabulary mastery record

- **State:** planned
- **Priority:** P1
- **Goal:** Represent per-word learning state explicitly and save it.
- **Acceptance criteria:**
  - new saves contain versioned mastery data
  - older saves load with safe defaults or an explicit migration
  - mastery state is independent from narrative text
- **Verification:** mastery tests, save round-trip tests, full suite.
- **Dependencies:** T-115.

### T-121 — Record encounter and practice events

- **State:** planned
- **Priority:** P1
- **Goal:** Update mastery deterministically when a word is encountered or correctly practiced.
- **Acceptance criteria:**
  - events are defined in code
  - correct and incorrect use have distinct effects
  - tests use an injected or deterministic context
- **Verification:** focused mastery tests and full suite.
- **Dependencies:** T-120.

### T-122 — Prevent mastery reward farming

- **State:** planned
- **Priority:** P1
- **Goal:** Stop repeated identical sentence use in the same context from awarding unlimited mastery or XP.
- **Acceptance criteria:**
  - first valid contextual use is rewarded
  - immediate duplicate use is recognized but not rewarded again
  - a genuinely new context can become rewardable
- **Verification:** regression tests and full suite.
- **Dependencies:** T-121.

### T-123 — Select vocabulary due for review

- **State:** planned
- **Priority:** P1
- **Goal:** Add a deterministic review-due selector based on the learning design.
- **Acceptance criteria:**
  - selector is testable without real-time sleeps
  - due ordering is stable
  - unseen words are not treated as overdue reviews
- **Verification:** spaced-review tests and full suite.
- **Dependencies:** T-122.

### T-124 — Add one playable review flow

- **State:** planned
- **Priority:** P1
- **Goal:** Let the player review due Biology words through the terminal.
- **Acceptance criteria:**
  - at least one command or post-quest flow presents due words
  - a correct full-sentence response updates mastery
  - feedback and save behavior remain deterministic
- **Verification:** parser/review tests, save tests, CLI smoke.
- **Dependencies:** T-123.

### T-130 — Add an end-to-end Biology completion test

- **State:** planned
- **Priority:** P1
- **Goal:** Script a new game through quest completion and one review outcome.
- **Acceptance criteria:**
  - test covers movement, collect, use, combat, quest completion, practice, save, and reload
  - test asserts state, not exact decorative prose
  - test runs with a fake AI provider and no paid API access
- **Verification:** end-to-end test and full suite.
- **Dependencies:** T-124.

## Blocked Tasks

None.

Use this format when needed:

```md
### T-xxx — Title

- **State:** blocked
- **Priority:** Pn
- **Blocker:** Exact technical or product blocker.
- **Evidence:** Commands, errors, or code paths already inspected.
- **Unblock condition:** Smallest fact or change required.
- **Next investigation:** One concrete next step.
```

## Future Phases

### Phase 2 — AI language feedback reliability

- normalize parser intent structures
- separate deterministic action authority from AI coaching text
- add regression corpora for common learner sentences
- validate AI feedback shape and failure modes

### Phase 3 — Content authoring and import

- validate small derived vocabulary packs
- map source categories to world-pack drafts
- add authoring diagnostics and content linting
- keep the full source vocabulary outside the repository

### Phase 4 — AI content generation expansion

- expand provider-neutral interfaces
- require structured outputs and validation
- add cache and clear regeneration rules
- support generated world-pack drafts without giving AI authority over state

### Phase 5 — Second complete world

Add a second world only after the Biology world satisfies its full phase exit criteria. Reuse the validated schema and learning loop rather than cloning hardcoded logic.

## Recently Completed

- 2026-06-22: Completed T-112 by adding `load_world_pack(path)`, actionable loader errors for missing files, invalid JSON, and schema failures, plus focused loader tests.
- 2026-06-22: Completed T-111 by adding minimal `WorldPack` Pydantic models, duplicate room/enemy ID validation, runtime-state field rejection, conversion to the existing runtime `World`, and focused schema tests.
- 2026-06-22: Completed T-107 by routing normal turn feedback through the required AI provider, keeping deterministic feedback behind explicit test/development paths, rolling back state on AI feedback failure, and documenting fake-provider CLI smoke.
- 2026-06-22: Completed T-106 by adding a bounded Codex CLI provider that requests schema-validated JSON, handles missing executable and timeout failures, and is covered by fake-runner tests.
- 2026-06-22: Completed T-105 by adding the required AI-agent contract, validated request/response models, a fake provider for tests, and explicit missing-provider behavior.
- 2026-06-22: Updated project direction to make the AI agent required and central, with deterministic code retained as the authority for game-state changes.
- 2026-06-22: Completed T-110 by adding characterization tests for the current Biology world identity, topology, content placement, enemy contract, target words, and quest steps.
- 2026-06-22: Adopted the Codex automation documentation bundle, including the runbook, quality gates, world schema notes, learning design notes, and the `.codex/20_minute_prompt.md` scheduled prompt.

Keep at most ten items here.

- Established the initial playable Biology CLI, deterministic systems, vocabulary practice, autosave, importer, language feedback, combat, and quest integration.
