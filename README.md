# Swedish Science Mafia: autoresearch that checks its own claims

We built an AI research loop for Track 1 of the AI x Science Hackathon in London (3–4 October 2026),
*Build Your Own Algorithm Autoresearch Framework*.

The idea is simple. A language model writes a small program that tries to solve a problem. We score
it, keep it if it is better, and ask for an improvement. Repeat. Loops like this are easy to fool,
though: they can overfit the test cases they are tuned on, get lucky, find loopholes in the scorer,
or get credit for gains a simple method would have reached anyway. So our loop checks itself at every
step, and every part of it was kept only if an experiment showed it was worth having.

## What we found

- **The famous FunSearch result is far from optimal.** On FunSearch's online bin-packing benchmark,
  its AI-evolved rule uses about 14 more bins per instance than the best possible packing. A simple
  rule we designed, **FWSS**, gets within about 2. It beats every published AI-designed rule we could
  compare against. ([online-frontier-v1](experiments/online-frontier-v1/RESULTS.md),
  [online-beyond-ss-v1](experiments/online-beyond-ss-v1/RESULTS.md))
- **Our loop improved on the best classical rule.** Started from Sum-of-Squares, a rule from 2006,
  it found a better one: 2.3 fewer bins per instance on instances it had never seen, for about $1 of
  compute in total. ([llm-from-ss-v1](experiments/llm-from-ss-v1/RESULTS.md))
- **Started from scratch, it gets close to FunSearch cheaply:** 97% of FunSearch's improvement over
  the classic best-fit rule, for about 20 cents per run on an open model.
  ([llm-long-search-v1](experiments/llm-long-search-v1/RESULTS.md))
- **The same pattern holds on a second benchmark.** On a travelling-salesman task used by a dozen
  AI-design papers, textbook methods from the 1950s–70s beat every published AI-designed heuristic.
  ([tsp-construct-v1](experiments/tsp-construct-v1/RESULTS.md))
- **The checks matter.** Testing on unseen instances caught programs that looked excellent but were
  not (one scored 0.960 on its test cases and 0.238 on new ones), and our scorer held up against 68
  deliberate attempts to cheat it. ([tournament-v2](experiments/tournament-v2/RESULTS.md),
  [gate-redteam-v1](experiments/gate-redteam-v1/RESULTS.md))

## Try it

You need Python 3.10+ and a C++ compiler. Run from the repository root:

```bash
pip install -r requirements.txt
python -m autoresearch.loop problems/erdos_squares --mock                            # no API calls, a few seconds
python -m autoresearch.loop problems/bin_packing_online --budget 0.10 --provider hf  # a real run, capped at $0.10
```

A live run uses an open model through the Hugging Face router and needs a Hugging Face token
(`HF_TOKEN`, or `huggingface-cli login`). To use Claude instead, add `--provider anthropic` and put
`ANTHROPIC_API_KEY` in a `.env` file (`cp .env.example .env`). Each run writes a readable report to
`runs/<problem>-<time>/report.md`; two example runs are in [runs/](runs/README.md).
`python -m autoresearch.loop --help` lists every option.

## How a run works

1. **Propose.** The model edits the current best program.
2. **Test safely.** The new program runs in a separate, sandboxed process on the problem's test
   instances. Suspicious code is rejected, and any record-breaking score is re-checked strictly.
3. **Keep or discard.** It is kept only if it scores better without getting worse where earlier
   attempts went wrong.
4. **Check on unseen instances.** When the budget runs out, the final program is tested on instances
   that were never used during the search. The report flags it if it only looked good on the familiar
   ones.
5. **Explain.** Parts of the program are removed one at a time to see which ones actually matter.
6. **Compare.** The result is measured against simple baselines on the same instances, so any gain is
   real.

More detail is in [autoresearch/README.md](autoresearch/README.md), and the design notes are in
[autoresearch/LOOP.md](autoresearch/LOOP.md).

## What we tried and left out

We also built idea triage (a cheap model choosing which ideas an expensive model should implement),
a memory of past failures in the prompt, gates built from counterexamples, and an adaptive controller
that decides when to edit, rewrite or restart. We tested each against a simpler alternative, and none
earned its place, so they are not in the loop. What we found, and the experiments behind it, are in
[experiments/README.md](experiments/README.md#what-we-tried-and-dropped).

## How we kept ourselves honest

- Every experiment's plan was written down before it ran, so the goalposts could not move.
- Final tests used new instances generated only after the search had finished.
- Every method we compared got the same budget.
- An AI search had to beat what a few minutes of ordinary tuning could reach.
- Every paid API call and its cost was logged, and independent reviewers re-computed the numbers of
  three studies from the saved data ([docs/reviews/](docs/reviews/README.md)).
- What went wrong is on the record too: credit running out, interrupted runs, corrections
  ([docs/logs/OVERNIGHT-2026-10-03.md](docs/logs/OVERNIGHT-2026-10-03.md)).

## What's in the repository

```
autoresearch/   the loop, the sandboxed scorer, and the explanation step
tournament/     the search code the loop runs on, and a way to compare whole frameworks at equal cost
problems/       the problems: online bin packing, circle packing, two Erdős problems, sum-difference
experiments/    every study, with its plan, results and raw data (start at experiments/README.md)
runs/           two example runs of the loop
docs/           literature review, coordination log, independent reviews (docs/README.md)
falsify/        FunSearch's published bin-packing rules, used as a reference by the studies
tests/          the test suite (python -m pytest tests -q)
```

To add your own problem, create a folder under `problems/` with a problem statement, a starting
program and a scorer; the [problem guide](problems/README.md) shows how. The loop needs no changes.

## Limitations

- FWSS has not yet been re-implemented by anyone outside the team.
- Most runs used one open model and a few hundred steps, so stronger models might do better.
- The loop picks programs using only two test instances, which is enough to find real gains but makes
  its overfitting warning noisy.
- The sandbox protects an honest loop; it is not a hardened security sandbox.

## Credits

ShinkaEvolve (Sakana AI, Apache-2.0). Problem statements and scoring rules come from the AlphaEvolve
problem repository (Apache-2.0 / CC-BY 4.0). FunSearch's bin-packing heuristics come from
google-deepmind/funsearch (Apache-2.0). The literature review is in
[docs/literature/related-work.md](docs/literature/related-work.md). Code was written during the event
with help from Codex and Claude.

To cite: Swedish Science Mafia (2026), *Autoresearch that checks its own claims*, AI x Science
Hackathon, London. https://github.com/swedishScienceMafia/swedishScienceMafia
