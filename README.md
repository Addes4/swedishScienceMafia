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

Each packing was checked for overlap at zero tolerance and audited at 80 and 160 digits. Every pair of squares, and every square and wall, is at least 2e-10 apart. The checks run independently of the search. The packings, with their catalogue-format SVGs, are in [`results/`](results).

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

## How it works

```
             ┌──────────── brief · evidence · library · own history with near misses ────────────┐
             ▼                                                                                   │
  LLM researcher ──► strategy (idea, source field, why it fits, code: initialize + vary)          │
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
- **A library holds the strategies that broke records.** Later researchers build on these strategies or combine them. A strategy designed for n = 101–132 carried over to n = 88.
- **Everything is replayable.** Every prompt, answer, run and certificate is appended to a notebook (`events.jsonl`). The workbench reads it live, or replays it.

## Quick start

```bash
uv venv --python 3.12 && uv pip install -r requirements.txt
python -m mosa serve                      # workbench at http://127.0.0.1:8777 (labs from history/ and runs/)

# a research lab: 4 researchers x 3 rounds on 20 sizes, evaluated on Modal (needs `modal token set` and the `codex` CLI)
python -m mosa lab --targets 101-110 122-132 --chains 4 --rounds 3 --backend modal

# run a library strategy on more sizes and seeds, on this machine (no model needed)
python -m mosa apply --strategy library:2 --targets 88 --seeds 1 2 --backend local --init 64 --children 64 --generations 2 --population 8 --polish 4

python -m mosa verify --n 88 --file results/n88.json  # independent certificate for any packing
python -m unittest tests.test_lab                     # end-to-end lab round with a stub researcher
```


## The workbench

`python -m mosa serve` (http://127.0.0.1:8777). It shows three things and offers one action.

- **Labs** (left): each named by its question, i.e. the sizes it attacks. A running lab breathes; a finished one shows how many discoveries it made.
- **The lab** (centre): a map of the research. One row per researcher, ideas left to right in the order they were tried. Each idea is a name, the field it was borrowed from, and one mark: ★ a new best-known packing, ○ none, ✕ the code failed. Finished labs can be replayed on their real timeline.
- **The selection** (right), in plain sentences:
  - **An idea:** its outcome in one sentence, why the researcher expected it to work, and what it does. The results per size, the code and the exact prompt are folded away.
  - **A discovery:** the packing, with a toggle to the previous best and the rearranged squares marked; the numbers in one sentence; how it was verified; the idea that found it; the catalogue-format SVG.
- **New lab:** sizes, researchers, rounds and an optional brief. Seeds, compute and reference sizes sit under "More options". From any idea, **Run on more sizes** reruns its strategy elsewhere.

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
  sandbox.py           runs model-written initialize/vary (time limit, validation, fresh namespace)
  evaluate.py          the evolutionary template and budget; gap, near miss, initial gap
  research.py          researcher chains, prompt, decisions, library, record verification
  backends.py          local process or Modal containers; modal_app.py defines the workers
  llm.py               one structured model call per round (Codex CLI; prompt/answer kept per round)
  store.py             the append-only notebook
  ui/                  workbench server and single-page app (no build step)
data/                  best known packings (jlevy/squares witnesses), catalogue sides and notes, strategy library
history/               the night's labs as notebooks (records re-verified on import: scripts/import_history.py)
briefs/                research briefs (e.g. n = 67 and the Göbel strip)
results/               verified records (JSON + catalogue-format SVG)
docs/NOTES.md          what worked, design principles, how this generalizes, submission guide, next steps
```

Data sources: the [squares-in-squares catalogue](https://kingbird.myphotos.cc/packing/squares_in_squares.html) (Erich Friedman, David Ellsworth) and the known-best witnesses from [jlevy/squares](https://github.com/jlevy/squares).
