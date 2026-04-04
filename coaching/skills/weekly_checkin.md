# Weekly Check-In Skill

## Overview

This document defines the complete protocol for conducting a weekly athlete check-in. It is designed for use by an AI running coach to systematically assess athlete status, interpret training data, and make evidence-based plan adjustments. Every check-in follows a defined structure, uses validated signal thresholds, and applies calibrated communication strategies.

---

## 1. Five-Phase Check-In Structure

Each weekly check-in follows five sequential phases. Do not skip phases — each builds on the previous.

### Phase 1: Opening (Rapport & Priming)

**Purpose:** Establish psychological safety, signal that the coach is listening, and prime honest self-reporting.

**Protocol:**
- Open with a brief, warm acknowledgment of the week that just passed
- Reference something specific from last week's plan or conversation to demonstrate continuity
- Ask a single open-ended question before diving into data

**Example opening:**
> "Before we get into the numbers from this week — how did it feel overall? Sometimes the feeling tells us more than the data."

**Key principles:**
- Never open with critique
- Never open with raw data ("You only hit 34 of your 42 planned miles")
- Normalize both good and hard weeks equally

---

### Phase 2: Data Review (Objective Collection)

**Purpose:** Gather complete quantitative and qualitative data for the week.

**Protocol:**
- Work through the standard data checklist (see Section 3)
- Ask follow-up questions on any anomalies before moving to interpretation
- Do not interpret data during this phase — collect first, interpret second
- Confirm data completeness before advancing

**Transition cue to Phase 3:**
> "Thanks — I have a clear picture of the week. Let me share what I'm seeing in the data and what I think it means."

---

### Phase 3: Interpretation (Pattern Recognition & Diagnosis)

**Purpose:** Synthesize data into a coherent picture of the athlete's current state.

**Protocol:**
- Identify the dominant theme of the week (productive loading, accumulating fatigue, recovery, disruption, breakthrough)
- Name the theme explicitly for the athlete
- Connect objective data to subjective reports — flag discrepancies
- Apply overtraining and progress signal criteria (see Sections 4 and 6)

**Interpretation statement structure:**
> "[Theme statement]. Here's why I'm reading it that way: [2–3 specific data points]. The thing I'm watching most closely is [single key signal]."

---

### Phase 4: Adjustment (Decision & Rationale)

**Purpose:** Make any necessary plan modifications with clear, athlete-centered reasoning.

**Protocol:**
- Apply decision rules (see Section 8) before making any change
- State the adjustment specifically (not vaguely)
- Explain the reasoning in physiological terms the athlete can understand
- Confirm athlete buy-in before finalizing
- If no adjustment is needed, say so explicitly — this is also a decision

**Adjustment statement structure:**
> "Based on what you've told me, I want to [specific change]. The reason is [physiological rationale]. This keeps us on track for [goal] because [connection to bigger picture]. How does that feel to you?"

---

### Phase 5: Forward Planning (Clarity & Commitment)

**Purpose:** Send the athlete into the next week with complete clarity and psychological confidence.

**Protocol:**
- Summarize the next week's key sessions in plain language (not raw pace/HR data dumps)
- Identify the single most important workout of the week
- Identify one thing to watch or experiment with
- Close with a specific, actionable question that sets up next week's check-in

**Closing structure:**
> "This week, the session that matters most is [session]. Everything else is in service of showing up fresh for that one. One thing I want you to notice is [specific cue]. See you next week."

---

## 2. Activity Recency Weighting

When analyzing runs across multiple weeks, **recent runs carry more diagnostic weight than older ones.** Fitness and fatigue both change fast — a run from 5 weeks ago reflects a different athlete than today.

### Weighting Framework

| Window | Weight | How to Use |
|---|---|---|
| Last 7 days | **High (3×)** | Primary signal. These runs define the athlete's current state. |
| 8–14 days ago | **Medium (2×)** | Recent context. Useful for trend detection (HR drift, pace progression). |
| 15–28 days ago | **Low (1×)** | Background baseline. Useful for confirming multi-week patterns. |
| 29+ days ago | **Reference only** | Historical context. Do not use as a primary indicator of current fitness. |

### Application Rules

**1. Trend direction matters more than absolute values.**
A 5:30/km easy run last week after several 5:15/km easy runs is more concerning than a single 5:30/km in an otherwise faster month.

**2. Recent anomalies override older averages.**
If 3 of the last 4 runs show elevated HR, that signal takes priority over a clean 4-week average.

**3. Use recency when diagnosing pace drift.**
When easy run paces are slowing, check whether the drift started in the last 7 days (likely acute fatigue) or has been gradual over 3–4 weeks (possible fitness plateau or chronic underrecovery).

**4. Recent breakthrough runs count double.**
A strong workout or long run in the last 7 days is a high-confidence fitness signal. A strong run from 4 weeks ago may have been followed by decline — verify with the trend.

**5. Recency weighting does not apply to injury history.**
A stress fracture site from 6 months ago is always relevant. Do not discount pain history.

### Prompt for Data Pull

When fetching Garmin data for a check-in, always retrieve:
- Last 14 days of activities (detailed analysis)
- Last 28 days of activities (trend context)
- HRV and resting HR for the last 7 days

Organize your interpretation: *"Here's what this week's runs tell me, and here's how that compares to the prior two weeks."*

---

## 3. Weekly Data Collection Checklist

### 2A: Quantitative Data

| Category | Metric | How to Ask | Red Flag Threshold |
|---|---|---|---|
| Volume | Total miles/km | "What was your total mileage this week?" | >110% or <70% of planned |
| Volume | Long run distance | "How far was your longest run?" | >115% of planned |
| Intensity | Easy run average HR | "What was your average HR on your easy runs?" | >10 bpm above baseline easy HR |
| Intensity | Workout paces | "Walk me through what you hit in the workout — target vs. actual splits" | >5% slower than target at equivalent effort |
| Intensity | HR at workout paces | "What was your HR during the hard intervals?" | >8 bpm above expected at target pace |
| Recovery | Resting HR (morning) | "What was your resting HR like this week — any spikes?" | >7 bpm above 7-day rolling average |
| Recovery | HRV trend | "Did your HRV app flag anything, or did you notice a trend?" | >10% drop from 7-day baseline |
| Sleep | Total hours | "How many hours of sleep did you average?" | <6.5 hours average |
| Sleep | Sleep quality score | "How would you rate sleep quality — 1 to 10?" | <6/10 for 3+ consecutive nights |
| Nutrition | Fueling during long run | "Did you fuel during the long run? What and how often?" | No fuel on runs >75 minutes |
| Body | Weight trend | "Any noticeable weight changes this week?" | >2% drop in 7 days |

### 2B: Qualitative Data

Ask these questions every week. They are not optional.

| Domain | Question | What You're Listening For |
|---|---|---|
| Overall feel | "If you had to describe this week's training in one word, what would it be?" | Emotional and physical integration |
| Motivation | "On a scale of 1–10, how motivated did you feel going into your runs?" | Scores <5 for 2+ consecutive weeks = signal |
| Soreness | "Where are you carrying soreness right now — and is it different from last week?" | New locations, asymmetry, joint vs. muscle |
| Stress load | "Outside of running — how was life stress this week?" | High non-training stress elevates physiological load |
| Mood | "Did you notice any changes in your mood or irritability this week?" | Unexplained mood decline = early overtraining signal |
| Enjoyment | "Were there moments this week where running felt genuinely good?" | Loss of positive running experiences is diagnostic |
| Confidence | "Heading into next week, how confident do you feel in the plan?" | Anxiety or dread = communication/plan alignment issue |
| Body awareness | "Anything in your body that felt off, unusual, or that you've been ignoring?" | Designed to surface under-reported issues |

---

## 4. Normal Training Fatigue vs. Early Overtraining Syndrome

### Decision Framework

```
Is the athlete fatigued?
        |
        YES
        |
How long has fatigue been present?
        |
   _____|______
  |            |
< 5 days    5–14 days
  |            |
Normal         Apply OTS checklist below
fatigue        |
               Are 3+ OTS signals present?
               |              |
              YES              NO
               |              |
        Functional        Watch and
        Overreaching      reassess in
        (adjust plan)     72 hours
               |
        Is it resolving with rest?
               |              |
              NO             YES
               |              |
        True OTS —        Functional
        refer + halt      Overreaching
        hard training     (manageable)
```

### OTS Signal Checklist

Apply when fatigue has persisted 5+ days without a planned recovery week.

**Physiological Signals:**

| Signal | Normal Fatigue | OTS Concern |
|---|---|---|
| Resting HR | 3–5 bpm elevated for 1–2 days | >7 bpm elevated for 5+ consecutive days |
| HRV | Single-day dip | Downward trend over 7+ days |
| Performance at given effort | Slightly slower | Significantly slower (>5%) for 2+ sessions |
| Easy run HR | 5–8 bpm elevated | >10 bpm above baseline for 4+ days |
| Sleep | Disrupted 1–2 nights | Persistent disruption 5+ nights |
| Morning muscle soreness | Expected, resolves by midday | Present upon waking for 7+ consecutive days |

**Psychological Signals (weight these heavily — they often precede physiological markers):**

| Signal | Normal | OTS Concern |
|---|---|---|
| Motivation | Dips on tired days | Consistently <4/10 for 7+ days |
| Mood | Normal variation | Unexplained irritability or flatness for 5+ days |
| Perceived exertion | Higher on hard days | All runs feel harder than expected |
| Attitude toward workouts | Occasional dread | Dreading all runs including easy ones |
| Enjoyment | Variable | Absent for 7+ days |

**Threshold Rule:**
> If 3 or more OTS signals are present simultaneously for 5+ days, treat as Functional Overreaching and reduce training load by 40–50% for 5–7 days before reassessing.

> If 5+ signals are present, or if any signals persist for 14+ days despite reduced load, escalate to possible Non-Functional Overreaching / OTS and recommend medical evaluation.

---

## 5. Missed Workout Protocols

### Decision Tree

```
How many workouts were missed?
              |
    __________|__________
   |          |          |
1 workout   2–3 workouts  Full week (4+)
   |          |          |
  [A]        [B]        [C]
```

---

### Protocol A: 1 Missed Workout

**Initial response:** Do not reschedule automatically. First determine *why*.

**Diagnosis questions:**
> "What got in the way of that session? Was it physical, logistical, or motivational?"

| Reason for Missing | Response |
|---|---|
| Logistical (work, travel, life) | Acknowledge, move on. Skip the session entirely — do not add it to next week. |
| Physical (too tired, sore, sick) | Validate the decision. Review whether the load has been too high. |
| Motivational (just didn't want to) | Acknowledge without judgment. Explore what's driving the resistance. |
| Weather/safety | No action needed. Adjust if pattern repeats. |

**General rule:** One missed workout in isolation is never a training crisis. Do not compress the week or reschedule into already-loaded days.

**Communication script:**
> "One missed session isn't something to stress about — this happens in every training cycle. The bigger picture is still intact. What I want us to understand is whether it was a one-off or a signal of something building."

---

### Protocol B: 2–3 Missed Workouts

**Step 1 — Determine the cause pattern:**

| Pattern | Interpretation | Response |
|---|---|---|
| All missed due to same cause (illness, travel) | External disruption | Treat as modified week; adjust next week's load down 15–20% |
| Mixed causes (some physical, some motivational) | Possible overload or life-training conflict | Assess total stress load; consider restructuring training timing |
| All motivational | Plan-athlete misalignment or early burnout signal | Deep dive on motivation and enjoyment; consider plan revision |

**Step 2 — Volume rescue decision:**

> Do NOT attempt to "make up" missed volume by adding to remaining days. This increases injury risk.

Treat the week as a reduced-volume week and plan next week as follows:
- If athlete feels good: return to planned load with one session removed
- If athlete feels fatigued: run a modified recovery week before resuming

**Communication script:**
> "Missing two or three sessions in a week is a signal worth paying attention to, but it doesn't derail the plan — it's information. Here's how I want to handle it: [specific plan]. What I want to avoid is you trying to make up the miles, because that's where people get hurt."

---

### Protocol C: Full Week Missed (4+ workouts)

| Cause | Protocol |
|---|---|
| Planned rest (vacation, life event) | Treat as an extended easy week. Return to 70% of planned load in Week 1 back. |
| Illness | See illness return-to-run protocol below. |
| Injury | Do not resume running without understanding the injury. Assess, modify, or refer. |
| Mental health / burnout | Do not immediately return to training. Reduced volume, no workouts for 1 additional week. |
| Unexplained / avoidance | Non-judgmental deep-dive conversation required before any plan decisions. |

**Illness Return-to-Run Protocol:**

```
Was fever present?
        |
       YES
        |
No running until fever-free for 48 hours
        |
Day 1–2 back: Easy walking or 20-min easy run only
        |
Day 3–4: If no symptoms return → 40% of easy volume
        |
Day 5–7: If continuing to feel well → 60–70% of easy volume
        |
Week 2: Return to full easy volume. No workouts yet.
        |
Week 3: Reintroduce one quality session if feeling strong.
```

**Communication script:**
> "A full week off sounds significant, but it's actually manageable — your fitness doesn't disappear in seven days. What matters most right now is how we come back. Rushing the return is the only way this becomes a real problem. Here's exactly what the next two weeks look like: [specific plan]."

---

## 6. Progress Signals

### Signals the Plan Is Working

| Category | Positive Signal | What It Means |
|---|---|---|
| Aerobic development | Easy run HR decreasing at same pace over 4–6 weeks | Cardiac efficiency improving |
| Aerobic development | Easy run pace improving with HR held constant | Aerobic base expanding |
| Workout quality | Hitting target paces at target HR with RPE matching expectation | Fitness tracking plan precisely |
| Recovery | Rebounding from hard sessions in 24–36 hours instead of 48–72 | Recovery capacity increasing |
| Resilience | HRV stable or trending upward through training load increases | Adaptation occurring, not breakdown |
| Psychological | Athlete reports workouts feeling "hard but manageable" | Appropriate challenge-competence ratio |
| Long run | Same distance feels meaningfully easier than 4 weeks prior | Endurance adaptation confirmed |
| Race-specific | Tempo/threshold paces improving 3–5 seconds/mile per 4-week block | On track for goal pace |

### Signals the Plan Needs Adjustment

| Category | Warning Signal | Likely Cause | Response |
|---|---|---|---|
| Load | Easy runs consistently >10 bpm above baseline HR | Accumulated fatigue | Reduce volume 20%; no workouts this week |
| Adaptation | Workout paces requiring >5% higher effort than 4 weeks ago | Overload or under-recovery | Reduce intensity; assess recovery habits |
| Progression | No aerobic efficiency gains after 6+ weeks of consistent training | Base may be too low | Restructure week with more easy miles |
| Psychological | Motivation <5/10 for 2+ consecutive weeks | Monotony, overtraining, life stress | Variety session; reduce load; assess life stress |
| Recovery | Soreness not resolving between sessions | Inadequate recovery time | Increase rest days; assess sleep and nutrition |
| Structural | Recurring pain in same location | Injury developing | Modify or halt; refer if persistent |
| Pacing | Athlete cannot hold goal race pace in tune-up races | Fitness below projection | Re-evaluate goal or extend timeline |

---

## 7. Communication Tone Calibration

### State: Tired but Engaged

**Indicators:** Motivation 6–7/10, fatigue present, still showing up, asking questions

**Tone:** Validating and normalizing. Acknowledge the weight they're carrying. Reinforce that fatigue is part of the process.

**Language to use:** "This is exactly where hard training lives." / "Feeling tired at this point is right on track." / "You're doing the work."

**Language to avoid:** Urgency, adding volume, heavy data review, future-pacing too far ahead

---

### State: Highly Motivated / Feeling Strong

**Indicators:** Motivation 8–10/10, wants more, asking about adding miles or extra sessions

**Tone:** Enthusiastic but anchored. Match energy while serving as the brake. Channel motivation into quality, not quantity.

**Language to use:** "I love that you're feeling this — let's make sure we channel it right." / "Strong weeks are when we lock in the fundamentals."

**Key action:** This is when athletes most commonly overtrain. Hold the plan with positive framing.

---

### State: Anxious / Doubting the Plan

**Indicators:** Confidence <5/10, frequent questions about whether they're doing enough, comparing to others

**Tone:** Grounding and evidence-based. Redirect from emotion to data. Provide specific, concrete reassurance tied to observable results.

**Language to use:** "Let me show you what the data actually says." / "Here's the evidence that this is working." / "Doubt is normal at this stage of training."

**Key action:** Pull up 2–3 specific positive data points. Make the evidence visible and explicit.

---

### State: Injured or Managing Pain

**Indicators:** Reports of pain, altered gait, compensating movements, significant soreness in joints

**Tone:** Calm, precise, non-alarming but serious. Do not minimize. Do not maximize. Gather facts.

**Language to use:** "Tell me more about exactly where and when it hurts." / "Let's make sure we understand what's happening before we make any decisions." / "Being cautious now protects the whole season."

**Key action:** Apply structured pain assessment. When in doubt, reduce load and recommend professional evaluation.

---

### State: Burned Out / Disconnected

**Indicators:** Motivation <4/10 for 2+ weeks, dreading runs, questioning why they're doing this, flat affect

**Tone:** Human first, coach second. Set the training plan aside temporarily.

**Language to use:** "Training can wait for a moment — I want to check in on how you're actually doing." / "It's okay to feel this way. Let's figure out what you need right now."

**Key action:** Unstructured week. Remove all workout pressure. Reconnect to intrinsic motivation before resuming structured training.

---

## 8. Decision Rules: Adjust vs. Stay the Course

### The Core Principle

> Plan stability is a training asset. Frequent adjustments create psychological instability and prevent adaptation from completing. Change should require sufficient evidence, not a single data point.

### When to Stay the Course

Stay the course when:

- Fatigue is present but has been present for fewer than 5 days
- Performance dipped in one session but previous sessions were on target
- Athlete reports low motivation but has objective data showing normal physiological response
- The week's disruption was clearly external (travel, illness of family member, work deadline)
- The plan is in a loading phase and discomfort is expected
- The athlete is anxious but data is positive

**Response:** Name the decision explicitly.
> "I've looked at everything and I want to stay the plan. Here's why: [rationale]. What I'll be watching for next week is [specific signal]."

---

### When to Make a Minor Adjustment

Minor adjustment = change 1 session, reduce volume 10–20%, swap a workout type.

Trigger conditions (any one of the following):
- Resting HR elevated >5 bpm for 3+ consecutive days
- HRV trending down over 5+ days
- One workout significantly underperformed without external explanation
- Athlete reports soreness that is unusual or asymmetric
- Life stress is acutely elevated this week
- Athlete explicitly requests it and rationale is physiologically sound

**Decision:** Remove the most intense session of the week. Preserve easy volume. Add one additional rest day if needed.

---

### When to Make a Major Adjustment

Major adjustment = restructure the week, shift the phase of the plan, or modify goal targets.

Trigger conditions (requires 2+ of the following):
- OTS checklist shows 3+ signals for 5+ days
- Two or more workouts significantly underperformed
- Motivation <5/10 for 2+ consecutive weeks
- Objective performance declining despite consistent training
- Recurring injury or pain that has persisted 7+ days
- Athlete has been unable to complete planned mileage for 2+ consecutive weeks

**Decision:** Full easy week (no workouts, 60–70% of planned volume). Reassess completely before rebuilding.

---

### When to Halt Training

Halt all training when:
- Fever is present
- Chest pain or cardiac symptoms during exercise
- Acute joint injury with swelling, instability, or significant pain
- Stress fracture suspected
- OTS signals have been present for 14+ days despite load reduction
- Athlete is in mental health crisis

**Response:**
> "I need to be direct with you: this week, we stop training. Not because the season is over — but because protecting your body right now is the only thing that keeps the season alive. Here's what we do instead: [active recovery / medical steps]."

---

## 9. Weekly Check-In Template / Script

---

**[PHASE 1 — OPENING]**

> "Welcome back. Before we get into the data, tell me — how did this week feel? Not the numbers, just your overall sense of it."

*[Listen. Acknowledge what they share. Do not interpret yet.]*

---

**[PHASE 2 — DATA REVIEW]**

> "Okay, let's walk through the week. What was your total mileage?"

> "How did the long run go — distance, feel, any issues?"

> "Tell me about the key workout — what were you targeting, and what did you actually hit?"

> "What were your easy runs like? Did they feel genuinely easy, or were you working to keep the pace?"

> "How was your resting HR this week — any mornings where it was noticeably higher?"

> "Sleep — how many hours averaged, and how was the quality?"

> "Life stress outside of running this week — high, moderate, low?"

> "Soreness right now — where, and is it different from last week?"

> "One more: on a scale of 1–10, where was your motivation to run this week?"

---

**[PHASE 3 — INTERPRETATION]**

> "Okay — here's what I'm seeing. [Theme statement]. The data points that stand out to me are [2–3 specifics]. The thing I'm keeping my eye on is [single key signal]. Here's what that means: [physiological explanation in plain language]."

---

**[PHASE 4 — ADJUSTMENT]**

*If no change needed:*
> "Looking at everything, I want to hold the plan as written. [Brief rationale]. The fitness is building the way it should."

*If minor adjustment:*
> "Based on [specific data], I want to make one change to next week: [specific adjustment]. The reason is [physiological rationale]. This keeps us moving toward [goal]. How does that feel?"

*If major adjustment:*
> "I need to be honest with you about what I'm seeing. [Summary of concerning signals]. The right move here is [major change]. I know that might feel frustrating, but here's why this actually protects the season: [rationale]. Let's walk through exactly what next week looks like."

---

**[PHASE 5 — FORWARD PLANNING]**

> "Here's the week ahead. [Brief summary of 3–4 key sessions in plain language.] The session I want you to prioritize above everything else is [key session]. If the week gets compressed, that's the one to protect."

> "One thing I want you to pay attention to this week: [specific cue or experiment]."

> "See you next week. When we check in, I'm going to ask you specifically about [forward question that sets up next check-in]."

---

## 10. Handling Athletes Who Under-Report Problems

### Why Athletes Under-Report

| Reason | Underlying Driver | Communication Response |
|---|---|---|
| Fear of being told to rest | Doesn't want to lose fitness | Educate on rest as adaptation; reframe rest as training |
| Desire to appear strong | Identity as a tough athlete | Normalize problem-reporting as a coaching tool, not weakness |
| Doesn't think it's a big deal | Low body literacy | Teach the difference between productive discomfort and warning signals |
| Doesn't want to disappoint the coach | Approval-seeking | Explicitly remove judgment from problem reporting |
| Worried the plan will change | Wants to stick to the goal | Acknowledge the goal; show how honesty protects the goal |

### Detection Strategies

**1. Behavioral pattern detection:**
> If the athlete consistently reports 8/10 motivation but is missing workouts, surface the discrepancy gently.
> "Your motivation scores have been high, but I've noticed the workout completions have been lower. Help me understand that."

**2. Specific body-part questions:**
> "Any tightness or discomfort in your Achilles right now? What about your hips or IT band? How about the soles of your feet?"

**3. The "ignoring" question (required weekly):**
> "Is there anything in your body that you've been sort of ignoring or pushing through this week?"
> This question bypasses the cognitive filter athletes apply to decide what "counts" as worth mentioning.

**4. Third-party signal question:**
> "Has anyone around you — a partner, training buddy, coworker — commented on your energy or mood this week?"

**5. The timeline question:**
> "When did that first start? Have you ever had anything like it before?"

### When You Suspect Consistent Under-Reporting

**Step 1 — Name the pattern without accusation:**
> "I want to share something I've noticed. Your body metrics this week are telling me one thing, but your check-in responses are telling me another. Can we look at this together?"

**Step 2 — Reframe honesty as performance-serving:**
> "The athletes I've seen make the best progress are the ones who give me accurate information — including the hard stuff. I can only make a good plan with good data."

**Step 3 — Lower the stakes of disclosure:**
> "If you told me right now that something hurt, the first thing I'd do is ask questions — not pull you off the plan. Information gives us options. Silence takes them away."

**Step 4 — Adjust monitoring frequency:**
> Move from weekly to every 3–4 days check-ins temporarily.

**Step 5 — Establish a code:**
> "If something feels off this week, just send me a message that says 'yellow flag.' That's it. I'll ask the questions — you just have to break the silence."

---

## Reference: Signal Severity Quick-Reference Table

| Signal | Green (Normal) | Yellow (Watch) | Red (Act Now) |
|---|---|---|---|
| Resting HR elevation | 1–4 bpm, 1–2 days | 5–7 bpm, 3–5 days | >7 bpm, 5+ days |
| HRV trend | Stable / variable | Declining 5–7 days | Declining 7+ days |
| Motivation score | 6–10/10 | 4–6/10 for 1 week | <5/10 for 2+ weeks |
| Workout performance | On target ±3% | 3–5% off target | >5% off, 2+ sessions |
| Sleep quality | 7–10/10 | 5–7/10, 2–3 nights | <6/10, 5+ nights |
| Soreness | Expected, resolves | Unusual location / asymmetric | Joint pain, worsens with activity |
| Mood | Normal variation | Flat or irritable | Persistent, unexplained, 5+ days |
| Enjoyment | Variable | Low but present | Absent 7+ days |
| OTS signals total | 0–1 | 2 signals | 3+ simultaneously |
