# TOEFL Text RPG

A CLI text RPG for learning TOEFL vocabulary through themed worlds, free-form English actions, AI-driven narration and feedback, quests, deterministic combat, and spaced review.

The project is designed around a strict boundary:

- A local AI agent is a required core part of the intended game experience.
- AI generates live narrative, richer sentence feedback, vocabulary explanations, and structured content drafts.
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
inventory before anything changes. The executable defaults to `codex`; override
it with `TOEFL_RPG_CODEX_EXECUTABLE` when needed.

For deterministic smoke tests without a live Codex call, opt into the fake test
provider explicitly:

```bash
printf "look\nstatus\nquit\n" \
  | TOEFL_RPG_AI_PROVIDER=fake PYTHONPATH=src python3 -m toefl_rpg
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
for a new full-sentence answer. Correct review sentences advance the persisted
review stage and schedule the next review.

Use `explain <word>` for an AI-generated explanation of a target word that is
visible in the current room or already practiced. The explanation is displayed
as coaching text only; deterministic state, XP, mastery, quests, and saves do
not change because of the explanation itself.

The deterministic engine still owns movement, inventory, combat, XP, quest
completion, vocabulary rewards, and saves. AI feedback is validated before display;
if the provider fails during a turn, the game state is not advanced.

Progress is autosaved after each handled turn:

```text
data/saves/slot1.json
```

The full TOEFL vocabulary source should stay outside the repo and be read from:

```text
/Users/gaohongyu1/Downloads/TOEFLiBT  词以类记2.0.txt
```
