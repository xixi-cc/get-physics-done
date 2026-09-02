"""Reference-diet classification and eager-loading boundaries."""

from pathlib import Path

from gpd.core.reference_diet import ReferenceDietClass, classify_reference
from gpd.core.workflow_staging import load_workflow_stage_manifest

ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = ROOT / "src" / "gpd" / "specs" / "workflows"


def test_reference_families_have_conservative_loading_classes() -> None:
    assert classify_reference("references/shared/scientific-constitution.md") is ReferenceDietClass.KERNEL
    assert classify_reference("references/orchestration/child-artifact-gate.md") is ReferenceDietClass.KERNEL
    assert classify_reference("references/protocols/order-of-limits.md") is ReferenceDietClass.JIT_CHECKLIST
    assert classify_reference("references/physics-subfields.md") is ReferenceDietClass.JIT_CHECKLIST
    assert classify_reference("references/examples/contradiction-resolution-example.md") is ReferenceDietClass.ARCHIVE_RETRIEVAL
    assert classify_reference("references/execution/executor-worked-example.md") is ReferenceDietClass.ARCHIVE_RETRIEVAL


def test_no_archive_retrieval_reference_is_default_eager_stage_authority() -> None:
    workflow_ids = sorted(
        path.name.removesuffix("-stage-manifest.json") for path in WORKFLOWS.glob("*-stage-manifest.json")
    )
    violations: list[str] = []
    for workflow_id in workflow_ids:
        manifest = load_workflow_stage_manifest(workflow_id)
        for stage in manifest.stages:
            for authority in stage.eager_authorities():
                if classify_reference(authority) is ReferenceDietClass.ARCHIVE_RETRIEVAL:
                    violations.append(f"{workflow_id}:{stage.id}:{authority}")

    assert violations == []
