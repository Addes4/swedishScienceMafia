# Related work and what it means for this project

Literature review done on 3 October 2026, during the hackathon. We searched for work on each of
our four parts and checked that every paper exists on arXiv or a publisher page. The 22 most
relevant papers were read in full (marked †), and the key numbers quoted here were checked
against the papers. `python3 docs/literature/fetch_papers.py` downloads them into
`docs/literature/related-papers/`. That folder is git-ignored because most of the PDFs cannot be
redistributed; the links below lead to every paper. [How the review was done](#how-this-review-was-done)
records the method, decisions and corrections. [What changed in our experiments](#what-changed-in-our-experiments)
records what the review changed in the running experiments. [related-work-log.md](../logs/related-work-log.md)
is the session's timeline, decisions, incidents and cost. [docs/papers/outlines/](../papers/outlines/README.md)
turns the findings into two candidate research papers.

## Question and answer

**Question.** Is anyone else working on what we are, which of our results are new, and what does
the literature imply for each part of the framework?

**Answer.** Yes: several 2026 groups study the same failure modes. Four of our contributions did
not appear in the roughly 60 papers we reviewed. Two of our results reproduce published findings,
and one mechanism is prior art. The review changed two running experiments: the tournament gained
the baselines and statistics the literature expects, and bp-ceiling gained a published rule as a
baseline and a headroom measurement. Every experiment that finished afterwards agreed with the
literature (see [How the finished runs line up](#how-the-finished-runs-line-up-with-the-literature)).

## Summary

- **The field has converged on our concern.** Several 2026 papers find that autoresearch loops
  fool themselves: simple baselines match elaborate search, rankings flip with the number of
  seeds, and evaluators get exploited. Our focus on loops that check their own claims is timely.
- **Our bin-packing null result is the expected one.** No paper beats best-fit on short
  (about 80-item) instances with independent item sizes. Published wins need long streams,
  structure to exploit, or features that see every open bin. bp-ceiling-v1 confirmed this: on
  5,000-item Weibull instances our linear rule, given a "new bin" option, matches FunSearch's code.
- **Several results are confirmations, not firsts.** Simplify's finding has a manual precedent,
  and adaptive restarting already exists in LLM evolution. We should phrase those as independent
  replications.
- **Some things are new.** Counterexample gates tested against a random-input gate at matched
  budgets, timing-shuffled and counterfactual-fork controls for a strategy controller, automated
  simplification with confidence intervals, and idea triage with randomised swaps. None of these
  appeared in the work we found.

## What is new and what is not

| Our claim | Status | Closest prior work | How to phrase it |
|---|---|---|---|
| Counterexamples as a promotion gate, compared with score-only and random-input gates at matched budgets (Falsify v3/v4) | New as far as we found | RAISE and ASRO use adversarial instances to *train* the search, not to gate promotion; the reusable holdout and the Ladder give the theory | "Counterexample gates beat score-only promotion; against a random gate the result is inconclusive." |
| Evolved winners reduce to simple rules (Simplify) | Confirmed, not first | Herrmann & Pallez did this by hand for FunSearch's bin-packing heuristic | "We automate the reduction, with ablation CIs and a witness; it independently reproduces their finding." |
| Leave the leader by the marginal value theorem, with move costs (Strategist) | Rule new; mechanism not | AdaEvolve, PACEvolve, MetaMax (2011) and Luby restarts already adapt restarts during a run | Claim the cost-weighted leave rule and the timing controls, not adaptive restarting. |
| Timing-shuffled replay and counterfactual forks | New as far as we found | None of the strategy papers separates timing from move mix | Lead with this for Strategist. |
| Rank ideas before code, route to model tiers, randomise 15% (Triage) | Ranking-before-code and swaps new; routing not | Relay Don't Route, LEVI and AdaptEvolve route work between cheap and strong models | "Measured triage", reported as a null. idea-table-v1 found rankers near chance (only Codex clearly above random, AUC 0.600) and ranked tiers no better than random tiers; the implementing model decided success. Make no cost-saving claim. |
| Strict re-check of anything that beats a record | Independently validated | HASE hit the same tolerance exploit on circle packing | "Our 1e-12 re-check guards against a documented exploit." |

Name clashes: Madeyski (2026) is also called "Triage", and `falsify` is an existing Haskell
property-testing library (de Vries 2023).

## By part

### Falsify and bin packing

- **No published method beats best-fit at our scale.**
  - FunSearch's c12 heuristic, evolved on 20 instances of 120 items, does worse than best-fit
    below about 90 items (Herrmann & Pallez †).
  - Sim et al. † rank best-fit first across 12 datasets and 6,064 instances. At 120 items the
    FunSearch gain is about 0.6 percentage points (OR1: 5.81% vs about 5.25% excess).
  - RAISE † loses to best-fit at 1,000 items, and also on its Uniform, Normal and Exponential
    shifts at 5,000 items (Uniform: 1.717% for best-fit vs 1.954%).
- **What a win needs:** many items still to come, a minimum item size or known distribution,
  structure to exploit, and global bin state. ASRO's large gains are on triplet instances
  (12.66% → 7.11%) and sorted Hard28 (40.02% → 12.45%). On randomly ordered Hard28 the gain is
  8.45% → 8.06%.
- **Counterexamples prove regressions, not improvements.** Sim et al. evolve item orders that
  make any rule lose to the others on some instance. The archive is a regression guard;
  improvement claims must be made over a distribution with paired statistics.
- **Theory for our gates.** The reusable holdout (Dwork et al.) and the Ladder (Blum & Hardt)
  explain why a reused validation set overfits. Our Codex revision is the textbook case: 1 win /
  0 losses on 1,000 cases became 3 / 14 on 10,000 fresh cases. The Ladder accepts only gains above
  a margin, which is close to our V4 bounded-loss gate.
- **Next steps the papers suggest.** Measure headroom first: best-fit against the exact optimum
  per family. Evolve instance generators (RAISE, ASRO) rather than archiving single inputs. Add
  global-state features. Sum-of-Squares (Csirik et al.) scores a bin by `N(gap+item) − N(gap)`,
  where N(g) counts open bins with gap g. This is our own derivation from the paper and still
  needs checking; our per-bin features cannot express it.
- `bp-ceiling-v1` already tests the main question this raises: whether the instances (length,
  distribution) or the representation holds us at best-fit.
- **Update, 4 October morning: the headroom has now been measured.**
  - [online-frontier-v1](../../experiments/online-frontier-v1/RESULTS.md) finds OPT = L1 on
    129 of 130 of FunSearch-style Weibull instances. Untuned Sum-of-Squares beats FunSearch's heuristic.
  - [online-beyond-ss-v1](../../experiments/online-beyond-ss-v1/RESULTS.md) adds FWSS, which knows the
    item count and keeps state. It ends about 2 bins above the optimum at 1k–100k items, against about
    14 for FunSearch.
  - FWSS is below the best published number in 15/15 settings of the MoH/HMACE leaderboard.
  - Its literature check (`experiments/online-beyond-ss-v1/literature.md`, 38 LLM-AHD papers in full
    text) found no LLM-AHD paper that compares with Sum-of-Squares, primal–dual or re-solving
    policies.
  - [llm-informed-v1](../../experiments/llm-informed-v1/RESULTS.md) is a null result. Telling the LLM
    what its function can know did not lead it to such rules.

### Simplify

- Herrmann & Pallez † found that lines 11–20 of FunSearch's c12 are never useful. They reduced it
  to a two-threshold rule: best-fit when the gap left would be under 7, otherwise first-fit into
  bins with more than 21 left. Understanding the Weibull heuristic took them several rounds of
  experiments by hand.
- Pelleriti et al. † (121 runs, 10,672 programs) find that constant tuning is the most common
  edit. About 30% of added lines re-add previously deleted code. On 13 of 15 runs, 24 Bayesian
  optimisation calls on an intermediate program's constants matched the run's final best.
- Javed, Gobet & Lane 2022 survey program simplification in genetic programming. `autoresearch/explain_code.py`
  (the explanation step of `python -m autoresearch.loop`) is an instance of it: single-part ablation, then
  a greedy minimal program accepted only within ±0.002 on both sides, so repairs are not reported as
  explanations.
- Classic genetic-programming work (Nordin et al. 1996; Langdon & Poli 1998) explains why inert
  terms accumulate under selection, as 8 of our winner's 11 terms did.

### Strategist

- **Closest prior work.**
  - AdaEvolve † keeps a decayed improvement signal per island, picks islands by UCB and opens a
    new island when all have stalled. It has no move costs and never abandons an island. Its
    ablation shows most of the gain comes from an extra LLM "tactics" call, not from the
    allocation.
  - PACEvolve † uses a momentum signal to choose between backtracking and crossover.
  - MetaMax (György & Kocsis 2011) † decides between continuing runs and starting new ones; it
    beat Luby restarts in their experiments and is about 40 lines to implement.
- **Our mixed results match the literature.** Gupta et al. † tested 30 search harnesses with
  3.1M rollouts. None significantly beats greedy sequential best-of-N after Holm correction
  (best p = 0.678).
- **Weak early signals explain premature switches.** Gupta et al. find that the rank
  correlation between partial and final scores is only 0–0.47 at 10% of the budget, rising
  above 0.7 by half. This supports requiring more evidence before leaving an improving leader.
- **Baselines to add in a later version:** MetaMax and Luby restarts, which need no tuning. They
  answer the objection that our patience rule was tuned after the fact.

### Triage

- Wen et al. † report off-the-shelf frontier models at chance at predicting which of two ideas
  wins (GPT-4.1: 51.9%). Fine-tuning plus retrieval reached 77%. Expect a prompted Claude ranker
  to be near random, so any ranker must be compared with the random ranker with confidence
  intervals.
- Ning et al. † find implementation variance 5–10 times larger than rerun variance. The winner
  flips in 26–44% of decisions when a different implementation is used. Labels from a single
  implementation are noisy, and success by tier is confounded with which model implemented the
  idea. Compute AUC on the randomly swapped assignments. `idea-table`, which implements every
  idea with every model, measures this directly.
- Relay, Don't Route † lets a cheap model explore and then hands the population to a strong
  model. It was best in 11 of 12 settings, and random per-call routing was often within noise.
  It is the closest prior work to our promotion step.

### Integrity gate

- HASE † reports exactly our exploit. On circle packing the agent scored 35.46 against a true
  score of 0, then exploited a 1e-8 overlap tolerance until the check was tightened to 1e-12.
- ThetaEvolve † shows that the n = 26 circle-packing record depends on tolerance: AlphaEvolve
  2.63586276 strict, ShinkaEvolve 2.635983 at 1e-7. A flagged record must name which reference it
  beat, and a margin smaller than n × tolerance is not a claim.
- ImpossibleBench † measures cheating with tasks that cannot be solved honestly, where any pass
  counts as cheating. Our problem set contains one such target: Erdős discrepancy's 1160 is a
  proven maximum (its `check_strict` already rejects anything above it), so every "beats record"
  flag there is an exploit. The Erdős squares reference is only conjectured optimal
  (Campbell–Staton), so a flag there is near-certainly an exploit but not provably one.
- Luo, Kasirzadeh & Shah † find that auditing a paper alone catches 55% of pitfalls such as
  post-hoc selection; with logs and code, 82%. Hidden-instance scores must never feed selection,
  and we should publish logs.

### Evaluating the whole framework

- Gideoni, Risi & Gal † run the AlphaEvolve problems we use at $20 per problem. Independent
  sampling and conditioned sampling match or beat ShinkaEvolve (sum-difference: Shinka 1.1095,
  independent sampling 1.1237). They recommend reporting P(A > B) with bootstrap CIs.
- Oved et al. † show that rankings flip with how a budget is split between seeds and iterations.
  On Heilbronn AdaEvolve leads at 1 seed and EvoX at 40, and more seeds exposed an evaluator
  exploit. Report best score against budget over several seeds.
- Ferreira, Hutter et al. † find that classical optimisers (TPE, CMA-ES) beat LLM agents on
  Karpathy's autoresearch task. A classical baseline belongs in any comparison.
- Consequence for `tournament-v1`: include independent sampling next to the plain loop (which
  is greedy best-of-N), run at least 3–5 seeds, report best score against dollars, and treat
  near-saturated problems such as circle packing as ties.

## How the finished runs line up with the literature

Results as of 23:10 on 3 October. Each run's RESULTS.md on its `exp/*` branch is the authority
for its numbers. The coordination log (`docs/logs/OVERNIGHT-2026-10-03.md` on branch
`docs/overnight-log`) records how the runs went. Overall, every finished run agrees with the
literature; none contradicts it.

| Run | Result | Literature |
|---|---|---|
| bp-ceiling-v1 | The limit is mainly the instances, then the missing "open a new bin" option. At 80 items nothing online beats best-fit robustly: the only interval below zero (−0.086 pp) fails under distribution shift. On Weibull the 20-feature space beats best-fit (−0.724 pp at 500 items, −1.182 pp at 5,000). Adding a new-bin option (21 weights) reaches −3.278 pp at 5,000, level with FunSearch's code (−3.329) and the tuned Herrmann & Pallez rules (−3.310). FunSearch's heuristic is worse than best-fit up to 500 items. | Confirms Herrmann & Pallez (gains need long streams; their heuristic loses at small n) and Sim et al. (best-fit wins at short lengths). New relative to them: a linear rule with a new-bin option matches FunSearch's code, so code is not what was missing. |
| memory-ablation (confirmatory, Weibull 5k, 10 seeds × 3 arms) | No evidence that executable counterexamples help; all primary intervals include zero, and executable memory had the worst point estimate. Memory cut harmful proposals (none 0.803, prose 0.202, executable 0.147) mainly by making the model propose no-ops (0.133 → 0.650 → 0.815). Memory was not token-matched. | Related to Pelleriti et al., who find evolutionary coding agents often re-propose earlier code; here memory pushed the model towards proposals that behave like the incumbent. Karimi et al.'s distilled diagnoses, an alternative way to present failures, remain untested. |
| idea-table-v1 (62 of 114 ideas complete after the credit ran out) | The implementer decided success, not the idea: Opus 62/62, Sonnet 60/62, Haiku 10/62. Ranker AUCs: Jev 0.484, Claude Haiku 0.516, Claude Opus 0.564, Codex 0.600 (only Codex clearly above random). Ranked triage did not beat random tiers. Sonnet on every idea was best per dollar. Implementation noise was not measured (the replicate step never ran). | As Wen et al. predict, off-the-shelf rankers are near chance. Relay Don't Route found per-call routing often within noise of random; our idea-level routing likewise did not beat random tiers. That success depended on the implementer echoes Ning et al.'s implementation lottery. |
| tournament-v1 (partial: 17 of 60 runs complete) | Not a budget-matched comparison: the API key ran out of credit 13.6 minutes in. At a common low-spend checkpoint the single-model loops led ShinkaEvolve in area under the score-vs-spend curve (lean +0.233, independent sampling +0.209); triage trailed (−0.156). Final scores did not differ. Circle packing and Erdős squares saturate within 1–3 Sonnet calls. | As Gideoni et al. and Gupta et al. found, simple loops and independent sampling are competitive; and as Oved et al. warn, the result depends on budget. Saturated problems cannot separate methods. |
| strategist-v2 | v1's fixes beat v1 on LABS (+0.137 merit factor, CI [0.043, 0.236]) and NK, mostly through gating crossover. Premature switches on LABS fell from 48% to 21%. A patience rule tuned on dev seeds still wins on LABS. | Gupta et al.: early signals are weak and no harness wins everywhere. Requiring more evidence before leaving is what their finding suggests, and the remaining gap to a tuned rule matches "no universal winner". |
| gate-redteam | Of 68 exploit attempts (28 hand-made, 40 written by Sonnet and Haiku), none gained a material unearned score. The only leak is a sub-tolerance overlap worth about 3e-10, below the record. | Catches the exploit class HASE documents. Its residual leak is bounded by n × tolerance, the same bound ThetaEvolve's tolerance comparison implies. |

## What changed in our experiments

The review's findings went to the six `exp/*` agents through the session coordinating them. The
rule was: no change to a pre-registered design; additions only as disclosed secondary analyses or
before a protocol was frozen. Adopted, as recorded in each protocol's change log:

- **tournament-v1** (protocol frozen after the review):
  - an `independent` arm, citing Gideoni et al. (commit `bafaaa7`);
  - `lean` named as greedy best-of-N (Gupta et al.);
  - problems with headroom first (sum_difference, erdos_squares);
  - P(A > B) with bootstrap intervals, and record ties;
  - every record flag reporting the reference, the margin and n × tolerance, with margins below
    that bound not claimed (ThetaEvolve).
  - The protocol uses 4 seeds rather than the 5 suggested, because that is what fits the $75 cap.
- **bp-ceiling-v1:** a secondary arm with the Herrmann & Pallez two-threshold rules,
  grid-searched per regime (commit `f736fb2`), and a tool that measures best-fit's distance from
  the exact optimum (commit `9141b1a`).
- **Not attributed to the review:** idea-table's randomised idea order and repeated
  implementations were in its protocol before the findings were sent. The repeated
  implementations never ran, because the credit ran out.

The tournament's full grid ($75 Anthropic, $75 Modal) was launched only after the user approved it
directly in the coordinating session. That session did not accept a relayed approval. The grid
stopped 13.6 minutes in when the Anthropic credit was exhausted (about 21:30), leaving 17 of 60
runs complete. The coordination log records the incident and the decision not to run a follow-up
tournament (v2) on open models.

## How this review was done

**Method.**
1. We read the repository: each part's README, results and stated next steps, and the hackathon
   brief.
2. Four search agents ran in parallel, one per area: Falsify, Strategist, Triage plus the gate,
   and recent comparable systems. They were told to report only papers they had confirmed.
3. All 44 arXiv IDs were checked against the arXiv API, and each title matched.
4. About 30 key claims were checked by hand on arXiv abstract or full-text pages.
5. Three reading agents read 22 papers in full: bin packing, search and evaluation, and triage
   plus integrity. Their most consequential numbers were re-checked against the papers: RAISE's
   tables, Gupta et al.'s Holm p-value, ASRO's table and Herrmann & Pallez's 90-item result.
6. We downloaded 56 PDFs, one PostScript file and one HTML page from open sources.
   `fetch_papers.py` reproduces this.

**Decisions.**
- PDFs are not committed: the repository is public, and most papers may not be redistributed.
- HAL's bot check and ACM's paywall were not circumvented; those six papers are listed in
  `fetch_papers.py` for download in a browser.
- Findings went to the experiment agents only through their coordinating session, so they had
  one source of instructions.

**Corrections made along the way.**
- A search agent said FunSearch's bin-packing heuristic was evolved on 5,000-item instances. The
  heuristic that loses to best-fit below 90 items (c12) was evolved on 20 instances of 120 items.
- A search agent listed AdaEvolve under two arXiv IDs. The correct one is 2602.20133; 2602.23413
  is EvoX.
- A first draft called the Erdős squares reference exact. `problems/erdos_squares/verify.py`
  says it is the Campbell–Staton conjecture, so only Erdős discrepancy (1160, proven) is a strict
  canary.
- ASRO's main text does not list the cross-bin statistics a reading agent attributed to its
  evolved solvers, so this document does not claim them.

**Limitations.**
- The search covered arXiv and the open web, not the full literature, so "new" means new among
  the papers we found.
- Most 2026 papers are preprints without peer review.
- Papers not marked † were judged from abstracts and key sections, and some numbers in read
  papers come from figures.
- The Sum-of-Squares feature `N(gap+item) − N(gap)` is our own derivation and untested as a per-bin
  feature. Sum-of-Squares itself was later run in full; see the 4 October update above.

**Cost.** No API or compute spend on experiments. The review used this Claude Code session and
its subagents only.

**Reproduce.** `python3 docs/literature/fetch_papers.py` downloads every available paper; add
`--only <text>` to fetch a subset. The papers it cannot fetch are printed with links at the end.

**Next steps.**
- Rephrase the claims in the root README and pitch as in the novelty table; the coordinating
  session owns the README.
- Rerun the tournament with credit, budget-matched, on problems that do not saturate.
- Consider ASRO-style instance generators and the Sum-of-Squares feature for a Falsify v5, in the
  Weibull regime where bp-ceiling found headroom.
- Research papers: see [docs/papers/outlines/](../papers/outlines/README.md).

## Reading list

Start with these:

| Paper | Why |
|---|---|
| Herrmann & Pallez 2025, [2510.27353](https://arxiv.org/abs/2510.27353) † | Simplify's precedent; best-fit wins below about 90 items |
| Sim, Renau & Hart 2025, [2501.11411](https://arxiv.org/abs/2501.11411) † | Best-fit first across 6,064 instances |
| Liu, Figalli et al. 2026, RAISE, [2606.31801](https://arxiv.org/abs/2606.31801) † | Adversarial instance search in the loop |
| Ke et al. 2026, ASRO, [2601.22896](https://arxiv.org/abs/2601.22896) † | Co-evolved instance generators |
| Gideoni, Risi & Gal 2026, [2602.16805](https://arxiv.org/abs/2602.16805) † | Simple baselines on our problems |
| Oved et al. 2026, [2609.19799](https://arxiv.org/abs/2609.19799) † | Seeds vs iterations; reporting protocol |
| Gupta et al. 2026, [2607.18235](https://arxiv.org/abs/2607.18235) † | No universally superior harness |
| Cemri et al. 2026, AdaEvolve, [2602.20133](https://arxiv.org/abs/2602.20133) † | Closest to Strategist |
| Yan et al. 2026, PACEvolve, [2601.10657](https://arxiv.org/abs/2601.10657) † | Backtrack-or-crossover rule |
| Dwork et al. 2015, [1506.02629](https://arxiv.org/abs/1506.02629); Blum & Hardt 2015, [1502.04585](https://arxiv.org/abs/1502.04585) | Theory for promotion gates |
| Wen et al. 2025, [2506.00794](https://arxiv.org/abs/2506.00794) † | Predicting which idea wins |
| Ning et al. 2026, [2607.26587](https://arxiv.org/abs/2607.26587) † | The implementation lottery |

By part:

- **Falsify:**
  - Bin-packing theory: Csirik et al., Sum-of-Squares ([cs/0210013](https://arxiv.org/abs/cs/0210013)); Bender et al. 2007, Sum-of-Squares heuristics; Kenyon & Mitzenmacher 2002, linear waste of best-fit; Angelopoulos et al. 2022 † ([2102.03311](https://arxiv.org/abs/2102.03311)).
  - Adversarial inputs: MetaOpt ([2311.12779](https://arxiv.org/abs/2311.12779)); Karimi et al. 2025 † ([2510.08755](https://arxiv.org/abs/2510.08755)); Nikoleit et al. 2026 ([2601.16849](https://arxiv.org/abs/2601.16849)).
  - Background: Solar-Lezama et al. 2006 (CEGIS); irace (López-Ibáñez et al. 2016); Cawley & Talbot 2010; delta debugging (Zeller & Hildebrandt 2002); the Hypothesis reducer (MacIver & Donaldson 2020).
- **Simplify:**
  - Pelleriti et al. 2026 † ([2605.20086](https://arxiv.org/abs/2605.20086)).
  - Li et al. 2026 (DeepMind), distilling AlphaEvolve discoveries by hand ([2602.16928](https://arxiv.org/abs/2602.16928)).
  - Langdon & Poli 1998; Nordin, Francone & Banzhaf 1996.
  - Javed, Gobet & Lane 2022, survey of GP simplification ([doi:10.1007/s10618-022-00830-7](https://doi.org/10.1007/s10618-022-00830-7)); Kinzett, Zhang & Johnston 2010 on noise in numerical simplification ([doi:10.1109/CEC.2010.5586181](https://doi.org/10.1109/CEC.2010.5586181)).
- **Strategist:**
  - Restarts: MetaMax, György & Kocsis 2011 † ([1401.3894](https://arxiv.org/abs/1401.3894)); Luby, Sinclair & Zuckerman 1993; bet-and-run (Friedrich, Kötzing & Wagner 2017).
  - Adaptive operator selection: Da Costa et al. 2008; Fialho et al. 2008, 2010.
  - Maximising the best found: Cicirello & Smith 2005, max k-armed bandit; Weitzman 1979.
  - Foraging under noisy estimates: Davidson & El Hady 2019 ([1809.05023](https://arxiv.org/abs/1809.05023)); Kilpatrick et al. 2021.
  - Calibration: Cheng et al. 2026, diff vs rewrite costs ([2604.27296](https://arxiv.org/abs/2604.27296)); Packebusch & Mertens 2016, LABS optima.
- **Triage:**
  - Model handoff and routing: Relay, Don't Route † ([2608.05651](https://arxiv.org/abs/2608.05651)); LEVI † ([2605.09764](https://arxiv.org/abs/2605.09764)); AdaptEvolve ([2602.11931](https://arxiv.org/abs/2602.11931)); FrugalGPT; RouteLLM.
  - Screening ideas before running them: AlphaResearch ([2511.08522](https://arxiv.org/abs/2511.08522)); FOREAGENT ([2601.05930](https://arxiv.org/abs/2601.05930)); the Ideation–Execution Gap ([2506.20803](https://arxiv.org/abs/2506.20803)).
  - Name clash: Madeyski 2026 ([2604.07494](https://arxiv.org/abs/2604.07494)).
- **Integrity gate:**
  - HASE † ([2607.03935](https://arxiv.org/abs/2607.03935)); ThetaEvolve † ([2511.23473](https://arxiv.org/abs/2511.23473)); ImpossibleBench † ([2510.20270](https://arxiv.org/abs/2510.20270)).
  - Luo, Kasirzadeh & Shah † ([2509.08713](https://arxiv.org/abs/2509.08713)); POPPER ([2502.09858](https://arxiv.org/abs/2502.09858)); METR, "Recent frontier models are reward hacking" (2025).
- **Evaluation and benchmarks:**
  - Ferreira, Hutter et al. † ([2603.24647](https://arxiv.org/abs/2603.24647)).
  - Benchmarks: CO-Bench, HeuriGym, ALE-Bench, AlgoTune.
