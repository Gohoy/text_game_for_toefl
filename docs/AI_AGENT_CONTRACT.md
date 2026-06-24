# AI Agent Contract

## Purpose

AI is a required runtime collaborator for the target TOEFL RPG. The agent provides live narration, sentence feedback, review answer evaluation, vocabulary explanation, NPC dialogue, and structured content drafts.

Deterministic code remains authoritative for state changes: HP, XP, combat, inventory, quest completion, mastery, save/load, and validation.

## Runtime Requirement

Player-facing gameplay must have a configured AI provider. If no provider is configured, runtime paths should fail with a clear `AIProviderUnavailable` error rather than silently degrading to permanent deterministic-only feedback.

Tests may use fake providers. Fake providers are part of the contract because they let the deterministic rule engine and validation behavior be tested without network access or paid API calls.

## Current Interface

The initial interface lives in `src/toefl_rpg/ai/contract.py`.

It defines:

- `SentenceQualityRequest` and `SentenceQualityEvaluation` for pre-action checks that require complete, correct English before player-facing CLI actions are accepted
- `TurnFeedbackRequest` and `TurnFeedback` for live turn narration and sentence coaching
- `PlayerSentenceInterpretationRequest` and `PlayerSentenceInterpretation` for proposed interpretations of open-ended player sentences
- `NPCDialogueRequest` and `NPCDialogue` for adaptive NPC responses
- `RoomNarrationRequest` and `RoomNarration` for adaptive room look narration
- `VocabularyExplanationRequest` and `VocabularyExplanation` for word-level learning help
- `ReviewAnswerEvaluationRequest` and `ReviewAnswerEvaluation` for AI-assisted review answer quality checks
- `ContentDraftRequest` and `StructuredContentDraft` for generated world or quest drafts
- `AIProvider` protocol for concrete providers
- `FakeAIProvider` for tests
- `require_ai_provider` for explicit missing-provider checks

Player sentence interpretation is advisory. The response is limited to a known deterministic action plus a proposed target and confidence score. The shared action set is defined by deterministic code in `src/toefl_rpg/engine/actions.py` and reused by parser and AI validation. AI cannot return HP, XP, inventory, quest, mastery, save, or map mutations through this model, and extra response fields are rejected before engine use.

Sentence quality evaluation is a pre-action learning gate in normal CLI play.
It judges whether the player's input is a complete and correct English sentence
before deterministic parsing, AI interpretation fallback, or state mutation can
run. Rejected inputs return a concise reason and a suggested rewrite; they do
not move the player, grant XP, change inventory, advance quests, update mastery,
or save progress.

NPC dialogue is also display-only. The request includes the NPC, room, quest progress, visible entities, and target words. The response may include a speaker line and vocabulary notes, but it cannot return deterministic state changes.

Room narration is display-only. The request includes the deterministic room ID, room description, exits, visible entities, quest progress, and target words. The response must echo the requested room ID, may enrich the prose, and may add vocabulary notes, but it cannot alter exits, items, NPCs, enemies, quest state, or rewards.

Review answer evaluation is advisory but required in normal runtime. The request includes the target word, learner sentence, world theme, and current review stage. The response may say whether the sentence uses the target word meaningfully and may provide a correction, but it cannot advance review state, grant XP, suppress duplicates, mutate saves, or complete quests. Deterministic code still applies the review event and rewards only after the response validates and the sentence passes deterministic minimum checks.

## Validation Rule

AI output must be parsed into typed models before use. Player-facing response
schemas are strict and include `additionalProperties: false` so `codex exec`
can pass them to the OpenAI structured-output response format. Invalid,
incomplete, or extra-field AI output must not mutate game state.

AI-authored world-pack drafts must pass through `validate_world_pack_draft()` or
`draft_world_pack()` in `src/toefl_rpg/ai/drafts.py` before they can be reviewed
as usable content. These helpers reject unsupported draft types and reuse the
`WorldPack` schema so malformed references, duplicate IDs, runtime-state fields,
and missing required fields cannot enter runtime content.

## Codex CLI Provider

The first concrete provider lives in `src/toefl_rpg/ai/codex_cli.py`.

It invokes:

```text
codex exec --sandbox read-only --skip-git-repo-check --output-schema <schema> --output-last-message <output> -
```

The provider writes the relevant Pydantic JSON schema to a temporary file, sends the request as stdin, reads the final structured response, and validates it before returning a typed model.

Timeouts, missing executables, non-zero exit codes, empty output, and invalid structured output are surfaced as explicit provider errors.
