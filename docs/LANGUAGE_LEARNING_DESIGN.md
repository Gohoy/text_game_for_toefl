# Language Learning Design

## Purpose

This document defines the learning loop for TOEFL vocabulary. The goal is not merely to display target words, but to make the player encounter, understand, use, revisit, and retain them through AI-agent-supported gameplay.

AI feedback is required for the intended game experience. Narrative wording and language coaching may vary, but mastery updates must remain deterministic and testable.

## Learning Loop

```text
encounter in context
→ attempt in a full sentence
→ receive concise correction or confirmation
→ cause an in-world consequence
→ reuse in a different context
→ complete a delayed review
→ reach mastery
```

A vocabulary word should not become mastered from passive exposure or repeated copy-paste alone.

## Per-Word Record

A minimal persisted record should support:

```text
word
status
mastery_points
encounter_count
correct_use_count
incorrect_use_count
review_stage
last_practiced_at
next_review_at
distinct_context_ids
recent_response_fingerprints
```

Implemented persistence status: saves now include a versioned `mastery` block with these fields for each persisted word, and legacy saves without the block load safe default records from the previous practiced-word set. Deterministic learning events are still the next implementation step.

Recommended derived statuses:

```text
new
encountered
learning
review_due
mastered
```

The status should be derived from deterministic fields where practical rather than independently mutated in several places.

## Learning Events

Use explicit events rather than updating mastery ad hoc:

| Event | Meaning | Suggested effect |
| --- | --- | --- |
| `word_encountered` | Word appears meaningfully in the current room, item, NPC, or quest | Record exposure; no mastery XP |
| `usage_incorrect` | Player attempts the word but grammar or meaning is not acceptable | Record attempt; give feedback; no positive mastery point |
| `usage_correct` | Correct contextual full-sentence use | Award a bounded mastery gain |
| `quest_usage_correct` | Correct use directly enables a quest action | Award a bounded mastery gain and normal quest consequence |
| `review_correct` | Correct use after the word becomes due | Advance review stage |
| `review_incorrect` | Incorrect due review | Reduce or hold stage and schedule a near retry |

The AI evaluator should explain language and propose feedback, but deterministic code decides which learning event occurred and what it changes.

## MVP Mastery Rule

A practical first implementation:

- first meaningful encounter: mark `encountered`
- first correct use in a context: `mastery_points +1`
- correct quest-required use: `mastery_points +1`
- correct delayed review: `mastery_points +1` and advance `review_stage`
- incorrect use: no positive point; schedule or retain a near retry
- repeated identical response in the same context: no additional reward
- mastery requires:
  - at least four mastery points
  - at least two distinct context IDs
  - at least one correct delayed review

Exact thresholds may change only with tests and a documented decision.

## Context IDs

Reward decisions need stable context IDs, for example:

```text
room:river_bank
quest:biology_investigation:analyze_sample
combat:invasive_vine
review:biology:session_2026_06_22
```

Decorative prose is not a context ID.

## Anti-Farming

The same normalized sentence, word, and context must not award repeated XP or mastery within a short period.

Use a deterministic response fingerprint derived from:

```text
normalized sentence + target word + context ID
```

Recognition and feedback may still occur; only the reward is suppressed.

A new reward becomes possible when at least one of these changes meaningfully:

- context ID
- requested communicative purpose
- delayed review stage
- sentence semantics as judged by deterministic rules or a validated evaluator result

Do not use an unvalidated AI judgment as the sole authority for reward. AI feedback is required for coaching quality, but reward authority stays in validated code paths.

## Review Scheduling

Review scheduling must be testable without sleeping.

Inject a clock or pass the current time into the scheduling function.

Suggested initial intervals after correct reviews:

```text
stage 0 → later in the current session
stage 1 → 1 day
stage 2 → 3 days
stage 3 → 7 days
stage 4 → 14 days
```

An incorrect review should schedule a near retry and may reduce the stage by one, but should not erase encounter history.

The first implementation may use game turns for same-session review and UTC timestamps for later review.

## Feedback Contract

Feedback should normally contain:

1. what action or meaning was understood
2. a concise corrected or more natural sentence
3. the gameplay result
4. words practiced and whether a reward was earned

Example:

```text
Action understood: collect a sample from the river.
Better English: I want to collect a sample from the polluted river.
Result: You fill a glass tube with cloudy water.
Words practiced: sample, polluted
Mastery: polluted +1
```

Do not overwhelm the player with a full grammar lesson during ordinary play. Offer deeper explanation through an explicit help or review action.

## Testing Requirements

Tests should cover:

- encounter without reward
- correct use with reward
- incorrect use without reward
- duplicate response reward suppression
- a new context becoming rewardable
- review due ordering
- correct review stage advancement
- incorrect review retry scheduling
- save/load round trip
- clock injection
