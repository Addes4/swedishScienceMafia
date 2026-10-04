# lean: bounded

Status: **RuntimeError: OpenAI HTTP 429; code=rate_limit_exceeded; response body withheld**. Real LLM: **True**.

API ledger: `{"actual_usd": 0.0744595, "reserved_usd": 0.03548, "committed_usd": 0.1099395, "unresolved_requests": 1, "attempts": 11, "settled_requests": 10, "input_tokens": 17029, "output_tokens": 3244}`.

| Gate | Mean difference vs reference | 95% case interval | Wins / ties / losses |
|---|---:|---|---|
| score_only | 0.0 | [0.0, 0.0] | 0 / 1600 / 0 |
| random_strict | 0.0 | [0.0, 0.0] | 0 / 1600 / 0 |
| strict | 0.0 | [0.0, 0.0] | 0 / 1600 / 0 |
| validated_budget | 0.0 | [0.0, 0.0] | 0 / 1600 / 0 |

Negative differences favor the candidate. Packing units are bins; circle units are negative radius sum.

Single pilot; gate controls share proposals; no causal memory or efficiency claim.


Full machine-readable results: [summary.json](summary.json). Method: [protocol.md](protocol.md).
