"""Behavioral regressions for event-driven defaults and explicit stop limits."""
import json
from pathlib import Path

import pytest

from gpd.core.observability import ObservabilityEvent, _apply_automatic_execution_guards


def run_guard(tmp_path: Path, *, config=None, facts=None, name="result"):
    planning = tmp_path / "GPD"
    planning.mkdir(exist_ok=True)
    (planning / "PROJECT.md").write_text("# Test project\n")
    if config is not None:
        (planning / "config.json").write_text(json.dumps(config))
    # Many routine tasks and a long elapsed interval must not create a review
    # without scientific evidence or an explicitly configured numeric limit.
    state = {"current_task_index": 20, "segment_started_at": "2026-09-06T00:00:00+00:00"}
    facts = facts or {"load_bearing": False}
    event = ObservabilityEvent(event_id="event", timestamp="2026-09-06T04:00:00+00:00",
        session_id="session", category="execution", name=name, action="produce", data={"execution": facts})
    _apply_automatic_execution_guards(state, event, facts, cwd=tmp_path)
    return state


def test_routine_work_does_not_require_human_review_just_for_elapsed_time_or_count(tmp_path):
    state = run_guard(tmp_path)
    assert not state.get("waiting_for_review")
    assert not state.get("downstream_locked")


@pytest.mark.parametrize("facts,reason", [
    ({"load_bearing": True}, "first_result"),
    ({"load_bearing": False, "proxy_only": True}, "skeptical_requestioning"),
    ({"load_bearing": False, "direct_anchor_missing": True}, "skeptical_requestioning"),
])
def test_scientific_gate_survives_disabled_numeric_limits(tmp_path, facts, reason):
    state = run_guard(tmp_path, facts=facts)
    assert state["waiting_for_review"] is True
    assert state["checkpoint_reason"] == reason


@pytest.mark.parametrize("config,reason", [
    ({"execution": {"checkpoint_after_n_tasks": 2}}, "task_budget_reached"),
    ({"execution": {"max_unattended_minutes_per_plan": 15}}, "time_budget_exceeded"),
])
def test_explicit_project_stop_limits_are_not_silently_ignored(tmp_path, config, reason):
    state = run_guard(tmp_path, config=config)
    assert state["waiting_for_review"] is True
    assert state["waiting_reason"] == reason


def test_explicit_dense_policy_keeps_first_result_gate_for_routine_result(tmp_path):
    state = run_guard(tmp_path, config={"review_cadence": "dense"})
    assert state["first_result_gate_pending"] is True
