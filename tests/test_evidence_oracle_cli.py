from __future__ import annotations

import json
from pathlib import Path

from gpd.cli import app
from gpd.core.research_evidence import EvidenceBundle
from tests.helpers.cli import StableCliRunner, json_output_from_result

runner = StableCliRunner()


def _write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def test_literature_evidence_flows_into_executable_verifier_result(tmp_path: Path) -> None:
    sources = tmp_path / "topic-CITATION-SOURCES.json"
    claim_evidence = tmp_path / "topic-CLAIM-EVIDENCE.json"
    bundle = tmp_path / "topic-EVIDENCE.json"
    spec = tmp_path / "limit-ORACLE.json"
    result_path = tmp_path / "limit-RESULT.json"
    verified_bundle = tmp_path / "topic-VERIFIED-EVIDENCE.json"
    _write_json(
        sources,
        [
            {
                "source_type": "paper",
                "reference_id": "ref-main",
                "title": "Long-wave benchmark",
                "authors": ["Ada Example"],
                "year": "2026",
                "arxiv_id": "2601.00001v2",
            }
        ],
    )
    _write_json(
        claim_evidence,
        {
            "schema_version": 1,
            "evidence": [
                {
                    "id": "ref-main:eq12",
                    "kind": "equation",
                    "locator": {"source": "2601.00001v2", "page": "7", "equation": "12"},
                }
            ],
            "links": [
                {
                    "claim_id": "claim-limit",
                    "evidence_id": "ref-main:eq12",
                    "relation": "supports",
                    "scope": "linear long-wave regime",
                }
            ],
        },
    )
    _write_json(
        spec,
        {
            "runner": "numeric-tolerance",
            "oracle_id": "limit-recovery",
            "check_id": "5.3",
            "claim_id": "claim-limit",
            "acceptance_test_id": "test-limit",
            "evidence_ids": ["ref-main"],
            "observed": 0.501,
            "expected": 0.5,
            "atol": 0.01,
            "rtol": 0.0,
        },
    )

    literature_result = runner.invoke(
        app,
        [
            "--cwd",
            str(tmp_path),
            "--raw",
            "evidence",
            "literature",
            str(sources),
            "--claim-evidence",
            str(claim_evidence),
            "--output",
            str(bundle),
        ],
        catch_exceptions=False,
    )
    assert literature_result.exit_code == 0
    assert json_output_from_result(literature_result)["evidence_count"] == 2

    oracle_result = runner.invoke(
        app,
        [
            "--cwd",
            str(tmp_path),
            "--raw",
            "verify",
            "oracle",
            str(spec),
            "--result-output",
            str(result_path),
            "--evidence-bundle",
            str(bundle),
            "--bundle-output",
            str(verified_bundle),
        ],
        catch_exceptions=False,
    )
    assert oracle_result.exit_code == 0
    assert json_output_from_result(oracle_result)["passed"] is True

    parsed = EvidenceBundle.model_validate_json(verified_bundle.read_text(encoding="utf-8"))
    assert {record.id for record in parsed.evidence} == {
        "ref-main",
        "ref-main:eq12",
        "oracle:limit-recovery",
    }
    assert any(
        link.claim_id == "claim-limit"
        and link.evidence_id == "oracle:limit-recovery"
        and link.relation == "supports"
        for link in parsed.links
    )
