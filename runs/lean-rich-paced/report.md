# lean: rich

Status: **RuntimeError: OpenAI HTTP 429; code=rate_limit_exceeded; response body withheld**. Real LLM: **True**.

API ledger: `{"actual_usd": 0.0583435, "reserved_usd": 0.075, "committed_usd": 0.1333435, "unresolved_requests": 1, "attempts": 8, "settled_requests": 7, "input_tokens": 9759, "output_tokens": 3488}`.

| Gate | Mean difference vs reference | 95% case interval | Wins / ties / losses |
|---|---:|---|---|
| score_only | -6.3 | [-7.1000000000000005, -5.6] | 19 / 1 / 0 |
| random_strict | -6.3 | [-7.1000000000000005, -5.6] | 19 / 1 / 0 |
| strict | -6.3 | [-7.1000000000000005, -5.6] | 19 / 1 / 0 |
| validated_budget | -6.3 | [-7.1000000000000005, -5.6] | 19 / 1 / 0 |

Negative differences favor the candidate. Packing units are bins; circle units are negative radius sum.

Single pilot; gate controls share proposals; no causal memory or efficiency claim.


Full machine-readable results: [summary.json](summary.json). Method: [protocol.md](protocol.md).
