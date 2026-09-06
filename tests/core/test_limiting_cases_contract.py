"""Prompt-contract guardrails for limiting-cases standalone/current-workspace behavior."""

from __future__ import annotations

from pathlib import Path

from gpd import registry

REPO_ROOT = Path(__file__).resolve().parents[2]
COMMAND_PATH = REPO_ROOT / "src/gpd/commands/limiting-cases.md"
WORKFLOW_PATH = REPO_ROOT / "src/gpd/specs/workflows/limiting-cases.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_limiting_cases_command_surfaces_typed_current_workspace_output_policy() -> None:
    command = _read(COMMAND_PATH)
    parsed = registry.get_command("limiting-cases")

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
                "GPD/research-map/*.md",
                "GPD/analysis/*.md",
            ],
        ),
        output_policy=registry.CommandOutputPolicy(
            output_mode="managed",
            managed_root_kind="gpd_managed_durable",
            default_output_subtree="GPD/analysis",
            stage_artifact_policy="gpd_owned_outputs_only",
        ),
    )
