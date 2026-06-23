# OpenGame Skill Review

## Source

This directory vendors two OpenGame skill documents for reference:

- `template_skill.md` copied from `leigest519/OpenGame` `agent-test/template-skill/README.md`
- `debug_skill.md` copied from `leigest519/OpenGame` `agent-test/debug-skill/README.md`
- `OPENGAME_LICENSE` copied from the same repository

Copied source commit: `c54307efe1dab927e7fc52dbb92af6b3df1d1c66`.

These files are reference material only. They are not active Codex skills, Python modules, or runtime dependencies for this project.

## Review Findings

### P1: Do not import OpenGame as a runtime dependency

OpenGame is a Node/TypeScript browser-game generation framework centered on Phaser/Vite projects, browser execution, and asset-generation providers. This project is a Python terminal RPG with Rich, Pydantic, pytest, JSON world packs, and a local AI-agent bridge. Pulling OpenGame into runtime would conflict with the terminal-first product invariant and add Node/tooling/API-key requirements that the current roadmap explicitly avoids.

Recommended action: keep OpenGame material in documentation only unless a future task intentionally builds a separate web prototype.

### P1: Adapt the Debug Skill concept into a TOEFL RPG playtest protocol

The Debug Skill's strongest fit is its persistent record of failure signatures, root causes, verified fixes, and proactive checks. This project already produces recurring evidence through automation, fake-provider CLI smoke tests, learner-sentence corpora, review-answer corpora, schema validation, and player-role playtests.

Recommended action: create a local `docs/PLAYTEST_DEBUG_PROTOCOL.md` with TOEFL-specific entries such as parser misses, AI narration omitting deterministic facts, review-answer false positives, save-path churn, schema-reference failures, and renderer output ambiguity. Keep entries small and backed by tests or smoke evidence.

### P2: Adapt the Template Skill concept for content, not code scaffolding

OpenGame's Template Skill evolves browser-game templates by extracting reusable structure from completed games. The equivalent value here is not Phaser scaffolding; it is reusable world-pack, quest, NPC-dialogue, vocabulary-review, and corpus-case patterns.

Recommended action: treat successful Biology patterns as templates for future worlds only after the Biology learning loop is stable. A good local template should include world-pack sections, target-word placement rules, quest-step shapes, review-answer traps, and required validation checks.

### P2: Avoid self-evolving templates until the manual content contract is stronger

OpenGame's template evolution expects many generated browser games and a classifier/abstractor/merger pipeline. This repo has one canonical world and a strict "one subject deeply before expansion" direction. Automated template evolution would be premature and likely add complexity before the learning-loop quality is proven.

Recommended action: defer any generated template library until after Phase 2 language-feedback reliability and at least one additional handcrafted world slice.

### P3: Keep OpenGame attribution and copied-doc isolation

The copied documents include original OpenGame context and relative links that do not match this repository. They should remain isolated under `docs/opengame_skills/` with explicit source and license notes, rather than being merged into `AGENTS.md` or active automation instructions.

Recommended action: if these docs are edited later, preserve the source commit and Apache-2.0 license reference.

## Useful Adaptation

The lowest-risk next task is documentation-only:

```text
T-new — Add TOEFL RPG playtest debug protocol

Goal: Convert the OpenGame Debug Skill idea into a local protocol for recurring CLI playtest failures.
Acceptance:
- protocol stores failure signature, observed player symptom, deterministic owner, AI boundary, verified fix, and regression coverage
- includes seed entries for the vial-liquid bug, parser-miss state preservation, review-answer false positives, and AI response schema failures
- no OpenGame runtime dependency or Node tooling is introduced
Verification:
- documentation consistency check
- existing full test suite remains green if touched by the task
```

Do not implement this by copying OpenGame's TypeScript debug-loop code. The current repository already has the right execution tools; it needs a concise domain-specific memory of verified playtest failures.
