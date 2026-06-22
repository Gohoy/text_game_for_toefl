# AI Agent Contract

## Purpose

AI is a required runtime collaborator for the target TOEFL RPG. The agent provides live narration, sentence feedback, vocabulary explanation, NPC dialogue, and structured content drafts.

Deterministic code remains authoritative for state changes: HP, XP, combat, inventory, quest completion, mastery, save/load, and validation.

## Runtime Requirement

Player-facing gameplay must have a configured AI provider. If no provider is configured, runtime paths should fail with a clear `AIProviderUnavailable` error rather than silently degrading to permanent deterministic-only feedback.

Tests may use fake providers. Fake providers are part of the contract because they let the deterministic rule engine and validation behavior be tested without network access or paid API calls.

## Current Interface

The initial interface lives in `src/toefl_rpg/ai/contract.py`.

It defines:

- `TurnFeedbackRequest` and `TurnFeedback` for live turn narration and sentence coaching
- `PlayerSentenceInterpretationRequest` and `PlayerSentenceInterpretation` for proposed interpretations of open-ended player sentences
- `NPCDialogueRequest` and `NPCDialogue` for adaptive NPC responses
- `RoomNarrationRequest` and `RoomNarration` for adaptive room look narration
- `VocabularyExplanationRequest` and `VocabularyExplanation` for word-level learning help
- `ContentDraftRequest` and `StructuredContentDraft` for generated world or quest drafts
- `AIProvider` protocol for concrete providers
- `FakeAIProvider` for tests
- `require_ai_provider` for explicit missing-provider checks

Player sentence interpretation is advisory. The response is limited to a known deterministic action plus a proposed target and confidence score. AI cannot return HP, XP, inventory, quest, mastery, save, or map mutations through this model, and extra response fields are rejected before engine use.

NPC dialogue is also display-only. The request includes the NPC, room, quest progress, visible entities, and target words. The response may include a speaker line and vocabulary notes, but it cannot return deterministic state changes.

Room narration is display-only. The request includes the deterministic room description, exits, visible entities, quest progress, and target words. The response may enrich the prose and add vocabulary notes, but it cannot alter exits, items, NPCs, enemies, quest state, or rewards.

## Validation Rule

AI output must be parsed into typed models before use. Invalid or incomplete AI output must not mutate game state.

## Codex CLI Provider

The first concrete provider lives in `src/toefl_rpg/ai/codex_cli.py`.

It invokes:

```text
codex exec --sandbox read-only --ask-for-approval never --skip-git-repo-check --output-schema <schema> --output-last-message <output> -
```

The provider writes the relevant Pydantic JSON schema to a temporary file, sends the request as stdin, reads the final structured response, and validates it before returning a typed model.

Timeouts, missing executables, non-zero exit codes, empty output, and invalid structured output are surfaced as explicit provider errors.
