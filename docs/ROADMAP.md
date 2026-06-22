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
- five-room Biology world loaded from the validated JSON world pack
- full-sentence action parsing for common actions
- verbose directional sentences such as `I go north to the fungus grove.`
- movement, inspection, inventory, collect, and use
- deterministic combat
- a three-step Biology Investigation quest
- contextual target-word practice
- AI-backed turn narration and sentence feedback through Codex CLI or the explicit fake test provider
- structured AI interpretation contract for advisory open-ended sentence parsing
- AI interpretation fallback for parser misses, with deterministic validation of rooms, items, enemies, and rewards
- AI-backed NPC dialogue grounded in room, quest, visible entity, and vocabulary context
- AI-backed room look narration grounded in deterministic room state
- deterministic placeholder English corrections retained only for tests/development
- JSON autosave and load
- versioned vocabulary mastery records in saves, with legacy-save defaults
- deterministic mastery events for encounters, correct use, and incorrect attempts
- duplicate response fingerprints suppress repeat mastery and XP rewards
- deterministic review-due vocabulary selector with injected clock
- playable `review` command for due vocabulary, full-sentence review answers, and persisted review stages
- end-to-end Biology quest, review, save, and reload coverage with a fake AI provider
- AI vocabulary explanation command for visible or practiced Biology words
- external vocabulary importer
- focused tests for several existing systems

## Latest Player-Role Assessment

2026-06-22 assessment: the current Biology quest is playable and now routes turn feedback, parser-miss interpretation, NPC dialogue, and room look narration through the AI-provider boundary, but AI-generated content drafts still need schema validation before the project expands authoring.

Evidence from an in-memory playthrough:

- the three-step Biology quest can be completed through movement, collecting the fungus sample, using the microscope, and defeating the invasive vine
- the game rewards contextual sentences such as `The harmless creature uses mimicry to avoid extinction.`
- sentence feedback now comes from a configured provider in normal runtime, with fake-provider smoke coverage for automation
- vocabulary learning now includes same-session delayed review through `review`, but the correctness check is still a simple deterministic full-sentence/word-use gate
- a fake-provider playtest can now interpret `Could you grab the specimen for my research?` as collecting the visible fungus sample, while deterministic validation still rejects invented targets such as `crystal sample`
- `talk to Dr. Lin` now requests validated AI dialogue without mutating quest state, XP, inventory, saves, or mastery
- `look` now requests validated AI room narration without mutating exits, items, NPCs, enemies, quest state, XP, inventory, saves, or mastery
- verbose movement sentences such as `I go north to the fungus grove.` resolve through deterministic parsing

Conclusion: continue with T-132 next. Biology startup now uses the validated JSON pack without changing player-visible behavior, cross-reference validation rejects bad content before runtime conversion, saves carry a versioned vocabulary mastery record, deterministic learning events update mastery records, duplicate response fingerprints suppress repeat rewards, a playable review command advances due words in stable order, an end-to-end test protects quest completion plus review persistence, visible or practiced vocabulary can be explained through the required AI provider without mutating deterministic state, verbose directional sentences now resolve to deterministic movement intents, parser misses can use validated AI interpretation before deterministic engine validation, NPC dialogue is AI-generated but display-only, and room look narration is AI-generated from deterministic room context. AI feedback is wired into the turn loop, while deterministic code remains the authority for state changes, content validation, and rewards.

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

- **State:** done
- **Priority:** P0
- **Goal:** Create one handcrafted Biology world pack matching current behavior.
- **Acceptance criteria:**
  - content passes schema validation
  - room IDs, exits, items, enemies, words, and quest steps match T-110
  - no full TOEFL source file is copied
- **Verification:** schema/content tests.
- **Dependencies:** T-112.

### T-114 — Switch Biology startup to the JSON loader

- **State:** done
- **Priority:** P0
- **Goal:** Use the validated world pack at runtime without changing player-visible behavior.
- **Acceptance criteria:**
  - characterization tests remain green
  - CLI smoke test passes
  - old hardcoded content is removed only when no longer referenced
- **Verification:** focused tests, full suite, CLI smoke.
- **Dependencies:** T-113.

### T-115 — Validate cross-references

- **State:** done
- **Priority:** P0
- **Goal:** Reject exits, item references, enemy references, and quest references that point to missing IDs.
- **Acceptance criteria:**
  - each invalid reference type has a focused test
  - error messages identify the source object and bad target ID
- **Verification:** schema/validator tests and full suite.
- **Dependencies:** T-114.

### T-120 — Add a persisted vocabulary mastery record

- **State:** done
- **Priority:** P1
- **Goal:** Represent per-word learning state explicitly and save it.
- **Acceptance criteria:**
  - new saves contain versioned mastery data
  - older saves load with safe defaults or an explicit migration
  - mastery state is independent from narrative text
- **Verification:** mastery tests, save round-trip tests, full suite.
- **Dependencies:** T-115.

### T-121 — Record encounter and practice events

- **State:** done
- **Priority:** P1
- **Goal:** Update mastery deterministically when a word is encountered or correctly practiced.
- **Acceptance criteria:**
  - events are defined in code
  - correct and incorrect use have distinct effects
  - tests use an injected or deterministic context
- **Verification:** focused mastery tests and full suite.
- **Dependencies:** T-120.

### T-122 — Prevent mastery reward farming

- **State:** done
- **Priority:** P1
- **Goal:** Stop repeated identical sentence use in the same context from awarding unlimited mastery or XP.
- **Acceptance criteria:**
  - first valid contextual use is rewarded
  - immediate duplicate use is recognized but not rewarded again
  - a genuinely new context can become rewardable
- **Verification:** regression tests and full suite.
- **Dependencies:** T-121.

### T-123 — Select vocabulary due for review

- **State:** done
- **Priority:** P1
- **Goal:** Add a deterministic review-due selector based on the learning design.
- **Acceptance criteria:**
  - selector is testable without real-time sleeps
  - due ordering is stable
  - unseen words are not treated as overdue reviews
- **Verification:** spaced-review tests and full suite.
- **Dependencies:** T-122.

### T-124 — Add one playable review flow

- **State:** done
- **Priority:** P1
- **Goal:** Let the player review due Biology words through the terminal.
- **Acceptance criteria:**
  - at least one command or post-quest flow presents due words
  - a correct full-sentence response updates mastery
  - feedback and save behavior remain deterministic
- **Verification:** parser/review tests, save tests, CLI smoke.
- **Dependencies:** T-123.

### T-130 — Add an end-to-end Biology completion test

- **State:** done
- **Priority:** P1
- **Goal:** Script a new game through quest completion and one review outcome.
- **Acceptance criteria:**
  - test covers movement, collect, use, combat, quest completion, practice, save, and reload
  - test asserts state, not exact decorative prose
  - test runs with a fake AI provider and no paid API access
- **Verification:** end-to-end test and full suite.
- **Dependencies:** T-124.

### T-125 — Add an AI vocabulary explanation command

- **State:** done
- **Priority:** P1
- **Goal:** Let the player ask for a focused explanation of a visible or practiced Biology word through the AI provider.
- **Acceptance criteria:**
  - command validates that the requested word is known in the current world before calling AI
  - AI explanation output is structured and displayed without mutating deterministic game state
  - missing or invalid AI output fails clearly and preserves state
- **Verification:** provider/request tests, parser/engine tests, CLI smoke with fake provider.
- **Dependencies:** T-130.

### T-126 — Improve structured interpretation for verbose movement

- **State:** done
- **Priority:** P1
- **Goal:** Handle common full-sentence movement phrasing such as `I go north to the fungus grove`.
- **Acceptance criteria:**
  - parser or validated AI interpretation maps verbose direction sentences to deterministic move intents
  - movement remains rejected when the selected exit is not available
  - tests cover at least one accepted verbose sentence and one rejected impossible move
- **Verification:** parser/engine tests and CLI smoke.
- **Dependencies:** T-125.

### T-127 — Add a structured AI interpretation contract

- **State:** done
- **Priority:** P1
- **Goal:** Define the AI-provider request and validated response shape for interpreting open-ended player sentences into proposed game intents.
- **Acceptance criteria:**
  - contract includes player sentence, current room context, visible entities, exits, and target words
  - response is limited to known deterministic actions and a proposed target
  - invalid response shapes fail clearly before reaching engine state mutation
  - fake provider supports deterministic tests without paid API access
- **Verification:** AI contract tests and provider validation tests.
- **Dependencies:** T-126.

### T-128 — Use AI interpretation as a validated fallback

- **State:** done
- **Priority:** P1
- **Goal:** When deterministic parsing returns unknown, ask the AI provider for a structured interpretation and then run the deterministic engine validation.
- **Acceptance criteria:**
  - fallback is used only after deterministic parser rules miss
  - AI cannot invent unavailable rooms, items, enemies, XP, or quest completion
  - ambiguous or invalid AI interpretations produce a clear player message without state mutation
  - tests cover one accepted open-ended command and one rejected AI-invented target
- **Verification:** parser/engine/provider tests and CLI smoke with fake provider.
- **Dependencies:** T-127.

### T-129 — Add AI-backed NPC dialogue

- **State:** done
- **Priority:** P1
- **Goal:** Make `talk to Dr. Lin` use a structured AI dialogue response while deterministic code still owns quest state and rewards.
- **Acceptance criteria:**
  - dialogue request includes NPC, room, quest progress, and visible target words
  - response is validated before display
  - AI dialogue cannot mutate inventory, XP, quest state, mastery, or saves
  - missing or invalid AI output fails clearly and preserves state
- **Verification:** AI contract tests, engine tests, CLI smoke with fake provider.
- **Dependencies:** T-128.

### T-131 — Add AI-backed room look narration

- **State:** done
- **Priority:** P1
- **Goal:** Make `look` request structured AI room narration while deterministic room state remains authoritative.
- **Acceptance criteria:**
  - narration request includes room, exits, visible entities, quest progress, and target words
  - AI output is validated before display
  - failed or invalid narration preserves state and reports a clear provider error
  - deterministic room descriptions remain available as validated context, not as mutable state
- **Verification:** AI contract tests, engine tests, CLI smoke with fake provider.
- **Dependencies:** T-129.

### T-132 — Validate AI content drafts against schema

- **State:** ready
- **Priority:** P1
- **Goal:** Ensure structured AI world or quest drafts are schema-validated before any authored content can be used.
- **Acceptance criteria:**
  - draft request includes theme, required words, and intended content type
  - returned draft is parsed into typed models or rejected with a useful error
  - invalid references cannot enter runtime world content
  - tests use fake providers and small fixtures only
- **Verification:** AI contract tests, world schema tests, full suite.
- **Dependencies:** T-131.

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

- 2026-06-22: Completed T-131 by adding structured AI room narration requests and responses, routing `look` through the AI provider, validating narration before display, and preserving deterministic room, quest, XP, inventory, mastery, and save state.
- 2026-06-22: Completed T-129 by adding structured AI NPC dialogue requests and responses, routing `talk to Dr. Lin` through the AI provider, validating dialogue before display, and preserving deterministic quest, XP, inventory, mastery, and save state.
- 2026-06-22: Completed T-128 by asking the AI provider for a structured interpretation only after deterministic parsing misses, converting accepted proposals back through existing deterministic handlers, and covering accepted open-ended collection plus rejected invented targets.
- 2026-06-22: Completed T-127 by adding advisory `PlayerSentenceInterpretationRequest` and `PlayerSentenceInterpretation` models, restricting AI-proposed actions to deterministic engine actions, forbidding extra state-mutation fields, and wiring fake/Codex providers through validated schemas.
- 2026-06-22: Completed T-126 by parsing verbose directional sentences such as `I go north to the fungus grove.` into deterministic move intents while preserving engine-side exit validation for impossible movement.
- 2026-06-22: Completed T-125 by adding an AI-backed `explain <word>` command for visible or practiced Biology vocabulary, validating requested words before provider calls, displaying structured explanations without state mutation, and preserving state on invalid AI output.
- 2026-06-22: Completed T-130 by adding a fake-AI end-to-end Biology playthrough covering movement, vocabulary practice, due review completion, quest completion, combat, save, reload, and post-load status.
- 2026-06-22: Completed T-123 by adding a deterministic review-due selector with an injected clock, stable due ordering, optional limiting, and regression coverage for unseen and malformed review records.
- 2026-06-22: Completed T-122 by making mastery rewards fingerprint-based, suppressing duplicate sentence/word/context rewards, preserving no-reward repeats, and allowing the same word to earn again in a new deterministic context.
- 2026-06-22: Completed T-121 by adding deterministic learning events for word encounters, correct usage, and incorrect attempts, wiring room encounters and practice actions into mastery records, and covering context IDs with focused tests.

Keep at most ten items here.
