# Documentation map

Where every document in this repository lives. Two rules decide the location:

- **Experiment write-ups stay with their data.** Each study's `PROTOCOL.md` and `RESULTS.md` sit in
  `experiments/<study>/` next to its raw traces, configs and hashes. The index is
  [experiments/README.md](../experiments/README.md).
- **Component documentation stays with its code.** Each package has a README next to the code it
  describes.

Everything else is in this folder.

## In this folder

| Folder | Contents |
|---|---|
| [literature/](literature/) | [related-work.md](literature/related-work.md): about 60 papers, which of our results are new and which reproduce published findings. [related-work-addendum.md](literature/related-work-addendum.md): papers on the questions the experiments left open. [novelty-check-sum-of-squares.md](literature/novelty-check-sum-of-squares.md): the literature check behind the Sum-of-Squares and FWSS novelty claims. [fetch_papers.py](literature/fetch_papers.py) re-downloads the reviewed papers into a git-ignored folder. |
| [logs/](logs/) | [OVERNIGHT-2026-10-03.md](logs/OVERNIGHT-2026-10-03.md): the coordination log, with decisions, approvals, incidents and spend. |
| [reviews/](reviews/README.md) | Independent referee-style reviews of three studies: recomputation, protocol adherence, claims. |

## Elsewhere in the repository

| Document | Contents |
|---|---|
| [README.md](../README.md) | Overview, quick start, key findings, and how we chose the defaults |
| [experiments/README.md](../experiments/README.md) | The studies on `main`, and the archived ones |
| [autoresearch/README.md](../autoresearch/README.md), [autoresearch/LOOP.md](../autoresearch/LOOP.md) | The one-command loop and the integrity gate; LOOP.md holds the design decisions and build log |
| [tournament/README.md](../tournament/README.md) | Whole-framework comparison at equal dollar budgets |
| [falsify/README.md](../falsify/README.md) | FunSearch's published bin-packing heuristics, the reference code of the headline studies |
| [problems/README.md](../problems/README.md) | The problem contract, and one `problem.md` per problem |
| [runs/README.md](../runs/README.md) | The committed demo runs and the live-demo plan |

## Not in `main`

Tag [`archive/full-research-2026-10-04`](https://github.com/swedishScienceMafia/swedishScienceMafia/tree/archive/full-research-2026-10-04)
holds the complete research record from before `main` was slimmed on 4 October:
- the studies of features we dropped (counterexample replay and gates, the Strategist controller, prompt
  memory, idea triage), with their code;
- the superseded design plans.

Research papers are not on `main` or in the archive tags: the papers supplied with the track and its
brief, the literature-review downloads, the experiment review PDF, and our own paper drafts, outlines
and pitch draft are kept by the team outside GitHub.

Other archived work is in tags `archive/all-approaches` (the four-approach live campaign) and
`archive/refresh-review-pdf`.
