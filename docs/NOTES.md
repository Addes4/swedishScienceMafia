# Mosa: notes for the team

Written at about 06:00 on Sunday 2026-10-04 (deadline 14:45). This is the handoff: what works, what we learned, how the
code is organised, how it generalizes, and what makes this a strong Track 1 entry.

## Status

- **Branch `mosa`** is a clean orphan branch with an MVP that works end to end:
  - LLM researchers (through the `codex` CLI) write strategies;
  - strategies are evaluated on Modal or locally, at equal budget across sizes × seeds;
  - candidate records are verified independently;
  - everything goes into an append-only notebook that the workbench shows live or replays.
- **Five verified new best-known packings:** n = 88, 123, 126, 129, 130. See the README table; the packings and the night's notebooks are on the branch `results-2026-10-04`.
- **Validated against the prototype.** Mosa reproduces the n = 88 discovery:
  - the compiled relaxation and the polish give the same sides as the prototype to 1e-15;
  - the same strategy and seed give the same record locally (9.8877007312) and on Modal (9.886746030783).
- **Workspaces:** a workspace is a problem, its instances and a shared memory (best solution per instance, the ideas that broke records). Sessions append to it; researchers continue across sessions; running an idea on more instances adds results to that idea. The `mosa` branch holds only the code and reference data; results live on `results-2026-10-04`.

## Positioning: what Mosa is, and is not

This is the core of the pitch, and it should guide every product decision.

- **Not code evolution.** AlphaEvolve, OpenEvolve and ShinkaEvolve use the LLM as a mutation operator on a program, with selection on a fitness score over many edits. Mosa uses the LLM as a researcher: it proposes a *method*, with its source field and a hypothesis, and tests it on a family of instances × seeds at equal budget. It reads graded evidence back (gap, near miss, initial gap, failures) and decides whether to refine, combine or replace. A lab takes 12–20 model calls; the compute goes into fair testing.
- **Not a numerical method.** Annealing, basin hopping, relaxation and SQP polish are the trusted *tools*. The model chooses and invents what to do with them. Our own fixed-operator searches on the same tools found nothing for n = 51–89 or 101–200, while LLM-designed strategies broke four records.
- **What is novel:**
  - the level of abstraction: strategies as reusable algorithms with stated hypotheses;
  - analogy across fields as the source of ideas;
  - evidence-shaped feedback, especially near misses;
  - a strict trust boundary, so model code can only propose candidates;
  - memory at three timescales (round history, library, notebook);
  - transfer of discovered strategies across instances.
- **Track 1 fit:** the discovered artifacts are algorithms, validated by verified new results on a benchmark studied since 1979.

**How this shapes the product:**
- **UI:**
  - Researchers are rows with a history, not a population.
  - Every idea shows the field it came from and the researcher's hypothesis, and its outcome as one graded sentence, not a score curve.
  - The lab header says that each idea was tested on N sizes × seeds, because multi-instance testing is the point.
  - Transfer is a first-class action ("Run on more sizes"), and discoveries found by a rerun say so.
  - Every discovery shows how it was verified and which idea found it.
- **Architecture:**
  - The trust boundary is in the code. `mosa/domain.py` holds the trusted relaxation, polish and verifier; `mosa/sandbox.py` runs the model's code, which can only return candidates.
  - The evaluator (`evaluate.py`) is defined over instance families and seeds.
  - The notebook keeps the reasoning (prompt, answer, outcome) next to the numbers.
- **What not to add:** fitness leaderboards, mutation counts, score curves. These describe evolution, not research, and they bury the ideas.

## What worked: general methods, with the evidence

1. **The LLM as a research strategist, not a solver.** Asked for individual moves, the LLM was no better than random. Asked for a *search strategy* (code for `initialize` and `vary` in a fixed evolutionary template), it produced the strategies behind four of the five records.
2. **Analogies across fields, on purpose.** The prompt asks for "a method imported from another field whose landscapes share these properties", plus the source of that method and why its assumptions fit.
   - Proposals included USPEX heredity (crystal structure prediction), AIRSS (random structure search), Rosetta fragment assembly (protein folding), large-neighbourhood search (operations research), grain growth and dislocation slip (metallurgy), and cut-and-splice (atomic clusters).
   - The n = 123 record came from large-neighbourhood search with grain nucleation. The n = 129 and 130 records came from cut-and-splice.
3. **Measured evidence as the interface, not raw state.** The prompt holds deterministic facts about the landscape, for example "perturbing a best known packing returns it or worse" and "random starts land 0.02–0.15 above". It holds no pictures or coordinates. We tested perception directly (images, SVG, JSON, colour-coded maps): the LLM did no better than random at telling where a move helps.
4. **Graded feedback.** Each researcher sees, for every size and seed, its gap, its **near miss** (the best other basin after polish) and its initial gap. When it saw only pass/fail, it abandoned every idea after one noisy run, jumping to a new field each round.
5. **One run is a noisy sample, so use seeds.** n = 88 fell on 7 of 8 seeds, so that record is robust. n = 123 was found by two different strategies. We rejected "screen first, then go broad": n = 123's initial population was 2e-4 *worse* than the record, and the record only appeared during evolution.
6. **History turns failures into refinements.** Researcher 4 (chain 3) went from:
   - round 1: rebuilding the whole packing. Too destructive: it never came within 3e-3.
   - round 2: "unlike the previous strategy, it never reconstructs the whole mosaic". Close, but no record.
   - round 3: "recombine intact pieces of locally optimized structures", which is Deaven & Ho's cut-and-splice from 1995, reinvented. It broke 3 records.
7. **A library makes discoveries transfer.** Record-breaking strategies, with their code, are offered to later researchers. The cut-and-splice strategy was designed for n = 101–132 and then broke n = 88 on a laptop, in a one-minute test.
8. **Equal budgets, a trusted evaluator and independent verification.** Every strategy gets the same template and compute, which makes comparisons fair. Strategy code can only propose candidates. Verification checks at zero tolerance and at 80 and 160 digits, independently of the search. Reward hacking has no route in.
9. **Polish more basins than looks necessary.** A relaxed side can sit up to 1e-3 (once 1e-2) above its polished optimum. The first n = 88 record came from the *4th* basin, so Mosa polishes the top 16.
10. **Which records give way.** Records built by *extending another packing* broke 4 of 8 times. Closed-form families broke 0 of 7, and records found by simulated annealing 0 of 3. Recombination is what exploits the inherited slack. n = 67, the 45° Göbel strip from 1980, is a plateau: about 70 seeds and a targeted lab with a brief did not move it.
11. **Engineering that mattered:**
    - compiled kernels, including the repair and the check (about 25% faster than the prototype);
    - Modal containers that each run many candidates at once, because the plan limits containers, not cores;
    - a record is saved the moment it's found, so a dying account loses nothing;
    - one JSON-lines file per lab, not one file per state, which had produced 563k files.

## What did not work (say so in the pitch: it makes the results credible)

- **LLM perception of geometry,** in any representation: no better than random.
- **LLM-proposed individual moves,** and the LLM as a selector among fixed tools.
- **Neural scorers and move policies:** about 1.3× better than random on unseen operators, but beaten by a short simulation at equal cost. None of the records needed them.
- **Early screening by "signs of life":** unvalidated, and rejected (see 5 above).
- **Looser solver tolerances for speed:** 2–13× faster, but measurably worse packings. The kernel is close to optimal.
- **Structural plateaus** such as n = 67.

## Design principles (the transferable part)

1. **Put the model where it has the edge:** choosing, adapting and combining *methods* (analogy, structure, scale) and writing them as code. Keep the numerics, evaluation and verification in trusted tools.
2. **Give it evidence and consequences, not raw state:** measured facts about the landscape, and the measured outcomes of its own code.
3. **Make feedback graded and replicated:** near misses, initial gaps, errors, several seeds.
4. **Hold a fixed template and equal budgets.** Strategies stay comparable, and the code's power is bounded.
5. **Separate proposer from verifier,** and make the verifier stricter than the search.
6. **Keep memory at three timescales:** the round history (within a researcher), the library (within a workspace) and the notebook (everything, replayable).
7. **Let the human steer at the level of evidence:** briefs, reference instances, choice of targets. A human chose cut-and-splice for n = 126; a brief carries the Göbel-strip analysis for n = 67.

## How it generalizes: adding a problem

The research loop, the evaluator, the sandbox, the notebook and the workbench are problem-agnostic. A new problem implements `mosa.domain.Domain`:

```python
class Circles(Domain):            # e.g. n circles in the smallest square (Packomania records)
    name, title = "circles", "Equal circles in the smallest square"
    problem = "Pack n equal circles without overlap into the smallest square. The objective is the side."
    evidence = "...measured facts: what perturbation, random starts and neighbour transplants do here..."
    api = "...initialize(record, neighbours, rng, count) / vary(parents, rng, count) in this domain's terms..."
    def targets(self): ...                 # sizes with known references
    def reference(self, n): ...            # best known solution (x, value)
    def best_known(self, n): ...
    def validate(self, x, value, n): ...   # shape and finiteness of model-written candidates
    def relax(self, x, value): ...         # penalty L-BFGS on pair overlaps, then repair -> (x, value, evaluations)
    def polish(self, x, value): ...        # SLSQP on the active contacts
    def verify(self, x, n): ...            # pairwise distances in mpmath -> certificate
    def svg(self, x, value): ...
```

Then register it in `mosa.domain.get`, and import the domain in `modal_app.py`'s warm-up step.

- **Other packing problems** follow the same recipe: circles in a square or a circle, polygons (with the separating-axis test), polyominoes, 3-D spheres or cubes, strip and bin packing. The squares adapter is about 400 lines, mostly the relaxation kernel.
- **Physics:**
  - Lennard-Jones and Morse clusters (references from the Cambridge Cluster Database), the Thomson problem (charges on a sphere), Tammes. Here `relax` is L-BFGS on the energy and `verify` recomputes the energy at high precision.
  - Cut-and-splice itself comes from this field, so the analogy runs in both directions.
- **Spatial optimization:** facility layout, floorplanning, sensor or antenna placement, nesting for cutting.
- **Beyond:** any family of instances with a fast local optimizer, a verifier and known best values. Only the adapter and the evidence text change.

## MVP contents, and what to build next

**In the MVP:**
- the squares adapter;
- the strategy sandbox;
- the equal-budget evaluator with near misses;
- local and Modal backends;
- researcher chains with brief, references, seeds, library and new / refine / combine decisions;
- independent verification;
- the notebook;
- the workbench: labs, a map of each lab's ideas (one row per researcher), idea and discovery panes in plain sentences, replay, New lab and Run on more sizes, dark and light themes;
- the CLI;
- an end-to-end test with a stub researcher.

**Next, in priority order. Small, elegant steps first:**
2. **Record a demo** from the workbench (script below).
3. **A Claude researcher option** in `llm.ask`. Today it calls the Codex CLI, which is what found the records. Keep the call structured.
4. **A circles adapter** to show generality, if there is time. Reproducing known optima is enough for the demo.
5. **Learned evidence:** derive the `evidence` text automatically from past notebooks ("vary-style perturbations returned the record in N% of runs…"), so the system writes its own landscape facts.
6. **Ideas as bandits:** spend seeds where near misses are promising, rather than equally.
7. **Literature retrieval** (Amass, arXiv) as a source of analogies, run as an A/B condition.
8. **Constructive starts for plateaus** (n = 67): briefs plus reference instances, plus an `initialize` that builds structures from scratch.

## Track 1 submission guide

**Judging:** five criteria of 20 points each. The submission is a 2-minute video, the repo link and a short description. Round 1 is a 5-minute pitch with demo and Q&A.

| Criterion | What to show |
|---|---|
| Technicality | Compiled relaxation plus an exact SQP polish; 80/160-digit verification; Modal fan-out (strategy, relax and polish workers, thousands of cores per lab); sandboxed model code; the notebook and replay |
| Creativity | The LLM as a *strategist* drawing analogies across fields; it reinvented Deaven & Ho from its own failures; near-miss feedback |
| Usefulness | Five new best-known results on a benchmark studied since 1979, verified and submitted to the catalogue; a reusable framework (the adapter contract) |
| Demo | Workbench replay of the real lab: the map filling in, Researcher 4's round 3, the n = 129 discovery with its rearranged squares marked and the verification |
| Alignment | Track 1 (AI discovery of algorithms) directly. Modal side challenge: the whole evaluation runs as Modal fan-out |

**2-minute video script:**
1. **0:00–0:15, the problem.** "Pack n unit squares into the smallest square: studied since 1979, records still improving. Can an AI researcher discover *search methods* that beat them?"
2. **0:15–0:40, how it works.** Over the lab map: each row is an LLM researcher, each mark an idea it wrote as code; tools test every idea at equal budget on Modal; an independent verifier checks every claim.
3. **0:40–1:15, the discovery.**
   - Open the lab n = 101–132, press Replay, and let the map fill in.
   - Stop on Researcher 4: round 1 too destructive, round 2 close, round 3 cut-and-splice with ★ 123, 129 and 130.
   - Select round 3 and read one line of "why the researcher expected it to work".
   - Point at Researcher 2's round 3: content-aware seam carving, from computational photography, beat the official n = 126.
4. **1:15–1:40, the record.** Select the discovery n = 129: toggle to the previous best and back (19 squares rearranged), 0.0093 smaller, verified at zero tolerance and at 80 and 160 digits, found by Researcher 4 in round 3.
5. **1:40–2:00, transfer and honesty.**
   - The library strategy broke n = 88 on 7 of 8 seeds.
   - n = 67 (the Göbel strip) still stands, which shows the system's limits.
   - Close: "five new best-known packings in one night, and the framework is problem-agnostic".

**Short description (for the form):**

> Mosa is an autoresearch workbench that moves the LLM one level above code evolution. Instead of mutating a program under a fitness score, as AlphaEvolve-style systems do, its LLM researchers propose search methods by analogy with other fields, each with a stated hypothesis, and write them as code. Trusted tools test every strategy at equal budget across many problem instances on Modal, and an independent verifier checks every claim. Researchers see graded feedback, including near misses, refine their ideas over rounds, and build on a library of strategies that worked. On the squares-in-squares packing benchmark, studied since 1979, Mosa found five new best-known packings in one night (n = 88, 123, 126, 129, 130). Each was verified at zero tolerance and at 80 and 160 digits. Four came from LLM-written strategies: one researcher reinvented the 1995 cut-and-splice method of atomic-cluster optimization after two failed rounds. The framework is problem-agnostic; a new problem only needs a relaxation, a polish and a verifier.

**Q&A preparation:**
- *"How is this different from AlphaEvolve, OpenEvolve or ShinkaEvolve?"* Those evolve a program: the LLM edits code, a score selects, over hundreds to thousands of edits. Mosa's LLM proposes a method with a hypothesis, sees graded evidence across many instances and seeds, and reasons about what to try next, in 12–20 calls per lab. Its outputs are reusable strategies (one designed for n = 101–132 broke n = 88), and its code cannot touch the evaluator. The two are complementary.
- *"Isn't this just an evolutionary algorithm?"* The template is evolutionary on purpose, so budgets stay comparable. The discovery happens at the level of *which operators and why*: the model invents them, explains them, and refines them from measured outcomes.
- *"Did the model just remember Deaven & Ho?"* Possibly. Rediscovering a classic for a new problem is itself the useful skill, and it reached the idea through two rounds of failure feedback. The prompt names no method.
- *"Are the records real?"* They are verified independently at zero tolerance and at 80 and 160 digits, with every pair and wall at least 2e-10 apart. They have been submitted to the catalogue. We claim best-known, not optimal.
- *"What did a human decide?"* The method for n = 126 (cut-and-splice) was chosen by a human, and briefs come from humans. The other four records came from strategies the LLM wrote.
- *"What does it cost?"* Roughly $150–200 of Modal compute for the whole night. A lab of 4 researchers × 3 rounds × 20 sizes costs about $30–100.
- *"Which models?"* The researchers ran on Codex (OpenAI) through the `codex` CLI. The framework itself was built with Claude Code. The model is pluggable.

## Operations

- **Environment:** `uv venv --python 3.12 && uv pip install -r requirements.txt`.
- **Modal:** `modal token set` once. Set `MOSA_MODAL_CONTAINERS` to the number of solver containers (default 48, each 64 cores), and leave room under the workspace's container limit.
- **Labs need the `codex` CLI, logged in.** `apply`, `verify` and the workbench do not.
- **Workbench:** `python -m mosa serve` serves http://127.0.0.1:8777. Port 8765 was taken on the dev machine.
- **Known limits:**
  - The first imported lab has no researcher-decision field, because the prototype didn't record one.
  - Comparison PNGs were never generated (the catalogue site rate-limited us). The workbench's record view replaces them, and the catalogue-format SVGs are on the `results-2026-10-04` branch.
  - Replay runs a whole lab in about 40 seconds.
