"""Tests for workout schema → Garmin API payload builder."""
import json
import pytest
from pacerai.cli import (
    _build_condition,
    _build_target,
    _build_steps,
    build_workout_payload,
    load_workout_input,
    pace_to_ms,
    CONDITION_TYPES,
    TARGET_TYPES,
    SPORT_TYPES,
    STEP_TYPES,
)


class TestBuildCondition:
    def test_time(self):
        cond, val = _build_condition({"type": "time", "seconds": 300})
        assert cond["conditionTypeId"] == 2
        assert cond["conditionTypeKey"] == "time"
        assert val == 300

    def test_distance(self):
        cond, val = _build_condition({"type": "distance", "meters": 1000})
        assert cond["conditionTypeId"] == 3
        assert val == 1000

    def test_lap_button(self):
        cond, val = _build_condition({"type": "lap_button"})
        assert cond["conditionTypeId"] == 1
        assert val is None

    def test_default_type_is_lap_button(self):
        cond, val = _build_condition({})
        assert cond["conditionTypeKey"] == "lap.button"
        assert val is None

    def test_reps(self):
        cond, val = _build_condition({"type": "reps", "reps": 12})
        assert cond["conditionTypeId"] == 10
        assert val == 12

    def test_calories(self):
        cond, val = _build_condition({"type": "calories", "calories": 200})
        assert cond["conditionTypeId"] == 4
        assert val == 200

    def test_iterations(self):
        cond, val = _build_condition({"type": "iterations"})
        assert cond["conditionTypeId"] == 7

    def test_unknown_type_raises(self):
        with pytest.raises(ValueError, match="Unknown duration type"):
            _build_condition({"type": "invalid"})


class TestBuildTarget:
    def test_none(self):
        tt, v1, v2 = _build_target({"type": "none"})
        assert tt["workoutTargetTypeId"] == 1
        assert v1 is None
        assert v2 is None

    def test_default_is_none(self):
        tt, v1, v2 = _build_target({})
        assert tt["workoutTargetTypeKey"] == "no.target"

    def test_heart_rate(self):
        tt, v1, v2 = _build_target({"type": "heart_rate", "min": 130, "max": 155})
        assert tt["workoutTargetTypeId"] == 4
        assert v1 == 130
        assert v2 == 155

    def test_pace_min_max_km(self):
        tt, v1, v2 = _build_target({"type": "pace", "min_km": 4.5, "max_km": 5.0})
        assert tt["workoutTargetTypeId"] == 6
        assert abs(v1 - pace_to_ms(4.5)) < 0.001  # faster = higher m/s
        assert abs(v2 - pace_to_ms(5.0)) < 0.001  # slower = lower m/s
        assert v1 > v2  # faster pace has higher m/s value

    def test_pace_fast_slow_aliases(self):
        tt, v1, v2 = _build_target({"type": "pace", "fast_min_km": 4.5, "slow_min_km": 5.0})
        assert abs(v1 - pace_to_ms(4.5)) < 0.001
        assert abs(v2 - pace_to_ms(5.0)) < 0.001

    def test_cadence(self):
        tt, v1, v2 = _build_target({"type": "cadence", "min": 170, "max": 180})
        assert tt["workoutTargetTypeId"] == 3
        assert v1 == 170
        assert v2 == 180

    def test_power(self):
        tt, v1, v2 = _build_target({"type": "power", "min": 200, "max": 250})
        assert tt["workoutTargetTypeId"] == 5
        assert v1 == 200
        assert v2 == 250

    def test_unknown_type_raises(self):
        with pytest.raises(ValueError, match="Unknown target type"):
            _build_target({"type": "magic"})


class TestBuildSteps:
    def test_single_warmup_step(self):
        steps = _build_steps([
            {
                "type": "step",
                "step_type": "warmup",
                "duration": {"type": "time", "seconds": 300},
                "target": {"type": "heart_rate", "min": 120, "max": 145},
            }
        ])
        assert len(steps) == 1
        s = steps[0]
        assert s["type"] == "ExecutableStepDTO"
        assert s["stepOrder"] == 1
        assert s["stepType"]["stepTypeId"] == 1  # warmup
        assert s["endConditionValue"] == 300
        assert s["targetValueOne"] == 120
        assert s["targetValueTwo"] == 145

    def test_repeat_group(self):
        steps = _build_steps([
            {
                "type": "repeat",
                "iterations": 3,
                "steps": [
                    {
                        "type": "step",
                        "step_type": "interval",
                        "duration": {"type": "time", "seconds": 60},
                        "target": {"type": "none"},
                    }
                ],
            }
        ])
        assert len(steps) == 1
        r = steps[0]
        assert r["type"] == "RepeatGroupDTO"
        assert r["numberOfIterations"] == 3
        assert r["stepOrder"] == 1
        assert len(r["workoutSteps"]) == 1
        assert r["workoutSteps"][0]["stepType"]["stepTypeKey"] == "interval"

    def test_step_order_increments(self):
        steps = _build_steps([
            {"type": "step", "step_type": "warmup", "duration": {"type": "lap_button"}, "target": {"type": "none"}},
            {"type": "step", "step_type": "interval", "duration": {"type": "lap_button"}, "target": {"type": "none"}},
            {"type": "step", "step_type": "cooldown", "duration": {"type": "lap_button"}, "target": {"type": "none"}},
        ])
        assert [s["stepOrder"] for s in steps] == [1, 2, 3]

    def test_order_start_param(self):
        steps = _build_steps([
            {"type": "step", "step_type": "interval", "duration": {"type": "lap_button"}, "target": {"type": "none"}},
        ], order_start=5)
        assert steps[0]["stepOrder"] == 5

    def test_strength_exercise_category(self):
        steps = _build_steps([
            {
                "type": "step",
                "step_type": "interval",
                "exercise": "core",
                "duration": {"type": "reps", "reps": 15},
                "target": {"type": "none"},
            }
        ])
        assert "exerciseCategory" in steps[0]
        assert steps[0]["exerciseCategory"]["exerciseCategoryName"] == "CORE"

    def test_unknown_step_type_raises(self):
        with pytest.raises(ValueError, match="Unknown step type"):
            _build_steps([{"type": "invalid"}])

    def test_unknown_step_kind_raises(self):
        with pytest.raises(ValueError, match="Unknown step_type"):
            _build_steps([{"type": "step", "step_type": "flying"}])

    def test_empty_steps(self):
        assert _build_steps([]) == []


class TestBuildWorkoutPayload:
    def _simple_schema(self, sport="running"):
        return {
            "name": "Test Workout",
            "sport": sport,
            "steps": [
                {
                    "type": "step",
                    "step_type": "interval",
                    "duration": {"type": "time", "seconds": 600},
                    "target": {"type": "none"},
                }
            ],
        }

    def test_basic_structure(self):
        payload = build_workout_payload(self._simple_schema())
        assert payload["workoutName"] == "Test Workout"
        assert payload["sportType"]["sportTypeId"] == 1  # running
        assert len(payload["workoutSegments"]) == 1
        assert len(payload["workoutSegments"][0]["workoutSteps"]) == 1

    def test_default_sport_is_running(self):
        payload = build_workout_payload({"name": "X", "steps": []})
        assert payload["sportType"]["sportTypeKey"] == "running"

    def test_all_sports(self):
        for sport in ["running", "cycling", "swimming", "strength", "walking", "hiking"]:
            payload = build_workout_payload(self._simple_schema(sport))
            assert payload["sportType"]["sportTypeKey"] in [
                "running", "cycling", "swimming", "strength_training", "walking", "hiking"
            ]

    def test_unknown_sport_raises(self):
        with pytest.raises(ValueError, match="Unknown sport"):
            build_workout_payload({"name": "X", "sport": "parkour", "steps": []})

    def test_segment_sport_matches_top_level(self):
        payload = build_workout_payload(self._simple_schema("cycling"))
        assert payload["workoutSegments"][0]["sportType"] == payload["sportType"]

    def test_segment_order(self):
        payload = build_workout_payload(self._simple_schema())
        assert payload["workoutSegments"][0]["segmentOrder"] == 1

    def test_full_interval_workout(self):
        schema = {
            "name": "4x1km Tempo",
            "sport": "running",
            "steps": [
                {
                    "type": "step",
                    "step_type": "warmup",
                    "duration": {"type": "time", "seconds": 600},
                    "target": {"type": "heart_rate", "min": 120, "max": 148},
                },
                {
                    "type": "repeat",
                    "iterations": 4,
                    "steps": [
                        {
                            "type": "step",
                            "step_type": "interval",
                            "duration": {"type": "distance", "meters": 1000},
                            "target": {"type": "pace", "min_km": 4.83, "max_km": 5.0},
                        },
                        {
                            "type": "step",
                            "step_type": "recovery",
                            "duration": {"type": "time", "seconds": 90},
                            "target": {"type": "heart_rate", "min": 110, "max": 140},
                        },
                    ],
                },
                {
                    "type": "step",
                    "step_type": "cooldown",
                    "duration": {"type": "time", "seconds": 600},
                    "target": {"type": "heart_rate", "min": 115, "max": 145},
                },
            ],
        }
        payload = build_workout_payload(schema)
        wsteps = payload["workoutSegments"][0]["workoutSteps"]
        assert len(wsteps) == 3
        assert wsteps[0]["stepType"]["stepTypeKey"] == "warmup"
        assert wsteps[1]["type"] == "RepeatGroupDTO"
        assert wsteps[1]["numberOfIterations"] == 4
        assert wsteps[2]["stepType"]["stepTypeKey"] == "cooldown"


class TestLoadWorkoutInput:
    def test_json_string(self):
        data = load_workout_input('{"name": "X", "sport": "running", "steps": []}')
        assert data["name"] == "X"

    def test_file_input(self, tmp_path):
        schema = {"name": "File Workout", "sport": "running", "steps": []}
        f = tmp_path / "workout.json"
        f.write_text(json.dumps(schema))
        data = load_workout_input(f"@{f}")
        assert data["name"] == "File Workout"
