# Pacerai — Project Context

## Garmin Connect Users

Users are configured in `users.json` (gitignored). Use **omer by default**. Switch to other users only when explicitly requested.

## Garmin CLI — Use This First

**Always use `pacerai` for any Garmin data or workout operations.** Do not write raw API code.

```bash
# All commands — run from the project root
poetry run pacerai [--user <name>] <command> [options]

# Auth (tokens stored in macOS Keychain)
poetry run pacerai login                        # browser login form
poetry run pacerai login --force                # re-authenticate
# Common examples
poetry run pacerai activities --limit 5         # recent activities
poetry run pacerai activity <id>                # single activity
poetry run pacerai stats                        # today's stats
poetry run pacerai sleep                        # last night's sleep
poetry run pacerai workouts                     # library
poetry run pacerai create-workout @file.json    # create from schema
poetry run pacerai schedule <workout_id> <date> # schedule workout
poetry run pacerai scheduled --start DATE --end DATE
# To use another user, --user must come BEFORE the command:
poetry run pacerai --user rami activities
```

All output is JSON: `{"status":"ok","data":{...}}`. For the full command reference and workout JSON schema, read `.claude/commands/garmin-cli.md`.

## Python Environment

Always run Python scripts with **poetry**:

```bash
poetry run python script.py
# or
poetry run python -c "..."
```

## Coaching Plans

When building a coaching plan for a user, store all their information under:

```
.coaching_plans/<username>/
```

This directory is gitignored (contains personal health data). Create it on first use.

### Recommended structure

```
.coaching_plans/
  omer/
    profile.md          # age, weight, VDOT, goal race, health notes
    training_plan.md    # current multi-week plan with paces and targets
    nutrition_plan.md   # caloric targets, macros, meal timing
    weekly_checkins/    # one file per check-in: YYYY-MM-DD.md
    notes.md            # ongoing coaching notes, observations, decisions
```

### Workflow

1. **New athlete** → run intake (see `coaching/skills/client_intake_form.md`), create `profile.md`
2. **Build plan** → generate `training_plan.md` using `coaching/skills/training_plan_builder.md`
3. **Weekly check-in** → read `profile.md` + last checkin, fetch Garmin data, write `weekly_checkins/YYYY-MM-DD.md`
4. **Always read `profile.md` first** before any coaching response — it holds the athlete's full context

Add `.coaching_plans/` to `.gitignore` (already done).

## Facts & Coaching Sync (Supabase)

Before coaching, check for prior context: `pacerai read-facts --start <date> --end <date>` and `pacerai read-coaching-notes --start <date> --end <date>`. After producing an interpretation or recommendation, persist it with `pacerai push-coaching-note --date <date> --body "..."` so future sessions have continuity. `sync-facts` is deterministic (no AI) and just mirrors Garmin data into Supabase — run it to keep facts current, but the *interpretation* is always written by Claude, not by the sync command itself.

## Workout Design Principles

- **Base/easy runs**: use heart-rate targets.
- **All other workouts** (intervals, tempo, threshold, race-pace, etc.): use **pace-based targets** (e.g. 5:00, 4:50 min/km) with `pace.zone` (workoutTargetTypeId 6). Never use heart rate for these.

### Usage in code

```python
from pacerai.auth import get_garmin_client

garmin = get_garmin_client()             # default user (omer)
garmin = get_garmin_client("yuval")      # explicit only
garmin = get_garmin_client("rami")       # explicit only
```
