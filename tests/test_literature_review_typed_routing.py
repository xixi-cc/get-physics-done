from __future__ import annotations

from pathlib import Path

from tests.assertion_taxonomy_support import assert_prompt_contracts, machine_exact, semantic_concept
from tests.workflow_authority_support import workflow_authority_text

REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS_DIR = REPO_ROOT / "src" / "gpd" / "specs" / "workflows"
AGENTS_DIR = REPO_ROOT / "src" / "gpd" / "agents"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_literature_review_workflow_routes_on_typed_status_and_artifact_gate() -> None:
    workflow = workflow_authority_text(WORKFLOWS_DIR, "literature-review")

    assert "references/orchestration/child-artifact-gate.md" in workflow
    assert "references/orchestration/continuation-boundary.md" in workflow
    assert "GPD/literature/{slug}-REVIEW.md" in workflow
    assert "GPD/literature/{slug}-CITATION-SOURCES.json" in workflow
    assert "GPD/literature/{slug}-CITATION-AUDIT.md" in workflow
    assert "all three paths are named in `files_written` and present/readable on disk" in workflow
    assert_prompt_contracts(
        workflow,
        machine_exact("literature-review checkpoint route", "checkpoint: include the decision question"),
    )
    assert "blocked/failed: list the missing artifact" in workflow


def test_literature_reviewer_shows_base_return_fields_and_one_shot_checkpointing() -> None:
    agent = _read(AGENTS_DIR / "gpd-researcher.md")

    assert "`literature-review`" in agent
    assert "typed checkpoint" in agent
    assert "standard `gpd_return` envelope" in agent
    assert "files_written" in agent
