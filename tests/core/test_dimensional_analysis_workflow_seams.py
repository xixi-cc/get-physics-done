"""Focused assertions for the dimensional-analysis standalone/workspace contract."""

from __future__ import annotations

from pathlib import Path

from gpd import registry

REPO_ROOT = Path(__file__).resolve().parents[2]
COMMAND_DOC = REPO_ROOT / "src/gpd/commands/dimensional-analysis.md"
WORKFLOW_DOC = REPO_ROOT / "src/gpd/specs/workflows/dimensional-analysis.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_dimensional_analysis_command_exposes_workspace_locked_policy() -> None:
    command_text = _read(COMMAND_DOC)
    parsed = registry.get_command("dimensional-analysis")

    assert parsed.command_policy == registry.CommandPolicy(
        schema_version=1,
        subject_policy=registry.CommandSubjectPolicy(
            explicit_input_kinds=["phase number or file path"],
        ),
        supporting_context_policy=registry.CommandSupportingContextPolicy(
            project_context_mode="project-aware",
            project_reentry_mode="disallowed",
            optional_file_patterns=[
                "GPD/STATE.md",
                "GPD/ROADMAP.md",
                "GPD/research-map/FORMALISM.md",
                "GPD/research-map/VALIDATION.md",
            ],
        ),
        output_policy=registry.CommandOutputPolicy(
            output_mode="managed",
            managed_root_kind="gpd_managed_durable",
            default_output_subtree="GPD/analysis",
        ),
    )
