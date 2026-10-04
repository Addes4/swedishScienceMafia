# Paper B outline: checking the claims of autoresearch loops

Status: outline, 3 October 2026, updated at 23:10 with every finished overnight run. Evidence
comes from:
- on main: `experiments/RESULTS.md`, `experiments/gate-v3/RESULTS.md`,
  `experiments/soft-gate-v4/RESULTS.md`, `experiments/simplify-v1/EXPERIMENT.md`;
- the RESULTS.md on branches `exp/gate-redteam`, `exp/memory-ablation`, `exp/bp-ceiling`,
  `exp/idea-table` and `exp/tournament`.

Related work is in [docs/literature/related-work.md](../../literature/related-work.md).

## Working title

*Is the Loop Fooling Itself? Executable Controls for the Claims Autoresearch Systems Make*

## Thesis

An algorithm-discovery loop makes four kinds of claim, and usually checks none of them:

1. this candidate is better than the one it replaces;
2. the search strategy's adaptation helped;
3. the discovered algorithm is new and does something meaningful;
4. this score beats a known record.

For each claim we give a control that can be run, and we show on bin packing and on problems
from Georgiev, Gómez-Serrano, Tao and Wagner (2025) that each control catches a real failure.
The paper is about measurement, not a new optimiser. It sits next to Gupta et al., Oved et al.
and Gideoni et al. (2026), which show evaluation practice in this field is fragile.

## Claims, controls and evidence (the paper's central table)

| Claim | Failure we observed | Control | Evidence | Status |
|---|---|---|---|---|
| "Better than its parent" | A Codex revision went from 1 win / 0 losses on 1,000 cases to 3 / 14 on 10,000 fresh cases | Counterexample replay and promotion gates; fresh audits | Replay cut drift away from best-fit: 0.000725 vs 0.023 excess bins, difference −0.0223 [−0.0378, −0.0108]. Gate vs score-only: −0.0022 [−0.0041, −0.0006]; vs a random gate: inconclusive. Soft gate with validation kept 15/16 beneficial proposals and blocked 328/599 harmful ones (strict: 14/16, 270/599). | Done (no LLM) |
| "Better", with an LLM proposing | Without memory, most Haiku proposals were harmful (0.803 in the confirmatory study) | Memory of executable counterexamples vs prose vs none | Confirmatory (Weibull 5k, 10 seeds × 3 arms, 900 calls): no evidence executable memory helps the audited policy; all primary intervals include 0. Memory cut harmful proposals (0.803 / 0.202 / 0.147 for none, prose, executable) mainly by inducing no-ops (0.133 / 0.650 / 0.815). Not token-matched. | Done: null on the primary endpoint |
| "This idea is promising" | Off-the-shelf models predict research outcomes at chance (Wen et al.) | Rank ideas before code, then replay rankers and routing policies offline on a table of every idea implemented by every model | idea-table (62 of 114 ideas complete): Opus 62/62, Sonnet 60/62, Haiku 10/62 improved, so the implementer decided success. AUC: Jev 0.484, Codex 0.600 (the only one clearly above random). Ranked tiers did not beat random tiers; uniform Sonnet was best per dollar. | Partial (credit ran out); null for triage |
| "The adaptation helped" | Many switches were premature (48% on LABS in v1) | Timing-shuffled replay; counterfactual forks | See Paper A: timing matters on Heilbronn and NK, not on LABS; the fix cut premature switches to 21% | Done (proxy moves) |
| "We discovered a new algorithm" | The 11-term evolved "winner" is exactly best-fit, and 8 of its 11 terms are inert | Automated simplification, ablation CIs, witness search | 35/43 candidates reduce to best-fit. Two-sided check: 17/43 are truly equivalent, while 26/43 were repaired rather than explained (a caveat we report). | Done (weight vectors only) |
| "Beats the record" | HASE (2026) documents tolerance exploits on circle packing | Separate process, hidden instances, strict 1e-12 re-check, margin vs n × tolerance | Red team: 68 attempts, none gained a material unearned score. 18/28 hand-made rejected (10 neutralised), 28/40 LLM-written rejected (12 honest). Residual: about 3e-10, below the record. | Done |
| "Our framework works" | Simple sampling matches complex search (Gideoni et al. 2026) | Matched-dollar tournament with independent sampling and greedy best-of-N baselines, 4 seeds, P(A > B) | tournament-v1 stopped 13.6 minutes in (credit exhausted); 17 of 60 runs complete. At a common low-spend checkpoint, lean (+0.233) and independent sampling (+0.209) led ShinkaEvolve in area under the curve, and triage trailed (−0.156). Final scores did not differ. Two of three problems saturate within 1–3 calls. | **Partial; not budget-matched** |

## Contributions

1. A taxonomy of the four claims an autoresearch loop makes, each with a control that can run
   inside the loop, and the cost of that control in evaluations.
2. Counterexample promotion gates compared with score-only *and random-input* gates at matched
   budgets. RAISE and ASRO use adversarial instances to train the search; we use them to decide
   promotion, and include the random-input gate as a control.
3. Automated simplification of discovered heuristics, which independently reproduces Herrmann &
   Pallez's manual finding, and the observation that a one-sided tolerance repairs a candidate
   rather than explaining it.
4. A red-team evaluation of an integrity gate with hand-made and LLM-written exploits.
5. Case studies, null results included, reported as replications of published findings.

## What is missing (in priority order)

| # | Gap | Why it matters | Source |
|---|---|---|---|
| 1 | **A complete, budget-matched tournament** on problems that do not saturate (sum_difference, plus harder instances) | v1 is partial and its main comparison is post hoc; reviewers will discount it | Rerun with credit: about $66 for v1's grid |
| 2 | ~~A regime with headroom~~ **Resolved:** bp-ceiling found it. 5,000-item Weibull: the linear rule beats best-fit by 1.18 pp, and with a new-bin option by 3.28 pp, level with FunSearch's code. | - | Rerun the gates (Falsify v2–v4) in this regime |
| 3 | ~~Memory-ablation confirmatory~~ **Done** (null; memory induces no-ops). Remaining: token-matched memory, and Karimi et al.'s distilled diagnoses as a fourth arm | The null is confounded by unequal memory size | New run, about $3 per 30 runs |
| 3b | **idea-table replicates:** implement a subset twice to measure the implementation lottery (Ning et al.) | The table's labels come from single implementations | Queued but never run |
| 4 | **Power for gate vs random gate** | The key comparison is inconclusive at 40 seeds. Either power it or state it as a bound. | New run, CPU only |
| 5 | **Simplify for code**, not just weight vectors: AST-level removal of statements and constants, with the same two-sided tolerance | Evolved programs are code. Pelleriti et al. find most edits are constant tuning. | New work |
| 6 | **Overhead of each control** (extra evaluations, tokens) | Answers "is checking worth it?" in research-efficiency terms | From existing logs |
| 7 | **An adversarial-generator comparison**: counterexample archive vs an ASRO- or RAISE-style generator | The obvious alternative design | New run |

## Section plan

1. **Introduction.** Three short stories open the paper: the 1/0 → 3/14 revision, the 11-term
   "winner" that is best-fit, and a tolerance exploit. Then the four claims, and the contributions.
2. **Related work.**
   - Evaluation critiques: Gideoni, Oved, Gupta, Ferreira/Hutter.
   - Adaptive data reuse: the reusable holdout, the Ladder.
   - Adversarial instances: MetaOpt, RAISE, ASRO, Karimi et al.
   - Simplification and bloat: Herrmann & Pallez, Pelleriti et al., Langdon & Poli.
   - Reward hacking: HASE, ImpossibleBench, METR, Luo et al. 2025.
3. **Framework.** The loop, the four claims and their controls, and what each control costs.
   Design rules: matched budgets, fresh audits, pre-registration, provenance.
4. **Case study 1: online bin packing.**
   - Gates (v2–v4).
   - LLM memory.
   - Simplification.
   - Why 80 items has no headroom (Herrmann & Pallez; Sim et al.), and the regime with headroom
     (gap 2).
5. **Case study 2: problems from Georgiev, Gómez-Serrano, Tao and Wagner (2025).** The tournament
   (gap 1), record flags, and the strict re-check in use.
6. **Case study 3: auditing a strategy controller.** A summary of Paper A's controls, or a pointer
   to it if both are submitted.
7. **Red-teaming the integrity gate.**
8. **Discussion.**
   - Null results as replications.
   - What the controls cannot catch: a gate is not a hardened sandbox, and counterexamples prove
     regressions, not improvements (Sim et al.).
   - Costs.
9. **Limitations.** Synthetic families, proxy moves in case study 3, Simplify limited to weight
   vectors, the gate vs random gate comparison underpowered.

**Figures:**
1. The loop with the four controls.
2. The claims table above.
3. Drift curves by arm (Falsify v2).
4. Gate confusion counts (beneficial and harmful proposals kept or blocked).
5. Simplification map (term counts before and after).
6. Tournament best score against dollars (gap 1).

## Likely reviewer objections

- **"Nothing beats best-fit, so what was discovered?"** The paper is about checking claims, not
  about beating best-fit. The 80-item null result matches two published studies. bp-ceiling
  found the regime where improvement is possible (5,000-item Weibull), and showed that a linear
  rule with a new-bin option reaches FunSearch's level there.
- **"The gates are no better than a random gate."** Report it honestly: they beat score-only
  promotion, and the comparison with a random gate is inconclusive and needs power (gap 4).
- **"Four contributions with no single result."** That is the risk of this paper. If the
  tournament result is weak, narrow the paper to claims 1 and 4 (promotion and records) and move
  Strategist into Paper A.

## Venues (check current deadlines; none were verified)

- A NeurIPS or ICLR workshop on AI for science, agents or evaluation. This is the best fit.
- TMLR, which takes submissions at any time.
- EvoApplications, if narrowed to the bin-packing case study.

## What the overnight results mean for this paper

Most claims did not survive checking:
- memory did not improve outcomes;
- ranking ideas did not beat random tiers;
- 80-item bin packing has no headroom;
- simple loops matched or led the elaborate frameworks at low spend.

That is a coherent paper ("what checking reveals") if each null is reported with its control and
power. It is weaker as a framework paper. Lead with the controls and the nulls they exposed, not
with the framework.

## Order of work

1. Rerun the tournament budget-matched (gap 1), and rerun the gates in the Weibull regime (gap 2).
2. Run gaps 3, 3b and 4 (token-matched memory, idea replicates, gate power).
3. Decide the scope:
   - Full paper if the reruns give clear results.
   - Otherwise narrow to promotion and records, with the nulls as case studies.
4. Search the literature again before writing.
