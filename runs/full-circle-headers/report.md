# full: circle

Status: **completed**. Real LLM: **True**.

API ledger: `{"actual_usd": 1.10101795, "reserved_usd": 0, "committed_usd": 1.10101795, "unresolved_requests": 0, "attempts": 31, "settled_requests": 31, "input_tokens": 85122, "output_tokens": 41148}`.

| Gate | Mean difference vs reference | 95% case interval | Wins / ties / losses |
|---|---:|---|---|
| score_only | -1.6867201246659427 | [-1.7583151435720283, -1.6126948599574398] | 5 / 0 / 0 |
| random_strict | -1.6867201246659427 | [-1.7583151435720283, -1.6126948599574398] | 5 / 0 / 0 |
| strict | -1.6867201246659427 | [-1.7583151435720283, -1.6126948599574398] | 5 / 0 / 0 |
| validated_budget | -1.6867201246659427 | [-1.7583151435720283, -1.6126948599574398] | 5 / 0 / 0 |

Negative differences favor the candidate. Packing units are bins; circle units are negative radius sum.

Single pilot; gate controls share proposals; no causal memory or efficiency claim.


Full machine-readable results: [summary.json](summary.json). Method: [protocol.md](protocol.md).
