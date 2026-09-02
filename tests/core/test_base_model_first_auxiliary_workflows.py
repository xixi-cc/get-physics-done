"""Base-model-first contracts for interactive diagnosis and explanation."""

from pathlib import Path

from gpd.core.workflow_staging import load_workflow_stage_manifest

ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = ROOT / "src" / "gpd" / "specs" / "workflows"


def test_interactive_debug_keeps_evidence_and_fresh_context_boundaries() -> None:
    source = (WORKFLOWS / "debug.md").read_text(encoding="utf-8")

    assert "ordinary single interactive issue" in source
    assert "current main model" in source
    assert "batch/parallel diagnosis" in source
    assert "explicitly requests independent isolation" in source
    assert "same filled investigation prompt" in source
    assert "do not self-promote a plausible" in source.lower()


def test_explain_keeps_independent_citation_audit_on_main_context_route() -> None:
    source = (WORKFLOWS / "explain.md").read_text(encoding="utf-8")

    assert "current main model writes the explanation" in source
    assert "explicitly asks" in source
    assert "for fresh isolation" in source
    assert "bibliographer remains a fresh" in source
    assert "independent audit on every route" in source
    assert "do not invent a child id" in source.lower()


def test_write_paper_routes_only_authoring_through_cognitive_profile() -> None:
    manifest = load_workflow_stage_manifest("write-paper")

    assert tuple(
        "cognitive_profile" in manifest.stage(stage_id).required_init_fields
        for stage_id in (
            "paper_bootstrap",
            "outline_and_scaffold",
            "figure_and_section_authoring",
            "consistency_and_references",
            "publication_review",
        )
    ) == (False, False, True, False, False)


def test_write_paper_main_context_route_preserves_science_and_review_gates() -> None:
    source = (WORKFLOWS / "write-paper" / "authoring.md").read_text(encoding="utf-8")

    assert "draft sections sequentially in the current main" in source
    assert "true parallel wave drafting" in source
    assert "same section prompt and evidence packet" in source
    assert "proof-redteam ceiling" in source
    assert "final referee" in source
    assert "not invent a child id" in source
