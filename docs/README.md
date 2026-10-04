# Documentation map

Where every document in this repository lives. Two rules decide the location:

- **Experiment write-ups stay with their data.** Each study's `PROTOCOL.md` and `RESULTS.md` sit in
  `experiments/<study>/` next to its raw traces, configs and hashes. The index of all studies is
  [experiments/README.md](../experiments/README.md).
- **Component documentation stays with its code.** Each package has a README next to the code it
  describes.

Everything else is in this folder.

## In this folder

| Folder | Contents |
|---|---|
| [literature/](literature/) | [related-work.md](literature/related-work.md): about 60 papers, which of our results are new and which reproduce published findings. [related-work-addendum.md](literature/related-work-addendum.md): papers on the questions the experiments left open. [research-directions.md](literature/research-directions.md): candidate new-finding areas with a literature verdict for each, and the Sum-of-Squares probe in [probes/](literature/probes/). [fetch_papers.py](literature/fetch_papers.py) re-downloads the reviewed papers into a git-ignored folder. |
| [logs/](logs/) | [OVERNIGHT-2026-10-03.md](logs/OVERNIGHT-2026-10-03.md): the coordination log, with decisions, approvals, incidents, spend, open work and the work that is not on `main`. [related-work-log.md](logs/related-work-log.md): the literature-review session's log. |
| [plans/](plans/README.md) | Design plans from 3 October that were superseded by the one-command loop, and one protocol that was never run. |
| [papers/](papers/) | [outlines/](papers/outlines/README.md): research-paper outlines (Strategist; checking the claims of autoresearch loops). [pitch-draft.md](papers/pitch-draft.md): submission text, video outline and likely questions. [review/](papers/review/): the experiment review PDF as of the evening of 3 October, its build script, and the addenda sent to its author. |
| [hackathon/](hackathon/) | The Track 1 brief ([track-1-brief.pdf](hackathon/track-1-brief.pdf)), the event's resource page ([website.md](hackathon/website.md)), and the papers supplied with the track ([track-1-papers/](hackathon/track-1-papers/)). |

## Elsewhere in the repository

| Document | Contents |
|---|---|
| [README.md](../README.md) | Project overview, quick start, key findings, components |
| [experiments/README.md](../experiments/README.md) | Every study, in the order it was run, with protocol, write-up and main result |
| [experiments/HANDOFF.md](../experiments/HANDOFF.md) | The first-round Falsify session's write-up and handoff |
| [experiments/PROTOCOL.md](../experiments/PROTOCOL.md), [PROTOCOL-v2.md](../experiments/PROTOCOL-v2.md), [RESULTS.md](../experiments/RESULTS.md) | First-round Falsify protocols and results, shared by `local-v1`, `local-v2`, `local-firstfit` and the Codex pilots. They stay at the top of `experiments/` because `falsify/report.py`, `falsify/pilot.py` and `falsify/simplify.py` read and write them there |
| [autoresearch/README.md](../autoresearch/README.md), [autoresearch/LOOP.md](../autoresearch/LOOP.md) | The one-command loop, integrity gate and triage; LOOP.md holds the design decisions and build log |
| [falsify/README.md](../falsify/README.md) | Counterexample replay, gates, soft gates, Simplify, and how the setup differs from FunSearch |
| [strategist/README.md](../strategist/README.md), [PROTOCOL.md](../strategist/PROTOCOL.md), [RESULTS.md](../strategist/RESULTS.md) | The adaptive strategy controller and its v1 study |
| [tournament/README.md](../tournament/README.md) | Whole-framework comparison at equal dollar budgets |
| [problems/README.md](../problems/README.md) | The problem contract, and one `problem.md` per problem |
| [runs/README.md](../runs/README.md) | The committed demo runs and the live-demo plan |

## Not in `main`

- **Archived branches** are kept as `archive/*` tags. On GitHub:
  [`archive/all-approaches`](https://github.com/swedishScienceMafia/swedishScienceMafia/tree/archive/all-approaches),
  the four-approach live campaign (`runs/FINDINGS.md`), and
  [`archive/refresh-review-pdf`](https://github.com/swedishScienceMafia/swedishScienceMafia/tree/archive/refresh-review-pdf),
  the former PR #2, whose PDF and build script are now in [papers/review/](papers/review/). The table
  "Work that is not on `main`" in the [coordination log](logs/OVERNIGHT-2026-10-03.md) lists everything else.
- **Work in progress** happens on `exp/*` and `docs/*` branches. Each one opens a pull request into
  `main` when it is done. New studies go in `experiments/<study>/`, logs in `docs/logs/`, and
  literature notes in `docs/literature/`.
