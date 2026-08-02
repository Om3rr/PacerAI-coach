"""Tests for Garmin fact extraction (pure functions, no network)."""
from unittest.mock import patch
import pytest
from garminconnect import GarminConnectTooManyRequestsError
from pacerai.supabase_sync import (
    facts_from_activity,
    facts_from_sleep,
    facts_from_hrv,
    facts_from_stats,
    facts_from_body_battery,
    facts_from_training_status,
    facts_from_weight,
    _with_retry,
)


def _by_key(rows, metric_key):
    return next(r for r in rows if r["metric_key"] == metric_key)


class TestFactsFromActivity:
    def _make_activity(self, **overrides):
        base = {
            "activityId": 12345,
            "activityName": "Morning Run",
            "activityType": {"typeKey": "running"},
            "startTimeLocal": "2026-04-04 07:30:00",
            "distance": 10000.0,
            "duration": 3300.0,
            "averageHR": 145,
            "averageSpeed": 3.03,
            "calories": 520,
        }
        base.update(overrides)
        return base

    def test_fact_date(self):
        rows = facts_from_activity("omer", self._make_activity())
        assert all(r["fact_date"] == "2026-04-04" for r in rows)

    def test_source(self):
        rows = facts_from_activity("omer", self._make_activity())
        assert all(r["source"] == "activity" for r in rows)

    def test_source_id(self):
        rows = facts_from_activity("omer", self._make_activity())
        assert all(r["source_id"] == "12345" for r in rows)

    def test_distance_km_value(self):
        rows = facts_from_activity("omer", self._make_activity())
        assert _by_key(rows, "distance_km")["metric_value"] == 10.0

    def test_avg_hr_value(self):
        rows = facts_from_activity("omer", self._make_activity())
        assert _by_key(rows, "avg_hr")["metric_value"] == 145

    def test_activity_type_is_text(self):
        rows = facts_from_activity("omer", self._make_activity())
        row = _by_key(rows, "activity_type")
        assert row["metric_text"] == "running"
        assert row["metric_value"] is None

    def test_missing_start_time_returns_empty(self):
        a = self._make_activity()
        del a["startTimeLocal"]
        assert facts_from_activity("omer", a) == []

    def test_missing_optional_fields_omitted(self):
        rows = facts_from_activity("omer", {"activityId": 1, "startTimeLocal": "2026-01-01 00:00:00"})
        keys = {r["metric_key"] for r in rows}
        assert "avg_hr" not in keys
        assert "calories" not in keys


class TestFactsFromSleep:
    def test_extracts_duration(self):
        data = {"dailySleepDTO": {"sleepTimeSeconds": 25200}}
        rows = facts_from_sleep("omer", "2026-04-04", data)
        assert _by_key(rows, "duration_sec")["metric_value"] == 25200

    def test_extracts_overall_sleep_score(self):
        data = {"dailySleepDTO": {"sleepScores": {"overall": {"value": 82}}}}
        rows = facts_from_sleep("omer", "2026-04-04", data)
        assert _by_key(rows, "sleep_score")["metric_value"] == 82

    def test_empty_data_returns_empty(self):
        assert facts_from_sleep("omer", "2026-04-04", {}) == []

    def test_all_rows_tagged_with_date_and_source(self):
        data = {"dailySleepDTO": {"sleepTimeSeconds": 100}, "averageSpO2Value": 96}
        rows = facts_from_sleep("omer", "2026-04-04", data)
        assert all(r["fact_date"] == "2026-04-04" and r["source"] == "sleep" for r in rows)


class TestFactsFromHrv:
    def test_extracts_last_night_avg(self):
        data = {"hrvSummary": {"lastNightAvg": 51, "weeklyAvg": 54}}
        rows = facts_from_hrv("omer", "2026-08-02", data)
        assert _by_key(rows, "last_night_avg")["metric_value"] == 51

    def test_extracts_status_as_text(self):
        data = {"hrvSummary": {"status": "UNBALANCED"}}
        rows = facts_from_hrv("omer", "2026-08-02", data)
        row = _by_key(rows, "status")
        assert row["metric_text"] == "UNBALANCED"

    def test_empty_data_returns_empty(self):
        assert facts_from_hrv("omer", "2026-08-02", {}) == []


class TestFactsFromStats:
    def test_extracts_steps(self):
        data = {"totalSteps": 8123}
        rows = facts_from_stats("omer", "2026-04-04", data)
        assert _by_key(rows, "total_steps")["metric_value"] == 8123

    def test_zero_values_included(self):
        # 0 is a meaningful value (e.g. no stress data yet) and must not be dropped
        data = {"averageStressLevel": 0}
        rows = facts_from_stats("omer", "2026-04-04", data)
        assert _by_key(rows, "stress_avg")["metric_value"] == 0

    def test_none_values_omitted(self):
        rows = facts_from_stats("omer", "2026-04-04", {"totalSteps": None})
        assert not any(r["metric_key"] == "total_steps" for r in rows)


class TestFactsFromBodyBattery:
    def test_extracts_charged_and_drained(self):
        entry = {"date": "2026-08-01", "charged": 54, "drained": 87}
        rows = facts_from_body_battery("omer", entry)
        assert _by_key(rows, "charged")["metric_value"] == 54
        assert _by_key(rows, "drained")["metric_value"] == 87

    def test_missing_date_returns_empty(self):
        assert facts_from_body_battery("omer", {"charged": 1}) == []


class TestWithRetry:
    def test_returns_result_on_success(self):
        assert _with_retry(lambda: 42) == 42

    def test_retries_then_succeeds(self):
        calls = {"n": 0}

        def flaky():
            calls["n"] += 1
            if calls["n"] < 2:
                raise GarminConnectTooManyRequestsError("rate limited")
            return "ok"

        with patch("time.sleep"):
            assert _with_retry(flaky, retries=3, base_delay=0) == "ok"
        assert calls["n"] == 2

    def test_raises_after_exhausting_retries(self):
        def always_fails():
            raise GarminConnectTooManyRequestsError("rate limited")

        with patch("time.sleep"):
            with pytest.raises(GarminConnectTooManyRequestsError):
                _with_retry(always_fails, retries=2, base_delay=0)

    def test_non_rate_limit_error_propagates_immediately(self):
        def boom():
            raise ValueError("something else")

        with pytest.raises(ValueError):
            _with_retry(boom, retries=3, base_delay=0)


class TestFactsFromWeight:
    def test_extracts_weight_kg_from_grams(self):
        summary = {"summaryDate": "2026-08-01", "latestWeight": {"weight": 105800.0}}
        rows = facts_from_weight("omer", summary)
        assert _by_key(rows, "weight_kg")["metric_value"] == 105.8

    def test_extracts_bmi_and_body_fat_when_present(self):
        summary = {
            "summaryDate": "2026-08-01",
            "latestWeight": {"weight": 105800.0, "bmi": 28.7, "bodyFat": 22.1},
        }
        rows = facts_from_weight("omer", summary)
        assert _by_key(rows, "bmi")["metric_value"] == 28.7
        assert _by_key(rows, "body_fat_pct")["metric_value"] == 22.1

    def test_missing_weight_returns_empty(self):
        assert facts_from_weight("omer", {"summaryDate": "2026-08-01", "latestWeight": {}}) == []

    def test_missing_summary_date_returns_empty(self):
        assert facts_from_weight("omer", {"latestWeight": {"weight": 100000.0}}) == []


class TestFactsFromTrainingStatus:
    def test_extracts_vo2max(self):
        data = {"mostRecentVO2Max": {"generic": {"vo2MaxValue": 48.0}}}
        rows = facts_from_training_status("omer", "2026-08-01", data)
        assert _by_key(rows, "vo2max")["metric_value"] == 48.0

    def test_missing_vo2max_returns_empty(self):
        assert facts_from_training_status("omer", "2026-08-01", {}) == []
