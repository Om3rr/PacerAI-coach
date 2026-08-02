---
name: garmin-sync
description: Read and write Garmin facts + coaching notes in Supabase so coaching sessions have memory across time. Use at the start of a coaching session to load prior context, and after producing an interpretation/recommendation to persist it.
---

## What this skill does

Pacerai stores two kinds of data in Supabase, kept deliberately separate:

- **Facts** (`garmin_facts` table) — raw Garmin data (activities, sleep, HRV, stats, body battery, training status), flattened into sparse `(user, date, source, metric_key, value)` rows. Pure code transformation, **no AI involved**. Safe to run unattended later (e.g. a scheduled job).
- **Coaching notes** (`coaching_notes` table) — dated interpretations/recommendations. **Always AI-authored** — Claude reads the facts, reasons about them, writes the note. The sync commands themselves never generate interpretation text.

This separation means facts can be kept fresh by a dumb scheduled job with no AI access, while the actual coaching judgment always comes from a model reading the facts (interactively today; potentially a headless LLM call later — same commands, different `--generated-by` value).

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

## Automated sync (GitHub Actions)

`.github/workflows/sync-facts.yml` runs `sync-facts --days 2` daily. No macOS Keychain in CI, so auth goes through an env var instead: `pacerai/auth.py::get_garmin_client` falls back to `GARMIN_TOKEN_<USER>` (same blob format as Keychain) when Keychain and the legacy file token store both come up empty. Export the current Keychain blob with `pacerai export-token` and set it as a GitHub Actions secret — see README "Automated daily sync" for the full setup. Treat that blob as a password; never print or commit it.

## Caution

`garmin_facts` and `coaching_notes` are real data once populated — don't run broad/unscoped deletes against them without explicit user confirmation, even for cleanup. Prefer scoping any cleanup query tightly (specific date range, specific test rows) over `WHERE user_name = ...` alone.
