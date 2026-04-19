# Pacerai

[![CI](https://github.com/Om3rr/PacerAI-coach/actions/workflows/ci.yml/badge.svg)](https://github.com/Om3rr/PacerAI-coach/actions/workflows/ci.yml)
[![Coverage](https://img.shields.io/badge/coverage-checked-brightgreen)](https://github.com/Om3rr/PacerAI-coach/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)

**AI-powered Garmin Connect coaching toolkit.** Use it from **Claude Code** or **Cursor** (Agent) like a personal running coach — it reads your real Garmin data and responds to natural language. Project context for assistants is in `AGENTS.md`; Cursor also loads skills from `.cursor/skills/`.

---

## What You Can Do

Just start a conversation. No commands to memorize.

**Getting started:**
> "Hi, I'm Omer. I just set up Pacerai — can you help me log in and take a look at my recent runs?"

> "I'm training for my second marathon in October. Pull my last 3 weeks of activities and tell me how my training looks."

> "I haven't been sleeping well this week. Check my sleep and HRV data and tell me if I should take it easy today."

**Weekly check-ins:**
> "It's Sunday — let's do my weekly check-in. Pull everything from Garmin and coach me through the week."

> "I felt strong this week but my easy pace HR was higher than usual. What's going on?"

**Workout planning:**
> "Design a 5×1km tempo interval session for me targeting 4:50/km and push it to my Garmin."

> "I'm running my long run tomorrow — schedule the 18km easy workout from my library for tomorrow."

**Rami (coached athlete):**
> "Pull Rami's last 5 runs — how are his easy-pace HR trends looking compared to 4 weeks ago?"

---

## How It Works

1. Your coding assistant reads your Garmin data through the `pacerai` CLI
2. It uses the coaching knowledge base (`coaching/`) to interpret it
3. It gives you a personalized, evidence-based response — not generic advice

**No app to install. No dashboard to visit.** Open Claude Code or Cursor in this directory and start talking.

---

## Setup (One Time)

### 1. Install

```bash
git clone https://github.com/Om3rr/PacerAI-coach.git
cd PacerAI-coach
poetry install
```

### 2. Add your user

```bash
cp users.json.example users.json
# Edit users.json — add your Garmin email under your name
```

```json
{
  "omer": { "email": "you@example.com" }
}
```

### 3. Log in

```bash
poetry run pacerai login
```

A browser window opens. Enter your Garmin Connect credentials. Tokens are saved to macOS Keychain — you only need to do this once.

MFA supported. If your account uses two-factor authentication, you'll be prompted for the code.

---

## More Example Prompts

### First session
> "Hi, I'm [name]. Help me get set up — I want to log in and see my recent runs."

> "I just finished my first week of marathon training. Pull my activities and give me feedback."

### Daily check-in
> "Quick check — how's my body battery and sleep looking today?"

> "My resting HR was elevated this morning. Is that something to worry about?"

### Training analysis
> "Compare my easy run paces over the last 4 weeks. Am I getting more aerobic efficient?"

> "I've been running 5 days a week for a month. Am I ready to add a 6th day?"

> "My long run last weekend was 24km at 5:45/km. Is that appropriate for my current fitness?"

### Workout creation
> "Create a pyramid interval workout: 400m, 800m, 1200m, 800m, 400m at 4:40/km with 90-second recoveries. Push it to Garmin."

> "Build me an easy 60-minute run with HR cap at 148 bpm."

> "Schedule my tempo workout for Thursday."

### Coaching & planning
> "I'm 12 weeks out from my marathon. Build me a training plan."

> "I missed three runs this week — life got in the way. How do we recover?"

> "I feel like I'm plateauing. What does my data say?"

### Nutrition & recovery
> "Based on my training load this week, what should my caloric target be?"

> "I slept 5 hours last night. Should I still do my intervals?"

### Multi-user (coaches)
> "Check Rami's last week — he's 68 and training for a 10K. How did he do?"

> "Pull Yuval's stats and compare this week's volume to last week."

---

## Supported Users

| User | Role |
|---|---|
| omer | Default user |
| yuval | Secondary athlete |
| rami | Age 68, coached runner, trains at Givat Ram |

To add a new user: add them to `users.json`, run `poetry run pacerai login --user <name>`.

---

## What the assistant can access

All data fetched live from Garmin Connect:

| Category | What's Available |
|---|---|
| Activities | Recent runs, distance, pace, HR, calories |
| Sleep | Duration, deep/REM/light, SpO2, sleep score |
| HRV | Daily HRV, trends |
| Heart Rate | Resting HR, daily min/max, 7-day average |
| Body Battery | Charge/drain patterns |
| Stats | Steps, calories, stress level |
| Training Status | Garmin's load/status assessment |
| Race Predictions | Garmin's predicted times |
| Workouts | Full library — create, schedule, manage |
| Calendar | Scheduled workout history |

---

## CLI Reference (for power users)

All commands: `poetry run pacerai <command> [--user <name>]`

```bash
# Activities
pacerai activities --limit 20
pacerai activities --start 2026-03-01 --end 2026-03-31 --type running
pacerai activity <id>

# Health metrics
pacerai sleep
pacerai hr
pacerai hrv
pacerai stats
pacerai body-battery --start 2026-04-01 --end 2026-04-04
pacerai training-status
pacerai race-predictions

# Workout library
pacerai workouts
pacerai create-workout @my_workout.json
pacerai create-workout @my_workout.json --dry-run
pacerai schedule <workout_id> 2026-04-10

# Auth
pacerai login
pacerai logout
```

All output is JSON: `{"status":"ok","data":{...}}`.

---

## Workout Schema

Push structured workouts directly to your Garmin device:

```json
{
  "name": "Tempo Intervals",
  "sport": "running",
  "steps": [
    {
      "type": "step",
      "step_type": "warmup",
      "duration": { "type": "time", "seconds": 600 },
      "target": { "type": "heart_rate", "min": 120, "max": 148 }
    },
    {
      "type": "repeat",
      "iterations": 4,
      "steps": [
        {
          "type": "step",
          "step_type": "interval",
          "duration": { "type": "distance", "meters": 1000 },
          "target": { "type": "pace", "min_km": 4.83, "max_km": 5.0 }
        },
        {
          "type": "step",
          "step_type": "recovery",
          "duration": { "type": "time", "seconds": 90 },
          "target": { "type": "heart_rate", "min": 110, "max": 140 }
        }
      ]
    },
    {
      "type": "step",
      "step_type": "cooldown",
      "duration": { "type": "time", "seconds": 600 },
      "target": { "type": "heart_rate", "min": 115, "max": 145 }
    }
  ]
}
```

**Pace notation:** decimal minutes. `4.5` = 4:30/km. `min_km` = faster bound, `max_km` = slower bound.

---

## Development

```bash
poetry install --with dev
poetry run pytest
poetry run pytest --cov=pacerai --cov-report=term-missing
```

Tests cover all pure logic (pace math, workout builder, auth tokens, keychain) without requiring Garmin credentials. The CI runs on every push and PR.

---

## Project Structure

```
pacerai/
  cli.py          # 30+ CLI commands + workout schema builder
  auth.py         # Garmin client factory, token management
  keychain.py     # macOS Keychain integration
  login_server.py # Browser-based login flow with MFA support
coaching/
  skills/         # 14 coaching protocols (intake, check-in, injury, race strategy...)
  research/       # Evidence base (zone 2, carb periodization, sleep, biomechanics...)
  books/          # Training book summaries (Daniels, Hansons, Pfitzinger, 80/20...)
tests/            # Pytest test suite (84 tests)
.github/
  workflows/
    ci.yml        # CI: test + coverage on every push/PR
```

---

## License

MIT
