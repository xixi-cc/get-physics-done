<purpose>
Verify review completion and sidecar freshness before presenting results.
</purpose>

<process>

<step name="return_results">
Apply `references/orchestration/child-artifact-gate.md` and `references/orchestration/continuation-boundary.md` for generic typed-return, label, freshness, and continuation semantics.

```bash
COMPLETION_GATE_INIT=$(load_literature_review_stage completion_gate "${topic:-$ARGUMENTS}")
if [ $? -ne 0 ]; then
  echo "ERROR: gpd initialization failed: $COMPLETION_GATE_INIT"
  exit 1
fi
```

Apply `COMPLETION_GATE_INIT.staged_loading.field_access_instruction` before reading `COMPLETION_GATE_INIT` and presenting results.

Local completion gate:

- completed: review, aligned `CITATION-SOURCES.json`, current `CITATION-AUDIT.md`, and parseable `EVIDENCE.json` v1 are present and named by their producing handoffs. Require `CLAIM-EVIDENCE.json` only for bound authoritative claims.
- checkpoint: include the decision question, context, options, and partial progress; record the user's answer as `checkpoint_response` before continuation.
- blocked/failed: list the missing artifact, malformed artifact, stale audit, or unresolved scope issue explicitly.

Include `papers_reviewed`, `field_assessment`, and citation verification details as needed.

</step>

</process>

<success_criteria>

- [ ] Source hierarchy followed (textbooks -> reviews -> papers -> arXiv -> web)
- [ ] Foundational works identified with key contributions
- [ ] Methods cataloged with regimes, limitations, and key references
- [ ] Results tabulated with uncertainties and conventions
- [ ] Citation network traced showing intellectual development
- [ ] Controversies and disagreements documented
- [ ] Open questions identified with feasibility assessment
- [ ] Current frontier mapped (recent results, active groups, emerging methods)
- [ ] Conventions cataloged across references
- [ ] LITERATURE-REVIEW.md created with all sections
- [ ] Recommended reading path provided
- [ ] Citations verified via gpd-bibliographer (no hallucinated references)
- [ ] Compact `EVIDENCE.json` emitted from the audited citation sidecar

</success_criteria>
