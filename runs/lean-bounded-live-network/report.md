# lean: bounded

Status: **RuntimeError: OpenAI HTTP 429; response body withheld**. Real LLM: **True**.

API ledger: `{"actual_usd": 0.0223565, "reserved_usd": 0.03548, "committed_usd": 0.0578365, "unresolved_requests": 1, "attempts": 5, "settled_requests": 4, "input_tokens": 3641, "output_tokens": 1379}`.

| Gate | Mean difference vs reference | 95% case interval | Wins / ties / losses |
|---|---:|---|---|
| score_only | 0.0 | [0.0, 0.0] | 0 / 1600 / 0 |
| random_strict | 0.0 | [0.0, 0.0] | 0 / 1600 / 0 |
| strict | 0.0 | [0.0, 0.0] | 0 / 1600 / 0 |
| validated_budget | 0.0 | [0.0, 0.0] | 0 / 1600 / 0 |

Negative differences favor the candidate. Packing units are bins; circle units are negative radius sum.

Single pilot; gate controls share proposals; no causal memory or efficiency claim.


Full machine-readable results: [summary.json](summary.json). Method: [protocol.md](protocol.md).
