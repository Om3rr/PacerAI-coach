# Garmin CLI Skill

You have access to a battle-tested Garmin Connect CLI (`pacerai`).
**Always use it instead of writing raw API code.** Every command outputs structured JSON.

## How to run

```bash
poetry run pacerai <command> [--user <name>] [options]
```

Default user is **omer**. Only pass `--user` when explicitly asked to work with another user.

---

## Authentication

Tokens are stored in **macOS Keychain** (not files). Login opens a local browser form.

```bash
# Login (opens browser with password + OTP form)
poetry run pacerai --user omer login
poetry run pacerai --user rami login

# Re-authenticate (force even if tokens exist)
poetry run pacerai --user omer login --force

# Remove tokens
poetry run pacerai --user omer logout
```

If `get_garmin_client()` raises `RuntimeError: No valid tokens`, run the login command above.

---

## Activities

### List recent activities
```bash
# Last 10 (default)
poetry run pacerai activities

# Last 20 running activities
poetry run pacerai activities --limit 20 --type running

# By date range
poetry run pacerai activities --start 2026-03-01 --end 2026-03-26

# Full raw API response (when you need fields not in slim view)
poetry run pacerai activities --full
```

**Slim output fields:** `id, name, type, date, distance_km, duration_min, avg_hr, avg_pace (MM:SS/km), calories`

### Get single activity
```bash
poetry run pacerai activity 12345678
poetry run pacerai activity 12345678 --full   # raw response
```

### Delete activity
```bash
poetry run pacerai delete-activity 12345678
```

### Rename activity
```bash
poetry run pacerai rename-activity 12345678 "Easy Run — Zone 2"
```

### Create manual activity (log a past run)
```bash
poetry run pacerai create-activity \
  --start "2026-03-25T07:00:00" \
  --type running \
  --distance-km 10.5 \
  --duration-min 55 \
  --name "Morning Run"
```
`--timezone` defaults to `Asia/Jerusalem`. Common type keys: `running`, `cycling`, `strength_training`, `walking`.

---

## Workout Library

### List library
```bash
poetry run pacerai workouts           # slim view (id, name, sport, updated)
poetry run pacerai workouts --limit 100 --full
```

### Get single workout (full schema)
```bash
poetry run pacerai workout 987654
```

### Create workout from JSON schema
```bash
# From inline JSON string
poetry run pacerai create-workout '{"name":"Easy Run","sport":"running","steps":[...]}'

# From a JSON file
poetry run pacerai create-workout @my_workout.json

# Dry run — print API payload without uploading
poetry run pacerai create-workout @my_workout.json --dry-run
```

**Returns:** `{"status":"ok","data":{"workout_id":987654,"name":"Easy Run"}}`

### Delete workout
```bash
poetry run pacerai delete-workout 987654
```

---

## Workout JSON Schema (for create-workout)

```json
{
  "name": "Threshold 3×8min",
  "sport": "running",
  "steps": [
    {
      "type": "step",
      "step_type": "warmup",
      "duration": {"type": "time", "seconds": 900},
      "target": {"type": "heart_rate", "min": 120, "max": 150}
    },
    {
      "type": "repeat",
      "iterations": 3,
      "steps": [
        {
          "type": "step",
          "step_type": "interval",
          "duration": {"type": "time", "seconds": 480},
          "target": {"type": "pace", "min_km": 4.48, "max_km": 4.65}
        },
        {
          "type": "step",
          "step_type": "recovery",
          "duration": {"type": "time", "seconds": 180},
          "target": {"type": "heart_rate", "min": 120, "max": 148}
        }
      ]
    },
    {
      "type": "step",
      "step_type": "cooldown",
      "duration": {"type": "time", "seconds": 900},
      "target": {"type": "heart_rate", "min": 120, "max": 150}
    }
  ]
}
```

### Schema reference

**`sport`:** `running` · `cycling` · `swimming` · `strength` · `walking` · `hiking`

**`step.step_type`:** `warmup` · `cooldown` · `interval` · `recovery` · `rest`

**`duration.type`:**
| type | extra field | example |
|------|-------------|---------|
| `time` | `seconds: int` | 8 min → `480` |
| `distance` | `meters: int` | 800m → `800` |
| `lap_button` | — | manual advance on watch |
| `reps` | `reps: int` | 12 reps → `12` |

**`target.type`:**
| type | fields | notes |
|------|--------|-------|
| `none` | — | no target shown |
| `heart_rate` | `min: int, max: int` | bpm |
| `pace` | `min_km: float, max_km: float` | decimal min/km. `4.5`=4:30, `5.083`=5:05, `5.833`=5:50 |

**Pace decimal quick reference:**
- 4:00/km → `4.0`
- 4:15/km → `4.25`
- 4:30/km → `4.5`
- 4:45/km → `4.75`
- 5:00/km → `5.0`
- 5:05/km → `5.083`
- 5:10/km → `5.167`
- 5:15/km → `5.25`
- 5:20/km → `5.333`
- 5:30/km → `5.5`
- 5:50/km → `5.833`
- 6:00/km → `6.0`
- 6:10/km → `6.167`

**Design rule:** Easy/base runs → `heart_rate` target. All quality work (intervals, tempo, threshold, race pace) → `pace` target. Never use HR for quality steps.

---

## Scheduling

### Schedule a library workout on a date
```bash
poetry run pacerai schedule 987654 2026-03-28
```
**Returns:** `{"schedule_id": 111222, "workout_id": 987654, "date": "2026-03-28"}`

### List scheduled workouts
```bash
poetry run pacerai scheduled --start 2026-03-24 --end 2026-03-30
```
**Slim fields:** `schedule_id, workout_id, name, date, sport`

Note: scheduled workouts are fetched via Garmin's calendar service (month-based). Multi-month ranges are handled automatically.

### Remove a scheduled workout
```bash
poetry run pacerai unschedule 111222   # use schedule_id from 'scheduled' output
```

---

## User Metrics

### Daily stats (steps, HR, calories, stress, body battery)
```bash
poetry run pacerai stats                   # today
poetry run pacerai stats --date 2026-03-25
```

### Heart rate
```bash
poetry run pacerai hr                      # today, slim (resting/min/max/7-day avg)
poetry run pacerai hr --date 2026-03-25 --full   # full HR timeline
```

### Sleep
```bash
poetry run pacerai sleep                   # last night
poetry run pacerai sleep --date 2026-03-25
```
**Slim fields:** `duration_sec, deep_sec, light_sec, rem_sec, awake_sec, sleep_score, avg_spo2`

### HRV
```bash
poetry run pacerai hrv
poetry run pacerai hrv --date 2026-03-25
```

### Body battery
```bash
poetry run pacerai body-battery
poetry run pacerai body-battery --start 2026-03-20 --end 2026-03-26
```

### Weight
```bash
poetry run pacerai weight --start 2026-03-01 --end 2026-03-26
```

### Training status and load
```bash
poetry run pacerai training-status
```

### Race predictions
```bash
poetry run pacerai race-predictions
```

### Personal records
```bash
poetry run pacerai personal-records
```

---

## Common workflows

### Create and schedule a workout in one shot
```bash
# Step 1: create (note the workout_id in output)
poetry run pacerai create-workout @workout.json

# Step 2: schedule it
poetry run pacerai schedule <workout_id> 2026-03-28
```

### Build a full training week
Create each workout as a JSON file, upload and schedule sequentially:
```bash
for day in mon tue wed thu fri sat; do
  poetry run pacerai create-workout @week/${day}.json
done
# Then schedule each with its returned workout_id
```

### Check another user's calendar
```bash
poetry run pacerai --user bob scheduled --start 2026-03-24 --end 2026-03-30
```

---

## Error output format
```json
{"status": "error", "message": "ValueError: Unknown sport 'foo'. Valid: running, cycling..."}
```
If a command fails, read the message — it tells you exactly what went wrong and what values are valid.
