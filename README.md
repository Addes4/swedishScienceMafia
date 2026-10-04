# Swedish Science Mafia: algorithm autoresearch that checks its own claims

Our team's work for Track 1 of the AI x Science Hackathon in London (3–4 October 2026), *Build Your Own Algorithm
Autoresearch Framework*. It holds two systems built on one principle: an AI research loop is easy to fool (overfitting,
lucky seeds, loopholes in the scorer, gains a simple method would have reached anyway), so nothing counts until it has
been checked independently.

## Mosa: a research workbench for optimization problems → [MOSA.md](MOSA.md)

LLM researchers propose *search methods* by analogy with other fields, each with a hypothesis, and write them as code.
Trusted tools test every strategy at equal budget across many instances and seeds (on Modal), and an independent verifier
checks every claim at high precision. You state a problem in plain words; the research agent picks it from a library of
trusted harnesses, or writes and self-tests a harness for a new one.

- **Five new best-known packings** of unit squares in a square (n = 88, 123, 126, 129, 130), a benchmark studied since
  1979; four came from strategies the LLM researchers wrote.
- A problem library beyond packing: points on a sphere for any Riesz exponent (Smale's logarithmic energy, Thomson,
  Tammes), and the circles-in-a-square benchmark that AlphaEvolve and ShinkaEvolve report.
- **Measured honestly:** at equal budget, a plain coding agent, a one-shot LLM strategy and basin hopping matched Mosa on
  original sphere problems, and the coding agent beat it on the n = 26 benchmark. With strong trusted tools, the method
  on top matters little ([details](MOSA.md#head-to-head-at-equal-budget-mosa-does-not-beat-simpler-methods)).

```bash
python -m mosa serve     # the workbench at http://127.0.0.1:8777
```

## The self-checking loop: AI-designed heuristics, audited → [AUTORESEARCH.md](AUTORESEARCH.md)

A FunSearch-style loop (a model writes a small program, it is scored, kept if better, and improved) that checks itself at
every step: held-out instances, matched budgets, baselines first, and an integrity gate that red-teaming could not break.

- **FunSearch's famous bin-packing result is far from optimal**, and a simple rule we designed (FWSS) beats every
  published AI-designed rule we could compare against.
- **The loop improved on the best classical rule**, and on a travelling-salesman benchmark textbook methods beat every
  published AI-designed heuristic.

```bash
python -m autoresearch.loop problems/erdos_squares --mock
```

## Repository

| Path | What |
|---|---|
| [MOSA.md](MOSA.md), `mosa/`, `baselines/`, `data/` | Mosa: the workbench, the problem harnesses and their reference data |
| [AUTORESEARCH.md](AUTORESEARCH.md), `autoresearch/`, `problems/`, `tournament/`, `falsify/` | The self-checking loop, its problems, the framework tournament and FunSearch's reference heuristics |
| `experiments/` | The loop's studies, each with its protocol, results and data ([index](experiments/README.md)) |
| `docs/` | [Documentation map](docs/README.md); Mosa's handoff notes are [docs/NOTES.md](docs/NOTES.md) |
| `tests/` | Both test suites: `python -m pytest tests` |

Setup: `pip install -r requirements.txt` (Python 3.12; the loop's C++ problems need a compiler; Mosa's researchers need
the `codex` CLI and, for Modal, `modal token set`).
