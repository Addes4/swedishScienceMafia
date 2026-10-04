# lean: bounded

Status: **completed**. Real LLM: **True**.

API ledger: `{"actual_usd": 0.0984885, "reserved_usd": 0, "committed_usd": 0.0984885, "unresolved_requests": 0, "attempts": 12, "settled_requests": 12, "input_tokens": 21961, "output_tokens": 4412}`.

| Gate | Mean difference vs reference | 95% case interval | Wins / ties / losses |
|---|---:|---|---|
| score_only | 0.0 | [0.0, 0.0] | 0 / 1600 / 0 |
| random_strict | 0.0 | [0.0, 0.0] | 0 / 1600 / 0 |
| strict | 0.0 | [0.0, 0.0] | 0 / 1600 / 0 |
| validated_budget | 0.0 | [0.0, 0.0] | 0 / 1600 / 0 |

Negative differences favor the candidate. Packing units are bins; circle units are negative radius sum.

Single pilot; gate controls share proposals; no causal memory or efficiency claim.


Full machine-readable results: [summary.json](summary.json). Method: [protocol.md](protocol.md).
