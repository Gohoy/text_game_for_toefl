# TOEFL RPG Playtest Debug Protocol

## Purpose

This protocol records recurring player-facing failures, their deterministic
owner, the AI boundary involved, and the regression evidence that protects the
fix. It adapts the copied OpenGame Debug Skill idea into this Python terminal
RPG without importing OpenGame, Node tooling, browser scaffolds, asset pipelines,
or new API-key requirements.

Use this document when a playtest, smoke run, or automated test exposes a bug
that is likely to recur across CLI input, AI feedback, world content, saves, or
rendering.

## Entry Format

Each entry should stay short and include:

| Field | Meaning |
| --- | --- |
| ID | Stable protocol entry ID. |
| Failure signature | The visible symptom, error text, or repeated behavior. |
| Observed player symptom | What the player sees or can do incorrectly. |
| Deterministic owner | The code or content layer that must own the fix. |
| AI boundary | What AI may suggest, and what it must not decide. |
| Verified fix | The implemented correction or guard. |
| Regression coverage | Tests or smoke commands that prove the behavior stays fixed. |
| Proactive check | What future agents should check before changing nearby behavior. |

## Seed Entries

### DBG-001 - Vial Liquid Inspection Fact

| Field | Value |
| --- | --- |
| Failure signature | A player asks whether the vaccine vial contains liquid, but deterministic output lacks a clear physical fact. |
| Observed player symptom | The player cannot tell whether shaking or inspecting the vial reveals liquid. AI narration may have no authoritative fact to ground its response. |
| Deterministic owner | World-pack item descriptions and the engine's inspect behavior. |
| AI boundary | AI may narrate around the item, but code owns the item existence and physical inspection fact. |
| Verified fix | The Biology world pack includes a deterministic vaccine-vial description: clear liquid moves inside the sealed vial. Inspecting or AI-interpreting a vial shake uses that fact. |
| Regression coverage | `tests/test_rules.py::test_inspecting_vaccine_vial_reports_liquid_contents`, `tests/test_rules.py::test_ai_interpreted_vial_shake_reports_liquid_contents`, and `tests/test_biology_world_characterization.py::test_biology_world_has_expected_rooms_and_content`. |
| Proactive check | Important physical item facts should live in validated world content before AI narration depends on them. |

### DBG-002 - Parser-Miss State Preservation

| Field | Value |
| --- | --- |
| Failure signature | Open-ended input misses deterministic parsing, then malformed or failed AI interpretation risks mutating room, inventory, XP, quest, or mastery state. |
| Observed player symptom | A failed parser-miss turn could appear to partially apply an action or lose player progress. |
| Deterministic owner | `GameEngine` parser-miss handling, action validation, and state rollback. |
| AI boundary | AI may propose an action and target for unknown sentences, but deterministic code validates the action and applies any state change. |
| Verified fix | Parser-miss AI provider failures and malformed responses raise clear provider errors while preserving state. Unauthorized state-like request and response fields are rejected. |
| Regression coverage | `tests/test_rules.py` parser-miss provider/state-preservation cases, `tests/test_ai_contract.py` strict request/response model coverage, and learner sentence corpus malformed/unknown cases in `tests/test_learner_sentence_corpus.py`. |
| Proactive check | Before adding parser fallback behavior, assert failed, low-confidence, malformed, and unauthorized AI interpretations leave state unchanged. |

### DBG-003 - Review-Answer False Positives

| Field | Value |
| --- | --- |
| Failure signature | A review answer contains the active word but only refers to study materials, games, lists, feelings, confidence, or test strategy rather than Biology meaning. |
| Observed player symptom | The player could receive review credit without using the target word meaningfully. |
| Deterministic owner | Review minimum checks, duplicate-answer checks, XP/review-stage updates, and persisted mastery records. |
| AI boundary | AI evaluates whether the sentence uses the target meaningfully and can suggest a better sentence, but deterministic code decides retry state, XP, review stage, and saves. |
| Verified fix | Rejected review answers keep the active word available, award no XP, and separate AI advice from deterministic retry text. The corpus includes many false-positive patterns. |
| Regression coverage | `tests/fixtures/review_answer_regression.json` plus `tests/test_learner_sentence_corpus.py`, including study-list, flashcard, quiz-prep, game, app, platform, and other target-use-only cases. |
| Proactive check | New review-answer patterns should declare whether they reach AI evaluation or deterministic precheck, then assert XP, review stage, and active review word explicitly. |

### DBG-004 - Codex Structured-Output Schema Failure

| Field | Value |
| --- | --- |
| Failure signature | Codex CLI rejects a structured-output schema because object schemas are not strict, for example missing `additionalProperties: false`. |
| Observed player symptom | Live AI feedback fails before narration or sentence feedback appears. |
| Deterministic owner | Pydantic model configuration and Codex CLI provider schema construction. |
| AI boundary | AI must return JSON matching the typed schema; code validates before display or state use. |
| Verified fix | Player-facing AI response and request schemas are strict. The Codex CLI provider writes schemas with `additionalProperties: false` and complete required fields. |
| Regression coverage | `tests/test_ai_contract.py::test_player_facing_response_schemas_are_strict_for_codex`, `tests/test_ai_contract.py::test_ai_request_schemas_are_strict_and_audited`, and strict-schema tests in `tests/test_codex_cli_provider.py`. |
| Proactive check | Any new AI request or response model must reject extra fields and should have schema strictness coverage before live Codex use. |

### DBG-005 - Save-Path Churn During Smoke Runs

| Field | Value |
| --- | --- |
| Failure signature | A smoke run or manual playtest accidentally reads from or writes to the normal player save slot instead of an isolated temporary save file. |
| Observed player symptom | The player may see stale progress during a smoke run, or automation may overwrite the normal save slot. |
| Deterministic owner | Application startup save-path selection and storage read/write helpers. |
| AI boundary | AI has no authority over save paths, save slots, or persisted game state. |
| Verified fix | `TOEFL_RPG_SAVE_PATH` lets smoke runs and manual live checks use a temporary save path while normal play defaults to `data/saves/slot1.json`. |
| Regression coverage | `tests/test_app.py::test_save_path_from_env_defaults_to_normal_slot`, `tests/test_app.py::test_save_path_from_env_uses_configured_path`, the fake-provider smoke command in `docs/QUALITY_GATES.md`, and the live Codex smoke command in `README.md`. |
| Proactive check | Any new smoke command or automated playtest should set `TOEFL_RPG_SAVE_PATH` to a temporary path unless it is explicitly testing the normal player save slot. |

## Maintenance Rules

- Add entries only for failures observed in playtests, smoke runs, tests, or user reports.
- Prefer one entry per root cause, not one entry per wording variation.
- Every entry needs regression evidence or a clear follow-up task to add it.
- Do not add OpenGame runtime code, Node tooling, browser-game scaffolds, asset pipelines, or API-key requirements.
- Keep this protocol factual and compact; detailed history belongs in Git.
