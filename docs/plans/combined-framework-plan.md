# Plan: one autoresearch framework from our existing pieces

> **Archived plan.** Copied on 4 October 2026 from branch `plan-combined-framework` (kept as local
> tag `archive/plan-combined-framework`, which also holds its draft code). It was not implemented as
> written; the project shipped `python -m autoresearch.loop` instead ([LOOP.md](../../autoresearch/LOOP.md)).

**Status: proposal for review.** No code written, no paid API calls made.
Branch `plan-combined-framework`, written Saturday 3 October 2026, about 19:30 BST.

Read for this plan: the experiment review PDF (revised 3 October; identical to the copy on
branch `refresh-review-pdf`), the root README, the track brief, the README of each part, and
the interfaces listed in the handoff: `strategist/problems.py`, `problems/README.md`,
`autoresearch/triage.py`, `gate.py`, `sandbox.py`, `claude.py`, `falsify/soft_gates.py`,
`falsify/simplify.py` and `falsify/core.py`. The 37 standard-library tests pass on this branch.
One free CPU calibration was run in a scratch directory (Appendix A).

## Summary

- **Build one loop.** Claude writes heuristic code. An integrity gate runs it in a process that
  never receives future inputs. Archived counterexamples and fresh validation inputs decide
  promotion. The next prompt shows the smallest inputs where the incumbent wins and where it
  loses. After the run, the winner is checked for being a rediscovered baseline, and every
  reported number comes from an audit generated after the search, with its token cost.
- **Main benchmark:** online bin packing on locally generated Weibull instances (FunSearch's
  distribution), audited at 1,000, 5,000 and 10,000 items. Circle packing runs through the same
  command as a generality check only.
- **Keep:** the Claude client and cost accounting, the integrity gate and problem contract,
  Falsify's archive logic and `gate_decision`, Simplify's paired comparisons and witnesses, and
  Strategist's move vocabulary and patience rule.
- **Drop from the critical path:** the Jev ranker and model tiering, the adaptive Strategist
  controller, the 12-weight feature space as the search space, and OR-Library (its files need a
  download nobody has approved).
- **First real-LLM run:** about 40 calls with a hard dollar cap ($10 on Opus 5.5 or $5 on Sonnet
  5.5). Token counts and dollars are recorded from every API response.

## 1. Pitch

Autoresearch loops usually trust a training score, and our own experiments show how that
fails. A Codex revision scored 1 win and 0 losses on 1,000 cases, then 3 wins and 14 losses on
10,000 fresh ones. An 11-term evolved "winner" turned out to be exactly best-fit. Our
framework is a loop that tries to refute each candidate before keeping it. Claude writes the
candidate as code. A fixed harness runs it in a separate process that only ever receives past
inputs, so it cannot look ahead. Inputs on which candidates lost go into an archive of
executable counterexamples. A candidate is promoted only if it beats the incumbent on training
cases, stays within a bounded loss on archived counterexamples, and does not lose on fresh
validation inputs. The model's next prompt then shows the smallest inputs where the incumbent
wins and where it loses, with both packings, not just a score. At the end, the winner is
compared placement by placement with known heuristics, so a rediscovered best-fit, or a
recalled FunSearch heuristic, is labelled as one. Every reported number comes from an audit
set generated after the search, together with the dollars it took to get there.

## 2. Architecture

```
problems/<name>/                 Strategist move vocabulary        autoresearch/claude.py
 problem.md, verify.py      ──►  + patience rule picks       ──►   Claude writes the code
 + sample(), reference()         edit | rewrite | crossover |      (tokens and $ logged
   (new, optional)               restart                           from API usage)
                                                                          │
                                                                          ▼
          autoresearch/gate.py + sandbox.py: static checks, separate process with keys
          stripped, online harness (the child never holds future items), time limit
                                                                          │
                                                                          ▼
     8 fixed training inputs + 16 archived counterexamples + 16 fresh validation inputs
          falsify.soft_gates.gate_decision  ──►  promote / reject, with the reason logged
                       │                                       ▲
     probe inputs where the candidate lost ──► archive (≤64, deduplicated by input hash)
                       │
     contrastive witnesses: shrunk inputs + both packings ──► next prompt

 after the run: fresh audit (new seed, generated now) ──► explain: fingerprint against known
 heuristics, two-sided simplification, witnesses ──► log.jsonl, notebook.md, summary.json
```

### Which existing module plays which role

| Role | Existing code | Evidence behind it | Change needed |
|---|---|---|---|
| Proposer and implementer | `autoresearch/claude.py` | Never called. Prices match current list prices. | One prompt per move type. Fix cache-read pricing: the code charges 0.1× input, but Opus 5.5 cache reads are $0.20/MTok (0.05×). |
| Problem contract | `problems/<name>/verify.py` | 8 gate tests | Optional `sample(split, seed)` and per-instance `reference()` so a problem can have an input distribution. Optional `run()` hook for harness problems. Existing folders are unchanged. |
| Integrity gate | `autoresearch/gate.py`, `sandbox.py` | 8 tests; isolation, not a security sandbox | Online harness for heuristic problems. One worker process per candidate, not one per instance. |
| Counterexample archive | Inline in `falsify/soft_gates.py` `run_seed` | V2 replay result; V3 and V4 gates | Lift it into a small class: deduplicate by input hash, keep the largest regressions, cap at 64. Reuse the V4 fix for within-generation maxima. |
| Promotion rule | `falsify.soft_gates.gate_decision` (pure function) | V3: counterexample gate beat score-only promotion. Against a random gate, and validated versus strict in V4: inconclusive. | Make the loss limits parameters (currently hard-coded at 1 bin and 2 losses), keeping the old values as defaults so V4 still reproduces. Feed it deltas against the incumbent. |
| Move scheduler | `strategist/controller.py` `Patience`, plus the four move names | A tuned patience rule beat the adaptive controller on LABS and NK. Patience 256 was about as robust. | Edit, rewrite, crossover and restart become four prompt templates. `Adaptive` stays available behind a flag, with no claims made for it. |
| Explanation | `falsify/simplify.py`: `compare`, `agreement`, `bootstrap`, `shrink`, `witness` | Reproduces byte-for-byte. Its acceptance rule is one-sided (known flaw). | Generalise from 12-weight vectors to any policy callable. Use two-sided acceptance. |
| Logging and analysis | `autoresearch/analyze.py` (log.jsonl, notebook.md) | Never run | Add gate statistics, move type, and measured cost per move type. |
| Audit discipline | Falsify protocols | Every Falsify study | A new audit script whose seeds are written into the protocol before the run. |

### Glue code (estimated sizes)

- `problems/binpacking_weibull/`: problem text, instance generator, L2 lower bound, best-fit and
  first-fit references, and the online harness (~250 lines).
- `autoresearch/loop.py`: rounds of 4 parallel candidates from one incumbent, the patience
  rule, the gate call, archive updates, witness feedback, and a dollar cap (~250 lines).
- `autoresearch/archive.py` (~60 lines), `autoresearch/explain.py` (~150), `autoresearch/audit.py` (~100).
- Tests (~150 lines). The harness's best-fit must match `falsify.core.pack` bin counts exactly
  on 80-item inputs, which gives a free independent check on the new harness. A program that
  reads files, times out, chooses an infeasible bin or tries to see future inputs must be
  rejected.
- A scripted fake model that returns canned programs, so the loop can be tested end to end
  without spending anything.

### What is genuinely new

1. **Counterexamples act on LLM-written code twice**: as a promotion gate, and as prompt
   feedback in the form of contrastive minimal witnesses ("on these 9 items you used 4 bins and
   best-fit used 3; here are both packings"). In the supplied papers (FunSearch, AlphaEvolve,
   ShinkaEvolve) the model is shown scores and evaluator text. We have not seen shrunk
   counterexample inputs used as feedback, but check the papers again before the pitch says
   so. The Codex pilot did this by hand, inside one conversation.
2. **The harness enforces online-ness by construction.** Inputs are streamed to the candidate
   process one item at a time, and the parent re-checks feasibility. Future items do not exist
   in the child process, so look-ahead cannot be hidden from the gate. Sorting the items first,
   an offline trick that beats best-fit trivially, is impossible.
3. **Automatic rediscovery check.** The winner's placement agreement with best-fit, first-fit
   and FunSearch's published Figure 6 heuristic is measured. This generalises the Simplify
   finding that the evolved "winner" was best-fit, and it is the first line of defence against
   contamination: Claude has very likely read the FunSearch paper.
4. **Measured cost per move type.** This replaces Strategist's proxy cost table (edit 1.2,
   rewrite 2, and so on) with real token costs, the input a future adaptive run would need.

## 3. The candidate, critiqued, and the options

### 3.1 The candidate pipeline, stage by stage

| Stage in the candidate | What the evidence says | Verdict |
|---|---|---|
| Claude proposes code "via autoresearch triage" | Triage has never run. Jev needs a third-party key. Its own evaluation needs 5 arms × 3 seeds at a matched dollar budget. | **Keep** the Claude client, gate, contract and logging. **Drop** Jev ranking and model tiering for now: an untested ranker adds a claim we cannot support by Sunday. |
| Strategist picks the move type | The controller learned over 3,000 cost units, roughly 1,500 to 2,500 moves. With ~40 LLM calls its estimates stay near the prior (4 pseudo-observations over 12 contexts). A tuned patience rule beat it on LABS and NK. Forks showed its switches were often premature. Its costs are proxies. | **Keep** the four moves and a fixed patience rule. **Drop** adaptive control from the main loop. **Add** measured cost per move. |
| Falsify's validated bounded-loss gate decides promotion | V3: counterexample gate beat score-only promotion, CI [−0.0041, −0.0006]. Against a random gate: inconclusive. V4: validated versus strict was inconclusive on final quality, and plain relaxation made it worse. Its thresholds (≤2 losses of ≤1 bin) were set on 80-item inputs, where most packings tie. On 1,000-item inputs packings almost always differ, so the thresholds must be recalibrated. On circle packing there is only one instance, so the gate has nothing to work with. | **Keep** `gate_decision` and the archive. Treat the V4 evidence as a design prior, not a transferred result. Set thresholds on development inputs before the run and write them into the protocol. |
| Simplify explains the winner | `simplify.py` only works on 12-weight vectors. Its one-sided tolerance can repair a bad candidate instead of explaining it (21 of 35 best-fit reductions were repairs). | **Keep** its paired comparison, bootstrap and witness tools. Explain code by behaviour (fingerprint, witnesses). Accept a simplification only if it is equivalent in both directions. |
| Benchmarks: circle packing and OR-Library/Weibull | Circle packing has a known record but no input distribution, so counterexamples cannot apply. OR-Library needs a file download, uses capacity 150, and the Falsify packer is hard-coded to capacity 100 and at most 4,096 items. Our Weibull generator puts best-fit at 4.17%, not FunSearch's published 3.98% (Appendix A). | **Weibull first** (generated locally, capacity 100). Circle packing as a cheap generality check. OR-Library only after the download is approved. Compare only against best-fit on our own instances until the generator is reconciled. |

### 3.2 Options, ranked

Effort is for one developer working with coding agents. Effects are expectations, not results.

| Rank | Option | Effort | Risk | Novelty | Performance | Interpretability and ease of use | Research efficiency |
|---|---|---|---|---|---|---|---|
| 1 | **A. Falsify loop**: the architecture above, on Weibull bin packing, plus a circle-packing check through the same command | 9–12 h, ~$5–10 | Medium | High: the counterexample mechanisms apply to LLM code, and online-ness is enforced by construction | First real chance of a fresh-audit result better than best-fit (FunSearch shows the gap exists). A null result is still informative. | High: one command, one contract, notebook, witnesses, fingerprint | Measured dollars per promotion; gates cost ~1 CPU second per candidate |
| 2 | **B. A plus a matched-budget ablation**: full loop vs score-only vs best-of-N, 3 seeds each | A + 2–3 h, ~1.5 h wall time, $25–70 | Medium–high (time) | High: tests whether executable feedback beats score-only feedback (the review's suggested next experiment) | Same as A | Same as A | The only option that produces a comparative efficiency result |
| 3 | **C. Run the existing triage loop as it is** (`--ranker random` or `claude`) on circle packing and the Erdős problems | 2–4 h, ~$5–20 | Low–medium: never run, so expect API-parameter bugs | Low: ShinkaEvolve-like | Measured against known records | Medium | Measured costs, no comparison |
| 4 | **D. No LLM: add a Weibull family to the 12-weight Falsify search** | 2–3 h, plus CPU overnight | Low | Low | Probably null. Simplify suggests the feature space cannot express anything better than best-fit, and the fixed packer cannot choose an empty bin while another bin fits. | — | — |
| 5 | **E. The candidate as written**: all four parts on circle packing and OR-Library/Weibull | 18–24 h | High: four parts never run together, the Jev key, a download, and an adaptive controller with too few moves to learn | Looks high, but few of its claims could be supported | Uncertain | Low: too many parts for a 4-minute video | Proxy costs; untested ranker |

**Recommendation:** A, then B if A is finished by about 09:30 Sunday. D runs overnight on spare
CPU only if someone has an hour for it: it is the control that separates "the 12-weight space
cannot express it" from "80-item inputs leave no room", which the review lists as untested. C is
the fallback if the harness work slips past Saturday night. E is not recommended.

## 4. Recommended plan

### 4.1 Stages (times BST)

| When | Stage | Done when | Cost |
|---|---|---|---|
| Sat 19:30–20:00 | Plan review | Approved, or changes requested | — |
| Sat 20:00–21:00 | **0. Environment.** `uv` virtual environment with `anthropic`, `numpy`, `scipy`, `pytest`. A person puts the key in `.env`; agents never print it. One smoke call through `autoresearch/claude.py` to exercise streaming, effort and the fallback beta parameter, none of which has ever run. Fix the cache-read price. | All 45 tests pass; one logged call with usage recorded | <$0.50 |
| Sat 21:00–23:30 | **1. Problem and harness.** `problems/binpacking_weibull/`: generator, L2 bound, references, streaming harness, tests | Harness best-fit matches `falsify.core.pack` on 80-item inputs; cheating, infeasible, crashing and timed-out programs are rejected | CPU only |
| Sat 23:30 – Sun 08:30 | **2. Loop.** `loop.py`, archive, gate thresholds (calibrated on development inputs and written into `docs/plans/llm-weibull-v1-protocol.md`), witness feedback, logging. Dry run with the fake model. Stages 1 and 2 can be built in parallel by two agents against a fixed interface. | Dry run produces log.jsonl, notebook.md and summary.json; gate decisions match hand checks | CPU only |
| Sun 08:30–09:15 | **3. First real run**, then the fresh audit (§4.2) | `experiments/llm-weibull-v1/` complete and committed | $5–10 cap |
| Sun 09:15–10:30 | **4. Explanation and report.** Fingerprint, witnesses, one two-sided simplification attempt, notebook. Circle-packing check through the same command (~10 calls). | Explanation section in the run folder; README section drafted | ~$3 |
| Sun 10:30 | **Decision point.** If stage 3 is done and the budget is approved, launch B's runs in parallel (~1.5 h wall) while writing. Otherwise polish A. | — | B: $25–70 cap |
| Sun 12:00 | **Freeze**: the demo works from a clean clone | — | — |
| Sun 12:00–14:45 | README, 4-minute video, submission | — | — |

### 4.2 The first real-LLM run (what it measures)

- **Pre-registration.** `docs/plans/llm-weibull-v1-protocol.md` is committed before the run. It fixes
  seeds, budget, stopping rule, gate thresholds, the audit seed and the reported metrics. The
  output folder `experiments/llm-weibull-v1/` is never edited after the run.
- **Problem.** Weibull(shape 3, scale 45), rounded, clipped to [1, 100], capacity 100. Training
  uses 8 fixed instances of 1,000 items. The archive starts with 16 Weibull instances. Each
  candidate gets 16 fresh validation instances and 8 fresh probe instances, and any probe it
  loses goes into the archive. Witnesses are shrunk from 100-item inputs, because shrinking
  1,000-item inputs is too slow. In the scratch check (Appendix A) a 5,000-item best-fit
  packing took about 0.07 s, so evaluation is negligible next to LLM latency.
- **Candidate interface**, as in FunSearch: `priority(item, bins) -> scores`, where `bins` holds
  the remaining capacity of every bin the item fits in, empty ones included. This is from
  memory of FunSearch's notebook; confirm it against the paper's supplement. Only numpy is
  allowed.
- **Loop.** It starts from best-fit, with 10 rounds of 4 parallel candidates from the current
  incumbent. Edit is the default move. After 3 rounds without a promotion it switches to
  rewrite, and after 6 to a restart from best-fit with an instruction to try a different
  mechanism. Crossover is used once two promoted programs exist. These values are fixed in the
  protocol, not tuned. The run stops at 40 implementation calls or at the dollar cap,
  whichever comes first.
- **Logged for every call:** model requested and model served, input, output and cache tokens,
  dollars computed from `usage`, latency, move type, outcome (integrity rejection, invalid,
  gate rejection with statistics, or promoted), and evaluation CPU seconds.
- **Fresh audit**, generated after the run from the pre-registered seed: 200 × 1,000, 50 × 5,000
  and 10 × 10,000 Weibull items, plus 100 × 1,000 from each of Falsify's other families as an
  out-of-distribution check. Policies audited: the champion, best-fit, first-fit, the starting
  program and FunSearch's Figure 6 heuristic (published code, credited). Reported: excess
  over L2, and paired per-instance differences against best-fit with bootstrap 95% intervals.
- **Explanation:** placement agreement with each baseline, contrastive witnesses, and one
  LLM-proposed simplification. It is accepted only if |Δ| ≤ tolerance on a separate suite,
  then confirmed on another fresh suite.
- **Estimated cost**, for approval only; the run records the actual figures:

  | Model (effort medium) | Per call (≈6k input, ≈6k output including thinking) | 40 calls | Cap |
  |---|---|---|---|
  | Opus 5.5 ($4 / $20 per MTok) | ≈$0.15 (range $0.08–0.25) | ≈$6 | $10 |
  | Sonnet 5.5 ($2 / $10 per MTok) | ≈$0.07 (range $0.04–0.12) | ≈$3 | $5 |

  Wall time is about 15–25 minutes for the run and about 5 minutes for the audit.

### 4.3 Decisions needed from the reviewer

1. **Model for all runs:** Opus 5.5 (the stronger default) or Sonnet 5.5 (about half the cost).
2. **Dollar caps:** smoke test $0.50, first run $10, ablation B $60 in total. Are these
   acceptable?
3. **Gate scope:** Weibull-only counterexamples (recommended: comparable to FunSearch, and the
   gate stays passable), or also Falsify's shifted families. Including them makes the gate
   enforce "no regression elsewhere", which may stop all progress.
4. **Downloads (each needs explicit approval):** FunSearch's released bin-packing notebook, to
   reconcile the generator, and the OR-Library `binpack1–4` files. Without them we report only
   "Weibull, our generator" and say nothing about OR-Library.
5. **Jev and tiering:** leave them documented as "implemented, not evaluated" (recommended), or
   take them out of the pitch entirely.

## 5. What the run can honestly support

### If the run produces a champion H, it can support

- The loop runs end to end with a real LLM, and N calls cost $X: measured dollars, tokens and
  minutes.
- H's performance on the fresh Weibull audit at 1k, 5k and 10k items: excess over L2, and the
  paired difference against best-fit with a 95% interval over audit instances. This is a claim
  about H on this distribution and these sizes, from one run and one seed.
- Whether H behaves like a known heuristic (placement agreement), and the concrete witness
  inputs showing where it wins and where it loses.
- Counts of integrity and gate rejections, with their reasons.
- The first measured token cost and success rate per move type (descriptive only).

### It cannot support

- That the loop beats anything. There is no matched comparison, and n = 1.
- That counterexample feedback or gating helped the LLM. That needs B.
- That H is novel. Claude has very likely seen FunSearch, so recall is the default assumption,
  and even a low fingerprint match would not prove novelty.
- Any comparison with FunSearch's Table 1 numbers. Our best-fit lands at 4.17%, theirs at
  3.98%, so the instances differ. Compare only against best-fit on the same instances.
- Anything about OR-Library, Jev triage, or adaptive Strategist control.
- Results beyond the audited families and sizes, or "better than best-fit" based on training or
  validation scores alone. That is the Strategist packing lesson.

### Baselines and controls B needs for a framework-level claim

- **Arms:**
  - (a) the full loop;
  - (b) score-only: aggregate feedback and promotion on training score alone, the analogue of
    V3's score-only arm;
  - (c) best-of-N: independent one-shot calls from the starting prompt, keeping the best by
    training score, at the same dollar budget. This is the baseline that most autoresearch
    claims skip;
  - optionally (d), D's 12-weight search on the same training instances as an expressiveness
    control, reported separately because CPU evaluations are not comparable to tokens.
- **Matching:** same model, effort, `max_tokens` and prompt template apart from the
  manipulated part. Same dollar cap, enforced from measured usage. Same training, validation
  and probe seeds for paired seeds. Every arm pays for the same evaluations even when it
  ignores them (the Falsify rule).
- **Seeds:** at least 3 per arm. With 3 the result is directional only: report every seed and
  make no significance claim.
- **Fresh audit data:** one shared audit set, generated after every arm finishes, from a seed
  written into the protocol beforehand. No arm or prompt ever sees it. Comparisons are paired.
- **No selection:** every run is reported, including failed and over-budget ones. No prompt or
  threshold is tuned on audit data, and development runs are labelled as such. The LABS
  development seeds showed how picking the best of ~15 variants inflates results.

## 6. What not to do

- Do not run Jev triage's five-arm comparison or put the adaptive Strategist controller in the
  main loop before Sunday. Neither can produce a supportable claim in time.
- Do not search over the 12-weight feature space again. Simplify showed the winner there is
  best-fit.
- Do not reuse V4's gate thresholds unchanged on 1,000-item inputs, and do not relax the gate
  without validation. V4 found that plain relaxation hurts.
- Do not use Simplify's one-sided tolerance to explain anything.
- Do not report training or validation scores as performance. Do not compare with FunSearch's
  published percentages, or label generated instances as OR-Library.
- Do not show audit or hidden instances to the model, or put audit seeds in prompts or logs that
  the model sees.
- Do not present the integrity gate as a security sandbox (the review says so explicitly), or
  call a heuristic Claude may have recalled a discovery.
- Do not chase the circle-packing record. Report the normalised score; anything above the
  record goes to the strict re-check and to a human.
- Do not add problems (Erdős and others) before the Weibull run works end to end.
- Do not modify anything under `experiments/<name>/`, reuse earlier audit seeds, or push to
  `main`. Keys go in `.env` only and are never printed. No paid call or cloud job runs before
  this plan is approved.

## Appendix A: calibration check (scratch only, no repository code)

A numpy online packer with FunSearch's interface: every bin the item fits in, empty bins
included, highest priority wins. Weibull(shape 3, scale 45), capacity 100. Excess over the
Martello–Toth L2 bound:

| Instances | First-fit | Best-fit | FunSearch Fig. 6 (OR heuristic) |
|---|---|---|---|
| 10 × 1,000 items | 5.20% | 4.65% | 4.53% |
| 5 × 5,000 items | 4.43% | 4.06% | 4.37% |
| 20 × 5,000 items, rounded sizes | 4.51% | 4.17% (SD 0.15) | — |
| 20 × 5,000 items, sizes rounded up | 4.55% | 4.23% (SD 0.14) | — |
| FunSearch Table 1, Weibull 5k | 4.23% | 3.98% | 0.68% (their Weibull heuristic) |

Takeaways:

- Our generator is close to FunSearch's but measurably different: about 0.2 points on
  best-fit, with a standard error of about 0.03.
- Figure 6's heuristic was evolved on OR instances. It does not beat best-fit on Weibull at
  5,000 items, so heuristics are distribution-specific. This supports auditing several sizes
  and families.
- Evaluation is cheap: about 0.07 s per 5,000-item packing.

## Appendix B: which finding drives which decision

| Finding (review page) | Decision in this plan |
|---|---|
| V2: counterexample replay reduced drift, CI excludes zero (p. 2) | Keep the archive |
| V3: counterexample gate beat score-only; against a random gate, inconclusive (p. 4) | Gate on counterexamples; B's score-only arm |
| V4: validated ≈ strict; plain relaxation worse (p. 5) | Recalibrate thresholds; do not relax without validation |
| Codex pilot: pilot win became a fresh-audit loss (p. 3) | Fresh audit after the run; contrastive witnesses rather than "fix this failure" |
| Simplify: winner = best-fit; one-sided tolerance repairs (pp. 6–7) | Rediscovery fingerprint; two-sided acceptance |
| Strategist: patience beats adaptive on LABS/NK; forks premature; proxy costs (pp. 8–10) | Patience rule; measured cost per move |
| Triage: never run; gate is not a security sandbox (p. 11) | Reuse the plumbing; no triage or security claims |
| FunSearch beat best-fit with code that sees every bin (p. 2) | Search over code with FunSearch's interface, not over weights |
