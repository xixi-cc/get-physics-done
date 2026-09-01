"""Opt-in main-context execution contracts."""

from pathlib import Path

from gpd.core.workflow_staging import load_workflow_stage_manifest

ROOT = Path(__file__).resolve().parents[2]
EXECUTOR_DISPATCH = ROOT / "src" / "gpd" / "specs" / "workflows" / "execute-phase" / "executor-dispatch.md"


def test_executor_dispatch_receives_cognitive_profile_only_when_needed() -> None:
    manifest = load_workflow_stage_manifest("execute-phase")

    assert "cognitive_profile" not in manifest.stage("phase_bootstrap").required_init_fields
    assert "cognitive_profile" in manifest.stage("executor_dispatch").required_init_fields


def test_base_model_first_execution_preserves_isolation_and_science_gates() -> None:
    source = EXECUTOR_DISPATCH.read_text(encoding="utf-8")

    assert "execute in the current main context by default" in source
    assert "true parallel fanout" in source
    assert "isolated worktree" in source
    assert "long unattended batch" in source
    assert "proof-redteam boundary" in source
    assert "does not gain shared-state or science-promotion authority" in source
    assert "Do not invent a child id" in source
