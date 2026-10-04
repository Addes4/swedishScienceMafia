# full: circle

Status: **RuntimeError: OpenAI HTTP 429; code=rate_limit_exceeded; response body withheld**. Real LLM: **True**.

API ledger: `{"actual_usd": 0.239357375, "reserved_usd": 0.03548, "committed_usd": 0.274837375, "unresolved_requests": 1, "attempts": 11, "settled_requests": 10, "input_tokens": 13085, "output_tokens": 10257}`.

| Gate | Mean difference vs reference | 95% case interval | Wins / ties / losses |
|---|---:|---|---|
| score_only | -1.6746905700505728 | [-1.7358284680279013, -1.6144469979949925] | 5 / 0 / 0 |
| random_strict | -1.6746905700505728 | [-1.7358284680279013, -1.6144469979949925] | 5 / 0 / 0 |
| strict | -1.6746905700505728 | [-1.7358284680279013, -1.6144469979949925] | 5 / 0 / 0 |
| validated_budget | -1.6746905700505728 | [-1.7358284680279013, -1.6144469979949925] | 5 / 0 / 0 |

Negative differences favor the candidate. Packing units are bins; circle units are negative radius sum.

Single pilot; gate controls share proposals; no causal memory or efficiency claim.


Full machine-readable results: [summary.json](summary.json). Method: [protocol.md](protocol.md).
