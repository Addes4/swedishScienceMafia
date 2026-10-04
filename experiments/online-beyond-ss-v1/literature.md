# Literature check: online bin packing on FunSearch-style benchmarks

Searched on 2026-10-04 with OpenAlex, web search and arXiv PDFs. The arXiv API and Semantic Scholar both returned HTTP 429. No git repository was modified.

**Read-status codes.**
- **FT** = I extracted the full text and read the relevant sections and tables.
- **FT-grep** = I extracted the full text and searched it for the setting and the numbers, without reading it closely.
- **ABS** = I saw only the abstract, a search snippet or OpenAlex metadata.

## 0. Bottom line

1. **No published online policy beats 0.483% over L1 on FunSearch's released Weibull 5k set.** No paper reports any number on that exact set except FunSearch itself (0.68%).
   - Across all Weibull(45,3), C=100, 5k-item settings, the lowest credible held-out numbers are:
     - HMACE: 0.585% (2605.07214);
     - MoH: 0.600% (2505.20881).
     - Both use 100 fresh instances, the L1 bound, and best fit at 4.149% on the same instances.
   - Lower numbers exist, but none is comparable:
     - QUBE: 0.41% over L2. QUBE generated its own 5 instances and reports the best of 10 runs, probably searched on those same instances.
     - RefineEvo: 0.25%. Its best-fit baseline is 2.26%, so its instances or bound differ from Weibull(45,3).
     - GigaEvo: claims 0.55% without specifying the setting.
2. **No paper runs a distribution-learning or re-solving online policy on Weibull(45,3).** I checked ProfilePacking, CGPP/pattern pricing, primal–dual, Banerjee–Freund and Liu–Li.
   - None of them is compared with FunSearch or any LLM-evolved heuristic.
   - None of the 38 LLM-AHD papers I checked runs Sum-of-Squares (SS) or any of these policies.
3. **Verdict.** Both claims look new:
   - a distribution-learning online policy below 0.3% over L1 on FunSearch's Weibull 5k;
   - a same-instance, same-metric comparison across the LLM-AHD leaderboard that includes the classical stochastic online-bin-packing algorithms.

   Caveats are in §3.

## 1. Leaderboard

### 1.1 Read these numbers with care: settings differ

- **Lower bound.**
  - FunSearch's paper says "fraction of excess bins used over the **L2** lower bound" (FT via PMC).
  - FunSearch's released notebook computes **L1** = ceil(sum/C) ("we calculate a lower bound on the optimal number of bins using the L1 bound"). Its excess is (mean bins − mean L1) / mean L1 over the instances. I read the code directly.
  - EoH's evaluation code also says "excess over the L1 lower bound".
  - The other papers use different bounds:
    - QUBE and X-evolve: L2;
    - MoH: L1, stated;
    - Sim et al.: sum/C without the ceiling;
    - 2407.10873: "best-known optimum";
    - the rest: "lower bound (Martello & Toth)".
  - Since L2 ≥ L1, a number over L2 can only understate excess over L1.
- **Instances.** Almost every paper generates its own 5 to 100 instances. Best fit at "5k, C=100" ranges from 3.88% (X-evolve) to 4.31% (MCTS-AHD), and is 2.26% in RefineEvo. Use each row's best-fit number to calibrate it.
- **"C=500" is not one setting.** Best fit at 5k items, C=500 is:
  - 3.91% on EoH's set, where item sizes scale with capacity;
  - 0.55% on MCTS-AHD's set;
  - 0.47% on MoH's set.
- **Aggregation.** Papers report the mean of 3 runs, the best of 3, 5 or 10 runs, or the mean of the top-1 or top-50 programs. The table states which.

### 1.2 Weibull(45,3), C=100, 5,000 items

| Paper (ID) | Read | Instances (BF on them) | Method: % excess | Bound | Notes |
|---|---|---|---|---|---|
| FunSearch, Nature 2024, doi 10.1038/s41586-023-06924-6 | FT (PMC) + notebook code | Released "Weibull 5k", 5 inst. (BF 3.98, FF 4.23) | **FunSearch 0.68** | Paper text says L2; notebook computes L1 | Training protocol for the Weibull heuristic not verified |
| EoH, 2401.02051 | FT | EoH 5k_C100 test, 5 inst. (BF 4.08) | EoH 0.80; FunSearch heuristic 0.80 | L1 (code) | Evolved on FunSearch's 5 instances (per Herrmann & Pallez) |
| Zhang et al. (PPSN'24), 2407.10873 | FT | 5 Weibull 5k instances that guide the search | Best top-1 over 5 runs: 0.59 (FunSearch with CodeLlama-7B/34B or GPT-4); mean 0.63±0.03 | Distance to "best-known optimum"; equal to L1 not verified | In-sample |
| MEoH, 2409.16867 | FT | 5 inst. | EoH 0.753; FunSearch (own run) 0.802; MEoH 1.387 | "Relaxation lower bound" | |
| HSEvo, 2412.14995 | FT | 5 generated (search set) | HSEvo 1.07±1.11; FunSearch 2.05±2.01; ReEvo 2.48±3.74; EoH 3.17±2.97 | M&T lb | Units not stated (presumably %); in-sample; GPT-4o-mini |
| QUBE, 2412.20694 | FT | Own 5 inst. (BF not given) | **QUBE 0.41**; FunSearch replica 0.55 | L2 | Best of 10 runs; OR runs are explicitly on the test instances, Weibull probably the same |
| MCTS-AHD, 2501.08603 | FT | MCTS-AHD 5k_100 set, 5 inst. (BF 4.31) | MCTS-AHD 1.06; FunSearch 1.30; HSEvo 1.43; EoH 1.63; ReEvo 2.72 | "Lower bound" | GPT-4o-mini, mean of 3 runs; 5k_100 is an in-domain scale |
| CALM, 2505.12285 | FT | MCTS-AHD set | CALM 0.83 (API), 0.85 (Qwen-7B + GRPO); EvoTune 4.27 | M&T | Mean of 3 runs |
| MoH (ICLR'26), 2505.20881 | FT | **100 inst.** (BF 4.149) | **MoH 0.600**; EoH 0.827; HSEvo 1.088; MCTS-AHD 1.769; ReEvo 2.022; FunSearch 2.165 | **L1, stated** | Best heuristic of 3 runs; held-out |
| HMACE, 2605.07214 | FT | Same table and instances as MoH | **HMACE (GPT-5.4) 0.585**; EoH* 0.801; CORAL 0.820 | MoH's L1; text says "FunSearch L2" | Held-out |
| X-evolve, 2508.07932 | FT | Own 5-inst. test (BF 3.88) | X-evolve 0.67 | L2 | Train/validation/test split; wrongly says FunSearch's Weibull heuristic is not public |
| HiFo-Prompt, 2508.13333 | FT | EoH 5k_C100 test (BF 4.08; mean LB 2006.2) | HiFo 0.69; ReEvo 0.78; MCTS-AHD 0.99; EoH 1.02 | LB | Mean of 3 runs |
| GigaEvo, 2511.17592 | FT | **Not specified** | "0.55% vs FunSearch 0.68%" ("new SOTA") | "Optimal offline", unspecified | Llama 3 7B/70B; no protocol given |
| TIDE, 2601.21239 | FT | MCTS-AHD set | TIDE 0.73; EoH 1.20; MCTS-AHD 2.49 (their run) | As MCTS-AHD | Mean of 3 runs |
| PathWise, 2601.20539 | FT | 10 inst. (BF 4.19) | PathWise 1.38 (GPT-4o-mini) | LB | Mean of 3 runs |
| CDEoH, 2603.19284 | FT | Own (LLM4AD) | CDEoH 1.054; ReEvo 1.611; EoH 2.406; FunSearch 3.878 | LB | 200-sample budget |
| BEAM, 2604.12898 | FT | "Weibull5k" | BEAM best 2.58; EoH best 3.13 | — | Says EoH's published ~0.6% "cannot [be reproduced] even if we triple the budget (>2% gap)" |
| ReVEL, 2604.04940 | FT | EoH-style (BF 4.08) | ReVEL 1.13; ReEvo 0.80 | LB | |
| RefineEvo, 2607.11358 | FT | 64 streams (**BF 2.26**) | RefineEvo 0.25; OpenEvolve 0.28±0.03; MCTS-AHD 0.31; HSEvo 0.33; EoH 0.39 | M&T | **Not comparable:** best fit is far below the 3.9–4.3% expected for Weibull(45,3) |
| Herrmann & Pallez, 2510.27353 | FT | 1000 inst. | ab-WorstFit (a=1, b=21) is 0.12% better than c14 (FunSearch), 0.15% better than EoH and 3.39% better than BF | **Relative to BF bins, not excess over LB** | Says there are no prior studies of online bin packing on Weibull(45,3) |
| Sim, Renau & Hart, 2501.11411 | FT | Angelopoulos's Weibull set + BPPLib (not Weibull(45,3)) | Weibull set ≈ FunSearch Weibull heuristic 16.8, BF 3.0, EoH 12.2 | sum/C | Parsed from a heatmap; column order inferred, **not verified** |
| LLM4AD 2412.17287; LLaMEA-HPO 2410.16309 | FT | 5 FunSearch-style inst. | Convergence plots only | — | No numbers |
| ReEvo 2402.01145; EvoTune 2504.05108 | FT | — | No Weibull online BPP (EvoTune: OR only) | — | |
| EoH-S 2508.03082 (AAAI'26); AST operator 2604.16420; LHNS (CEC'25, ABS) | FT / FT / ABS | Tested at C=200/500 only | e.g. EoH-S: n5k c200 0.33, n5k c500 0.25, n10k c500 0.10 | LB | Not C=100 |

### 1.3 Weibull(45,3), C=100, 10,000 and 100,000 items

| Paper | 10k | 100k | Notes |
|---|---|---|---|
| FunSearch | **0.32** | **0.03** | Released set; number of 100k instances not stated in the paper (not verified) |
| EoH (Table 1) | EoH 0.61; FunSearch 0.33 | — | EoH test set |
| QUBE | **0.29** | — | L2; best of 10 runs; probably in-sample |
| X-evolve | 0.38 | 0.12 | 100k is a single instance; L2 |
| MoH / HMACE | 0.414 / 0.404 | — | 100 inst., L1 |
| TIDE / CALM / MCTS-AHD | 0.36 / 0.50 / 0.74 | — | MCTS-AHD set |
| HiFo-Prompt | 0.42 | — | EoH set |
| MEoH table | EoH 0.537; MEoH 0.651; FunSearch (own run) 2.595 | EoH 0.391; MEoH 0.080; FunSearch (own run) 3.319 | |
| PathWise | 1.23 | — | |
| CDEoH / ReVEL | 0.483 / 0.59 | — | ReVEL's table lists EoH = ReEvo = 0.33 at 10k |
| RefineEvo | 0.19 | 0.01 | Not comparable (BF 2.18 at 10k) |
| BEAM | best 1.99 | best 1.82 | |

### 1.4 OR1–OR4 (Falkenauer u120/u250/u500/u1000, C=150, 20 instances each)

| Paper | OR1 | OR2 | OR3 | OR4 | Protocol |
|---|---|---|---|---|---|
| FunSearch (FT) | 5.30 (BF 5.81, FF 6.42) | 4.19 (6.06, 6.45) | 3.11 (5.37, 5.74) | 2.47 (4.94, 5.23) | Evolved on generated OR1-size instances; held-out |
| QUBE (FT) | **4.06** | **3.73** | **1.79** | **1.75** | **Searched directly on the test instances**; best of 10 runs; FunSearch replica 4.48/4.07/3.02/2.06 |
| X-evolve (FT) | 5.50 | 4.43 | 2.98 | 2.45 | Trained on OR1-like, validated on OR2-like generated data; L2 |
| EvoTune (FT) | — | — | Validation = 20×500, C=150 "OR-Library" instances; best top-1 mean over 10 seeds 2.80 (validation), **2.59±0.13 on fresh OR-distribution test** (Phi, 22.4k samples) | — | FunSearch baseline with the same LLMs: 2.92 on test |
| ASRO, 2601.22896 (FT) | Falkenauer U pooled: ASRO-EoH 4.53, EoH 5.00, BF 5.39 | | | | Bound unspecified; their "Weibull" set has BF 1.75, so it is not Weibull(45,3) |
| Zhang et al. 2407.10873 (FT) | — | Generated 20×250 "OR" set: best 5.34 ((1+1)-EPS) | — | — | Best-known-optimum metric |
| Herrmann & Pallez (FT) | Uniform(20,100), C=150, 500 items: ab-FirstFit is 0.71% better than c12 (FunSearch OR) and 2.71% better than BF | | | | Relative to BF |

Context from the team's own probe (not literature): SS gets 7.107% on OR3, worse than best fit.

### 1.5 Best reported numbers

- **(a) Weibull 5k, C=100.**
  - On FunSearch's released set: FunSearch's 0.68% is the only published number.
  - In-sample on the released set: 0.59%, if 2407.10873's five instances are FunSearch's (not verified).
  - Lowest anywhere: RefineEvo 0.25% (not comparable) and QUBE 0.41% (L2, own instances, best of 10, probably in-sample).
  - Best held-out under L1: **HMACE 0.585%** and MoH 0.600%, on 100 instances.
  - GigaEvo claims 0.55% but gives no setting.
- **(b) Weibull 10k, C=100.**
  - QUBE 0.29% (L2, caveats as above);
  - FunSearch 0.32%;
  - RefineEvo 0.19% (not comparable).
- **(c) Weibull 100k, C=100.**
  - FunSearch 0.03%;
  - RefineEvo 0.01% (not comparable);
  - MEoH 0.080%;
  - X-evolve 0.12% (one instance).
- **(d) EoH-style settings, on EoH's own test sets (5 instances each, BF 3.9–4.9%).**

  | Items | C=100 | C=500 |
  |---|---|---|
  | 1k | HiFo-Prompt 2.19% (EoH 2.24%) | HiFo-Prompt 2.07% |
  | 5k | HiFo-Prompt 0.69% | HiFo-Prompt 0.66% |
  | 10k | FunSearch heuristic 0.33% (EoH Table 1) | HiFo-Prompt 0.40% |

  - On MCTS-AHD's sets, C=500 is near-trivial (best fit 0.25–0.55%). CALM with Qwen reports 0.00%, 0.17% and 0.14% at 1k, 5k and 10k.
  - On MoH's 100-instance sets: HMACE 0.079% at 5k, C=500 and 0.020% at 10k, C=500.

## 2. Prior art: near-optimal or distribution-learning online policies

**Angelopoulos, Kamali & Shadkami, 2102.03311 (IJCAI'22 / JAIR, doi 10.1613/jair.1.14820). FT.**
- **Method.** ProfilePacking and Hybrid(λ) mixed with FirstFit. Frequency predictions come from a prefix of the input; the profile has m=5000 items and is packed with FFD rather than optimally.
- **Data.** Weibull with shape 3.0 and scale 1000, scaled to k=100; how the scaling works is not verified. Also BPPLib GI, Schwerin, Randomly Generated, Hard28 and Wäscher. n = 10⁶, single sequences, plus 20-sequence averages.
- **Results.**
  - Plots only: bins against prediction error, compared with FF, BF and the L2 bound. **No table, so the gap to OPT cannot be read numerically.**
  - Hybrid(λ ∈ {0.25, 0.5, 0.75}) beats FF and BF on Weibull for η < ~0.27.
  - Pure ProfilePacking degrades quickly with error.
- **Baselines.** No SS (mentioned only for its 2–2.7 competitive ratio). It predates FunSearch, and FunSearch cites it.

**Learning-augmented follow-ups.**
- Online bin covering with frequency predictions (2401.14881, SWAT'24): covering, not packing. ABS.
- Dynamic bin packing with predictions (SIGMETRICS'23); tight bounds for dynamic bin packing with predictions (doi 10.1145/3700437): dynamic setting. ABS.
- Online bin packing with item-size estimates (2505.09321): theory only; the full text has no experiments. FT-grep.
- None uses Weibull(45,3) or compares with FunSearch.

**Pattern-based distribution learning (Nottingham Ningbo).** This is the closest methodological prior art.
- **Papers.**
  - PatternPack (Symmetry 2022, doi 10.3390/sym14071301; ABS);
  - fuzzy-logic bin selector (ESWA 2024, doi 10.1016/j.eswa.2024.123515; ABS);
  - CGPP column-generation pattern pricing (Zhang et al., 2409.04456; FT);
  - risk-aware pattern adjustment (ESWA 2026, doi 10.1016/j.eswa.2025.131074; ABS: SSRN returned 403);
  - H. Zhang's PhD thesis (FT-grep).
- **Method.** A sliding-window frequency estimate, LP or column-generation patterns, and a best-fit fallback. This is close to "LP re-solving with a learned distribution".
- **CGPP data.**
  - uniform and normal mixtures with 20k items;
  - Balaji's BW/LW/PP distributions;
  - Burke dual-normal;
  - Poisson;
  - Weibull with shape {0.5, 1, 1.5, 2, 5}, 10⁵ items, C=100;
  - the thesis's risk-aware chapter uses Weibull(k=2, λ=30).
- **CGPP results and baselines.** Absolute bin gaps over L2 (for example, Weibull shape 2: CGPP 133.8 bins against BF 1039.8). Baselines are BF, ORL, ProfilePack, PatternPack and FPP.
- **No SS, no FunSearch comparison and no Weibull(45,3).** The thesis mentions SS and FunSearch only in related work.

**Banerjee & Freund.**
- SIGMETRICS 2020, doi 10.1145/3393691.3394224: 2-page abstract (FT). Full version: "Good prophets know when the end is near", Management Science 2024, doi 10.1287/mnsc.2023.04307 (FT via NSF PAR).
- **Experiments.** Toy instances only: their Example 1.1, and B=20 with uniform items {1..20}. They compare their uniform-loss re-solving algorithm with adaptive re-solving (ARC), the static fluid policy (SRC) and SOS, in loss-against-T plots. Their algorithm reaches O(1) loss; SS and SRC grow as Θ(√T).
- No Weibull, no FunSearch.

**Gupta & Radovanović, 1211.2687 (Oper. Res. 2020). FT.** SS against PD-exp on three toy distributions (BW with B=9, PP with B=10, LW with B=10), one sample path with T up to 10⁵, regret plots. No Weibull.

**Ayyadevara, Dabas, Khan & Sreenivas, 2205.03622 (ICALP'22; doi 10.1145/3728642). FT-grep.** Theory only; no experiments.

**Liu & Li, 2112.03200 ("Online bin packing with known T"). FT.**
- **Method.** An LP-based adaptive re-solving algorithm (their Algorithm 2), using a learned distribution and a known T.
- **Experiments.** Compared with SS and Gupta–Radovanović on the same three toy distributions, T ≤ 2000, 100 trials. It sometimes reaches bounded regret.
- No Weibull.

**Bender et al., JEA 2007 ("Sum-of-squares heuristics for bin packing and memory allocation"). ABS (search snippet).** An experimental comparison of SS against BF. Neither dominates; SS does better when item sizes vary less. Not Weibull(45,3) as far as the snippet shows.

**Deep RL.**
- Balaji et al. ORL (1911.10641, FT): PPO against SS and BF on toy BW/PP/LW distributions (B=9 and B=100). No Weibull.
- I found no 1-D deep-RL paper that compares with FunSearch. The 2026 "Deep RL on item-compatibility graphs for 1-D bin packing" was seen as a title only.

**OpenAlex citation intersections.** FunSearch has 494 citing works indexed; preprint coverage is incomplete.
- The DOI given for Csirik et al., 10.1145/1120582.1120586, resolves in OpenAlex to "Hidden word statistics". The correct DOI is **10.1145/1120582.1120583** (62 citers).

| FunSearch citers that also cite… | Result |
|---|---|
| Csirik et al. 2006 (JACM), the 2000 STOC version, or cs/0509031 | **None** |
| Angelopoulos et al. (25 citers) | Sim et al. 2501.11411; LHNS (CEC'25); Zhang et al. ESWA 2026 (risk-aware patterns) |
| Gupta–Radovanović | ESWA 2026 only |
| Banerjee–Freund, Ayyadevara, Liu–Li, ORL | **None** |
| Castiñeiras' Weibull benchmark | 2407.10873; Sim et al. |

**Full-text checks.**
- None of the 38 LLM-AHD and benchmark PDFs I extracted mentions Sum-of-Squares or Csirik et al. as a method. TIDE cites only Coffman et al.'s survey, which has Csirik as a co-author.
- None compares with SS, primal–dual, ProfilePacking or re-solving policies.
- Herrmann & Pallez and Sim et al. compare only with the Any-Fit family.

**GitHub.** `arnoldcastro5000/crucible-loop` appeared in search. Its snippet mentions SS as a concept and FunSearch's heuristics as `bin_packing_online` baselines, which matches this team's repo naming. The repo now returns 404, so no numbers are available (not verified). `jorsacademy/llm-guided-heuristic-discovery-bin-packing` also returns 404.

## 3. Verdict

**1. "A distribution-learning online policy reaching < 0.3% over L1 on FunSearch's Weibull 5k" looks new.**
- No published online number on Weibull(45,3), C=100, 5k is below 0.41% except RefineEvo's non-comparable 0.25%.
- No distribution-learning or re-solving policy has been run on this benchmark.

To make the claim defensible:
- (i) Report it on FunSearch's released 5 instances **and** on ≥100 fresh instances with L1, plus best fit as a calibration row. MoH and HMACE's 100-instance protocol is the closest existing comparator (0.585–0.600%).
- (ii) Show that the policy uses only past items: no prefix oracle and no known T, or state it if it does. ProfilePacking's original setup uses predicted frequencies.
- (iii) Report the gap between OPT and L1 on these instances. I found **no paper computing exact OPT** for FunSearch's Weibull instances, so it is unknown whether <0.2% over L1 is reachable. At 5k items, 0.2% is about 4 bins over an L1 of roughly 2006.
- (iv) Cite Angelopoulos et al. and Zhang/Bai's CGPP as methodological precedents. Cite Herrmann & Pallez, Sim et al. and BEAM's non-reproduction remark as context on the benchmark.

**2. A comparison across the whole LLM-AHD leaderboard is new in two respects:**
- **(a)** It would be the first on the same instances with the same metric. Today best fit at "5k, C=100" ranges from 2.26% to 4.31% across papers, and the bounds are L1, L2, sum/C or "best-known".
- **(b)** It would be the first to include classical stochastic-online algorithms.

The largest existing same-instance comparison is MoH/HMACE's table: 11 methods, 15 capacity × size settings, 100 instances each, with no OR baselines beyond FF and BF.

**Not verified:**
- QUBE's Weibull train/test protocol;
- GigaEvo's setting;
- whether 2407.10873 used FunSearch's released instances;
- HSEvo's units;
- Angelopoulos's item scaling;
- the number of FunSearch's 100k instances;
- the Sim et al. heatmap values;
- ESWA 2026, ESWA 2024 and Symmetry 2022 full texts.
