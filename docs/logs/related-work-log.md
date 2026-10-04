# Literature-review session, 3 October 2026: work log

This log records what the literature-review session did, decided and produced. The session was a
separate Claude Code session from the one coordinating the overnight experiments. Findings are in
[related-work.md](../literature/related-work.md), paper plans in
[docs/papers/outlines/](../papers/outlines/README.md) and the pitch draft in
[docs/papers/pitch-draft.md](../papers/pitch-draft.md). The experiments are recorded in their own
RESULTS.md files and in the coordination log (`docs/logs/OVERNIGHT-2026-10-03.md` on branch
`docs/overnight-log`). Times are BST and approximate unless they come from commits.

> **Paths.** On 4 October at about 06:20 this log moved from `context/` to `docs/logs/`, and the
> files it describes moved into `docs/` ([map](../README.md)). Paths below were updated to the new
> locations, including in entries describing earlier commits.

## What was asked

1. Go through the repository and suggest papers that explore the same thing, or that are worth
   reading.
2. Download them into `context/`, and judge whether they are useful and what they imply.
3. Summarise; say whether the work was unnecessary; say whether it fits the hackathon track.
4. Document the findings, then carry out the next steps.
5. Run the experiments now rather than overnight.
6. Say whether this could become a research paper, and outline both candidate papers.
7. Document everything.

## Timeline

| Time | Event |
|---|---|
| before 19:30 | Read every component's README, results and stated next steps, and the hackathon brief. Four search agents ran in parallel (Falsify; Strategist; Triage and integrity; comparable 2026 systems). About 20 of the reported papers were opened on arXiv by hand to confirm them. First recommendations given. |
| 19:30 | Asked to download everything. Three reading agents started on 22 key papers. All 44 arXiv IDs checked against the arXiv API; every title matched. |
| 19:35–19:45 | Downloaded 56 PDFs, one PostScript file and one HTML page into `docs/literature/related-papers/`, with a local index. Six papers could not be fetched (bot check, paywall or no open copy). |
| 19:45–19:55 | Reading agents reported. Their most consequential claims were re-checked against the papers: RAISE's tables, Gupta et al.'s Holm p-value and ASRO's table. |
| 19:58 | Plan given for the remaining time; the user asked for the findings to be documented first and the next steps carried out after. |
| 20:03 | Commit `fc2e9a4`: `docs/literature/related-work.md` and a README link. |
| 20:05 | Commit `a9b0659`: pitch draft. Findings sent to the coordinating session to relay to the six experiment agents. |
| 20:08 | The user asked to run the experiments now. This session told the user to approve the tournament in the coordinating session, and did not launch anything itself (see Decisions). |
| 20:10 | The coordinating session confirmed the user approved the full tournament directly ($75 Anthropic, $75 Modal). |
| 21:46 | Commit `503df2f`: pitch draft updated with strategist-v2, gate-redteam and the memory-ablation pilot. |
| 21:54 | Commit `5b2d9bb`: method, decisions and corrections recorded in related-work.md; `docs/literature/fetch_papers.py` added and tested. |
| 22:10 | Commit `34ec6b2`: two paper outlines. |
| 23:10 | Documents updated with bp-ceiling, the memory-ablation confirmatory study, idea-table and the partial tournament. Paper-outline index and this log written. |
| 23:15 | Commit `1e28890`. The coordinating session merged `docs/related-work` into its local branch `consolidate-overnight` (merge `91633c9`); this session checked that the merged files match. The overnight log's 20:05 entry now links this log. |

## What was produced

All files are on branch `docs/related-work` (worktree `../swedishScienceMafia-related-work`). The
branch is merged into the local branch `consolidate-overnight`; neither has been pushed.

| File | Content |
|---|---|
| `docs/literature/related-work.md` | The review. It covers: what is new and what is not; the literature by part; how each finished run lines up with the literature; what the review changed in the experiments; method, decisions, corrections and limitations; the reading list. |
| `docs/literature/fetch_papers.py` | Re-downloads every available paper into the git-ignored `docs/literature/related-papers/`, and lists the six that need a browser. |
| `docs/logs/related-work-log.md` | This log. |
| `docs/papers/pitch-draft.md` | Short description, video outline, demo plan, track criteria, likely questions with answers, submission checklist. All result slots are filled. |
| `docs/papers/outlines/` | Index plus outline A (Strategist) and outline B (checking the claims of autoresearch loops). |
| `README.md`, `.gitignore` | A link to the review; `docs/literature/related-papers/` ignored. |

Outside git: `docs/literature/related-papers/` in the main checkout holds the downloaded papers and a
local `README.md` index with a verdict for each paper.

## Decisions

- **PDFs are not committed.** The repository is public and most papers may not be redistributed.
  `fetch_papers.py` makes the set reproducible instead.
- **Access controls were respected.** HAL's bot check and ACM's paywall were not worked around.
  The six affected papers are listed for browser download.
- **One source of instructions for the experiment agents.** Findings went only to the
  coordinating session, which relayed them. At its request this session did not message the
  agents directly.
- **No design changes to pre-registered experiments.** The review's suggestions were offered as
  secondary analyses, or as input before a protocol was frozen. related-work.md lists which ones
  were adopted, with commits.
- **Spending approval.** This session passed on the user's words ("go ahead with the next steps
  yourself", then "run them now, not overnight") but did not treat them as approval to spend. The
  coordinating session also declined to act on a relayed approval and confirmed with the user
  directly. That is the intended behaviour, and it is recorded here for that reason.
- **Paper recommendation: write outline A first.** Its evidence is the most complete and its gaps
  cost little to fill.

## Incidents and corrections

- **Errors in subagent reports, corrected before use:**
  - FunSearch's c12 heuristic was evolved on 120-item instances, not 5,000-item ones.
  - AdaEvolve's arXiv ID is 2602.20133; 2602.23413 is EvoX.
  - ASRO's main text does not list the cross-bin features one report attributed to it.
- **Own error, caught before commit:** a draft said the Erdős squares reference is exact. The
  problem's `verify.py` calls it a conjecture (Campbell–Staton), so only Erdős discrepancy is a
  proven-maximum canary.
- **Two links in the results table overstated what papers showed and were narrowed:** LEVI and
  Gideoni et al. no longer appear there.
- **A read-only check briefly changed into the tournament agent's worktree** (about 19:58).
  Nothing was written there.
- **The API credit ran out at about 21:30**, cutting the tournament (17 of 60 runs complete) and
  the idea table (62 of 114 ideas complete). The coordination log records this. It is mentioned
  here because the documents were updated with those partial results.

## Cost

- **Experiment spend:** none. This session made no Anthropic API calls for experiments and used
  no Modal compute.
- **Session usage:** this session and its seven subagents (four search, three reading) ran on the
  Claude Code account. The subagents used about 763,000 tokens in total; the session's own usage
  was not measured. The coordination log suspects that agent usage billed to the same
  organisation contributed to the credit running out. Keeping research sessions on a separate
  organisation or budget would avoid that.

## How to reproduce or continue

```sh
git log --oneline main..docs/related-work          # this session's commits
python3 docs/literature/fetch_papers.py                     # re-download the papers (run on the branch)
python3 docs/literature/fetch_papers.py --only Herrmann     # one paper
```

## Open work

- **Push and open a PR:** the user decides. The work now travels in `consolidate-overnight`,
  which already links related-work.md from the README.
- **The coordinating session** owns the final pitch and can use `docs/papers/pitch-draft.md` as input.
- **Download six papers by hand** (listed by `fetch_papers.py`).
- **Before writing any paper:** run the gaps listed in each outline, and search the literature
  again.
