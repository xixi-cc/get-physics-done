# GPD thinning capability evaluation

This harness compares prompt and orchestration slices without exposing scoring
anchors to the model under test.

- `fixtures/canary-v1/public.jsonl` is the only task source copied into a run
  bundle.
- `fixtures/canary-v1/private-oracles.jsonl` stays outside the model workspace
  and is used only after artifacts are sealed.
- `prepare_bundle.py` validates both halves, copies only public tasks, and writes
  a hash-backed manifest.
- Theory reviews use all eight rubric dimensions on a 0--4 scale. Answer length
  is not a scoring dimension.

The 12-task canary is the first subset of the planned 48-task matrix: two
state/authority tasks, four deep-theory tasks, three theory-construction tasks,
two numerical tasks, and one citation task.
