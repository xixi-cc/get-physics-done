from __future__ import annotations

from pathlib import Path

from tests.assertion_taxonomy_support import assert_prompt_contracts, machine_exact, semantic_concept

ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = ROOT / "src" / "gpd" / "specs" / "workflows"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_literature_review_emits_audited_locator_only_evidence_bundle() -> None:
    scoped = _read(WORKFLOWS / "literature-review" / "scope-locked.md")
    handoff = _read(WORKFLOWS / "literature-review" / "review-handoff.md")
    completion = _read(WORKFLOWS / "literature-review" / "completion-gate.md")

    assert_prompt_contracts(
        scoped,
        *semantic_concept(
            "literature claim evidence",
            required=("{slug}-CLAIM-EVIDENCE.json", "page/equation/figure/data locators"),
        ),
    )
    assert_prompt_contracts(
        handoff,
        machine_exact(
            "literature evidence command",
            ("gpd --raw evidence literature", "{slug}-EVIDENCE.json"),
        ),
        *semantic_concept("locator-only evidence", required=("never inline", "paper bodies")),
    )
    assert_prompt_contracts(
        completion,
        *semantic_concept("literature evidence completion", required=("EVIDENCE.json", "parseable")),
    )


def test_verify_work_runs_named_oracles_and_preserves_claim_ceiling() -> None:
    inventory = _read(WORKFLOWS / "verify-work" / "inventory-build.md")

    assert_prompt_contracts(
        inventory,
        machine_exact(
            "verify oracle execution",
            (
                'gpd --raw verify oracle "$ORACLE_SPEC"',
                "${PHASE_DIR_ABS}/oracle-results/*.json",
                "${PHASE_DIR_ABS}/evidence/*.json",
            ),
        ),
        *semantic_concept(
            "oracle claim ceiling",
            required=("Passing proves", "only the encoded check", "Never invent an oracle spec"),
        ),
    )
