# Novelty and significance check: Sum-of-Squares against FunSearch bin packing (4 October 2026)

These are a search agent's working notes, copied unchanged apart from this header (05:45–06:05 BST).
The downloaded PDFs and text extracts it mentions were kept out of the repository because of
licensing.

**Verdict.** No source compares Sum-of-Squares, or any distribution-aware online algorithm, with
FunSearch or with LLM-evolved bin-packing heuristics. One lead is unverified: a GitHub repository
that now returns 404. No source shows OPT = L1 on FunSearch's Weibull instances.

**Not checked.** OpenReview reviews could not be read: the site returned a challenge page.

Everything below marked OPENED was downloaded/fetched and read (text extracts in `txt/`, PDFs in `pdf/`).
Items marked NOT OPENED are leads only, not confirmed.

## A. Has anyone compared SS / SS variants / Gupta-Radovanovic / distribution-aware online BPP algorithms against FunSearch or LLM-evolved heuristics?

Verdict: NOT FOUND (no confirmed source runs SS or any distribution-aware online algorithm against FunSearch/LLM-evolved heuristics).

Closest confirmed items:

1. Herrmann & Pallez, "An In-depth Study of LLM Contributions to the Bin Packing Problem", arXiv 2510.27353 v2 (17 Jun 2026); published ACM TELO, doi 10.1145/3821574 (Crossref: 18 Jun 2026). OPENED.
   - Distil FunSearch c12/c14 and EoH into a 2-parameter "ab-Baselines" family (ab-FirstFit/ab-BestFit/ab-WorstFit). These are ordinary priority functions (fit within FunSearch's interface).
   - Weibull(3,45), 5000 items: ab-WorstFit (a=1,b=21) beats c14 by 0.12% and EoH by 0.15% (and BestFit by 3.39%) on average over 1000 instances. Results are relative to BestFit, not to L1/optimum.
   - Related work: they state they know of no prior research on stochastic online BPP with uniform lower bound a>0 or with non-uniform distributions such as Weibull; they also concede relevant work may have escaped their review. They cite Ayyadevara et al. 2025 (stochastic online BPP) but never mention Sum-of-Squares (0 hits for "sum of squares", "Csirik", "Gupta").
   - => The SS result directly answers the "missing related work" gap H&P point to; SS (Csirik et al. 2006) has guarantees for arbitrary discrete distributions.
2. Sim, Renau & Hart, "Beyond the Hype: Benchmarking LLM-Evolved Heuristics for Bin Packing", arXiv 2501.11411 (EvoApplications 2025, LNCS). OPENED.
   - 5 LLM heuristics (FS1, FS2, FSW, EoC, EoH) vs NF, FF, BF, WF, AWF on 6,064 instances / 12 datasets; metric "average excess bins" over sum/C (continuous bound). No SS, no Harmonic, no exact optima.
3. MetaMuse (Ma et al., ICLR 2026), arXiv 2510.03851. OPENED. Online BPP baselines include NF, WF, AWF, FF, BF, Harmonic-k, Refined First Fit on Weibull(3,45), Falkenauer-U, Scholl-1, Gaussian traces. Stronger classical (worst-case) baselines, but no SS.
4. Ernest Davis, "Comment on (Romera-Paredes et al., 2023)" (11 Jan 2024) and companion review (7 Jan 2024), cs.nyu.edu/~davise/papers/FunSearchComment.pdf and FunSearch.pdf. OPENED. Bin-packing section: describes FF/BF as standard and explicitly says he could not determine whether FF/BF are state of the art. No SS, no optimum analysis.
5. FunSearch itself (Nature 2024) main text + SI + GitHub notebook. OPENED.
   - Main text: notes that online BPP variants with strong worst-case guarantees exist (cites Lee&Lee Harmonic, Ramanan et al., Seiden, the Coffman-Csirik-Galambos-Martello-Vigo survey chapter) but says they perform poorly in practice and that FF/BF are most commonly used. Also notes "Augmenting the heuristics with memory of previously seen items can even lead to heuristics outperforming best fit" (hyper-heuristic ref).
   - Main text says excess is measured over the L2 lower bound (Martello-Toth); the released bin_packing.ipynb says the lower bound is computed with the L1 bound. Weibull 100k: "only 0.03% off the lower bound on the optimum".
   - SI A.3: 10 runs, Weibull 10k excess 0.44% +/- 0.11% vs FF 4.20%, BF 3.90%; "first fit and best fit" called the two standard ones in the literature. SI contains no "sum of squares", "Csirik", "Harmonic".
   - SI E.4: Weibull parameters "based on standard values in the literature [33]" where [33] = Angelopoulos, Kamali, Shadkami, "Online bin packing with predictions" (arXiv 2102.03311).
   - google-deepmind/funsearch issues (11 total): none about SS or optima.
6. Angelopoulos, Kamali & Shadkami, "Online Bin Packing with Predictions", arXiv 2102.03311 (IJCAI 2022 / JAIR 2023). OPENED.
   - This is FunSearch's cited source for the Weibull setting. Its related work explicitly discusses SS (Csirik et al. 2006a, expected loss O(sqrt n)), Gupta & Radovanovic 2020 (same guarantee, decisions depend only on item size and bin levels), and Banerjee & Freund (O(1) loss when n and the distribution are known). Its own algorithm (ProfilePacking) is frequency-prediction based, i.e. distribution-aware. So the SS literature was one citation hop from FunSearch's benchmark. No empirical SS comparison there (1 mention).
7. Crucible Loop GitHub repo (github.com/arnoldcastro5000/crucible-loop). NOT OPENED: repo returns 404 (API, raw, web); only search-engine snippets claim an LLM-as-mutation loop on online BPP (sizes 1-100, capacity 100) whose "archived champion" is the SS algorithm. Treat as unverified; worth a manual check (may have been deleted/privatised; owner's other repos are unrelated).
8. jorsacademy/llm-guided-heuristic-discovery-bin-packing (GitHub). NOT OPENED (404).

Other checks (all negative for SS):
- arXiv full texts grepped for "sum of squares"/"Csirik"/"Gupta": EoH 2401.02051, ReEvo 2402.01145, Understanding-evo-search 2407.10873, MEoH 2409.16867, LLaMEA-HPO 2410.16309, HSEvo 2412.14995, LLM4AD 2412.17287, QUBE 2412.20694, MCTS-AHD 2501.08603, Böther et al. 2503.03350, EvoTune 2504.05108, CALM 2505.12285, RedAHD 2505.20242, MoH 2505.20881, EoH-S 2508.03082, X-evolve 2508.07932, HiFo-Prompt 2508.13333, MetaMuse 2510.03851, GigaEvo 2511.17592, irace-evo 2511.14794, DRAGON 2601.06502, Art-of-Being-Difficult 2601.16849, PathWise 2601.20539, TIDE 2601.21239, ASRO 2601.22896, OR-Agent 2602.13769, CCTS 2602.03132, ReVEL 2604.04940, AST operator 2604.16420, HMACE 2605.07214, Latent Heuristic Search 2605.17137, RAISE 2606.31801, AI Finds A Way 2608.23875, Dynamic instance clustering 2608.03129, T-GADE 2609.12286. Zero SS mentions in all. (RedAHD/Agentic Researcher/ScientistOne/SeaEvo/LEVI "sum of squares" hits are unrelated uses.)
- Google Scholar (fetched): "Csirik"+"FunSearch" -> 4 hits (FunSearch itself, Zhang-Liu-Bai ESWA 2026 risk-aware pattern adjustment, TIDE, Quan et al. 3D packing); the Csirik hits are the handbook survey, not SS (checked TIDE text; OpenAlex refs of ESWA paper do not include SS JACM 2006). "sum-of-squares algorithm"+"large language models"+"bin packing" -> 0 hits. "sum-of-squares"+"bin packing"+"FunSearch" (2024+) -> 5 hits, all unrelated uses.
- OpenAlex citers of Csirik et al. JACM 2006 (W1992365301), 2023-2026: 6 works (Ayyadevara et al. TALG 2025; Green Bin Packing 2026; Banerjee & Freund MS 2024; Hong-Xie-Wang 2023; Tan et al. SSRN 2024; Kevin Sim's Napier thesis record with year 2026, abstract is GP hyper-heuristics, no LLM). Semantic Scholar citers (STOC 2000 record, 80 cites) since 2023: Good Prophets, Power of Migrations, Hong et al., Online Bin Covering with Frequency Predictions, Green Bin Packing. None LLM-related.
- Huayan Zhang PhD thesis (Nottingham 2024, OPENED): discusses SS and Gupta in background, Weibull experiments, no FunSearch.
- Hacker News FunSearch thread (Algolia API, item 38643076): bin-packing comments are about LLM-as-mutator; no SS.
- Gary Marcus substack (Dec 2023): no bin-packing specifics.
- GitHub code search (gh): no SS bin-packing code in LLM/FunSearch contexts.
- OpenReview reviews: COULD NOT CHECK. api2.openreview.net and openreview.net return a "Challenge verification required" page; Chrome extension not connected. (EoH ICML 2024 forum BwAkaxqiLB; ReEvo NeurIPS 2024 483IPG0HWL; MCTS-AHD ICML 2025 Do1OdZzYHr; MoH ICLR 2026 tIQZ7pVN6S.) Manual check recommended.

## B. How widely is FunSearch's online BPP benchmark used (2024-2026)?

Verdict: very widely; it is the default online-BPP task of the LLM automatic-heuristic-design (AHD) literature.

Confirmed (opened) papers using FunSearch/EoH Weibull online BPP (Weibull(45,3) items, C=100 5k, and EoH/MoH's extended C in {100..500} x n in {1k,5k,10k}) as a benchmark: ~27, e.g.
- EoH (ICML 2024 oral): beats FunSearch with far fewer LLM queries; "significantly outperforms" hand-crafted baselines.
- HSEvo (AAAI 2025), MEoH (2409.16867), LLaMEA-HPO (2410.16309): 5 Weibull 5k instances, claims SOTA/convergence.
- MCTS-AHD (ICML 2025): Table 3, gaps to lower bound; its "FunSearch" (GPT-4o-mini rerun) 1.30% at 5k/C100, MCTS-AHD 1.06%.
- MoH (ICLR 2026): Table 2, 15 settings, avg 0.453%.
- MetaMuse (ICLR 2026): up to 30.93% less bin usage than human heuristics.
- PathWise (ICML 2026), TIDE, ASRO, ReVEL ("reduce up to 20 bins"), RAISE (OOD distributions), HMACE (0.441%), Latent Heuristic Search, AST operator, T-GADE, EvoTune (online BP as one of 3 tasks), LLM4AD platform (OBP task), QUBE, X-evolve (re-runs exact FunSearch protocol OR1-4 + Weibull 5k/10k/100k), DRAGON, RedAHD, CALM, EoH-S, HiFo-Prompt, Dynamic Instance Clustering (2608.03129).
- arXiv API abstract search: 39 abstracts 2024-2026 mention bin packing + LLM (about half are AHD papers); many AHD papers mention BPP only in the body, so true count is higher (estimate 40+).
- FunSearch citations: Herrmann & Pallez report 1,498 Google Scholar citations at 10 Jun 2026; Google Scholar page fetched today shows 2,187.
- Nearly all compare only to FF/BF + other LLM methods; metric = excess over ceil(sum/C) (often mislabeled L2 or even "optimal": TIDE says optimal BPP results are "taken from MCTS-AHD", which are lower-bound gaps).

## C. Has anyone shown OPT = L1 on FunSearch's Weibull instances, or computed exact optima?

Verdict: NOT FOUND.
- FunSearch calls the bound a lower bound "generally not achievable in the online setting"; notebook uses L1; paper text says L2.
- DRAGON (2601.06502): on Weibull-5K, OR-Tools MP and CP-SAT "failed to produce feasible solutions before timeouts"; its offline agent gets 0.33% gap to L2 (FunSearch 0.69%, EoH 0.66%). So no exact optima there.
- HMACE uses "FunSearch L2 lower bounds as oracle references"; MoH uses ceil(sum/c) (attributed to Martello & Toth); Sim et al. use sum/C.
- Background (not FunSearch-specific): OR-Library binpack1-4 optima are long known; random 1D BPP instances typically have OPT at or near L1/L2 (IRUP-type behaviour). So (1) is a useful certification, probably unsurprising to BPP specialists.

## D. Do MoH / HMACE report the quoted numbers?

Verdict: FOUND, numbers match.
- MoH (Shi et al., ICLR 2026, arXiv 2505.20881) Table 2 "Results on Online BPP": capacities 100,200,300,400,500 x sizes 1k,5k,10k (15 settings); 100 Weibull instances per size; best of 3 runs; lb = ceil(sum w_i / c). Average row: BF 1.607, FF 1.729, FunSearch 0.825, EoH 0.680, ReEvo 1.240, HSEvo 1.125, MCTS-AHD 1.006, MoH 0.453 (%).
- HMACE (Yan et al., arXiv 2605.07214, preprint) Table 2: copies MoH's 8 columns verbatim and adds GPT-5.4 runs EoH* 0.664, CORAL* 0.755, HMACE* 0.441 (%). Text: HMACE* best starred method, beats MoH in 12 of 15 settings. => "best published LLM method 0.441%" = HMACE*.
- Caveats: MoH's FunSearch column is a rerun (2.165% at C100/5k) not the Nature heuristic (0.68% at 5k); numbers are best-of-3 on authors' own instance draws (MoH code: github.com/yiding-s/MoH); HMACE is not peer reviewed (as far as seen).

## Significance assessment (my judgement)

Who cares: (i) the LLM-AHD community, whose most-used online-BPP leaderboard has no strong classical baseline; (ii) critics (Davis; Sim et al.; Herrmann & Pallez in ACM TELO) — this strengthens their case with a theory-backed algorithm they did not find; (iii) online-algorithms people (SS rarely benchmarked on Weibull).

Strongest framing: "the missing baseline and the tight bound". (a) OPT = L1 almost always, so the leaderboard metric is pure online waste; (b) a 2006, parameter-free, distribution-oblivious algorithm with known guarantees for discrete distributions matches/beats two years of LLM-evolved heuristics, including FunSearch's own released heuristic on its own released test data; (c) the reason is structural: the stateless priority(item, visible bins) interface cannot represent SS (restricted to visible bins it collapses to best fit), so the search space excluded the right algorithm class; (d) horizon knowledge (Banerjee-Freund style) gives a further ~3.5x reduction.

Likely reviewer objections:
1. SS uses global state (bin-level histogram incl. bins the item does not fit) that the interface withheld -> "unfair". Turn it into the point: the interface, not the LLM, is the bottleneck; show an LLM given SS-capable state.
2. "FunSearch aimed at discovery, not SOTA; it only claimed to beat FF/BF." Counter: subsequent papers treat the benchmark as SOTA leaderboard; Nature framed "new algorithms".
3. Different instances / best-of-3 / copied baselines: only Weibull 5k test data was released; 10k/100k and MoH/HMACE settings are regenerated. Need same-instance runs, many seeds, CIs.
4. Small effect: 0.483 vs 0.684% is ~3-4 bins on ~2,000; and H&P already beat c14 by 0.12% inside the interface. Need SS vs ab-WorstFit head-to-head.
5. Known-horizon variant uses extra information (n); theory (Banerjee & Freund) already predicts O(1) loss, so not novel per se.
6. OPT = L1 is expected for random instances (bounded-waste regime); OR-Library optima already known.
7. SS has worse worst-case/linear-waste behaviour (competitive ratio >= 2; SS variants needed for linear-waste distributions) -> test on Sim et al.'s 12-dataset suite for robustness.
