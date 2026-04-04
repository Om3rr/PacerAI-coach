# Garmin Sleep Analysis — Nutrition Coaching Skill

## 1. Purpose

This skill enables a **nutrition and training coach** (human or AI) to:

- Pull a client’s **Garmin Connect sleep** data via the Python `garminconnect` library.
- **Interpret** duration, stages, recovery signals (SpO₂, respiration, stress), and Garmin’s composite sleep score.
- Produce **actionable coaching**: training load, recovery, and **nutrition** adjustments aligned with a **sports-active parent** pursuing **fat loss** through **aerobic training**.

**When to use**

- Weekly check-ins, recovery reviews, or when the client reports fatigue, cravings, or poor adherence.
- Before prescribing hard intervals or aggressive calorie deficits.
- When investigating suspected recovery debt, stress overload, or sleep-disordered breathing patterns (always with appropriate medical-disclaimer framing).

**Project context**

- Run from the project root using `poetry run python3`.
- Authenticated client: `from pacerai.auth import get_garmin_client` then `garmin = get_garmin_client()` (use `get_garmin_client("username")` for other users only when explicitly requested).
- Sleep payload: `garmin.get_sleep_data("YYYY-MM-DD")` (string date in local/Garmin convention for that account).

---

## 2. How to Fetch Sleep Data

Run from the **garminus project root** (or ensure `main` is importable on `PYTHONPATH`).

### Single date

```python
from datetime import date
from main import get_garmin_client

garmin = get_garmin_client()
target = "2025-03-15"  # or date.today().isoformat()
raw = garmin.get_sleep_data(target)
# raw is typically a dict; guard for None or empty on days with no data
if not raw:
    print(f"No sleep data for {target}")
else:
    dto = raw.get("dailySleepDTO") or raw.get("sleepData")  # tolerate shape variance
```

### Last 7 days (loop)

```python
from datetime import date, timedelta
from main import get_garmin_client

garmin = get_garmin_client()
end = date.today()
rows = []
for i in range(7):
    d = (end - timedelta(days=i)).isoformat()
    payload = garmin.get_sleep_data(d)
    rows.append({"date": d, "payload": payload})
# rows[0] = today, rows[1] = yesterday, ...
# Process each row["payload"] for trends (see §5)
```

**Implementation notes**

- Some days return **no sleep** (travel, watch off, sync delay). Skip or mark `missing` instead of treating as zero sleep.
- Prefer extracting **`dailySleepDTO`** when present; if the library returns a different top-level key, normalize before interpretation.
- For coaching, use **calendar dates** the client recognizes; align with their timezone if comparing to training logs.

---

## 3. Key Fields to Extract

Assume nested under **`dailySleepDTO`** unless the API nests differently—always use safe `.get()` access.

| Path / field | Meaning | Optimal / reference range |
|--------------|---------|---------------------------|
| `dailySleepDTO.sleepTimeSeconds` | Total sleep duration | **7–9 h** → **25 200–32 400 s** |
| `dailySleepDTO.deepSleepSeconds` | Deep (N3) sleep | **16–33%** of total sleep time |
| `dailySleepDTO.remSleepSeconds` | REM sleep | **21–31%** of total sleep time |
| `dailySleepDTO.awakeSleepSeconds` | Time awake during the sleep period | Lower is better; use for fragmentation context |
| `dailySleepDTO.averageSpO2Value` | Average blood oxygen overnight | **95–100%** |
| `dailySleepDTO.lowestSpO2Value` | Lowest SpO₂ | **Flag if &lt; 90%** (possible desaturation) |
| `dailySleepDTO.averageRespirationValue` | Breaths per minute | **12–20** typical adult range |
| `dailySleepDTO.avgHeartRate` | Average HR during sleep | Individual baseline; watch **sudden elevation** vs client norm |
| `dailySleepDTO.avgSleepStress` | Autonomic stress during sleep | **0–15** favorable; higher = more vigilance/load |
| `dailySleepDTO.sleepScores.overall.value` | Garmin composite sleep score | **0–100** (higher better) |
| `dailySleepDTO.sleepScores.overall.qualifierKey` | Qualitative bucket | **POOR / FAIR / GOOD / EXCELLENT** |
| `dailySleepDTO.sleepScoreFeedback` | Garmin text feedback key | Map to human-readable message if needed |

**Derived metrics (compute in code)**

- `deep_pct = 100 * deepSleepSeconds / sleepTimeSeconds` (if `sleepTimeSeconds > 0`)
- `rem_pct = 100 * remSleepSeconds / sleepTimeSeconds`

---

## 4. Interpretation Logic

Evaluate in order **after** confirming valid sleep data for the night (`sleepTimeSeconds` present and &gt; 0). Combine multiple flags when applicable; prioritize **safety** (SpO₂) and **severe short sleep**.

```text
IF no payload OR sleepTimeSeconds missing/zero:
  → "No Garmin sleep for this date"; do not infer poor sleep from absence alone.

IF averageSpO2Value < 94 OR lowestSpO2Value < 90:
  → Flag possible sleep-related breathing issue / desaturation.
  → Recommend medical evaluation (PCP or sleep medicine); do not diagnose.
  → Coaching: avoid stacking hard training + large deficit until assessed.

IF sleepScores.overall.value < 60 OR qualifierKey == "POOR":
  → Reduce training intensity/volume next day(s); prioritize easy aerobic or rest.
  → Nutrition: maintain energy availability; do not deepen deficit; ensure adequate carbs around training.
  → Explicitly flag to client in written summary.

IF sleepTimeSeconds < 21600 (i.e. < 6 h):
  → Nutrition protocol: maintain total calories (or slight increase if highly active parent);
     prioritize protein and complex carbs; avoid aggressive restriction.
  → Training: cap intensity; prefer Zone 2 / easy work.

IF deep_pct < 16%:
  → Recovery concern: suggest earlier consistent bedtime, wind-down routine, caffeine cutoff.
  → Mention reducing alcohol (deep sleep suppressor).

IF rem_pct < 21%:
  → Flag risk of hormonal stress and emotional eating patterns; empathetic check-in.
  → Review alcohol, late heavy meals, screen time, irregular sleep schedule.

IF avgSleepStress > 25:
  → High autonomic load overnight: prescribe rest day or easy session only.
  → Pair with stress-management and sleep-consistency messaging (not moralizing).

IF (good sleep streak: e.g. 3+ nights with overall ≥ 70 or qualifier GOOD/EXCELLENT
    AND no SpO₂ flags AND avgSleepStress generally ≤ 25):
  → Green light for planned hard sessions and controlled deficit days (within coach plan).
```

**Client profile anchor**

- Sports-active parent, fat loss via aerobic work: protect **recovery** and **adherence** over maximal weekly deficit when sleep is compromised.

---

## 5. Weekly Trend Analysis

When you have **7 daily records** (see §2 loop):

1. **Chronic short sleep**  
   - Count nights with `sleepTimeSeconds < 25 200` (&lt; 7 h) or &lt; 21 600 (&lt; 6 h).  
   - If ≥ 3 short nights: shift plan toward **sustainability**—fewer “hero” sessions, stronger sleep hygiene coaching.

2. **REM debt**  
   - Track `rem_pct` across nights. **Sustained** low REM suggests schedule disruption, alcohol, or stress—not a one-off bad night.

3. **Deep sleep pattern**  
   - Repeated `deep_pct < 16%` with normal time in bed → focus on **timing and substances** (alcohol, late training, caffeine).

4. **SpO₂ trend**  
   - Single noisy night vs **multi-night** low average or repeated lowest &lt; 90%. Trend + symptoms (snoring, AM headaches) strengthens referral messaging **without diagnosing**.

5. **Stress trend**  
   - Rising `avgSleepStress` across the week → cumulative load; front-load **easy days** and stabilize calories before tightening deficit.

6. **Score trajectory**  
   - Improving `sleepScores.overall.value` + stable duration → client is adapting; can progress training/nutrition as planned.

---

## 6. Coaching Output Template

Use this as a **client-facing weekly sleep summary**. Replace placeholders; omit sections with no data.

```markdown
### Sleep check-in — week of {{WEEK_START}} to {{WEEK_END}}

**Headline:** {{ONE_LINE_SUMMARY}}  
*(e.g. “Solid recovery most nights; two short sleeps around {{EVENT}}.”)*

**Averages (7 nights)**  
- Time asleep: **{{AVG_SLEEP_HOURS}} h** (nights logged: **{{N_LOGGED}}/7**)  
- Garmin sleep score: **{{AVG_SCORE}}** (range **{{MIN}}–{{MAX}}**)  
- Best night: **{{BEST_DATE}}** — **{{BEST_NOTE}}**  
- Toughest night: **{{WORST_DATE}}** — **{{WORST_NOTE}}**

**Stages (when available)**  
- Deep sleep: typically **{{DEEP_PCT_RANGE}}** of your night — {{DEEP_COACH_COMMENT}}  
- REM: **{{REM_PCT_RANGE}}** — {{REM_COACH_COMMENT}}

**Recovery signals**  
- Overnight stress: **{{STRESS_TREND}}**  
- SpO₂: **{{SPO2_SUMMARY}}** {{SPO2_ACTION_IF_ANY}}

**Training this week**  
{{TRAINING_ADJUSTMENTS}}

**Nutrition this week**  
{{NUTRITION_ADJUSTMENTS}}

**Your 2–3 focus habits**  
1. {{HABIT_1}}  
2. {{HABIT_2}}  
3. {{HABIT_3}}

**Medical safety**  
{{MEDICAL_DISCLAIMER_OR_EMPTY}}
*(If SpO₂ flags: encourage professional evaluation; you are not providing a medical diagnosis.)*
```

---

## 7. Nutrition Adjustments Based on Sleep

| Situation | Next-day (or multi-day) nutrition coaching |
|-----------|-----------------------------------------------|
| **Poor sleep night** (POOR score, &lt; 6 h, or major fragmentation) | **Maintain or slightly increase** calories vs a strict deficit day. **Prioritize protein** (satiety, lean mass). **Emphasize complex carbs** around training and earlier in the day. **Avoid compounding** with the hardest session + lowest calories. |
| **Repeated poor sleep** | Keep **protein floor** non-negotiable; use **moderate carb** on training days; **do not chase fat loss** with deeper deficit until sleep stabilizes. |
| **Good sleep streak** (consistent duration + GOOD/EXCELLENT or scores clearly strong) | **Green light** for planned **hard training** and **controlled deficit** days per the overall plan; still monitor fatigue and life stress. |
| **High overnight stress** (`avgSleepStress` high) | Stabilize **meal timing** and **adequate carbs** relative to aerobic volume; reduce perfectionism on tracking; avoid alcohol as a “wind-down.” |

**Principles for this client archetype**

- Fat loss is a **months-long** project; **sleep-protected** weeks improve adherence and protect lean mass.  
- Aerobic training **depends on glycogen and recovery**—short sleep is a signal to **fuel appropriately**, not to “earn” rest through undereating.

---

## Skill execution checklist (for the AI)

1. Import `get_garmin_client` from `main` and call `get_sleep_data` for the requested date(s).  
2. Normalize payload → `dailySleepDTO` and compute `deep_pct`, `rem_pct`.  
3. Apply §4 rules; note conflicts (e.g. short sleep + good score—explain nuance).  
4. Build §5 weekly narrative if 7 days supplied.  
5. Output §6 template with §7 nutrition and training hooks filled in.  
6. Keep tone **supportive, specific, and non-judgmental**; escalate **SpO₂** concerns with clear, non-diagnostic language.
