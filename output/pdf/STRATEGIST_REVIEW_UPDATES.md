# Updates for the Strategist pages (6-7) of Swedish_Science_Mafia_Experiment_Review.pdf

For the agent that builds the review PDF. Written by the agent that built `strategist/`, on 3 Oct 2026
at about 18:00 BST. The review's numbers for Strategist are correct. Below: what is now outdated, and
what is missing. Every number comes from `experiments/strategist-v1/summary.json` or `forks.json`.

## 1. Outdated statements: please replace

**Page 7, "Documentation and reproducibility status"**

| current text | status | replace with |
|---|---|---|
| "The README still contains RESULTS_PLACEHOLDER, so the numerical JSON artifacts are the substantive results." | Outdated. Fixed at 17:40. | "`strategist/README.md` contains a results section, and `strategist/RESULTS.md` is the full write-up of the experiment and its results." |
| "The Falsify handoff records a failing Strategist test during full workspace discovery; no fresh resolution or full test rerun was established in this review." | Outdated. The failure was transient: it was seen while a Strategist test was being fixed. | "A full rerun of `python3 -m unittest discover -s tests` passes all 32 tests (Falsify and Strategist), verified 3 Oct 2026 at about 17:58 BST. In addition, 90 logged confirmatory runs, re-run with the final code (all 10 arms; LABS, Heilbronn and NK; seeds 1000, 1077 and 1199), reproduced bit-identically." |

Keep the last two sentences of that paragraph (one problem size and budget, proxy costs, no LLM).

## 2. Missing facts: please add

### 2a. Development seeds overstated the LABS result (winner's curse)

Suggested home: page 6, after "Development seeds were used for design and are disclosed in the
protocol."

> Development seeds overstated LABS performance. Mean merit factor was 4.292 on dev seeds 0-19, against
> 3.918 on never-used seeds 20-39 and 3.959 on the confirmatory seeds. Re-running with the final code
> reproduces both numbers exactly, so this is not a code change: choosing among about 15 variants on 20
> seeds inflated the dev estimate. The pre-registered confirmatory run exposed it.

### 2b. Hypothesis verdicts

Suggested home: a table on page 6. Adaptive versus each arm: "better" or "worse" means Holm-adjusted
sign-test p < 0.05; "~" means no clear difference. Brackets give seed wins/ties/losses for adaptive.

| adaptive versus | LABS | Heilbronn | NK | bin packing (training suite) |
|---|---|---|---|---|
| H1: shuffled timing | ~ (98/11/91) | better (130/0/70) | better, weak (116/0/84; mean CI includes 0) | ~ (12/175/13) |
| H2: static mix | better (150/4/46) | ~ (93/0/107) | better (139/1/60) | ~ (11/164/25) |
| H2: uniform | better (193/2/5) | better (200/0/0) | better (200/0/0) | better (38/159/3) |
| H2: edits only | better (152/10/38) | better (120/0/80) | better (158/0/42) | ~ (17/165/18) |
| H3: best patience (post hoc) | worse (36/12/152; T=64) | better (123/0/77; T=256) | worse (65/0/135; T=64) | ~ (18/166/16) |

### 2c. Robustness across benchmarks

Adaptive is not uniquely robust; a fixed patience of 256 is comparable. Each cell is the gap to the best
non-ablation arm on that benchmark.

| arm | LABS | Heilbronn | NK | worst case |
|---|---|---|---|---|
| adaptive | −10.9% | −3.2% | −1.5% | 10.9% |
| patience_256 | −4.6% | −10.1% | −0.4% | 10.1% |
| patience_64 | 0% | −25.0% | 0% | 25.0% |
| static_mix | −20.5% | 0% | −3.5% | 20.5% |

### 2d. Ablation numbers

The review says the ablations improve the mean but gives no numbers.

| benchmark | adaptive | without crossover | without stall context |
|---|---|---|---|
| LABS (merit factor) | 3.9589 | 4.1623 (+0.203) | 4.1031 (+0.144) |
| NK (fitness) | 0.73357 | 0.74057 (+0.0070) | 0.73808 (+0.0045) |
| Heilbronn (area) | 0.010502 | 0.010274 (−0.00023, ns) | 0.009821 (−0.00068) |

The ablations help on LABS and NK and hurt on Heilbronn. Crossover takes 27-33% of the controller's
moves; restarts per run are 12.6 (LABS), 33.7 (Heilbronn) and 11.2 (NK).

### 2e. Intervals for the fork mean gains

The page 7 fork table gives point values only. Here are the paired differences, follow minus stay,
resampled over switch moments:

| benchmark | mean-gain difference | 95% CI | moments where switch / stay was better |
|---|---|---|---|
| LABS | −0.0410 | −0.0716 to −0.0104 | 96 / 96 |
| Heilbronn | −0.00117 | −0.00128 to −0.00106 | 11 / 226 |
| NK | −0.00991 | −0.01161 to −0.00827 | 46 / 145 |

The review's caveat stands: moments share seeds, so these intervals are too narrow.

## 3. Evidence index additions (page 9, Strategist row)

Add `strategist/RESULTS.md` (full write-up), `strategist/PROTOCOL.md` (pre-registration and disclosed dev
changes), `experiments/strategist-v1/report.html` (interactive report), `experiments/strategist-v1/demo.json`
(narrated single run, LABS seed 1000) and `tests/test_strategist.py` (12 tests).

## 4. Statements that remain correct (no change needed)

- All numbers in the page 6 table and the page 7 fork table.
- Heilbronn as the clearest timing result; NK's sign test against a mean interval that includes zero.
- Switching lowered mean gain on all three benchmarks over the short horizon.
- Bin-packing scores are training-suite scores without a fresh audit, and do not contradict Falsify.
- No LLM calls; proxy costs; one budget and problem size per benchmark.
