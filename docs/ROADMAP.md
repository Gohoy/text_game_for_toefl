# Roadmap

## Current State

- Repository initialized with planning documentation and a minimal playable Python scaffold.
- Vocabulary source identified at `/Users/gaohongyu1/Downloads/TOEFLiBT  词以类记2.0.txt`.
- The game can currently render a small Biology Realm, move between rooms, inspect target words, award XP, and provide basic English feedback.

## Next Milestones

1. Create Python package scaffold and CLI entry point.
2. Add deterministic engine state, movement, and save/load.
3. Add Rich renderer for room panels, mini-map, vocabulary status, and feedback.
4. Add first Biology Realm world pack with five rooms and ten target words.
5. Add command and sentence parser for typed English actions.
6. Add deterministic combat and quest progression.
7. Add vocabulary importer for the TOEFL source file.
8. Add language feedback and mastery tracking.
9. Add focused tests for rules, importer, schema validation, and quest progress.

## Progress Notes

- 2026-06-18: Created project overview, repository instructions, README, and roadmap.
- 2026-06-18: Removed the local LaunchAgent/script continuation path in favor of Codex app automation for visible run details.
- 2026-06-18: Added the first playable Python/Rich scaffold with Biology Realm rooms, sentence parsing, movement, inspection, XP, and smoke-tested CLI output.
- 2026-06-18: Copied the full TOEFL vocabulary source into `data/raw/`, expanded the Biology demo to five rooms, and added inventory, collect, use, help, and status actions.
- 2026-06-18: Added deterministic Biology Investigation quest progress with objectives, quest XP, status/UI display, and tests.
- 2026-06-18: Removed the tracked raw vocabulary copy; future import work should read `/Users/gaohongyu1/Downloads/TOEFLiBT  词以类记2.0.txt` directly or generate small validated derived content.
