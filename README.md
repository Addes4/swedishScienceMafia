# Mosa

**An autoresearch workbench: LLM researchers write search strategies, trusted tools test them, and nothing counts until it is independently verified.**

Built in one night at the London AI x Science Hackathon (Track 1: AI automated discovery of algorithms). On the benchmark
we used, packing *n* unit squares into the smallest square, Mosa found **five new best-known packings**. Four of them
came from strategies written by the LLM researchers themselves.

| n | best known before | Mosa | improvement | found by |
|---|---|---|---|---|
| 88 | 9.888153053759 (Ellsworth 2024) | **9.886746030783** | 1.41e-3 | the library's cut-and-splice strategy, applied to n < 100 (beat the record on 7 of 8 seeds) |
| 123 | 11.601384658386 (official 11.601399793788) | **11.600907781033** | 4.77e-4 | LLM researcher: large-neighbourhood search + grain nucleation; found again by another researcher |
| 126 | 11.774735132407 (de Winter 2026, AI-assisted) | **11.773303609158** | 1.43e-3 | cut-and-splice recombination (Deaven & Ho 1995), chosen by a human |
| 129 | 11.881306218090 (Ellsworth 2024) | **11.872029851656** | 9.28e-3 | LLM researcher: cut-and-splice, reinvented after two failed rounds |
| 130 | 11.911187706549 (official 11.911190520159) | **11.909544620011** | 1.64e-3 | same researcher and round as n = 129 |

Each packing was checked for overlap at zero tolerance and audited at 80 and 160 digits. Every pair of squares, and every square and wall, is at least 2e-10 apart. The checks run independently of the search. The packings, with their catalogue-format SVGs, are on the branch [`results-2026-10-04`](../../tree/results-2026-10-04/results), with the night's research notebooks.

We are not claiming these are optimal. They have been submitted to the squares-in-squares catalogue for verification.

## What is new

Most LLM-driven discovery systems, such as AlphaEvolve, OpenEvolve, ShinkaEvolve and FunSearch, evolve **programs**. The model acts as a mutation operator that edits code, and a fitness score selects the survivors over hundreds or thousands of edits. The searches that set most squares-in-squares records (simulated annealing, basin hopping, hand-made constructions) use **operators a human chose**.

Mosa moves the model one level up, **from editing programs to doing research.** It proposes methods by analogy, tests them fairly across many instances, and reasons from graded evidence. The numerics and the verification stay in trusted tools.

| | Code evolution (AlphaEvolve, OpenEvolve, ShinkaEvolve) | Numerical search (annealing, basin hopping) | Mosa |
|---|---|---|---|
| What the model produces | edits to a program | nothing: a human designs the operators | a search method: its source field, a hypothesis for why it fits, and code |
| What gets evaluated | a program, by its score | one run | a strategy on a family of instances × seeds, at equal budget |
| Feedback to the model | a fitness score | — | graded evidence per instance: gap, near miss, initial gap, failures |
| Where new ideas come from | local edits to existing code | the designer | analogies across fields: crystal structure prediction, protein folding, metallurgy, computational photography… |
| Memory | the population | — | each researcher's history, a library of strategies that worked, a replayable notebook |
| Trust | the program computes its own result | the program | numerics and verification are fixed tools; model code can only propose candidates |
| Model calls per lab | hundreds to thousands | none | 12–20 (4 researchers × 3–5 rounds); the compute goes into testing |

**Evidence that the difference matters:**
- **Same tools, different strategies.** Our own searches with fixed operators (group perturbations, soft modes, neighbour transplants, beam search) used the same relaxation and polish. They never improved a best-known packing for n = 51–89 or 101–200. On the same tools, LLM-designed strategies broke four.
- **Strategies are reusable algorithms, not one-off solutions.** The cut-and-splice strategy was designed while attacking n = 101–132. It then broke n = 88 on 7 of 8 seeds.
- **Reasoning from evidence, not selection.** Researcher 4's round 1 rebuilt the packing and was too destructive. Round 2 made local edits and came close. In round 3 it reasoned its way to recombining intact pieces, which is Deaven & Ho's 1995 method from atomic clusters, and broke n = 123, 129 and 130.
- **Ideas from far away.** Content-aware seam carving, from computational photography, beat the official n = 126. Large-neighbourhood search with grain nucleation broke n = 123.

**Prior work, honestly:** AlphaEvolve has also improved packing bounds, for example for circles and hexagons. The approaches are complementary: an evolved program could become one of Mosa's tools, and a Mosa strategy could be evolved further.

**Connection to Track 1 (AI automated discovery of algorithms):** what Mosa discovers *are* algorithms, namely search strategies, each with a stated hypothesis. They are validated by new results on a benchmark studied since 1979 and verified independently of the system that found them. The framework itself is the autoresearcher: it decides what to try next from its own evidence. The only problem-specific code is a small domain adapter.

## How we know it is real, and what we have not shown

These follow the standards of the team's checking framework on `main` (*autoresearch that checks its own claims*):

- **Every record is verified independently.** A strategy can only hand over coordinates. Mosa recomputes every clearance at zero tolerance and at 80 and 160 digits; a strategy never reports its own score.
- **Integrity scan.** We adopted the static gate from `main`: strategy code that touches files, processes, the network, the import system or the evaluator is rejected before it runs. All 35 strategies written tonight pass it, and it rejects deliberate cheats (`tests/test_sandbox.py`).
- **Held-out sizes.** The cut-and-splice strategy was designed while attacking n = 101–132. On sizes it never saw (n = 11–99), it broke n = 88 on 7 of 8 seeds.
- **Equal budgets.** Every strategy gets the same template and candidate counts, on the same sizes and seeds.
- **Seeds as a control for luck.** One run is a noisy sample. n = 88 fell on 7 of 8 seeds, and n = 123 was found by two different strategies.
- **Not shown:** that Mosa's research loop beats simpler methods at equal budget. We tested it (next section) and it did not. n = 67 also resisted everything.

## Head to head at equal budget: Mosa does not beat simpler methods

On 4 October we ran Mosa against three simpler methods. Every method got the same trusted harness (relax, polish,
independent verifier) and the same evaluation budget per instance, so only the method differs.
- **Plain coding agent:** Codex (the model Mosa's researchers use), working free-form with the harness as a library;
  `baselines/coding_agent.py`.
- **One-shot LLM strategy:** one researcher, one round, no research loop.
- **Basin hopping:** the standard method, no LLM.

Tables come from `baselines/compare.py`.

**Original problems first (nothing to memorize).** Points on a sphere minimizing the Riesz s-energy, with exponents
nobody has published optima for. n = 150, 200 and 250; 12 runs × 576 relaxations per instance for every arm.

| s | Mosa | One-shot LLM strategy | Basin hopping | Plain coding agent |
|---|---|---|---|---|
| 0.5 | best on 3 of 3 | best on 3 of 3 | best on 3 of 3 | best on 3 of 3 |
| 6 (rugged: random starts spread over many minima) | best on 3 of 3 | best on 3 of 3 | best on 3 of 3 | best on 3 of 3, using 35–67% of its budget |

Every arm found the same lowest energy, to 6 decimals, on every instance. At s = 6 the share of single runs that reached
it varied: on n = 250, 4 of 12 for Mosa, 7 of 12 for the one-shot strategy and 4 of 12 for basin hopping.

**A published benchmark.** Circles in a unit square maximizing the sum of radii, n = 26:

| Method | Sum of radii | Overlap tolerance |
|---|---|---|
| Plain coding agent (11 minutes, 12% of its budget) | **2.6359830849** | 0 (our verifier) |
| ThetaEvolve, best published | 2.63598308 | 1e-6 |
| ShinkaEvolve | 2.63598283 | 1e-7 |
| Mosa (all 36 runs: 4 researchers × 3 rounds × 3 seeds) | 2.6359773947 | 0 |
| AlphaEvolve | 2.63586276 | 0 |

**Squares, n = 85–88.** Mosa and the coding agent held the best-known packings on 85, 86 and 88; both were 2.2e-6 short
on 87. Neither found a record.

**What this means.** When the trusted tools are strong, they do most of the work: the method on top barely changes
the best result. A plain coding agent with the same tools matched or beat Mosa, using fewer evaluations. We found no
evidence that Mosa's research loop adds value at equal budget on these problems.

Mosa's demonstrated value is elsewhere:
- any problem stated in words becomes a verified, self-tested harness and a workspace a person can steer;
- every claim is checked independently and traced to the code and seed that produced it;
- the overnight squares campaign found five verified records, but at a much larger budget and with no matched comparison.

## An unseen problem: charges on a sphere

To check that the framework is not tuned to squares, we added the Thomson problem: n unit charges on a sphere,
minimizing their Coulomb energy, with best-known energies from the Cambridge Cluster Database. Strategies get no known
configuration, only what their workspace has found for nearby sizes.

| n = 300–305, 72 runs each, same evaluator and budget | best known reached | gap at n = 300 | gap at n = 301 |
|---|---|---|---|
| Basin hopping (Wales & Doye 1997), the standard method | 4 of 6 | 0.054 | 0.038 |
| Mosa: 4 researchers × 3 rounds | 4 of 6 | **0.019** | 0.038 |

**A tie.** Mosa matched the standard method on a problem it had never seen and came closer on the hardest size, but
one small experiment shows no advantage. Some of Mosa's budget went to strategies whose code failed.

## How it works

```
             ┌──────────── brief · evidence · library · own history with near misses ────────────┐
             ▼                                                                                   │
  LLM researcher ──► strategy (idea, source field, why it fits, code: initialize + vary)          │
                         │      every strategy also sees the workspace's memory: the best         │
                         │      solution found so far for each instance                           │
                         │                                                                       │
                         ▼   sandboxed, time-limited, invalid candidates dropped                 │
  evaluator: same budget on every size × seed ── relax (compiled) ── keep distinct basins ──      │
             polish best 16 exactly (SQP) ── gap, near miss, initial gap ────────────────────────┘
                         │
                         ▼   candidate record
  independent verifier (zero tolerance, 80 and 160 digits) ──► notebook ──► workbench, library
```

- **The LLM works at the level of search strategy.** It never places pieces. Each round, a researcher picks a method, often one imported from another field, explains why that method's assumptions match the measured landscape, and writes it as code for a small evolutionary template.
- **The tools do the numerical work, and they are trusted.** Strategy code can only propose candidates. It cannot touch the relaxation, the polish or the verifier, so there is no route to grading its own homework.
- **Feedback is graded, not pass/fail.** Researchers see per-size, per-seed gaps and **near misses**: how close their best other basin came. With only pass/fail, one noisy failure made them drop each idea after a single round.
- **Any problem you can state.** The research agent picks problems from a library of trusted harnesses (squares in a square; the Thomson problem; Riesz s-energies on the sphere for any s, which have no published answers to memorize). For anything else ("pack 20–25 circles in the smallest circle") it writes a harness on the spot: a random start, a fast local optimizer, an independent checker, a picture and any published values. The harness passes the same integrity scan as strategies and a self-test (random starts are relaxed and checked; the checker must recompute their values and reject malformed solutions; nothing may beat a published value in a self-test) before any research runs on it. You can read its code and test in the conversation.
- **Related problems share a workspace.** An instance is a problem and a size. Problems in one family share a representation (Thomson and the Riesz energies are all points on a sphere), so one strategy runs on all of them, and what was found for one is offered to the others.
- **You direct the research in a conversation.** "Beat the best known packings of squares near n = 125" becomes a workspace: the research agent picks the problem, the instances, the number of researchers, rounds and seeds (sized to the compute), writes their brief and says why. Later messages expand or redirect the research, or ask about it.
- **The workspace is the unit of shared context.** A workspace is a problem, its instances and a memory: the best solution found for every instance and the ideas that broke records. Everything that runs in it sees that memory, so what was found for n = 118 is offered when working on n = 88. You choose what shares context by choosing what goes in the same workspace. A strategy designed for n = 101–132 carried over to n = 88.
- **Everything is replayable.** Every prompt, answer, run and certificate is appended to a notebook (`events.jsonl`). The workbench reads it live, or replays it.

## Quick start

```bash
uv venv --python 3.12 && uv pip install -r requirements.txt
python -m mosa serve                      # workbench at http://127.0.0.1:8777 (workspaces in runs/)

# say what to research: the planning agent creates the workspace and runs it (needs `modal token set` and the `codex` CLI)
python -m mosa run "Beat the best known packings of squares near n = 125" --backend modal

# or set everything yourself: 4 researchers x 3 rounds on 20 sizes
python -m mosa lab --targets 101-110 122-132 --chains 4 --rounds 3 --backend modal --out runs/squares --name "Squares near 120"

# continue the same researchers in that workspace, or run one of its ideas on more instances (no model needed)
python -m mosa lab --out runs/squares --targets 88 123-130 --rounds 2 --backend modal
python -m mosa apply --out runs/squares --idea 0:3:3 --targets 88 --seeds 1 2 3 --backend local

# another problem: the Thomson problem, and its basin-hopping baseline at the same budget
python -m mosa lab --domain thomson --targets 300-305 --out runs/thomson --name "Thomson problem"
python -m mosa apply --domain thomson --strategy baselines/thomson-basin-hopping.py --targets 300-305 --seeds 1 2 3 --out runs/thomson-baseline

python -m unittest tests.test_lab tests.test_sandbox  # end-to-end sessions with a stub researcher; the integrity scan
```

## The workbench

`python -m mosa serve` (http://127.0.0.1:8777).

- **Workspaces** (left), each with a name. A running one breathes.
- **The workspace** (centre): its instances, with ★ a new best-known and ● the best known reached standing out, then a map of the research. One row per researcher, ideas left to right in the order they were tried. Each idea is a name, the field it was borrowed from, and one mark: ★ new best-known, ● best known reached, ○ neither, ✕ the code failed. Finished workspaces can be replayed on their real timeline.
- **The selection** (right), in plain sentences:
  - **An idea:** its outcome in one sentence, why the researcher expected it to work, and what it does. The results per instance, the code and the exact prompt are folded away. **Run on more instances** adds results to the same idea.
  - **An instance:** its best solution (a packing, or charges on a sphere), how it compares with the best known, how it was verified, and the idea that found it.
- **The conversation** (right, whenever nothing is selected): talk to the workspace's research agent. Ask it to expand or redirect the research ("add 88–90", "focus on 126 and borrow from 125") and it plans and starts a session, continuing the same researchers; ask it a question ("why did researcher 2's idea fail?") and it answers from the workspace's state. A note appears when a session finishes. **New workspace** is the first message of a new conversation.

Arrow keys move between ideas; Esc closes the selection.

## What Mosa does and does not do

**Does:**
- Lets the model make the high-level choices: which search to run, from which field, at what scale; whether to refine, combine or replace an idea.
- Runs every strategy at equal budget, on many sizes and seeds.
- Reports near misses.
- Verifies every candidate independently.
- Keeps provenance from each record back to the exact round, code and seed.

**Does not:**
- Let the model place pieces or judge pictures. We measured image, SVG and JSON perception: all no better than random.
- Let model-written code touch the evaluator.
- Claim optimality.
- Require training. Neural networks are optional and are not the method.

**Not solved:** structural plateaus. n = 67 is the Göbel strip, 8 + √2/2, which has stood since 1980. It held through about 70 seeds and a targeted lab with a research brief. Recombining near a plateau cannot leave it. Beating it needs a different construction, which is the job of a brief and a constructive `initialize`.

## Repository

```
mosa/
  domain.py            what a problem must provide (the only problem-specific code)
  domains/squares/     compiled relaxation, SQP polish, high-precision audit, catalogue data, SVG
  domains/thomson/     Riesz s-energy on the sphere (s = 1 is the Thomson problem), relaxation, 50-digit verifier
  harness.py           harnesses written on the spot for problems outside the library, scanned and self-tested
  sandbox.py           runs model-written initialize/vary (integrity scan, time limit, validation, fresh namespace)
  evaluate.py          the evolutionary template and budget; gap, near miss, initial gap; neighbours from memory
  research.py          workspaces: sessions, researchers that continue, shared memory, library, record verification
  orchestrator.py      the research agent: answers questions about a workspace, or plans and starts a session
  backends.py          local process or Modal containers; modal_app.py defines the workers
  llm.py               one structured model call per round (Codex CLI; prompt/answer kept per round)
  store.py             the append-only notebook (one per workspace)
  ui/                  workbench server and single-page app (no build step)
baselines/             strategies run without a researcher (basin hopping for the Thomson problem)
data/                  reference data: best known packings (jlevy/squares), catalogue sides and notes, Thomson energies
docs/NOTES.md          what worked, design principles, how this generalizes, submission guide, next steps
```

Data sources: the [Cambridge Cluster Database](https://www-wales.ch.cam.ac.uk/~wales/CCD/Thomson/table.html) (Thomson energies), the [squares-in-squares catalogue](https://kingbird.myphotos.cc/packing/squares_in_squares.html) (Erich Friedman, David Ellsworth) and the known-best witnesses from [jlevy/squares](https://github.com/jlevy/squares).
