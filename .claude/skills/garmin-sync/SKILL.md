---
name: garmin-sync
description: Read and write Garmin facts + coaching notes in Supabase so coaching sessions have memory across time. Use at the start of a coaching session to load prior context, and after producing an interpretation/recommendation to persist it.
---

## What this skill does

Pacerai stores two kinds of data in Supabase, kept deliberately separate:

- **Facts** (`garmin_facts` table) — raw Garmin data (activities, sleep, HRV, stats, body battery, training status), flattened into sparse `(user, date, source, metric_key, value)` rows. Pure code transformation, **no AI involved**. Safe to run unattended later (e.g. a scheduled job).
- **Coaching notes** (`coaching_notes` table) — dated interpretations/recommendations. **Always AI-authored** — Claude reads the facts, reasons about them, writes the note. The sync commands themselves never generate interpretation text.

This separation means facts can be kept fresh by a dumb scheduled job with no AI access, while the actual coaching judgment always comes from a model reading the facts — interactively in a chat session (`--generated-by claude-interactive`, the default) or from the daily headless job (`--generated-by claude-headless`, see below).

## When to use

- **Start of a coaching session / check-in**: before answering, pull recent context instead of (or alongside) live Garmin queries.
- **After writing a coaching interpretation, recommendation, or check-in summary**: persist it so the next session doesn't start cold.
- **Periodically (or when data looks stale)**: sync facts so `read-facts` has current data.

## Commands

All run via `poetry run pacerai [--user <name>] <command>`. Output is JSON: `{"status":"ok","data":...}`.

```bash
# Deterministic, no AI — pull recent Garmin data into garmin_facts
pacerai sync-facts --days 7
pacerai sync-facts --days 7 --dry-run     # inspect rows without writing

# Read facts back (use this instead of re-fetching from Garmin when recent data already synced)
pacerai read-facts --start 2026-04-01 --end 2026-04-07
pacerai read-facts --start 2026-04-01 --end 2026-04-07 --source sleep

# Persist an interpretation you (Claude) just wrote
pacerai push-coaching-note --date 2026-04-07 \
  --title "Week check-in" \
  --body "Aerobic HR trending down at same pace — good sign. Sleep debt building, ease Thursday's intervals." \
  --tags recovery,pacing

# Read back prior coaching context
pacerai read-coaching-notes --start 2026-04-01 --end 2026-04-07

# Most recent synced date (used by the daily job's dedup check)
pacerai last-synced
```

`--body` also accepts `@filepath` for longer notes.

## Facts schema reference

`garmin_facts` sources and their `metric_key`s (all sparse — new keys never require a migration):

| source | metric_key examples |
|---|---|
| `activity` | `distance_km`, `duration_min`, `avg_hr`, `avg_speed_ms`, `calories`, `activity_type` (text), `activity_name` (text) |
| `sleep` | `duration_sec`, `deep_sec`, `light_sec`, `rem_sec`, `awake_sec`, `avg_spo2`, `sleep_score` |
| `hrv` | `last_night_avg`, `weekly_avg`, `last_night_5min_high`, `status` (text) |
| `stats` | `total_steps`, `total_distance_m`, `active_calories`, `resting_calories`, `avg_hr`, `resting_hr`, `stress_avg`, `body_battery_charged`, `body_battery_drained` |
| `body_battery` | `charged`, `drained` |
| `training_status` | `vo2max` |
| `weight` | `weight_kg`, `bmi`, `body_fat_pct` |

`source_id` holds the Garmin activity ID for `activity` facts, and `""` (never `NULL`) for daily-aggregate sources — this matters because Postgres unique constraints never match two `NULL`s, so upserts would silently duplicate if `source_id` were left null. Don't change this without checking `pacerai/supabase_sync.py::_row`.

## One-time setup (already done for this project)

`supabase/schema.sql` creates both tables — run once via the Supabase SQL editor (PostgREST can't run DDL). `.env` needs `SUPABASE_URL` and `SUPABASE_SERVICE_KEY` (the **secret** key, not publishable/anon — this runs server-side and needs to bypass RLS).

## Automated sync (local, via launchd)

GitHub Actions was tried first but Garmin appears to block/rate-limit the OAuth login flow from GitHub's shared runner IPs (429 on the OAuth exchange endpoint on the very first real attempt). The daily sync now runs locally instead: `scripts/daily_sync.sh`, scheduled via `launchd` (see `scripts/com.pacerai.dailysync.plist.example`), checks `pacerai last-synced` to avoid double-running, calls `sync-facts` for the gap, then runs a headless Claude Code session (`claude -p`, restricted to the `pacerai` CLI via `--allowedTools`) that only writes a new coaching note if something's actually changed since the last one. Full setup in README "Automated daily sync (local, via launchd)".

`pacerai export-token` / the `GARMIN_TOKEN_<USER>` env-var auth fallback in `auth.py` are no longer used for this but left in place — harmless, generically useful if a headless/CI setup is worth revisiting later (e.g. a residential-IP self-hosted runner).

## Caution

`garmin_facts` and `coaching_notes` are real data once populated — don't run broad/unscoped deletes against them without explicit user confirmation, even for cleanup. Prefer scoping any cleanup query tightly (specific date range, specific test rows) over `WHERE user_name = ...` alone.
