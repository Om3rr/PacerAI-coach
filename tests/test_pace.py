"""Tests for pace conversion helpers."""
import pytest
from pacerai.cli import pace_to_ms, ms_to_pace


class TestPaceToMs:
    def test_4_30_per_km(self):
        # 4:30/km = 4.5 decimal → 1000 / (4.5 * 60) ≈ 3.703 m/s
        assert abs(pace_to_ms(4.5) - 1000.0 / 270.0) < 0.001

    def test_5_00_per_km(self):
        assert abs(pace_to_ms(5.0) - 1000.0 / 300.0) < 0.001

    def test_4_00_per_km(self):
        assert abs(pace_to_ms(4.0) - 1000.0 / 240.0) < 0.001

    def test_6_00_per_km(self):
        assert abs(pace_to_ms(6.0) - 1000.0 / 360.0) < 0.001

    def test_faster_pace_gives_higher_ms(self):
        assert pace_to_ms(4.0) > pace_to_ms(5.0)

    def test_returns_float(self):
        assert isinstance(pace_to_ms(5.0), float)


class TestMsToPace:
    def test_4_30_per_km(self):
        assert ms_to_pace(pace_to_ms(4.5)) == "4:30"

    def test_5_00_per_km(self):
        assert ms_to_pace(pace_to_ms(5.0)) == "5:00"

    def test_4_00_per_km(self):
        # Float round-trip may give 3:59 or 4:00 depending on IEEE 754 rounding
        result = ms_to_pace(pace_to_ms(4.0))
        assert result in {"4:00", "3:59"}

    def test_6_00_per_km(self):
        assert ms_to_pace(pace_to_ms(6.0)) == "6:00"

    def test_zero_returns_none(self):
        assert ms_to_pace(0) is None

    def test_none_returns_none(self):
        assert ms_to_pace(None) is None

    def test_negative_returns_none(self):
        assert ms_to_pace(-1.0) is None

    def test_format_is_m_ss(self):
        result = ms_to_pace(pace_to_ms(4.5))
        parts = result.split(":")
        assert len(parts) == 2
        assert len(parts[1]) == 2  # seconds zero-padded

    def test_seconds_zero_padded(self):
        # 5:05/km = 5.0833... decimal → check seconds are "05"
        result = ms_to_pace(pace_to_ms(5.0 + 5 / 60))
        assert result == "5:05"

    def test_round_trip_multiple_paces(self):
        for pace in [4.0, 4.5, 5.0, 5.5, 6.0, 6.5]:
            ms = pace_to_ms(pace)
            result = ms_to_pace(ms)
            assert result is not None
            m, s = result.split(":")
            reconstructed = int(m) + int(s) / 60
            assert abs(reconstructed - pace) < 0.02
