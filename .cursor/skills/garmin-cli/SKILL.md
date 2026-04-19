---
name: garmin-cli
description: >-
  Runs and interprets the `pacerai` Garmin Connect CLI (activities, workouts,
  scheduling, stats, sleep, HRV). Use when fetching Garmin data, creating or
  scheduling workouts, or when the user mentions Garmin, pacerai, Connect, or
  workout JSON for this project.
---

# Garmin CLI (`pacerai`)

From the project root, always use:

```bash
poetry run pacerai <command> [--user <name>] [options]
```

Default user is **omer** unless the user asks for another account.

- Structured JSON on stdout: `{"status":"ok","data":{...}}` or `{"status":"error","message":"..."}`.
- Do not implement raw Garmin API calls in this repo; use the CLI or `get_garmin_client()` as described in `AGENTS.md`.

**Full command list, authentication, workout JSON schema, pace decimals, and workflows:** read `docs/garmin-cli.md` (shared with Claude Code via `.claude/commands/garmin-cli.md`).
