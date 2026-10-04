# Research-directions session log, 4 October 2026

The log of one Claude Code session that followed up the hackathon with new research. The user asked:

1. "look through the repo and ssm-paper-sources … think about what areas we could go deeper into to
   make actual new findings … look up papers within the suggested area";
2. "shall we continue with the most promising directions?";
3. "yes you can [commit], make sure to document everything also. the most promising ones".

PR #8 moved the files this log first wrote under `context/`: the review and the novelty check to
`docs/literature/`, this log to `docs/logs/`. Paths below are the current ones.

Times are BST and come from `date` or file modification times; "≈" marks an estimate. Each
study's own `RUN_LOG.md` is the authority for its details.

## What came out of it

| Study | Branch, folder | Result | Spend |
|---|---|---|---|
| Research-directions review | `docs/research-directions`, `docs/literature/research-directions.md` | Six candidate directions, each with a literature verdict. Classical online algorithms against FunSearch: not done anywhere. | $0 |
| online-frontier-v1 | `exp/online-frontier`, `experiments/online-frontier-v1/` | On FunSearch's Weibull benchmark OPT = L1 on 129 of 130 instances. Sum-of-Squares (2006) is 10–11 bins above OPT and FunSearch's heuristic 13–14, at 5k–100k items; SS − FS-W = −2.65 [−3.07, −2.24] bins per instance on 100 fresh 5k instances. FunSearch's stateless interface cannot express SS. FS-OR beats SS on OR1–OR4. | $0 (CPU) |
| overfit-gates-v1 | `exp/overfit-gates`, `experiments/overfit-gates-v1/` | Selection overfitting was small (0.61 bins per promotion). Strict, random and soft vetoes all blocked the best run, cutting the final advantage from 2.28 to about 0.3–0.4 bins per instance. 554 of 635 archived counterexamples are 2 items long. Ladder and sign-test gates changed nothing; Thresholdout accepted no-ops. | $0 (CPU) |
| online-beyond-ss-v1 (session b1, coordinated with this one) | `exp/online-beyond-ss`, `experiments/online-beyond-ss-v1/` | Known-horizon FWSS (size-weighted SS plus a best-fit finish) is 1.6–2.1 bins above OPT at 1k–100k items. Without the horizon the weights are worse than plain SS. On the 15 MoH/HMACE leaderboard settings, plain SS averages 0.444% against 0.441% for the best published LLM method. b1's numbers, not re-checked here. | $0 (CPU) |
| llm-from-ss-v1 | `exp/llm-from-ss`, `experiments/llm-from-ss-v1/` (not pushed) | **Yes.** On 100 fresh 5k instances, all with proved OPT, all 4 runs beat SS (10.68 bins above OPT). Run s3 weights N(g)² by (100/g)^0.8 and gets 8.37: −2.31 [−2.58, −2.04], 92/6/2, the best horizon-free rule found. The other three runs flipped SS's tie-break and get 10.20, −0.48 [−0.74, −0.22]. No run used the item count. On the same instances FWSS gets 1.83 and FunSearch 13.52. Level-weighted SS is a known family (Csirik et al. §8.1), whose examples weight the other way. | $1.0994 HF |
| short-horizon-v1 | `exp/short-horizon`, `experiments/short-horizon-v1/` (not pushed) | **Yes.** On 100 fresh 5k instances, Δ vs best fit in pp:

- selection on 5k streams −2.61; on 200-item streams −0.33; on 80-item streams −0.15;
- 5k streams plus a gate of short mined counterexamples −0.58; plus short random streams −0.09.

B−A = +2.28 [+1.19, +3.03] and C−A = +2.46 [+1.40, +3.18], with complete separation (exact permutation p = 0.029 each; Holm p = 0.057, the floor with 4 runs per arm). D vs E −0.49 (p = 0.63): the short length removes the gain, not the counterexamples' content. Mechanism: placements that open a new bin while one fits are 0.169 under A against 0.020 (B) and 0.014 (C). | $1.84 HF |

Related, from another session: llm-long-search-v1 (merged to `main` in PR #5) ran 4 × 300 steps of
the loop from best fit for $0.80. The best rules reached 96.8% of FunSearch's gain, and SS beat all
of them.

## Timeline

| Time | Event |
|---|---|
| ≈ 01:10–01:30 | Read the repo, the three paper drafts with their ledgers, and each study's next steps. Six literature-check agents ran in parallel, one per candidate direction. An exploratory CPU probe of SS against FunSearch on FunSearch's released data and fresh instances: SS 0.483% against FunSearch 0.684% over L1 on the released Weibull 5k data; SS loses on OR3. |
| 01:34 | Wrote `docs/literature/research-directions.md` and the probe, uncommitted, on `docs/research-directions`. |
| ≈ 01:45 | The user asked to continue with the most promising directions. Chose the two that need no API spend: (1) classical algorithms against FunSearch, run here; (2) overfitting and promotion gates, run by a subagent on `exp/overfit-gates`. |
| 01:48 | The overfit-gates protocol was hashed before any scoring. |
| 01:48:57 | The online-frontier-v1 protocol was hashed. Its stated time was corrected from 01:50 to 01:48 and it was rehashed at 01:49:02, before any confirmatory code ran. |
| ≈ 01:55 | Session b1 asked to coordinate. Agreed lanes: b1 takes ProfilePacking, LP re-solving, weighted SS and the other AHD papers' settings, on `exp/online-beyond-ss`. Seeds: this session 81000–83999 (and the probe's 50000–53003, 60000–62001); b1 90000–99999. This session sent b1 the observation that its FWSS finish needs the horizon T; b1 relabelled FWSS as known-horizon before its test run. |
| 02:01 | Load average 55 on 10 cores, caused by two concurrent `llm-long-search-v1` audits (2 × 8 workers, another session). The timed search loops had already finished, so only wall time was affected. Our jobs kept to 1–2 processes. |
| ≈ 02:17 | online-frontier pre-run checks passed. The compact evaluator equals the full one (75/75). Arc-flow OPT equals OR-Library's listed value on 76/80; on the other 4 it is one bin lower, with verified packings that meet L1. This is a known correction, not a new result. |
| 02:19–02:30 | online-frontier-v1 confirmatory run: 210 instances, every OPT proved, 1,313 CPU-seconds, no protocol deviations. |
| 02:20 | PD-exp implementation check on Gupta & Radovanović's Figure 3 distributions. It reproduces their qualitative behaviour, so PD-exp's large excess is the algorithm, not a bug. |
| ≈ 02:35 | Reported online-frontier-v1 to the user and asked for commit approval and spend caps. |
| ≈ 03:00 | b1 reported its MoH/HMACE leaderboard comparison (see the table above). |
| 03:02–03:05 | overfit-gates-v1 finished, CPU only. Incident: a chained background command thought dead started duplicate scoring for about a minute; the duplicate rows were identical and were dropped (its RUN_LOG). |
| ≈ 03:30 | b1's online-beyond-ss-v1 confirmatory run finished. |
| 05:35 | Another (coordinating) session committed `docs/research-directions`, `exp/online-frontier` and `exp/overfit-gates` unchanged, at the user's request, and pushed them to `origin`. This session made neither the commit nor the push. |
| 05:36 | The user approved commits and "the most promising" paid follow-ups. |
| ≈ 05:40 | Launched `llm-from-ss-v1` (HF cap $2.50, seeds 84000–84999), `short-horizon-v1` (HF cap $4.00, seeds 85000–86999) and a final targeted novelty check (no spend). Each follow-up commits its protocol before its first run and its results at the end, locally only. |
| 05:52 | Session 2d took the second-benchmark lane: does the weak-baseline pattern hold beyond bin packing? Branch `exp/tsp-construct` (worktree `../ssm-tsp-construct`), CPU only, seeds 200000–209999. Target: the step-by-step TSP construction task (FunSearch/EoH/ReEvo/MCTS-AHD/HSEvo). By 2d's reading of the papers, MCTS-AHD's best LLM heuristic is 9.69% / 11.79% / 13.71% above LKH at n = 50/100/200, against about 5.5% / 7.6% for textbook farthest insertion (Kool et al. 2019); not checked here. Flow shop (NEH + IG) is still free. |
| 05:59 | Final novelty check finished, no spend (`docs/literature/novelty-check-sum-of-squares.md`).

- **Not found anywhere:** an SS or distribution-aware online algorithm compared with FunSearch or LLM-evolved heuristics.
- **Coverage:** about 35 LLM-heuristic papers grepped; citers of Csirik et al. on OpenAlex and Semantic Scholar; Google Scholar; GitHub; Hacker News; FunSearch's issues.
- **Not found either:** OPT = L1 on FunSearch's Weibull instances.
- **How widely the benchmark is used:** about 27 papers opened, an estimated 40+ in total.
- **Confirmed:** MoH Table 2 (avg 0.453%) and HMACE* (0.441%) match b1's citations.
- **Open leads:**
  - OpenReview reviews were not checked (challenge page).
  - A 404 GitHub repo whose search snippet says an LLM loop's champion was SS.
- **FunSearch's own SI** cites Angelopoulos et al. for its Weibull setting, and that paper discusses SS, Gupta–Radovanović and Banerjee–Freund. |
| 06:57–07:10 | Load average about 64–70 on 10 cores: about 33 worker processes of session 2d's TSP study plus another session's `bin_packing_online_informed` loop. This session's two LLM studies stayed within their caps (3 and 4 processes). They use 30 s-per-instance evaluation timeouts, so this session asked 2d to cap at 4 processes; 2d agreed and its remaining jobs drain to at most 4. Both studies were asked to log load and count timeouts per arm. Interim counts: short-horizon-v1 below 1% per arm, with 2 evaluations invalid only by timeout, both in control arm A; llm-from-ss-v1 1 of 736. Session 2d also reported running `pkill -f "multiprocessing.spawn"` at about 06:31, which matches every multiprocessing worker of this user. Our loops use a ThreadPoolExecutor and `python -c` sandbox children, which that pattern does not match, and no kill signatures appear in either study's logs, so neither study was affected. |
| 08:03 | Session 2d reported interim tsp-construct-v1 results: pre-registered, CPU only, $0, branch `exp/tsp-construct` (not pushed). These are 2d's numbers, not re-checked here.

Setup: MCTS-AHD's released 1,000-instance test sets for the step-by-step TSP construction task. 2d's nearest neighbour reproduces the published Greedy Construct exactly.

- **The interface ceiling.** The interface passes the full distance matrix, so a stateless function can emit any tour. Greedy edge + 2-opt + Or-opt (about 60 lines) is 1.85 / 2.44 / 2.85% above optimal at n = 50/100/200. The best published LLM results are 4.76 / 6.47 / 8.88%. An emitted LKH tour scores 0.00%.
- **The textbook baseline.** Farthest insertion (1977) gets 5.53 / 7.49 / 9.03% and beats every row of MCTS-AHD's Table 1, as well as CALM, MoH, Clade-AHD and PathWise.
- **Released heuristics re-run:** MCTS-AHD 8.78 / 10.30%; HiFo 9.09%; ReEvo 10.5 / 11.9%.
- **Released-code findings:** Clade-AHD's released heuristic is exactly nearest neighbour. HiFo's repeats one deterministic rollout 8 times.
- **A reference error.** MCTS-AHD's n = 200 'optimal' (10.659) is 0.46% below the proven optimum of its own test set (10.708), so published n = 200 gaps are overstated by about 0.5 points.

With online-frontier-v1 and online-beyond-ss-v1, the weak-baseline pattern now holds on two benchmarks. |
| ≈ 08:50 | Session b1 had independent reviewers check online-frontier-v1 and overfit-gates-v1 on main (468a352), at the user's request (`docs/reviews/`, branch `fix/obss-u250-12`). Verdict for both: "sound, with issues". Every headline number recomputed exactly, and `analyze.py` reproduced byte-identical outputs. The issues were interpretation and bookkeeping. |
| 08:43 | Corrections applied on branch `research/followup-2026-10-04` from origin/main. Each new figure was recomputed from saved data, and the paper's Theorem 3 bound was checked.

**online-frontier-v1:**
- the interface claim narrowed (only one stateless restriction tested; FunSearch's evaluator permits state);
- the failed OR-optimum check (76/80) listed as a deviation;
- the n = 5 released set reported descriptively;
- 16 pre-registered contrasts instead of 32;
- PD-exp's bound corrected to √(8BT);
- the OR data hashes logged.

**overfit-gates-v1:**
- leads with the 2-item-archive mechanism;
- the promotion-weighted gap is 0.38 [0.07, 1.05], against 0.61 for the mean of run means;
- the wrong tournament-v2 attribution replaced;
- the bound overstatement is about 4–10× with a competitive σ;
- the veto contrasts rest on 2–4 runs (sign test p = 0.25). |
| 08:53 | llm-from-ss-v1 finished (commits 1c6bc88 pre-registration at 05:41, 0b0e7e9 results). Three runs hit the 5,400 s wall limit at 293, 264 and 286 steps because of machine load; this is recorded as a deviation. One evaluation in 1,147 timed out, and it would not have been accepted. The loop's own OVERFIT? flag on s0–s2, from 2 hidden instances, was overturned by the 100-instance audit. |
| ≈ 09:05 | short-horizon-v1 finished (aa16408). Incidents, all logged in its RUN_LOG: its run monitor expired, so the audit started 22 minutes late (this session prompted it); a false monitor alert; a leftover load-logger loop was killed. Public-instance timeouts: 2/599 in A, 1/600 in D, 0 in B, C and E. The control arm plausibly lost one promotion to load, which biases the contrasts toward zero. |
| 09:05 | Session 2d told it may raise its worker cap: no timeout-sensitive work of this session is running. |

## Decisions and why

- **CPU-only directions first.** The first "continue" did not name a budget, so the two directions
  that need no API spend ran first. Paid ones waited for the user's approval.
- **Pre-registration without commits.** Commits were not yet approved, so each protocol's SHA-256
  and time were written to its `RUN_LOG.md` before any run.
- **The exact optimum, not best fit, as the reference.** Measuring headroom against best fit made
  FunSearch's gain look like 65 bins per instance. Against the optimum, all of the gain is online
  waste and the remaining gap is 13–14 bins.
- **PD-exp kept as specified.** Its poor numbers were checked against the paper's own figure rather
  than tuned, because the protocol fixed its parameters.
- **Choice of the paid follow-ups.** The planned "does the loop rediscover SS when state is allowed"
  study was replaced by "can the loop improve on SS when it starts from SS". The reason:
  llm-long-search-v1 had already shown that the loop, allowed state, reached 96.8% of FunSearch and
  stayed below SS. The short-horizon study was chosen because overfit-gates-v1 had just produced
  direct evidence for the mechanism: 554 of 635 archived counterexamples were 2 items long.
  Strategist's timing controls on ShinkaEvolve and behavioural dedup are deferred. They need more
  setup and more spend.
- **Caps.** Recorded Hugging Face spend before the follow-ups was about $9.4 of a credit of about
  $20: tournament-v2 full-v2b $8.04, full-v2 $0.44, smoke $0.14, llm-long-search $0.80, demos about
  $0.01. The two follow-ups are capped at $6.50 combined.

## Spend

| Item | Spend |
|---|---|
| Literature agents, the probe, online-frontier-v1, overfit-gates-v1 | $0 of API calls; CPU only (about 2,000 CPU-seconds here and 6,707 for overfit-gates) |
| llm-from-ss-v1 | $1.0994 of HF credit (1,143 calls) |
| short-horizon-v1 | $1.84 of HF credit |

## Open items

- **OR-Library data in public `origin`.** `exp/online-frontier` includes OR-Library's
  `binpack1`–`4` files. OR-Library's page states no licence. These files are widely redistributed,
  for example in BPPLib, but the team may prefer to replace them with a fetch script and their
  hashes.
- **Index.** `experiments/README.md` does not list the new studies yet. Add them when the branches
  are merged.
- **Branches.** `docs/research-directions` and `exp/online-frontier` were merged into main and their
  remote refs deleted (session 43, PR #8 era). Their later local commits are carried by
  `research/followup-2026-10-04`, which also holds the review corrections. It is not pushed yet.
- **Wording.** The final novelty check found no prior comparison (`novelty-check-sum-of-squares.md`).
  Two open leads: OpenReview reviews (blocked by a challenge page) and a deleted GitHub repository.
  The reviewer objections to answer, in its order:
  1. SS uses state the interface withheld.
  2. FunSearch aimed at discovery, not a leaderboard.
  3. Different instances.
  4. A small effect (head-to-head against ab-WorstFit is already in online-frontier-v1: 10.9 against 13.6 bins at 5k).
  5. The known-horizon variant uses n.
  6. OPT = L1 is expected for random instances.
  7. SS's worst case: test on Sim et al.'s 12-dataset suite.
