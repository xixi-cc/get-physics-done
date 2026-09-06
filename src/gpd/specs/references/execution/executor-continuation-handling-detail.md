If spawned as a continuation, first read `state.json` convention_lock, verify
prior artifacts/log entries/reported values, skip completed tasks, and resume at
the provided cursor. If another checkpoint hits, return cumulative completed
tasks and research state, then stop.
