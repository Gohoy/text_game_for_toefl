# Automated Development Runbook

## Purpose

This runbook defines how a scheduled coding agent should advance the project in one small, reviewable cycle. It is optimized for a task that is triggered approximately every 20 minutes.

The interval is not permission to start large work. Each invocation should finish or safely stop after one coherent increment.

## Scheduler Requirement: Prevent Overlap

The scheduler should not start a second run while a previous run is active.

If the scheduler does not provide single-flight execution, wrap the invocation with an operating-system lock. On macOS, a simple lock-directory wrapper is sufficient:

```bash
#!/usr/bin/env bash
set -euo pipefail

LOCK_DIR="/tmp/text_game_for_toefl_codex.lock"

if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  echo "Another Codex cycle is active; skipping this trigger."
  exit 0
fi

cleanup() {
  rmdir "$LOCK_DIR" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

# Invoke the configured Codex automation here.
```

If stale-lock handling is needed, add it in the scheduler wrapper rather than in application code.

## Files Read on Every Run

Read in this order:

1. `AGENTS.md`
2. `docs/ROADMAP.md`
3. `docs/QUALITY_GATES.md`
4. this runbook
5. task-relevant implementation and tests

Read the overview and specialist design documents only when relevant to the selected task.

## Cycle Algorithm

### 1. Preflight

Run:

```bash
git status --short --branch
git log -5 --oneline
```

Then:

- identify uncommitted changes
- identify unpushed local commits
- preserve all user work
- attempt to push previously verified local commits when appropriate
- do not begin unrelated work on top of unexplained changes

### 2. Handle a Dirty Worktree

Never reset, restore, clean, or overwrite the worktree.

Use this decision order:

1. If the changes clearly belong to the roadmap task marked `in_progress`, continue that task.
2. If the changes are verified and coherent but uncommitted, finish documentation and commit them.
3. If the changes are unrelated user work, avoid those files and select a non-overlapping task.
4. If no safe non-overlapping task exists, add a precise blocked note to `docs/ROADMAP.md` only when that edit itself is safe; otherwise exit without changing files.

### 3. Select One Task

Use this priority:

1. Continue the sole `in_progress` task.
2. Otherwise choose the first `ready` task with the highest priority.
3. Respect dependencies.
4. Prefer tasks that restore a broken build or protect data.
5. Prefer behavior-preserving tests before refactors.
6. Do not start a second task after the first one is complete.

If the selected task cannot be completed in one cycle:

- split it into independently verifiable tasks
- keep the original as an umbrella item if useful
- mark only the first slice `ready`
- implement at most that first slice

If a task fails to advance in two consecutive attempts, mark it `blocked` with:

- the exact blocker
- evidence already gathered
- the minimum unblock condition
- a suggested next investigation

Then promote the next safe task.

### 4. Establish the Baseline

Before editing:

- inspect the target implementation
- inspect directly related tests
- run the narrowest useful test
- determine whether any failure is pre-existing

For a refactor, add a characterization test first.
For a bug fix, add a failing regression test first when practical.
For a new feature, test the public behavior or deterministic rule rather than private implementation details.

### 5. Implement a Vertical Slice

A good slice contains all required layers for one observable outcome:

```text
data/schema → rule → state change → renderer/CLI → test → documentation
```

Not every task touches every layer. Avoid leaving a new public option, field, or command disconnected from its deterministic behavior.

Use stable IDs for world content and save references. Keep narrative content separate from rule evaluation.

### 6. Verify

Run focused tests first. Then run all mandatory gates in `docs/QUALITY_GATES.md`.

Do not weaken, skip, or delete tests merely to obtain a green run.

If the baseline was already red:

- do not introduce additional failures
- fix the baseline only when it is small, understood, and higher priority than the selected task
- otherwise mark the task blocked or select a non-overlapping task

### 7. Update Documentation

Every successful or blocked run updates `docs/ROADMAP.md`.

Additional updates are event-driven:

- update `README.md` for user-visible commands, setup, or gameplay
- update `docs/WORLD_SCHEMA.md` for content-contract changes
- update `docs/LANGUAGE_LEARNING_DESIGN.md` for mastery or review-rule changes
- update `docs/QUALITY_GATES.md` when verification commands change
- append to `docs/DECISIONS.md` only for durable architectural decisions
- update the overview only for product or architecture direction, not routine progress

Do not append a long diary entry. Keep only current status, evidence, and the next executable task.

### 8. Commit and Push

Commit only after applicable quality gates pass.

Commit message format:

```text
<type>(<scope>): <outcome> [<task-id>]
```

Examples:

```text
test(content): lock current biology world behavior [T-110]
feat(content): validate room exit references [T-115]
feat(review): schedule due vocabulary deterministically [T-123]
```

Then attempt to push. A push failure must not cause destructive history changes.

### 9. Final Run Report

The agent response for each invocation should report:

```text
Task: T-xxx — title
Outcome: completed | in progress | blocked | no safe change
Changed: important files
Verification: exact commands and results
Commit: hash or "not committed"
Push: success, skipped, or failed
Next: next ready task
```

Do not claim a test or push succeeded without evidence.

## Queue Maintenance

`docs/ROADMAP.md` should normally contain at least three small ready or planned tasks.

When fewer than three executable tasks remain:

1. Do not invent a new product direction.
2. Read the current phase exit criteria.
3. Decompose the next unmet criterion into three to five small tasks.
4. Add acceptance criteria and verification commands.
5. Commit the planning update as a docs-only task.
6. Stop; implementation begins on the next run.

Do not advance to a new phase until all current phase exit criteria are met or explicitly revised in `docs/DECISIONS.md`.

## Scheduled Prompt

The exact prompt stored in `.codex/20_minute_prompt.md` should be used by the scheduler. Keep the prompt short; the repository documents contain the operating detail.
