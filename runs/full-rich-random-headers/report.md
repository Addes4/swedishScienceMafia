# full: rich

Status: **completed**. Real LLM: **True**.

API ledger: `{"actual_usd": 0.34615365, "reserved_usd": 0, "committed_usd": 0.34615365, "unresolved_requests": 0, "attempts": 25, "settled_requests": 25, "input_tokens": 54166, "output_tokens": 13004}`.

| Gate | Mean difference vs reference | 95% case interval | Wins / ties / losses |
|---|---:|---|---|
| score_only | -1.95 | [-2.6, -1.4000000000000001] | 10 / 8 / 2 |
| random_strict | -1.95 | [-2.6, -1.4000000000000001] | 10 / 8 / 2 |
| strict | -1.95 | [-2.6, -1.4000000000000001] | 10 / 8 / 2 |
| validated_budget | -1.95 | [-2.6, -1.4000000000000001] | 10 / 8 / 2 |

Negative differences favor the candidate. Packing units are bins; circle units are negative radius sum.

Single pilot; gate controls share proposals; no causal memory or efficiency claim.


Full machine-readable results: [summary.json](summary.json). Method: [protocol.md](protocol.md).
