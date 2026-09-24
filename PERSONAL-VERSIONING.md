# Personal GPD version policy

This repository treats the personal GPD line as the only deployable runtime.
The official `origin` repository is an upstream evidence source: its releases
and commits are reviewed and selectively integrated, but are never installed
directly on either host.

## Version identity

Every promoted personal release has four independent identifiers:

1. upstream package baseline, such as `1.2.2`;
2. personal release tag, such as `xixi-v1.2.2-astra.20260906.1`;
3. the Git commit resolved by that tag;
4. the SHA-256 of the built wheel and source archive.

The Python package version remains aligned with upstream unless the personal
release process is deliberately changed to support PEP 440 local versions.
Consequently, `gpd --version` alone is not sufficient to identify a personal
release. `~/.gpd/ACTIVE-SOURCE.json` and the release receipt are authoritative.

## Branch roles

- `origin/main`: read-only official upstream tracking branch.
- `local/astra-current`: local promotion worktree for the personal stable line.
- `personal/main`: remote personal stable line and deployment authority.
- `local/dev` (published as `personal/dev`): integration line for local work and selected upstream changes.
- `feature/*`: bounded experiments or fixes based on `personal/dev`.
- `archive/*`: retained historical research branches that are not deployment candidates.

Existing historical local branches remain evidence until they are deliberately
archived. Their recency, directory name, or modification time does not make them
deployable.

## Promotion and deployment

1. Fetch official references without modifying the running environment.
2. Review upstream changes and integrate only selected changes into `personal/dev`.
3. Run the repository tests and the Astra-specific workflow checks.
4. Fast-forward `personal/main` to the accepted commit.
5. Create an annotated `xixi-v...` tag and immutable release receipt.
6. Build one wheel and one source archive; record their SHA-256 values.
7. Install the exact same wheel on local WSL and `office-ubuntu`.
8. Verify version output, package-tree equality, receipt equality, and smoke checks.

"Latest local version" means the newest promoted and verified personal release,
not the newest dirty working tree or the newest official release.

## Current promoted release

- Historical rollout label: `personal-astra-theory-20260906`
- Formal personal tag: `xixi-v1.2.2-astra.20260924.2`
- Upstream package baseline: `1.2.2`
- Astra optimization completed: 2026-09-06
- Version governance and dual-host promotion completed: 2026-09-07
- Skill discovery description release: 2026-09-24
- Baseline test contract repair and full-suite validation: 2026-09-24
