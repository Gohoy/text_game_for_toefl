# Local Continuation Automation

The project is continued by a local macOS LaunchAgent that runs every 30 minutes.

LaunchAgent:

```text
/Users/gaohongyu1/Library/LaunchAgents/com.gohoy.toefl-text-rpg-codex.plist
```

Runner script:

```text
/Users/gaohongyu1/project/text_game_for_toefl/scripts/continue_codex.sh
```

Logs:

```text
/Users/gaohongyu1/project/text_game_for_toefl/.codex-automation/
```

Useful commands:

```bash
launchctl print gui/$(id -u)/com.gohoy.toefl-text-rpg-codex
launchctl kickstart -k gui/$(id -u)/com.gohoy.toefl-text-rpg-codex
launchctl bootout gui/$(id -u) /Users/gaohongyu1/Library/LaunchAgents/com.gohoy.toefl-text-rpg-codex.plist
launchctl bootstrap gui/$(id -u) /Users/gaohongyu1/Library/LaunchAgents/com.gohoy.toefl-text-rpg-codex.plist
```

The script has a lock directory so a new run skips if the previous run is still active.

