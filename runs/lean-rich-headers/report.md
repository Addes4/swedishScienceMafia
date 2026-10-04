# lean: rich

Status: **completed**. Real LLM: **True**.

API ledger: `{"actual_usd": 0.1486235, "reserved_usd": 0, "committed_usd": 0.1486235, "unresolved_requests": 0, "attempts": 18, "settled_requests": 18, "input_tokens": 30726, "output_tokens": 7277}`.

| Gate | Mean difference vs reference | 95% case interval | Wins / ties / losses |
|---|---:|---|---|
| score_only | -0.35 | [-0.8, 0.15000000000000002] | 8 / 9 / 3 |
| random_strict | -0.35 | [-0.8, 0.15000000000000002] | 8 / 9 / 3 |
| strict | -0.35 | [-0.8, 0.15000000000000002] | 8 / 9 / 3 |
| validated_budget | -0.35 | [-0.8, 0.15000000000000002] | 8 / 9 / 3 |

Negative differences favor the candidate. Packing units are bins; circle units are negative radius sum.

Single pilot; gate controls share proposals; no causal memory or efficiency claim.


Full machine-readable results: [summary.json](summary.json). Method: [protocol.md](protocol.md).
