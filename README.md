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

The workbench is laid out like an editor:
- **Activity bar:** labs, records, strategy library, problem sizes, new lab.
- **Explorer:** each lab's researchers and rounds.
- **Tabbed documents:**
  - *Research threads*, the default view: every researcher's rounds as cards, with per-size result strips.
  - *Round:* the idea and why it fits, the strategy, a results heatmap, the code and the exact prompt.
  - *Record:* before and after, with the rearranged squares highlighted, verification and provenance.
  - *Problem size:* the catalogue history and every attempt.
- **Bottom panel:** live progress and the notebook.
- **Replay** plays any lab back on its real timeline.
- ⌘K opens the command palette, ⌘B toggles the sidebar, ⌘J toggles the panel.

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
