# Pitch and submission draft (team-internal)

Drafted 3 October 2026 at 20:05; result slots filled at 21:46 and 23:10 from each experiment's
RESULTS.md. The coordinating session owns the root README and the final pitch; this draft is
input for it. Decide whether to delete this file before submitting.
Claims follow [docs/literature/related-work.md](../literature/related-work.md): each one says what is new
and what independently reproduces published work.

## Short description (for both submission forms)

> An autoresearch framework that checks its own claims. Candidate algorithms are proposed by
> LLMs, ranked before any code is written, and sent to the right model. Every claimed
> improvement must also survive the inputs where earlier candidates failed. A controller learns
> when to edit, rewrite or restart. Winners are reduced to the shortest rule with the same
> measured quality. Every experiment has a pre-written protocol, matched budgets and a fresh
> audit. Tested on online bin packing and four problems from Tao et al.'s repository.
> On the evidence: in a bin-packing regime with headroom, a linear rule found by search matches
> FunSearch's evolved code. At low spend, simple loops beat a published framework. And the checks
> caught what would otherwise have been claimed: memory that does not help, an idea ranker at
> chance, an "evolved" heuristic that is best-fit.

## Video (max 4 minutes; the brief asks for these four things)

| Time | Brief asks | Content |
|---|---|---|
| 0:00–0:40 | What the system does | The loop: propose → rank → implement → gate → keep → choose the next move → explain. Name the failure each part prevents: promoting regressions, wasting budget on bad ideas or the wrong move, opaque winners, evaluator exploits. |
| 0:40–1:50 | What is novel | (1) Counterexample gates tested against score-only and random-input gates at matched budgets. (2) A strategy controller with timing-shuffled and counterfactual-fork controls, which tell real adaptation from luck. (3) Automated simplification with ablation CIs. (4) Triage with randomised swaps, so the ranker's value is measured, not assumed. |
| 1:50–3:10 | What we tested it on | Tournament (partial: the API credit ran out after 17 of 60 runs): at a common low-spend checkpoint, our plain loop (+0.233 area under the curve, CI [0.096, 0.386]) and independent sampling (+0.209) led ShinkaEvolve; triage trailed (−0.156); final scores tied, and two problems saturate within 1–3 calls. Bin packing: nothing beats best-fit at 80 items, consistent with Herrmann & Pallez and Sim et al. On 5,000-item Weibull our 21-weight linear rule reaches −3.28 pp vs best-fit, level with FunSearch's code (−3.33), after reproducing FunSearch's published numbers exactly. Memory (closed-loop Haiku, 10 seeds): executable counterexamples did not improve the audited policy; memory cut harmful proposals mainly by making the model propose no-ops. Idea table: the implementing model decided success (Opus 62/62, Haiku 10/62); rankers were near chance and ranked triage did not beat random tiers. Strategist v2 (200 seeds): v1's fixes beat v1 on LABS (+0.137 merit factor, CI [0.043, 0.236]) and NK, mostly through gating crossover, and cut premature switches on LABS from 48% to 21%. A patience rule tuned on dev seeds still wins on LABS. Gate red team: 28 hand-made and 40 LLM-written exploits, none gained a material unearned score. Simplify: the 11-term "winner" is exactly best-fit. |
| 3:10–4:00 | What we would do next | Evolve instance generators instead of single counterexamples (RAISE, ASRO). Use measured LLM token costs in Strategist. Fine-tune the ranker on our own run logs (Wen et al. show fine-tuning is what makes outcome prediction work). |

## Live demo (1:30 in round 1)

> Superseded at 23:55 on 3 October by the one-command demo: plan in
> [runs/README.md](../../runs/README.md#live-demo-plan-1-minute-30). The short description and the video
> outline below do not mention `python -m autoresearch.loop` yet. The steps below are the earlier plan.

1. `python3 -m strategist.demo --benchmark labs --seed 1000`: a narrated run, switch by switch, with
   the controller's reasons from `Adaptive.explain`.
2. Open `experiments/report.html`: a counterexample from the archive, and a candidate the gate
   rejected.
3. The bp-ceiling figure: the linear rule with a new-bin option against FunSearch's code and
   best-fit across instance lengths.

## Track 1 criteria → our evidence

| Criterion | Evidence |
|---|---|
| Novelty | The controls and gates in the novelty row above, none of which appeared in the ~60 papers we reviewed |
| Performance | Weibull 5k: linear rule −3.28 pp vs best-fit, level with FunSearch's code. Tournament (partial): plain loop and independent sampling led ShinkaEvolve at low spend. Falsify v2: drift away from best-fit 0.000725 vs 0.023 excess bins (CI of the difference [−0.0378, −0.0108]). V3 gate beats score-only promotion. |
| Interpretability | Simplify; every run has a protocol, config, traces and source hashes; Strategist explains each switch |
| Research efficiency | Triage spends strong models on favourites; gates stop budget being spent on false improvements; Strategist charges moves by cost |

Pitch the checks as efficiency and performance mechanisms ("the loop stops paying for fake
progress"), not as safety. Otherwise it reads as a Track 2 project.

## Likely questions, with answers

- **"Nothing beat best-fit, so does it work?"** At 80 items nothing published beats best-fit
  either: FunSearch's heuristic is worse below about 90 items (Herrmann & Pallez 2025), and
  best-fit ranks first across 6,064 instances (Sim et al. 2025). Our gates did what they were
  built for: they stopped the search drifting away from the best rule. bp-ceiling showed why: at
  80 items there is almost no headroom, while on 5,000-item Weibull our linear rule reaches
  FunSearch's level once it may open a new bin.
- **"Isn't adaptive restarting already in AdaEvolve and PACEvolve?"** Yes. What's new is the
  cost-weighted leave rule, and above all the controls that separate timing from move mix. None
  of those papers has them, and our results show timing matters on Heilbronn but not on LABS.
  The forks also showed the controller left improving lines too early. v2 required more evidence
  and gated crossover, and premature switches on LABS fell from 48% to 21% (seed-clustered CI of
  the difference [−35, −17] points). Like Gupta et al. (2026), we find no universal winner: a
  tuned patience rule still beats v2 on LABS.
- **"Why not just sample many programs?"** Gideoni et al. (2026) show simple sampling is
  competitive, so we include it as a baseline. In our partial tournament it led ShinkaEvolve at
  low spend (+0.209 area), close to our plain loop (+0.233).
- **"How do you know a record isn't an exploit?"** Separate process, credentials stripped,
  hidden instances, and an independent 1e-12 re-check. HASE (2026) documented exactly the
  tolerance exploit this catches. We red-teamed it.
  - Of 28 hand-made exploits, 18 were rejected and 10 were scored as the valid programs they
    really were.
  - Of 40 live Sonnet and Haiku attempts, 28 were rejected and 12 ran as honest, weak programs.
  - The only leak was 2 sub-tolerance overlaps scoring below the record, worth about 3e-10,
    which is bounded by n × tolerance.
  - It is not a hardened security sandbox: code can still run inside the child process, but it
    cannot change the reported score.
- **"Does the ranker beat random?"** Mostly no.
  - AUC: Jev 0.484, Claude Opus 0.564, Codex 0.600; only Codex is clearly above random
    (+0.102 [0.028, 0.178]).
  - Ranked triage did not beat random tiers, because the implementing model decided success.
  - Off-the-shelf LLMs are near chance at this task (Wen et al. 2025), so we expected this. Our
    table of every idea implemented by every model is what let us measure it.

## Submission checklist

- [ ] Email admin@algorithmdiscovery.org: team name, repo URL, short description, video link
      (Google Drive, ≤ 4 min)
- [ ] Hackathon form: 2-minute demo, repo link, short description (deadline 14:45)
- [ ] Root README results table updated with the overnight results and links
- [ ] Repo has install/run instructions, design explanation, integrated benchmarks (the brief's four requirements)
