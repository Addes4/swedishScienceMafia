# PLAN — Track 1, Task 1: Autoresearch Framework (built on ShinkaEvolve)

> Working plan for the AI x Science Hackathon (London, Oct 3–4 2026).
> Any agent or teammate picking this up: read this whole file first.
> Source material lives in `context/` (`website.md` = hackathon rules, `context/Track 1 papers/` = brief + papers).

## 1. The brief (from `context/Track 1 papers/Build Your Own Algorithm Autoresearch Framework (3).pdf`)

Build a **reusable system that automatically discovers, tests and improves algorithms** — not a solver hard-coded to one benchmark. "The goal is not simply to discover a good algorithm. The goal is to build a system that can discover good algorithms."

**Judging (track, organised by C3 + AIDDA):**
1. **Novelty & inventiveness** — how original is the approach to automated research (idea generation, experiments, learning from results, agent coordination, search).
2. **Performance** — demonstrated improvement on benchmarks. Judges *also* credit mechanisms: learning from previous experiments, selecting promising directions, **avoiding repeating unproductive searches**.
3. **Interpretability & ease of use** — easy to understand, run, inspect discoveries, reproduce, and adapt to a new problem.
4. **Research efficiency** — compute, experimental runs and LLM tokens per unit of progress.

**Hackathon-wide judging** (`context/website.md`): Technicality, Creativity, Usefulness, Demo, Track alignment — 20 pts each.

**Deliverables**
- Track: email `admin@algorithmdiscovery.org` with team name, repo URL, short description, link to **≤4 min video** (Google Drive).
- Repo must contain: source code, install/run instructions, high-level design explanation, examples of integrated benchmarks.
- Video covers: what the system does, what's novel, problems tested, what we'd do next.
- Hackathon: 2-min demo, repo link, short description. **Deadline Sun Oct 4, 14:45 BST.** Round 1 pitch = 1:30 pitch + 1:30 live demo + 2:00 Q&A.
- Rules: build during the event; open-source libs allowed **if credited** (credit ShinkaEvolve, Apache-2.0).

Suggested benchmark source: Tao et al. / Georgiev et al. (2025) "Mathematical exploration and discovery at scale" problem repository.

## 2. Core idea

**Pitch:** *"Shinka searches programs; we make it do research. Ideas compete before they cost compute, failures become memory, and every score is independently verified."*

We use ShinkaEvolve as the evolutionary engine and add a research layer drawn from the other papers in `context/Track 1 papers/`.

### What ShinkaEvolve already gives us (do NOT pitch these as ours)
Verified against `context/Track 1 papers/ShinkaEvolve.pdf` (Lange, Imajuku, Cetin — Sakana AI, arXiv 2509.19349; code: https://github.com/SakanaAI/ShinkaEvolve):
- Parent + inspiration sampling balancing exploration/exploitation; fixed-size archive; island subpopulations with migration
- Novelty rejection sampling: code-embedding similarity + LLM-as-novelty-judge
- Bandit-based LLM ensemble selection
- Meta-scratchpad: every T generations, summarises **successful** solutions into insights/recommendations appended to the mutation prompt
- Diff, full-rewrite and crossover mutations; `EVOLVE-BLOCK-START` / `EVOLVE-BLOCK-END` markers for immutable code
- Evaluator can return textual feedback, which is stored in the archive and shown to later mutations
- New SOTA circle packing (n=26) with only 150 samples

**Gaps Shinka itself admits (Limitations section) — our hooks:**
- "Fixed configurations with limited automatic control over exploration-exploitation balance" → behavioural niches (D) and idea tournament (A) adapt where effort goes.
- "Task specification requires manual human expertise for objective functions and evaluation" → our problem contract + integrity verifier (C) makes evaluators harder to get wrong / exploit.
- Scratchpad learns from successes only → failure memory (B).
- The evaluator is trusted, and its textual feedback goes straight back to the LLM → integrity gate (C) and generic rejection (C') must make sure detector reasons never leak into that feedback channel.

## 3. Architecture

```
            ┌──────────────── Research memory ◄──────────────┐
            │  (Shinka scratchpad + failure lessons)          │
            ▼                                                 │
 1. Select parent      Shinka sampler + behavioural niches (FunSearch)
            ▼
 2. Propose ideas      LLM writes K short NL hypotheses — no code yet
            ▼
 3. Idea tournament    cheap pairwise LLM judging, Elo   (Co-Scientist)
            ▼          memory check: "already tried & failed?" → drop
 4. Implement winner   Shinka diff mutation, EVOLVE-block only (FunSearch)
            ▼
 5. Cascade eval       small/fast instances first; fail → stop
            ▼
 6. Integrity gate     independent recompute + hidden cases (Reward-hacking paper)
            ▼          hack → quarantine + generic rejection only
 7. Archive + reflect  score profile → niche; analyst writes a lesson ───┘
            ▼
 8. Final report       auto-generated research report    (AI Scientist)
```

### Components and provenance

| # | Component | Inspired by | What it does | Criterion |
|---|---|---|---|---|
| A | **Idea tournament** | Co-Scientist (tournament/Elo, reflection) | Generate K text hypotheses per step, rank pairwise cheaply, implement only top-1/2. Bad ideas die for ~hundreds of tokens. | Efficiency, Novelty |
| B | **Failure memory** | Co-Scientist meta-review agent | Structured lessons `{hypothesis, change, result, why}` from *failures too*; ideas matching a known dead end are filtered before implementation. Extends Shinka's success-only scratchpad. | "Avoid repeating unproductive searches" |
| C | **Integrity gate** | Reward Hacking Challenges (Huang et al. 2026) | Metric computed in a separate process the candidate can't touch; independent re-verification (e.g. exact geometric checks, no tolerance abuse); hidden held-out instances; static checks (no file/network/evaluator access). Hacks are quarantined and logged. | Trust, Demo, Technicality |
| C' | **Generic rejection feedback** | Same paper: evasion 40.5% with detailed feedback vs 20.3% generic | The generator only hears "rejected", never the detector's reasons. | Design point for pitch |
| D | **Behavioural niches** | FunSearch (signature clustering across inputs) | Cluster programs by per-instance score vector, not code similarity; sample across niches. | Performance |
| E | **Skeleton / evolve-block only** | FunSearch | Evolve only the critical function; keeps discoveries short & readable. (Shinka supports EVOLVE-BLOCK markers — verify.) | Interpretability |
| F | **Research report** | The AI Scientist | End-of-run markdown: what was tried, what worked and why, lineage of the best program, final algorithm explained, hacks caught, token/eval spend. | Interpretability, Demo |
| G | *(stretch)* Literature grounding | The AI Scientist (Semantic Scholar novelty check) | Seed idea generation with known techniques for the problem (arXiv/OpenAlex). | Novelty |

Explicitly **not** doing: full Co-Scientist multi-agent system (too token-hungry), AI Scientist paper writing.

### Reusability contract
Adding a new problem = one folder:
```
problems/<name>/
  initial.py        # seed program with EVOLVE-BLOCK markers
  evaluate.py       # public fast eval (cascade stage 1)
  verify.py         # independent integrity check + hidden instances (never shown to LLM)
  problem.md        # task description for prompts
```

## 4. Benchmarks
1. **Circle packing, n=26** (maximise sum of radii in unit square; AlphaEvolve ≈ 2.635). Main showcase: fast, visual, known target, classic hack surface (overlap within float tolerance).
2. **Second domain** to prove generality — pick one: online bin packing (FunSearch, OR heuristic) or another Tao et al. problem (e.g. an autocorrelation inequality).

## 5. Evidence plan (ablations)
Each component (A, B, C, D) has an on/off flag. Same budget (e.g. 100 LLM calls), several seeds, circle packing:
1. Vanilla Shinka
2. + Idea tournament (A)
3. + Failure memory (B)
4. Full system

Plots: best score vs LLM calls, best score vs tokens, evals wasted on rejected candidates. Integrity: # hacks caught, with one concrete example shown in the demo. Run sweeps on Modal overnight.

## 6. Build order (each step leaves a demoable state)
1. **Baseline** — stock ShinkaEvolve running on circle packing; record baseline curve. *(Sat morning)*
2. **Integrity gate (C, C')** — self-contained, strongest demo story.
3. **Idea tournament + memory check (A, B)** — the headline novelty.
4. **Lessons + research report (B, F).**
5. *(stretch)* Behavioural niches (D), second benchmark, literature grounding (G).
6. **Ablation runs on Modal**, dashboard/report page, README, video. *(Sat night → Sun morning)*

Steps 1–3 alone are a complete submission.

**Parallel split for 3–4 people:** (i) integrity gate + problem contract, (ii) tournament + memory inside the Shinka loop, (iii) benchmarks + ablation runner + Modal, (iv) report/dashboard + README + video.

## 7. Open questions / to verify
- [ ] Read current ShinkaEvolve code (`SakanaAI/ShinkaEvolve`; paper features are verified, code may have moved on): where to hook (a) pre-mutation idea stage, (b) custom evaluator/verifier, (c) scratchpad/meta prompts. Does it already have any of A–G?
- [ ] Fork vs pip-install + wrap? (Prefer wrapping/subclassing so our contribution is clearly separable.)
- [ ] LLM provider: Claude API ($200 credits/person) vs Gemini (Antigravity). Doesn't affect design; Shinka supports multiple.
- [ ] Compute: Modal ($150/person) for parallel evals and ablation sweeps.
- [ ] Choose second benchmark.
- [ ] Team roles.

## 8. Resources
- Papers in `context/Track 1 papers/`: ShinkaEvolve, FunSearch ("Mathematical discoveries with LLMs.pdf"), Co-Scientist, The AI Scientist, Reward Hacking Challenges, track brief. Also present but **not yet read for this plan**: AlphaEvolve, "MATHEMATICAL EXPLORATION AND DISCOVERY AT SCALE" (Georgiev/Tao et al. — benchmark source), "LLM's from hypothesis to discovery".
- Track support: Discord https://discord.gg/ZN36RsFPs, admin@algorithmdiscovery.org
