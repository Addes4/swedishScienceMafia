# Live campaign findings

Generated from saved summaries, events and the shared usage ledger. This file can be regenerated; raw run evidence is retained.

Campaign usage: `{"actual_usd": 3.718923825, "reserved_usd": 0.90208, "committed_usd": 4.621003825, "unresolved_requests": 12, "attempts": 213, "settled_requests": 201, "input_tokens": 369415, "output_tokens": 143628}`. Costs use recorded tokens and standard API prices; credits/invoice adjustments are not included.

| Run | Evaluated candidates | Outcome | Mean audit difference | Actual USD | Reserved USD |
|---|---:|---|---:|---:|---:|
| [full-circle-headers](full-circle-headers/report.md) | 18 | completed | -1.6867201246659427 | 1.101018 | 0.000000 |
| [full-circle-live](full-circle-live/report.md) | 6 | RuntimeError: OpenAI HTTP 429; code=rate_limit_exceeded; response body withheld | -1.6746905700505728 | 0.239357 | 0.035480 |
| [full-rich-headers](full-rich-headers/report.md) | 18 | completed | -5.7 | 0.340939 | 0.000000 |
| [full-rich-live](full-rich-live/report.md) | 9 | RuntimeError: OpenAI HTTP 429; code=rate_limit_exceeded; response body withheld | -8.0 | 0.212205 | 0.075000 |
| [full-rich-random-headers](full-rich-random-headers/report.md) | 18 | completed | -1.95 | 0.346154 | 0.000000 |
| [full-rich-random-live](full-rich-random-live/report.md) | 6 | RuntimeError: OpenAI HTTP 429; code=rate_limit_exceeded; response body withheld | 0.0 | 0.142576 | 0.075000 |
| [lean-bounded-headers](lean-bounded-headers/report.md) | 12 | completed | 0.0 | 0.098489 | 0.000000 |
| [lean-bounded-live](lean-bounded-live/report.md) | 0 | RuntimeError: OpenAI network request failed; response body withheld | 0.0 | 0.000000 | 0.000000 |
| [lean-bounded-live-network](lean-bounded-live-network/report.md) | 4 | RuntimeError: OpenAI HTTP 429; response body withheld | 0.0 | 0.022357 | 0.035480 |
| [lean-bounded-paced](lean-bounded-paced/report.md) | 10 | RuntimeError: OpenAI HTTP 429; code=rate_limit_exceeded; response body withheld | 0.0 | 0.074459 | 0.035480 |
| [lean-circle-headers](lean-circle-headers/report.md) | 5 | RuntimeError: Rate-limit wait exceeds 300 seconds; defer this run | -1.6850899239975212 | 0.071750 | 0.055000 |
| [lean-circle-live](lean-circle-live/report.md) | 2 | RuntimeError: OpenAI HTTP 429; response body withheld | -1.6412324606603523 | 0.030948 | 0.075000 |
| [lean-circle-paced](lean-circle-paced/report.md) | 7 | RuntimeError: OpenAI HTTP 429; code=rate_limit_exceeded; response body withheld | -1.6461888861006078 | 0.143226 | 0.075000 |
| [lean-rich-headers](lean-rich-headers/report.md) | 18 | completed | -0.35 | 0.148623 | 0.000000 |
| [lean-rich-live](lean-rich-live/report.md) | 2 | RuntimeError: OpenAI HTTP 429; response body withheld | 0.0 | 0.011162 | 0.075000 |
| [lean-rich-paced](lean-rich-paced/report.md) | 7 | RuntimeError: OpenAI HTTP 429; code=rate_limit_exceeded; response body withheld | -6.3 | 0.058343 | 0.075000 |

Negative differences favor the candidate. Packing units are bins; circle units are negative radius sum. A zero difference can mean the initial best-fit policy remained deployed.

## Interpretation limits

- Interrupted trajectories retain their own frozen audits. Later runs use new seeds and are separate pilots.

- Case bootstrap intervals condition on one search trajectory. They do not establish scheduler or ranker superiority.

- Gate arms share proposals and cached evaluation work. Public FunSearch reference results are separate from generated fresh audits.

- OpenAI generation/ranking substitutes for Claude/Jev; no result here measures the original providers.

- The ledger is authoritative for per-run token totals; early concurrent-run summaries had an aggregation bug, documented in the protocol amendments. Dollar settlements were unaffected.


Protocol: [CAMPAIGN_PROTOCOL.md](CAMPAIGN_PROTOCOL.md). Narrative methods and findings: [RESEARCH_LOG.md](../RESEARCH_LOG.md).
