# Overnight experiments, 3 October 2026: coordination log

This log records how the six overnight experiments were set up, run and interrupted: the decisions,
approvals, incidents and costs that are not in any single experiment's write-up. Each experiment's
own `RESULTS.md` is on its branch and is the authority for its numbers. Times are BST and
approximate unless stated.

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
| 4 | Framework tournament | `exp/tournament` `89974fa` (v1), v2 in progress | `experiments/tournament-v1/`, `tournament-v2/` | v1 partial: 17 of 60 runs complete. v2 (open models via HF) running. | See the tournament RESULTS.md. v1 is not a budget-matched comparison. |
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
| 20:05 | The literature-review session (`docs/related-work`) sent findings; they were relayed to each agent as secondary analyses. That session also relayed a user approval for the full tournament; it was not acted on until the user confirmed directly. |
| 20:10 | User confirmed the full tournament: Anthropic cap $75, Modal cap raised to $75. |
| 20:20 | Asked whether the experiments were worth it, the user chose to keep the tournament design (5 arms × 3 problems × 4 seeds at $1.10 per run) and the 114-idea table, over the suggested alternatives. |
| 21:30 | Credit exhausted (incident 1). |
| 21:45 | Tournament app stopped by hand; agents resumed with no-API instructions. |
| 22:00 | Claude Code session limit on the second account (incident 2). User switched accounts; agents resumed two at a time. |
| 22:15 | User asked for another route than Anthropic credit. The HF router was verified and tournament-v2 started on open models. |
| 22:15-22:30 | bp-ceiling, memory-ablation and idea-table finished and were written up. |

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

## Spend ledger (experiments only)

| Experiment | Anthropic | Modal | Other |
|---|---:|---:|---|
| bp-ceiling | $0 | ~$0.41 | - |
| idea-table | $19.73 (12 mid-stream failures logged at $0) | ~$0.39 | Jev ~$0.005; one Codex call on the ChatGPT plan |
| memory-ablation | $3.82 | ~$0.37 | - |
| tournament-v1 | $41.86 ($40.23 full grid, $0.96 smoke, $0.67 check) | $7.25 (billing report) | Jev $0.011 |
| tournament-v2 | $0 | in progress | HF router, cap $12 |
| strategist-v2 | $0 | $0.33 | - |
| gate-redteam | $0.21 | $0 | - |
| **Total** | **≈ $65.6** | **≈ $8.8 + v2** | |

Claude Code agent usage is not in this table; it was not metered separately.

## Fallback LLM route: Hugging Face router

At 22:15 the HF router (`https://router.huggingface.co/v1`, OpenAI-compatible) was verified with two
tiny calls billed to the user's HF credit (about $20). Tournament-v2 reruns the grid with
`deepseek-ai/DeepSeek-V4.1-Flash` for every single-model arm on a pinned provider. Its triage arm uses
DeepSeek-V4-Pro / V4.1-Flash / Qwen3.5-9B tiers. The cap is $12 of HF spend. Tournament-v1 (Claude)
stays a separate, partial study.

## Bugs found, not yet fixed on main

- `autoresearch/rankers.py`, `ClaudeRanker`: models return `"kind"` as a list and the parser crashes
  on every batch; the triage loop has the same bug. Worked around in `exp/idea-table`, not fixed at
  the source.
- Three gate fixes sit unmerged on `exp/gate-redteam`:
  - `dabeabd` caps candidate output size;
  - `73ecbc4` rejects non-finite circle radii;
  - `3823826` makes the static scan ignore comments and string literals.

## Open work and how to finish it

| Item | Command or action | Needs |
|---|---|---|
| Fill the idea table | `python -m autoresearch.ideatable fill experiments/idea-table-v1` (skips done cells; `--dry-run` prints cost) | Anthropic credit, ~$15.53 |
| Rerun tournament-v1's 43 truncated runs | `modal run --detach tournament/modal_app.py --grid experiments/tournament-v1/grids/rerun.json --experiment-cap 90`, then `python -m tournament.pull full-v1-rerun` and `tournament.report` (see tournament-v1 RESULTS.md) | Anthropic credit, ≤ $47.30 |
| Strategist with measured LLM costs | Fill `experiments/strategist-v2/costs/measured_llm.json`, then `python -m strategist.v2 confirm --costs measured --modal` | Measured cost ratios |
| Consolidate | Merge the `exp/*` branches into one branch; apply the adapter, gate fixes and rankers fix once; update the root README hub | - |
| One runnable framework | A single command that runs the LLM loop under the integrity gate with a spend cap, then a fresh audit and comparison with the cheap baselines | Owner |
| Submission | Video of at most 4 minutes, repo URL and short description to admin@algorithmdiscovery.org by 14:45 on 4 Oct; code freeze 10:30 | Owner |
| Devin | Check the session; it may lack access to the GitHub org | User |

## Devin task, as pasted by the user

```
Repo: github.com/swedishScienceMafia/swedishScienceMafia. Work on a new branch
devin/funsearch-repro and open a PR when done; do not merge.

Paper: FunSearch (Romera-Paredes et al., Nature 2024), PDF in
"context/Track 1 papers/Mathematical discoveries with LLMs.pdf";
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
