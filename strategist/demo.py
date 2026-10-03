"""Narrated single run: watch the search stagnate, change strategy, and resume improving.

    python -m strategist.demo --benchmark labs --seed 1003
"""
import argparse
import json
from pathlib import Path
from .controller import STALL_NAMES, Adaptive, context
from .problems import BENCHMARKS
from .search import COSTS, Run


def narrate(bench, seed, budget, verbose=True):
    problem = BENCHMARKS[bench](seed)
    policy = Adaptive(COSTS, seed)
    run = Run(problem, policy, budget, seed, trace=True)
    show = lambda f: f'{problem.display(f):.5g}'
    say = print if verbose else (lambda *a, **k: None)
    say(f'{problem.name}: {problem.__doc__.splitlines()[0]}')
    say(f'budget {budget:g} cost units; move costs {COSTS}; start {show(run.f_best)}\n')
    say(f'{"cost":>7}  event')
    events = []
    while True:
        state = context(run.stall, run.leader)
        why, stall = policy.explain(state, run), run.stall
        if not run.step(): break
        t = run.trace[-1]
        if t['op'] == 'restart':
            line = (f'RESTART  leader stalled {stall} moves ({state}): staying yields {why["stay"]:.2e}/cu '
                    f'< a fresh excursion {why["explore"]:.2e}/cu')
        elif t['op'] == 'resume':
            line = f'RESUME   excursion stalled {stall} moves, as long as the leader had; back to best {show(run.f_best)}'
        elif t['gain'] > 0:
            where = 'leader' if state.startswith('lead') else 'excursion, which overtook the leader'
            line = f'NEW BEST {show(t["best"])} by {t["op"]} on the {where}, after {stall} non-improving moves'
        else: continue
        events.append({'spent': t['spent'], 'text': line})
        say(f'{t["spent"]:7.0f}  {line}')
    say(f'\nfinal best {show(run.f_best)} after {run.steps} moves; '
        f'{run.ops.count("restart")} restarts, {run.ops.count("resume")} resumes')
    say('\nmoves the controller chose, by context (share of moves in that context):')
    for state in sorted(run.usage, key=lambda s: (s.split('/')[0], STALL_NAMES.index(s.split('/')[1]))):
        counts = run.usage[state]; n = sum(counts.values())
        say(f'  {state:15s} n={n:5d}  ' + '  '.join(f'{op}={c/n:4.0%}' for op, c in counts.items() if c))
    return run, events


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--benchmark', choices=BENCHMARKS, default='labs')
    parser.add_argument('--seed', type=int, default=1003)
    parser.add_argument('--budget', type=float, default=3000.)
    parser.add_argument('--trace', help='write the full move-by-move trace as JSON')
    args = parser.parse_args()
    run, events = narrate(args.benchmark, args.seed, args.budget)
    if args.trace:
        p = run.problem
        Path(args.trace).parent.mkdir(parents=True, exist_ok=True)
        Path(args.trace).write_text(json.dumps({
            'benchmark': args.benchmark, 'seed': args.seed, 'budget': args.budget, 'name': p.name,
            'higher_is_better': p.higher_is_better, 'events': events,
            'trace': [{**t, 'child': p.display(t['child']), 'working': p.display(t['working']),
                       'best': p.display(t['best'])} for t in run.trace]})+'\n')


if __name__ == '__main__': main()
