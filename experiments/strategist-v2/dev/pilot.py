"""Pilot run before the dev grid was fixed (disclosed in PROTOCOL.md): dev seeds 40-49 only.

    /Users/adriansohrabi/.venvs/ssm/bin/python experiments/strategist-v2/dev/pilot.py
"""
import statistics
import sys
from multiprocessing import Pool
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from strategist import v2                     # noqa: E402
from strategist.search import COSTS           # noqa: E402

CONFIGS = [('v1', {'kind': 'v1'})] + [(l, v2.v2_spec(l.split('/'))) for l in [
    'gate02/inherit/point', 'gate10/inherit/point', 'off/cap16/point', 'off/fixed16/point', 'off/cap64/point',
    'off/inherit/improving16', 'off/inherit/improving64', 'off/inherit/yield64', 'off/inherit/upper90',
    'gate10/cap16/improving64', 'gate02/fixed16/improving64']] + [('patience_64', {'kind': 'patience', 'T': 64})]


def job(bench_seed):
    bench, seed = bench_seed
    return v2.run_job({'phase': 'pilot', 'bench': bench, 'seed': seed, 'budget': 3000., 'costs': COSTS,
                       'arms': CONFIGS})


if __name__ == '__main__':
    with Pool(2) as pool:
        records = [r for rs in pool.map(job, [(b, s) for b in v2.BENCHES for s in range(40, 50)]) for r in rs]
    for bench in v2.BENCHES:
        print(bench)
        for name, _ in CONFIGS:
            rs = [r for r in records if r['benchmark'] == bench and r['arm'] == name]
            n = sum(sum(r['ops'].values()) for r in rs)
            print(f"  {name:28s} mean={statistics.fmean(r['final'] for r in rs):.5g} "
                  f"crossover share={sum(r['ops']['crossover'] for r in rs)/n:.2f} "
                  f"restarts={statistics.fmean(r['ops']['restart'] for r in rs):.1f}")
