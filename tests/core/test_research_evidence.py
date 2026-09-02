from __future__ import annotations

import pytest

from gpd.contracts import ContractReference, VerificationEvidence
from gpd.core.research_evidence import (
    ClaimEvidenceLink,
    EvidenceBundle,
    EvidenceLocator,
    ResearchEvidence,
    citation_source_to_evidence,
    contract_reference_to_evidence,
    literature_evidence_bundle,
    research_evidence_to_verification_evidence,
    verification_evidence_to_evidence,
    write_paper_claim_to_evidence_bundle,
)
from gpd.mcp.paper.bibliography import CitationSource
from gpd.mcp.paper.models import WritePaperAuthoringClaim, WritePaperAuthoringClaimEvidence


def test_contract_and_verification_adapters_keep_durable_locators() -> None:
    reference = ContractReference(
        id="ref-benchmark",
        kind="paper",
        locator="arXiv:2401.01234v2#page=7",
        role="benchmark",
        why_it_matters="Defines the normalization used by the benchmark.",
    )
    evidence = contract_reference_to_evidence(reference)
    assert evidence.id == "ref-benchmark"
    assert evidence.locator.source == "arXiv:2401.01234v2#page=7"

    verification = verification_evidence_to_evidence(
        VerificationEvidence(
            method="numeric-tolerance",
            evidence_path="GPD/verification/limit.json",
            commit_sha="abc123",
            notes="Recovered the contracted q -> 0 limit.",
        ),
        evidence_id="oracle:limit",
    )
    assert verification.id == "oracle:limit"
    assert verification.locator.version == "abc123"
    assert verification.summary == "Recovered the contracted q -> 0 limit."

    legacy_roundtrip = research_evidence_to_verification_evidence(
        verification,
        link=ClaimEvidenceLink(claim_id="claim-limit", evidence_id=verification.id),
    )
    assert legacy_roundtrip.evidence_path == "GPD/verification/limit.json"
    assert legacy_roundtrip.claim_id == "claim-limit"
    assert legacy_roundtrip.commit_sha == "abc123"


def test_literature_bundle_links_claims_to_canonical_sources() -> None:
    source = CitationSource(
        source_type="paper",
        reference_id="ref-main",
        title="Long-wave benchmark",
        authors=["Ada Example"],
        year="2026",
        arxiv_id="2601.00001v2",
    )
    bundle = literature_evidence_bundle(
        [source],
        claim_evidence=EvidenceBundle(
            evidence=[
                ResearchEvidence(
                    id="ref-main:eq12",
                    kind="equation",
                    locator=EvidenceLocator(source="2601.00001v2", equation="12"),
                )
            ],
            links=[
                ClaimEvidenceLink(
                    claim_id="claim-instability",
                    evidence_id="ref-main:eq12",
                    scope="linear regime",
                )
            ],
        ),
    )
    assert bundle.schema_version == 1
    assert bundle.evidence[0].locator.source == "2601.00001v2"
    assert bundle.evidence[1].locator.equation == "12"
    assert bundle.links[0].scope == "linear regime"


def test_paper_claim_adapter_emits_records_and_links_without_rewriting_legacy_model() -> None:
    claim = WritePaperAuthoringClaim(
        id="CLM-claim-1",
        statement="The benchmark is recovered.",
        evidence=WritePaperAuthoringClaimEvidence(
            result_ids=["RES-result-1"],
            citation_source_ids=["ref-main"],
        ),
    )
    bundle = write_paper_claim_to_evidence_bundle(claim)
    assert {item.id for item in bundle.evidence} == {"result:RES-result-1", "citation:ref-main"}
    assert {link.claim_id for link in bundle.links} == {"CLM-claim-1"}


def test_bundle_rejects_orphan_claim_links() -> None:
    with pytest.raises(ValueError, match="missing evidence ids"):
        EvidenceBundle(links=[ClaimEvidenceLink(claim_id="claim-1", evidence_id="missing")])


def test_citation_adapter_uses_stable_identifier_before_title() -> None:
    evidence = citation_source_to_evidence(
        CitationSource(
            source_type="paper",
            reference_id="ref-doi",
            title="A result",
            doi="10.1000/example",
        )
    )
    assert evidence.id == "ref-doi"
    assert evidence.locator.source == "10.1000/example"
