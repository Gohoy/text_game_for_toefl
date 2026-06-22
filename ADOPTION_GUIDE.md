# Adoption Guide

## What This Bundle Contains

This bundle proposes a document system for safe, high-frequency Codex development:

```text
AGENTS.md
CLAUDE.md
.codex/20_minute_prompt.md
docs/AUTOMATION_RUNBOOK.md
docs/QUALITY_GATES.md
docs/ROADMAP.md
docs/DECISIONS.md
docs/LANGUAGE_LEARNING_DESIGN.md
docs/WORLD_SCHEMA.md
docs/DOCUMENTATION_AND_DEVELOPMENT_ADDENDUM.md
```

## Safe Adoption Order

1. Create a branch or commit the current repository state.
2. Compare the proposed `AGENTS.md` with the current one; preserve any repository-specific facts not present here.
3. Replace duplicate `CLAUDE.md` content with the pointer version.
4. Add the new runbook, quality-gate, decision, learning-design, and world-schema files.
5. Merge the proposed roadmap structure with actual current code/test status. Do not mark a capability complete solely because this template says so.
6. Put `.codex/20_minute_prompt.md` into the scheduled task configuration.
7. Ensure the scheduler cannot overlap runs.
8. Run one supervised cycle before relying on unattended execution.

## Important Validation Before Use

The proposed roadmap is based on the current documentation, not a fresh inspection of the source tree. The first Codex run should verify:

- actual test file names
- actual dependency and package configuration
- whether all listed current capabilities are present and green
- whether scripted CLI input exits cleanly
- whether the current worktree is clean

Adjust `docs/QUALITY_GATES.md` and task readiness to match evidence from the repository.

## Avoid Blind Replacement

Do not overwrite the existing overview or README with a generic template. They already contain useful product and run information. Apply the role separation described in the addendum and update those files only when current code confirms the claims.
