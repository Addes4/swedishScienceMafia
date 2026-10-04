# Running the integrated research pilots

`evidence_loop.py` connects the existing problem contracts, Strategist policies, Falsify gates and simplification into one auditable loop. The current campaign tests the four architectural options in PLAN.md. It uses OpenAI generation and ranking, with measured token costs; this is an adapted implementation of triage, not a test of Claude or Jev.

See [campaign methods](../runs/CAMPAIGN_PROTOCOL.md), [live findings](../runs/FINDINGS.md) and [research log](../RESEARCH_LOG.md) before interpreting a score.

```sh
python -m pip install -r requirements-research.txt
python -m pytest -q
python -m autoresearch.evidence_loop --problem bounded --steps 2 --mock --out runs/my-software-check
```

For live runs, put `OPENAI_API_KEY=...` in the root `.env` file locally. Git ignores it. Omit `--mock`; supply the approved run budget, fresh output directory and seed. The default persistent campaign ledger enforces the session's $25 total ceiling. Do not remove or reset the ledger to circumvent that limit. `--approach full` enables three ranked model tiers and adaptive move selection. `--ranker random` supplies a control. `--scheduler patience` overrides the adaptive schedule for a separate control.

The loop chooses a move before asking the model for code, validates every required case, and records all gate decisions. A valid exploratory program can remain available to the proposer even when deployment rejects it. This avoids forcing all future proposals to start from the deployed rule. Packing gate arms share the same proposal stream; they are diagnostic replays, not independent searches.

The three adapters expose different hypotheses:

| Adapter | Search object | Independent check | Final comparison |
|---|---|---|---|
| `bounded` | 12 scoring weights, fixed C++ packer | Existing fixed simulator | Best-fit / first-fit on fresh families |
| `rich` | Python `priority(item, bins)` | Assignment length, capacity and count | Fresh OR-style/Weibull, plus separate public references |
| `circle` | Python `solve(n=26)` | Existing strict geometry verifier | Supplied seed under the same 30-second limit |

Each run stores configuration and source hashes, fixed/split/audit inputs, candidate ancestry, raw API requests and responses, per-request usage, evaluator outputs and a human-readable report. `frozen.json` is written before constructing audit data. Code subprocesses have stripped environments and timeouts; this is an honest-loop execution boundary, not a hardened hostile-code sandbox.

To regenerate the campaign index after runs finish:

```sh
python scripts/report_campaign.py
```

Interrupted runs are retained. Do not continue selection after viewing their audit. Use a separately documented new seed and output directory within the remaining allocation. HTTP 429 retries are limited to confirmed rate-limit rejections; uncertain requests keep their reservation.
