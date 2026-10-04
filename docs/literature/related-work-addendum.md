# Related work, addendum: papers on the open questions

Written late on 3 October 2026, after the overnight experiments. The main review is
[related-work.md](related-work.md). This addendum searched arXiv for the five questions the
experiments left open. It is based on **abstracts only**: no full texts were read, so treat every
claim below as the abstract's own claim. Papers already in the main review are marked *(in
review)*.

Search method: 15 arXiv API queries (about 6–8 results each), on 3 October 2026. The queries
covered:
- LLM heuristic design for online bin packing;
- LLM versus classical tuning;
- Sum-of-Squares;
- interpreting evolved heuristics;
- counterexample and reflection feedback;
- self-repair;
- research-idea prediction;
- routing for code;
- surrogates and evaluation cost;
- evaluations of AlphaEvolve-style frameworks.

## 1. Can an LLM loop beat a cheap, classically tuned baseline?

Our finding (bp-ceiling-v1): on Weibull 5k, a 21-weight linear rule tuned by CMA-ES matches
FunSearch's evolved code.

| Paper | What the abstract says | What it means for us |
|---|---|---|
| van Stein, Vermetten & Bäck 2024, *LLaMEA-HPO* ([2410.16309](https://arxiv.org/abs/2410.16309)) | Offloading hyper-parameter tuning of generated algorithms to an HPO procedure in the loop gives comparable or better results with fewer LLM queries, including on online bin packing. "Separating algorithmic innovation … from parameter tuning" matters. | The closest prior work to our result. They tune the LLM's constants with a classical optimiser; we show that on this family, with the right features, the classical tuner alone reaches FunSearch's level. Cite it, and phrase our claim as the extreme case of their point. |
| Chen et al. 2026, *TIDE* ([2601.21239](https://arxiv.org/abs/2601.21239)) | Treating evolution as monolithic text generation ignores the coupling of structure and constants; promising algorithms are discarded because of uncalibrated constants. An inner differential-mutation loop tunes parameters. | Same theme. Evolved programs may lose to tuned simple rules partly because their constants are untuned. |
| Liu et al. 2024, *EoH* ([2401.02051](https://arxiv.org/abs/2401.02051)); Ye et al. 2024, *ReEvo* ([2402.01145](https://arxiv.org/abs/2402.01145)); Zheng et al. 2025, *MCTS-AHD* ([2501.08603](https://arxiv.org/abs/2501.08603)) | Standard LLM heuristic-design frameworks. EoH reports beating handcrafted heuristics on online bin packing at a low query budget. | The baselines our CPU-tuned rule should be compared against, on their published bin-packing settings. |
| Csirik, Johnson, Kenyon et al., *Sum-of-Squares* ([cs/0210013](https://arxiv.org/abs/cs/0210013), [cs/0509031](https://arxiv.org/abs/cs/0509031)) | A classic online bin-packing rule, with worst-case analysis. | It scores a placement using the counts of open bins at each gap size: global state our per-bin features cannot express. A natural next feature, or a target for an LLM to rediscover. |
| Herrmann & Pallez 2025 ([2510.27353](https://arxiv.org/abs/2510.27353)) *(in review)* | LLM heuristics on these instances stay opaque. Simpler hand-derived algorithms are more efficient and generalise better, which suggests the instances are simple. | Matches our result from the other direction. |

## 2. What do FunSearch-level rules actually do?

| Paper | What the abstract says | What it means for us |
|---|---|---|
| Zhang & Lu 2026, *BehaveSim* ([2603.02787](https://arxiv.org/abs/2603.02787)) | Code similarity metrics miss algorithmic similarity. BehaveSim compares problem-solving trajectories with dynamic time warping and clusters generated algorithms by behaviour. | A ready method to test whether our 21-weight rule, FunSearch's heuristic and the two-threshold rule are the same algorithm. memory-ablation already measured decision agreement, with a maximum of 0.782 against FunSearch. |
| van Stein, Kononova & Kotthoff 2026, *LLaMEA-SAGE* ([2601.21511](https://arxiv.org/abs/2601.21511)) | A surrogate over AST features of evaluated programs, plus explainable-AI attribution, turns the features that drive performance into natural-language mutation instructions. | Related to Simplify's ablations, but used to guide search instead of explaining the result. |

## 3. Does failure feedback help, and in what form?

Our finding (memory-ablation-v1): raw short counterexamples did not improve the audited final
policy, and made the model propose no-ops.

| Paper | What the abstract says | What it means for us |
|---|---|---|
| Karimi et al. 2025 ([2510.08755](https://arxiv.org/abs/2510.08755)) *(in review)* | Exposing the LLM to instances where a heuristic underperforms, explaining why, and specialising by input region gives about 28× better worst-case performance than FunSearch. | The positive counterpart to our null. They explain failures; we pasted raw instances. |
| Gungordu, Xiong & Fekri 2026, *MOSAIC* ([2608.07544](https://arxiv.org/abs/2608.07544)) | Scalar better/worse feedback tells the LLM whether a heuristic improved, but not where in the instance space or why. MOSAIC co-evolves instances and specialist heuristics in a quality-diversity archive. Decision trees find the regions where each heuristic wins, and a reflection model writes persistent insights. | A concrete design for the next Falsify memory: region-level "where and why", not single inputs. It also answers our 2-item counterexample problem. |
| Olausson et al. 2023, *Is self-repair a silver bullet?* ([2306.09896](https://arxiv.org/abs/2306.09896)) | Once the cost of repair is counted, self-repair gains are often modest, vary a lot between subsets, and are sometimes absent. | The same lesson as our matched-cost null: feedback loops must be judged at equal cost. |
| Ye et al. 2024, *ReEvo* ([2402.01145](https://arxiv.org/abs/2402.01145)) | LLM reflections act as "verbal gradients" inside evolutionary search. | The usual form of failure memory, and a baseline to compare against. |

## 4. Can idea ranking work, especially when the task is hard?

Our finding (idea-table-v1): prompted rankers were near chance, ranked triage did not beat random
tiers, and the implementing model decided success.

| Paper | What the abstract says | What it means for us |
|---|---|---|
| Zhang 2026, *Budgeted Subset Refinement* ([2607.14118](https://arxiv.org/abs/2607.14118)) | Given a noisy pool of LLM ideas, generation plus reranking alone produced no research-strong ideas. Random-k refinement is a strong low-cost baseline, and diversity-aware MMR-k selection gives the best trade-off. | Echoes our null: random is hard to beat. Selecting for diversity, rather than ranking by promise, is the alternative to test. |
| Wang, Peng & Wu 2026, *Dual-surrogate guided search* ([2607.13911](https://arxiv.org/abs/2607.13911)) | Under limited query and evaluation budgets, a surrogate trained on the archive chooses which parent and operator to use before each LLM call. | An outcome-trained predictor instead of a prompted ranker. Our idea table is exactly the training and test data such a predictor needs. |
| Si, Hashimoto & Yang 2025 ([2506.20803](https://arxiv.org/abs/2506.20803)) *(in review)* | Ideas judged promising before execution do not hold up after execution. | The ideation–execution gap behind our triage result. |

## 5. When evaluation, not the model, is the cost

Our observation (tournament-v2 smoke runs): with an open model, a call took 18–36 s and cost
about $0.002, while one program evaluation took up to 665 s.

| Paper | What the abstract says | What it means for us |
|---|---|---|
| Tanveer 2026, *LEVI* ([2605.09764](https://arxiv.org/abs/2605.09764)) *(in review)* | Full-set evaluation wastes rollouts on redundant examples. Stronger search architecture can substitute for larger models. | Supports evaluating on fewer, chosen instances. |
| Yin et al. 2026, *Landscape-aware AAD* ([2602.04529](https://arxiv.org/abs/2602.04529)) | Existing methods need extensive evaluation of the target problem. Discovery is decoupled from costly evaluation using proxy functions matched to the target's landscape. | One route when evaluation is the bottleneck. |
| Ahmed, Mostajabdaveh & Zhou 2026, *Latent Heuristic Search* ([2605.17137](https://arxiv.org/abs/2605.17137)); Hao et al. 2024, *LLMs as surrogate models* ([2406.10675](https://arxiv.org/abs/2406.10675)) | A learned surrogate predicts performance so that search avoids evaluating every candidate. | The literature mostly counts LLM queries. Reporting wall-clock and CPU next to tokens, as our logs allow, is a cheap way to make "research efficiency" honest. |

## Other recent framework papers found

- Gupta et al. 2026, *Automated Discovery Has No Universally Superior Harness*
  ([2607.18235](https://arxiv.org/abs/2607.18235)) *(in review)*.
- Assumpção et al. 2025, *CodeEvolve* ([2510.14150](https://arxiv.org/abs/2510.14150)): an open-source
  evolutionary coding agent.
- Yu et al. 2025, *SATLUTION* ([2509.07367](https://arxiv.org/abs/2509.07367)): repository-scale code
  evolution for SAT solvers.
- Lu et al. 2026 ([2609.38757](https://arxiv.org/abs/2609.38757)): in-context evolution stagnates;
  proposes parametric self-evolution.
- Gungordu, Xiong & Fekri 2026, *PathWise* ([2601.20539](https://arxiv.org/abs/2601.20539)): a planning
  agent over a graph memory of the search.
- Liu et al. 2026, *RAISE* ([2606.31801](https://arxiv.org/abs/2606.31801)) *(in review)*.

## What this changes in how we describe our work

1. **"A cheap formula matches FunSearch"** should be framed as the extreme case of a known trend:
   separating structure from parameter tuning (LLaMEA-HPO, TIDE). Our addition is that on this
   instance family one extra feature plus classical tuning suffices, with no LLM at all.
2. **The memory null** contrasts with Karimi et al. and MOSAIC. Their failure feedback explains
   where and why; ours was raw 2-item inputs. The null is about that form of memory, not about
   failure feedback in general.
3. **The triage null** matches Budgeted Subset Refinement (random is a strong baseline). The
   promising alternatives are outcome-trained surrogates and diversity-aware selection, not better
   prompts for rankers.
