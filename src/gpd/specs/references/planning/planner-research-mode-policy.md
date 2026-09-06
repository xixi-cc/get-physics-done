# Planner Research Mode Policy

Research mode controls breadth, not correctness. All modes must preserve
contract completeness, proof obligations, anchors, forbidden proxies,
acceptance tests, and physics verification.

## Explore Mode (`research_mode: "explore"`)

Use when the problem domain is new, the best approach is unknown, or multiple
methods remain viable.

- Identify materially distinct viable approaches during planning analysis.
- Do not silently emit branch-like alternative plans, set `branch: true`, or
  create side-work detours from explore mode alone.
- If the user has not chosen a tangent route, keep viable methods provisional within the authorized objective. Ask only
  when their choice changes scope, a locked assumption or required authority.
- Load research needed to distinguish live methods, including decisive
  tradeoffs, known failures and precedent; reuse sufficient existing evidence.
- Compare methods within the approved objective when needed to resolve it.
  Creating a separate hypothesis branch or side investigation retains its scope gate.

## Balanced Mode (`research_mode: "balanced"`)

Use for standard research when one approach is reasonably clear.

- Create one primary plan.
- Mention alternatives as plan context rather than separate plans.
- Use targeted literature coverage around the selected method.
- Select informative cross-checks for the actual result; honor required
  limiting cases, conventions, convergence evidence and contract anchors.
- Route failed or newly viable alternatives through the tangent decision model.

## Exploit Mode (`research_mode: "exploit"`)

Use for well-known methods, extensions of previous work, routine calculations,
or production runs.

- Create one focused plan with minimal optional enrichment.
- Skip broad researcher work when the method is established in CONTEXT.md or
  prior phases.
- Use narrow literature: exact process, exact method, exact order.
- Suppress optional tangents unless the approved contract, anchor, or
  physics-validity path is blocked.
- Keep decisive acceptance tests, required anchors, forbidden-proxy handling,
  and the primary observable explicit.

## Adaptive Mode (`research_mode: "adaptive"`)

Use for multi-phase projects where approach choice may evolve.

- Use the current uncertainty to choose breadth. Start focused when the method
  and evidence are already sufficient; broaden only for a real unresolved choice.
- Reuse existing research only when it covers the exact method family, anchors,
  and decisive evidence path.
- Do not infer narrowing from phase number alone.
- If a later phase hits a physics redirect, temporarily revert to explore mode
  for that phase.

## Reading The Mode

Read `research_mode` from the planner handoff. If absent, default to
`adaptive`.
