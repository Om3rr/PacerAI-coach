# Pace Calculator Skill

## Overview

This document defines the complete methodology for deriving training paces from race performances using Jack Daniels' VDOT framework. It is the authoritative reference for all pace-related coaching decisions.

---

## 1. VDOT Derivation — Step by Step

VDOT is a surrogate VO2max value derived from race performance. It does not require lab testing — it is inferred from the oxygen cost of running at race pace combined with the fractional utilization sustainable for a given duration.

### 1.1 Conceptual Foundation

The calculation rests on three components:

- **Oxygen cost of running at velocity V** (ml/kg/min):
  `O2_cost = −4.60 + 0.182258 × V + 0.000104 × V²`
  where V is in meters per minute.

- **Fractional VO2max utilization** (% of VO2max sustainable for the race duration, expressed as a fraction):
  `%VO2max = 0.8 + 0.1894393 × e^(−0.012778 × t) + 0.2989558 × e^(−0.1932605 × t)`
  where t is race duration in minutes.

- **VDOT** (the effective VO2max):
  `VDOT = O2_cost / %VO2max`

### 1.2 Step-by-Step Calculation

**Step 1: Convert race time to decimal minutes.**

> Example: 5K in 22:30 → t = 22.5 min

**Step 2: Convert race distance to meters.**

| Race | Meters |
|------|--------|
| 1 mile | 1609.34 |
| 5K | 5000 |
| 10K | 10000 |
| Half Marathon | 21097.5 |
| Marathon | 42195 |

**Step 3: Compute average velocity V (m/min).**

`V = distance_meters / t`

> Example: 5000 / 22.5 = 222.22 m/min

**Step 4: Compute oxygen cost at that velocity.**

`O2_cost = −4.60 + 0.182258 × V + 0.000104 × V²`

> Example: −4.60 + (0.182258 × 222.22) + (0.000104 × 222.22²)
> = −4.60 + 40.50 + 5.13 = 41.03 ml/kg/min

**Step 5: Compute fractional utilization at race duration.**

`%VO2max = 0.8 + 0.1894393 × e^(−0.012778 × 22.5) + 0.2989558 × e^(−0.1932605 × 22.5)`

> = 0.8 + 0.1894393 × 0.7514 + 0.2989558 × 0.01289
> = 0.8 + 0.1423 + 0.003854 = 0.9462

**Step 6: Divide to get VDOT.**

`VDOT = 41.03 / 0.9462 = 43.4`

**Step 7: Round to nearest integer (or use interpolation for precision).**

> VDOT = **43**

### 1.3 Multiple Race Times — Which to Use

- Use the **most recent** race within the last 16 weeks.
- If multiple recent races exist, use the one yielding the **highest VDOT** (best predictor of current fitness).
- Do not average VDOT values across races of different distances — select one.
- Time trials on the track are acceptable; road races should be noted as potentially slow (tangents, surface).

### 1.4 Quick Reference — VDOT from Common Race Times

| VDOT | 1 Mile | 5K | 10K | Half Marathon | Marathon |
|------|--------|----|-----|---------------|----------|
| 30 | 10:34 | 34:14 | 1:11:00 | 2:37:01 | 5:29:26 |
| 35 | 9:11 | 29:36 | 1:01:21 | 2:15:55 | 4:44:47 |
| 40 | 8:09 | 26:19 | 54:35 | 2:00:25 | 4:13:48 |
| 45 | 7:20 | 23:42 | 49:09 | 1:47:46 | 3:48:54 |
| 50 | 6:41 | 21:35 | 44:44 | 1:37:52 | 3:29:07 |
| 55 | 6:09 | 19:52 | 41:13 | 1:30:08 | 3:13:53 |

---

## 2. The Five Daniels Training Paces

### 2.1 Overview Table

| Pace Zone | Abbreviation | % VO2max | % HRmax | RPE (1–10) | Primary Adaptation |
|-----------|--------------|----------|---------|------------|-------------------|
| Easy | E | 59–74% | 65–79% | 3–4 | Aerobic base, recovery, fat metabolism |
| Marathon | M | 75–84% | 80–89% | 5–6 | Glycogen management, LT approach |
| Threshold | T | 83–88% | 88–92% | 6–7 | Lactate threshold, metabolic efficiency |
| Interval | I | 95–100% | 97–100% | 8–9 | VO2max development, cardiac output |
| Repetition | R | >100% | N/A (anaerobic) | 9–10 | Running economy, speed, neuromuscular |

> **Coaching Note:** HR is not a reliable indicator for Repetition pace because efforts are short (≤2 min) and HR lags behind intensity. Use pace and perceived effort for R workouts.

---

### 2.2 Easy Pace (E)

**Purpose:** Recovery, aerobic base building, long runs. The majority of weekly mileage (≥60%) should be at this effort.

**Physiological target:** 59–74% VO2max. This range allows full aerobic stimulus without accumulating significant lactate.

**Effort feel:** Fully conversational. You can speak in complete sentences. Breathing is rhythmic and unhurried.

**HR target:** 65–79% HRmax (or 60–75% Heart Rate Reserve).

**Calculation from VDOT:**
Easy pace corresponds to running at 59–74% of VDOT. In practice, use the midpoint (~67%) for most runs. The pace band is intentionally wide — athletes should run on the **slower end** when fatigued or in heat, faster end when fresh.

For practical use, consult the reference table in Section 3.

**Key rules:**
- Never run faster than the top of E range during designated easy days.
- Long runs stay within E pace regardless of athlete's desire to push.
- Use effort and HR to govern on hilly or hot days; ignore pace.

---

### 2.3 Marathon Pace (M)

**Purpose:** Race-specific preparation for marathon. Teaches the body to sustain a demanding but manageable effort for 2–5+ hours.

**Physiological target:** 75–84% VO2max. Sits just below lactate threshold, at a pace where glycogen is the dominant fuel but fat oxidation is still significant.

**Effort feel:** Comfortably hard. Conversation is possible but limited to short phrases. Breathing is steady and somewhat labored.

**HR target:** 80–89% HRmax.

**Key rules:**
- M pace segments are typically 12–18 miles total in a workout.
- Do not use M pace for athletes more than 6 weeks from their marathon — substitute T pace work instead.
- If marathon goal time differs significantly from VDOT-predicted time, use VDOT-derived M pace, not goal pace, until fitness catches up.

---

### 2.4 Threshold Pace (T)

**Purpose:** Raising the lactate threshold — the cornerstone of distance running development.

**Physiological target:** 83–88% VO2max. The pace at which blood lactate begins to accumulate faster than it can be cleared. Sustained T pace improves the body's lactate clearance capacity.

**Effort feel:** Comfortably hard. The correct T pace feels like the fastest effort you could sustain for ~60 minutes in a race.

**HR target:** 88–92% HRmax (or ~90% HRmax as a single-number guide).

**Session structure:**
- **Tempo runs:** 20–40 minutes of continuous T pace.
- **Cruise intervals:** 3–5 × (5–10 min at T) with 1-minute recovery jogs. Total T volume: 30–50 min per session.
- Do not exceed 10% of weekly mileage at T pace.

**Key rules:**
- T pace is a single point, not a range. Athletes often run too fast; reinforce discipline.
- Recovery between cruise intervals must be short (≤1 min jog). Longer recovery makes it an I workout.
- T workouts are not "race efforts" — they should feel manageable throughout.

---

### 2.5 Interval Pace (I)

**Purpose:** Maximizing VO2max by spending time at or near 100% VO2max.

**Physiological target:** 95–100% VO2max. Often described as "5K race effort" — because I pace and 5K race pace are approximately equivalent.

**Effort feel:** Hard. Breathing is labored and conversation is impossible.

**Session structure:**
- Intervals: 3–5 minutes each at I pace (e.g., 1000m or 1200m repeats).
- Recovery: Equal time jogging (1:1 work:rest ratio for most athletes).
- Total I pace volume: No more than 8% of weekly mileage, or ~10 km per session.

**Key rules:**
- Never cut recovery short to simulate race conditions.
- Do not run faster than I pace.
- I workouts are the most taxing — limit to once per week during heavy training.

---

### 2.6 Repetition Pace (R)

**Purpose:** Improving running economy and speed. Short, fast repeats at faster-than-race pace stress neuromuscular patterns.

**Physiological target:** Exceeds 100% VO2max (anaerobic). The stimulus is mechanical, not cardiovascular.

**Effort feel:** Very fast and controlled, but not an all-out sprint. Fast and smooth — not grinding.

**Session structure:**
- Repeats: 200m, 400m, or 600m at R pace.
- Recovery: Full recovery (2–3 minutes easy jogging or walking between reps). Work:rest ratio is often 1:3 or more.
- Total R volume: No more than 5% of weekly mileage, or 8 km per session.

**Key rules:**
- Full recovery is non-negotiable — if rest is cut short, pace will degrade and the economy benefit is lost.
- R workouts should never leave the athlete feeling spent. If the last rep is slower than the first, rest was insufficient.
- Use R pace sparingly in marathon training; most valuable for 5K–10K-focused athletes.

---

## 3. Pace Reference Table — VDOT 30 to 55

All paces shown in **min:sec per mile**. E pace shown as a range (slow–fast). M, T, I, R shown as single target paces.

| VDOT | E Pace (slow) | E Pace (fast) | M Pace | T Pace | I Pace | R Pace (400m) |
|------|--------------|--------------|--------|--------|--------|----------------|
| 30 | 13:40 | 12:30 | 11:30 | 10:58 | 10:15 | 9:48 |
| 31 | 13:18 | 12:10 | 11:11 | 10:40 | 9:58 | 9:31 |
| 32 | 12:58 | 11:51 | 10:53 | 10:22 | 9:41 | 9:15 |
| 33 | 12:38 | 11:33 | 10:36 | 10:06 | 9:25 | 9:00 |
| 34 | 12:20 | 11:16 | 10:20 | 9:50 | 9:10 | 8:45 |
| 35 | 12:03 | 11:00 | 10:05 | 9:35 | 8:56 | 8:31 |
| 36 | 11:47 | 10:45 | 9:51 | 9:21 | 8:42 | 8:18 |
| 37 | 11:32 | 10:31 | 9:37 | 9:07 | 8:29 | 8:05 |
| 38 | 11:17 | 10:17 | 9:24 | 8:54 | 8:17 | 7:53 |
| 39 | 11:04 | 10:05 | 9:12 | 8:42 | 8:05 | 7:42 |
| 40 | 10:51 | 9:53 | 9:00 | 8:30 | 7:54 | 7:31 |
| 41 | 10:39 | 9:42 | 8:49 | 8:19 | 7:44 | 7:21 |
| 42 | 10:27 | 9:31 | 8:38 | 8:08 | 7:33 | 7:11 |
| 43 | 10:16 | 9:21 | 8:28 | 7:58 | 7:24 | 7:01 |
| 44 | 10:05 | 9:11 | 8:18 | 7:48 | 7:14 | 6:52 |
| 45 | 9:55 | 9:01 | 8:09 | 7:39 | 7:05 | 6:44 |
| 46 | 9:45 | 8:52 | 8:00 | 7:30 | 6:57 | 6:36 |
| 47 | 9:36 | 8:43 | 7:51 | 7:21 | 6:49 | 6:28 |
| 48 | 9:27 | 8:35 | 7:43 | 7:13 | 6:41 | 6:20 |
| 49 | 9:18 | 8:27 | 7:35 | 7:05 | 6:33 | 6:13 |
| 50 | 9:10 | 8:19 | 7:27 | 6:57 | 6:26 | 6:06 |
| 51 | 9:02 | 8:12 | 7:20 | 6:50 | 6:19 | 5:59 |
| 52 | 8:54 | 8:05 | 7:13 | 6:43 | 6:13 | 5:53 |
| 53 | 8:47 | 7:58 | 7:06 | 6:36 | 6:06 | 5:47 |
| 54 | 8:40 | 7:51 | 6:59 | 6:30 | 6:00 | 5:41 |
| 55 | 8:33 | 7:45 | 6:53 | 6:24 | 5:54 | 5:35 |

> **Coaching Note:** Values derived from Daniels' VDOT model. For VDOT values between integers, interpolate linearly.

---

## 4. Heart Rate Alternatives When No Race Data Exists

### 4.1 Establishing HRmax

**Preferred methods (in order of reliability):**

1. **Recent 5K race or all-out time trial:** HRmax ≈ average HR in the final mile.
2. **Structured field test:** After a 10-minute warm-up, run 3 minutes hard, then sprint for 30 seconds. Peak HR recorded is a reliable HRmax estimate.
3. **Age-based formula (lowest reliability):** `HRmax = 208 − (0.7 × age)` (Tanaka formula, preferred over 220-age).

> **Coaching Note:** Age-based HRmax estimates carry ±10–15 bpm individual error. Treat HR-derived paces as provisional until validated by race effort.

### 4.2 Resting HR and Heart Rate Reserve (HRR)

`HRR = HRmax − HRrest`

Karvonen formula for target HR at a given intensity:
`Target HR = HRrest + (% intensity × HRR)`

### 4.3 HR-Based Pace Zones (Provisional)

| Zone | % HRmax | % HRR | Approximate Daniels Equivalent |
|------|---------|-------|-------------------------------|
| Zone 1 | <65% | <55% | Below E (recovery) |
| Zone 2 | 65–79% | 55–74% | E (Easy) |
| Zone 3 | 80–89% | 75–84% | M (Marathon) |
| Zone 4 | 88–92% | 84–88% | T (Threshold) |
| Zone 5 | 93–100% | 89–100% | I (Interval) |

> **HR does not capture R pace** — use pace and RPE exclusively for repetition work.

### 4.4 Transitioning from HR to VDOT

As soon as possible, assign a time trial:
- **Beginners:** 1-mile or 5K time trial after 4 weeks of base training.
- **Returning athletes:** A 5K effort-based run within the first 2 weeks.

### 4.5 Limitations of HR-Only Coaching

- HR is affected by sleep, stress, caffeine, heat, and dehydration — all unrelated to fitness.
- HR drift during long runs makes M/T pace difficult to assess.
- Athletes with cardiac conditions (beta-blockers, arrhythmia history) require physician clearance before using HR targets.

---

## 5. Environmental and Course Adjustments

### 5.1 Heat and Humidity

| Temperature (°F) | Adjustment |
|-----------------|------------|
| 60–65°F | No adjustment needed |
| 65–70°F | Slow all paces by 0–1.5% |
| 70–75°F | Slow all paces by 1.5–3% |
| 75–80°F | Slow all paces by 3–5% |
| 80°F+ | Slow all paces by 5–8%, consider effort-based running |
| 90°F+ | Use RPE and HR only; abandon pace targets |

**Humidity Adjustment:**
- Humidity above 40% begins to impair cooling; above 80% is equivalent to ~5°F additional temperature increase.
- Use the **Heat Index** (apparent temperature) when humidity is above 50%.

### 5.2 Altitude

| Elevation | Adjustment to I/T Pace | Adjustment to E/M Pace |
|-----------|------------------------|------------------------|
| <2,000 ft (610m) | No adjustment | No adjustment |
| 2,000–4,000 ft | Slow I/T by 3–5% | No adjustment |
| 4,000–6,000 ft | Slow I/T by 5–8% | Slow E/M by 2–3% |
| 6,000–8,000 ft | Slow I/T by 8–12% | Slow E/M by 4–6% |
| 8,000+ ft | Slow I/T by 12–20% | Slow E/M by 6–10% |

### 5.3 Hilly Courses

- Each 1% of uphill grade adds approximately 8–12 seconds per mile.
- Each 1% of downhill grade removes approximately 5–8 seconds per mile (diminishing benefit due to braking).

**Coaching recommendation:** For structured quality sessions (T, I, R), use a flat course or track. Reserve hilly routes for E and M paces.

---

## 6. Fully Worked Example

**Athlete profile:**
- First marathon: **5:02:00**
- Recent 5K time trial (two weeks ago): **28:30**

### Step 1: Calculate VDOT from the marathon

- Distance: 42195 m | Time: 302 minutes
- V = 42195 / 302 = 139.7 m/min
- O2 cost = −4.60 + (0.182258 × 139.7) + (0.000104 × 139.7²) = **22.89 ml/kg/min**
- %VO2max at 302 min ≈ **0.800** (both exponentials approach 0 at this duration)
- VDOT (marathon) = 22.89 / 0.800 = **28.6 → VDOT 29**

> **Coaching Note:** A 5-hour+ marathon yields a low VDOT because the fractional utilization denominator floors at ~80%. Long marathon times often underestimate true aerobic fitness for newer runners who lack marathon-specific preparation.

### Step 2: Calculate VDOT from the 5K time trial

- Distance: 5000 m | Time: 28.5 minutes
- V = 5000 / 28.5 = 175.44 m/min
- O2 cost = −4.60 + (0.182258 × 175.44) + (0.000104 × 175.44²) = **30.58 ml/kg/min**
- %VO2max at 28.5 min = 0.8 + 0.1894393 × 0.6957 + 0.2989558 × 0.00422 = **0.9330**
- VDOT (5K) = 30.58 / 0.9330 = **32.8 → VDOT 33**

### Step 3: Select the governing VDOT

**Use VDOT 33.** The 5K time trial is more recent and produces the higher VDOT. The marathon's lower VDOT reflects pacing inexperience, fueling issues, and underdeveloped race-specific fitness.

> For a first-time marathoner, the marathon time is a poor fitness indicator. Prioritize the 5K result.

### Step 4: Assign Training Paces (VDOT 33)

| Pace Zone | Target Pace | Notes |
|-----------|------------|-------|
| Easy (E) | 12:38–11:33 /mile | Use 12:00–12:30 for most runs |
| Marathon (M) | 10:36 /mile | Implies ~4:38 marathon if fully prepared |
| Threshold (T) | 10:06 /mile | Cruise intervals and tempo runs |
| Interval (I) | 9:25 /mile | Track repeats (1000m–1200m) |
| Repetition (R) | 9:00 /mile | 200m–400m fast repeats with full recovery |

### Step 5: Predicted race times at VDOT 33

| Race | Predicted Time |
|------|---------------|
| 5K | 29:36 |
| 10K | 1:01:21 |
| Half Marathon | 2:15:55 |
| Marathon | 4:44:47 |

> **Coaching Note:** The athlete's first marathon of 5:02 significantly underperforms the VDOT 33 prediction of 4:44. This is typical — first marathons carry a 5–15% time penalty from pacing errors, fueling inexperience, and underdeveloped race-specific fitness. A second marathon with proper preparation will close this gap substantially.

---

## 7. Handling Stale Race Data (Older Than 16 Weeks)

### 7.1 Definition of Stale

Race data older than **16 weeks (approximately 4 months)** is considered stale.

### 7.2 Staleness Factors and Adjustments

| Scenario | Recommended Action |
|----------|-------------------|
| Athlete has been training consistently | Assign a time trial; use stale VDOT conservatively (−2 points) as interim |
| Athlete had an injury layoff <4 weeks | Subtract 1 VDOT point per week of inactivity |
| Athlete had an injury layoff 4–8 weeks | Assume VDOT −4 to −6; build back before reassessing |
| Athlete had an injury layoff >8 weeks | Treat as new baseline; prescribe by HR/effort for 4 weeks |
| Athlete reports paces feeling "too easy" | Schedule time trial |
| Athlete reports paces feeling "too hard" | Reduce VDOT by 2 points; investigate training stress and sleep |

### 7.3 Detraining Rate

- **~5–7% per week** in the first 3 weeks of complete inactivity.
- **~1–3% per week** thereafter.
- Athletes who continued cross-training during a running layoff: apply a ~50% reduced penalty.

### 7.4 Conservative Interim Pacing Protocol

1. Subtract 2 VDOT points from the last known value.
2. Use HR and RPE to validate.
3. Explicitly flag all paces as "provisional."
4. Schedule a formal reassessment.

> **Coaching Note:** The cost of running too slow is modest (slight undertraining). The cost of running too fast (overtraining from inflated VDOT) is injury, burnout, and lost training weeks.

---

## 8. When to Reassess and How

### 8.1 Triggers for Reassessment

**Scheduled:**
- Every **10–12 weeks** for developing athletes.
- Every **16 weeks** for experienced athletes with stable fitness.

**Unscheduled triggers:**
- Race within the last 4 weeks (always update from race data)
- Athlete consistently finds training paces "too easy" for 2+ weeks
- Significant fatigue, paces feeling disproportionately hard
- After return from injury or illness
- After a significant training block increase (>20% mileage jump over 4 weeks)

### 8.2 Reassessment Methods (In Order of Preference)

1. **Race result (gold standard)** — any official race within the past 4 weeks
2. **5K time trial (preferred field test)** — 10-min easy warm-up, 4 × 100m strides, then race-effort 5K
3. **1-mile time trial** — for beginners or limited fitness

### 8.3 Updating VDOT After Reassessment

- New VDOT **higher**: Update immediately; adjust all training paces upward.
- New VDOT **lower**: Investigate before adjusting. Was the effort truly maximal? Were conditions poor? Is the athlete fatigued?

### 8.4 VDOT Update Policy

| Change in VDOT | Action |
|----------------|--------|
| +3 or more points | Immediate update; review training plan load |
| +1 to +2 points | Immediate update; paces adjust smoothly |
| No change | Confirm training is appropriate; consider different race distance |
| −1 to −2 points | Investigate; provisional reduction with follow-up test in 2 weeks |
| −3 or more points | Significant investigation required; medical factors ruled out |

---

## Appendix: Quick Reference Card

**To derive VDOT from a race:**
1. Convert time to minutes → calculate V (m/min) → calculate O2 cost → calculate %VO2max → divide.

**To assign paces:**
1. Look up VDOT in the pace table (Section 3).
2. Apply environmental adjustments (Section 5).
3. Confirm data is fresh (<16 weeks); if not, subtract 2 VDOT points (Section 7).

**To update VDOT:**
1. Reassess every 10–16 weeks or after any race (Section 8).
2. Always use the most recent, highest-VDOT result from valid data.
3. Flag all provisional paces clearly.
