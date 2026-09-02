<purpose>
Delegate phase verification to one fresh `gpd-verifier` and gate the produced report.
</purpose>
<philosophy>
Fail closed on unusable project, contract, proof, or anchor state. One fresh verifier owns scientific status; its child handoff is one-shot and wrapper-gated.
</philosophy>
<shared_contract_floor>
**Project Contract Gate:** {project_contract_gate}
**Project Contract Load Info:** {project_contract_load_info}
**Project Contract Validation:** {project_contract_validation}
**Contract Intake:** {contract_intake}
**Effective Reference Intake:** {effective_reference_intake}

Treat `project_contract` as authoritative only when `project_contract_gate.authoritative` is true. A visible-but-blocked contract must be repaired before authoritative verification scope. `effective_reference_intake` is the structured source of carry-forward anchors; `active_references` and citation fields are compact routing handles. Keep bodies lazy and anchor obligations explicit.
</shared_contract_floor>

<process>

<step name="load_anchor_context">
Load this stage before using anchor, bundle, state, or verifier-handoff fields:

```bash
INVENTORY_BUILD_INIT=$(gpd --raw init verify-work "${PHASE_ARG}" --stage inventory_build)
if [ $? -ne 0 ]; then
  echo "ERROR: gpd inventory-build initialization failed: $INVENTORY_BUILD_INIT"
  # STOP; surface the error.
fi
```

<field_access>
Apply `INVENTORY_BUILD_INIT.staged_loading.field_access_instruction`; keep reference bodies lazy.
</field_access>

- Check every named benchmark, prior artifact, and must-read anchor or report why it could not be checked. Stable knowledge docs are reviewed background synthesis: use them only with stronger sources, never as decisive evidence.
</step>

<step name="load_protocol_bundle_handles">
Use `protocol_bundle_load_manifest` for targeted loading and `protocol_bundle_verifier_extensions` as the primary bundle-extension surface; call `get_bundle_checklist` only if extensions are missing. Bundles cannot replace contract or anchor checks.

For PLAN contracts with project-local anchors or prior-output paths, call `suggest_contract_checks(contract, project_dir=...)`, fill the returned `request_template` completely, and run each applicable check with `run_contract_check(request=..., project_dir=...)`.
</step>

<step name="delegate_verification">
## Delegate Verification

Spawn `gpd-verifier` once with scoped write. Pass `project_contract` only when `project_contract_gate.authoritative`; keep `active_references` as handles. It owns checks, evidence mapping, comparisons, canonical status, and gaps under `verification-status-authority.md`. Keep decisive comparison gaps legible at claim / acceptance-test / reference level; presentation headings are non-authority. Checkpoint for researcher input.

> Verifier checkpoints use `references/orchestration/continuation-boundary.md`; the wrapper starts a fresh continuation after the user responds.

Use `verification_report_finalizer_bridge` for non-gap outcomes; gap-only reports may use `verification_report_skeleton_bridge`. Validate every canonical report before routing.

Set `VERIFIER_HANDOFF_STARTED_AT=$(date -u +"%Y-%m-%dT%H:%M:%SZ")` immediately before spawning.

Prompt: "First, read {GPD_AGENTS_DIR}/gpd-verifier.md for your role and instructions." Verify Phase {phase_number}. Verification flags from the normalized parser: $VERIFY_FLAG_TEXT; flags narrow optional breadth only.

Read the phase verification, PLAN/SUMMARY/proof-redteam artifacts, STATE, and ROADMAP.

Pass staged contract/gate values, compact handles, and `{phase_proof_review_status}`; do not pass rendered reference or protocol bodies.

<selected_protocol_bundle_ids>
{selected_protocol_bundle_ids}
</selected_protocol_bundle_ids>

<protocol_bundle_load_manifest>
{protocol_bundle_load_manifest}
</protocol_bundle_load_manifest>

<protocol_bundle_verifier_extensions>
{protocol_bundle_verifier_extensions}
</protocol_bundle_verifier_extensions>

Schema finalization is bounded: validator pass returns; after the second validator failure total, including the initial failure and one repair rerun, return `gpd_return.status: blocked` with latest errors.

Run an explicitly named oracle instead of paraphrasing it:

```bash
gpd --raw verify oracle "$ORACLE_SPEC" \
  --result-output "${PHASE_DIR_ABS}/oracle-results/${ORACLE_ID}.json"
```

For literature evidence, add `--evidence-bundle "$EVIDENCE_BUNDLE"
--bundle-output "${PHASE_DIR_ABS}/evidence/${ORACLE_ID}-EVIDENCE.json"`.
Record observed/expected/tolerance; failed/error stay non-passed. Passing proves
only the encoded check. Never invent an oracle spec.

<spawn_contract>
write_scope:
  mode: scoped_write
  allowed_paths:
    - ${PHASE_DIR_ABS}/${phase_number}-VERIFICATION.md
    - ${PHASE_DIR_ABS}/oracle-results/*.json
    - ${PHASE_DIR_ABS}/evidence/*.json
expected_artifacts:
  - ${PHASE_DIR_ABS}/${phase_number}-VERIFICATION.md
shared_state_policy: return_only
</spawn_contract>

Run this `child_gate`; shared gate/continuation rules live in `references/orchestration/child-artifact-gate.md` and `references/orchestration/continuation-boundary.md`; scientific routing lives in `references/verification/verification-status-authority.md`.

```yaml
child_gate:
  id: "verify_work_verifier_report"
  role: "gpd-verifier"
  return_profile: "verifier"
  required_status: "completed"
  expected_artifacts:
    - "${PHASE_DIR_ABS}/${phase_number}-VERIFICATION.md"
  allowed_roots:
    - "${PHASE_DIR_ABS}"
  freshness_marker: "after $VERIFIER_HANDOFF_STARTED_AT"
  validators:
    - "gpd validate handoff-artifacts - --expected '${PHASE_DIR_ABS}/${phase_number}-VERIFICATION.md' --allowed-root '${PHASE_DIR_ABS}' --required-suffix=-VERIFICATION.md --require-status completed --require-files-written --fresh-after \"$VERIFIER_HANDOFF_STARTED_AT\""
    - "gpd validate verification-contract ${PHASE_DIR_ABS}/${phase_number}-VERIFICATION.md"
    - "verification-status-authority.md status rules"
    - "required proof-redteam artifacts report status: passed"
  applicator:
    command: "sync_verifier_output only after tuple passes"
    require_passed_true: false
  failure_route: "fail_closed -> gpd:verify-work ${phase_number} | repair_prompt_once | fresh_verifier_continuation_or_non_green_stop | non_green_stop_with_validator_errors"
  status_route:
    checkpoint: "fresh verifier continuation after user response"
    blocked: "non-green stop with validator errors"
    failed: "non-green stop with validator errors"
```

If runtime delegation is unavailable, fallback execution is still `gpd-verifier` work: read both report bridges, create bridge-valid body-only evidence, use the skeleton bridge only for conservative gap reports, and use `gpd verification-report finalize` for passed, `human_needed`, `expert_needed`, or typed non-gap outcomes. Do not hand-author frontmatter. Verification-report YAML must come from the skeleton/finalizer helpers; keep transcripts, hashes, oracle details, prose-only evidence, and `gpd_return` runtime return envelopes out of YAML, not in YAML. Then run `sync_verifier_output`; on validation failure, stop non-green and do not wrapper-repair the canonical report.
</step>

<step name="sync_verifier_output">
Read the verifier-produced verification file or report path.

Apply the `verify_work_verifier_report` child_gate before downstream routing.
Route only on canonical verification frontmatter plus `gpd_return.status`;
headings, marker strings, runtime success, and preexisting reports are not
authority. Every verifier-written canonical `VERIFICATION.md`, including gap or
non-green handoffs, must pass `gpd validate verification-contract` before this
wrapper accepts it. Missing, unreadable, unnamed, invalid, or failed-validation
reports stop through the tuple failure route; do not list them as authoritative,
route to gaps, enter `gap_repair`, patch frontmatter, or recompute canonical
status. Existing canonical frontmatter stays authoritative; append only the
session-local overlay here.

Load the staged researcher-session scaffold and canonical schema pack at this stage.

```bash
INTERACTIVE_VALIDATION_INIT=$(gpd --raw init verify-work "${PHASE_ARG}" --stage interactive_validation)
if [ $? -ne 0 ]; then
  echo "ERROR: gpd interactive-validation initialization failed: $INTERACTIVE_VALIDATION_INIT"
  # STOP; surface the error.
fi
```

<field_access>
Apply `INTERACTIVE_VALIDATION_INIT.staged_loading.field_access_instruction`
before reading `INTERACTIVE_VALIDATION_INIT`. Session-overlay writes stay
report-schema bounded.
</field_access>

Keep the session overlay frontmatter compatible with the authoritative verification report.
Write to `${PHASE_DIR_ABS}/${phase_number}-VERIFICATION.md`.
Changed verification files fail `gpd pre-commit-check` when this header is missing or mismatched against the active lock.
</step>

</process>
