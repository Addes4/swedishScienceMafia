"""Seed-paired, equal-cost comparison of switching policies across benchmarks.

    python -m strategist.experiment --seeds 1000:1200 --out experiments/strategist-v1
"""
import argparse
import json
import statistics
import time
from multiprocessing import Pool
from pathlib import Path
from .controller import OPS, Adaptive, Fixed, Patience, shuffled
from .problems import BENCHMARKS
from .search import COSTS, UNIFORM_COSTS, Run
from .stats import holm, paired

COST_MODELS = {'llm_proxy': COSTS, 'uniform': UNIFORM_COSTS}
PATIENCE = (16, 64, 256)
PRIMARY = ('timing_shuffled', 'static_mix', 'uniform', 'edits_only', 'patience_best')


def policies(costs, seed):
    """Every arm except timing_shuffled, which replays the paired adaptive run."""
    out = {
        'adaptive': Adaptive(costs, seed),
        'adaptive_blind': Adaptive(costs, seed, contextual=False, name='adaptive_blind'),
        'adaptive_no_crossover': Adaptive(costs, seed, moves=('edit', 'rewrite'), name='adaptive_no_crossover'),
        'edits_only': Fixed({'edit': 1}, seed, 'edits_only'),
        'uniform': Fixed({op: 1 for op in OPS}, seed, 'uniform'),
        'static_mix': Fixed({'edit': .6, 'rewrite': .3, 'crossover': .1}, seed, 'static_mix'),
    }
    out.update({f'patience_{t}': Patience(t) for t in PATIENCE})
    return out


def record(bench, seed, arm, run, checkpoints, seconds):
    p = run.problem
    return {'benchmark': bench, 'seed': seed, 'arm': arm, 'final': p.display(run.f_best),
            'curve': [p.display(f) for f in run.best_at(checkpoints)], 'spent': run.spent, 'steps': run.steps,
            'ops': {op: run.ops.count(op) for op in run.costs}, 'usage': run.usage if arm == 'adaptive' else None,
            'seconds': seconds}


def run_seed(job):
    bench, seed, budget, cost_model = job
    costs, problem = COST_MODELS[cost_model], BENCHMARKS[bench](seed)
    checkpoints = [budget*i/30 for i in range(1, 31)]
    out, adaptive_ops = [], None
    for arm, policy in policies(costs, seed).items():
        start = time.monotonic()
        run = Run(problem, policy, budget, seed, costs).run()
        out.append(record(bench, seed, arm, run, checkpoints, time.monotonic()-start))
        if arm == 'adaptive': adaptive_ops = run.ops
    start = time.monotonic()
    run = Run(problem, shuffled(adaptive_ops, seed), budget, seed, costs).run()
    out.append(record(bench, seed, 'timing_shuffled', run, checkpoints, time.monotonic()-start))
    return out


def summarise(records, benchmarks):
    summary = {}
    for bench in benchmarks:
        rs = [r for r in records if r['benchmark'] == bench]
        sign = 1 if BENCHMARKS[bench](0).higher_is_better else -1
        by_arm = {}
        for r in rs: by_arm.setdefault(r['arm'], {})[r['seed']] = r
        seeds = sorted(by_arm['adaptive'])
        arms = {}
        for arm, runs in by_arm.items():
            finals = [runs[s]['final'] for s in seeds]
            total = sum(sum(runs[s]['ops'].values()) for s in seeds)
            arms[arm] = {'mean': statistics.fmean(finals), 'median': statistics.median(finals),
                         'sd': statistics.stdev(finals) if len(finals) > 1 else 0.,
                         'auc': statistics.fmean(statistics.fmean(runs[s]['curve']) for s in seeds),
                         'curve_median': [statistics.median(runs[s]['curve'][i] for s in seeds) for i in range(30)],
                         'curve_q25': [sorted(runs[s]['curve'][i] for s in seeds)[len(seeds)//4] for i in range(30)],
                         'curve_q75': [sorted(runs[s]['curve'][i] for s in seeds)[3*len(seeds)//4] for i in range(30)],
                         'op_share': {op: sum(runs[s]['ops'][op] for s in seeds)/total for op in runs[seeds[0]]['ops']},
                         'restarts_per_run': statistics.fmean(runs[s]['ops']['restart'] for s in seeds)}
        best_patience = max((f'patience_{t}' for t in PATIENCE), key=lambda a: sign*arms[a]['mean'])
        by_arm['patience_best'] = by_arm[best_patience]
        comparisons = {}
        for arm in by_arm:
            if arm == 'adaptive': continue
            diffs = [sign*(by_arm['adaptive'][s]['final']-by_arm[arm][s]['final']) for s in seeds]
            auc = [sign*(statistics.fmean(by_arm['adaptive'][s]['curve'])-statistics.fmean(by_arm[arm][s]['curve']))
                   for s in seeds]
            comparisons[arm] = {'final': paired(diffs), 'auc': paired(auc)}
        for metric in ('final', 'auc'):
            for arm, p in zip(PRIMARY, holm([comparisons[a][metric]['sign_p'] for a in PRIMARY])):
                comparisons[arm][metric]['holm_p'] = p
        usage = {}
        for s in seeds:
            for state, counts in (by_arm['adaptive'][s]['usage'] or {}).items():
                row = usage.setdefault(state, dict.fromkeys(counts, 0))
                for op, n in counts.items(): row[op] += n
        summary[bench] = {'higher_is_better': sign > 0, 'seeds': len(seeds), 'arms': arms,
                          'patience_best': best_patience, 'comparisons': comparisons, 'adaptive_usage': usage}
    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--benchmarks', default=','.join(BENCHMARKS))
    parser.add_argument('--seeds', default='1000:1200', help='start:stop, half-open')
    parser.add_argument('--budget', type=float, default=3000.)
    parser.add_argument('--costs', choices=COST_MODELS, default='llm_proxy')
    parser.add_argument('--workers', type=int, default=6)
    parser.add_argument('--out', default='experiments/strategist-v1')
    args = parser.parse_args()
    benchmarks = args.benchmarks.split(',')
    lo, hi = map(int, args.seeds.split(':'))
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    (out/'config.json').write_text(json.dumps({**vars(args), 'cost_table': COST_MODELS[args.costs],
                                               'patience': PATIENCE, 'primary': PRIMARY}, indent=2)+'\n')
    jobs = [(b, s, args.budget, args.costs) for b in benchmarks for s in range(lo, hi)]
    records, start = [], time.monotonic()
    with Pool(args.workers) as pool, open(out/'runs.jsonl', 'w') as log:
        for i, rs in enumerate(pool.imap_unordered(run_seed, jobs), 1):
            for r in rs: log.write(json.dumps(r)+'\n')
            records.extend(rs)
            if i % 50 == 0 or i == len(jobs):
                print(f'{i}/{len(jobs)} seed-jobs  {time.monotonic()-start:.0f}s', flush=True)
    summary = summarise(records, benchmarks)
    (out/'summary.json').write_text(json.dumps(summary, indent=2)+'\n')
    for bench, s in summary.items():
        print(f'\n== {bench} ({s["seeds"]} seeds; positive difference = adaptive better)')
        for arm, a in sorted(s['arms'].items(), key=lambda kv: -kv[1]['mean']*(1 if s['higher_is_better'] else -1)):
            c = s['comparisons'].get(arm, {}).get('final')
            extra = (f"  diff={c['mean']:+.4g} CI=[{c['interval95'][0]:+.3g},{c['interval95'][1]:+.3g}] "
                     f"W/T/L={c['wins']}/{c['ties']}/{c['losses']} p={c['sign_p']:.2g}") if c else ''
            print(f'  {arm:22s} mean={a["mean"]:.5g} median={a["median"]:.5g}{extra}')
        c = s['comparisons']['patience_best']['final']
        print(f"  adaptive vs patience_best ({s['patience_best']}): diff={c['mean']:+.4g} "
              f"W/T/L={c['wins']}/{c['ties']}/{c['losses']} holm_p={c['holm_p']:.2g}")


if __name__ == '__main__': main()
