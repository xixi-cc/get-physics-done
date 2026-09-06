"""Focused assertions for the quick command wrapper contract."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
QUICK_COMMAND = REPO_ROOT / "src" / "gpd" / "commands" / "quick.md"
QUICK_STAGE_DIR = REPO_ROOT / "src" / "gpd" / "specs" / "workflows" / "quick"
QUICK_REFERENCES_DIR = REPO_ROOT / "src" / "gpd" / "specs" / "references" / "quick"


def test_quick_command_wrapper_surfaces_staged_handoff_and_preserves_workflow_gates() -> None:
    command = QUICK_COMMAND.read_text(encoding="utf-8")
    bootstrap = (QUICK_STAGE_DIR / "task-bootstrap.md").read_text(encoding="utf-8")
    authoring = (QUICK_STAGE_DIR / "task-authoring.md").read_text(encoding="utf-8")
    mode_boundary = (QUICK_REFERENCES_DIR / "quick-mode-boundary.md").read_text(encoding="utf-8")

    assert "workflow owns the staged main-context authoring" in " ".join(command.split())
    assert "conditional role loading" in command
    assert "@{GPD_INSTALL_DIR}/workflows/quick/task-bootstrap.md" in command
    assert "@{GPD_INSTALL_DIR}/workflows/quick.md" not in command
    assert "active stage authority" in command
    assert "Typical quick tasks in physics research" not in command
    assert "When to Use Quick vs Full Workflow" not in command
    assert "Rigor Expectations in Quick Mode" not in command

    assert "task description already supplied in $ARGUMENTS" in bootstrap
    assert "project_exists" in bootstrap
    assert "quick-delegated-authoring.md" in authoring
    assert "Do not invent a child id" in authoring
    assert "gpd state add-decision" in authoring
    assert "gpd state update" in authoring
    assert "Promote out of quick" in mode_boundary
    assert "gpd:add-phase" in mode_boundary
    assert "gpd:insert-phase" in mode_boundary


def test_quick_execution_stages_authorize_durable_outputs_and_keep_delegation_lazy() -> None:
    from gpd.core.workflow_staging import load_workflow_stage_manifest

    manifest = load_workflow_stage_manifest("quick")
    direct = manifest.stage("task_authoring")
    reference = manifest.stage("reference_context")
    for stage in (direct, reference):
        assert {"GPD/quick/NNN-slug", "GPD/STATE.md", "GPD/state.json"} <= set(stage.writes_allowed)
    assert "reference_context" in direct.next_stages
    assert "references/quick/quick-delegated-authoring.md" not in direct.loaded_authorities
    assert any("references/quick/quick-delegated-authoring.md" in item.authorities for item in direct.conditional_authorities)
