"""Tests for activity projection helper."""
import pytest
from pacerai.cli import _slim_activity


class TestSlimActivity:
    def _make_activity(self, **overrides):
        base = {
            "activityId": "12345",
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

    def test_id(self):
        assert _slim_activity(self._make_activity())["id"] == "12345"

    def test_name(self):
        assert _slim_activity(self._make_activity())["name"] == "Morning Run"

    def test_type(self):
        assert _slim_activity(self._make_activity())["type"] == "running"

    def test_date_truncated(self):
        assert _slim_activity(self._make_activity())["date"] == "2026-04-04"

    def test_distance_km(self):
        result = _slim_activity(self._make_activity(distance=10000.0))
        assert result["distance_km"] == 10.0

    def test_distance_rounded(self):
        result = _slim_activity(self._make_activity(distance=10123.456))
        assert result["distance_km"] == 10.12

    def test_duration_min(self):
        result = _slim_activity(self._make_activity(duration=3600.0))
        assert result["duration_min"] == 60.0

    def test_avg_hr(self):
        assert _slim_activity(self._make_activity())["avg_hr"] == 145

    def test_avg_pace_present(self):
        result = _slim_activity(self._make_activity(averageSpeed=3.33))
        assert result["avg_pace"] is not None

    def test_calories(self):
        assert _slim_activity(self._make_activity())["calories"] == 520

    def test_missing_fields_default_to_none_or_zero(self):
        result = _slim_activity({})
        assert result["id"] is None
        assert result["distance_km"] == 0.0
        assert result["avg_pace"] is None
        assert result["avg_hr"] is None

    def test_zero_speed_gives_none_pace(self):
        result = _slim_activity(self._make_activity(averageSpeed=0))
        assert result["avg_pace"] is None

    def test_type_missing_activity_type(self):
        a = self._make_activity()
        del a["activityType"]
        result = _slim_activity(a)
        assert result["type"] is None
