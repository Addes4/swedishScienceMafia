# Pitch and submission draft (team-internal)

Drafted 3 October 2026, evening, before the overnight results. Fill the `[RESULT: …]` slots
after the 10:30 code freeze, then decide whether to delete this file before submitting.
Claims follow [context/related-work.md](../context/related-work.md): each one says what is new
and what independently reproduces published work.

## Short description (for both submission forms)

> An autoresearch framework that checks its own claims. Candidate algorithms are proposed by
> LLMs, ranked before any code is written, and sent to the right model. Every claimed
> improvement must also survive the inputs where earlier candidates failed. A controller learns
> when to edit, rewrite or restart. Winners are reduced to the shortest rule with the same
> measured quality. Every experiment has a pre-written protocol, matched budgets and a fresh
> audit. Tested on online bin packing and four problems from Tao et al.'s repository.
> [RESULT: one-line headline from the tournament.]

## Video (max 4 minutes; the brief asks for these four things)

| Time | Brief asks | Content |
|---|---|---|
| 0:00–0:40 | What the system does | The loop: propose → rank → implement → gate → keep → choose the next move → explain. Name the failure each part prevents: promoting regressions, wasting budget on bad ideas or the wrong move, opaque winners, evaluator exploits. |
| 0:40–1:50 | What is novel | (1) Counterexample gates tested against score-only and random-input gates at matched budgets. (2) A strategy controller with timing-shuffled and counterfactual-fork controls, which tell real adaptation from luck. (3) Automated simplification with ablation CIs. (4) Triage with randomised swaps, so the ranker's value is measured, not assumed. |
| 1:50–3:10 | What we tested it on | [RESULT: tournament, best score against dollars per arm with seeds and CIs, with sampling baselines.] Bin packing: nothing beat best-fit at 80 items, consistent with Herrmann & Pallez and Sim et al.; [RESULT: bp-ceiling, long Weibull instances]. Strategist: beats fixed move mixes; timing matters on Heilbronn (130/0/70 seeds). Simplify: the 11-term "winner" is exactly best-fit. |
| 3:10–4:00 | What we would do next | Evolve instance generators instead of single counterexamples (RAISE, ASRO). Use measured LLM token costs in Strategist. Fine-tune the ranker on our own run logs (Wen et al. show fine-tuning is what makes outcome prediction work). |

## Live demo (1:30 in round 1)

1. `python3 -m strategist.demo --benchmark labs --seed 1000`: a narrated run, switch by switch, with
   the controller's reasons from `Adaptive.explain`.
2. Open `experiments/report.html`: a counterexample from the archive, and a candidate the gate
   rejected.
3. [RESULT: the tournament report or a triage notebook showing one idea's path: proposal → rank →
   model → gate → score.]

## Track 1 criteria → our evidence

| Criterion | Evidence |
|---|---|
| Novelty | The controls and gates in the novelty row above, none of which appeared in the ~60 papers we reviewed |
| Performance | [RESULT: tournament]. Falsify v2: drift away from best-fit 0.000725 vs 0.023 excess bins (CI of the difference [−0.0378, −0.0108]). V3 gate beats score-only promotion. |
| Interpretability | Simplify; every run has a protocol, config, traces and source hashes; Strategist explains each switch |
| Research efficiency | Triage spends strong models on favourites; gates stop budget being spent on false improvements; Strategist charges moves by cost |

Pitch the checks as efficiency and performance mechanisms ("the loop stops paying for fake
progress"), not as safety. Otherwise it reads as a Track 2 project.

## Likely questions, with answers

- **"Nothing beat best-fit, so does it work?"** At 80 items nothing published beats best-fit
  either: FunSearch's heuristic is worse below about 90 items (Herrmann & Pallez 2025), and
  best-fit ranks first across 6,064 instances (Sim et al. 2025). Our gates did what they were
  built for: they stopped the search drifting away from the best rule. [RESULT: bp-ceiling.]
- **"Isn't adaptive restarting already in AdaEvolve and PACEvolve?"** Yes. What's new is the
  cost-weighted leave rule, and above all the controls that separate timing from move mix. None
  of those papers has them, and our results show timing matters on Heilbronn but not on LABS.
- **"Why not just sample many programs?"** Gideoni et al. (2026) show simple sampling is
  competitive, so we include it as a baseline. [RESULT: how our arms compare with it.]
- **"How do you know a record isn't an exploit?"** Separate process, credentials stripped,
  hidden instances, and an independent 1e-12 re-check. HASE (2026) documented exactly the
  tolerance exploit this catches. [RESULT: gate-redteam catch rate.]
- **"Does the ranker beat random?"** [RESULT: idea-table AUC with CI against the random ranker.]
  Off-the-shelf LLMs are near chance at this task (Wen et al. 2025), so a random-ranker
  baseline is required.

## Submission checklist

- [ ] Email admin@algorithmdiscovery.org: team name, repo URL, short description, video link
      (Google Drive, ≤ 4 min)
- [ ] Hackathon form: 2-minute demo, repo link, short description (deadline 14:45)
- [ ] Root README results table updated with the overnight results and links
- [ ] Repo has install/run instructions, design explanation, integrated benchmarks (the brief's four requirements)
