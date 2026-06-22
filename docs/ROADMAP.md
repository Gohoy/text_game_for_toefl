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

**Phase 2 — AI language feedback reliability**

Phase 1 exit criteria are satisfied as of 2026-06-22. The project has a playable Biology CLI with movement, items, a three-step quest, deterministic combat, autosave, vocabulary sentence practice, XP, and required AI-provider paths for player-facing narration, sentence feedback, vocabulary explanations, NPC dialogue, room narration, parser-miss interpretation, and structured content drafting.

The current goal is to improve language-feedback reliability while preserving deterministic authority over game state, rewards, saves, mastery, quest completion, combat, and validation.

## Phase 1 Exit Criteria

Phase 1 is complete. Exit evidence:

- current Biology behavior is protected by characterization and end-to-end tests in `tests/test_biology_world_characterization.py`, `tests/test_biology_world_pack.py`, and `tests/test_biology_e2e.py`
- the required AI-agent interface covers turn feedback, player sentence interpretation, NPC dialogue, room narration, vocabulary explanations, and structured content drafts in `src/toefl_rpg/ai/contract.py`
- missing AI-agent configuration fails clearly in player runtime paths, with fake-provider test coverage in `tests/test_ai_contract.py`, `tests/test_rules.py`, and `tests/test_biology_e2e.py`
- tests use `FakeAIProvider` and Codex CLI subprocess fakes without network or paid API access
- Biology world content loads from the validated JSON world pack, with loader and schema coverage in `tests/test_world_loader.py`, `tests/test_world_schema.py`, and `tests/test_biology_world_pack.py`
- content references are checked deterministically before runtime conversion
- vocabulary mastery has an explicit persisted model and legacy-save defaults in `tests/test_storage.py`
- duplicate response fingerprints prevent unlimited mastery and XP farming in `tests/test_mastery.py`
- the `review` command provides a deterministic delayed-review flow
- `tests/test_biology_e2e.py` completes the Biology quest, review loop, save, and reload path with a fake AI provider
- saves remain compatible through explicit defaults for legacy saves without mastery data

## Current Capabilities

- terminal startup through `python -m toefl_rpg`
- Rich-based room presentation
- five-room Biology world loaded from the validated JSON world pack
- full-sentence action parsing for common actions
- shared deterministic action contract used by parser intents and AI interpretation validation
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
- AI world-pack draft validation through the deterministic `WorldPack` schema
- deterministic placeholder English corrections retained only for tests/development
- JSON autosave and load
- versioned vocabulary mastery records in saves, with legacy-save defaults
- deterministic mastery events for encounters, correct use, and incorrect attempts
- duplicate response fingerprints suppress repeat mastery and XP rewards
- deterministic review-due vocabulary selector with injected clock
- playable `review` command for due vocabulary, AI-assisted full-sentence review answer evaluation, and persisted review stages
- review result messages separate AI coaching text from deterministic reward and retry summaries
- duplicate review answers are detected before AI review evaluation, preserving no-reward behavior while avoiding unnecessary provider calls
- configurable `TOEFL_RPG_SAVE_PATH` for CLI smoke tests and isolated playthroughs
- end-to-end Biology quest, review, save, and reload coverage with a fake AI provider
- AI vocabulary explanation command for visible or practiced Biology words
- invalid AI outputs for turn feedback, sentence interpretation, vocabulary explanation, NPC dialogue, and room narration fail clearly without leaving partial state changes
- mismatched AI vocabulary explanation words are rejected before display while preserving deterministic state
- external vocabulary importer
- focused tests for several existing systems

## Latest Player-Role Assessment

2026-06-22 assessment: the current Biology quest is playable and routes turn feedback, parser-miss interpretation, NPC dialogue, room look narration, vocabulary explanations, and content drafting through the AI-provider boundary. AI-generated world-pack drafts have a deterministic schema-validation path. Phase 1 is closed; remaining work belongs in Phase 2 language-feedback reliability.

Evidence from an in-memory playthrough:

- the three-step Biology quest can be completed through movement, collecting the fungus sample, using the microscope, and defeating the invasive vine
- the game rewards contextual sentences such as `The harmless creature uses mimicry to avoid extinction.`
- sentence feedback now comes from a configured provider in normal runtime, with fake-provider smoke coverage for automation
- vocabulary learning now includes same-session delayed review through `review`, with normal runtime answers checked by a validated AI review evaluator before deterministic mastery and XP changes are applied
- a fake-provider playtest can now interpret `Could you grab the specimen for my research?` as collecting the visible fungus sample, while deterministic validation still rejects invented targets such as `crystal sample`
- `talk to Dr. Lin` now requests validated AI dialogue without mutating quest state, XP, inventory, saves, or mastery
- `look` now requests validated AI room narration without mutating exits, items, NPCs, enemies, quest state, XP, inventory, saves, or mastery
- AI-authored world-pack drafts must validate as `WorldPack` before they can be reviewed as usable content
- verbose movement sentences such as `I go north to the fungus grove.` resolve through deterministic parsing
- a learner-sentence regression corpus now captures accepted, rejected, and ambiguous sentence patterns and verifies whether each route is handled by deterministic parsing or validated AI interpretation fallback
- low-confidence and unknown AI interpretation corpus cases now preserve deterministic state and show retry guidance instead of mutating the world
- a review-answer regression corpus now captures accepted, rejected, and malformed answer cases and verifies deterministic-vs-AI evaluation routing
- turn-feedback display regressions now protect labeled AI narration, sentence feedback, suggested sentence, vocabulary notes, and separate deterministic Result output
- vocabulary explanation display regressions now protect distinct meaning, example, and memory-hint lines without mutating deterministic state
- vocabulary explanation mismatch regressions now reject AI responses for the wrong word without mutating deterministic state
- review answers now use a validated AI quality judgment for meaningful target-word use while deterministic code still controls review events, stages, XP, duplicate suppression, and saves
- successful and rejected review messages now label AI advice separately from deterministic result summaries
- duplicate review-answer messages are now protected from looking like normal AI acceptance or rejection and do not grant extra XP or mastery
- duplicate review answers now skip AI review evaluation before returning the distinct duplicate message
- malformed AI outputs across turn feedback, sentence interpretation, vocabulary explanation, NPC dialogue, and room narration now have regression coverage for clear provider errors and state preservation
- low-confidence parser-miss retry guidance now has engine and renderer regressions proving deterministic state is preserved and retry text stays separate from AI coaching
- parser intents and AI interpretation responses now share the same deterministic action contract from `src/toefl_rpg/engine/actions.py`
- CLI playtests can now set `TOEFL_RPG_SAVE_PATH` to avoid the default player save slot
- Codex CLI provider invocation now matches the installed `codex exec` flags by avoiding the unsupported `--ask-for-approval` option
- player-facing AI response schemas now set `additionalProperties: false` for Codex structured-output compatibility, and live Codex turns have a longer default timeout with an environment override
- documentation now distinguishes the required fake-provider CLI smoke from an optional manual live Codex smoke, both using temporary save paths

Conclusion: proceed with Phase 2. Biology startup uses the validated JSON pack without changing player-visible behavior, cross-reference validation rejects bad content before runtime conversion, saves carry a versioned vocabulary mastery record, deterministic learning events update mastery records, duplicate response fingerprints suppress repeat rewards, a playable review command advances due words in stable order using validated AI evaluation for answer quality, review messages separate AI advice from deterministic rewards and retry state, duplicate review-answer messages avoid extra rewards, bypass unnecessary AI evaluation, and remain distinct from normal review acceptance or rejection, review-answer corpus coverage now distinguishes deterministic checks from AI evaluation, low-confidence AI interpretation coverage protects state-preserving retry guidance, turn-feedback display coverage protects AI coaching labels and separate deterministic Result output, vocabulary explanation display and mismatch coverage protects distinct meaning, example, memory-hint lines, wrong-word rejection, and deterministic state preservation, Codex CLI invocation, strict response schemas, live timeout defaults, and live-smoke documentation match the installed local `codex exec` structured-output requirements, an end-to-end test protects quest completion plus review persistence, smoke playtests can use an isolated save path, visible or practiced vocabulary can be explained through the required AI provider without mutating deterministic state, verbose directional sentences resolve to deterministic movement intents, parser misses can use validated AI interpretation before deterministic engine validation, parser and AI action names share one deterministic contract, NPC dialogue is AI-generated but display-only, room look narration is AI-generated from deterministic room context, and AI content drafts have a schema-validation gate. AI feedback is wired into the turn loop, malformed AI output is rejected with clear provider errors, and deterministic code remains the authority for state changes, content validation, and rewards.

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

- **State:** done
- **Priority:** P1
- **Goal:** Ensure structured AI world or quest drafts are schema-validated before any authored content can be used.
- **Acceptance criteria:**
  - draft request includes theme, required words, and intended content type
  - returned draft is parsed into typed models or rejected with a useful error
  - invalid references cannot enter runtime world content
  - tests use fake providers and small fixtures only
- **Verification:** AI contract tests, world schema tests, full suite.
- **Dependencies:** T-131.

### T-133 — Consolidate Phase 1 exit assessment

- **State:** done
- **Priority:** P1
- **Goal:** Check Phase 1 exit criteria against the implemented Biology loop and split any remaining unmet work into small Phase 2 tasks.
- **Acceptance criteria:**
  - roadmap current capabilities and exit assessment match code and tests
  - remaining gaps are represented as ready or planned tasks
  - no implementation claims are made without verification evidence
- **Verification:** documentation consistency check, `python3 -m pytest -q`.
- **Dependencies:** T-132.

### T-134 — Add language-feedback regression corpus

- **State:** done
- **Priority:** P1
- **Goal:** Start Phase 2 by capturing common learner sentence patterns and expected deterministic/AI-boundary behavior.
- **Acceptance criteria:**
  - fixture contains accepted, rejected, and ambiguous learner sentences
  - tests distinguish deterministic parser hits from AI interpretation fallback
  - no paid API or live Codex call is required
- **Verification:** parser/engine tests and full suite.
- **Dependencies:** T-133.

### T-135 — Improve review answer quality checks

- **State:** done
- **Priority:** P1
- **Goal:** Replace the simple review word-use gate with a validated AI-assisted quality judgment while code keeps mastery rewards authoritative.
- **Acceptance criteria:**
  - AI can advise whether a review sentence uses the target word meaningfully
  - deterministic code still controls review stage, XP, duplicate suppression, and saves
  - invalid AI judgment preserves state and reports a clear error
- **Verification:** AI contract tests, review engine tests, full suite.
- **Dependencies:** T-133.

### T-136 — Add AI feedback failure regression cases

- **State:** done
- **Priority:** P1
- **Goal:** Broaden regression coverage for malformed or unusable AI feedback across player-facing language paths.
- **Acceptance criteria:**
  - tests cover invalid turn feedback, sentence interpretation, vocabulary explanation, NPC dialogue, and room narration outputs
  - each failure preserves deterministic state and reports a clear provider error
  - fake providers are used; no live Codex CLI call is required
- **Verification:** AI contract tests, engine tests, full suite.
- **Dependencies:** T-134.

### T-137 — Centralize deterministic action names

- **State:** done
- **Priority:** P1
- **Goal:** Keep parser actions, AI interpretation actions, and engine dispatch names aligned through one shared contract.
- **Acceptance criteria:**
  - deterministic action literals are defined in one importable place
  - parser and AI interpretation validation use the same action set where practical
  - behavior remains unchanged for existing commands and learner-sentence corpus cases
- **Verification:** parser tests, AI contract tests, engine tests, full suite.
- **Dependencies:** T-136.

### T-138 — Separate review coaching text from reward summaries

- **State:** done
- **Priority:** P2
- **Goal:** Make review result messages easier to read by keeping AI coaching text distinct from deterministic reward and scheduling summaries.
- **Acceptance criteria:**
  - successful and rejected review messages clearly separate AI advice from deterministic reward/state results
  - turn feedback still appears through the existing AI feedback channel
  - no mastery, XP, duplicate suppression, or save behavior changes
- **Verification:** review engine tests, CLI smoke with fake provider, full suite.
- **Dependencies:** T-135.

### T-139 — Add configurable CLI smoke save path

- **State:** done
- **Priority:** P1
- **Goal:** Let automated CLI smoke tests run without reading or writing the user's default save slot.
- **Acceptance criteria:**
  - CLI/runtime can use an environment-configured save path
  - default save behavior remains unchanged for normal play
  - smoke command can target a temporary save path and leave tracked files untouched
- **Verification:** CLI smoke with fake provider and temporary save path, storage tests, full suite.
- **Dependencies:** T-138.

### T-140 — Add review-answer learner corpus cases

- **State:** done
- **Priority:** P2
- **Goal:** Extend the learner sentence corpus with review-answer examples that distinguish deterministic minimum checks from AI quality judgment.
- **Acceptance criteria:**
  - corpus includes accepted, rejected, and malformed review-answer cases
  - tests verify which cases stop at deterministic checks and which reach AI evaluation
  - fake providers are used; no live Codex CLI call is required
- **Verification:** learner corpus tests, review engine tests, full suite.
- **Dependencies:** T-138.

### T-141 — Add turn-feedback display regression cases

- **State:** done
- **Priority:** P2
- **Goal:** Protect the player-facing shape of AI turn feedback without depending on exact prose.
- **Acceptance criteria:**
  - tests assert narration, sentence feedback, suggested sentence, and vocabulary notes remain visibly separated
  - deterministic result text remains distinct from AI coaching
  - fake providers are used; no live Codex CLI call is required
- **Verification:** engine/renderer tests and full suite.
- **Dependencies:** T-138.

### T-142 — Add low-confidence interpretation corpus cases

- **State:** done
- **Priority:** P2
- **Goal:** Capture ambiguous learner commands where AI interpretation should decline rather than mutate state.
- **Acceptance criteria:**
  - corpus includes low-confidence or unknown AI interpretation examples
  - tests verify state preservation and clear retry guidance
  - deterministic parser hits still bypass AI interpretation
- **Verification:** learner corpus tests, engine tests, full suite.
- **Dependencies:** T-137.

### T-145 — Fix Codex CLI approval flag compatibility

- **State:** done
- **Priority:** P0
- **Goal:** Keep normal live Codex CLI gameplay from failing on installed `codex exec` versions that do not support `--ask-for-approval`.
- **Acceptance criteria:**
  - provider command no longer includes the unsupported `--ask-for-approval` flag
  - command construction test protects the installed-compatible invocation shape
  - AI agent contract documentation shows the working command
- **Verification:** Codex CLI provider tests, full suite, CLI smoke with fake provider.
- **Dependencies:** T-106.

### T-147 — Fix Codex structured-output schema compatibility

- **State:** done
- **Priority:** P0
- **Goal:** Keep normal live Codex CLI gameplay from failing when OpenAI structured outputs require strict object schemas.
- **Acceptance criteria:**
  - player-facing response schemas include `additionalProperties: false`
  - AI response models reject extra state-mutation fields
  - provider tests verify the schema file passed to Codex is strict
  - live Codex provider default timeout is long enough for slower local Codex configurations and remains environment-configurable
- **Verification:** AI contract tests, Codex CLI provider tests, app tests, full suite, CLI smoke with fake provider.
- **Dependencies:** T-106.

### T-143 — Add review duplicate-message regression

- **State:** done
- **Priority:** P2
- **Goal:** Protect the player-facing message and state behavior when a review answer repeats an already-completed sentence.
- **Acceptance criteria:**
  - repeated review answer message is distinct from AI acceptance and AI rejection
  - duplicate review still avoids extra XP and mastery gain
  - test uses fake providers and does not require live Codex CLI
- **Verification:** review engine tests and full suite.
- **Dependencies:** T-140.

### T-144 — Add vocabulary explanation display regression

- **State:** done
- **Priority:** P2
- **Goal:** Protect the player-facing shape of AI vocabulary explanations without depending on exact prose.
- **Acceptance criteria:**
  - explanation output keeps meaning, example, and memory hint visibly distinct
  - deterministic state remains unchanged after explanation display
  - test uses fake providers and does not require live Codex CLI
- **Verification:** engine/renderer tests and full suite.
- **Dependencies:** T-125.

### T-146 — Add Codex CLI live smoke documentation

- **State:** done
- **Priority:** P2
- **Goal:** Document a safe manual smoke path for running one live Codex-backed turn without touching the normal save slot.
- **Acceptance criteria:**
  - README shows a live-provider command using `TOEFL_RPG_SAVE_PATH`
  - docs distinguish fake smoke from live Codex smoke
  - no automation gate requires a paid or live Codex call
- **Verification:** documentation consistency check and fake-provider smoke.
- **Dependencies:** T-145.

### T-148 — Add review duplicate pre-check optimization

- **State:** done
- **Priority:** P2
- **Goal:** Avoid calling the review-evaluation AI provider when a review answer fingerprint is already known to be duplicate.
- **Acceptance criteria:**
  - duplicate review answers are detected before AI review evaluation
  - duplicate message and no-reward behavior from T-143 remain unchanged
  - fake-provider tests prove no review-evaluation request is sent for duplicates
- **Verification:** review engine tests and full suite.
- **Dependencies:** T-143.

### T-149 — Add vocabulary explanation word-mismatch regression

- **State:** done
- **Priority:** P2
- **Goal:** Protect the failure path when AI returns an explanation for a different vocabulary word.
- **Acceptance criteria:**
  - mismatched explanation word raises a clear provider error
  - deterministic state remains unchanged
  - fake-provider test does not require live Codex CLI
- **Verification:** engine tests and full suite.
- **Dependencies:** T-144.

### T-150 — Add parser-miss retry display regression

- **State:** done
- **Priority:** P2
- **Goal:** Protect the player-facing retry guidance when AI interpretation declines or cannot confidently parse a learner sentence.
- **Acceptance criteria:**
  - low-confidence parser-miss output shows retry guidance instead of normal success feedback
  - deterministic state remains unchanged
  - test uses fake providers and does not require live Codex CLI
- **Verification:** engine/renderer tests and full suite.
- **Dependencies:** T-142.

### T-151 — Add review AI rejection display regression

- **State:** ready
- **Priority:** P2
- **Goal:** Protect the player-facing shape of AI review rejection feedback without depending on exact prose.
- **Acceptance criteria:**
  - rejected review answers keep AI advice, suggested sentence, and deterministic retry result visibly distinct
  - active review word remains unchanged after rejection
  - test uses fake providers and does not require live Codex CLI
- **Verification:** engine/renderer tests and full suite.
- **Dependencies:** T-140.

### T-152 — Add parser-miss malformed-response regression

- **State:** planned
- **Priority:** P2
- **Goal:** Protect the failure path when AI parser-miss interpretation returns malformed structured data.
- **Acceptance criteria:**
  - malformed parser-miss AI output raises a clear provider error
  - deterministic state remains unchanged
  - test uses fake providers and does not require live Codex CLI
- **Verification:** engine tests and full suite.
- **Dependencies:** T-142.

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

## Current Phase Focus

### Phase 2 — AI language feedback reliability

- normalize parser intent structures
- separate deterministic action authority from AI coaching text
- expand regression corpora for common learner sentences
- validate AI feedback shape and failure modes

## Future Phases

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

- 2026-06-22: Completed T-150 by adding engine and renderer regressions that keep low-confidence parser-miss retry guidance in the Result output, separate from AI coaching, while preserving deterministic state and avoiding normal success feedback.
- 2026-06-22: Completed T-149 by adding a fake-provider regression that rejects AI vocabulary explanations for the wrong word with a clear provider error while preserving deterministic state.
- 2026-06-22: Completed T-148 by moving duplicate review-answer detection before AI review evaluation, preserving the distinct duplicate message and no-reward behavior while proving no fake-provider review-evaluation request is sent.
- 2026-06-22: Completed T-146 by documenting a temporary-save manual live Codex smoke command in README, distinguishing it from the required fake-provider smoke gate, and keeping automation free of paid or live Codex requirements.
- 2026-06-22: Completed T-144 by adding engine and renderer regressions that keep AI vocabulary explanation meaning, example, and memory-hint lines visibly distinct while preserving deterministic state and avoiding an unrelated English Feedback panel.
- 2026-06-22: Completed T-143 by adding a review duplicate-message regression that verifies repeated active review answers use a distinct duplicate message, clear the active review, and avoid extra XP, review-stage, and mastery-point gains with a fake provider.
- 2026-06-22: Completed T-147 by making player-facing AI response schemas strict with `additionalProperties: false`, adding extra-field rejection tests, asserting the Codex CLI schema file uses the strict schema required by OpenAI structured outputs, and raising the default live Codex timeout while keeping `TOEFL_RPG_CODEX_TIMEOUT` configurable.
- 2026-06-22: Completed T-142 by extending the learner-sentence corpus with explicit low-confidence and unknown AI interpretation cases that preserve state and require clear retry guidance while deterministic parser hits still bypass AI interpretation.
- 2026-06-22: Completed T-145 by removing the unsupported `--ask-for-approval` option from the Codex CLI provider command, adding a command-shape regression assertion, and updating the AI agent contract command example.
- 2026-06-22: Completed T-141 by adding engine and renderer regressions that keep AI narration, sentence feedback, suggested sentence, and vocabulary notes visibly separated from deterministic Result output.

Keep at most ten items here.
