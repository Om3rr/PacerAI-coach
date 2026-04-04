#!/usr/bin/env python3
"""
Pacerai — AI-friendly Garmin Connect CLI.

Every command outputs JSON: {"status":"ok","data":...} or {"status":"error","message":...}
Run with: poetry run pacerai <command> [options]
"""

import argparse
import json
import sys
from datetime import date, datetime
from pacerai.auth import get_garmin_client


# ─── Output helpers ────────────────────────────────────────────────────────────

def ok(data):
    print(json.dumps({"status": "ok", "data": data}, indent=2, default=str))

def err(msg, code=1):
    print(json.dumps({"status": "error", "message": msg}, indent=2))
    sys.exit(code)

def today() -> str:
    return date.today().isoformat()


# ─── Pace helpers ──────────────────────────────────────────────────────────────

def pace_to_ms(pace_min_km: float) -> float:
    """4.5 → 3.70 m/s  (4:30/km decimal → m/s)"""
    return 1000.0 / (pace_min_km * 60.0)

def ms_to_pace(ms: float) -> str:
    """3.70 m/s → '4:30' string."""
    if not ms or ms <= 0:
        return None
    total_secs = 1000.0 / ms
    m, s = divmod(int(total_secs), 60)
    return f"{m}:{s:02d}"


# ─── Activity projection ────────────────────────────────────────────────────────

def _slim_activity(a: dict) -> dict:
    avg_speed = a.get("averageSpeed") or 0
    return {
        "id": a.get("activityId"),
        "name": a.get("activityName"),
        "type": a.get("activityType", {}).get("typeKey"),
        "date": (a.get("startTimeLocal") or "")[:10],
        "distance_km": round((a.get("distance") or 0) / 1000, 2),
        "duration_min": round((a.get("duration") or 0) / 60, 1),
        "avg_hr": a.get("averageHR"),
        "avg_pace": ms_to_pace(avg_speed) if avg_speed else None,
        "calories": a.get("calories"),
    }


# ─── Workout JSON schema → Garmin API payload ──────────────────────────────────

SPORT_TYPES = {
    "running":          {"sportTypeId": 1,  "sportTypeKey": "running"},
    "cycling":          {"sportTypeId": 2,  "sportTypeKey": "cycling"},
    "swimming":         {"sportTypeId": 4,  "sportTypeKey": "swimming"},
    "strength":         {"sportTypeId": 5,  "sportTypeKey": "strength_training"},
    "walking":          {"sportTypeId": 9,  "sportTypeKey": "walking"},
    "hiking":           {"sportTypeId": 3,  "sportTypeKey": "hiking"},
}

STEP_TYPES = {
    "warmup":   {"stepTypeId": 1, "stepTypeKey": "warmup"},
    "cooldown": {"stepTypeId": 2, "stepTypeKey": "cooldown"},
    "interval": {"stepTypeId": 3, "stepTypeKey": "interval"},
    "recovery": {"stepTypeId": 4, "stepTypeKey": "recovery"},
    "rest":     {"stepTypeId": 5, "stepTypeKey": "rest"},
    "repeat":   {"stepTypeId": 6, "stepTypeKey": "repeat"},
    "active":   {"stepTypeId": 3, "stepTypeKey": "interval"},  # alias
}

CONDITION_TYPES = {
    "lap_button": {"conditionTypeId": 1, "conditionTypeKey": "lap.button"},
    "time":       {"conditionTypeId": 2, "conditionTypeKey": "time"},
    "distance":   {"conditionTypeId": 3, "conditionTypeKey": "distance"},
    "calories":   {"conditionTypeId": 4, "conditionTypeKey": "calories"},
    "iterations": {"conditionTypeId": 7, "conditionTypeKey": "iterations"},
    "reps":       {"conditionTypeId": 10, "conditionTypeKey": "reps"},
}

TARGET_TYPES = {
    "none":        {"workoutTargetTypeId": 1, "workoutTargetTypeKey": "no.target"},
    "heart_rate":  {"workoutTargetTypeId": 4, "workoutTargetTypeKey": "heart.rate.zone"},
    "pace":        {"workoutTargetTypeId": 6, "workoutTargetTypeKey": "pace.zone"},
    "cadence":     {"workoutTargetTypeId": 3, "workoutTargetTypeKey": "cadence.zone"},
    "power":       {"workoutTargetTypeId": 5, "workoutTargetTypeKey": "power.zone"},
}


def _build_condition(dur: dict) -> tuple:
    """Returns (condition_dict, value). value is None for lap_button."""
    t = dur.get("type", "lap_button")
    cond = CONDITION_TYPES.get(t)
    if cond is None:
        raise ValueError(f"Unknown duration type '{t}'. Valid: {list(CONDITION_TYPES)}")
    value = None
    if t == "time":
        value = dur["seconds"]
    elif t == "distance":
        value = dur["meters"]
    elif t in ("reps", "calories"):
        value = dur.get("value") or dur.get("reps") or dur.get("calories")
    return cond, value


def _build_target(tgt: dict) -> tuple:
    """Returns (target_type_dict, val_one, val_two)."""
    t = tgt.get("type", "none")
    tt = TARGET_TYPES.get(t)
    if tt is None:
        raise ValueError(f"Unknown target type '{t}'. Valid: {list(TARGET_TYPES)}")
    v1, v2 = None, None
    if t == "heart_rate":
        v1 = tgt["min"]
        v2 = tgt["max"]
    elif t == "pace":
        # pace min/km decimal (e.g. 4.5 = 4:30/km). Garmin wants faster=lower value first.
        # NOTE: Garmin stores pace as m/s; lower m/s = slower pace.
        # targetValueOne should be the FASTER pace (higher m/s = lower min/km value)
        fast_min_km = tgt.get("min_km") or tgt.get("fast_min_km")  # faster (lower number)
        slow_min_km = tgt.get("max_km") or tgt.get("slow_min_km")  # slower (higher number)
        if fast_min_km and slow_min_km:
            v1 = pace_to_ms(fast_min_km)   # faster → higher m/s
            v2 = pace_to_ms(slow_min_km)   # slower → lower m/s
    elif t in ("cadence", "power"):
        v1 = tgt.get("min")
        v2 = tgt.get("max")
    return tt, v1, v2


def _build_steps(steps: list, order_start: int = 1) -> list:
    """Recursively convert step schema to Garmin API step dicts."""
    result = []
    order = order_start
    for s in steps:
        if s["type"] == "repeat":
            iterations = s["iterations"]
            inner = _build_steps(s["steps"], order_start=1)
            result.append({
                "type": "RepeatGroupDTO",
                "stepOrder": order,
                "stepType": STEP_TYPES["repeat"],
                "numberOfIterations": iterations,
                "endCondition": CONDITION_TYPES["iterations"],
                "endConditionValue": iterations,
                "workoutSteps": inner,
            })
            order += 1
        elif s["type"] == "step":
            kind = s.get("step_type", "interval")
            st = STEP_TYPES.get(kind)
            if st is None:
                raise ValueError(f"Unknown step_type '{kind}'. Valid: {list(STEP_TYPES)}")
            cond, cond_val = _build_condition(s.get("duration", {"type": "lap_button"}))
            tt, v1, v2 = _build_target(s.get("target", {"type": "none"}))
            step_dict = {
                "type": "ExecutableStepDTO",
                "stepOrder": order,
                "stepType": st,
                "endCondition": cond,
                "endConditionValue": cond_val,
                "targetType": tt,
                "targetValueOne": v1,
                "targetValueTwo": v2,
            }
            # Strength exercise category (optional)
            if "exercise" in s:
                step_dict["exerciseCategory"] = {
                    "exerciseCategoryId": None,
                    "exerciseCategoryName": s["exercise"].upper(),
                }
            result.append(step_dict)
            order += 1
        else:
            raise ValueError(f"Unknown step type '{s['type']}'. Must be 'step' or 'repeat'.")
    return result


def build_workout_payload(schema: dict) -> dict:
    """Convert simple workout schema dict to Garmin API payload."""
    name = schema.get("name", "Workout")
    sport_key = schema.get("sport", "running").lower()
    sport = SPORT_TYPES.get(sport_key)
    if sport is None:
        raise ValueError(f"Unknown sport '{sport_key}'. Valid: {list(SPORT_TYPES)}")

    steps = _build_steps(schema.get("steps", []))
    return {
        "workoutName": name,
        "sportType": sport,
        "workoutSegments": [{
            "segmentOrder": 1,
            "sportType": sport,
            "workoutSteps": steps,
        }],
    }


def load_workout_input(raw: str) -> dict:
    """Parse workout input: JSON string or @filename."""
    if raw.startswith("@"):
        path = raw[1:]
        try:
            with open(path) as f:
                return json.load(f)
        except FileNotFoundError:
            err(f"File not found: {path}")
        except json.JSONDecodeError as e:
            err(f"Invalid JSON in {path}: {e}")
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        err(f"Invalid JSON: {e}. Use a valid JSON string or @filepath.")


# ─── Command handlers ──────────────────────────────────────────────────────────

def cmd_activities(args):
    garmin = get_garmin_client(args.user)
    if args.start_date or args.end_date:
        start = args.start_date or today()
        end = args.end_date or today()
        activities = garmin.get_activities_by_date(start, end, args.type)
    else:
        activities = garmin.get_activities(start=args.offset, limit=args.limit, activitytype=args.type)
    data = activities if args.full else [_slim_activity(a) for a in activities]
    ok(data)


def cmd_activity(args):
    garmin = get_garmin_client(args.user)
    activity = garmin.get_activity(args.id)
    if args.full:
        ok(activity)
    else:
        ok(_slim_activity(activity))


def cmd_delete_activity(args):
    garmin = get_garmin_client(args.user)
    result = garmin.delete_activity(args.id)
    ok({"deleted_id": args.id, "result": result})


def cmd_create_activity(args):
    """Create a manual activity (for logging past runs without a device)."""
    garmin = get_garmin_client(args.user)
    result = garmin.create_manual_activity(
        start_datetime=args.start,    # ISO 8601, e.g. "2026-03-25T07:00:00"
        time_zone=args.timezone,      # e.g. "Asia/Jerusalem"
        type_key=args.type,           # e.g. "running", "cycling"
        distance_km=args.distance_km,
        duration_min=args.duration_min,
        activity_name=args.name,
    )
    ok(result)


def cmd_rename_activity(args):
    garmin = get_garmin_client(args.user)
    result = garmin.set_activity_name(args.id, args.name)
    ok({"id": args.id, "new_name": args.name, "result": result})


# ─── Workout library ────────────────────────────────────────────────────────────

def cmd_workouts(args):
    garmin = get_garmin_client(args.user)
    workouts = garmin.get_workouts(start=args.offset, limit=args.limit)
    if args.full:
        ok(workouts)
    else:
        ok([{
            "id": w.get("workoutId"),
            "name": w.get("workoutName"),
            "sport": w.get("sportType", {}).get("sportTypeKey"),
            "updated": (w.get("updateDate") or "")[:10],
        } for w in workouts])


def cmd_workout(args):
    garmin = get_garmin_client(args.user)
    ok(garmin.get_workout_by_id(args.id))


def cmd_create_workout(args):
    """Create a workout from a JSON schema string or @filepath.

    Schema format:
    {
      "name": "Easy Run 65min",
      "sport": "running",
      "steps": [
        {"type":"step","step_type":"warmup","duration":{"type":"time","seconds":600},
         "target":{"type":"heart_rate","min":120,"max":150}},
        {"type":"repeat","iterations":3,"steps":[
          {"type":"step","step_type":"interval","duration":{"type":"time","seconds":480},
           "target":{"type":"pace","min_km":4.48,"max_km":4.65}},
          {"type":"step","step_type":"recovery","duration":{"type":"time","seconds":180},
           "target":{"type":"heart_rate","min":120,"max":148}}
        ]},
        {"type":"step","step_type":"cooldown","duration":{"type":"time","seconds":900},
         "target":{"type":"heart_rate","min":120,"max":150}}
      ]
    }

    Pace note: min_km is decimal minutes. 4.5 = 4:30/km, 5.083 = 5:05/km.
               min_km = faster bound (lower number), max_km = slower bound.
    Duration types: time (seconds), distance (meters), lap_button, reps
    Target types: none, heart_rate (min/max bpm), pace (min_km/max_km)
    Step types: warmup, cooldown, interval, recovery, rest
    Sports: running, cycling, swimming, strength, walking, hiking
    """
    schema = load_workout_input(args.json)
    try:
        payload = build_workout_payload(schema)
    except ValueError as e:
        err(str(e))

    if args.dry_run:
        ok({"dry_run": True, "payload": payload})
        return

    garmin = get_garmin_client(args.user)
    result = garmin.upload_workout(payload)
    ok({"workout_id": result.get("workoutId"), "name": payload["workoutName"], "result": result})


def cmd_delete_workout(args):
    garmin = get_garmin_client(args.user)
    garmin.garth.delete(
        "connectapi",
        f"/workout-service/workout/{args.id}",
        api=True,
    )
    ok({"deleted_id": args.id})


# ─── Scheduling ────────────────────────────────────────────────────────────────

def cmd_schedule(args):
    garmin = get_garmin_client(args.user)
    result = garmin.schedule_workout(args.workout_id, args.date)
    ok({"workout_id": args.workout_id, "date": args.date, "schedule_id": result.get("scheduleId"), "result": result})


def cmd_unschedule(args):
    garmin = get_garmin_client(args.user)
    garmin.garth.delete(
        "connectapi",
        f"/workout-service/schedule/{args.schedule_id}",
        api=True,
    )
    ok({"deleted_schedule_id": args.schedule_id})


def cmd_scheduled(args):
    """List scheduled workouts in a date range (uses calendar service)."""
    from datetime import date as date_cls
    garmin = get_garmin_client(args.user)
    start_str = args.start or today()
    end_str = args.end or today()
    start_d = date_cls.fromisoformat(start_str)
    end_d = date_cls.fromisoformat(end_str)

    # Fetch each month in range (calendar service is month-based)
    all_items = []
    seen_months = set()
    cur = start_d.replace(day=1)
    while cur <= end_d:
        key = (cur.year, cur.month)
        if key not in seen_months:
            seen_months.add(key)
            try:
                result = garmin.garth.get(
                    "connectapi",
                    f"/calendar-service/year/{cur.year}/month/{cur.month}",
                    api=True,
                ).json()
                all_items.extend(result.get("calendarItems", []))
            except Exception:
                pass  # month not available (too far future or no data)
        # advance to next month
        if cur.month == 12:
            cur = cur.replace(year=cur.year + 1, month=1)
        else:
            cur = cur.replace(month=cur.month + 1)

    # Filter to scheduled workouts in the date range
    workouts = [
        i for i in all_items
        if i.get("itemType") == "workout"
        and start_str <= (i.get("date") or "") <= end_str
    ]

    if args.full:
        ok(workouts)
    else:
        ok([{
            "schedule_id": i.get("id"),
            "workout_id": i.get("workoutId"),
            "name": i.get("title"),
            "date": i.get("date"),
            "sport": i.get("sportTypeKey"),
        } for i in workouts])


# ─── User metrics ──────────────────────────────────────────────────────────────

def cmd_stats(args):
    cdate = args.date or today()
    garmin = get_garmin_client(args.user)
    stats = garmin.get_stats(cdate)
    if args.full:
        ok(stats)
    else:
        ok({
            "date": cdate,
            "total_steps": stats.get("totalSteps"),
            "total_distance_m": stats.get("totalDistanceMeters"),
            "active_calories": stats.get("activeKilocalories"),
            "resting_calories": stats.get("bmrKilocalories"),
            "avg_hr": stats.get("averageHeartRate"),
            "resting_hr": stats.get("restingHeartRate"),
            "min_hr": stats.get("minHeartRate"),
            "max_hr": stats.get("maxHeartRate"),
            "stress_avg": stats.get("averageStressLevel"),
            "body_battery_charged": stats.get("bodyBatteryChargedValue"),
            "body_battery_drained": stats.get("bodyBatteryDrainedValue"),
        })


def cmd_summary(args):
    cdate = args.date or today()
    garmin = get_garmin_client(args.user)
    ok(garmin.get_user_summary(cdate))


def cmd_hr(args):
    cdate = args.date or today()
    garmin = get_garmin_client(args.user)
    data = garmin.get_heart_rates(cdate)
    if args.full:
        ok(data)
    else:
        ok({
            "date": cdate,
            "resting_hr": data.get("restingHeartRate"),
            "min_hr": data.get("minHeartRate"),
            "max_hr": data.get("maxHeartRate"),
            "last_7_days_avg": data.get("lastSevenDaysAvgRestingHeartRate"),
        })


def cmd_sleep(args):
    cdate = args.date or today()
    garmin = get_garmin_client(args.user)
    data = garmin.get_sleep_data(cdate)
    if args.full:
        ok(data)
    else:
        daily = data.get("dailySleepDTO", {})
        ok({
            "date": cdate,
            "duration_sec": daily.get("sleepTimeSeconds"),
            "deep_sec": daily.get("deepSleepSeconds"),
            "light_sec": daily.get("lightSleepSeconds"),
            "rem_sec": daily.get("remSleepSeconds"),
            "awake_sec": daily.get("awakeSleepSeconds"),
            "sleep_score": daily.get("sleepScores", {}).get("overall", {}).get("value") if isinstance(daily.get("sleepScores"), dict) else daily.get("sleepScores"),
            "avg_spo2": data.get("averageSpO2Value"),
        })


def cmd_weight(args):
    start = args.start or today()
    end = args.end or today()
    garmin = get_garmin_client(args.user)
    ok(garmin.get_weigh_ins(start, end))


def cmd_training_status(args):
    cdate = args.date or today()
    garmin = get_garmin_client(args.user)
    ok(garmin.get_training_status(cdate))


def cmd_hrv(args):
    cdate = args.date or today()
    garmin = get_garmin_client(args.user)
    ok(garmin.get_hrv_data(cdate))


def cmd_body_battery(args):
    start = args.start or today()
    end = args.end or today()
    garmin = get_garmin_client(args.user)
    ok(garmin.get_body_battery(start, end))


def cmd_race_predictions(args):
    garmin = get_garmin_client(args.user)
    data = garmin.get_race_predictions()
    if args.full:
        ok(data)
    else:
        preds = data if isinstance(data, list) else [data]
        ok([{
            "distance": p.get("raceDistance") or p.get("distance"),
            "predicted_time": p.get("predictedTime") or p.get("time"),
            "pace_per_km": p.get("paceInMinutesPerKilometer"),
        } for p in preds if p])


def cmd_personal_records(args):
    garmin = get_garmin_client(args.user)
    ok(garmin.get_personal_record())


def cmd_login(args):
    """Open a local browser login form, authenticate, and save tokens to Keychain."""
    from pacerai import keychain as kc
    if kc.exists(args.user) and not args.force:
        ok({"user": args.user, "message": "Already logged in (tokens in Keychain). Use --force to re-authenticate."})
        return
    from pacerai import login_server
    success = login_server.run(args.user)
    if success:
        ok({"user": args.user, "message": "Login successful. Tokens saved to Keychain."})
    else:
        err(f"Login failed or timed out for user '{args.user}'.")


def cmd_logout(args):
    """Remove tokens from Keychain."""
    from pacerai import keychain as kc
    kc.delete(args.user)
    ok({"user": args.user, "message": "Tokens removed from Keychain."})


# ─── Arg parser ────────────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="pacerai",
        description="Pacerai — Garmin Connect CLI. All output is JSON.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--user", "-u", default="omer",
                   help="Garmin user profile name (default: omer). Known profiles: omer, yuval, rami. New profiles are created on first login.")

    sub = p.add_subparsers(dest="command", required=True, title="commands")

    # ── activities ──
    sp = sub.add_parser("activities", help="List recent activities")
    sp.add_argument("--limit", "-n", type=int, default=10)
    sp.add_argument("--offset", type=int, default=0)
    sp.add_argument("--type", "-t", help="Activity type key, e.g. running, cycling, strength_training")
    sp.add_argument("--start-date", "--start", help="YYYY-MM-DD filter start")
    sp.add_argument("--end-date", "--end", help="YYYY-MM-DD filter end")
    sp.add_argument("--full", action="store_true", help="Return full raw API response")
    sp.set_defaults(func=cmd_activities)

    sp = sub.add_parser("activity", help="Get a single activity")
    sp.add_argument("id", help="Activity ID")
    sp.add_argument("--full", action="store_true")
    sp.set_defaults(func=cmd_activity)

    sp = sub.add_parser("delete-activity", help="Delete an activity")
    sp.add_argument("id", help="Activity ID")
    sp.set_defaults(func=cmd_delete_activity)

    sp = sub.add_parser("create-activity", help="Log a manual activity")
    sp.add_argument("--start", required=True, help="Start datetime ISO 8601, e.g. 2026-03-25T07:00:00")
    sp.add_argument("--timezone", default="Asia/Jerusalem", help="IANA timezone")
    sp.add_argument("--type", required=True, help="Activity type key, e.g. running")
    sp.add_argument("--distance-km", type=float, required=True)
    sp.add_argument("--duration-min", type=int, required=True)
    sp.add_argument("--name", required=True, help="Activity name")
    sp.set_defaults(func=cmd_create_activity)

    sp = sub.add_parser("rename-activity", help="Rename an activity")
    sp.add_argument("id", help="Activity ID")
    sp.add_argument("name", help="New activity name")
    sp.set_defaults(func=cmd_rename_activity)

    # ── workout library ──
    sp = sub.add_parser("workouts", help="List workout library")
    sp.add_argument("--limit", "-n", type=int, default=50)
    sp.add_argument("--offset", type=int, default=0)
    sp.add_argument("--full", action="store_true")
    sp.set_defaults(func=cmd_workouts)

    sp = sub.add_parser("workout", help="Get a single workout from library")
    sp.add_argument("id", help="Workout ID")
    sp.set_defaults(func=cmd_workout)

    sp = sub.add_parser("create-workout", help="Create a workout from JSON schema")
    sp.add_argument("json", metavar="JSON_OR_FILE",
                    help='JSON string or @filepath. See --help for schema.')
    sp.add_argument("--dry-run", action="store_true",
                    help="Print payload without uploading")
    sp.set_defaults(func=cmd_create_workout)
    sp.__doc__ = cmd_create_workout.__doc__

    sp = sub.add_parser("delete-workout", help="Delete a workout from library")
    sp.add_argument("id", help="Workout ID")
    sp.set_defaults(func=cmd_delete_workout)

    # ── scheduling ──
    sp = sub.add_parser("schedule", help="Schedule a library workout on a date")
    sp.add_argument("workout_id", help="Workout ID")
    sp.add_argument("date", help="Date YYYY-MM-DD")
    sp.set_defaults(func=cmd_schedule)

    sp = sub.add_parser("unschedule", help="Remove a scheduled workout")
    sp.add_argument("schedule_id", help="Schedule ID (from 'scheduled' command)")
    sp.set_defaults(func=cmd_unschedule)

    sp = sub.add_parser("scheduled", help="List scheduled workouts in a date range")
    sp.add_argument("--start", help="YYYY-MM-DD (default: today)")
    sp.add_argument("--end", help="YYYY-MM-DD (default: today)")
    sp.add_argument("--full", action="store_true")
    sp.set_defaults(func=cmd_scheduled)

    # ── user metrics ──
    sp = sub.add_parser("stats", help="Daily stats summary (steps, HR, calories, stress, body battery)")
    sp.add_argument("--date", "-d", help="YYYY-MM-DD (default: today)")
    sp.add_argument("--full", action="store_true")
    sp.set_defaults(func=cmd_stats)

    sp = sub.add_parser("summary", help="Full daily user summary")
    sp.add_argument("--date", "-d", help="YYYY-MM-DD (default: today)")
    sp.set_defaults(func=cmd_summary)

    sp = sub.add_parser("hr", help="Heart rate data for a day")
    sp.add_argument("--date", "-d", help="YYYY-MM-DD (default: today)")
    sp.add_argument("--full", action="store_true", help="Include full HR timeline")
    sp.set_defaults(func=cmd_hr)

    sp = sub.add_parser("sleep", help="Sleep data for a night")
    sp.add_argument("--date", "-d", help="YYYY-MM-DD (default: today)")
    sp.add_argument("--full", action="store_true")
    sp.set_defaults(func=cmd_sleep)

    sp = sub.add_parser("weight", help="Weigh-in data for a date range")
    sp.add_argument("--start", help="YYYY-MM-DD (default: today)")
    sp.add_argument("--end", help="YYYY-MM-DD (default: today)")
    sp.set_defaults(func=cmd_weight)

    sp = sub.add_parser("training-status", help="Training status and load")
    sp.add_argument("--date", "-d", help="YYYY-MM-DD (default: today)")
    sp.set_defaults(func=cmd_training_status)

    sp = sub.add_parser("hrv", help="HRV data for a night")
    sp.add_argument("--date", "-d", help="YYYY-MM-DD (default: today)")
    sp.set_defaults(func=cmd_hrv)

    sp = sub.add_parser("body-battery", help="Body battery data for a date range")
    sp.add_argument("--start", help="YYYY-MM-DD (default: today)")
    sp.add_argument("--end", help="YYYY-MM-DD (default: today)")
    sp.set_defaults(func=cmd_body_battery)

    sp = sub.add_parser("race-predictions", help="Garmin race time predictions")
    sp.add_argument("--full", action="store_true")
    sp.set_defaults(func=cmd_race_predictions)

    sp = sub.add_parser("personal-records", help="Personal records")
    sp.set_defaults(func=cmd_personal_records)

    # ── auth ──
    sp = sub.add_parser("login", help="Open browser login form and save tokens to Keychain")
    sp.add_argument("--force", action="store_true", help="Re-authenticate even if tokens exist")
    sp.set_defaults(func=cmd_login)

    sp = sub.add_parser("logout", help="Remove tokens from Keychain")
    sp.set_defaults(func=cmd_logout)

    return p


# ─── Entry point ───────────────────────────────────────────────────────────────

def main():
    parser = build_parser()
    args = parser.parse_args()
    try:
        args.func(args)
    except Exception as e:
        err(f"{type(e).__name__}: {e}")


if __name__ == "__main__":
    main()
