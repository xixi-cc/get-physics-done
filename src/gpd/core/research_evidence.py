"""Small shared evidence protocol for claim-bearing GPD workflows.

The protocol intentionally stores locators and links rather than source text.
Workflows can therefore exchange evidence without eagerly copying papers,
results, or figures into every prompt.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import TYPE_CHECKING, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

if TYPE_CHECKING:
    from gpd.contracts import VerificationEvidence

__all__ = [
    "EVIDENCE_SCHEMA_VERSION",
    "EvidenceLocator",
    "ResearchEvidence",
    "ClaimEvidenceLink",
    "EvidenceBundle",
    "contract_reference_to_evidence",
    "verification_evidence_to_evidence",
    "research_evidence_to_verification_evidence",
    "citation_source_to_evidence",
    "literature_evidence_bundle",
    "write_paper_claim_to_evidence_bundle",
    "write_evidence_bundle",
]


EVIDENCE_SCHEMA_VERSION = 1
EvidenceKind = Literal["paper", "equation", "figure", "dataset", "code", "result", "note", "verification", "other"]
EvidenceRelation = Literal["supports", "contradicts", "limits", "derived_from"]


def _required_text(value: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError("must not be blank")
    return normalized


def _optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    return normalized or None


def _stable_id(prefix: str, value: str) -> str:
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]
    return f"{prefix}:{digest}"


class EvidenceLocator(BaseModel):
    """A compact pointer to evidence; detailed content remains at the source."""

    model_config = ConfigDict(validate_assignment=True, extra="forbid")

    source: str
    version: str | None = None
    page: str | None = None
    section: str | None = None
    equation: str | None = None
    figure: str | None = None
    line: str | None = None
    data_slice: str | None = None
    sha256: str | None = None

    @field_validator("source", mode="before")
    @classmethod
    def _normalize_source(cls, value: str) -> str:
        return _required_text(value)

    @field_validator("version", "page", "section", "equation", "figure", "line", "data_slice", "sha256", mode="before")
    @classmethod
    def _normalize_optional_fields(cls, value: str | None) -> str | None:
        return _optional_text(value)


class ResearchEvidence(BaseModel):
    """One reusable scientific evidence record."""

    model_config = ConfigDict(validate_assignment=True, extra="forbid")

    id: str
    kind: EvidenceKind = "other"
    locator: EvidenceLocator
    title: str | None = None
    summary: str | None = None

    @field_validator("id", mode="before")
    @classmethod
    def _normalize_id(cls, value: str) -> str:
        return _required_text(value)

    @field_validator("title", "summary", mode="before")
    @classmethod
    def _normalize_optional_fields(cls, value: str | None) -> str | None:
        return _optional_text(value)


class ClaimEvidenceLink(BaseModel):
    """The scoped relation between a claim and a reusable evidence record."""

    model_config = ConfigDict(validate_assignment=True, extra="forbid")

    claim_id: str
    evidence_id: str
    relation: EvidenceRelation = "supports"
    scope: str | None = None
    note: str | None = None

    @field_validator("claim_id", "evidence_id", mode="before")
    @classmethod
    def _normalize_ids(cls, value: str) -> str:
        return _required_text(value)

    @field_validator("scope", "note", mode="before")
    @classmethod
    def _normalize_optional_fields(cls, value: str | None) -> str | None:
        return _optional_text(value)


class EvidenceBundle(BaseModel):
    """A closed, portable set of evidence records and claim bindings."""

    model_config = ConfigDict(validate_assignment=True, extra="forbid")

    schema_version: Literal[1] = EVIDENCE_SCHEMA_VERSION
    evidence: list[ResearchEvidence] = Field(default_factory=list)
    links: list[ClaimEvidenceLink] = Field(default_factory=list)

    @model_validator(mode="after")
    def _validate_identity_and_links(self) -> EvidenceBundle:
        evidence_ids = [record.id for record in self.evidence]
        if len(evidence_ids) != len(set(evidence_ids)):
            raise ValueError("evidence ids must be unique")
        known = set(evidence_ids)
        missing = sorted({link.evidence_id for link in self.links if link.evidence_id not in known})
        if missing:
            raise ValueError(f"claim links reference missing evidence ids: {', '.join(missing)}")
        return self


def contract_reference_to_evidence(reference: object) -> ResearchEvidence:
    """Adapt a :class:`ContractReference` without changing persisted contracts."""

    from gpd.contracts import ContractReference

    parsed = reference if isinstance(reference, ContractReference) else ContractReference.model_validate(reference)
    kind: EvidenceKind = parsed.kind if parsed.kind in {"paper", "dataset"} else "other"
    return ResearchEvidence(
        id=parsed.id,
        kind=kind,
        locator=EvidenceLocator(source=parsed.locator),
        summary=parsed.why_it_matters,
    )


def verification_evidence_to_evidence(record: object, *, evidence_id: str | None = None) -> ResearchEvidence:
    """Adapt legacy verification provenance to a shared evidence record."""

    from gpd.contracts import VerificationEvidence

    parsed = record if isinstance(record, VerificationEvidence) else VerificationEvidence.model_validate(record)
    source = parsed.evidence_path or parsed.proof_artifact_path or parsed.trace_id or f"verification:{parsed.method}"
    return ResearchEvidence(
        id=evidence_id or _stable_id("verification", source),
        kind="verification",
        locator=EvidenceLocator(source=source, version=parsed.commit_sha, sha256=parsed.proof_artifact_sha256),
        summary=parsed.notes,
    )


def research_evidence_to_verification_evidence(
    evidence: ResearchEvidence | dict[str, object],
    *,
    link: ClaimEvidenceLink | dict[str, object] | None = None,
    method: str = "research-evidence",
) -> VerificationEvidence:
    """Adapt shared evidence back to the legacy verifier persistence model."""

    from gpd.contracts import VerificationEvidence

    parsed = evidence if isinstance(evidence, ResearchEvidence) else ResearchEvidence.model_validate(evidence)
    parsed_link = (
        None
        if link is None
        else link
        if isinstance(link, ClaimEvidenceLink)
        else ClaimEvidenceLink.model_validate(link)
    )
    locator_details = parsed.locator.model_dump(exclude_none=True)
    notes = parsed.summary
    if len(locator_details) > 1:
        compact_locator = ", ".join(f"{key}={value}" for key, value in locator_details.items() if key != "source")
        notes = f"{notes}; {compact_locator}" if notes else compact_locator
    return VerificationEvidence(
        method=method,
        evidence_path=parsed.locator.source,
        commit_sha=parsed.locator.version,
        notes=notes,
        claim_id=parsed_link.claim_id if parsed_link is not None else None,
    )


def citation_source_to_evidence(source: object, *, source_artifact: str | None = None) -> ResearchEvidence:
    """Adapt one strict literature citation source to the shared protocol."""

    from gpd.mcp.paper.bibliography import CitationSource

    parsed = source if isinstance(source, CitationSource) else CitationSource.model_validate(source)
    canonical = parsed.doi or parsed.arxiv_id or parsed.url or source_artifact or parsed.title
    reference_id = parsed.reference_id or _stable_id("citation", canonical)
    version = parsed.arxiv_id or parsed.year or None
    return ResearchEvidence(
        id=reference_id,
        kind="paper" if parsed.source_type == "paper" else ("dataset" if parsed.source_type == "data" else "other"),
        locator=EvidenceLocator(source=canonical, version=version),
        title=parsed.title,
    )


def literature_evidence_bundle(
    sources: list[object],
    *,
    claim_evidence: EvidenceBundle | dict[str, object] | None = None,
    source_artifact: str | None = None,
) -> EvidenceBundle:
    """Build the literature-review seam from citations plus scoped claim evidence."""

    claim_bundle = (
        EvidenceBundle()
        if claim_evidence is None
        else claim_evidence
        if isinstance(claim_evidence, EvidenceBundle)
        else EvidenceBundle.model_validate(claim_evidence)
    )
    return EvidenceBundle(
        evidence=[
            *(citation_source_to_evidence(source, source_artifact=source_artifact) for source in sources),
            *claim_bundle.evidence,
        ],
        links=list(claim_bundle.links),
    )


def write_paper_claim_to_evidence_bundle(claim: object) -> EvidenceBundle:
    """Adapt one legacy paper-authoring claim and its id-only bindings."""

    from gpd.mcp.paper.models import WritePaperAuthoringClaim

    parsed = claim if isinstance(claim, WritePaperAuthoringClaim) else WritePaperAuthoringClaim.model_validate(claim)
    bindings: tuple[tuple[str, list[str], EvidenceKind], ...] = (
        ("source-note", parsed.evidence.source_note_ids, "note"),
        ("result", parsed.evidence.result_ids, "result"),
        ("figure", parsed.evidence.figure_ids, "figure"),
        ("citation", parsed.evidence.citation_source_ids, "paper"),
    )
    records: list[ResearchEvidence] = []
    links: list[ClaimEvidenceLink] = []
    for prefix, ids, kind in bindings:
        for bound_id in ids:
            evidence_id = f"{prefix}:{bound_id}"
            records.append(
                ResearchEvidence(id=evidence_id, kind=kind, locator=EvidenceLocator(source=bound_id))
            )
            links.append(ClaimEvidenceLink(claim_id=parsed.id, evidence_id=evidence_id))
    return EvidenceBundle(evidence=records, links=links)


def write_evidence_bundle(path: Path, bundle: EvidenceBundle) -> None:
    """Write a canonical bundle for workflow handoff."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(bundle.model_dump_json(indent=2) + "\n", encoding="utf-8")
