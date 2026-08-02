# Pacerai — Context for Claude Projects

Pacerai is a Garmin Connect coaching toolkit. It has a CLI (`pacerai`, not available in this Project) and a Supabase database that stores two things:

## `garmin_facts` — raw Garmin data, sparse format

One row per `(user, date, source, metric_key)`. `source` is one of: `activity`, `sleep`, `hrv`, `stats`, `body_battery`, `training_status`. `metric_value` holds numbers, `metric_text` holds strings (only one is populated per row). New metric types can appear at any time without a schema change — don't assume a fixed set of `metric_key`s.

Common keys: `distance_km`, `duration_min`, `avg_hr`, `calories` (activity) · `duration_sec`, `sleep_score`, `avg_spo2` (sleep) · `last_night_avg`, `status` (hrv) · `total_steps`, `resting_hr`, `stress_avg` (stats) · `charged`, `drained` (body_battery) · `vo2max` (training_status).

This data is purely mechanical — nobody has interpreted it yet.

## `coaching_notes` — dated interpretations

One row per note: `user_name`, `note_date`, optional `period_start`/`period_end` for weekly notes, `title`, `body` (the actual coaching text), `tags`, `generated_by` (`claude-interactive` | `claude-api` | `manual`), `status` (`draft` | `final`).

This is where prior coaching judgment lives — read it before giving new advice so you don't repeat or contradict a prior recommendation.

## How to use this as a coach

1. Read recent rows from both tables for the athlete and date range in question.
2. Reason over the facts yourself — Pacerai never auto-generates interpretations.
3. If you produce a new recommendation worth remembering, it should be written back to `coaching_notes` (via the `pacerai push-coaching-note` CLI, run from the Pacerai repo — not available directly from this Project unless connected via an integration).
