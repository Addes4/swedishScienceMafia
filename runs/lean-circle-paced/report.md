# lean: circle

Status: **RuntimeError: OpenAI HTTP 429; code=rate_limit_exceeded; response body withheld**. Real LLM: **True**.

API ledger: `{"actual_usd": 0.1432255, "reserved_usd": 0.075, "committed_usd": 0.21822550000000002, "unresolved_requests": 1, "attempts": 8, "settled_requests": 7, "input_tokens": 14010, "output_tokens": 10856}`.

| Gate | Mean difference vs reference | 95% case interval | Wins / ties / losses |
|---|---:|---|---|
| score_only | -1.6461888861006078 | [-1.6974410776249882, -1.5949366945762269] | 5 / 0 / 0 |
| random_strict | -1.6461888861006078 | [-1.6974410776249882, -1.5949366945762269] | 5 / 0 / 0 |
| strict | -1.6461888861006078 | [-1.6974410776249882, -1.5949366945762269] | 5 / 0 / 0 |
| validated_budget | -1.6461888861006078 | [-1.6974410776249882, -1.5949366945762269] | 5 / 0 / 0 |

Negative differences favor the candidate. Packing units are bins; circle units are negative radius sum.

Single pilot; gate controls share proposals; no causal memory or efficiency claim.


Full machine-readable results: [summary.json](summary.json). Method: [protocol.md](protocol.md).
