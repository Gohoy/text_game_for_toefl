#!/bin/zsh
set -eu

export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

REPO_DIR="/Users/gaohongyu1/project/text_game_for_toefl"
CODEX_BIN="/opt/homebrew/bin/codex"
AUTOMATION_DIR="$REPO_DIR/.codex-automation"
LOG_DIR="$AUTOMATION_DIR/logs"
LOCK_DIR="$AUTOMATION_DIR/run.lock"
MAX_LOCK_AGE_SECONDS=3600

mkdir -p "$LOG_DIR"

timestamp() {
  date "+%Y-%m-%d %H:%M:%S"
}

log() {
  print "[$(timestamp)] $*"
}

if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  lock_mtime="$(stat -f %m "$LOCK_DIR" 2>/dev/null || echo 0)"
  now="$(date +%s)"
  age="$((now - lock_mtime))"
  if [ "$age" -gt "$MAX_LOCK_AGE_SECONDS" ]; then
    log "Removing stale lock older than ${MAX_LOCK_AGE_SECONDS}s: $LOCK_DIR"
    rm -rf "$LOCK_DIR"
    mkdir "$LOCK_DIR"
  else
    log "Previous Codex run still active; skipping."
    exit 0
  fi
fi

cleanup() {
  rm -rf "$LOCK_DIR"
}
trap cleanup EXIT INT TERM

RUN_LOG="$LOG_DIR/run-$(date +%Y%m%d-%H%M%S).log"
exec >> "$RUN_LOG" 2>&1

log "Starting TOEFL text RPG Codex continuation."
cd "$REPO_DIR"

if [ "${TOEFL_RPG_DRY_RUN:-0}" = "1" ]; then
  log "Dry run enabled. Repository: $REPO_DIR"
  "$CODEX_BIN" --version
  git status --short --branch
  exit 0
fi

git fetch origin main
if git diff --quiet && git diff --cached --quiet; then
  git merge --ff-only origin/main
else
  log "Repository has local changes before Codex run; leaving pull/merge decisions to Codex."
fi

"$CODEX_BIN" exec \
  --cd "$REPO_DIR" \
  --sandbox danger-full-access \
  --ask-for-approval never \
  --model gpt-5.5 \
  - <<'PROMPT'
Continue building the TOEFL CLI text RPG.

Required workflow:
1. Read CLAUDE.md and docs/OVERVIEW_STRUCTURE_PLAN.md.
2. Check git status.
3. Pick the smallest coherent next milestone that moves the game toward a complete playable state.
4. Keep deterministic game logic in code and AI/content generation behind structured validation.
5. Prefer Python, Rich, Pydantic, and pytest as directed by the project docs.
6. Run focused tests or a manual smoke check when relevant.
7. Update docs/ROADMAP.md with a short progress note.
8. If the repository is coherent and verification passes, commit with a clear message and push to origin/main.

Important constraints:
- Preserve user changes.
- Do not use destructive git commands.
- Keep the game runnable after every run.
- Do not add paid image-generation dependencies.
PROMPT

log "Codex continuation finished."
