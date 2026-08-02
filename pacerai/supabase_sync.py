"""Sync Garmin facts + coaching notes to Supabase.

Two concerns kept separate:
  - `facts_from_*` / `sync_facts`: pure code, no AI. Safe to run unattended.
  - `push_coaching_note` / `read_coaching_notes`: storage for AI-authored
    interpretations. The AI work happens elsewhere (e.g. Claude in a chat
    session) — this module just persists/retrieves the text.

Rows are sparse (user, date, source, metric_key, metric_value/text) so new
metric types never require a schema migration.
"""
import os
import time
from datetime import date, timedelta

import requests
from dotenv import load_dotenv
from garminconnect import GarminConnectTooManyRequestsError

from pacerai.auth import get_garmin_client, persist_token

load_dotenv()


def _with_retry(fn, *args, retries=3, base_delay=20, **kwargs):
    """Retry on Garmin 429s with exponential backoff (20s, 40s, 80s)."""
    for attempt in range(retries):
        try:
            return fn(*args, **kwargs)
        except GarminConnectTooManyRequestsError:
            if attempt == retries - 1:
                raise
            time.sleep(base_delay * (2 ** attempt))


def _env() -> tuple[str, str]:
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_KEY")
    if not url or not key:
        raise RuntimeError(
            "SUPABASE_URL and SUPABASE_SERVICE_KEY must be set (in .env or the environment)."
        )
    return url.rstrip("/"), key


def _headers(key: str, prefer: str | None = None) -> dict:
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }
    if prefer:
        headers["Prefer"] = prefer
    return headers


def _upsert(table: str, rows: list[dict], on_conflict: str) -> list[dict]:
    if not rows:
        return []
    url, key = _env()
    resp = requests.post(
        f"{url}/rest/v1/{table}?on_conflict={on_conflict}",
        headers=_headers(key, prefer="resolution=merge-duplicates,return=representation"),
        json=rows,
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def _insert(table: str, row: dict) -> dict:
    url, key = _env()
    resp = requests.post(
        f"{url}/rest/v1/{table}",
        headers=_headers(key, prefer="return=representation"),
        json=row,
        timeout=30,
    )
    resp.raise_for_status()
    result = resp.json()
    return result[0] if isinstance(result, list) else result


def _select(table: str, params: dict) -> list[dict]:
    url, key = _env()
    resp = requests.get(
        f"{url}/rest/v1/{table}",
        headers=_headers(key),
        params=params,
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


# ─── Fact extraction (pure, no network) ─────────────────────────────────────

def _row(user, fact_date, source, metric_key, *, source_id="", value=None, text=None, metadata=None):
    # source_id defaults to "" rather than None: Postgres unique constraints
    # never consider two NULLs equal, so NULL source_id would break upsert
    # dedup for every source that has no natural id (sleep, hrv, stats, ...).
    return {
        "user_name": user,
        "fact_date": fact_date,
        "source": source,
        "source_id": source_id,
        "metric_key": metric_key,
        "metric_value": value,
        "metric_text": text,
        "metadata": metadata,
    }


def facts_from_activity(user: str, a: dict) -> list[dict]:
    fact_date = (a.get("startTimeLocal") or "")[:10]
    if not fact_date:
        return []
    source_id = str(a.get("activityId")) if a.get("activityId") is not None else None
    avg_speed = a.get("averageSpeed") or 0
    numeric = {
        "distance_km": round((a.get("distance") or 0) / 1000, 2),
        "duration_min": round((a.get("duration") or 0) / 60, 1),
        "avg_hr": a.get("averageHR"),
        "avg_speed_ms": avg_speed or None,
        "calories": a.get("calories"),
    }
    rows = [
        _row(user, fact_date, "activity", k, source_id=source_id, value=v)
        for k, v in numeric.items()
        if v is not None
    ]
    text_fields = {
        "activity_type": (a.get("activityType") or {}).get("typeKey"),
        "activity_name": a.get("activityName"),
    }
    rows += [
        _row(user, fact_date, "activity", k, source_id=source_id, text=v)
        for k, v in text_fields.items()
        if v
    ]
    return rows


def facts_from_sleep(user: str, fact_date: str, data: dict) -> list[dict]:
    daily = data.get("dailySleepDTO") or {}
    numeric = {
        "duration_sec": daily.get("sleepTimeSeconds"),
        "deep_sec": daily.get("deepSleepSeconds"),
        "light_sec": daily.get("lightSleepSeconds"),
        "rem_sec": daily.get("remSleepSeconds"),
        "awake_sec": daily.get("awakeSleepSeconds"),
        "avg_spo2": data.get("averageSpO2Value"),
    }
    scores = daily.get("sleepScores")
    if isinstance(scores, dict):
        overall = (scores.get("overall") or {}).get("value")
        if overall is not None:
            numeric["sleep_score"] = overall
    return [
        _row(user, fact_date, "sleep", k, value=v)
        for k, v in numeric.items()
        if v is not None
    ]


def facts_from_hrv(user: str, fact_date: str, data: dict) -> list[dict]:
    summary = data.get("hrvSummary") or {}
    numeric = {
        "last_night_avg": summary.get("lastNightAvg"),
        "weekly_avg": summary.get("weeklyAvg"),
        "last_night_5min_high": summary.get("lastNight5MinHigh"),
    }
    rows = [
        _row(user, fact_date, "hrv", k, value=v)
        for k, v in numeric.items()
        if v is not None
    ]
    if summary.get("status"):
        rows.append(_row(user, fact_date, "hrv", "status", text=summary["status"]))
    return rows


def facts_from_stats(user: str, fact_date: str, data: dict) -> list[dict]:
    numeric = {
        "total_steps": data.get("totalSteps"),
        "total_distance_m": data.get("totalDistanceMeters"),
        "active_calories": data.get("activeKilocalories"),
        "resting_calories": data.get("bmrKilocalories"),
        "avg_hr": data.get("averageHeartRate"),
        "resting_hr": data.get("restingHeartRate"),
        "stress_avg": data.get("averageStressLevel"),
        "body_battery_charged": data.get("bodyBatteryChargedValue"),
        "body_battery_drained": data.get("bodyBatteryDrainedValue"),
    }
    return [
        _row(user, fact_date, "stats", k, value=v)
        for k, v in numeric.items()
        if v is not None
    ]


def facts_from_body_battery(user: str, entry: dict) -> list[dict]:
    fact_date = entry.get("date")
    if not fact_date:
        return []
    numeric = {"charged": entry.get("charged"), "drained": entry.get("drained")}
    return [
        _row(user, fact_date, "body_battery", k, value=v)
        for k, v in numeric.items()
        if v is not None
    ]


def facts_from_weight(user: str, summary: dict) -> list[dict]:
    fact_date = summary.get("summaryDate")
    latest = summary.get("latestWeight") or {}
    if not fact_date or latest.get("weight") is None:
        return []
    numeric = {
        "weight_kg": round(latest["weight"] / 1000, 2),
        "bmi": latest.get("bmi"),
        "body_fat_pct": latest.get("bodyFat"),
    }
    return [
        _row(user, fact_date, "weight", k, value=v)
        for k, v in numeric.items()
        if v is not None
    ]


def facts_from_training_status(user: str, fact_date: str, data: dict) -> list[dict]:
    vo2max = ((data.get("mostRecentVO2Max") or {}).get("generic") or {})
    rows = []
    if vo2max.get("vo2MaxValue") is not None:
        rows.append(_row(user, fact_date, "training_status", "vo2max", value=vo2max["vo2MaxValue"]))
    return rows


# ─── Orchestration ───────────────────────────────────────────────────────────

def _date_range(days: int) -> list[str]:
    today = date.today()
    return [(today - timedelta(days=i)).isoformat() for i in range(days)]


def sync_facts(user: str, days: int = 7) -> list[dict]:
    """Fetch recent Garmin data and flatten it into fact rows. No AI, no writes."""
    garmin = get_garmin_client(user)
    dates = _date_range(days)
    start, end = dates[-1], dates[0]

    rows: list[dict] = []

    for a in _with_retry(garmin.get_activities_by_date, start, end):
        rows += facts_from_activity(user, a)

    for d in dates:
        try:
            rows += facts_from_sleep(user, d, _with_retry(garmin.get_sleep_data, d))
        except Exception:
            pass
        try:
            rows += facts_from_hrv(user, d, _with_retry(garmin.get_hrv_data, d))
        except Exception:
            pass
        try:
            rows += facts_from_stats(user, d, _with_retry(garmin.get_stats, d))
        except Exception:
            pass
        try:
            rows += facts_from_training_status(user, d, _with_retry(garmin.get_training_status, d))
        except Exception:
            pass

    try:
        for entry in _with_retry(garmin.get_body_battery, start, end):
            rows += facts_from_body_battery(user, entry)
    except Exception:
        pass

    try:
        weigh_ins = _with_retry(garmin.get_weigh_ins, start, end)
        for summary in (weigh_ins or {}).get("dailyWeightSummaries", []):
            rows += facts_from_weight(user, summary)
    except Exception:
        pass

    persist_token(user, garmin)
    return rows


def push_facts(rows: list[dict]) -> int:
    _upsert("garmin_facts", rows, on_conflict="user_name,fact_date,source,source_id,metric_key")
    return len(rows)


def last_synced_date(user: str) -> str | None:
    """Most recent fact_date synced for this user, or None if never synced."""
    rows = _select("garmin_facts", {
        "user_name": f"eq.{user}",
        "order": "fact_date.desc",
        "limit": "1",
        "select": "fact_date",
    })
    return rows[0]["fact_date"] if rows else None


def read_facts(user: str, start: str, end: str, source: str | None = None) -> list[dict]:
    params = {
        "user_name": f"eq.{user}",
        "fact_date": [f"gte.{start}", f"lte.{end}"],
        "order": "fact_date.asc,source.asc,metric_key.asc",
    }
    if source:
        params["source"] = f"eq.{source}"
    return _select("garmin_facts", params)


def push_coaching_note(
    user: str,
    note_date: str,
    body: str,
    *,
    period_start: str | None = None,
    period_end: str | None = None,
    title: str | None = None,
    tags: list[str] | None = None,
    status: str = "final",
    generated_by: str = "claude-interactive",
) -> dict:
    row = {
        "user_name": user,
        "note_date": note_date,
        "period_start": period_start,
        "period_end": period_end,
        "title": title,
        "body": body,
        "tags": tags,
        "status": status,
        "generated_by": generated_by,
    }
    return _insert("coaching_notes", row)


def read_coaching_notes(user: str, start: str, end: str) -> list[dict]:
    params = {
        "user_name": f"eq.{user}",
        "note_date": [f"gte.{start}", f"lte.{end}"],
        "order": "note_date.asc",
    }
    return _select("coaching_notes", params)
