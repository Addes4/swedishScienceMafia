# full: rich

Status: **completed**. Real LLM: **True**.

API ledger: `{"actual_usd": 0.340938575, "reserved_usd": 0, "committed_usd": 0.340938575, "unresolved_requests": 0, "attempts": 32, "settled_requests": 32, "input_tokens": 59713, "output_tokens": 15933}`.

| Gate | Mean difference vs reference | 95% case interval | Wins / ties / losses |
|---|---:|---|---|
| score_only | -5.7 | [-6.6, -4.8] | 14 / 5 / 1 |
| random_strict | -4.5 | [-5.45, -3.5999999999999996] | 19 / 1 / 0 |
| strict | -5.7 | [-6.6, -4.8] | 14 / 5 / 1 |
| validated_budget | -5.7 | [-6.6, -4.8] | 14 / 5 / 1 |

Negative differences favor the candidate. Packing units are bins; circle units are negative radius sum.

Single pilot; gate controls share proposals; no causal memory or efficiency claim.


Full machine-readable results: [summary.json](summary.json). Method: [protocol.md](protocol.md).
