# Faster execution without changing the search algorithm

Implemented on `research/throughput-modal`, based on `ed5f882`. This branch changes
execution infrastructure. It does not restart, migrate, or edit the active pilot
runs in `/private/tmp/ssm-all-approaches`, or modify any `experiments/` evidence.

Use **four local evaluation workers** for the current small code-search pilots.
Modal is available for larger evaluations and additional concurrent workloads;
it was slower for the small cases measured here. The new API scheduler removes
the unconditional 15-second pause and observes rate-limit headers. Both features
are opt-in, so an existing command retains its original execution settings.

## Changes and rationale

- `--api-scheduler headers`: requests share a file-backed coordinator beside the
  spend ledger. At most two requests are in flight, with one per model. It observes
  remaining requests/tokens and reset times; it uses counted input plus the output
  allowance for token reservations. Token-count calls do not reserve generation
  tokens. There is no unconditional delay. Only confirmed rate/overload rejections
  are retried, at most three times, respecting `Retry-After`; waits beyond five
  minutes defer the run. Ambiguous network failures keep their spend reservation.
  This is advisory: other clients and shared model-family limits can still cause
  rejections. The legacy transport does not participate in this coordinator.
- `--eval-workers 4`: independent cases run in bounded parallel subprocesses.
  Input order, deterministic case seeds, deduplication, all-case validity, logical
  work counts, and parent-side verification are preserved. Artifacts and cache
  mutations remain on the calling thread. Wall time is recorded separately from
  summed case elapsed time. The inexpensive bounded-weight packer remains serial.
- `--eval-backend modal`: each code/case execution gets a fresh Modal Sandbox,
  one CPU with a one-CPU limit, 2 GiB memory, one numerical-library thread,
  Python 3.14, NumPy 2.5.3 and SciPy 1.18.1. Only the trusted worker, candidate and
  case are transferred. There are no repository mounts or API secrets, networking
  is blocked, and the same independent verifier runs locally. Candidate timeout
  includes Python imports, but excludes container setup and transfer. Containers
  terminate in `finally`, with an additional platform lifetime cap. Infrastructure
  errors stop the run rather than being scored as candidate failures.
- `--env-file /absolute/path/.env`: explicitly load an existing local key file.
  Its contents are never sent to a candidate or cloud evaluator. Spend accounting
  remains in the existing ledger; Modal costs are separate from API token costs.

Backend and concurrency are frozen in each new run's configuration. Changing
hardware or concurrency changes timeout behavior; comparisons must use the same
configuration, matched budgets, fresh audit data and independent seeds. These
changes do not establish an algorithmic improvement or a win over best-fit.

## Validation, 3 October 2026

`autoresearch.throughput_smoke` uses four fixed bin-packing cases (seed 98217), the
provided best-fit code, a deliberately artificial two-second import delay, one
provided circle construction, and an infinite-loop candidate with a two-second
timeout. The delay fixture tests scheduling only. No LLM supplies these candidates.

| Path | Four best-fit cases | Same cases + 2 s delay each | Initial backend setup |
|---|---:|---:|---:|
| Local, one worker | 0.604 s | 8.739 s | <0.001 s |
| Local, four workers | 0.247 s | 2.248 s | <0.001 s |
| Modal, four workers | 3.361 s | 5.234 s | 13.753 s |

All three produced bin counts `[56, 2097, 54, 2111]`, the same circle radius sum
`0.9285387089611934`, and rejected the infinite-loop candidate. Modal executed ten
Sandboxes and recorded successful termination for each. On this one smoke sample,
local parallelism reduced packing wall time by 2.45x; the latency fixture improved
by 3.89x. These are small, single-run execution checks, not throughput estimates
for a complete search campaign. Modal build time is shown separately. Modal billed
cost was not retrieved; no claim of cloud cost savings is supported by this check.

A one-step full-loop **mock** run with four local workers completed through
simplification and fresh audit: eight audit ties, zero model spend. This validates
integration only, not real proposal generation or research quality.

A separate **real** OpenAI transport check requested `OK` from `gpt-6-luna` and
received it: 21 input tokens, five output tokens, 1.147 s generation request wall
time, estimated API cost **$0.0000046** using the runner's price table. Both HTTP
requests succeeded on their first attempt. The generation response supplied a
request limit of 50, remaining 37, reset about 21,315 seconds, and a token limit
of 60,000. The request-limit period is not inferred from this single header.
Credits do not remove provider request limits. This check did not exercise a
real 429; simulated tests cover exhaustion, Retry-After, shared coordination,
expired leases, non-retryable quota errors and unknown network failures.

All 75 tests pass (4.64 seconds); see `validation/throughput/` for recorded
summaries, safe transport headers, token ledger and evaluator records. Full local
mock artifacts are retained under `results/throughput/` in this worktree. No keys
are included. The mock configuration retains its original run path for provenance.

## Running a new configuration

Install `requirements-research.txt` in a dedicated environment; install
`requirements-modal.txt` and authenticate Modal if using its backend. Example:

```sh
python -m autoresearch.evidence_loop --problem rich --approach lean \
  --steps 12 --seed 9201 --budget 3 \
  --api-scheduler headers --eval-workers 4 --eval-backend local \
  --env-file /absolute/path/to/.env \
  --ledger runs/new-throughput-usage.jsonl --out runs/new-throughput-rich
```

For a fresh Modal comparison, change the backend to `modal` and use a fresh output
directory. Set the same backend/workers for every comparison arm. The worker limit
is per process; four simultaneous runs with four workers can launch sixteen
evaluations. Start with four, then scale only after measuring realistic cases.
Keep the existing campaign ledger when adding runs to a campaign so the monetary
ceiling remains shared. The example uses a separate ledger for a new campaign.

Reproduce the execution checks without any model calls:

```sh
python -m pytest -q
python -m autoresearch.throughput_smoke --backend local --workers 1 --out results/check-serial
python -m autoresearch.throughput_smoke --backend local --workers 4 --out results/check-four
python -m autoresearch.throughput_smoke --backend modal --workers 4 --out results/check-modal
```

All output paths must be new. The Modal command creates paid Sandboxes. These
checks do not rerun failed scientific hypotheses or use the research audit data.

Implementation references: [OpenAI rate limits](https://developers.openai.com/api/docs/guides/rate-limits),
[Modal Sandbox API](https://modal.com/docs/sdk/py/latest/Sandbox),
[Sandbox files](https://modal.com/docs/guide/sandbox-files), and
[Sandbox resources](https://modal.com/docs/guide/sandbox-resources).
