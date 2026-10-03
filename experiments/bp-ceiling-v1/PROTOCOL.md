# bp-ceiling-v1: is the best-fit ceiling the representation or the instances?

Written before the confirmatory searches and before generating any audit instance. Changes
made after this point are listed at the end.

## Question

No Falsify search has beaten best-fit on fresh data. Falsify scores each open bin with 12 or
20 fixed linear features on 80-item instances from its own families. FunSearch beat best-fit
by 3.3 points of the L2 bound on 5,000-item Weibull instances with Python code that sees every
bin. Which of the two differences holds Falsify at best-fit: the representation or the
instances (length and distribution)?

## Positive control (done before this protocol; it gates everything else)

On FunSearch's own Weibull 5k test data (5 instances, notebook commit cc53f27), our evaluator
reproduces the notebook exactly: best fit 2067.0 mean bins, FunSearch's Weibull heuristic
2001.4, L2 bound 1987.8 (3.98% and 0.68% excess, as published). Checked in
tests/test_longpack.py. Our generator: Weibull(scale 45, shape 3), clipped to 1..100 and
truncated to integers. The Supplementary Information says "rounded"; the released items fit
truncation (mean 39.75; 40.18 expected with rounding, 39.68 with truncation).

## Regimes (instances)

Each candidate evaluation costs 20,000 item steps in every regime:

| Regime | Training set per search seed | Audit (fresh) |
|---|---|---|
| `falsify80` | 250 instances x 80 items, the five Falsify training families in turn | 2,500 (500 per family); 1,500 shifted-family instances reported separately |
| `weibull500` | 40 x 500 Weibull items | 400 instances |
| `weibull5k` | 4 x 5,000 Weibull items (FunSearch trained on 5 x 5,000) | 40 instances |

Training sets come from namespace `bp-ceiling-v1/train` and differ per search seed. Audit
instances come from namespace `bp-ceiling-v1/audit` and are generated only in
`falsify.ceiling audit`, after every search result is on disk. Nothing from the audit
returns to search.

## Representations

- `linear20`: the 20 contextual features of `falsify/contextual.py` scoring open bins only; a
  new bin opens only when nothing fits. Includes the 12-feature space (last 8 weights zero).
- `linear21`: the same features, plus one unused bin offered as a candidate with a 21st
  "new bin" indicator feature. FunSearch's heuristics can open a bin while an open bin fits;
  this arm tests whether that ability, rather than code, is what `linear20` lacks.
- `code`: FunSearch's published Weibull heuristic, fixed (not searched), as a representative
  of the code space. FunSearch's OR heuristic, first fit and best fit are reference rows.

## Search (linear representations)

- `hc` (primary): the existing gated_search proposal stream with score-only promotion. Each
  generation evaluates best fit, the explorer, a mutation of the explorer and a mutation of a
  random anchor (`contextual.anchors()`, zero-padded); mutations are `mutate_contextual`
  generalised to 21 weights (identical for 20). 2,000 generations = 8,000 candidate
  evaluations = 160 million item steps per seed.
- `cmaes` (secondary): CMA-ES (`cma` 4.5.0) from best fit, sigma 0.5, bounds [-12, 12], the
  same 8,000 evaluations. Deploys the best training policy, best fit included.
- Objective: total bins on the seed's training set. 20 seeds (0-19) per regime x
  representation x optimizer: 240 runs, fanned out on Modal (app `ssm-bp-ceiling`, cap $15
  enforced in code).

## Endpoints

For every policy and audit set: excess % = 100 (sum bins - sum L2) / sum L2, as FunSearch
reports, and delta = excess %(policy) - excess %(best fit) in percentage points (negative =
better than best fit). Also wins/ties/losses against best fit per instance.

Primary: delta of the deployed `hc` policy per regime x representation, mean over 20 seeds,
95% bootstrap interval over seeds (10,000 resamples, seed 20261003). For fixed heuristics:
delta with a 95% bootstrap interval over audit instances.

Decision rule: a cell has headroom over best fit if its interval lies entirely below 0. The
instances are a ceiling for a regime if FunSearch's heuristic has no headroom there; the
representation is a ceiling if `linear20` has none in a regime where FunSearch's heuristic has.

## Secondary and descriptive

- `cmaes` cells; shifted families; per-family deltas in `falsify80`; train-vs-audit change.
- Length sweep of the fixed heuristics: Weibull n = 80 ... 10,000 and the five Falsify
  families at n = 80, 500, 5,000, about 100,000 items per point (namespace
  `bp-ceiling-v1/sweep`).
- Mechanism: how often FunSearch's heuristic opens a new bin while an open bin fits.

## Disclosed before confirmatory runs

- Pilot (timing and sanity only): seed 1000, 400 evaluations, `weibull5k`, all four linear
  arms, training namespace only. Training changes were -117, -97, -108 and -281 bins against
  best fit's about 8,270. No audit data existed.
- The problem adapter `problems/bin_packing_online` uses the same generator with a different
  salt; its instances are not used here.

## Changes after this protocol

All made after the 240 searches finished and before any audit instance was generated.

1. **Added arm `ab_rules` (secondary).** The team's literature review pointed to Herrmann &
   Pallez (2025, arXiv 2510.27353), who reduce FunSearch's heuristics to two-threshold rules
   (ab-FirstFit, ab-BestFit, ab-WorstFit). For every regime and search seed we grid-search the
   three variants with a in 0..15 and b in a+1..40 (1,560 evaluations, fewer than the 8,000 of
   the linear arms) on that seed's training set, deploy the best (best fit if nothing beats
   it) and audit it like the other arms. `falsify/longpack.cpp: pack_ab` implements the rules
   and is tested against the paper's priority functions.
2. **Added decision statistics** to the audit (share of items placed in a new bin while an
   open bin fits; share of bins ending exactly full), on the first 10 primary audit instances.
3. **Determinism fix before launch:** `longpack.cpp` is compiled with `-ffp-contract=off` so
   hill-climbing runs give identical results on Modal (x86) and macOS (arm64). CMA-ES runs are
   reproducible only on the same platform (BLAS and RNG differences).
