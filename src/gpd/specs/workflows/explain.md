<workflow_goal>
Explain a requested physics concept rigorously and in context. The command supports project-backed explanations and standalone explanations only when the standalone request already names an explicit target.
</workflow_goal>

<step name="validate_context">
Run centralized command-context preflight first.

```bash
CONTEXT=$(gpd --raw validate command-context explain "$ARGUMENTS")
if [ $? -ne 0 ]; then
  echo "$CONTEXT"
  exit 1
fi
```

Parse the returned JSON.

Load and follow `{GPD_INSTALL_DIR}/references/results/result-lookup-policy.md` whenever canonical result-registry lookup is needed.

- If `project_exists=true`, operate in project-context mode. If `$ARGUMENTS` is empty, ask one focused question to identify the concept, result, method, notation, or paper to explain before continuing.
- If `project_exists=false`, require an explicit concept/topic from `$ARGUMENTS` and operate in standalone mode. Do not promise that an empty standalone launch can be clarified later; centralized preflight should reject it.
- If the request is non-empty but too vague to explain meaningfully, ask one clarifying question.
- If structured citation-source fields are present in init payloads, treat them as the preferred paper catalog for follow-up links and reference IDs.
- If the concept maps to a canonical stored result, apply the shared result lookup policy before dependency tracing.
</step>

<step name="scope_request">
Determine what kind of explanation is needed.

1. Extract the core concept, method, notation, result, or paper title from `$ARGUMENTS` or from the focused clarification answer collected in project-context mode.
2. Infer the likely explanation goal:
   - Conceptual grounding for the active phase
   - Formal clarification of notation/equations
   - Method comparison before or during execution
   - Paper/context briefing
3. Choose the right depth:
   - Brief operational clarification if the request is narrow and local
   - Full conceptual + formal explanation if the request is broader or foundational
4. Generate a slug for the output file from the concept.
5. If structured citation-source metadata is available, prefer it over prose-only reference reconstruction when selecting papers to mention or link.
6. If the explanation needs canonical stored-result context, apply the shared result lookup policy.

**Important:** Do not default to a generic textbook exposition. The explanation must answer why this matters in the user's current workflow or requested standalone task.
</step>

<step name="gather_project_context">
If project context exists, gather the minimum useful context packet before spawning the explainer.

```bash
INIT=$(gpd --raw init progress --include project,state,roadmap,config --no-project-reentry)
```

Use the init payload to extract:

- Project title / milestone
- Current phase and next phase
- Whether work is paused or currently executing
- Research mode, autonomy mode, and model profile
- Any structured citation-source catalog fields such as `citation_source_files`, `citation_source_count`, and `derived_citation_sources`
- Any manuscript-local reference status surfaced as `derived_manuscript_reference_status` when the explanation is about the active paper or manuscript
- Canonical stored-result metadata plus direct, upstream, or downstream context gathered with the shared result lookup policy when the concept maps to `intermediate_results`

Search the local workspace for relevant mentions of the requested concept:

```bash
rg -n -i --fixed-strings -- "{concept}" GPD paper manuscript docs src 2>/dev/null | head -60
```

Also check for nearby high-value context when present:

- `GPD/research-map/*.md`
- Current phase `PLAN.md`, `SUMMARY.md`, `RESEARCH.md`, `VERIFICATION.md`
- `paper/`, `manuscript/`, or `draft/`
- Existing `GPD/literature/*REVIEW.md`
- Existing `GPD/literature/*-CITATION-SOURCES.json`
- Existing manuscript-local `BIBLIOGRAPHY-AUDIT.json` when available
- Existing canonical result entries and dependency context gathered with the shared result lookup policy

If no project context exists, gather only the user request plus any relevant local files in the current working directory.

Keep all GPD-authored explanation artifacts rooted under `GPD/explanations/` in the current workspace. In project-context mode, that means the resolved project root's `GPD/explanations/`; in standalone mode, it means `./GPD/explanations/` in the invoking workspace.

Create the output directory:

```bash
mkdir -p GPD/explanations
```
</step>

<step name="spawn_explainer">
The current main model writes the explanation by default, preserving the active notation and conceptual context. Do not load an explainer role for this route. If the user explicitly asks
for fresh isolation, a genuinely independent subproblem can run in parallel, or measured context pressure requires it, resolve `gpd-explainer` and load the runtime delegation convention at that time. Record the concrete reason; a role's existence is not a reason to spawn.

```markdown
<objective>
Explain the following concept rigorously and in context: {concept}
</objective>

<mode>
{project-context or standalone}
</mode>

<available_context>
- User request: {raw request}
- Project summary / roadmap / state excerpts when available
- Current phase, manuscript, or active process context when available
- Relevant local files and `rg` hits mentioning the concept
- Local conventions and notation artifacts when available
</available_context>

<requirements>
1. Start with the short answer in one paragraph.
2. Explain why this concept matters in the current project or requested task.
3. Include prerequisite definitions only when needed to understand the requested concept.
4. Give the rigorous core: definition, physical meaning, assumptions, limits, and equations/derivation where needed.
5. Connect the concept to this project's files, conventions, current phase, or manuscript claims when available.
6. Distinguish established literature facts from project-specific assumptions or interpretations.
7. If structured citation-source metadata is available, use it to keep the literature guide tied to stable `reference_id` entries and openable URLs.
8. If canonical stored-result context is available, use the direct, dependency, or impact context gathered by the shared result lookup policy.
9. Include sources when requested or when factual attribution requires them; do not add a literature survey to a local notation clarification. Prefer openable primary-source links.
10. Never fabricate citations. If a reference is uncertain, mark it clearly as unverified instead of guessing.
11. Include common confusions or follow-up questions only when they help the current request.
</requirements>

<output>
Write to: GPD/explanations/{slug}-EXPLAIN.md

Use only the sections needed by the requested depth; retain the frontmatter and the core explanation. Possible sections:

- Frontmatter (`concept`, `date`, `mode`, `project_context`, `citation_status`)
- Executive Summary
- Why This Matters Here
- Prerequisites and Dependencies
- Core Explanation
- Formal Structure / Equations
- Project-Specific Connection
- Common Confusions and Failure Modes
- Literature Guide
  - Foundational papers
  - Practical/working references
  - Current frontier
- Suggested Follow-up Questions
</output>
```

For the ordinary main-context route, execute `filled_prompt` in the
current main context and write `GPD/explanations/{slug}-EXPLAIN.md` directly.
Then continue to citation verification; do not invent a child id or typed
child return for this route.

For a fresh-context route:

```
task(
  prompt=filled_prompt,
  subagent_type="gpd-explainer",
  model="{explainer_model}",
  readonly=false,
  description="Explain {slug}"
)
```
</step>

<step name="verify_citations">
Inspect the actual explanation for citations. If there are none, record `citation_status: not_applicable`; no bibliographer or empty audit is needed. Do not use this route to omit sources necessary to substantiate factual claims.

For ordinary explanations with a bounded, directly verifiable reference set, the main agent checks authoritative metadata and exact claim support, records sources and findings in `GPD/explanations/{slug}-CITATION-AUDIT.md`, and sets citation status from actual evidence. Unavailable sources remain unverified.

Use a fresh independent bibliographer when requested, when source/claim conflicts remain, or when a substantial literature synthesis needs independent review. The following delegation is conditional on that need; do not invent a child id for a direct audit.

Resolve bibliographer model:

```bash
BIBLIO_MODEL=$(gpd resolve-model gpd-bibliographer)
```

Before the first actual delegation, load `{GPD_INSTALL_DIR}/references/orchestration/runtime-delegation-note.md` and follow its runtime convention.

```
task(
  subagent_type="gpd-bibliographer",
  model="{biblio_model}",
  readonly=false,
  prompt="First, read {GPD_AGENTS_DIR}/gpd-bibliographer.md for your role and instructions.

Audit the citations in `GPD/explanations/{slug}-EXPLAIN.md`.

For every citation anywhere in the explanation, including inline citations and its associated claim:
1. Verify that the reference is real and supports the exact associated claim; inspect source text, not only topical metadata
2. Check title, authors, year, journal/arXiv metadata, and openable URL
3. Flag hallucinated, inaccurate, or weakly supported references
4. Write the audit to `GPD/explanations/{slug}-CITATION-AUDIT.md`

Return a typed `gpd_return` envelope. Use `status: completed` when the audit finished, even if the human-readable heading is `## CITATION ISSUES FOUND`; use `status: checkpoint` only when researcher input is required to continue."
)
```

If the bibliographer completed with issues recorded in the audit report:

- Read the audit report
- Correct metadata in the explanation file where the fix is straightforward
- Remove or explicitly flag unresolved references
- Preserve the explanation, but never leave fabricated citations unmarked

If the bibliographer step fails entirely:

- Keep the explanation
- Set citation status to unverified in the final report
- Tell the user which file still needs manual checking
</step>

<step name="return_results">
Return to the orchestrator with:

- Explanation summary (3-6 lines)
- Report path
- Project anchor (current phase / manuscript / standalone)
- Citation verification status
- Papers to open next only when sources were relevant to the request

Format:

```markdown
## EXPLANATION COMPLETE

**Concept:** {concept}
**Report:** GPD/explanations/{slug}-EXPLAIN.md
**Project anchor:** {current phase / manuscript / standalone}
**Citation verification:** {not_applicable | all verified | issues found in GPD/explanations/{slug}-CITATION-AUDIT.md | unverified}

**Key takeaways:**

1. {takeaway}
2. {takeaway}
3. {takeaway}

**Papers to open next (omit when not applicable):**

1. {paper title} — {url}
2. {paper title} — {url}
3. {paper title} — {url}
```

If the concept remains ambiguous or critical context is missing:

```markdown
## CHECKPOINT REACHED

**Type:** clarification
**Need:** {what disambiguation is required}
**Why it matters:** {how the explanation would change}
```
</step>
