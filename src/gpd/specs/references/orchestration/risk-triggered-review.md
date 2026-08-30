# Risk-Triggered Workflow Agents

This reference defines the `"auto"` policy for `workflow.research`,
`workflow.plan_checker`, `workflow.verifier`, and
`execution.checkpoint_before_downstream_dependent_tasks`.

The policy separates reasoning depth from process repetition. `model_profile`
continues to control the capability and internal rigor of the main planner and
executor. `auto` controls only whether an additional independent agent or
bounded review gate is justified by current evidence.

## Shared Rules

1. Do not activate an independent agent solely because the profile is
   `deep-theory`, the phase contains equations, or an optional artifact is
   absent.
2. Explicit user requests for an audit, independent check, literature review,
   proof check, or publication-ready validation always activate the relevant
   route.
3. A result is **load-bearing** when a later task, phase, claim, expensive run,
   or manuscript conclusion would assume it is correct.
4. A fresh equivalent check clears a risk signal. Do not repeat the same check
   at the first-result, pre-fanout, plan-checker, and verifier gates unless the
   result, assumptions, convention lock, source anchor, or dependent claim has
   materially changed.
5. Record each automatic decision as `auto_route: run|skip`, its trigger or
   skip reason, the result fingerprint or artifact used for deduplication, and
   any uncleared risk. Do not interrupt the user for a clean automatic skip.
6. Skipping an independent agent does not promote evidence. Ordinary outputs
   remain `working` or `candidate`; only an applicable accepted check may
   promote them to `validated`, `independently_confirmed`, or publication-ready.
7. Proof-bearing work keeps its mandatory proof-redteam route. `auto` never
   weakens proof-obligation detection or substitutes self-review for an
   independent proof audit.

## Researcher Auto Route

Run the independent phase researcher only when at least one condition holds:

- the user explicitly requests research, discovery, literature coverage, or
  comparison of approaches;
- the plan must choose between materially different formalisms or methods and
  current project evidence does not settle the choice;
- a literature attribution, novelty claim, canonical equation, empirical
  anchor, or method provenance is required but missing or plausibly stale;
- an unresolved domain-knowledge gap prevents the main planner from writing an
  executable plan;
- the roadmap or phase contract explicitly makes discovery, literature review,
  or method comparison a deliverable.

Otherwise skip the child researcher. The tier-1 main planner may still perform
bounded source lookup and full theoretical reasoning inside the requested
scope; `auto` is not a ban on research.

## Plan-Checker Auto Route

Run the independent plan checker only when at least one condition holds:

- the user explicitly requests a careful or independent plan audit;
- the fresh plan is proof-bearing;
- execution is expensive, irreversible, externally mutating, or has a broad
  numerical/experimental fanout;
- multiple plans have load-bearing dependencies whose acceptance tests or
  convention handoffs are unresolved;
- the plan would promote a result to validated/canonical status or directly
  support a manuscript-level claim;
- a known contradiction, sign ambiguity, convention conflict, uncontrolled
  approximation, or prior failed verification remains open.

Otherwise rely on the main planner's structured contract/preflight validators
and skip the independent checker.

## Verifier Auto Route

Run the independent verifier only when at least one condition holds:

- the user explicitly requests careful verification, an independent check, or
  a final audit;
- a new result is about to become load-bearing and no fresh equivalent
  independent check has cleared it;
- the phase claims validated, canonical, accepted, complete, publication-ready,
  or independently-confirmed status;
- the result contradicts a prior phase, source, limiting case, conservation
  law, convention lock, or independent calculation;
- proof-redteam, execution, or consistency evidence leaves an unresolved
  material issue.

Otherwise skip the generic verifier, preserve candidate status, and continue
only along routes that do not require stronger evidence.

## Downstream Checkpoint Deduplication

With `execution.checkpoint_before_downstream_dependent_tasks="auto"`, require a
pre-dependent gate only when a downstream task would consume an uncleared
load-bearing result. Reuse a fresh first-result, proof-redteam, targeted
independent cross-check, or verifier pass when it covers the same result,
assumptions, conventions, and claim scope. Log `deduplicated_against` and do not
ask the user to approve the same unchanged result twice.
