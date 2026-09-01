"""Shared strings for model-visible prompt wrappers."""

from __future__ import annotations

from gpd.core.model_visible_sections import (
    MODEL_VISIBLE_CLOSED_SCHEMA_PHRASE,
    render_model_visible_note,
)

__all__ = [
    "agent_visibility_note",
    "command_visibility_note",
    "MODEL_VISIBLE_CLOSED_SCHEMA_PHRASE",
    "AGENT_ARTIFACT_WRITE_AUTHORITIES",
    "AGENT_FRONTMATTER_AUTHORITY_POINTER",
    "INTERNAL_AGENT_BOUNDARY_POINTER",
    "READ_ONLY_INTERNAL_AGENT_BOUNDARY_POINTER",
    "AGENT_COMMIT_AUTHORITIES",
    "AGENT_ROLE_FAMILIES",
    "AGENT_SHARED_STATE_AUTHORITIES",
    "AGENT_SURFACES",
    "COMMAND_POLICY_FRONTMATTER_KEY",
    "COMMAND_POLICY_PROMPT_WRAPPER_KEY",
    "VALID_CONTEXT_MODES",
    "REVIEW_CONTRACT_CONDITIONAL_WHENS",
    "REVIEW_CONTRACT_FRONTMATTER_KEY",
    "REVIEW_CONTRACT_MODES",
    "REVIEW_CONTRACT_PREFLIGHT_CHECKS",
    "REVIEW_CONTRACT_PROMPT_WRAPPER_KEY",
    "REVIEW_CONTRACT_REQUIRED_STATES",
    "REVIEW_CONTRACT_WRAPPER_KEYS",
    "SKEPTICAL_RIGOR_GUARDRAILS_HEADING",
    "review_contract_visibility_note",
    "skeptical_rigor_guardrails_section",
]

REVIEW_CONTRACT_FRONTMATTER_KEY = "review-contract"
REVIEW_CONTRACT_PROMPT_WRAPPER_KEY = "review_contract"
REVIEW_CONTRACT_WRAPPER_KEYS = (
    REVIEW_CONTRACT_PROMPT_WRAPPER_KEY,
    REVIEW_CONTRACT_FRONTMATTER_KEY,
)
SKEPTICAL_RIGOR_GUARDRAILS_HEADING = "Scientific Rigor Guardrails"
VALID_CONTEXT_MODES = ("global", "projectless", "project-aware", "project-required")
AGENT_COMMIT_AUTHORITIES = ("direct", "orchestrator")
AGENT_SURFACES = ("public", "internal")
AGENT_ROLE_FAMILIES = ("worker", "analysis", "verification", "review", "coordination")
AGENT_ARTIFACT_WRITE_AUTHORITIES = ("scoped_write", "read_only")
AGENT_SHARED_STATE_AUTHORITIES = ("return_only", "direct")
AGENT_FRONTMATTER_AUTHORITY_POINTER = (
    "Authority: use the frontmatter-derived Agent Requirements block for commit, surface, artifact, and "
    "shared-state policy."
)
INTERNAL_AGENT_BOUNDARY_POINTER = (
    "Internal specialist boundary: stay inside assigned scoped artifacts and the return envelope; do not act as "
    "the default writable implementation agent."
)
READ_ONLY_INTERNAL_AGENT_BOUNDARY_POINTER = (
    "Internal specialist boundary: stay read-only inside assigned scoped artifacts and the return envelope; "
    "do not act as the default writable implementation agent."
)
COMMAND_POLICY_FRONTMATTER_KEY = "command-policy"
COMMAND_POLICY_PROMPT_WRAPPER_KEY = "command_policy"
REVIEW_CONTRACT_MODES = ("publication", "review")
REVIEW_CONTRACT_REQUIRED_STATES = ("phase_executed",)
REVIEW_CONTRACT_CONDITIONAL_WHENS = (
    "project-backed manuscript review",
    "standalone explicit-artifact review",
    "theorem-bearing claims are present",
    "theorem-bearing manuscripts are present",
)
REVIEW_CONTRACT_PREFLIGHT_CHECKS = (
    "command_context",
    "project_state",
    "knowledge_target",
    "knowledge_document",
    "knowledge_review_freshness",
    "roadmap",
    "conventions",
    "research_artifacts",
    "verification_reports",
    "manuscript",
    "artifact_manifest",
    "bibliography_audit",
    "bibliography_audit_clean",
    "compiled_manuscript",
    "publication_blockers",
    "review_ledger",
    "review_ledger_valid",
    "referee_decision",
    "referee_decision_valid",
    "publication_review_outcome",
    "reproducibility_manifest",
    "reproducibility_ready",
    "manuscript_proof_review",
    "referee_report_source",
    "phase_lookup",
    "phase_artifacts",
    "phase_summaries",
    "phase_proof_review",
)
def _join_disjunction(values: tuple[str, ...]) -> str:
    return " or ".join(f"`{value}`" for value in values)


def agent_visibility_note() -> str:
    return render_model_visible_note(
        "Agent YAML rules.",
        "`tools` is a list of tool names;",
        "`commit_authority`, `surface`, `role_family`, `artifact_write_authority`, and `shared_state_authority` "
        "must use the closed agent-authority vocabularies;",
        "the active YAML values below are authoritative for this agent.",
    )


def command_visibility_note() -> str:
    return render_model_visible_note(
        "Command YAML rules.",
        "Strict booleans; omit empty optional fields.",
        f"`{COMMAND_POLICY_PROMPT_WRAPPER_KEY}` (frontmatter `{COMMAND_POLICY_FRONTMATTER_KEY}`) uses integer "
        "`schema_version: 1`; its string lists, dotted suffixes, and active values control intake and outputs.",
        f"`context_mode` is {_join_disjunction(VALID_CONTEXT_MODES)}; `allowed_tools` is a tool-name list; "
        "`requires` accepts only `files`; `agent` is a canonical label.",
        "`project_reentry_capable: true` requires `context_mode: project-required`.",
        "Any user-visible completion, checkpoint, blocked return, failed return, retry gate, or stop that expects later "
        "action must end with `## > Next Up`; include concrete GPD commands and `gpd:suggest-next` for project-backed recovery.",
    )


def review_contract_visibility_note() -> str:
    return render_model_visible_note(
        "Review-contract YAML rules.",
        f"Use `{REVIEW_CONTRACT_PROMPT_WRAPPER_KEY}` with integer `schema_version: 1`; omit empty fields and treat "
        "the active YAML values as authoritative.",
        "Use only the closed mode/state/preflight vocabularies. Lists reject blanks and duplicates.",
        "Each `conditional_requirements[].when` is unique and needs a non-empty requirement.",
        "Each `scope_variants[].scope` is unique; `scope`/`activation` are non-empty and the variant needs an override "
        "or preflight field.",
        "Non-empty output/evidence/blocker override lists replace their top-level lists. Relaxed checks become "
        "non-blocking, optional checks make missing inputs advisory, and active scope variants apply additively.",
    )


def skeptical_rigor_guardrails_section() -> str:
    return (
        f"## {SKEPTICAL_RIGOR_GUARDRAILS_HEADING}\n\n"
        "- Use scientific skepticism and critical thinking: test contradictions, missing anchors, overclaims, failure modes, "
        "preferred interpretations, and your first impression. Agreement is not evidence.\n"
        "- Ground claims in inspected artifacts, cited sources, executed checks, or labeled background knowledge.\n"
        "- Report missing, failed, blocked, inconclusive, unverified, or unreproduced evidence plainly. Never fabricate "
        "references, numbers, derivations, artifacts, proofs, or completion, and never substitute ungrounded fallback content.\n"
        "- When certainty is not warranted, narrow the claim, lower confidence, and name the weakest remaining check.\n"
    )
