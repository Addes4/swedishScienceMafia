"""Counterfactual forks at switch points: did leaving the line cause the progress that followed?

At each moment the adaptive controller leaves the leader line, the whole search state is copied. Forks
from the copy either follow the controller or stay on the line with small edits, each with an
independent random stream, for the same cost window.

    python -m strategist.forks --seeds 2000:2040 --out experiments/strategist-v1
"""
import argparse
import copy
import json
import statistics
from multiprocessing import Pool
from pathlib import Path
from .controller import Adaptive, Fixed, context
from .problems import BENCHMARKS
from .search import COSTS, Run
from .stats import paired

BENCHMARK_SET = ('labs', 'heilbronn', 'nk')


def switch_points(problem, seed, budget):
    """Snapshots of the adaptive run taken just before each decision to leave the leader line."""
    run = Run(problem, Adaptive(COSTS, seed), budget, seed)
    snapshots = []
    while True:
        if run.leader and run.policy.leaves(context(run.stall, True), run) == 'restart':
            snapshots.append(copy.deepcopy(run, memo={id(problem): problem}))
        if not run.step(): break
    return snapshots


def fork_seed(job):
    bench, seed, budget, window, forks, moments = job
    problem = BENCHMARKS[bench](seed)
    snaps = [s for s in switch_points(problem, seed, budget) if s.spent+window <= budget]
    if len(snaps) > moments: snaps = [snaps[round(i*(len(snaps)-1)/(moments-1))] for i in range(moments)]
    out = []
    for i, snap in enumerate(snaps):
        result = {'benchmark': bench, 'seed': seed, 'spent': snap.spent, 'stall': snap.stall,
                  'before': problem.display(snap.f_best)}
        for arm in ('switch', 'stay'):
            gains = []
            for k in range(forks):
                policy = copy.deepcopy(snap.policy) if arm == 'switch' else Fixed({'edit': 1}, seed, 'stay')
                fork = snap.fork(policy, f'{arm}/{i}/{k}', window).run()
                gains.append(problem.oriented(problem.display(fork.f_best)-problem.display(snap.f_best)))
            result[arm] = {'p_improve': sum(g > 0 for g in gains)/forks, 'mean_gain': statistics.fmean(gains)}
        out.append(result)
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--seeds', default='2000:2040')
    parser.add_argument('--budget', type=float, default=3000.)
    parser.add_argument('--window', type=float, default=300.)
    parser.add_argument('--forks', type=int, default=20)
    parser.add_argument('--moments', type=int, default=6, help='switch points sampled per seed')
    parser.add_argument('--workers', type=int, default=6)
    parser.add_argument('--out', default='experiments/strategist-v1')
    args = parser.parse_args()
    lo, hi = map(int, args.seeds.split(':'))
    jobs = [(b, s, args.budget, args.window, args.forks, args.moments) for b in BENCHMARK_SET for s in range(lo, hi)]
    with Pool(args.workers) as pool: moments = [m for ms in pool.map(fork_seed, jobs) for m in ms]
    summary = {}
    for bench in BENCHMARK_SET:
        ms = [m for m in moments if m['benchmark'] == bench]
        summary[bench] = {
            'moments': len(ms), 'seeds': len({m['seed'] for m in ms}),
            'p_improve': {arm: statistics.fmean(m[arm]['p_improve'] for m in ms) for arm in ('switch', 'stay')},
            'mean_gain': {arm: statistics.fmean(m[arm]['mean_gain'] for m in ms) for arm in ('switch', 'stay')},
            'p_improve_difference': paired([m['switch']['p_improve']-m['stay']['p_improve'] for m in ms]),
            'gain_difference': paired([m['switch']['mean_gain']-m['stay']['mean_gain'] for m in ms])}
        s = summary[bench]
        print(f"{bench}: {s['moments']} switch points from {s['seeds']} seeds; P(new best within "
              f"{args.window:g} cu) switch={s['p_improve']['switch']:.3f} stay={s['p_improve']['stay']:.3f} "
              f"diff CI={[round(x, 3) for x in s['p_improve_difference']['interval95']]}", flush=True)
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    (out/'forks.json').write_text(json.dumps({'config': vars(args), 'summary': summary, 'moments': moments}, indent=2)+'\n')


if __name__ == '__main__': main()
