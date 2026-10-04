# lean: rich

Status: **RuntimeError: OpenAI HTTP 429; response body withheld**. Real LLM: **True**.

API ledger: `{"actual_usd": 0.011162, "reserved_usd": 0.075, "committed_usd": 0.086162, "unresolved_requests": 1, "attempts": 3, "settled_requests": 2, "input_tokens": 6816, "output_tokens": 4873}`.

| Gate | Mean difference vs reference | 95% case interval | Wins / ties / losses |
|---|---:|---|---|
| score_only | 0.0 | [0.0, 0.0] | 0 / 20 / 0 |
| random_strict | 0.0 | [0.0, 0.0] | 0 / 20 / 0 |
| strict | 0.0 | [0.0, 0.0] | 0 / 20 / 0 |
| validated_budget | 0.0 | [0.0, 0.0] | 0 / 20 / 0 |

Negative differences favor the candidate. Packing units are bins; circle units are negative radius sum.

Single pilot; gate controls share proposals; no causal memory or efficiency claim.


Full machine-readable results: [summary.json](summary.json). Method: [protocol.md](protocol.md).
