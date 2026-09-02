"""Capability contracts for the consolidated research role."""

from pathlib import Path

from gpd import registry

ROOT = Path(__file__).resolve().parents[2]
AGENTS = ROOT / "src" / "gpd" / "agents"
WORKFLOWS = ROOT / "src" / "gpd" / "specs" / "workflows"
CONSTITUTION = ROOT / "src" / "gpd" / "specs" / "references" / "shared" / "scientific-constitution.md"

LEGACY_RESEARCH_ROLES = {
    "gpd-phase-researcher",
    "gpd-project-researcher",
    "gpd-research-synthesizer",
    "gpd-research-mapper",
    "gpd-literature-reviewer",
}


def test_one_research_role_replaces_five_legacy_roles() -> None:
    names = set(registry.list_agents())
    assert "gpd-researcher" in names
    assert names.isdisjoint(LEGACY_RESEARCH_ROLES)
    assert not any((AGENTS / f"{name}.md").exists() for name in LEGACY_RESEARCH_ROLES)


def test_researcher_and_constitution_stay_compact_and_keep_scientific_invariants() -> None:
    prompt = (AGENTS / "gpd-researcher.md").read_text(encoding="utf-8")
    constitution = CONSTITUTION.read_text(encoding="utf-8")

    assert len(prompt.split()) <= 900
    assert len(constitution.split()) <= 1_200
    assert all(
        mode in prompt for mode in ("project-survey", "phase-research", "literature-review", "project-map", "synthesis")
    )
    assert all(
        term in constitution
        for term in (
            "assumptions",
            "dimensions",
            "limiting cases",
            "convergence",
            "uncertainty",
            "Never invent",
            "independent verification",
        )
    )
    assert "shared-protocols.md" not in prompt
    assert "physics-subfields.md" not in prompt
    assert "project-types/" not in prompt


def test_workflows_pass_explicit_research_modes() -> None:
    expected = {
        "new-project/literature-survey.md": ("project-survey", "synthesis"),
        "new-milestone/survey-objectives.md": ("project-survey", "synthesis"),
        "plan-phase/research-routing.md": ("phase-research",),
        "research-phase/research-handoff.md": ("phase-research",),
        "literature-review/scope-locked.md": ("literature-review",),
        "map-research/mapper-authoring.md": ("project-map",),
    }
    for relative, modes in expected.items():
        text = (WORKFLOWS / relative).read_text(encoding="utf-8")
        assert "gpd-researcher" in text
        for mode in modes:
            assert f"Use mode `{mode}`" in text
