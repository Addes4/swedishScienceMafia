# lean: circle

Status: **RuntimeError: OpenAI HTTP 429; response body withheld**. Real LLM: **True**.

API ledger: `{"actual_usd": 0.030948000000000003, "reserved_usd": 0.075, "committed_usd": 0.105948, "unresolved_requests": 1, "attempts": 3, "settled_requests": 2, "input_tokens": 6234, "output_tokens": 4565}`.

| Gate | Mean difference vs reference | 95% case interval | Wins / ties / losses |
|---|---:|---|---|
| score_only | -1.6412324606603523 | [-1.6995337081095883, -1.5847071914719408] | 5 / 0 / 0 |
| random_strict | -1.6412324606603523 | [-1.6995337081095883, -1.5847071914719408] | 5 / 0 / 0 |
| strict | -1.6412324606603523 | [-1.6995337081095883, -1.5847071914719408] | 5 / 0 / 0 |
| validated_budget | -1.6412324606603523 | [-1.6995337081095883, -1.5847071914719408] | 5 / 0 / 0 |

Negative differences favor the candidate. Packing units are bins; circle units are negative radius sum.

Single pilot; gate controls share proposals; no causal memory or efficiency claim.


Full machine-readable results: [summary.json](summary.json). Method: [protocol.md](protocol.md).
