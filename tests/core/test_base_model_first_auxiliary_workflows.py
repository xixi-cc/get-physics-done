"""Base-model-first contracts for interactive diagnosis and explanation."""

from pathlib import Path

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
