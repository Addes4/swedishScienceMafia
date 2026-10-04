# lean: bounded

Status: **RuntimeError: OpenAI network request failed; response body withheld**. Real LLM: **False**.

API ledger: `{"actual_usd": 0, "reserved_usd": 0, "committed_usd": 0, "unresolved_requests": 0, "attempts": 0, "settled_requests": 0, "input_tokens": 0, "output_tokens": 0}`.

| Gate | Mean difference vs reference | 95% case interval | Wins / ties / losses |
|---|---:|---|---|
| score_only | 0.0 | [0.0, 0.0] | 0 / 1600 / 0 |
| random_strict | 0.0 | [0.0, 0.0] | 0 / 1600 / 0 |
| strict | 0.0 | [0.0, 0.0] | 0 / 1600 / 0 |
| validated_budget | 0.0 | [0.0, 0.0] | 0 / 1600 / 0 |

Negative differences favor the candidate. Packing units are bins; circle units are negative radius sum.

Single pilot; gate controls share proposals; no causal memory or efficiency claim.


Full machine-readable results: [summary.json](summary.json). Method: [protocol.md](protocol.md).
