---
load_when:
  - "research mode"
  - "explore exploit"
  - "research strategy"
  - "adaptive research"
tier: 1
context_cost: low
---

# Research Modes

Research mode controls search breadth, never correctness, evidence authority,
write scope, or required verification. It is independent of model tier,
cognitive profile, autonomy, and skill discovery. No mode prescribes a token
budget, reference count, task count, phase count, or extra agent count.

| Mode | Use |
|---|---|
| **adaptive** (default) | Infer breadth from the current task and inspected evidence. Stay focused when the method is established; compare alternatives when an unresolved choice changes the result. |
| **explore** | Investigate materially distinct viable methods and their failure modes within the approved question. |
| **balanced** | Develop a primary approach with targeted alternatives and relevant cross-checks. |
| **exploit** | Execute an established method with minimal optional enrichment. |

## Automatic selection

The user need not name a mode. Read the effective project configuration and
current contract. Preserve explicit project settings. With adaptive policy,
choose the narrowest useful work that resolves the current uncertainty; do not
start with a broad survey merely because this is the first phase. Keep
`research_mode` set to `adaptive`; infer the current posture from evidence,
without rewriting configuration on each task.

Narrow optional exploration when decisive comparisons or an explicit approach
lock stabilize the method, conventions permit comparison, and no unresolved
anchor failure or fundamental objection undermines that choice. If a benchmark
fails or a real methodological alternative emerges, broaden only the affected
question. Record a decision when it changes the research path, not for every
routine change of attention. Phase number alone is not evidence.

## Role effects

- Researcher and bibliographer: obtain enough reliable sources and comparison
  evidence to resolve the scientific question. Verify every citation actually
  used; neither pad a bibliography nor skip essential source verification.
- Planner and roadmapper: size plans and dependency waves around meaningful
  results, real dependencies, validation, and recoverable work boundaries.
  Surface alternatives before creating branches. Do not silently emit
  branch-like alternative plans, set `branch: true`, or create side-work detours.
  only explicit tangent decisions become hypothesis branches or parallel plans.
- Executor and experiment designer: choose derivation detail, parameter coverage,
  convergence studies, and uncertainty estimates from the claim and failure
  mechanisms. Exploratory estimates remain labeled estimates; narrowing a
  method never establishes its correctness or publication readiness.
- Verifier, plan-checker, and consistency-checker: preserve contract completeness,
  proof obligations, decisive anchors, forbidden proxies, direct-vs-proxy and
  formulation-critical checks. Test relevant failure modes; optional breadth
  may vary, but mode names cannot lower the contract-critical floor.
- Referee: judge the artifact against its intended claims and target venue.
  Exploratory work can have limited scope, but not fabricated or overstated
  evidence. Publication claims require the applicable supporting evidence.

## Delegation and autonomy

Under `cognitive_profile: base-model-first`, the main capable agent performs
ordinary reasoning, planning, bounded execution, and writing. Load a role body
only when that role is actually dispatched. Delegate for an independent audit,
a concrete separable task, fresh-context isolation, or explicit user request.
A required independent proof or decisive verification gate remains independent.
`research`, `plan_checker`, and `verifier` set to `auto` use their workflow's
risk classifier; they do not mean disabled.

Autonomy governs human checkpoints, not scientific rigor. Honor locked choices,
STOP conditions, write authority, and first-result/dependency gates. Ask when a
missing decision changes scope, authority, or scientific meaning; do not ask the
user to select a workflow label. Explicit model/reasoning restrictions remain in
force, including task-specific translation routes. Use the runtime's selected
capable model for main-context work without inventing a model identifier or
changing global runtime settings.

## Overrides and references

Advanced overrides remain available through `gpd config set research_mode
<mode>` and `gpd:settings`. They are not prerequisites for ordinary requests.
`research_mode` is the only persisted adaptive-mode knob; there is no separate
`adaptive_transition` block.

- `../planning/planning-config.md`: configuration schema.
- `../orchestration/model-profiles.md`: model tiers, independent of breadth.
- `../../workflows/branch-hypothesis.md`: explicitly authorized branching.

Explore and adaptive modes do **not** silently create git-backed hypothesis branches. Flag complementary approaches as tangent candidates for optional parallel investigation. Narrow on prior decisive evidence or an explicit approach lock, never on phase number alone.
