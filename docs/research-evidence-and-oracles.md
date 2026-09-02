# Research evidence and executable oracles

GPD uses a small evidence exchange format for claim-bearing literature and
verification workflows. It complements rather than replaces the existing
project contract and `VerificationEvidence` models.

An `EvidenceBundle` v1 contains locator-only `ResearchEvidence` records and
optional claim links. Relations are `supports`, `contradicts`, `limits`, or
`derived_from`. Source bodies remain in their original files and are loaded only
when needed.

Convert an audited literature-review citation sidecar:

```bash
gpd --raw evidence literature \
  GPD/literature/topic-CITATION-SOURCES.json \
  --claim-evidence GPD/literature/topic-CLAIM-EVIDENCE.json \
  --output GPD/literature/topic-EVIDENCE.json
```

The claim-evidence bundle is optional for a standalone review. It carries the
page/equation/figure/data-level records and links for decisive claims; every
`evidence_id` must resolve inside that bundle.

## Oracle specifications

`gpd verify oracle` accepts one closed JSON object using a `python`, `pytest`,
or `numeric-tolerance` runner.

```json
{
  "runner": "numeric-tolerance",
  "oracle_id": "small-q-limit",
  "check_id": "5.3",
  "claim_id": "claim-dispersion",
  "acceptance_test_id": "test-small-q",
  "evidence_ids": ["ref-dispersion"],
  "observed": 0.501,
  "expected": 0.5,
  "atol": 0.01,
  "rtol": 0.0
}
```

Run it and extend the evidence chain:

```bash
gpd --raw verify oracle GPD/oracles/small-q.json \
  --result-output GPD/verification/small-q-RESULT.json \
  --evidence-bundle GPD/literature/topic-EVIDENCE.json \
  --bundle-output GPD/verification/small-q-EVIDENCE.json
```

Python callables use `module:function` plus JSON `args` and `kwargs`. Pytest
specifications name explicit test nodes. The runner records observed values,
expected values, and execution status; a passing oracle establishes only its
encoded acceptance condition.

Four bounded executable examples live under `evals/research_smoke/`.
