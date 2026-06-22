# TOEFL Text RPG

A CLI text RPG for learning TOEFL vocabulary through themed worlds, free-form English actions, AI-driven narration and feedback, quests, deterministic combat, and spaced review.

The project is designed around a strict boundary:

- A local AI agent is a required core part of the intended game experience.
- AI generates live room narration, NPC dialogue, richer sentence feedback, review answer evaluation, vocabulary explanations, and structured content drafts.
- Code controls game rules, state, validation, combat, progress, and saves.

See [docs/OVERVIEW_STRUCTURE_PLAN.md](docs/OVERVIEW_STRUCTURE_PLAN.md) for the full structure plan.

## Run

```bash
PYTHONPATH=src python3 -m toefl_rpg
```

Normal play uses the local Codex CLI as the required AI provider for turn narration
and sentence feedback. When the deterministic parser cannot understand a
sentence, the AI provider may propose a structured action; the deterministic
engine still validates visible rooms, items, enemies, quest state, XP, and
inventory before anything changes. Review answers are also evaluated through the
AI provider for meaningful target-word use, while deterministic code still
controls review stage, XP, duplicate suppression, and saves. The executable
defaults to `codex`; override it with `TOEFL_RPG_CODEX_EXECUTABLE` when needed.

For deterministic smoke tests without a live Codex call, opt into the fake test
provider explicitly. Use `TOEFL_RPG_SAVE_PATH` to keep smoke runs away from the
normal player save slot:

```bash
printf "look\nstatus\nquit\n" \
  | TOEFL_RPG_AI_PROVIDER=fake TOEFL_RPG_SAVE_PATH=/tmp/toefl-rpg-smoke.json PYTHONPATH=src python3 -m toefl_rpg
```

Current supported actions include:

- `help`
- `look`
- `go east`
- `I want to go to the east`
- `I go north to the fungus grove.`
- `I want to inspect the microscope`
- `I want to collect the fungus sample`
- open-ended equivalents such as `Could you grab the specimen for my research?`
- `I want to use the microscope`
- `I attack the invasive vine`
- `The fungus is vital for the forest.`
- `explain fungus`
- `review`
- `A fungus can be vital for forest metabolism.`
- `talk to Dr. Lin`
- `inventory`
- `status`
- `quit`

The current Biology Investigation quest has three deterministic steps: collect the fungus sample, analyze it with the microscope, and defeat the invasive vine.
After using target words in context, `review` presents due vocabulary and asks
for a new full-sentence answer. In normal play, the AI provider judges whether
the answer uses the target word meaningfully; deterministic code then applies
the review result, advances persisted review stage, and schedules the next
review. Review messages keep AI advice separate from deterministic result lines
such as XP, review stage, and retry state.

Use `explain <word>` for an AI-generated explanation of a target word that is
visible in the current room or already practiced. The explanation is displayed
as coaching text only; deterministic state, XP, mastery, quests, and saves do
not change because of the explanation itself.

Use `look` for AI-generated room narration grounded in the deterministic room
description, exits, visible entities, quest progress, and target words. Use
`talk to Dr. Lin` for AI-generated NPC dialogue grounded in the current room,
quest progress, visible entities, and target words. Narration and dialogue are
coaching text only; deterministic quest state and rewards remain controlled by
code.

The deterministic engine still owns movement, inventory, combat, XP, quest
completion, vocabulary rewards, and saves. AI feedback is validated before display;
if the provider fails during a turn, the game state is not advanced.

Progress is autosaved after each handled turn:

```text
data/saves/slot1.json
```

Set `TOEFL_RPG_SAVE_PATH` to use a different save file for smoke tests or
isolated playthroughs. If it is unset, normal play continues to use the default
slot above.

The full TOEFL vocabulary source should stay outside the repo and be read from:

```text
/Users/gaohongyu1/Downloads/TOEFLiBT  词以类记2.0.txt
```
