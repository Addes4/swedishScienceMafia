# lean: circle

Status: **completed**. Real LLM: **True**.

API ledger: `{"actual_usd": 2.2774199999999998, "reserved_usd": 0, "committed_usd": 2.2774199999999998, "unresolved_requests": 0, "attempts": 18, "settled_requests": 18, "input_tokens": 47496, "output_tokens": 33712}`.

| Gate | Mean difference vs reference | 95% case interval | Wins / ties / losses |
|---|---:|---|---|
| score_only | -1.7048286609086953 | [-1.755876585305219, -1.6537807365121715] | 5 / 0 / 0 |
| random_strict | -1.7048286609086953 | [-1.755876585305219, -1.6537807365121715] | 5 / 0 / 0 |
| strict | -1.7048286609086953 | [-1.755876585305219, -1.6537807365121715] | 5 / 0 / 0 |
| validated_budget | -1.7048286609086953 | [-1.755876585305219, -1.6537807365121715] | 5 / 0 / 0 |

Negative differences favor the candidate. Packing units are bins; circle units are negative radius sum.

Single pilot; gate controls share proposals; no causal memory or efficiency claim.


Full machine-readable results: [summary.json](summary.json). Method: [protocol.md](protocol.md).
