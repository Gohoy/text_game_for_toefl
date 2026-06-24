# Quality Gates

## Principle

Verification should be fast enough for frequent automation but strong enough to keep the repository runnable. Run focused tests during development and the mandatory gates before committing.

The commands below assume execution from the repository root.

## Mandatory Gates for Python Code Changes

```bash
python3 -m compileall -q src
python3 -m pytest -q
```

If the project standardizes commands in `pyproject.toml`, a `Makefile`, or a task runner, update this document and use the canonical commands.

## Required Fake CLI Smoke Gate

Run this when changing application startup, command parsing, rendering, movement, inventory, quests, combat, saves, or language practice:

```bash
printf "I look around the area.\nCould you show me my current status?\nI would like to quit and save my progress.\n" \
  | TOEFL_RPG_AI_PROVIDER=fake TOEFL_RPG_SAVE_PATH=/tmp/toefl-rpg-smoke.json PYTHONPATH=src python3 -m toefl_rpg
```

The process must:

- start successfully
- accept scripted input
- use the explicit fake AI provider instead of making a live Codex call
- use a temporary `TOEFL_RPG_SAVE_PATH` instead of the normal player save slot
- show no traceback
- terminate successfully

Keep a deterministic subprocess smoke test in the test suite once practical; the shell smoke command remains useful for integration verification.

This required smoke gate must stay fake-provider only. Automation should not
require a paid API call, a live Codex session, or the normal player save slot.

## Manual Live Codex Smoke

Run this only when changing Codex CLI provider wiring, structured-output
schemas, timeouts, or player-facing AI runtime behavior:

```bash
printf "I look around the area.\nI would like to quit and save my progress.\n" \
  | TOEFL_RPG_SAVE_PATH=/tmp/toefl-rpg-live-smoke.json PYTHONPATH=src python3 -m toefl_rpg
```

The process should:

- call the configured local Codex CLI provider
- use a temporary `TOEFL_RPG_SAVE_PATH`
- show AI-generated turn feedback or narration
- show no traceback or schema-format error
- terminate successfully

Do not make this command a mandatory automation gate.

## Content and Schema Gate

Run the focused schema tests when changing world packs, loaders, validators, or content IDs:

```bash
python3 -m pytest -q tests/test_world_schema.py
```

Requirements:

- malformed content is rejected with a useful path and message
- IDs are unique within their namespace
- exits and quest references point to existing IDs
- loading repository content does not require network access
- tests use small fixtures, not the full local TOEFL source file

If the test file has a different name, update this document after the canonical test is added.

## Save/Load Gate

When state or save schema changes, verify:

- current saves round-trip
- missing optional fields receive safe defaults
- incompatible versions fail clearly or migrate explicitly
- content objects are referenced by stable IDs
- temporary test saves do not pollute tracked files

Use focused tests such as:

```bash
python3 -m pytest -q tests/test_save*.py
```

## Importer Gate

Importer tests must use repository fixtures:

```bash
python3 -m pytest -q tests/test_vocab_importer.py
```

The test suite must not depend on:

```text
/Users/gaohongyu1/Downloads/TOEFLiBT  词以类记2.0.txt
```

That path is a runtime source available to the project owner, not a portable test dependency.

## Documentation-Only Changes

For documentation-only tasks:

- verify referenced paths exist or are explicitly proposed
- ensure commands match the repository
- ensure current-state claims agree with tests and code
- do not mark implementation tasks complete

No empty code commit is required for documentation work.

## Definition of Green

A run is green when:

- mandatory applicable commands exit with status 0
- no traceback appears in smoke output
- no new failing or skipped critical tests are introduced
- changed behavior has direct test evidence
- documentation reflects the resulting behavior
- `git diff --check` passes

Final check:

```bash
git diff --check
```

## When a Gate Is Too Slow

Do not silently stop running it.

Instead:

1. measure the command
2. split fast unit tests from slower integration tests
3. keep a mandatory fast gate for every run
4. add a scheduled full-suite gate
5. document the change here and in `docs/DECISIONS.md`
