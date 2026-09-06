"""Focused assertions for the sensitivity-analysis standalone/current-workspace contract."""

from __future__ import annotations

from pathlib import Path

from gpd import registry

REPO_ROOT = Path(__file__).resolve().parents[2]
COMMAND_DOC = REPO_ROOT / "src/gpd/commands/sensitivity-analysis.md"
WORKFLOW_DOC = REPO_ROOT / "src/gpd/specs/workflows/sensitivity-analysis.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_sensitivity_analysis_command_exposes_typed_workspace_locked_policy() -> None:
    command_text = _read(COMMAND_DOC)
    parsed = registry.get_command("sensitivity-analysis")

    assert parsed.command_policy == registry.CommandPolicy(
        schema_version=1,
        subject_policy=registry.CommandSubjectPolicy(
            explicit_input_kinds=["--target quantity", "--params p1,p2,..."],
        ),
        supporting_context_policy=registry.CommandSupportingContextPolicy(
            project_context_mode="project-aware",
            project_reentry_mode="disallowed",
            optional_file_patterns=[
                "GPD/STATE.md",
                "GPD/ROADMAP.md",
                "GPD/analysis/PARAMETERS.md",
            ],
        ),
        output_policy=registry.CommandOutputPolicy(
            output_mode="managed",
            managed_root_kind="gpd_managed_durable",
            default_output_subtree="GPD/analysis",
            stage_artifact_policy="gpd_owned_outputs_only",
        ),
    )
