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
- deterministic item inspection details for described world-pack items, including the vaccine vial's visible liquid
- deterministic combat
- a three-step Biology Investigation quest
- contextual target-word practice
- AI-backed turn narration and sentence feedback through Codex CLI or the explicit fake test provider
- structured AI interpretation contract for advisory open-ended sentence parsing
- AI interpretation fallback for parser misses, with deterministic validation of rooms, items, enemies, and rewards
- malformed parser-miss AI interpretation responses are rejected with clear provider errors and state preservation
- parser-miss AI interpretations with unauthorized extra fields are rejected before deterministic validation
- parser-miss AI interpretation requests reject unauthorized extra state-like fields before reaching providers
- AI-backed NPC dialogue grounded in room, quest, visible entity, and vocabulary context
- mismatched AI NPC dialogue speakers are rejected before display while preserving deterministic state
- empty AI NPC dialogue speaker and line fields are rejected while preserving deterministic state
- malformed AI NPC dialogue vocabulary notes are rejected before display while preserving deterministic state
- AI NPC dialogue with unauthorized extra fields is rejected before display while preserving deterministic state
- AI NPC dialogue requests reject unauthorized extra state-like fields before reaching providers
- AI-backed room look narration grounded in deterministic room state
- AI room narration requests reject unauthorized extra state-like fields before reaching providers
- malformed AI room narration responses are rejected with clear provider errors and state preservation
- mismatched AI room narration room IDs are rejected before display while preserving deterministic state
- AI room narration with unauthorized extra fields is rejected before display while preserving deterministic state
- AI world-pack draft validation through the deterministic `WorldPack` schema
- empty AI world-pack draft title and room text are rejected by deterministic schema validation
- AI content drafts with unauthorized top-level fields are rejected before generated content is accepted
- AI world-pack draft payloads with unauthorized nested mutation-like fields are rejected by deterministic schema validation
- AI content-draft validation errors distinguish envelope failures from world-pack payload failures and keep nested field paths visible
- AI content-draft requests reject unauthorized extra state-like fields before reaching providers
- deterministic placeholder English corrections retained only for tests/development
- JSON autosave and load
- versioned vocabulary mastery records in saves, with legacy-save defaults
- deterministic mastery events for encounters, correct use, and incorrect attempts
- duplicate response fingerprints suppress repeat mastery and XP rewards
- deterministic review-due vocabulary selector with injected clock
- playable `review` command for due vocabulary, AI-assisted full-sentence review answer evaluation, and persisted review stages
- review result messages separate AI coaching text from deterministic reward and retry summaries
- rejected review answers keep AI advice, suggested sentence, and deterministic retry result visibly distinct
- AI review-evaluation requests reject unauthorized extra state-like fields before reaching providers
- all AI request models have strict-schema audit coverage in the AI contract tests
- parser and AI sentence interpretation share an executable action/target convention audit
- learner sentence corpus covers polite deterministic commands and polite AI-interpretation fallback
- learner sentence corpus covers desire-based movement phrasing with explicit deterministic state expectations
- learner sentence corpus covers permission-question movement phrasing with explicit deterministic state expectations
- learner sentence corpus covers negative request phrasing so negated movement does not execute the positive action
- learner sentence corpus covers indirect polite questions routed through validated AI interpretation
- learner sentence corpus covers hedged intention movement phrasing with explicit deterministic state expectations
- parser movement matching tolerates common separator punctuation in full-sentence movement input
- renderer tests keep deterministic result text visually separate from AI coaching for successful and rejected turns
- vocabulary explanation renderer coverage keeps explanation, example, and memory hint in the result panel without an empty feedback panel
- AI feedback formatting has rules and renderer coverage for multiple distinct vocabulary-note lines
- plain-console renderer fallback keeps deterministic results and English feedback under separate labels
- parser-miss AI interpretation provider failures preserve location, inventory, XP, quest progress, and mastery
- empty AI review-evaluation explanation and suggested-sentence fields are rejected while active review state remains unchanged
- malformed AI review-evaluation judgment flags are rejected while active review state remains unchanged
- AI review evaluations with unauthorized extra fields are rejected while active review state remains unchanged
- duplicate review answers are detected before AI review evaluation, preserving no-reward behavior while avoiding unnecessary provider calls
- review-answer corpus covers fluent but synonym-heavy incorrect target-word use that reaches AI evaluation and keeps review active without XP
- review-answer corpus covers memorized definition-style misuse that reaches AI evaluation and keeps review active without XP
- review-answer corpus covers target-word context mismatch that reaches AI evaluation and keeps review active without XP
- review-answer corpus covers vague grammatical target-word use that reaches AI evaluation and keeps review active without XP
- review-answer corpus covers metaphorical target-word use that reaches AI evaluation and keeps review active without XP
- review-answer corpus covers copied-example reuse that reaches AI evaluation and keeps review active without XP
- review-answer corpus covers negated target-word use that reaches AI evaluation and keeps review active without XP
- review-answer corpus covers list-like target-word fragments rejected by deterministic precheck without AI evaluation
- review-answer corpus covers question-form target-word use that reaches AI evaluation and keeps review active without XP
- review-answer corpus covers quoted target-word mentions that reach AI evaluation and keep review active without XP
- review-answer corpus covers hypothetical target-word use that reaches AI evaluation and keeps review active without XP
- review-answer corpus covers overgeneralized target-word use that reaches AI evaluation and keeps review active without XP
- review-answer corpus covers learner uncertainty phrasing that reaches AI evaluation and keeps review active without XP
- review-answer corpus covers tautological target-word use that reaches AI evaluation and keeps review active without XP
- review-answer corpus covers shallow example-label target-word use that reaches AI evaluation and keeps review active without XP
- review-answer corpus covers personal-preference target-word use that reaches AI evaluation and keeps review active without XP
- review-answer corpus covers emotional-reaction target-word use that reaches AI evaluation and keeps review active without XP
- review-answer corpus covers confidence-only target-word use that reaches AI evaluation and keeps review active without XP
- review-answer corpus covers comparison-only target-word use that reaches AI evaluation and keeps review active without XP
- review-answer corpus covers test-strategy-only target-word use that reaches AI evaluation and keeps review active without XP
- review-answer corpus covers score-goal-only target-word use that reaches AI evaluation and keeps review active without XP
- review-answer corpus covers exam-context-only target-word use that reaches AI evaluation and keeps review active without XP
- review-answer corpus covers passage-prediction-only target-word use that reaches AI evaluation and keeps review active without XP
- review-answer corpus covers analogy-only target-word use that reaches AI evaluation and keeps review active without XP
- review-answer corpus covers cause-effect-free target-word use that reaches AI evaluation and keeps review active without XP
- review-answer corpus covers unsupported-certainty target-word use that reaches AI evaluation and keeps review active without XP
- review-answer corpus covers location-only target-word use that reaches AI evaluation and keeps review active without XP
- review-answer corpus covers relation-only target-word use that reaches AI evaluation and keeps review active without XP
- review-answer corpus covers category-label target-word use that reaches AI evaluation and keeps review active without XP
- review-answer corpus covers answer-label target-word use that reaches AI evaluation and keeps review active without XP
- review-answer corpus covers translation-only target-word use that reaches AI evaluation and keeps review active without XP
- review-answer corpus covers spelling-only target-word use that reaches AI evaluation and keeps review active without XP
- review-answer corpus covers pronunciation-only target-word use that reaches AI evaluation and keeps review active without XP
- review-answer corpus covers morphology-only target-word use that reaches AI evaluation and keeps review active without XP
- review-answer corpus covers frequency-only target-word use that reaches AI evaluation and keeps review active without XP
- review-answer corpus covers visual-form-only target-word use that reaches AI evaluation and keeps review active without XP
- review-answer corpus covers difficulty-only target-word use that reaches AI evaluation and keeps review active without XP
- review-answer corpus covers memorization-method-only target-word use that reaches AI evaluation and keeps review active without XP
- review-answer corpus covers etymology-only target-word use that reaches AI evaluation and keeps review active without XP
- review-answer corpus covers source-only target-word use that reaches AI evaluation and keeps review active without XP
- learner sentence corpus covers pronoun-like item references with explicit AI fallback and deterministic collect validation
- learner sentence corpus covers compound action requests while proving only one deterministic action executes
- learner sentence corpus covers self-correction phrasing routed through AI fallback and deterministic collect validation
- learner sentence corpus covers overly broad location requests routed through AI fallback with no state mutation
- learner sentence corpus covers ambiguous enemy references rejected by deterministic combat without state mutation
- learner sentence corpus covers broad tool-use requests rejected by deterministic item validation without state mutation
- learner sentence corpus covers broad conversation requests rejected by deterministic NPC validation without state mutation
- learner sentence corpus covers broad collection requests rejected by deterministic item validation without AI fallback or state mutation
- learner sentence corpus covers broad inspection requests rejected by deterministic visible-target validation without AI fallback or state mutation
- learner sentence corpus covers vague combat pronouns rejected by deterministic enemy validation without state mutation
- learner sentence corpus covers vague inventory requests routed through AI interpretation with no state mutation
- learner sentence corpus covers indirect inventory-availability requests routed through AI interpretation to deterministic inventory with no state mutation
- learner sentence corpus covers broad status requests routed through AI interpretation to deterministic status with no state mutation
- learner sentence corpus covers indirect recap requests routed through AI interpretation to deterministic status with no state mutation
- learner sentence corpus covers indirect status-comparison requests routed through AI interpretation to deterministic status with no state mutation
- learner sentence corpus covers indirect route-confirmation requests routed through AI interpretation to deterministic status with no state mutation
- learner sentence corpus covers indirect readiness checks routed through AI interpretation to deterministic status with visible enemy grounding and no state mutation
- learner sentence corpus covers indirect quest-progress requests routed through AI interpretation to deterministic status with no state mutation
- learner sentence corpus covers indirect goal-reminder requests routed through AI interpretation to deterministic status with no state mutation
- learner sentence corpus covers indirect objective-priority requests routed through AI interpretation to deterministic status with no state mutation
- learner sentence corpus covers indirect enemy-warning requests routed through AI interpretation to deterministic room narration with visible enemy grounding and no state mutation
- learner sentence corpus covers indirect strategy-advice requests routed through AI interpretation to deterministic room narration with visible enemy grounding and no state mutation
- learner sentence corpus covers indirect safety-check requests routed through AI interpretation to deterministic room narration with visible enemy grounding and no state mutation
- learner sentence corpus covers indirect retreat-advice requests routed through AI interpretation to deterministic room narration with visible enemy grounding and no movement, combat, or state mutation
- learner sentence corpus covers indirect rest requests routed through AI interpretation to deterministic status with no healing or state mutation
- learner sentence corpus covers indirect help requests routed through AI interpretation to deterministic help with no state mutation
- learner sentence corpus covers indirect hint requests routed through AI interpretation to deterministic help with no state mutation
- learner sentence corpus covers indirect prerequisite-reminder requests routed through AI interpretation to deterministic help with no state mutation
- learner sentence corpus covers indirect vocabulary-reminder requests routed through AI interpretation to deterministic help with no state mutation
- learner sentence corpus covers indirect review requests routed through AI interpretation to deterministic review handling with no state mutation when no words are due
- learner sentence corpus covers indirect review-readiness requests routed through AI interpretation to deterministic review availability with no mastery mutation
- learner sentence corpus covers indirect vocabulary explanation requests routed through AI interpretation to deterministic explanation with no state mutation
- learner sentence corpus covers indirect look requests routed through AI interpretation to deterministic room narration with no state mutation
- learner sentence corpus covers indirect map-or-exits requests routed through AI interpretation to deterministic room narration with exits grounding and no state mutation
- learner sentence corpus covers indirect route-planning requests routed through AI interpretation to deterministic room narration with exits grounding and no automatic movement
- learner sentence corpus covers indirect backtracking requests routed through AI interpretation to deterministic room narration with exits grounding and no automatic movement
- learner sentence corpus covers indirect detour requests routed through AI interpretation to deterministic room narration with exits grounding and no automatic movement
- learner sentence corpus covers indirect repeat-room narration requests routed through AI interpretation to deterministic room narration with no state mutation
- learner sentence corpus covers indirect save-exit requests routed through AI interpretation to deterministic quit handling with no state mutation
- learner sentence corpus covers indirect NPC dialogue requests routed through AI interpretation to deterministic talk validation with no state mutation
- configurable `TOEFL_RPG_SAVE_PATH` for CLI smoke tests and isolated playthroughs
- end-to-end Biology quest, review, save, and reload coverage with a fake AI provider
- AI vocabulary explanation command for visible or practiced Biology words
- invalid AI outputs for turn feedback, sentence interpretation, vocabulary explanation, NPC dialogue, and room narration fail clearly without leaving partial state changes
- malformed AI turn-feedback vocabulary notes are rejected with state rollback after state-changing actions
- AI turn feedback with unauthorized extra fields is rejected with state rollback after state-changing actions
- AI turn-feedback requests reject unauthorized extra state-like fields before reaching providers
- empty AI vocabulary-explanation meaning, example, and memory-hint fields are rejected while preserving deterministic state
- AI vocabulary explanations with unauthorized extra fields are rejected while preserving deterministic state
- AI vocabulary-explanation requests reject unauthorized extra state-like fields before reaching providers
- empty AI turn-feedback narration, feedback, and suggested-sentence fields are rejected with state rollback after state-changing actions
- mismatched AI vocabulary explanation words are rejected before display while preserving deterministic state
- external vocabulary importer
- focused tests for several existing systems

## Latest Player-Role Assessment

2026-06-22 assessment: the current Biology quest is playable and routes turn feedback, parser-miss interpretation, NPC dialogue, room look narration, vocabulary explanations, and content drafting through the AI-provider boundary. AI-generated world-pack drafts have a deterministic schema-validation path. Phase 1 is closed; remaining work belongs in Phase 2 language-feedback reliability.

2026-06-23 playtest update: direct Biology actions remain playable in memory with a fake AI provider, but indirect metacognitive requests still need explicit corpus coverage so the AI can map them to deterministic status/help/look actions without mutation.

Evidence from an in-memory playthrough:

- the three-step Biology quest can be completed through movement, collecting the fungus sample, using the microscope, and defeating the invasive vine
- the game rewards contextual sentences such as `The harmless creature uses mimicry to avoid extinction.`
- sentence feedback now comes from a configured provider in normal runtime, with fake-provider smoke coverage for automation
- vocabulary learning now includes same-session delayed review through `review`, with normal runtime answers checked by a validated AI review evaluator before deterministic mastery and XP changes are applied
- a fake-provider playtest can now interpret `Could you grab the specimen for my research?` as collecting the visible fungus sample, while deterministic validation still rejects invented targets such as `crystal sample`
- `talk to Dr. Lin` now requests validated AI dialogue without mutating quest state, XP, inventory, saves, or mastery
- NPC dialogue speaker mismatches now raise clear provider errors before display and preserve deterministic state
- empty NPC dialogue required fields now have regression coverage proving provider errors preserve deterministic state
- malformed NPC dialogue vocabulary notes now have regression coverage proving provider errors preserve deterministic state
- NPC dialogue extra-field regressions now prove unauthorized mutation-like fields are rejected before display
- `look` now requests validated AI room narration without mutating exits, items, NPCs, enemies, quest state, XP, inventory, saves, or mastery
- malformed room narration responses, including empty required fields, now raise clear provider errors and preserve deterministic state
- room narration responses must echo the requested room ID, and mismatches now raise clear provider errors before display
- room narration extra-field regressions now prove unauthorized mutation-like fields are rejected before display
- AI-authored world-pack drafts must validate as `WorldPack` before they can be reviewed as usable content
- AI-authored world-pack drafts with empty required title or room description text now raise clear validation errors before acceptance
- AI-authored content drafts with unauthorized top-level fields now raise clear validation errors before payload acceptance
- AI-authored world-pack payloads with nested mutation-like fields now raise clear validation errors before generated content is accepted
- verbose movement sentences such as `I go north to the fungus grove.` resolve through deterministic parsing
- permission-question movement sentences such as `Can I go north to the fungus grove?` resolve through deterministic parsing
- a learner-sentence regression corpus now captures accepted, rejected, and ambiguous sentence patterns and verifies whether each route is handled by deterministic parsing or validated AI interpretation fallback
- polite learner commands such as `Please...` and `Could you...` are covered across deterministic parsing and AI interpretation fallback routes
- low-confidence and unknown AI interpretation corpus cases now preserve deterministic state and show retry guidance instead of mutating the world
- malformed parser-miss AI interpretation corpus cases now raise clear provider errors while preserving deterministic state
- a review-answer regression corpus now captures accepted, rejected, and malformed answer cases and verifies deterministic-vs-AI evaluation routing
- turn-feedback display regressions now protect labeled AI narration, sentence feedback, suggested sentence, vocabulary notes, and separate deterministic Result output
- vocabulary explanation display regressions now protect distinct meaning, example, and memory-hint lines without mutating deterministic state
- vocabulary explanation mismatch regressions now reject AI responses for the wrong word without mutating deterministic state
- empty vocabulary-explanation required fields now have regression coverage proving provider errors preserve deterministic state
- vocabulary-explanation extra-field regressions now prove unauthorized mutation-like fields are rejected before display
- review answers now use a validated AI quality judgment for meaningful target-word use while deterministic code still controls review events, stages, XP, duplicate suppression, and saves
- successful and rejected review messages now label AI advice separately from deterministic result summaries
- review rejection display regressions now keep AI advice, suggested sentence, and deterministic retry result in the Result panel while active review state remains unchanged
- empty review-evaluation required fields now have regression coverage proving provider errors preserve the active review word
- malformed review-evaluation judgment flags now have regression coverage proving provider errors preserve the active review word
- review-evaluation extra-field regressions now prove unauthorized mutation-like fields preserve the active review word
- duplicate review-answer messages are now protected from looking like normal AI acceptance or rejection and do not grant extra XP or mastery
- duplicate review answers now skip AI review evaluation before returning the distinct duplicate message
- synonym-heavy review answers such as defining `fungus` as a harmless animal now reach validated AI evaluation, remain rejected, keep the review active, and award no XP
- location-only review answers such as placing `fungus` near a research tent now reach validated AI evaluation, remain rejected, keep the review active, and award no XP
- answer-label review answers such as calling `fungus` the correct review answer now reach validated AI evaluation, remain rejected, keep the review active, and award no XP
- exam-context-only review answers such as saying `fungus` may appear in a difficult TOEFL exam question now reach validated AI evaluation, remain rejected, keep the review active, and award no XP
- reading-skill-only review answers such as saying `fungus` can improve TOEFL reading skill now reach validated AI evaluation, remain rejected, keep the review active, and award no XP
- dictionary-skill-only review answers such as saying the learner can find `fungus` in a TOEFL dictionary now reach validated AI evaluation, remain rejected, keep the review active, and award no XP
- note-taking-only review answers such as saying the learner wrote `fungus` in biology notes now reach validated AI evaluation, remain rejected, keep the review active, and award no XP
- study-list-only review answers such as saying `fungus` is a TOEFL study-list entry now reach validated AI evaluation, remain rejected, keep the review active, and award no XP
- flashcard-deck-only review answers such as saying `fungus` belongs in a TOEFL flashcard deck now reach validated AI evaluation, remain rejected, keep the review active, and award no XP
- quiz-prep-only review answers such as saying `fungus` helps TOEFL quiz preparation now reach validated AI evaluation, remain rejected, keep the review active, and award no XP
- indirect goal-reminder requests such as `What should I accomplish next?` now route through validated AI interpretation to deterministic status, preserving state while surfacing the next Biology Investigation objective
- indirect vocabulary-reminder requests such as `Which word should I practice here?` now route through validated AI interpretation to deterministic help, preserving state while surfacing current practice examples
- indirect next-word requests such as `Which vocabulary word comes next?` now route through validated AI interpretation to deterministic help, preserving state while avoiding practice credit
- indirect review-readiness requests such as `Am I ready for a review?` now route through validated AI interpretation to deterministic review availability with no mastery mutation
- indirect detour requests such as `Is there another way around?` now route through validated AI interpretation to deterministic room narration with exits grounding and no automatic movement
- malformed AI outputs across turn feedback, sentence interpretation, vocabulary explanation, NPC dialogue, and room narration now have regression coverage for clear provider errors and state preservation
- empty turn-feedback required fields now have regression coverage proving validation failures roll back state-changing actions
- malformed turn-feedback vocabulary notes now have regression coverage proving validation failures roll back state-changing actions
- turn-feedback extra-field regressions now prove unauthorized mutation-like fields roll back state-changing actions
- broad destination requests such as `Please take me to the lab.` now avoid accidental collect parsing, route through AI interpretation, and preserve deterministic state when declined
- low-confidence parser-miss retry guidance now has engine and renderer regressions proving deterministic state is preserved and retry text stays separate from AI coaching
- empty sentence-interpretation action and reason fields now have regression coverage proving provider errors preserve deterministic state
- sentence-interpretation extra-field regressions now prove unauthorized mutation-like fields are rejected before deterministic validation
- parser intents and AI interpretation responses now share the same deterministic action contract from `src/toefl_rpg/engine/actions.py`
- CLI playtests can now set `TOEFL_RPG_SAVE_PATH` to avoid the default player save slot
- Codex CLI provider invocation now matches the installed `codex exec` flags by avoiding the unsupported `--ask-for-approval` option
- player-facing AI response schemas now set `additionalProperties: false` for Codex structured-output compatibility, and live Codex turns have a longer default timeout with an environment override
- Codex CLI structured-output schema strictness is covered for AI content-draft calls through a subprocess fake
- documentation now distinguishes the required fake-provider CLI smoke from an optional manual live Codex smoke, both using temporary save paths
- vaccine vial inspection now deterministically reports that clear liquid moves inside, so AI narration has an authoritative fact for player questions about whether the vial contains liquid

Conclusion: proceed with Phase 2. Biology startup uses the validated JSON pack without changing player-visible behavior, cross-reference validation rejects bad content before runtime conversion, saves carry a versioned vocabulary mastery record, deterministic learning events update mastery records, duplicate response fingerprints suppress repeat rewards, a playable review command advances due words in stable order using validated AI evaluation for answer quality, review messages separate AI advice from deterministic rewards and retry state, rejected review answers keep AI advice and deterministic retry text visibly distinct, empty review-evaluation required fields preserve the active review word, duplicate review-answer messages avoid extra rewards, bypass unnecessary AI evaluation, and remain distinct from normal review acceptance or rejection, review-answer corpus coverage now distinguishes deterministic checks from AI evaluation, broad destination requests now avoid accidental collect parsing and preserve state when AI interpretation declines them, low-confidence, malformed, and empty-field AI interpretation coverage protects state-preserving retry guidance and provider errors, turn-feedback display, empty-field, and vocabulary-note coverage protects AI coaching labels, separate deterministic Result output, and rollback after state-changing actions, vocabulary explanation display, mismatch, and empty-field coverage protects distinct meaning, example, memory-hint lines, wrong-word rejection, and deterministic state preservation, NPC dialogue mismatch, empty-field, and vocabulary-note coverage rejects wrong or malformed dialogue before display, room narration malformed, empty-field, and wrong-room coverage rejects invalid look prose before display, Codex CLI invocation, strict response schemas, live timeout defaults, and live-smoke documentation match the installed local `codex exec` structured-output requirements, an end-to-end test protects quest completion plus review persistence, smoke playtests can use an isolated save path, visible or practiced vocabulary can be explained through the required AI provider without mutating deterministic state, verbose and permission-question directional sentences resolve to deterministic movement intents, parser misses can use validated AI interpretation before deterministic engine validation, parser and AI action names share one deterministic action contract, NPC dialogue is AI-generated but display-only, room look narration is AI-generated from deterministic room context, and AI content drafts have a schema-validation gate that rejects malformed, cross-reference-invalid, empty required text, and unauthorized top-level fields. AI feedback is wired into the turn loop, malformed AI output is rejected with clear provider errors, and deterministic code remains the authority for state changes, content validation, and rewards.

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

- **State:** done
- **Priority:** P2
- **Goal:** Protect the player-facing shape of AI review rejection feedback without depending on exact prose.
- **Acceptance criteria:**
  - rejected review answers keep AI advice, suggested sentence, and deterministic retry result visibly distinct
  - active review word remains unchanged after rejection
  - test uses fake providers and does not require live Codex CLI
- **Verification:** engine/renderer tests and full suite.
- **Dependencies:** T-140.

### T-152 — Add parser-miss malformed-response regression

- **State:** done
- **Priority:** P2
- **Goal:** Protect the failure path when AI parser-miss interpretation returns malformed structured data.
- **Acceptance criteria:**
  - malformed parser-miss AI output raises a clear provider error
  - deterministic state remains unchanged
  - test uses fake providers and does not require live Codex CLI
- **Verification:** engine tests and full suite.
- **Dependencies:** T-142.

### T-153 — Add NPC dialogue speaker-mismatch regression

- **State:** done
- **Priority:** P2
- **Goal:** Protect the failure path when AI dialogue returns a speaker different from the requested visible NPC.
- **Acceptance criteria:**
  - mismatched NPC dialogue speaker raises a clear provider error
  - deterministic state remains unchanged
  - test uses fake providers and does not require live Codex CLI
- **Verification:** engine tests and full suite.
- **Dependencies:** T-129.

### T-154 — Add room narration malformed-response regression

- **State:** done
- **Priority:** P2
- **Goal:** Protect the failure path when AI room narration returns malformed structured data.
- **Acceptance criteria:**
  - malformed room narration raises a clear provider error
  - deterministic state remains unchanged
  - test uses fake providers and does not require live Codex CLI
- **Verification:** engine tests and full suite.
- **Dependencies:** T-131.

### T-155 — Add content draft malformed-payload regression

- **State:** done
- **Priority:** P2
- **Goal:** Protect the failure path when AI content drafting returns a malformed world-pack payload.
- **Acceptance criteria:**
  - malformed world-pack draft payload raises a clear validation error
  - no generated content is accepted without deterministic schema validation
  - test uses fake providers and does not require live Codex CLI
- **Verification:** AI content draft tests and full suite.
- **Dependencies:** T-132.

### T-156 — Add turn-feedback empty-field regression

- **State:** done
- **Priority:** P2
- **Goal:** Protect the failure path when AI turn feedback returns empty required coaching fields.
- **Acceptance criteria:**
  - empty narration, feedback, or suggested sentence raises a clear provider error
  - deterministic state is rolled back when feedback validation fails after a state-changing action
  - test uses fake providers and does not require live Codex CLI
- **Verification:** engine tests and full suite.
- **Dependencies:** T-136.

### T-157 — Add review evaluation empty-field regression

- **State:** done
- **Priority:** P2
- **Goal:** Protect the failure path when AI review evaluation returns empty required feedback fields.
- **Acceptance criteria:**
  - empty explanation or suggested sentence raises a clear provider error
  - active review state remains unchanged
  - test uses fake providers and does not require live Codex CLI
- **Verification:** review engine tests and full suite.
- **Dependencies:** T-140.

### T-158 — Add vocabulary explanation empty-field regression

- **State:** done
- **Priority:** P2
- **Goal:** Protect the failure path when AI vocabulary explanations return empty required learning fields.
- **Acceptance criteria:**
  - empty meaning, example, or memory hint raises a clear provider error
  - deterministic state remains unchanged
  - test uses fake providers and does not require live Codex CLI
- **Verification:** engine tests and full suite.
- **Dependencies:** T-149.

### T-159 — Add NPC dialogue empty-field regression

- **State:** done
- **Priority:** P2
- **Goal:** Protect the failure path when AI NPC dialogue returns empty required display fields.
- **Acceptance criteria:**
  - empty speaker or dialogue line raises a clear provider error
  - deterministic state remains unchanged
  - test uses fake providers and does not require live Codex CLI
- **Verification:** engine tests and full suite.
- **Dependencies:** T-153.

### T-160 — Add sentence-interpretation empty-field regression

- **State:** done
- **Priority:** P2
- **Goal:** Protect the failure path when AI parser-miss interpretation returns empty required fields.
- **Acceptance criteria:**
  - empty action or reason raises a clear provider error
  - deterministic state remains unchanged
  - test uses fake providers and does not require live Codex CLI
- **Verification:** learner-sentence corpus or engine tests and full suite.
- **Dependencies:** T-152.

### T-161 — Add room narration wrong-location regression

- **State:** done
- **Priority:** P2
- **Goal:** Protect the failure path when AI room narration returns a different room ID than requested.
- **Acceptance criteria:**
  - mismatched room ID raises a clear provider error before display
  - deterministic state remains unchanged
  - test uses fake providers and does not require live Codex CLI
- **Verification:** engine tests and full suite.
- **Dependencies:** T-154.

### T-162 — Add content draft empty-field regression

- **State:** done
- **Priority:** P2
- **Goal:** Protect the failure path when AI content drafting returns a world pack with empty required text fields.
- **Acceptance criteria:**
  - empty required title or room text raises a clear validation error
  - no generated content is accepted without deterministic schema validation
  - test uses fake providers and does not require live Codex CLI
- **Verification:** AI content draft tests and full suite.
- **Dependencies:** T-155.

### T-163 — Add turn-feedback vocabulary-note type regression

- **State:** done
- **Priority:** P2
- **Goal:** Protect the failure path when AI turn feedback returns malformed vocabulary notes.
- **Acceptance criteria:**
  - non-string vocabulary notes raise a clear provider error
  - deterministic state is rolled back when validation fails after a state-changing action
  - test uses fake providers and does not require live Codex CLI
- **Verification:** engine tests and full suite.
- **Dependencies:** T-156.

### T-164 — Add NPC dialogue vocabulary-note type regression

- **State:** done
- **Priority:** P2
- **Goal:** Protect the failure path when AI NPC dialogue returns malformed vocabulary notes.
- **Acceptance criteria:**
  - non-string vocabulary notes raise a clear provider error before display
  - deterministic state remains unchanged
  - test uses fake providers and does not require live Codex CLI
- **Verification:** engine tests and full suite.
- **Dependencies:** T-159.

### T-165 — Add room narration vocabulary-note type regression

- **State:** done
- **Priority:** P2
- **Goal:** Protect the failure path when AI room narration returns malformed vocabulary notes.
- **Acceptance criteria:**
  - non-string vocabulary notes raise a clear provider error before display
  - deterministic state remains unchanged
  - test uses fake providers and does not require live Codex CLI
- **Verification:** engine tests and full suite.
- **Dependencies:** T-161.

### T-166 — Add review evaluation boolean type regression

- **State:** done
- **Priority:** P2
- **Goal:** Protect the failure path when AI review evaluation returns a malformed judgment flag.
- **Acceptance criteria:**
  - non-boolean meaningful-use judgment raises a clear provider error
  - active review state remains unchanged
  - test uses fake providers and does not require live Codex CLI
- **Verification:** review engine tests and full suite.
- **Dependencies:** T-157.

### T-167 — Add vocabulary explanation extra-field regression

- **State:** done
- **Priority:** P2
- **Goal:** Protect the failure path when AI vocabulary explanations return unauthorized state-like fields.
- **Acceptance criteria:**
  - extra mutation-like fields raise a clear provider error before display
  - deterministic state remains unchanged
  - test uses fake providers and does not require live Codex CLI
- **Verification:** engine tests and full suite.
- **Dependencies:** T-158.

### T-168 — Add sentence interpretation extra-field regression

- **State:** done
- **Priority:** P2
- **Goal:** Protect the failure path when AI parser-miss interpretation returns unauthorized state-like fields.
- **Acceptance criteria:**
  - extra mutation-like fields raise a clear provider error before deterministic validation
  - deterministic state remains unchanged
  - test uses fake providers and does not require live Codex CLI
- **Verification:** engine tests and full suite.
- **Dependencies:** T-160.

### T-169 — Add NPC dialogue extra-field regression

- **State:** done
- **Priority:** P2
- **Goal:** Protect the failure path when AI NPC dialogue returns unauthorized state-like fields.
- **Acceptance criteria:**
  - extra mutation-like fields raise a clear provider error before display
  - deterministic state remains unchanged
  - test uses fake providers and does not require live Codex CLI
- **Verification:** engine tests and full suite.
- **Dependencies:** T-164.

### T-170 — Add room narration extra-field regression

- **State:** done
- **Priority:** P2
- **Goal:** Protect the failure path when AI room narration returns unauthorized state-like fields.
- **Acceptance criteria:**
  - extra mutation-like fields raise a clear provider error before display
  - deterministic state remains unchanged
  - test uses fake providers and does not require live Codex CLI
- **Verification:** engine tests and full suite.
- **Dependencies:** T-165.

### T-171 — Add turn feedback extra-field regression

- **State:** done
- **Priority:** P2
- **Goal:** Protect the failure path when AI turn feedback returns unauthorized state-like fields after a deterministic action.
- **Acceptance criteria:**
  - extra mutation-like fields raise a clear provider error before display
  - deterministic state is rolled back after a state-changing action
  - test uses fake providers and does not require live Codex CLI
- **Verification:** engine tests and full suite.
- **Dependencies:** T-163.

### T-172 — Add review evaluation extra-field regression

- **State:** done
- **Priority:** P2
- **Goal:** Protect the failure path when AI review evaluation returns unauthorized state-like fields.
- **Acceptance criteria:**
  - extra mutation-like fields raise a clear provider error before display
  - active review state remains unchanged
  - test uses fake providers and does not require live Codex CLI
- **Verification:** review engine tests and full suite.
- **Dependencies:** T-166.

### T-173 — Add content draft extra-field regression

- **State:** done
- **Priority:** P2
- **Goal:** Protect the failure path when AI content drafting returns unauthorized state-like fields outside the world-pack payload.
- **Acceptance criteria:**
  - extra mutation-like fields raise a clear validation error before generated content is accepted
  - deterministic schema validation remains the only acceptance gate
  - test uses fake providers and does not require live Codex CLI
- **Verification:** AI content draft tests and full suite.
- **Dependencies:** T-162.

### T-174 — Add content draft payload mutation-field regression

- **State:** done
- **Priority:** P2
- **Goal:** Protect the failure path when AI world-pack drafts include unauthorized mutation-like payload fields.
- **Acceptance criteria:**
  - payload fields that imply player state, rewards, saves, or inventory raise clear validation errors
  - no generated content is accepted without deterministic schema validation
  - test uses fake providers and does not require live Codex CLI
- **Verification:** AI content draft and world schema tests plus full suite.
- **Dependencies:** T-173.

### T-175 — Add Codex schema strictness coverage for content drafts

- **State:** done
- **Priority:** P2
- **Goal:** Ensure Codex CLI structured-output schemas for content drafting stay strict after validation expansions.
- **Acceptance criteria:**
  - generated response schema for content drafts has `additionalProperties: false` where required
  - test uses subprocess fakes and does not require live Codex CLI
  - existing provider command behavior remains unchanged
- **Verification:** Codex CLI provider tests and full suite.
- **Dependencies:** T-174.

### T-176 — Add content draft request strictness regression

- **State:** done
- **Priority:** P2
- **Goal:** Keep AI content-draft requests bounded to the documented prompt inputs before they reach providers.
- **Acceptance criteria:**
  - content-draft request models reject unauthorized extra fields such as player XP, inventory, or save paths
  - existing fake-provider content draft behavior remains unchanged
  - tests do not require live Codex CLI
- **Verification:** AI contract tests and full suite.
- **Dependencies:** T-175.

### T-177 — Add content draft rejection message regression

- **State:** done
- **Priority:** P2
- **Goal:** Keep invalid AI-authored world-pack draft failures clear enough for future in-game authoring tools.
- **Acceptance criteria:**
  - validation failures include whether the rejected layer is the content-draft envelope or the world-pack payload
  - nested payload field paths remain visible in the raised error
  - tests use fake providers and do not require live Codex CLI
- **Verification:** AI content draft tests and full suite.
- **Dependencies:** T-176.

### T-178 — Add turn-feedback request strictness regression

- **State:** done
- **Priority:** P2
- **Goal:** Keep turn-feedback prompts bounded to deterministic action context before they reach providers.
- **Acceptance criteria:**
  - turn-feedback request models reject unauthorized extra fields such as XP, inventory, or save paths
  - existing fake-provider turn-feedback behavior remains unchanged
  - tests do not require live Codex CLI
- **Verification:** AI contract tests and full suite.
- **Dependencies:** T-177.

### T-179 — Add vocabulary-explanation request strictness regression

- **State:** done
- **Priority:** P2
- **Goal:** Keep vocabulary-explanation prompts bounded to learner sentence and theme context before they reach providers.
- **Acceptance criteria:**
  - vocabulary-explanation request models reject unauthorized extra fields such as mastered flags, XP, or inventory
  - existing fake-provider vocabulary explanation behavior remains unchanged
  - tests do not require live Codex CLI
- **Verification:** AI contract tests and full suite.
- **Dependencies:** T-178.

### T-180 — Add sentence-interpretation request strictness regression

- **State:** done
- **Priority:** P2
- **Goal:** Keep parser-miss AI interpretation prompts bounded to visible deterministic context before they reach providers.
- **Acceptance criteria:**
  - sentence-interpretation request models reject unauthorized extra fields such as XP, inventory, or quest completion flags
  - existing fake-provider interpretation behavior remains unchanged
  - tests do not require live Codex CLI
- **Verification:** AI contract tests and full suite.
- **Dependencies:** T-179.

### T-181 — Add NPC dialogue request strictness regression

- **State:** done
- **Priority:** P2
- **Goal:** Keep NPC dialogue prompts bounded to visible deterministic context before they reach providers.
- **Acceptance criteria:**
  - NPC dialogue request models reject unauthorized extra fields such as XP, inventory, or quest completion flags
  - existing fake-provider NPC dialogue behavior remains unchanged
  - tests do not require live Codex CLI
- **Verification:** AI contract tests and full suite.
- **Dependencies:** T-180.

### T-182 — Add room narration request strictness regression

- **State:** done
- **Priority:** P2
- **Goal:** Keep room narration prompts bounded to deterministic room context before they reach providers.
- **Acceptance criteria:**
  - room narration request models reject unauthorized extra fields such as XP, inventory, or quest completion flags
  - existing fake-provider room narration behavior remains unchanged
  - tests do not require live Codex CLI
- **Verification:** AI contract tests and full suite.
- **Dependencies:** T-181.

### T-183 — Add review-evaluation request strictness regression

- **State:** done
- **Priority:** P2
- **Goal:** Keep review-evaluation prompts bounded to the active review word and learner answer before they reach providers.
- **Acceptance criteria:**
  - review-evaluation request models reject unauthorized extra fields such as XP, inventory, or review-stage overrides
  - existing fake-provider review-evaluation behavior remains unchanged
  - tests do not require live Codex CLI
- **Verification:** AI contract tests and full suite.
- **Dependencies:** T-182.

### T-184 — Audit remaining AI request strictness coverage

- **State:** done
- **Priority:** P2
- **Goal:** Confirm every AI request model has explicit strictness coverage or a documented reason for not needing it.
- **Acceptance criteria:**
  - tests or notes cover each request model in `toefl_rpg.ai.contract`
  - any missing strictness regression is split into a small follow-up task
  - no live Codex CLI is required
- **Verification:** AI contract tests and full suite.
- **Dependencies:** T-183.

### T-185 — Audit parser intent shape consistency

- **State:** done
- **Priority:** P2
- **Goal:** Ensure deterministic parser intents and AI interpretation results continue to share the same action vocabulary and target conventions.
- **Acceptance criteria:**
  - tests identify every deterministic action exposed through parser or AI interpretation
  - target conventions for movement, collection, use, attack, talk, look, explain, review, status, and inventory are documented by assertions or fixtures
  - no live Codex CLI is required
- **Verification:** parser, AI contract, and rules tests plus full suite.
- **Dependencies:** T-184.

### T-186 — Add learner sentence corpus case for polite command forms

- **State:** done
- **Priority:** P2
- **Goal:** Expand full-sentence input coverage for polite learner commands such as "Could you..." and "Please...".
- **Acceptance criteria:**
  - corpus includes at least one accepted deterministic case and one AI-interpretation fallback case
  - expected state mutation remains deterministic and explicit
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-185.

### T-187 — Add renderer regression for AI coaching versus deterministic results

- **State:** done
- **Priority:** P2
- **Goal:** Keep AI coaching text visually distinct from deterministic result summaries in player-facing output.
- **Acceptance criteria:**
  - renderer tests assert separate labels or sections for AI feedback and deterministic result text
  - at least one successful action and one rejected action are covered
  - no live Codex CLI is required
- **Verification:** renderer tests and full suite.
- **Dependencies:** T-186.

### T-188 — Add learner sentence corpus case for desire-based phrasing

- **State:** done
- **Priority:** P2
- **Goal:** Expand full-sentence input coverage for learner phrases such as "I would like to..." and "I need to..." without changing deterministic authority.
- **Acceptance criteria:**
  - corpus includes at least one accepted desire-based movement or interaction sentence
  - expected parser route or AI fallback route is explicit
  - expected state mutation remains deterministic and explicit
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-187.

### T-189 — Add renderer regression for vocabulary explanation output boundaries

- **State:** done
- **Priority:** P2
- **Goal:** Keep vocabulary explanation result text separate from turn-level AI coaching and avoid showing an empty feedback panel.
- **Acceptance criteria:**
  - renderer tests cover vocabulary explanation output with no turn feedback panel
  - explanation, example, and memory hint remain in the deterministic result section
  - no live Codex CLI is required
- **Verification:** renderer tests and full suite.
- **Dependencies:** T-188.

### T-190 — Add AI feedback formatting regression for multiple vocabulary notes

- **State:** done
- **Priority:** P2
- **Goal:** Ensure multiple AI vocabulary notes stay readable and separate in the English feedback text.
- **Acceptance criteria:**
  - rules or renderer tests cover at least two vocabulary notes from AI turn feedback
  - each note is rendered on a distinct `Vocabulary:` line
  - deterministic result text remains unchanged
  - no live Codex CLI is required
- **Verification:** rules or renderer tests plus full suite.
- **Dependencies:** T-189.

### T-191 — Add learner sentence corpus case for permission-question phrasing

- **State:** done
- **Priority:** P2
- **Goal:** Expand full-sentence input coverage for learner permission questions such as "Can I..." or "May I..." while keeping deterministic state authority.
- **Acceptance criteria:**
  - corpus includes at least one accepted permission-question action sentence
  - expected parser route or AI fallback route is explicit
  - expected state mutation remains deterministic and explicit
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-190.

### T-192 — Add state-preservation regression for AI interpretation provider failure

- **State:** done
- **Priority:** P2
- **Goal:** Ensure parser-miss AI interpretation failures do not mutate player state before raising a clear AI provider error.
- **Acceptance criteria:**
  - test covers an AI interpretation exception or malformed response during an otherwise actionable sentence
  - player location, inventory, XP, quest progress, and mastery remain unchanged
  - no live Codex CLI is required
- **Verification:** rules tests and full suite.
- **Dependencies:** T-191.

### T-193 — Add plain-console renderer regression for result and feedback labels

- **State:** done
- **Priority:** P2
- **Goal:** Keep fallback non-Rich terminal output clear when rendering deterministic results and AI feedback.
- **Acceptance criteria:**
  - renderer test covers `Panel is None` fallback behavior or an equivalent plain-console path
  - deterministic result text and English feedback keep separate labels
  - no live Codex CLI is required
- **Verification:** renderer tests and full suite.
- **Dependencies:** T-192.

### T-194 — Add learner sentence corpus case for negative request phrasing

- **State:** done
- **Priority:** P2
- **Goal:** Ensure learner phrasing such as "I do not want to..." does not accidentally execute the positive action.
- **Acceptance criteria:**
  - corpus includes at least one negative request sentence
  - expected route and no-mutation outcome are explicit
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-193.

### T-195 — Add parser regression for punctuation-heavy movement input

- **State:** done
- **Priority:** P2
- **Goal:** Keep common punctuation-heavy learner movement input parseable without weakening action authority.
- **Acceptance criteria:**
  - parser test covers at least one movement sentence with extra punctuation
  - expected action and target are explicit
  - no live Codex CLI is required
- **Verification:** parser tests and full suite.
- **Dependencies:** T-194.

### T-196 — Add review answer corpus case for synonym-heavy incorrect use

- **State:** done
- **Priority:** P2
- **Goal:** Keep review-answer AI evaluation coverage clear when a learner writes a fluent sentence that does not use the active target word meaningfully.
- **Acceptance criteria:**
  - review corpus includes a fluent but incorrect or off-target sentence
  - fake AI evaluation keeps review active without XP
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-195.

### T-197 — Add review answer corpus case for memorized definition misuse

- **State:** done
- **Priority:** P2
- **Goal:** Keep review evaluation coverage clear when a learner writes a grammatical definition-like sentence that names the word but does not show usable meaning in context.
- **Acceptance criteria:**
  - review corpus includes a fluent definition-style answer that names the active word without a meaningful TOEFL use
  - fake AI evaluation rejects it while keeping the review active and awarding no XP
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-196.

### T-198 — Add learner sentence corpus case for indirect polite questions

- **State:** done
- **Priority:** P2
- **Goal:** Expand full-sentence input coverage for indirect polite requests such as "Would you mind..." while preserving deterministic state authority.
- **Acceptance criteria:**
  - corpus includes at least one indirect polite question
  - expected parser route or AI fallback route is explicit
  - expected mutation or no-mutation outcome is explicit
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-197.

### T-199 — Add review answer corpus case for context mismatch

- **State:** done
- **Priority:** P2
- **Goal:** Protect review feedback when the target word is used in a sentence that is fluent but unrelated to the biology context being reviewed.
- **Acceptance criteria:**
  - review corpus includes a full sentence that contains the active target word but mismatches the requested learning context
  - fake AI evaluation rejects it without XP and keeps the active review word
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-198.

### T-200 — Add learner sentence corpus case for hedged intention phrasing

- **State:** done
- **Priority:** P2
- **Goal:** Expand full-sentence input coverage for learner hedges such as "I think I should..." while preserving deterministic state authority.
- **Acceptance criteria:**
  - corpus includes at least one hedged intention sentence
  - expected parser route or AI fallback route is explicit
  - expected mutation or no-mutation outcome is explicit
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-199.

### T-201 — Add learner sentence corpus case for pronoun-like item references

- **State:** done
- **Priority:** P2
- **Goal:** Clarify how learner input with references such as "it" should route when deterministic state still owns item identity and validation.
- **Acceptance criteria:**
  - corpus includes at least one pronoun-like item reference sentence
  - expected AI interpretation route and deterministic validation outcome are explicit
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-200.

### T-202 — Add learner sentence corpus case for compound action requests

- **State:** done
- **Priority:** P2
- **Goal:** Clarify how sentences with multiple requested actions should route when deterministic code must execute only one validated action at a time.
- **Acceptance criteria:**
  - corpus includes at least one compound action sentence
  - expected parser route or AI fallback route is explicit
  - expected mutation or no-mutation outcome is explicit
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-201.

### T-203 — Add review answer corpus case for vague but grammatical target use

- **State:** done
- **Priority:** P2
- **Goal:** Protect review feedback when a learner uses the target word in a grammatical but vague sentence that does not prove meaning.
- **Acceptance criteria:**
  - review corpus includes a vague full sentence containing the active review word
  - fake AI evaluation rejects it without XP and keeps the active review word
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-202.

### T-204 — Add learner sentence corpus case for self-correction phrasing

- **State:** done
- **Priority:** P2
- **Goal:** Clarify how learner sentences with self-correction such as "I mean..." should route without letting AI mutate state directly.
- **Acceptance criteria:**
  - corpus includes at least one self-correction sentence
  - expected parser route or AI fallback route is explicit
  - expected mutation or no-mutation outcome is explicit
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-203.

### T-205 — Add review answer corpus case for metaphorical target use

- **State:** done
- **Priority:** P2
- **Goal:** Protect review feedback when the active word appears metaphorically rather than as the intended Biology meaning.
- **Acceptance criteria:**
  - review corpus includes a fluent metaphorical sentence containing the active review word
  - fake AI evaluation rejects it without XP and keeps the active review word
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-204.

### T-206 — Add learner sentence corpus case for overly broad location requests

- **State:** done
- **Priority:** P2
- **Goal:** Clarify how learner requests such as "take me to the lab" route when deterministic movement requires concrete exits.
- **Acceptance criteria:**
  - corpus includes at least one broad location request sentence
  - expected parser route or AI fallback route is explicit
  - expected mutation or no-mutation outcome is explicit
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-205.

### T-207 — Add review answer corpus case for copied example reuse

- **State:** done
- **Priority:** P2
- **Goal:** Protect review feedback when a learner repeats a suggested example without showing fresh understanding.
- **Acceptance criteria:**
  - review corpus includes at least one copied-example-style answer for the active review word
  - expected AI evaluation result and deterministic XP/review outcome are explicit
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-206.

### T-208 — Add learner sentence corpus case for ambiguous enemy references

- **State:** done
- **Priority:** P2
- **Goal:** Clarify how learner attack requests with vague enemy references route when deterministic combat requires a concrete visible target.
- **Acceptance criteria:**
  - corpus includes at least one vague enemy-reference attack sentence
  - expected parser route or AI fallback route is explicit
  - expected combat mutation or no-mutation outcome is explicit
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-207.

### T-209 — Add learner sentence corpus case for broad tool-use requests

- **State:** done
- **Priority:** P2
- **Goal:** Clarify how learner requests such as "use the tool" route when deterministic item use requires a concrete inventory or visible target.
- **Acceptance criteria:**
  - corpus includes at least one broad tool-use sentence
  - expected parser route or AI fallback route is explicit
  - expected mutation or no-mutation outcome is explicit
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-208.

### T-210 — Add review answer corpus case for negated target-word use

- **State:** done
- **Priority:** P2
- **Goal:** Protect review feedback when a learner uses the active word in a sentence that negates or avoids demonstrating the target meaning.
- **Acceptance criteria:**
  - review corpus includes at least one negated target-word answer
  - expected AI evaluation result and deterministic XP/review outcome are explicit
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-209.

### T-211 — Add learner sentence corpus case for broad conversation requests

- **State:** done
- **Priority:** P2
- **Goal:** Clarify how learner requests such as "talk to someone" route when deterministic dialogue requires a concrete visible NPC.
- **Acceptance criteria:**
  - corpus includes at least one broad conversation sentence
  - expected parser route or AI fallback route is explicit
  - expected mutation or no-mutation outcome is explicit
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-210.

### T-212 — Add review answer corpus case for list-like target-word fragments

- **State:** done
- **Priority:** P2
- **Goal:** Protect review feedback when a learner provides a list-like fragment instead of a sentence that demonstrates the active word.
- **Acceptance criteria:**
  - review corpus includes at least one list-like fragment or fragment-style answer
  - expected deterministic precheck or AI evaluation route is explicit
  - expected XP/review outcome is explicit
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-211.

### T-213 — Add learner sentence corpus case for broad collection requests

- **State:** done
- **Priority:** P2
- **Goal:** Clarify how learner requests such as "collect the thing" route when deterministic collection requires a concrete visible item.
- **Acceptance criteria:**
  - corpus includes at least one broad collection sentence
  - expected parser route or AI fallback route is explicit
  - expected mutation or no-mutation outcome is explicit
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-212.

### T-214 — Add review answer corpus case for question-form target use

- **State:** done
- **Priority:** P2
- **Goal:** Protect review feedback when a learner asks a question about the active word instead of using it to show meaning.
- **Acceptance criteria:**
  - review corpus includes at least one question-form answer containing the active review word
  - expected AI evaluation result and deterministic XP/review outcome are explicit
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-213.

### T-215 — Add learner sentence corpus case for broad inspection requests

- **State:** done
- **Priority:** P2
- **Goal:** Clarify how learner requests such as "inspect everything" route when deterministic inspection requires a concrete visible target.
- **Acceptance criteria:**
  - corpus includes at least one broad inspection sentence
  - expected parser route or AI fallback route is explicit
  - expected mutation or no-mutation outcome is explicit
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-214.

### T-216 — Add review answer corpus case for quoted target-word mention

- **State:** done
- **Priority:** P2
- **Goal:** Protect review feedback when a learner only mentions the target word as a quoted term instead of using it in context.
- **Acceptance criteria:**
  - review corpus includes at least one quoted-word answer containing the active review word
  - expected AI evaluation result and deterministic XP/review outcome are explicit
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-215.

### T-217 — Add learner sentence corpus case for vague combat requests

- **State:** done
- **Priority:** P2
- **Goal:** Clarify how learner requests such as "fight it" route when deterministic combat requires a visible enemy target.
- **Acceptance criteria:**
  - corpus includes at least one vague combat sentence
  - expected parser route or AI fallback route is explicit
  - expected mutation or no-mutation outcome is explicit
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-216.

### T-218 — Add review answer corpus case for hypothetical target-word use

- **State:** done
- **Priority:** P2
- **Goal:** Protect review feedback when a learner writes a hypothetical sentence that names the target word but does not show concrete meaning in context.
- **Acceptance criteria:**
  - review corpus includes at least one hypothetical answer containing the active review word
  - expected AI evaluation result and deterministic XP/review outcome are explicit
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-217.

### T-219 — Add learner sentence corpus case for vague inventory requests

- **State:** done
- **Priority:** P2
- **Goal:** Clarify how learner requests such as "show me my stuff" route when deterministic inventory commands require a supported inventory phrase or AI interpretation.
- **Acceptance criteria:**
  - corpus includes at least one vague inventory-style sentence
  - expected parser route or AI fallback route is explicit
  - expected mutation or no-mutation outcome is explicit
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-218.

### T-220 — Add review answer corpus case for overgeneralized target-word use

- **State:** done
- **Priority:** P2
- **Goal:** Protect review feedback when a learner overgeneralizes the active word into an incorrect broad category.
- **Acceptance criteria:**
  - review corpus includes at least one overgeneralized answer containing the active review word
  - expected AI evaluation result and deterministic XP/review outcome are explicit
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-219.

### T-221 — Add learner sentence corpus case for broad status requests

- **State:** done
- **Priority:** P2
- **Goal:** Clarify how learner requests such as "tell me how I am doing" route when deterministic status commands require a supported phrase or AI interpretation.
- **Acceptance criteria:**
  - corpus includes at least one broad status-style sentence
  - expected parser route or AI fallback route is explicit
  - expected mutation or no-mutation outcome is explicit
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-220.

### T-222 — Add review answer corpus case for learner uncertainty phrasing

- **State:** done
- **Priority:** P2
- **Goal:** Protect review feedback when a learner says they are unsure about the active word instead of using it meaningfully.
- **Acceptance criteria:**
  - review corpus includes at least one uncertainty answer containing the active review word
  - expected AI evaluation result and deterministic XP/review outcome are explicit
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-221.

### T-223 — Add learner sentence corpus case for indirect help requests

- **State:** done
- **Priority:** P2
- **Goal:** Clarify how learner requests such as "what can I do now" route when deterministic help commands require a supported phrase or AI interpretation.
- **Acceptance criteria:**
  - corpus includes at least one indirect help-style sentence
  - expected parser route or AI fallback route is explicit
  - expected mutation or no-mutation outcome is explicit
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-222.

### T-224 — Add review answer corpus case for tautological target-word use

- **State:** done
- **Priority:** P2
- **Goal:** Protect review feedback when a learner uses the active word in a circular or tautological sentence that does not show meaning.
- **Acceptance criteria:**
  - review corpus includes at least one tautological answer containing the active review word
  - expected AI evaluation result and deterministic XP/review outcome are explicit
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-223.

### T-225 — Add learner sentence corpus case for indirect review requests

- **State:** done
- **Priority:** P2
- **Goal:** Clarify how learner requests such as "quiz me on words" route when deterministic review commands require a supported phrase or AI interpretation.
- **Acceptance criteria:**
  - corpus includes at least one indirect review-style sentence
  - expected parser route or AI fallback route is explicit
  - expected mutation or no-mutation outcome is explicit
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-224.

### T-226 — Add review answer corpus case for shallow example-label target-word use

- **State:** done
- **Priority:** P2
- **Goal:** Protect review feedback when a learner writes that the active word is "an example" of a topic without demonstrating the word's meaning.
- **Acceptance criteria:**
  - review corpus includes at least one shallow example-label answer containing the active review word
  - expected AI evaluation result and deterministic XP/review outcome are explicit
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-225.

### T-227 — Add learner sentence corpus case for indirect explanation requests

- **State:** done
- **Priority:** P2
- **Goal:** Clarify how learner requests such as "tell me what this word means" route when deterministic explanation commands require a supported phrase or AI interpretation.
- **Acceptance criteria:**
  - corpus includes at least one indirect vocabulary-explanation-style sentence
  - expected parser route or AI fallback route is explicit
  - expected mutation or no-mutation outcome is explicit
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-226.

### T-228 — Add review answer corpus case for personal-preference target-word use

- **State:** done
- **Priority:** P2
- **Goal:** Protect review feedback when a learner writes a personal preference about the active word without demonstrating its meaning.
- **Acceptance criteria:**
  - review corpus includes at least one personal-preference answer containing the active review word
  - expected AI evaluation result and deterministic XP/review outcome are explicit
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-227.

### T-229 — Add learner sentence corpus case for indirect look requests

- **State:** done
- **Priority:** P2
- **Goal:** Clarify how learner requests such as "what is around me" route when deterministic look commands require a supported phrase or AI interpretation.
- **Acceptance criteria:**
  - corpus includes at least one indirect look-style sentence
  - expected parser route or AI fallback route is explicit
  - expected mutation or no-mutation outcome is explicit
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-228.

### T-230 — Add learner sentence corpus case for indirect NPC dialogue requests

- **State:** done
- **Priority:** P2
- **Goal:** Clarify how learner requests such as "ask the scientist for advice" route when deterministic talk commands require a supported phrase or AI interpretation.
- **Acceptance criteria:**
  - corpus includes at least one indirect NPC-dialogue-style sentence
  - expected parser route or AI fallback route is explicit
  - expected mutation or no-mutation outcome is explicit
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-229.

### T-231 — Add review answer corpus case for emotional-reaction target-word use

- **State:** done
- **Priority:** P2
- **Goal:** Protect review feedback when a learner writes only an emotional reaction to the active word without demonstrating its meaning.
- **Acceptance criteria:**
  - review corpus includes at least one emotional-reaction answer containing the active review word
  - expected AI evaluation result and deterministic XP/review outcome are explicit
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-230.

### T-232 — Add learner sentence corpus case for indirect status comparison requests

- **State:** done
- **Priority:** P2
- **Goal:** Clarify how learner requests such as "am I ready to continue" route when deterministic status commands require a supported phrase or AI interpretation.
- **Acceptance criteria:**
  - corpus includes at least one indirect status-comparison-style sentence
  - expected parser route or AI fallback route is explicit
  - expected mutation or no-mutation outcome is explicit
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-231.

### T-233 — Add learner sentence corpus case for indirect inventory availability requests

- **State:** done
- **Priority:** P2
- **Goal:** Clarify how learner requests such as "what am I carrying" route when deterministic inventory commands require a supported phrase or AI interpretation.
- **Acceptance criteria:**
  - corpus includes at least one indirect inventory-availability-style sentence
  - expected parser route or AI fallback route is explicit
  - expected mutation or no-mutation outcome is explicit
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-232.

### T-234 — Add learner sentence corpus case for indirect quest-progress requests

- **State:** done
- **Priority:** P2
- **Goal:** Clarify how learner requests such as "what part of the investigation remains" route when progress can be answered through deterministic status/help style actions.
- **Acceptance criteria:**
  - corpus includes at least one indirect quest-progress-style sentence
  - expected parser route or AI fallback route is explicit
  - expected mutation or no-mutation outcome is explicit
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-233.

### T-235 — Add review answer corpus case for analogy-only target-word use

- **State:** done
- **Priority:** P2
- **Goal:** Protect review feedback when a learner uses the active target word only in an analogy without showing the Biology meaning.
- **Acceptance criteria:**
  - review corpus includes at least one analogy-only answer containing the active review word
  - expected AI evaluation result and deterministic XP/review outcome are explicit
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-234.

### T-236 — Add learner sentence corpus case for indirect vocabulary-reminder requests

- **State:** done
- **Priority:** P2
- **Goal:** Clarify how learner requests such as "which word should I practice here" route when the answer can be given through deterministic help, look, or explanation-style actions.
- **Acceptance criteria:**
  - corpus includes at least one indirect vocabulary-reminder-style sentence
  - expected parser route or AI fallback route is explicit
  - expected mutation or no-mutation outcome is explicit
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-235.

### T-237 — Add review answer corpus case for cause-effect-free target-word use

- **State:** done
- **Priority:** P2
- **Goal:** Protect review feedback when a learner includes the active word but gives no biological cause, effect, role, or property.
- **Acceptance criteria:**
  - review corpus includes at least one cause-effect-free answer containing the active review word
  - expected AI evaluation result and deterministic XP/review outcome are explicit
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-236.

### T-238 — Add learner sentence corpus case for indirect save-exit intent

- **State:** done
- **Priority:** P2
- **Goal:** Clarify how learner requests such as "I am done for now" route when the intended outcome is deterministic quit/save behavior.
- **Acceptance criteria:**
  - corpus includes at least one indirect save-exit-style sentence
  - expected parser route or AI fallback route is explicit
  - expected quit/save result and mutation expectations are explicit
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-237.

### T-239 — Add review answer corpus case for unsupported certainty claim

- **State:** done
- **Priority:** P2
- **Goal:** Protect review feedback when a learner uses the active word in a confident sentence that still does not demonstrate the Biology meaning.
- **Acceptance criteria:**
  - review corpus includes at least one unsupported-certainty answer containing the active review word
  - expected AI evaluation result and deterministic XP/review outcome are explicit
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-238.

### T-240 — Add learner sentence corpus case for indirect repeat-room narration requests

- **State:** done
- **Priority:** P2
- **Goal:** Clarify how learner requests such as "remind me where I am" route when the answer can be given through deterministic look handling and AI room narration.
- **Acceptance criteria:**
  - corpus includes at least one indirect repeat-room-narration-style sentence
  - expected parser route or AI fallback route is explicit
  - expected mutation or no-mutation outcome is explicit
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-239.

### T-241 — Add review answer corpus case for location-only target-word use

- **State:** done
- **Priority:** P2
- **Goal:** Protect review feedback when a learner places the active word in a location but does not show a biological role, property, or consequence.
- **Acceptance criteria:**
  - review corpus includes at least one location-only answer containing the active review word
  - expected AI evaluation result and deterministic XP/review outcome are explicit
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-240.

### T-242 — Add learner sentence corpus case for indirect enemy-warning requests

- **State:** done
- **Priority:** P2
- **Goal:** Clarify how learner requests such as "what danger is nearby" route when the current room has no live enemy versus when combat validation is required.
- **Acceptance criteria:**
  - corpus includes at least one indirect enemy-warning-style sentence
  - expected parser route or AI fallback route is explicit
  - expected mutation or no-mutation outcome is explicit
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-241.

### T-243 — Add review answer corpus case for relation-only target-word use

- **State:** done
- **Priority:** P2
- **Goal:** Protect review feedback when a learner names a relation involving the active word but does not show the Biology meaning, role, property, or consequence.
- **Acceptance criteria:**
  - review corpus includes at least one relation-only answer containing the active review word
  - expected AI evaluation result and deterministic XP/review outcome are explicit
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-242.

### T-244 — Add learner sentence corpus case for indirect map-or-exits requests

- **State:** done
- **Priority:** P2
- **Goal:** Clarify how learner requests such as "which paths can I take" route when the answer can be given through deterministic room narration or help without mutating state.
- **Acceptance criteria:**
  - corpus includes at least one indirect map-or-exits-style sentence
  - expected parser route or AI fallback route is explicit
  - expected mutation or no-mutation outcome is explicit
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-243.

### T-245 — Add review answer corpus case for source-only target-word use

- **State:** done
- **Priority:** P2
- **Goal:** Protect review feedback when a learner says where they learned the active word but does not show its Biology meaning, role, property, or consequence.
- **Acceptance criteria:**
  - review corpus includes at least one source-only answer containing the active review word
  - expected AI evaluation result and deterministic XP/review outcome are explicit
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-244.

### T-246 — Add learner sentence corpus case for indirect goal reminder requests

- **State:** done
- **Priority:** P2
- **Goal:** Clarify how learner requests such as "what should I accomplish next" route when the answer can be given through deterministic status or help without mutating state.
- **Acceptance criteria:**
  - corpus includes at least one indirect goal-reminder-style sentence
  - expected parser route or AI fallback route is explicit
  - expected mutation or no-mutation outcome is explicit
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-245.

### T-247 — Add learner sentence corpus case for prerequisite reminders

- **State:** done
- **Priority:** P2
- **Goal:** Clarify how learner requests such as "what do I need before using the microscope" route when the answer can be given through deterministic help, status, or room narration without mutating state.
- **Acceptance criteria:**
  - corpus includes at least one indirect prerequisite-reminder sentence
  - expected parser route or AI fallback route is explicit
  - expected mutation or no-mutation outcome is explicit
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-246.

### T-248 — Add learner sentence corpus case for strategy advice requests

- **State:** done
- **Priority:** P2
- **Goal:** Clarify how learner requests such as "how should I deal with the vine" route when the answer should advise through deterministic help, status, or room narration instead of performing combat.
- **Acceptance criteria:**
  - corpus includes at least one indirect strategy-advice sentence
  - expected parser route or AI fallback route is explicit
  - expected mutation or no-mutation outcome is explicit
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-247.

### T-249 — Add review answer corpus case for category-label target use

- **State:** done
- **Priority:** P2
- **Goal:** Protect review feedback when a learner names the broad category of the active word but does not show its Biology meaning, role, property, or consequence.
- **Acceptance criteria:**
  - review corpus includes at least one category-label answer containing the active review word
  - expected AI evaluation result and deterministic XP/review outcome are explicit
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-248.

### T-250 — Add learner sentence corpus case for indirect recap requests

- **State:** done
- **Priority:** P2
- **Goal:** Clarify how learner requests such as "can you summarize what happened" route when the answer can be given through deterministic status, help, or room narration without mutating state.
- **Acceptance criteria:**
  - corpus includes at least one indirect recap-style sentence
  - expected parser route or AI fallback route is explicit
  - expected mutation or no-mutation outcome is explicit
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-249.

### T-251 — Add review answer corpus case for answer-label target use

- **State:** done
- **Priority:** P2
- **Goal:** Protect review feedback when a learner says the active word is the answer or review target but does not show its Biology meaning, role, property, or consequence.
- **Acceptance criteria:**
  - review corpus includes at least one answer-label sentence containing the active review word
  - expected AI evaluation result and deterministic XP/review outcome are explicit
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-250.

### T-252 — Add learner sentence corpus case for indirect readiness checks

- **State:** done
- **Priority:** P2
- **Goal:** Clarify how learner requests such as "am I ready to fight" route when the answer should use deterministic status or room narration instead of performing combat.
- **Acceptance criteria:**
  - corpus includes at least one indirect readiness-check sentence
  - expected parser route or AI fallback route is explicit
  - expected mutation or no-mutation outcome is explicit
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-251.

### T-253 — Add review answer corpus case for translation-only target use

- **State:** done
- **Priority:** P2
- **Goal:** Protect review feedback when a learner says they can translate the active word but does not show its Biology meaning, role, property, or consequence.
- **Acceptance criteria:**
  - review corpus includes at least one translation-only sentence containing the active review word
  - expected AI evaluation result and deterministic XP/review outcome are explicit
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-252.

### T-254 — Add learner sentence corpus case for indirect retreat advice requests

- **State:** done
- **Priority:** P2
- **Goal:** Clarify how learner requests such as "should I retreat from here" route when the answer should use deterministic status or room narration instead of moving or attacking.
- **Acceptance criteria:**
  - corpus includes at least one indirect retreat-advice sentence
  - expected parser route or AI fallback route is explicit
  - expected mutation or no-mutation outcome is explicit
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-253.

### T-255 — Add review answer corpus case for spelling-only target use

- **State:** done
- **Priority:** P2
- **Goal:** Protect review feedback when a learner comments on the spelling or letters of the active word but does not show its Biology meaning, role, property, or consequence.
- **Acceptance criteria:**
  - review corpus includes at least one spelling-only sentence containing the active review word
  - expected AI evaluation result and deterministic XP/review outcome are explicit
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-254.

### T-256 — Add learner sentence corpus case for indirect healing or rest requests

- **State:** done
- **Priority:** P2
- **Goal:** Clarify how learner requests such as "can I rest here" route when no rest/heal command exists, preserving deterministic state while still giving useful AI-guided feedback.
- **Acceptance criteria:**
  - corpus includes at least one indirect healing or rest sentence
  - expected parser route or AI fallback route is explicit
  - expected mutation or no-mutation outcome is explicit
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-255.

### T-257 — Add review answer corpus case for pronunciation-only target use

- **State:** done
- **Priority:** P2
- **Goal:** Protect review feedback when a learner comments on pronouncing the active word but does not show its Biology meaning, role, property, or consequence.
- **Acceptance criteria:**
  - review corpus includes at least one pronunciation-only sentence containing the active review word
  - expected AI evaluation result and deterministic XP/review outcome are explicit
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-256.

### T-258 — Add review answer corpus case for etymology-only target use

- **State:** done
- **Priority:** P2
- **Goal:** Protect review feedback when a learner comments on the origin or history of the active word but does not show its Biology meaning, role, property, or consequence.
- **Acceptance criteria:**
  - review corpus includes at least one etymology-only sentence containing the active review word
  - expected AI evaluation result and deterministic XP/review outcome are explicit
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-257.

### T-259 — Add learner sentence corpus case for indirect hint requests

- **State:** done
- **Priority:** P2
- **Goal:** Clarify how learner requests such as "can you give me a hint" route when the answer should use deterministic help, status, or room narration without changing game state.
- **Acceptance criteria:**
  - corpus includes at least one indirect hint-request sentence
  - expected parser route or AI fallback route is explicit
  - expected mutation or no-mutation outcome is explicit
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-258.

### T-260 — Add review answer corpus case for morphology-only target use

- **State:** done
- **Priority:** P2
- **Goal:** Protect review feedback when a learner comments on the form, suffix, or grammar of the active word but does not show its Biology meaning, role, property, or consequence.
- **Acceptance criteria:**
  - review corpus includes at least one morphology-only sentence containing the active review word
  - expected AI evaluation result and deterministic XP/review outcome are explicit
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-259.

### T-261 — Add learner sentence corpus case for indirect route-planning requests

- **State:** done
- **Priority:** P2
- **Goal:** Clarify how learner requests such as "how can I reach the microscope tent" route when the answer should use deterministic help, status, or room narration without moving the player automatically.
- **Acceptance criteria:**
  - corpus includes at least one indirect route-planning sentence
  - expected AI fallback route and deterministic no-mutation outcome are explicit
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-260.

### T-262 — Add review answer corpus case for frequency-only target use

- **State:** done
- **Priority:** P2
- **Goal:** Protect review feedback when a learner says the active word is common or frequent in TOEFL passages but does not show its Biology meaning, role, property, or consequence.
- **Acceptance criteria:**
  - review corpus includes at least one frequency-only sentence containing the active review word
  - expected AI evaluation result and deterministic XP/review outcome are explicit
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-261.

### T-263 — Add review answer corpus case for visual-form-only target use

- **State:** done
- **Priority:** P2
- **Goal:** Protect review feedback when a learner comments on how the active word looks on the page but does not show its Biology meaning, role, property, or consequence.
- **Acceptance criteria:**
  - review corpus includes at least one visual-form-only sentence containing the active review word
  - expected AI evaluation result and deterministic XP/review outcome are explicit
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-262.

### T-264 — Add learner sentence corpus case for indirect objective-priority requests

- **State:** done
- **Priority:** P2
- **Goal:** Clarify how learner requests such as "which task is most urgent" route when the answer should use deterministic status or help without mutating state.
- **Acceptance criteria:**
  - corpus includes at least one indirect objective-priority sentence
  - expected AI fallback route and deterministic no-mutation outcome are explicit
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-263.

### T-265 — Add review answer corpus case for difficulty-only target use

- **State:** done
- **Priority:** P2
- **Goal:** Protect review feedback when a learner says the active word is difficult or easy to remember but does not show its Biology meaning, role, property, or consequence.
- **Acceptance criteria:**
  - review corpus includes at least one difficulty-only sentence containing the active review word
  - expected AI evaluation result and deterministic XP/review outcome are explicit
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-264.

### T-266 — Add review answer corpus case for memorization-method-only target use

- **State:** done
- **Priority:** P2
- **Goal:** Protect review feedback when a learner says how they memorize the active word but does not show its Biology meaning, role, property, or consequence.
- **Acceptance criteria:**
  - review corpus includes at least one memorization-method-only sentence containing the active review word
  - expected AI evaluation result and deterministic XP/review outcome are explicit
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-265.

### T-267 — Add learner sentence corpus case for indirect safety-check requests

- **State:** done
- **Priority:** P2
- **Goal:** Clarify how learner requests such as "is it safe to move on" route when the answer should use deterministic status or room narration without moving, attacking, or mutating state.
- **Acceptance criteria:**
  - corpus includes at least one indirect safety-check sentence
  - expected AI fallback route and deterministic no-mutation outcome are explicit
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-266.

### T-268 — Add review answer corpus case for confidence-only target use

- **State:** done
- **Priority:** P2
- **Goal:** Protect review feedback when a learner says they feel confident about the active word but does not show its Biology meaning, role, property, or consequence.
- **Acceptance criteria:**
  - review corpus includes at least one confidence-only sentence containing the active review word
  - expected AI evaluation result and deterministic XP/review outcome are explicit
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-267.

### T-269 — Add learner sentence corpus case for indirect backtracking requests

- **State:** done
- **Priority:** P2
- **Goal:** Clarify how learner requests such as "how do I get back to camp" route when the answer should use deterministic room narration or status without moving automatically.
- **Acceptance criteria:**
  - corpus includes at least one indirect backtracking sentence
  - expected AI fallback route and deterministic no-mutation outcome are explicit
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-268.

### T-270 — Add review answer corpus case for comparison-only target use

- **State:** done
- **Priority:** P2
- **Goal:** Protect review feedback when a learner compares the active word with another word but does not show its Biology meaning, role, property, or consequence.
- **Acceptance criteria:**
  - review corpus includes at least one comparison-only sentence containing the active review word
  - expected AI evaluation result and deterministic XP/review outcome are explicit
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-269.

### T-271 — Add learner sentence corpus case for indirect detour requests

- **State:** done
- **Priority:** P2
- **Goal:** Clarify how learner requests such as "is there another way around" route when the answer should use deterministic room narration or help without moving automatically.
- **Acceptance criteria:**
  - corpus includes at least one indirect detour sentence
  - expected AI fallback route and deterministic no-mutation outcome are explicit
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-270.

### T-272 — Add review answer corpus case for test-strategy-only target use

- **State:** done
- **Priority:** P2
- **Goal:** Protect review feedback when a learner says the active word helps with TOEFL test strategy but does not show its Biology meaning, role, property, or consequence.
- **Acceptance criteria:**
  - review corpus includes at least one test-strategy-only sentence containing the active review word
  - expected AI evaluation result and deterministic XP/review outcome are explicit
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-271.

### T-273 — Add review answer corpus case for score-goal-only target use

- **State:** done
- **Priority:** P2
- **Goal:** Protect review feedback when a learner says the active word helps a TOEFL score goal but does not show its Biology meaning, role, property, or consequence.
- **Acceptance criteria:**
  - review corpus includes at least one score-goal-only sentence containing the active review word
  - expected AI evaluation result and deterministic XP/review outcome are explicit
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-272.

### T-275 — Add learner sentence corpus case for indirect route-confirmation requests

- **State:** done
- **Priority:** P2
- **Goal:** Clarify how learner requests such as "am I on the right path" route when the answer should use deterministic status or room narration without moving automatically.
- **Acceptance criteria:**
  - corpus includes at least one indirect route-confirmation sentence
  - expected AI fallback route and deterministic no-mutation outcome are explicit
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-273.

### T-276 — Add review answer corpus case for exam-context-only target use

- **State:** done
- **Priority:** P2
- **Goal:** Protect review feedback when a learner places the active word only in an exam context but does not show its Biology meaning, role, property, or consequence.
- **Acceptance criteria:**
  - review corpus includes at least one exam-context-only sentence containing the active review word
  - expected AI evaluation result and deterministic XP/review outcome are explicit
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-275.

### T-277 — Add review answer corpus case for passage-prediction-only target use

- **State:** done
- **Priority:** P2
- **Goal:** Protect review feedback when a learner predicts the active word may appear in TOEFL passages but does not show its Biology meaning, role, property, or consequence.
- **Acceptance criteria:**
  - review corpus includes at least one passage-prediction-only sentence containing the active review word
  - expected AI evaluation result and deterministic XP/review outcome are explicit
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-276.

### T-278 — Add learner sentence corpus case for indirect next-word requests

- **State:** done
- **Priority:** P2
- **Goal:** Clarify how learner requests such as "which vocabulary word should I use next" route when the answer should use deterministic help, status, or room narration without granting practice credit.
- **Acceptance criteria:**
  - corpus includes at least one indirect next-word sentence
  - expected AI fallback route and deterministic no-mutation outcome are explicit
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-277.

### T-279 — Add review answer corpus case for reading-skill-only target use

- **State:** done
- **Priority:** P2
- **Goal:** Protect review feedback when a learner says the active word improves reading skill but does not show its Biology meaning, role, property, or consequence.
- **Acceptance criteria:**
  - review corpus includes at least one reading-skill-only sentence containing the active review word
  - expected AI evaluation result and deterministic XP/review outcome are explicit
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-278.

### T-280 — Add review answer corpus case for dictionary-skill-only target use

- **State:** done
- **Priority:** P2
- **Goal:** Protect review feedback when a learner says the active word helps dictionary lookup or vocabulary study but does not show its Biology meaning, role, property, or consequence.
- **Acceptance criteria:**
  - review corpus includes at least one dictionary-skill-only sentence containing the active review word
  - expected AI evaluation result and deterministic XP/review outcome are explicit
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-279.

### T-281 — Add learner sentence corpus case for indirect review-readiness requests

- **State:** done
- **Priority:** P2
- **Goal:** Clarify how learner questions such as "Am I ready for a review?" route when the response should use deterministic status, help, or review availability without mutating mastery state.
- **Acceptance criteria:**
  - learner sentence corpus includes at least one indirect review-readiness sentence
  - expected AI fallback route and deterministic no-mutation outcome are explicit
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-280.

### T-282 — Add review answer corpus case for note-taking-only target use

- **State:** done
- **Priority:** P2
- **Goal:** Protect review feedback when a learner says the active word appears in notes or study materials but does not show its Biology meaning, role, property, or consequence.
- **Acceptance criteria:**
  - review corpus includes at least one note-taking-only sentence containing the active review word
  - expected AI evaluation result and deterministic XP/review outcome are explicit
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-281.

### T-283 — Add review answer corpus case for study-list-only target use

- **State:** done
- **Priority:** P2
- **Goal:** Protect review feedback when a learner says the active word belongs on a study list but does not show its Biology meaning, role, property, or consequence.
- **Acceptance criteria:**
  - review corpus includes at least one study-list-only sentence containing the active review word
  - expected AI evaluation result and deterministic XP/review outcome are explicit
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-282.

### T-284 — Add review answer corpus case for flashcard-deck-only target use

- **State:** done
- **Priority:** P2
- **Goal:** Protect review feedback when a learner says the active word belongs in a flashcard deck but does not show its Biology meaning, role, property, or consequence.
- **Acceptance criteria:**
  - review corpus includes at least one flashcard-deck-only sentence containing the active review word
  - expected AI evaluation result and deterministic XP/review outcome are explicit
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-283.

### T-285 — Add review answer corpus case for quiz-prep-only target use

- **State:** done
- **Priority:** P2
- **Goal:** Protect review feedback when a learner says the active word helps quiz preparation but does not show its Biology meaning, role, property, or consequence.
- **Acceptance criteria:**
  - review corpus includes at least one quiz-prep-only sentence containing the active review word
  - expected AI evaluation result and deterministic XP/review outcome are explicit
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-284.

### T-286 — Add review answer corpus case for practice-schedule-only target use

- **State:** ready
- **Priority:** P2
- **Goal:** Protect review feedback when a learner says the active word belongs in a practice schedule but does not show its Biology meaning, role, property, or consequence.
- **Acceptance criteria:**
  - review corpus includes at least one practice-schedule-only sentence containing the active review word
  - expected AI evaluation result and deterministic XP/review outcome are explicit
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-285.

### T-287 — Add review answer corpus case for word-bank-only target use

- **State:** planned
- **Priority:** P2
- **Goal:** Protect review feedback when a learner says the active word belongs in a TOEFL word bank but does not show its Biology meaning, role, property, or consequence.
- **Acceptance criteria:**
  - review corpus includes at least one word-bank-only sentence containing the active review word
  - expected AI evaluation result and deterministic XP/review outcome are explicit
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-286.

### T-288 — Add review answer corpus case for glossary-only target use

- **State:** planned
- **Priority:** P2
- **Goal:** Protect review feedback when a learner says the active word belongs in a glossary but does not show its Biology meaning, role, property, or consequence.
- **Acceptance criteria:**
  - review corpus includes at least one glossary-only sentence containing the active review word
  - expected AI evaluation result and deterministic XP/review outcome are explicit
  - no live Codex CLI is required
- **Verification:** learner sentence corpus tests and full suite.
- **Dependencies:** T-287.

### T-274 — Add deterministic item inspection descriptions

- **State:** done
- **Priority:** P2
- **Goal:** Let world packs provide deterministic inspection facts for known item IDs so AI narration can rely on code-owned item details.
- **Acceptance criteria:**
  - world schema accepts non-empty item descriptions keyed by existing item IDs
  - schema validation rejects descriptions for missing item IDs and blank descriptions
  - inspecting a described visible item uses the deterministic description
  - Biology world data includes a vaccine vial description about visible liquid contents
- **Verification:** world schema tests, Biology world characterization tests, rules tests, and full suite.
- **Dependencies:** none.

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

- 2026-06-23: Completed T-285 by adding a review-answer corpus regression for `Fungus helps my TOEFL quiz preparation.`, which reaches AI review evaluation, remains rejected, keeps review active, and awards no XP.
- 2026-06-23: Completed T-284 by adding a review-answer corpus regression for `Fungus belongs in my TOEFL flashcard deck.`, which reaches AI review evaluation, remains rejected, keeps review active, and awards no XP.
- 2026-06-23: Completed T-283 by adding a review-answer corpus regression for `Fungus is a study-list entry for TOEFL.`, which reaches AI review evaluation, remains rejected, keeps review active, and awards no XP.
- 2026-06-23: Completed T-282 by adding a review-answer corpus regression for `I wrote fungus in my biology notes.`, which reaches AI review evaluation, remains rejected, keeps review active, and awards no XP.
- 2026-06-23: Completed T-281 by adding a learner-sentence corpus regression for `Am I ready for a review?`, routed through AI interpretation to deterministic review availability with no mastery mutation.
- 2026-06-23: Completed T-280 by adding a review-answer corpus regression for `I can find fungus quickly in a TOEFL dictionary.`, which reaches AI review evaluation, remains rejected, keeps review active, and awards no XP.
- 2026-06-23: Completed T-279 by adding a review-answer corpus regression for `Fungus can improve my TOEFL reading skill.`, which reaches AI review evaluation, remains rejected, keeps review active, and awards no XP.
- 2026-06-23: Completed T-278 by adding a learner-sentence corpus regression for `Which vocabulary word comes next?`, routed through AI interpretation to deterministic help with no practice credit or state mutation.
- 2026-06-23: Completed T-277 by adding a review-answer corpus regression for `Fungus may appear in future TOEFL biology passages.`, which reaches AI review evaluation, remains rejected, keeps review active, and awards no XP.
- 2026-06-23: Completed T-275 by adding a learner-sentence corpus regression for `Am I on the right path?`, routed through AI interpretation to deterministic status with quest grounding and no movement.

Keep at most ten items here.
