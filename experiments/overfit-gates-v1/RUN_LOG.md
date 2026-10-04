# overfit-gates-v1: run log

Times are BST, from `date` on the machine.

- Sun Oct  4 01:48:44 BST 2026: PROTOCOL.md frozen before any scoring. SHA-256 `9675d9f9131c5b0c0f7dcfa3252489e2739d5bfff95c4ac42c48d161599271b8`.
- Sun Oct  4 01:50:10 BST 2026: positive control 1 passed (6/6 programs, 3 promoted, bins and packing hashes identical; control.json). Starting pool scoring, 2 workers, load 21.61 19.62 14.10.
- Sun Oct  4 02:53:41 BST 2026: pool scoring finished (206 groups). Starting dedup check then archive scoring, 2 workers, load 4.96 5.64 10.00.
- Sun Oct  4 02:53:45 BST 2026: pool scoring finished (206/206 groups, 0 errors, 6,707 CPU-seconds in workers). The chained dedup/archive command had exited without output, so they were started by hand with 3 workers (load 4.88 5.61 9.96, below the protocol's threshold of 6).
- Sun Oct  4 02:54:42 BST 2026: dedup (36 jobs, 3 workers) and archive scoring (2 workers; load had risen above 6) finished.
- Sun Oct  4 02:54:42 BST 2026: dedup and archive scoring finished.
- Sun Oct  4 02:55:08 BST 2026: **Correction to the two lines above.** The chained command I believed had died was
  still waiting on the pool. At 02:53:41 it started its own dedup and archive runs (2 workers)
  at the same time as my manual runs (3 workers, then 2). For about a minute up to 5 scoring
  processes ran together, and the result files got duplicate rows: archive 400 rows for 255 keys,
  dedup 74 rows for 38 keys. Every duplicate was identical (bins and packing hashes), because
  scoring is deterministic. Duplicates were dropped, keeping the first row per key. The dedup
  check has 38 rows rather than 36 or 40, because the two concurrent runs read different
  `done` sets; the analysis uses pairs that have both members.
