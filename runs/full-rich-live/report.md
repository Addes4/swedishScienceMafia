# full: rich

Status: **RuntimeError: OpenAI HTTP 429; code=rate_limit_exceeded; response body withheld**. Real LLM: **True**.

API ledger: `{"actual_usd": 0.2122048, "reserved_usd": 0.075, "committed_usd": 0.2872048, "unresolved_requests": 1, "attempts": 18, "settled_requests": 17, "input_tokens": 26693, "output_tokens": 8815}`.

| Gate | Mean difference vs reference | 95% case interval | Wins / ties / losses |
|---|---:|---|---|
| score_only | -8.0 | [-9.15, -6.949999999999999] | 18 / 2 / 0 |
| random_strict | -8.0 | [-9.15, -6.949999999999999] | 18 / 2 / 0 |
| strict | 0.0 | [0.0, 0.0] | 0 / 20 / 0 |
| validated_budget | -8.0 | [-9.15, -6.949999999999999] | 18 / 2 / 0 |

Negative differences favor the candidate. Packing units are bins; circle units are negative radius sum.

Single pilot; gate controls share proposals; no causal memory or efficiency claim.


Full machine-readable results: [summary.json](summary.json). Method: [protocol.md](protocol.md).
