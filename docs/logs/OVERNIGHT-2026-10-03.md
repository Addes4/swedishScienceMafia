# Overnight experiments, 3 October 2026: coordination log

This log records how the six overnight experiments were set up, run and interrupted: the decisions,
approvals, incidents and costs that are not in any single experiment's write-up. Each experiment's
own `RESULTS.md` is on its branch and is the authority for its numbers. Times are BST and
approximate unless stated.

> **Paths.** On 4 October at about 06:20 this log moved from `experiments/` to `docs/logs/`, and
> other documents moved into `docs/` ([map](../README.md)). Paths and links below were updated to
> the new locations, including in entries describing earlier commits.

## Why these experiments

After PR #1 the project had four parts (Falsify, Simplify, Strategist, triage) with three gaps:
no search had beaten best-fit on fresh data, no closed-loop LLM run had been recorded, and the
triage comparison had never run. The six experiments below were chosen to close those gaps, each
answering one design question for the final framework.

## Experiments at a glance

| # | Experiment | Branch, commit | Folder | Status | Headline |
|---|---|---|---|---|---|
| 1 | Bin-packing ceiling | `exp/bp-ceiling` `50d9f9c` | `experiments/bp-ceiling-v1/` | Done | The 80-item instances are the ceiling. On Weibull 5k a 21-weight linear rule reaches −3.28 pp vs best fit (FunSearch's heuristic −3.33 pp). The evaluator reproduces FunSearch's published 3.98% / 4.23% / 0.68% exactly. |
| 2 | Idea table (triage) | `exp/idea-table` `7697c21` | `experiments/idea-table-v1/` | Partial: 62 of 114 ideas complete | The model decides success: Opus 62/62, Sonnet 60/62, Haiku 10/62. Jev and the Claude rankers are at chance; Codex AUC is 0.600. Ranked triage does not beat random tiers. Sonnet on every idea is best per dollar. |
| 3 | Memory ablation | `exp/memory-ablation` `f259c82` | `experiments/memory-ablation-v1/` | Done | Executable counterexamples did not improve the audited final policy; all primary intervals include 0. Memory cut harmful proposals mainly by inducing no-op proposals. Memory was not token-matched (934 vs 1,172 tokens). |
| 4 | Framework tournament | `exp/tournament` `dfde427` | `experiments/tournament-v1/`, `tournament-v2/` | v1 partial: 17 of 60 runs complete. v2: HF route and smoke runs only; the grid was not run. | v1: two of three problems saturate within 1–3 Sonnet calls. At a common early spend, lean (+0.233 AUC, CI [0.096, 0.386]) and independent sampling (+0.209) led ShinkaEvolve, and triage trailed (−0.156). Final scores did not differ. Not budget-matched. |
| 5 | Strategist v2 | `exp/strategist-v2` `3d3372b` | `experiments/strategist-v2/` | Done | v2 beats v1 on LABS (+0.137) and NK (+0.0058), ties on Heilbronn. A patience rule tuned on dev seeds still wins on LABS. Almost all of the gain comes from the crossover gate. |
| 6 | Gate red-team | `exp/gate-redteam` `b55dea3` | `experiments/gate-redteam-v1/` | Done | 0 of 68 exploit attempts (28 hand-written, 40 LLM-written) gained a material unearned score. Three backward-compatible fixes are in separate commits. |
| - | Devin: FunSearch reproduction | `devin/funsearch-repro` (expected) | `devin/funsearch_repro/` (expected) | Started by the user; no branch pushed as of 22:35 | - |

## Setup used by every agent

- Shared virtual environment `~/.venvs/ssm` (Python 3.12, `requirements.txt` plus `modal`; bp-ceiling
  added `cma`). System Python 3.14 has no packages.
- Keys live only in the main checkout's git-ignored `.env`. Each worktree symlinks it
  (`ln -sf <main>/.env .env`). Key values were never printed or committed.
- Modal profile `adrian-sohrabi01`. Apps are named `ssm-<experiment>`.
- Hugging Face CLI logged in. Its token (in `~/.cache/huggingface/token`) is used for the HF router
  fallback below.
- Each agent worked in its own worktree on `exp/<name>`, wrote `PROTOCOL.md` before confirmatory
  runs, and followed one documentation standard for `RESULTS.md`, `summary.json` and figures.

## Timeline and decisions

| Time | Event |
|---|---|
| 19:30 | Six agents launched with spend caps: idea-table $40, memory-ablation $15, tournament $75 (smoke run only until go-ahead), gate-redteam $5, bp-ceiling and strategist $0 (CPU and Modal only). |
| 19:50 | User added the Anthropic and TypeSafe (Jev) keys; verified with one Haiku call. User pasted the Devin task (below) into Devin. |
| 19:55 | Memory-ablation pilot null (no promotions in the 80-item regime). Go-ahead to run the confirmatory study in the Weibull 5k code regime, merging the `bp-ceiling` adapter. |
| 20:00 | User asked that everything be documented. The documentation standard was sent to all agents. |
| 20:05 | The literature-review session (`docs/related-work`) sent findings; they were relayed to each agent as secondary analyses. That session also relayed a user approval for the full tournament; it was not acted on until the user confirmed directly. That session's own record is [docs/logs/related-work-log.md](related-work-log.md). |
| 20:10 | User confirmed the full tournament: Anthropic cap $75, Modal cap raised to $75. |
| 20:20 | Asked whether the experiments were worth it, the user chose to keep the tournament design (5 arms × 3 problems × 4 seeds at $1.10 per run) and the 114-idea table, over the suggested alternatives. |
| 21:30 | Credit exhausted (incident 1). |
| 21:45 | Tournament app stopped by hand; agents resumed with no-API instructions. |
| 22:00 | Claude Code session limit on the second account (incident 2). User switched accounts; agents resumed two at a time. |
| 22:15 | User asked for another route than Anthropic credit. The HF router was verified and tournament-v2 started on open models. |
| 22:15-22:30 | bp-ceiling, memory-ablation and idea-table finished and were written up. |
| 22:32-23:03 | The tournament-v2 smoke grid (5 arms, $0.03 each) took 30 minutes. LLM calls took 18–36 s, but programs written from scratch took up to 611 s per evaluation, running erdos_squares' 13 instances in sequence at up to 60 s each. The tournament agent was told to evaluate instances in parallel and, if still needed, to lower per-instance time limits equally across arms as a disclosed pre-launch amendment. |
| 23:05 | The user decided not to run the tournament-v2 grid. Tournament-v1's partial data already answered the main question: two of three problems saturate within 1–3 Sonnet calls, and the single-model loops led ShinkaEvolve at low spend while triage trailed. The remaining time goes to the submission: consolidating branches, a single runnable framework, the README and the video. Tournament-v2 is documented as the HF route plus its smoke test, with the protocol marked "not executed". |
| 23:06-23:15 | Consolidation on branch `consolidate-overnight` (from `main`). The six `exp/*` branches, `docs/overnight-log` and `docs/related-work` were merged. Conflicts arose only in `.gitignore` (kept both sides) and in the imports of `autoresearch/gate.py` (kept both `tokenize` and `ThreadPoolExecutor`). The ClaudeRanker crash was fixed with tests, and the README hub was updated. 175 tests pass. `check --all` gives the same scores as `main` for the deterministic problems; circle packing and Erdős discrepancy start from unseeded random programs, so they vary between runs (0.3512 and 0.3563 in two runs of circle packing on `main`). Nothing was pushed. |
| 23:15-23:20 | Documentation audit of `consolidate-overnight`. Every experiment folder has PROTOCOL.md, RESULTS.md (with reproduce, cost, limitations, evidence index and next steps), summary.json and, except tournament-v2, a figure; there are no broken links and every new module has a docstring. The gap was the per-part READMEs, so each experiment's suggested text was folded into `falsify/`, `strategist/` and `autoresearch/`, and `tournament/README.md` was written. The literature session's final log commit was merged. |
| 23:25 | At the user's request the branch was pushed and PR #3 opened. A pre-push scan found no keys or email addresses; the largest file is 1.6 MB. |
| 23:30-23:40 | Asked what is new and what remains open, the coordinator searched arXiv (15 queries) for papers on the five open questions and wrote [docs/literature/related-work-addendum.md](../literature/related-work-addendum.md). It is based on abstracts only. Main changes: frame the cheap-formula result as the extreme case of separating structure from tuning (LLaMEA-HPO, TIDE). Read the memory null against failure feedback that explains where and why (Karimi et al., MOSAIC). |
| 23:47 | Correction: the last four entries' times were first written as 00:00–00:45 (the coordinator assumed it was past midnight without checking). They were fixed from git commit times, and the addendum's "4 October" date was changed to 3 October. |
| 23:39-23:55 | One-command loop, built from the spec the user pasted, on branch `feat/one-command` (worktree `../swedishScienceMafia-one-command`, from `consolidate-overnight`). `python -m autoresearch.loop` wraps `tournament.run` (lean arm, gate on, hard cap, mock API), then audits the final program on hidden instances, scores `problems/<name>/baselines/*.py` with the same gate (FunSearch's two heuristics for bin packing), explains the program by two-sided ablation (`autoresearch/explain_code.py`) and writes `report.md`. One correction to the spec's evidence table: in tournament-v1 the arm ahead of ShinkaEvolve was plain lean without the gate, so the README credits the gate to Falsify's gate-v3, not to the tournament. 182 tests pass. Live demo ([runs/demo-binpacking](../../runs/demo-binpacking/report.md)): 8 DeepSeek-V4.1-Flash steps for $0.0038; nothing beat best fit (7 of 8 proposals packed exactly like it). Mock demo on Erdős squares in 4 s. Decisions, bugs, limitations and the spec verbatim: [autoresearch/LOOP.md](../../autoresearch/LOOP.md). Latest `consolidate-overnight` merged in. Pushed at the user's choice as PR #4 on top of PR #3, after a key scan of the diff and of the runs' archives. |
| 23:50-00:10 | Duplicate build. Before the coordinator knew the `feat/one-command` worktree existed, it launched an agent on the same spec, with four corrections. That agent built local branch `feat/one-command-v2` (5c99cae, 184 tests, HF spend $0.0047), which is kept as an unpushed backup. Two of the four corrections were right, two were wrong. Wrong: the Javed, Gobet & Lane 2022 citation is real (Data Mining and Knowledge Discovery, doi 10.1007/s10618-022-00830-7, checked on Crossref). Right: the "44/139" figure had no source in the repo. Lesson: check `git worktree list` before launching a builder. |
| 00:15-00:19 | The user chose PR #4. Its builder removed "44/139" (54709ac). The coordinator reviewed the PR at that commit: 182 tests pass, the `--mock` run takes 3.9 s, no keys were found, and it contains `consolidate-overnight`. At the user's request PR #4 was merged into `consolidate-overnight` (ca5f0a0), so PR #3 now contains the loop. The live bin-packing demo found no improvement: 7 of 8 proposals scored exactly as best-fit. A live Erdős-squares demo is untested. |
| 00:20 | Another session launched the tournament-v2 confirmatory grid as `full-v2b`, from worktree `../ssm-tv2` on branch `tournament-v2-launch`, with pre-launch amendments: bin_packing_online replaces circle_packing, 4 gate workers, a 4-hour wall limit per run. Caps: $0.15 of HF per run ($9 for the grid) and $60 of Modal. This coordinator did not start it and left it running. Its results are not on this branch, so `tournament-v2/RESULTS.md` still describes smoke runs only. |
| 00:25-00:31 | Readability pass for outside readers, at the user's request. The root README was restructured: summary, quick start, key findings, method, components, reproduction, layout, limitations and citation. Added `experiments/README.md`, an index of all studies with protocols and results. Replaced the coordinator's private venv path with `python` in seven write-ups, fixed one broken link, and relabelled triage's planned-but-not-run experiment. The repository has no LICENSE file; the team has to choose one. |
| 01:17 | At the user's request, launched [llm-long-search-v1](../../experiments/llm-long-search-v1/PROTOCOL.md), pre-registered in adb7fe9: 4 runs of `autoresearch.loop` on `bin_packing_online`, 300 steps each, DeepSeek-V4.1-Flash via HF, with a $3 cap. |
| 01:50-02:14 | The runs finished at a total cost of $0.80. Fresh audit on 100 unseen instances: all 4 runs beat best-fit; the best reached −3.20 pp against FunSearch's −3.31 (97% of its gain) but stayed 0.11 pp [0.07, 0.15] behind, so 0 of 4 reached FunSearch's level by the pre-registered test. Sum-of-Squares, added after the protocol as a disclosed reference, beat FunSearch (−0.17 pp). The README's idea-table wording was also corrected: Codex and Opus did rank better than chance. |
| 02:25 | PR #5 (llm-long-search-v1) was merged into `main` (02ba33e). |
| 05:33-05:43 | Documentation pass at the user's request ("make sure everything got documented"). Other sessions had left finished but uncommitted work, all now preserved: online-beyond-ss-v1, online-frontier-v1, overfit-gates-v1 and `docs/literature/research-directions.md`. Each was committed unchanged on its own branch and pushed. The four-approach campaign's documents were committed on `research/all-approaches` and pushed; its 470 MB of raw files were copied out of `/private/tmp` to `~/Documents/ssm-backups/all-approaches-20261004-0535`. Tournament-v2's full grid (`full-v2b`, results committed at 05:28) had no write-up and its RESULTS.md still said the grid was not run, so its results were written up from `summary.json`, and two macOS-duplicate files were renamed. All of this except the campaign was merged into `main` through branch `integrate/night-results`. The README now reflects FWSS and the gate caveat from overfit-gates-v1. |
| 06:10-06:40 | Repository cleanup at the user's request ("the github is completely without structure"). Documentation moved into a `docs/` hub ([docs/README.md](../README.md)): literature under `docs/literature/`, logs under `docs/logs/`, plans under `docs/plans/`, paper material under `docs/papers/`, hackathon material under `docs/hackathon/`. Experiment write-ups stay next to their data; the early v3, v4 and Simplify protocols moved into their study folders. The user chose: archive unmerged branches as `archive/*` tags, keep the supplied paper PDFs, leave other people's branches and the three running lanes (b1, 2d, cc) alone. Merged branches were deleted on GitHub and locally, after their owners confirmed. PR #2 was closed and folded into `docs/papers/review/`. |
| 05:48-10:26 | Session 2d, under the user's /goal ("make a breakthrough or discover something new"), claimed a lane no other session was using and ran [tsp-construct-v1](../../experiments/tsp-construct-v1/RESULTS.md) (pre-registered, CPU only, $0). It asked whether classical TSP heuristics beat the LLM-designed `select_next_node` heuristics of MCTS-AHD and its successors on their released test sets. Result: the interface passes the whole distance matrix. Greedy + 2-opt + Or-opt emitted through it beats every published step-by-step result at n = 50 / 100 / 200, and farthest insertion (1977) beats every LLM-AHD row of the MCTS-AHD lineage. 5 of 6 released LLM heuristics are Pareto-dominated, and Clade-AHD's released file is exactly nearest neighbour. MCTS-AHD's n = 200 optimum is 0.46% too low (LKH, confirmed by heavy LKH on 20 and exact integer-programming proofs on 5 instances). An independent fact-check subagent then found overstatements: a plan cache behind the reported speeds, 'every result' where POMO rows exist, '60 lines', and 'proved optimum'. They were corrected and uncached times added. A paper draft is in `docs/papers/tsp-construct/`. |
| 06:31 | Incident 4 (below): a `pkill -f "multiprocessing.spawn"` by session 2d killed workers of its own pools. |
| 07:08-09:12 | At session cc's request, session 2d capped its TSP worker pools at 4 processes in total while cc's timeout-sensitive LLM runs (llm-from-ss-v1, short-horizon-v1) finished; cc then lifted the cap. |

## Incidents

1. **Anthropic credit exhausted (about 21:30).** The Claude Code account running the agents and the
   experiments' `.env` key both returned "credit balance is too low" at the same time. The experiments'
   own logs account for only about $66 of the $200 (ledger below). The rest was most likely the agents'
   own usage, billed to the same organisation. Effects:
   - the idea table lost 146 of 342 cells;
   - the tournament lost 43 of 60 runs;
   - memory-ablation's confirmatory had already finished.

   **Lesson:** keep the experiments' key on a different organisation from the account that runs the
   agents, and budget agent usage explicitly.
2. **Runaway retries.** After the cutoff, ShinkaEvolve containers kept retrying and logged more than
   12,000 billing errors. App `ap-NB2agmLSJI8pfUTwKvEQNr` was stopped by hand. Fixed in `exp/tournament`
   `65ffdcb`: billing and authentication errors are now fatal.
3. **Session limit after re-login (about 22:00).** Four resumed Opus agents hit the new account's limit
   within about 20 minutes. Afterwards agents were resumed at most two at a time, in priority order.

4. **A pattern kill on a shared machine (06:31, session 2d).** To stop a one-off script that kept respawning
   failing workers, session 2d ran `pkill -f "multiprocessing.spawn" -U <user>`. Every session runs as the same
   OS user, so the pattern matches every multiprocessing worker on the machine. It killed workers of three of
   tsp-construct-v1's own pools, which then waited forever on the lost tasks. A check with `ps` showed that the
   other sessions' `autoresearch.loop` runs start their children with a different command line and were not
   hit. A follow-up kill of the session's own PIDs was refused by the permission classifier. The study resumed
   with skip-if-exists runners and a HOLD file (details in its `RUN_LOG.md`).
   **Lesson:** never kill by pattern on this machine; make long runs stoppable with a HOLD file and resumable.

## Spend ledger (experiments only)

| Experiment | Anthropic | Modal | Other |
|---|---:|---:|---|
| bp-ceiling | $0 | ~$0.41 | - |
| idea-table | $19.73 (12 mid-stream failures logged at $0) | ~$0.39 | Jev ~$0.005; one Codex call on the ChatGPT plan |
| memory-ablation | $3.82 | ~$0.37 | - |
| tournament-v1 and v2 | $41.86 ($40.23 full grid, $0.96 smoke, $0.67 check) | $7.47 (billing report, both versions; the last hour may be incomplete) | Jev $0.011; HF $0.1408 (v2 smoke) |
| strategist-v2 | $0 | $0.33 | - |
| gate-redteam | $0.21 | $0 | - |
| one-command demo (`runs/demo-binpacking`) | $0 | $0 | HF $0.0038 |
| **Total** | **≈ $65.6** | **≈ $9.0** | HF ≈ $0.145 |

Claude Code agent usage is not in this table; it was not metered separately.

## Fallback LLM route: Hugging Face router

At 22:15 the HF router (`https://router.huggingface.co/v1`, OpenAI-compatible) was verified with two
tiny calls billed to the user's HF credit (about $20). The tournament's arms can now run on open
models:
- single-model arms: DeepSeek-V4.1-Flash on deepinfra, $0.20 / $0.60 per million tokens;
- triage tiers: DeepSeek-V4-Pro on deepinfra and Qwen3.5-9B on together.

A Flash call cost about $0.0019, roughly 25 times less than a Sonnet call in v1. Only smoke runs were
made ($0.14). Tournament-v1 (Claude) stays a separate, partial study. Before any open-model grid, turn
on parallel instance scoring (`GATE_WORKERS`, committed and off by default); evaluating programs,
not the model, set the wall time.

## Bugs found and where they are fixed

All three are fixed on `consolidate-overnight`, not yet on `main`.
- `autoresearch/rankers.py`, `ClaudeRanker`: a list-valued `"kind"` crashed the parser on every batch,
  and the triage loop shared it. Fixed in `e8f15cc`, with `tests/test_rankers.py`.
- Gate hardening from `exp/gate-redteam` is merged:
  - `dabeabd` caps candidate output size;
  - `73ecbc4` rejects non-finite circle radii;
  - `3823826` makes the static scan ignore comments and string literals.
- Retries on billing and authentication errors, from `exp/tournament` `65ffdcb`: these errors are now
  fatal, for both the Anthropic and HF routes.

## Open work and how to finish it

| Item | Command or action | Needs |
|---|---|---|
| Fill the idea table | `python -m autoresearch.ideatable fill experiments/idea-table-v1` (skips done cells; `--dry-run` prints cost) | Anthropic credit, ~$15.53 |
| Rerun tournament-v1's 43 truncated runs | `modal run --detach tournament/modal_app.py --grid experiments/tournament-v1/grids/rerun.json --experiment-cap 90`, then `python -m tournament.pull full-v1-rerun` and `tournament.report` (see tournament-v1 RESULTS.md) | Anthropic credit, ≤ $47.30 |
| Strategist with measured LLM costs | Fill `experiments/strategist-v2/costs/measured_llm.json`, then `python -m strategist.v2 confirm --costs measured --modal` | Measured cost ratios |
| Publish the consolidation | Pushed `consolidate-overnight` and opened [PR #3](https://github.com/swedishScienceMafia/swedishScienceMafia/pull/3) into `main` (not merged) | Team review |
| One runnable framework | Built: `python -m autoresearch.loop` on branch `feat/one-command` (see the 23:39 entry and [runs/README.md](../../runs/README.md) for the demo plan). At the user's choice, pushed and opened as [PR #4](https://github.com/swedishScienceMafia/swedishScienceMafia/pull/4) into `consolidate-overnight` (on top of PR #3) | Team review, then merge into PR #3 |
| Submission | Video of at most 4 minutes, repo URL and short description to admin@algorithmdiscovery.org by 14:45 on 4 Oct, the event's submission deadline ([schedule](https://github.com/swedishScienceMafia/swedishScienceMafia/blob/archive/full-research-2026-10-04/docs/hackathon/website.md)). The "10:30 code freeze" in earlier plans was an internal target, not an event rule. Draft description, video outline and Q&A are in `docs/papers/pitch-draft.md` | Owner |
| Review PDF | Done: PR #2 was closed at about 06:20 on 4 October; its refreshed PDF and build script are in [docs/papers/review/](https://github.com/swedishScienceMafia/swedishScienceMafia/tree/archive/full-research-2026-10-04/docs/papers/review) | – |
| Devin | Check the session; it may lack access to the GitHub org | User |

## Devin task, as pasted by the user

```
Repo: github.com/swedishScienceMafia/swedishScienceMafia. Work on a new branch
devin/funsearch-repro and open a PR when done; do not merge.

Paper: FunSearch (Romera-Paredes et al., Nature 2024), PDF in
"docs/hackathon/track-1-papers/Mathematical discoveries with LLMs.pdf";
code at github.com/google-deepmind/funsearch.

1. Reproduce the online bin-packing table: first-fit, best-fit and FunSearch's
   published heuristics on OR-Library OR1-OR4 and Weibull 5k (10k/100k if time),
   reported as % excess bins over the L2 lower bound. Code in
   devin/funsearch_repro/ with a one-command script and RESULTS.md comparing your
   numbers to the paper's.
2. Go further by testing the published result: following falsify/README.md,
   search for item streams where FunSearch's Weibull heuristic uses more bins
   than best-fit (including the families in falsify/core.py), shrink each to a
   minimal example, and report how often and where it loses. Then simplify the
   heuristic (drop parts while performance stays within tolerance) to show which
   parts matter.
CPU only, no LLM API calls, don't modify existing folders, small commits.
```


## Work that is not on `main` (as of 4 October, 06:20)

| What | Where | Why it is not merged |
|---|---|---|
| Four-approach live campaign (OpenAI models): findings, ledger, per-run reports | Tag [`archive/all-approaches`](https://github.com/swedishScienceMafia/swedishScienceMafia/tree/archive/all-approaches) on GitHub (`runs/FINDINGS.md`), formerly branch `research/all-approaches`; raw files in `~/Documents/ssm-backups/all-approaches-20261004-0535` and `~/Desktop/ssm-all-approaches.zip` | It is a parallel framework (`autoresearch/evidence_loop.py` and related files) built from the first `main`. Merging it would put two competing loops and conflicting READMEs in front of readers |
| Throughput and Modal evaluation work | Local tag `archive/throughput-modal` (not pushed) | Its commits are already in `archive/all-approaches` |
| Framework plans | The plans are in [docs/plans/](https://github.com/swedishScienceMafia/swedishScienceMafia/blob/archive/full-research-2026-10-04/docs/plans/README.md); the full branches are local tags `archive/plan-unified-autoresearch` and `archive/plan-combined-framework` (not pushed) | Superseded by `autoresearch.loop` (PR #4) |
| Duplicate one-command build | Local tag `archive/one-command-v2` (5c99cae, not pushed) | Kept as a backup; PR #4 was chosen |
| Workshop-paper drafts (LaTeX and PDF) | `~/Desktop/ssm-paper-sources/` and the PDFs on the Desktop | Written by another session outside the repository |
| Devin's FunSearch reproduction | – | No branch or pull request was ever pushed |
| tsp-construct-v1 (finished; claimed at 05:48) | Session 2d: branch `exp/tsp-construct`, worktree `../ssm-tsp-construct`, folder `experiments/tsp-construct-v1`, paper in `docs/papers/tsp-construct/`; CPU only | Committed on its branch; the user decides whether to push and open a PR |
