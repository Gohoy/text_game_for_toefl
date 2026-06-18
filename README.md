# TOEFL Text RPG

A CLI text RPG for learning TOEFL vocabulary through themed worlds, free-form English actions, quests, deterministic combat, and spaced review.

The project is designed around a strict boundary:

- AI helps generate structured content, language feedback, and narrative.
- Code controls game rules, state, validation, combat, progress, and saves.

See [docs/OVERVIEW_STRUCTURE_PLAN.md](docs/OVERVIEW_STRUCTURE_PLAN.md) for the full structure plan.

## Run

```bash
PYTHONPATH=src python3 -m toefl_rpg
```

Current supported actions include:

- `look`
- `go east`
- `I want to go to the east`
- `I want to inspect the microscope`
- `talk to Dr. Lin`
- `quit`
