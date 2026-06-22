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
- `VocabularyExplanationRequest` and `VocabularyExplanation` for word-level learning help
- `ContentDraftRequest` and `StructuredContentDraft` for generated world or quest drafts
- `AIProvider` protocol for concrete providers
- `FakeAIProvider` for tests
- `require_ai_provider` for explicit missing-provider checks

## Validation Rule

AI output must be parsed into typed models before use. Invalid or incomplete AI output must not mutate game state.

The next implementation task should add a Codex CLI provider that conforms to this interface and returns validated structured responses.
