<quick_durability_minimum>
Every completed quick task leaves a directory under GPD/quick/, a current-task PLAN.md and SUMMARY.md with actual evidence, and structured updates through `gpd state add-decision` and `gpd state update`.

For main-context work, the current agent writes and verifies those artifacts directly. Do not invent child returns. For delegated work, require the structured child `gpd_return`, current-run `files_written`, the expected child artifact gate and `gpd apply-return-updates` before applying completion state. An agent message, partial commit or stale file does not establish completion.

Run pre-commit-check for the actual changed files before a requested/configured commit; commit only the explicit task allowlist and respect commit_docs. Keep incomplete evidence and report blockers without a completion decision.
</quick_durability_minimum>
