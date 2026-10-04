# LLM-AHD "TSP step-by-step construction" (select_next_node): leaderboard, baselines, critiques, artifacts

Compiled 2026-10-04. Sources were read as full text: arXiv HTML pages (converted to text), PDFs through pypdf, and GitHub files through the GitHub API.

Labels used below:
- **[V]**: verified in the paper's own text or table.
- **[C]**: computed by me from published numbers. The arithmetic is shown.
- **[I]**: my inference. It is not stated in the paper.

All gaps are mean optimality gaps on uniform random points in the unit square, unless a row says otherwise.

---

## 0. The task

The task is the AEL/EoH/ReEvo/MCTS-AHD interface `select_next_node(current_node, destination_node, unvisited_nodes, distance_matrix)`. The tour starts at node 0, and the destination is node 0. The function receives the full distance matrix at every step.

The interface originates with **AEL**, Liu et al., "Algorithm Evolution Using Large Language Model", arXiv:2311.15249. ReEvo states: "We used the best heuristic found in AEL [46] as the seed for ReEvo."

MCTS-AHD's test protocol is used by CALM, Clade-AHD, RedAHD and TIDE (n=50):
- 1,000 instances per n, generated with `np.random.seed(1234)`.
- Optima from LKH: 5.675 (n=50), 7.768 (n=100), 10.659 (n=200).

---

## 1. Leaderboard

### 1a. Pure `select_next_node` on uniform instances

Each row gives the best configuration reported in that paper for its own method [V], unless marked otherwise.

| Paper (arXiv) | LLM | # test inst. / ref. | n=20 | n=50 | n=100 | n=200 | n=500 | n=1000 |
|---|---|---|---|---|---|---|---|---|
| AEL (2311.15249) Table I | GPT-4 | 64 / LKH3 | 6.2 | 11.1 | 10.5 | 11.2 | **12.8** | **12.8** |
| MCTS-AHD (2501.08603) Table 1 | GPT-4o-mini | 1000 / LKH | – | 9.69 | 11.79 | 13.71 | – | – |
| MCTS-AHD Table 12 | GPT-3.5-turbo | 1000 / LKH | 7.71 | 11.82 | – | – | – | – |
| MCTS-AHD Table 10 | Qwen2.5-Coder-32B | 1000 / LKH | – | 10.52 | 11.81 | – | – | – |
| MCTS-AHD Table 9, best single run of 10 | GPT-4o-mini | 1000 / LKH | – | 8.48 [C: 6.156/5.675] | – | – | – | – |
| MoH (2505.20881) Table 1 (best of 3 runs) | GPT-4o-mini | 128 / Concorde | 6.837 | 9.893 | 11.444 | 13.307 | 14.224 | 15.049 |
| CALM (2505.12285) Table 2 | Qwen2.5-7B-Instruct-INT4 + GRPO | 1000 / LKH (MCTS-AHD sets) | – | 10.04 | 11.58 | 13.41 | – | – |
| HiFo-Prompt (2508.13333) Tables 1 and 7 | Qwen2.5-Max | not stated / LKH3 | **3.619** (n=10: 1.654) | 6.625 | 8.582 | **8.877** | – | – |
| HiFo-Prompt Table 11 | GPT-4o-mini | same | – | 7.058 | 9.579 | – | – | – |
| Clade-AHD "Beyond the Node" (2602.00549) Table I | GPT-4o-mini | 1000 / LKH (MCTS-AHD sets) | – | 10.39 | 9.22 | 11.30 | – | – |
| PathWise (2601.20539) Table 1 | GPT-5-nano (reasoning: medium) | 250 / LKH-3 (opt 5.687/7.767/10.709) | – | 8.41 | 11.85 | 12.14 | – | – |
| TIDE (2601.21239) Table 1 | Qwen3-Max | 1000 (n50) / 128 (n100) / 64 (n200); LKH3 | – | **4.76** | 7.15 | 10.65 | – | – |
| SimpleEvol (2609.37172) Tables 3 and 11 | GPT-5-mini | 64 per n (own seeds) / elkai-LK | – | 4.77 | **6.47** | 9.49 | – | – |
| MeEvo (2606.14202) Table X | DeepSeek-V4-Flash | 64 / LKH | – | 11.55 | 11.84 | 14.59 | – | – |
| AHD Agent (2605.08756) Table 1 (w/ SR) | Qwen3-4B-Instruct (RL) | 64 / LKH | – | – | 13.86 | 15.14 | – | – |
| Agentic ESOpt (2608.17310) Table 5 | LLaMA-3.1-8B | MCTS-AHD sets (opt 3.8199/5.6750) | 9.42 [C] | 13.55 [C] | – | – | – | – |
| RefineEvo (2607.11358) Table 1 (objective only) | DeepSeek-V3 | 64 / no optimum given | – | obj 6.176 (≈8.5 [I]) | obj 8.541 (≈10.1 [I]) | obj 11.868 (≈10.9 [I]) | obj 18.476 (≈11.8 [I]) | obj 25.851 (≈11.9 [I]) |
| RefineEvo Table 21 (objective only) | Claude Opus 4.6 | 64 / no optimum given | – | – | obj 8.018 (≈3.3 [I]) | obj 11.202 (≈4.7 [I]) | obj 17.478 (≈5.8 [I]) | – |

The authors' own reruns of baselines vary widely. ReEvo, for example:
- MoH table: 11.966 / 13.133 / 14.403 (n = 50 / 100 / 200).
- HiFo table (Qwen2.5-Max): 10.239 / 12.577 / 14.890.
- TIDE table (Qwen3-Max): 8.27 / 10.06 / 10.75.
- PathWise table (GPT-5-nano, low reasoning): 28.13 / 30.23 / 31.51.

HSEvo by TIDE: 8.04 / 10.01 / 10.80. MCTS-AHD by TIDE: 8.19 / 10.18 / 11.09.

**Best published gap with a pure select_next_node heuristic, uniform instances and an explicit gap [V]:**
- **n=50: 4.76%.** TIDE, Qwen3-Max, 1,000 MCTS-AHD instances. SimpleEvol with GPT-5-mini reports 4.77%.
- **n=100: 6.47%.** SimpleEvol, GPT-5-mini. See the caveat below. The next best is TIDE at 7.15% (128 instances).
- **n=200: 8.877%.** HiFo-Prompt, Qwen2.5-Max. SimpleEvol reports 9.49%.
- **n=20:** HiFo-Prompt, 3.619%.
- **n=500 and n=1000:** AEL with GPT-4, 12.8% at both sizes.
- Matched on GPT-4o-mini, the best results are:
  - n=50: MCTS-AHD 9.69%.
  - n=100: Clade-AHD 9.22%.
  - n=200: Clade-AHD 11.30%.
  - HiFo-Prompt with GPT-4o-mini reports 7.058% / 9.579% at n=50 / 100, but on an unspecified test set.

**Caveats:**
- **SimpleEvol.** It says the test set is "three independently generated sets of 64 instances each" (SeedSequence-based `gen_inst.py` in the repo). Its "Opt (best known)" row, however, is 5.6750 / 7.7680 / 10.6590. Those are exactly MCTS-AHD's 1,000-instance LKH means. [I] So its gaps were probably computed against another test set's optimum, which adds noise of roughly ±0.5–1 pp.
- **RefineEvo.** It reports only objective values on 64-instance sets: the RefineEvo repo generates them with seed 1234 after a 64×TSP100 training draw. It gives no optimum.
  - My [I] gaps divide by typical uniform optima: about 5.69, 7.76, 10.70, 16.52 and 23.10.
  - The Greedy row is consistent with this. 9.651 / 7.76 gives 24.4% and 6.944 / 5.69 gives 22.0%, which are normal NN gaps.
  - If the inference holds, Claude Opus 4.6 with RefineEvo (≈3.3% at n=100, ≈4.7% at n=200) would be the best result found anywhere. Its TSPLIB average is 5.45% (Table 21).
  - The Opus heuristic is not in the repo. The repo's `gpt.py` is a weaker heuristic.
- **HiFo-Prompt.** Its test-instance count is not stated. Its test-set runtime is very large: Table 1 shows 244.7 s on TSP50 versus EoH's 1.4 s, and 16,099 s on TSP200 versus EoH's 78 s.

### 1b. Excluded or not comparable (reported for completeness)

- **HMACE (2605.07214) Table 1.** The rows for FunSearch through MoH are copied from MoH's constructive table. The starred GPT-5.4 rows give HMACE* 0.000 / 0.000 / 0.014 / 0.177 / 0.809 / 1.319 (n = 20–1000, average 0.387%). Those values match MoH's *improvement* (KGLS) rows: MoH-KGLS averages 0.391%.
  - The Table 4 ablation reports "TSP-construct" HMACE Obj 5.96%.
  - [I] The starred rows are not the select_next_node task. The paper is internally inconsistent.
- **MOSAIC (2608.07544) Table 1.** Its test set mixes uniform, grid, ring and mixture layouts (200 instances per n). It reports portfolio Top-k and Oracle results. With GPT-5-nano: Top-3 6.01 / 9.06 / 12.18 and Oracle 3.15 / 5.74 / 8.81.
- **EoH-S (2508.03082) Table 2.** Gaussian-mixture instances. It evaluates a set of 10 heuristics with per-instance best: 4.0 / 6.5 / 9.0 / 11.1% at n = 50 / 100 / 200 / 500. DeepSeek-V3.
- **RouteRepair (2609.11452) Table 5.** It uses its own adapter, `score_next_node(current_node, candidate_node, unvisited_nodes, distance_matrix, tour_history)`, with deepseek-v4-flash.
  - Pure construction: 12.30 / 14.59 / 17.31 / 20.11 (n = 20–200).
  - With 2-opt: 1.17 / 2.33 / 3.34 / 4.69.
- **RedAHD (2505.20242) Table 3.** This is *not* the select_next_node interface: it writes an end-to-end route function, and its Fig. 3 shows 2-opt being used. It runs on the same MCTS-AHD 1,000-instance sets.
  - Objectives 5.767 / 8.006 / 11.164 give 1.62 / 3.06 / 4.74% [C].
- **Agentic ESOpt Table 17.** Over 20 runs, TSP50 averages 6.5007 versus EoH's 6.5517.

---

## 2. Do AHD papers compare against insertion, Christofides, greedy-edge, savings, space-filling curve or construction plus 2-opt on this task?

**Not under the standard protocol.** No paper using the uniform select_next_node test sets from AEL, ReEvo or MCTS-AHD compares against any insertion heuristic, Christofides, greedy edge, savings, space-filling curve, or construction plus 2-opt.

Their only manual baseline is nearest neighbour:
- MCTS-AHD: "The Greedy Construct baseline is the Nearest-greedy heuristic algorithm for TSP".
- AEL: "Human (Greedy)".
- MoH and HMACE: "Nearest Neighbor".
- AHD Agent: "Baseline heuristic".

Other baselines in this setting are POMO, LEHD and a genetic-programming baseline (GP in MeEvo: 11.17 / 12.63 / 13.85).

Exceptions and near-misses [V]:

1. **MCTS-AHD Table 11 (TSPLIB, 15 instances below 500 nodes).** Quote: "Christofides, Greedy, Nearest insertion, and Nearest-greedy are manually designed heuristics for TSP where their results are also drawn from (Duflo et al., 2019)."
   - Average gaps: Christofides 11.50%, Greedy 18.09%, Nearest insertion 23.11%, Nearest-greedy 25.41%, GPHH-best 16.00%, EoH 15.87%, ReEvo 13.95%, MCTS-AHD 11.10%.
   - RedAHD Table 4 reuses the same Duflo numbers and adds rl1889, u1817, d1655, d657, fl1577 and u724.
   - ReEvo Table 2 compares only to Nearest Neighbour and GHPP.
   - **Farthest insertion does not appear in any of these.** Duflo et al. 2019 (GPHH) do not report it.
2. **RouteRepair (2609.11452) Table 5** is the only AHD paper found that puts farthest insertion next to an LLM constructive TSP heuristic on random instances. Quote: "Table 5: Constructive TSP results before and after identical 2-opt postprocessing. Values are optimality gaps (%)."

   | Method | Avg | TSP20 | TSP50 | TSP100 | TSP200 |
   |---|---|---|---|---|---|
   | Nearest Neighbor | 22.5292 | 16.6312 | 23.3894 | 24.0871 | 26.0093 |
   | Cheapest Insertion | 16.2027 | 10.5209 | 16.4571 | 18.2242 | 19.6084 |
   | Farthest Insertion | 6.0049 | 2.1389 | 5.3997 | 7.2928 | 9.1883 |
   | NN + 2-opt | 3.3430 | 1.4812 | 2.8873 | 4.2526 | 4.7507 |
   | Cheapest Insertion + 2-opt | 9.0931 | 5.2145 | 8.9455 | 10.6561 | 11.5563 |
   | Farthest Insertion + 2-opt | 4.9245 | 1.5299 | 4.1329 | 6.1041 | 7.9312 |
   | RouteRepair-Constructive | 16.0760 | 12.2957 | 14.5876 | 17.3112 | 20.1095 |
   | RouteRepair-Constructive + 2-opt | 2.8805 | 1.1689 | 2.3272 | 3.3359 | 4.6899 |

   The paper says: "Farthest Insertion is the strongest conventional constructor before postprocessing." Its own pure LLM constructor loses to FI by about 10 pp, and it then turns to the +2-opt comparison.

   On TSPLIB (30 instances): RouteRepair + 2-opt 3.9244%, NN + 2-opt 4.3187%, FI + 2-opt 7.0208%.
3. **FI appears in other LLM-AHD papers, but not on the constructive task:**
   - **EoH (2401.02051) Table 10, GLS task, 1,000 instances, Concorde:** NN 17.448 / 23.230 / 25.104 and FI 2.242 / 7.263 / 12.456 (TSP20 / 50 / 100). EoH-GLS: 0.000 / 0.000 / 0.025.
     - [I] EoH's FI at TSP100 (12.46%) disagrees with Kool's 7.59% and RouteRepair's 7.29%. EoH's implementation probably differs.
   - **ASRO "Game-Theoretic Co-Evolution" (2601.22896) Table 2, GLS task, Concorde.** Uniform TSP100: NI 20.88, FI 8.54, EoH 0.27, ASRO-EoH 0.05.
   - **EvoPH (2509.24509) Table 1, TSPLIB-derived "TGB", whole-heuristic evolution, Gemini-2.5-pro.** The BASE column gives Christofides 20.64%, 2-opt 6.62%, nearest-insertion 19.54%, farthest-insertion 8.20%, nearest-neighbour 24.67% and random-insertion 9.43%. EvoPH from the FI seed reaches 4.05%.
4. **Construction plus 2-opt:** only RouteRepair, as above. Kool et al. list "Chr.f. + 2OPT", but that paper is not an AHD paper.

---

## 3. Classical constructions on uniform random TSP

### Kool, van Hoof & Welling, ICLR 2019, arXiv:1803.08475, Table 1 [V]

The test set has 10,000 instances per n. Gaps are relative to the best value: Concorde, Gurobi and LKH3 all agree. Values are objective (gap).

| Method | n=20 | n=50 | n=100 |
|---|---|---|---|
| Concorde / Gurobi / LKH3 | 3.84 (0.00%) | 5.70 (0.00%) | 7.76 (0.00%) |
| Nearest Insertion | 4.33 (12.91%) | 6.78 (19.03%) | 9.46 (21.82%) |
| Random Insertion | 4.00 (4.36%) | 6.13 (7.65%) | 8.52 (9.69%) |
| **Farthest Insertion** | **3.93 (2.36%)** | **6.01 (5.53%)** | **8.35 (7.59%)** |
| Nearest Neighbor | 4.50 (17.23%) | 7.00 (22.94%) | 9.68 (24.73%) |
| Chr.f. + 2OPT (from Vinyals) | 3.85 (0.37%) | 5.79 (1.65%) | – |
| OR Tools (from Bello) | 3.85 (0.37%) | 5.80 (1.83%) | 7.99 (2.90%) |
| AM greedy | 3.85 (0.34%) | 5.80 (1.76%) | 8.12 (4.53%) |

Appendix B.3 describes the insertion heuristics. Each node is inserted at its cheapest position. FI chooses `argmax_{i∉S} min_{j∈S} d_ij`. NN starts at the first node.

### Johnson & McGeoch 1997, "The TSP: A Case Study in Local Optimization", Table 1 [V]

Values are average % excess over the Held-Karp bound on random Euclidean instances. Source PDF: www.cs.ubc.ca/~hutter/previous-earg/EmpAlgReadingGroup/TSP-JohMcg97.pdf.

| N | 10^2 | 10^2.5 | 10^3 | 10^3.5 | 10^4 | 10^4.5 | 10^5 | 10^5.5 | 10^6 |
|---|---|---|---|---|---|---|---|---|---|
| Christofides | 9.5 | 9.9 | 9.7 | 9.8 | 9.9 | 9.8 | 9.9 | – | – |
| Savings (CW) | 9.2 | 10.7 | 11.3 | 11.8 | 11.9 | 12.0 | 12.1 | 12.1 | 12.2 |
| Greedy edge | 19.5 | 18.8 | 17.0 | 16.8 | 16.6 | 14.7 | 14.9 | 14.5 | 14.2 |
| NN | 25.6 | 26.2 | 26.0 | 25.5 | 24.3 | 24.0 | 23.6 | 23.4 | 23.3 |
| 2-Opt (Table 3) | 4.5 | 4.8 | 4.9 | 4.9 | 5.0 | 4.8 | 4.9 | 4.8 | 4.9 |
| 3-Opt (Table 3) | 2.5 | 2.5 | 3.1 | 3.0 | 3.0 | 2.9 | 3.0 | 2.9 | 3.0 |

The Held-Karp bound lies about 0.6–1.0% below the optimum. On DIMACS E1k instances the excess of the optimum over HK is 0.59–1.01% (opts.html).

### 8th DIMACS TSP Challenge raw data (Johnson & McGeoch summary chapter, 2002)

The summary-chapter PDF (archive.dimacs.rutgers.edu/Challenges/TSP/papers/stspchap.pdf) uses a font that cannot be text-extracted. Instead I **computed [C]** averages from the published raw tour lengths (`https://archive.dimacs.rutgers.edu/Challenges/TSP/<ALG>.d`) and the published HK and optimal values (`.../opts.html`).

Values are % over the optimum at E1k (10 instances) and E3k (5 instances), and % over HK for all sizes. The results page itself lists FI under "Classic Tour Construction Algorithms: < 15% above the HK Bound".

| Algorithm | E1k over OPT / over HK | E3k over OPT / over HK | E10k HK | E100k HK | E1M HK |
|---|---|---|---|---|---|
| Farthest Insertion (Bentley) | **11.72 / 12.54** | 11.68 / 12.47 | 13.35 | 13.40 | 13.47 |
| Random Insertion | 13.49 / 14.33 | 13.44 / 14.23 | 14.52 | 15.01 | 15.13 |
| Nearest Insertion | 24.94 / 25.86 | 25.63 / 26.52 | 26.50 | 27.07 | 27.00 |
| Cheapest Insertion | 21.04 / 21.93 | 21.56 / 22.42 | 21.90 | 22.04 | 22.07 |
| Savings | 10.57 / 11.38 | 10.99 / 11.77 | 11.82 | 12.14 | 12.14 |
| CCA (convex hull, cheapest insertion, angle) | 9.30 / 10.11 | 10.69 / 11.47 | 11.73 | – | – |
| Christofides, greedy shortcuts | 9.00 / 9.80 | 9.02 / 9.79 | 9.81 | 9.85 | 9.79 |
| Christofides, standard shortcuts | 13.65 / 14.48 | 13.81 / 14.61 | 14.81 | 14.69 | 14.59 |
| Greedy edge | 17.16 / 18.02 | 16.47 / 17.29 | 16.42 | 14.73 | 14.26 |
| NN (JM, average of 10 runs) | 25.03 / 25.95 | 24.89 / 25.77 | 24.34 | 23.78 | 23.28 |
| Space-filling curve | 31.28 / 32.25 | 32.47 / 33.40 | 34.56 | 34.94 | 35.09 |

### Farthest insertion across n on uniform instances

- 2.36% (n=20), 5.53% (n=50) and 7.59% (n=100) [Kool].
- 9.19% (n=200) [RouteRepair; its 2.14 / 5.40 / 7.29 at n = 20 / 50 / 100 agree with Kool].
- About 11.7% (n=1000, over the optimum) [C, DIMACS].
- n=500 has no published uniform figure. [I] It is probably about 10.5–11%.

### Comparison of the LLM-AHD leaderboard with farthest insertion

- The well-known numbers are all worse than FI at every size:
  - MCTS-AHD with GPT-4o-mini: 9.69 / 11.79 / 13.71.
  - CALM: 10.04 / 11.58 / 13.41.
  - MoH: 9.89 / 11.44 / 13.31.
  - Clade-AHD: 10.39 / 9.22 / 11.30.
  - PathWise: 8.41 / 11.85 / 12.14.
  - AHD Agent, MeEvo and AEL are also worse at every size.
- Only TIDE (4.76 / 7.15), SimpleEvol (4.77 / 6.47) and HiFo-Prompt at n=200 (8.877) edge below FI, by at most 1.1 pp. All three use per-step rollouts.
- At n=20 FI wins (2.36 vs 3.62). At n=1000 FI also wins (about 11.7 vs AEL's 12.8).
- RefineEvo with Opus 4.6 [I] would beat FI by 3–4 pp, if its objective values are taken at face value.

---

## 4. Has anyone said these results are worse than farthest insertion, or that the interface allows planning?

**Short answer: no paper found makes either point as a critique.**

The named critique and benchmark papers do not cover TSP construction:
- **Herrmann & Pallez, arXiv:2510.27353**, "An In-depth Study of LLM Contributions to the Bin Packing Problem". Bin packing only. Its simple "ab-Baselines" beat the LLM-evolved heuristics. It never mentions TSP or insertion.
- **Sim, Renau & Hart, arXiv:2501.11411**, "Beyond the Hype: Benchmarking LLM-Evolved Heuristics for Bin Packing". Bin packing only. TSP appears only in a remark about solver-benchmark sizes.
- **Zhang et al., arXiv:2407.10873**, "Understanding the Importance of Evolutionary Search in AHD with LLMs".
  - It criticises "inadequate baselines, where existing LLM-based EPS methods were primarily evaluated against random search or simple heuristics derived through human intuitions".
  - Its remedy is a (1+1)-EPS search baseline, not classical TSP constructions.
  - Its TSP task (64 TSP100 instances) follows EoH and ReEvo, which is the GLS setting. It never mentions insertion or farthest insertion.
- **HeuriGym, arXiv:2506.07972.** It excludes TSP deliberately: "we intentionally exclude ubiquitous problems such as TSP … likely memorized during pretraining". It calls the AHD frameworks' targets "toy problems under 20 lines of code (e.g., TSP, bin packing)". It does not mention FI.
- **BLADE, arXiv:2504.20183.** Continuous black-box optimisation (MA-BBOB, SBOX-COST). No TSP.
- The **survey arXiv:2509.08269** never mentions insertion or farthest insertion.

Closest related observations [V]:
- **RouteRepair (2609.11452)** is the only paper with FI next to an LLM constructive heuristic on random TSP. It concedes "Farthest Insertion is the strongest conventional constructor before postprocessing". It does not relate this to the MCTS-AHD/ReEvo leaderboard, and it uses a different scoring adapter.
- **MOSAIC (2608.07544)** comes closest on the interface point. Quote: "prompt-level complexity constraints that confine candidates to single-pass scoring rules, excluding mechanisms such as look-ahead or remaining-cost estimation". It responds by having its prompts "permit heavier per-candidate computation". This treats lookahead as a feature to exploit, not as a fairness problem.
- **SimpleEvol (2609.37172)**: "The stronger model is able to synthesize more advanced heuristic components, such as insertion-based structural reasoning, scale-normalized regret … while the weaker model tends to rely on simpler greedy rollout strategies." Again this is a feature, not a critique.
- **HMACE (2605.07214), Appendix A.6**: "On TSP, successful heuristics usually combine local edge cost with a light form of geometric lookahead."

**The interface is being exploited in practice [V]. The best heuristics run rollouts inside `select_next_node`:**
- **MCTS-AHD's released "leading heuristic"** (`problems/tsp_constructive/gpt.py`; the README says gpt.py "contains a leading heuristic function designed by MCTS-AHD"). For every candidate it builds a full nearest-neighbour completion back to the destination, then scores it as 0.7·immediate + 0.3·rollout plus a centre-distance penalty.
- **HiFo-Prompt, Appendix H.1** ("MST lookahead and cluster-aware simulation"). For a beam of candidates it computes the MST of the remaining nodes and a full greedy simulated path.
- **TIDE, Appendix F.1.** For up to 12 nearest candidates it computes the MST cost and builds a nearest-neighbour path to the destination. It then applies **2-opt until no improvement** to that path, and scores 0.8·direct + 0.1·MST + 0.6·simulated cost. In effect it re-solves the remaining tour with NN plus 2-opt at every step.
- **SimpleEvol, appendix.** The GPT-4.1-nano heuristic is a "Weighted nearest-neighbor rollout". The GPT-5-mini heuristic uses MST, insertion deltas, regret and "sampled lookahead".
- **RefineEvo.** Its evolved operator texts mention "two-step lookahead" and "depth-limited optimal path evaluation".
- **Compute cost is not normalised.** In HiFo-Prompt Table 1, the TSP200 test set takes 16,099 s versus EoH's 78 s. LKH3 takes 6,312 s.
- **RedAHD (2505.20242) shows what removing the interface does.** An end-to-end route function on the same test sets gives 1.62 / 3.06 / 4.74%. Its Table 2 notes the gap between "IC" and ACO results.

[I] No paper found says that (a) the step-by-step TSP results of ReEvo, MCTS-AHD, CALM, MoH, Clade-AHD, PathWise and others are worse than farthest insertion, or that (b) because `select_next_node` receives the whole distance matrix, "constructive" heuristics can embed full-tour planning (rollouts, 2-opt), so they are not comparable to one-pass constructions or to each other without a compute budget. Both points appear to be open.

---

## 5. Released test sets and best heuristics (GitHub API, paths verified)

### MCTS-AHD: github.com/zz1358m/MCTS-AHD-master (branch `main`)

- Data:
  - `problems/tsp_constructive/dataset/test{20,50,100,200,500,1000}_dataset.npy` holds 1,000 instances each. Example: test50 is 800,128 bytes, which is 1000×50×2 float64.
  - `train50_dataset.npy` holds 64 instances.
  - `val{20,50,100,200}_dataset.npy` hold 64 instances each.
- Generator: `problems/tsp_constructive/gen_inst.py`, using `np.random.seed(1234)` with draws in the order train50, val20–200 (64 each), then test20–1000 (1,000 each).
- Evaluators: `eval.py` and `eval-test.py`. The start node is 0, the destination is 0, and the code calls `select_next_node(..., distance_matrix=dist_mat.copy())`.
- **Best heuristic:** `problems/tsp_constructive/gpt.py`, the NN-rollout heuristic described above.
- TSPLIB files: `problems/tsp_constructive/test/tsplib/*.tsp` (15 instances) and `test/test_tsplib.py`.
- Prompts: `prompts/tsp_constructive/{func_desc,func_signature,seed_func}.txt`. Config: `cfg/problem/tsp_constructive.yaml`.
- The repo contains no LKH optimum files. The values 5.675 / 7.768 / 10.659 come from the paper.
- Clade-AHD (github.com/Mriya0306/Clade-AHD) carries an identical copy of the dataset and its own `problems/tsp_constructive/gpt.py`.

### ReEvo: github.com/ai4co/reevo (branch `main`)

- Generator: `problems/tsp_constructive/gen_inst.py`, using seed 1234, the same order as MCTS-AHD, and **64** test instances per n for n = 20, 50, 100, 200, 500, 1000. The datasets are not committed and are generated on first run.
- Evaluator: `problems/tsp_constructive/eval.py`.
- Synthetic results notebook: `problems/tsp_constructive/test/test_synthetic.ipynb`. It contains the code of `select_next_node_ReEvo`, the best ReEvo heuristic, and of the AEL heuristic. Objectives on the 64-instance test sets for n = 20 / 50 / 100 / 200 / 500 / 1000:
  - NN: 4.4466 / 6.8919 / 9.6508 / 13.4248 / 20.6527 / 29.1780.
  - AEL: 4.0787 / 6.2331 / 8.6010 / 12.3072 / 19.2370 / 27.3443.
  - ReEvo: 4.0906 / 6.2269 / 8.5676 / 12.0927 / 18.9482 / 26.7917.
  - No optima are given.
- TSPLIB: `problems/tsp_constructive/test/tsplib/` (21 instances) and `test_tsplib.py`.
- Prompts: `prompts/tsp_constructive/`. Baseline prompts: `baselines/ael/prompts/tsp_constructive/`.

### EoH: github.com/FeiLiu36/EoH (branch `main`)

- Example: `examples/tsp_construct/`. It contains `prob.py`, `runEoH.py` (DeepSeek, problem_size=50, n_instance=8), `get_instance.py` (seed 2024), and `evaluation/{evaluation.py, heuristic.py, runEval.py}`.
- `evaluation/heuristic.py` is the AEL heuristic, labelled "example heuristic".
- Test data: `examples/tsp_construct/testingdata/instance_data_{10,20,50,100,200}.pkl`. `runEval.py` uses n_test_ins=64 for sizes 20 / 50 / 100.
- `examples/tsp_construct/results.txt` reports "Average dis on 100 instance" of 4.558 / 7.014 / 9.811 for n = 20 / 50 / 100.
- `examples/tsp_construct_class/results/pops_best/population_generation_*.json` holds an EoH run's best heuristics per generation.

### LLM4AD: github.com/Optima-CityU/LLM4AD (branch `main`)

- Task: `llm4ad/task/optimization/tsp_construct/`, containing `evaluation.py` (defaults n_instance=16, problem_size=50, timeout 30 s), `get_instance.py` (seed 2024, generated on the fly), `template.py` and `paras.yaml` (timeout_seconds: 20).
- Examples: `example/tasks/tsp_construct/run_eoh.py` and `run_partevo.py`.
- There is no fixed test set and no stored best heuristic.

### Other repos with TSP-construct artifacts

- **HiFo-Prompt**, github.com/Challenger-XJTU/HiFo-Prompt: `examples/tsp_construct/evaluation/heuristic.py` (4,544 bytes; the best heuristic) and `examples/tsp_construct/evaluation/results/pops_best/*.json`. Its test data is EoH's pkl files, and its `runEval.py` uses n_test_ins=100.
- **SimpleEvol**, github.com/HenryZhu1029/SimpleEvol-Master: `problems/tsp_constructive/{gen_inst.py, eval.py, eval-test.py, tsplib/test_tsplib.py}`. `gen_inst.py` uses SeedSequence([1234, split, n]) with 64 instances.
- **RefineEvo**, github.com/samwu-learn/RefineEvo: `problems/tsp_constructive/{gen_inst.py, gpt.py, test.py, test_tsplib.py}`. The data uses seed 1234 with train TSP100×64 drawn first, then 64 per n.
- **MeEvo**, github.com/Qzs1335/MeEvo: `evaluators/tsp_construct/dataset/test{20..1000}_dataset.npy` (64 each), plus `gen_reference.py` and `gpt.py`.
- **PathWise**, github.com/oguzhangungordu/PathWise: `problems/tsp_constructive/eval.py`.
- **Agentic ESOpt**, github.com/zz1358m/Agentic-ESOpt: per-run best code at `ahd-test-time/results/{EoH,EoH+AgenticESOpt,Sample+AgenticESOpt}{1000,2000}/TSP_construct/*_final_best_code.py`.
- Repos listed in the papers but with no TSP-construct files found by the tree search: CALM (github.com/whxru/CALM, branch master) and AHD-Agent (github.com/Antoniano1963/AHD-Agent).
- No repository link was found in the HTML for TIDE, MoH or HMACE.

---

## Source index (arXiv IDs read)

- 2311.15249 AEL
- 2401.02051 EoH
- 2402.01145 ReEvo
- 2412.14995 HSEvo (GLS only)
- 2412.17287 LLM4AD (normalised scores only)
- 2501.08603 MCTS-AHD
- 2504.05108 EvoTune (GLS only)
- 2505.12285 CALM
- 2505.20242 RedAHD
- 2505.20881 MoH
- 2506.07972 HeuriGym
- 2507.20541 MeLA (ACO)
- 2508.03082 EoH-S
- 2508.13333 HiFo-Prompt
- 2509.24509 EvoPH
- 2512.03762 RoCo (ACO)
- 2512.08609 CogMCTS (TSP via GLS only; step-by-step only for KP)
- 2601.20539 PathWise
- 2601.20868 DASH (GLS)
- 2601.21239 TIDE
- 2601.22896 ASRO
- 2602.00549 Clade-AHD
- 2602.08253 G-LNS (LNS)
- 2602.13769 OR-Agent (normalised scores only: TSP-Constructive 0.959)
- 2602.16038 LaGO (TSPLIB)
- 2604.24043 A2DEPT (TSP only for N ≤ 25 vs OPRO)
- 2605.06123 Back to the Beginning (constructive TSP reported only relative to the best method)
- 2605.07214 HMACE
- 2605.08756 AHD Agent
- 2606.14202 MeEvo
- 2606.31801 RAISE (no TSP)
- 2607.11358 RefineEvo
- 2608.00700 DGA2D (TSPLIB solvers)
- 2608.03636 MuEvo (ACO)
- 2608.07544 MOSAIC
- 2608.17310 Agentic ESOpt
- 2609.11452 RouteRepair (PDF)
- 2609.37172 SimpleEvol
- 2407.10873, 2501.11411, 2510.27353 (critiques), 2509.08269 (survey)
- 1803.08475 Kool et al.
- Johnson & McGeoch 1997, and the DIMACS raw data
