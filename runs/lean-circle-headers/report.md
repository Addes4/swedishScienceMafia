# lean: circle

Status: **RuntimeError: Rate-limit wait exceeds 300 seconds; defer this run**. Real LLM: **True**.

API ledger: `{"actual_usd": 0.07175000000000001, "reserved_usd": 0.055, "committed_usd": 0.12675, "unresolved_requests": 1, "attempts": 6, "settled_requests": 5, "input_tokens": 6413, "output_tokens": 5638}`.

| Gate | Mean difference vs reference | 95% case interval | Wins / ties / losses |
|---|---:|---|---|
| score_only | -1.6850899239975212 | [-1.7390174407979209, -1.625137024197563] | 5 / 0 / 0 |
| random_strict | -1.6850899239975212 | [-1.7390174407979209, -1.625137024197563] | 5 / 0 / 0 |
| strict | -1.6850899239975212 | [-1.7390174407979209, -1.625137024197563] | 5 / 0 / 0 |
| validated_budget | -1.6850899239975212 | [-1.7390174407979209, -1.625137024197563] | 5 / 0 / 0 |

Negative differences favor the candidate. Packing units are bins; circle units are negative radius sum.

Single pilot; gate controls share proposals; no causal memory or efficiency claim.


Full machine-readable results: [summary.json](summary.json). Method: [protocol.md](protocol.md).
