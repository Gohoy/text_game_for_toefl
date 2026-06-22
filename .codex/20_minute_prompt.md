Continue `text_game_for_toefl` autonomously for exactly one small, coherent increment.

Important product direction: AI is a required core part of this game, not an optional add-on. Build toward a Codex CLI or equivalent local AI-agent runtime for live narration, sentence feedback, vocabulary explanations, and structured content drafting. Deterministic code still owns authoritative state, validation, XP, combat, quest completion, mastery, and saves.

Follow the repository as the source of truth:

1. Read `AGENTS.md`, `docs/ROADMAP.md`, `docs/QUALITY_GATES.md`, and `docs/AUTOMATION_RUNBOOK.md`.
2. Run `git status --short --branch` and preserve all user changes.
3. Continue the sole `in_progress` task, otherwise select the first highest-priority `ready` unblocked task.
4. If it is too large for one run, split it in `docs/ROADMAP.md` and implement only the first independently useful slice.
5. Inspect the existing implementation and tests before editing. Prefer a characterization or regression test first.
6. Make the smallest vertical change that satisfies the task acceptance criteria. Do not do unrelated refactors or start a second task.
7. Run focused tests, then every applicable command in `docs/QUALITY_GATES.md`.
8. Update `docs/ROADMAP.md` on every successful or blocked run, and update other documents only according to the ownership matrix in `AGENTS.md`.
9. Commit coherent verified work with the roadmap task ID, then push when possible. Never use destructive Git commands or force-push.
10. Do not ask broad clarification questions during this scheduled run. If blocked, record the exact blocker and unblock condition, promote the next safe task when appropriate, and stop.

Finish with: task ID, outcome, changed files, verification commands/results, commit, push status, and next ready task. Never claim success without evidence.
