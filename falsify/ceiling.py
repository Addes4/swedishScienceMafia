"""bp-ceiling-v1: is the best-fit ceiling the representation or the instances? No LLM calls.

Search linear bin-scoring policies (the Falsify feature space) in three instance regimes with
matched budgets, then audit them and FunSearch's fixed code heuristics on fresh instances that
are generated only after every search has finished. See experiments/bp-ceiling-v1/PROTOCOL.md.

    python -m falsify.ceiling search --regime weibull5k --representation linear20 --optimizer hc --seed 0
    python -m falsify.ceiling audit --out experiments/bp-ceiling-v1      # after all runs exist
    python -m falsify.ceiling sweep --out experiments/bp-ceiling-v1      # length sweep, fixed heuristics
    python -m falsify.ceiling tune-ab --out experiments/bp-ceiling-v1    # ab-heuristic grid per seed
    python -m falsify.ceiling headroom --out experiments/bp-ceiling-v1   # best fit vs exact optimum, n = 80
Fan-out of the searches on Modal: falsify/ceiling_modal.py.
"""
import argparse
import hashlib
import json
import random
import shutil
import statistics
import time
from pathlib import Path

from .contextual import CONTEXT_BEST_FIT, anchors
from .core import SHIFT_FAMILIES, TRAIN_FAMILIES, read_json, write_json
from .funsearch_heuristics import AB_VARIANTS, HEURISTICS, SOURCE
from .longpack import (Instance, falsify_items, l2_bound, pack_ab, pack_linear, pack_priority, pack_rule,
                       weibull_items)

ITEM_STEPS_PER_EVALUATION = 20000
REGIMES = {'falsify80': 80, 'weibull500': 500, 'weibull5k': 5000}
REPRESENTATIONS = {'linear20': 20, 'linear21': 21}
OPTIMIZERS = ['hc', 'cmaes']
TRAIN_NAMESPACE = 'bp-ceiling-v1/train'
AUDIT_NAMESPACE = 'bp-ceiling-v1/audit'
AUDIT_COUNTS = {'falsify80': 2500, 'weibull500': 400, 'weibull5k': 40}
SHIFT_AUDIT_COUNT = 1500
BOOTSTRAP_SEED = 20261003


def regime_cases(regime, namespace, seed, count, families=TRAIN_FAMILIES):
    """count instances of a regime; falsify families cycle in order."""
    n = REGIMES[regime]
    if regime.startswith('falsify'):
        return [Instance(falsify_items(f'{namespace}/{regime}/{seed}/{i}', families[i % len(families)], n),
                         family=families[i % len(families)]) for i in range(count)]
    return [Instance(weibull_items(f'{seed}/{i}', n, namespace=f'{namespace}/{regime}'), family='weibull')
            for i in range(count)]


def training_cases(regime, seed):
    return regime_cases(regime, TRAIN_NAMESPACE, seed, ITEM_STEPS_PER_EVALUATION // REGIMES[regime])


def start_weights(representation):
    return list(CONTEXT_BEST_FIT) + [0.] * (REPRESENTATIONS[representation] - 20)


def anchor_bank(representation):
    pad = [0.] * (REPRESENTATIONS[representation] - 20)
    return [list(a['weights']) + pad for a in anchors()]


def mutate(weights, rng):
    """falsify.contextual.mutate_contextual for any number of weights (identical for 20)."""
    child = list(weights)
    for _ in range(rng.choice([1, 1, 2, 3, 5])):
        j = rng.randrange(len(child))
        child[j] = max(-12., min(12., child[j] + rng.gauss(0, rng.choice([.1, .3, 1., 3.]))))
    return child


def total_bins(weights, cases):
    return sum(pack_linear(weights, c) for c in cases)


def hill_climb(cases, representation, seed, evaluations):
    """gated_search's proposal stream with fixed-only promotion: per generation best-fit, the
    explorer, a mutation of the explorer and a mutation of a random anchor."""
    start = start_weights(representation)
    bank = anchor_bank(representation)
    explorer, deployed = list(start), list(start)
    deployed_score = total_bins(start, cases)
    reference = deployed_score
    digest = hashlib.sha256()
    scores_log, promotions = [], []
    for generation in range(evaluations // 4):
        rng = random.Random(80000000 + seed * 100000 + generation)
        common = [list(start), list(explorer), mutate(explorer, rng), mutate(rng.choice(bank), rng)]
        digest.update(json.dumps(common).encode())
        scores = [total_bins(w, cases) for w in common]
        scores_log.append([s - reference for s in scores])
        eligible = [i for i, s in enumerate(scores) if s <= deployed_score]
        if eligible:
            best = min(scores[i] for i in eligible)
            tied = [i for i in eligible if scores[i] == best]
            selected = random.Random(110000000 + seed * 100000 + generation).choice(tied)
            if common[selected] != deployed:
                promotions.append({'generation': generation, 'train_excess': best - reference,
                                   'weights': common[selected]})
            deployed, deployed_score = list(common[selected]), best
        best = min(scores)
        explorer = list(common[rng.choice([i for i, s in enumerate(scores) if s == best])])
    return {'weights': deployed, 'train_excess_bins': deployed_score - reference, 'reference_bins': reference,
            'evaluations': 4 * (evaluations // 4), 'proposal_sha256': digest.hexdigest(),
            'score_log': scores_log, 'promotions': promotions}


def cmaes(cases, representation, seed, evaluations):
    """CMA-ES from best-fit (sigma 0.5, bounds [-12, 12]); deploys the best evaluated policy,
    best-fit included, ties to the earliest."""
    import cma
    start = start_weights(representation)
    reference = total_bins(start, cases)
    deployed, deployed_score = list(start), reference
    es = cma.CMAEvolutionStrategy(start, 0.5, {'seed': 1000 + seed, 'bounds': [-12, 12], 'verbose': -9,
                                               'maxfevals': evaluations - 1, 'tolfun': 0, 'tolx': 0,
                                               'tolflatfitness': 10 ** 9, 'tolstagnation': 10 ** 9})
    used, log, promotions = 1, [], []
    while used < evaluations:
        xs = es.ask()
        xs = xs[:evaluations - used]
        scores = [total_bins([float(v) for v in x], cases) for x in xs]
        used += len(xs)
        for x, s in zip(xs, scores):
            if s < deployed_score:
                deployed, deployed_score = [float(v) for v in x], s
                promotions.append({'evaluation': used, 'train_excess': s - reference, 'weights': deployed})
        log.append([min(scores) - reference, statistics.median(scores) - reference, float(es.sigma)])
        if len(xs) < es.popsize:
            break
        es.tell(xs, scores)
    return {'weights': deployed, 'train_excess_bins': deployed_score - reference, 'reference_bins': reference,
            'evaluations': used, 'score_log': log, 'promotions': promotions}


def run_search(regime, representation, optimizer, seed, evaluations):
    started = time.monotonic()
    cases = training_cases(regime, seed)
    search = hill_climb if optimizer == 'hc' else cmaes
    result = search(cases, representation, seed, evaluations)
    item_steps = sum(len(c) for c in cases)
    result.update({'regime': regime, 'representation': representation, 'optimizer': optimizer, 'seed': seed,
                   'training_instances': len(cases), 'item_steps_per_evaluation': item_steps,
                   'search_item_steps': item_steps * result['evaluations'],
                   'training_sha256': hashlib.sha256(json.dumps([c.items for c in cases]).encode()).hexdigest(),
                   'seconds': time.monotonic() - started})
    return result


def run_name(regime, representation, optimizer, seed):
    return f'{regime}-{representation}-{optimizer}-{seed}'


AB_GRID = [(v, a, b) for v in AB_VARIANTS for a in range(16) for b in range(a + 1, 41)]


def tune_ab(regime, seed):
    """Grid-search Herrmann & Pallez's ab-heuristics (3 variants, a in 0..15, b in a+1..40) on
    the same training set as search seed `seed`; deploy the lowest total, best fit included,
    ties to best fit and then to grid order."""
    started = time.monotonic()
    cases = training_cases(regime, seed)
    reference = sum(pack_rule(c, 'best_fit') for c in cases)
    totals = [sum(pack_ab(c, v, a, b) for c in cases) for v, a, b in AB_GRID]
    best = min(range(len(AB_GRID)), key=lambda i: totals[i])
    policy = ({'ab': AB_GRID[best][0], 'a': AB_GRID[best][1], 'b': AB_GRID[best][2]}
              if totals[best] < reference else 'best_fit')
    return {'regime': regime, 'representation': 'ab_rules', 'optimizer': 'grid', 'seed': seed, 'weights': policy,
            'train_excess_bins': min(totals[best], reference) - reference, 'reference_bins': reference,
            'evaluations': len(AB_GRID) + 1, 'grid_totals_minus_best_fit': [t - reference for t in totals],
            'training_sha256': hashlib.sha256(json.dumps([c.items for c in cases]).encode()).hexdigest(),
            'seconds': time.monotonic() - started}


def snapshot_source(out, name='source'):
    source = Path(out) / name
    source.mkdir(parents=True, exist_ok=True)
    for p in Path(__file__).parent.iterdir():
        if p.suffix in ['.py', '.cpp']:
            shutil.copyfile(p, source / p.name)
    write_json(Path(out) / f'{name}_hashes.json',
               {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(source.iterdir())})


# ---------------------------------------------------------------- audit (after all searches)

def bootstrap(values, rng_seed=BOOTSTRAP_SEED, draws=10000):
    rng = random.Random(rng_seed)
    means = sorted(statistics.mean(rng.choices(values, k=len(values))) for _ in range(draws))
    return [means[int(.025 * draws)], means[int(.975 * draws) - 1]]


def excess_percent(bins, bounds):
    return 100 * (sum(bins) - sum(bounds)) / sum(bounds)


def audit_cases(regime):
    cases = regime_cases(regime, AUDIT_NAMESPACE, 'final', AUDIT_COUNTS[regime])
    if regime.startswith('falsify'):
        cases += regime_cases(regime, AUDIT_NAMESPACE, 'shift', SHIFT_AUDIT_COUNT, SHIFT_FAMILIES)
    return cases


def decision_stats(items, assignment, capacity=100):
    """Share of items put in a new bin although an open bin could take them, and share of
    used bins that end exactly full."""
    import numpy as np
    remaining = np.full(len(items), capacity)
    opened = eager = 0
    for x, b in zip(items, assignment):
        if b >= opened:
            eager += bool((remaining[:opened] >= x).any())
            opened = b + 1
        remaining[b] -= x
    used = remaining[remaining < capacity]
    return {'new_bin_while_open_fits': eager / len(items), 'full_bins': float((used == 0).mean())}


def policy_trace(policy, case):
    if isinstance(policy, dict):
        return pack_ab(case, policy['ab'], policy['a'], policy['b'], trace=True)[1]
    if isinstance(policy, list):
        return pack_linear(policy, case, trace=True)[1]
    if policy in ('best_fit', 'first_fit', 'worst_fit'):
        return pack_rule(case, policy, trace=True)[1]
    return pack_priority(HEURISTICS[policy], case, trace=True)[1]


def policy_bins(policy, cases):
    if isinstance(policy, dict):
        return [pack_ab(c, policy['ab'], policy['a'], policy['b']) for c in cases]
    if isinstance(policy, list):
        return [pack_linear(policy, c) for c in cases]
    if policy in ('best_fit', 'first_fit', 'worst_fit'):
        return [pack_rule(c, policy) for c in cases]
    return [pack_priority(HEURISTICS[policy], c) for c in cases]


def compare(bins, reference, bounds, cases, families):
    keep = [i for i, c in enumerate(cases) if c.family in families]
    b, r, lb = [bins[i] for i in keep], [reference[i] for i in keep], [bounds[i] for i in keep]
    return {'excess_percent': excess_percent(b, lb), 'delta_pp': excess_percent(b, lb) - excess_percent(r, lb),
            'mean_excess_bins_vs_best_fit': statistics.mean(x - y for x, y in zip(b, r)),
            'wins': sum(x < y for x, y in zip(b, r)), 'ties': sum(x == y for x, y in zip(b, r)),
            'losses': sum(x > y for x, y in zip(b, r)), 'n': len(keep)}


def instance_ci(bins, reference, bounds, cases, families):
    """Bootstrap over audit instances of the pp difference against best fit."""
    keep = [i for i, c in enumerate(cases) if c.family in families]
    mean_bound = statistics.mean(bounds[i] for i in keep)
    diffs = [100 * (bins[i] - reference[i]) / mean_bound for i in keep]
    return bootstrap(diffs)


def audit(out):
    out = Path(out)
    if (out / 'summary.json').exists():
        raise SystemExit('audit already completed')
    config = read_json(out / 'config.json')
    runs = {}
    for regime in REGIMES:
        for representation in REPRESENTATIONS:
            for optimizer in OPTIMIZERS:
                for seed in range(config['seeds']):
                    name = run_name(regime, representation, optimizer, seed)
                    runs[name] = read_json(out / 'runs' / f'{name}.json.gz')
                    assert runs[name]['evaluations'] == config['evaluations'], name
        for seed in range(config['seeds']):
            runs[f'ab-{regime}-{seed}'] = read_json(out / 'runs' / f'ab-{regime}-{seed}.json.gz')
    snapshot_source(out, 'audit_source')
    # Audit instances are created only here, after every search result exists.
    results, fixed = [], {}
    for regime in REGIMES:
        cases = audit_cases(regime)
        bounds = [l2_bound(c.items) for c in cases]
        reference = policy_bins('best_fit', cases)
        families = ['weibull'] if regime.startswith('weibull') else TRAIN_FAMILIES
        groups = {'primary': families}
        if regime.startswith('falsify'):
            groups.update({'shift': SHIFT_FAMILIES, **{f: [f] for f in TRAIN_FAMILIES + SHIFT_FAMILIES}})
        fixed[regime] = {'n_instances': len(cases), 'items_per_instance': REGIMES[regime],
                         'audit_sha256': hashlib.sha256(json.dumps([c.items for c in cases]).encode()).hexdigest()}
        for policy in ['best_fit', 'first_fit', 'funsearch_weibull', 'funsearch_or']:
            t0 = time.monotonic()
            bins = reference if policy == 'best_fit' else policy_bins(policy, cases)
            fixed[regime][policy] = {g: {**compare(bins, reference, bounds, cases, fam),
                                         'delta_pp_ci95_instances': instance_ci(bins, reference, bounds, cases, fam)}
                                     for g, fam in groups.items()}
            fixed[regime][policy]['seconds'] = time.monotonic() - t0
            print(regime, policy, round(fixed[regime][policy]['primary']['delta_pp'], 4), flush=True)
        for name, run in runs.items():
            if run['regime'] != regime:
                continue
            bins = policy_bins(run['weights'], cases)
            sample = [c for c in cases if c.family in families][:10]
            stats = [decision_stats(c.items, policy_trace(run['weights'], c)) for c in sample]
            results.append({k: run[k] for k in ['regime', 'representation', 'optimizer', 'seed', 'weights',
                                                 'train_excess_bins', 'reference_bins', 'evaluations', 'seconds']}
                           | {'audit': {g: compare(bins, reference, bounds, cases, fam) for g, fam in groups.items()},
                              'decisions': {k: statistics.mean(x[k] for x in stats) for k in stats[0]}})
    cells = []
    arms = [(rep, opt) for rep in REPRESENTATIONS for opt in OPTIMIZERS] + [('ab_rules', 'grid')]
    for regime in REGIMES:
        for representation, optimizer in arms:
                rs = [r for r in results if (r['regime'], r['representation'], r['optimizer']) ==
                      (regime, representation, optimizer)]
                deltas = [r['audit']['primary']['delta_pp'] for r in rs]
                train = [100 * r['train_excess_bins'] / r['reference_bins'] for r in rs]
                cells.append({'regime': regime, 'representation': representation, 'optimizer': optimizer,
                              'seeds': len(rs), 'delta_pp_mean': statistics.mean(deltas),
                              'delta_pp_ci95_seeds': bootstrap(deltas), 'delta_pp_min': min(deltas),
                              'delta_pp_max': max(deltas), 'seeds_better_than_best_fit': sum(d < 0 for d in deltas),
                              'seeds_identical_to_best_fit': sum(r['audit']['primary']['wins'] == 0 and
                                                                 r['audit']['primary']['losses'] == 0 for r in rs),
                              'train_change_percent_of_best_fit_bins_mean': statistics.mean(train),
                              'new_bin_while_open_fits_mean': statistics.mean(
                                  r['decisions']['new_bin_while_open_fits'] for r in rs),
                              'full_bins_mean': statistics.mean(r['decisions']['full_bins'] for r in rs),
                              'mean_seconds': statistics.mean(r['seconds'] for r in rs)})
                if regime.startswith('falsify'):
                    shift = [r['audit']['shift']['delta_pp'] for r in rs]
                    cells[-1]['shift_delta_pp_mean'] = statistics.mean(shift)
                    cells[-1]['shift_delta_pp_ci95_seeds'] = bootstrap(shift)
    control = positive_control(out)
    write_json(out / 'audit.json', results)
    write_json(out / 'summary.json', {'decision_table': decision_table(cells, fixed), 'cells': cells,
                                      'fixed_heuristics': fixed, 'positive_control': control,
                                      'funsearch_source': SOURCE, 'bootstrap_seed': BOOTSTRAP_SEED})
    for c in cells:
        print(c['regime'], c['representation'], c['optimizer'], round(c['delta_pp_mean'], 4),
              [round(x, 4) for x in c['delta_pp_ci95_seeds']], flush=True)


def decision_table(cells, fixed):
    """Headline per regime: delta (pp of the L2 bound, negative = better than best fit) with its
    95% interval, and whether the interval lies entirely below zero."""
    table = {}
    for regime in REGIMES:
        row = {'best_fit_excess_percent': fixed[regime]['best_fit']['primary']['excess_percent']}
        for c in cells:
            if c['regime'] == regime:
                ci = c['delta_pp_ci95_seeds']
                row[f"{c['representation']}_{c['optimizer']}"] = {
                    'delta_pp': c['delta_pp_mean'], 'ci95_over_seeds': ci, 'headroom': ci[1] < 0}
        for policy in ['first_fit', 'funsearch_weibull', 'funsearch_or']:
            f = fixed[regime][policy]['primary']
            row[policy] = {'delta_pp': f['delta_pp'], 'ci95_over_instances': f['delta_pp_ci95_instances'],
                           'headroom': f['delta_pp_ci95_instances'][1] < 0}
        table[regime] = row
    return table


def positive_control(out):
    data = read_json(Path(out) / 'funsearch_weibull5k_test.json.gz')['instances']
    items = [v['items'] for v in data.values()]
    bounds = [l2_bound(x) for x in items]
    rows = {}
    for policy in ['best_fit', 'first_fit', 'funsearch_weibull', 'funsearch_or']:
        bins = [pack_rule(x, policy) if policy in ('best_fit', 'first_fit') else pack_priority(HEURISTICS[policy], x)
                for x in items]
        rows[policy] = {'mean_bins': statistics.mean(bins), 'excess_percent_l2': excess_percent(bins, bounds)}
    rows['mean_l2_bound'] = statistics.mean(bounds)
    rows['published'] = {'best_fit': 3.98, 'first_fit': 4.23, 'funsearch_weibull': 0.68}
    return rows


# ---------------------------------------------------------------- length sweep (fixed heuristics)

SWEEP_LENGTHS = [80, 200, 500, 1000, 2000, 5000, 10000]
SWEEP_ITEMS = 100000


def sweep(out):
    out = Path(out)
    rows = []
    for family in ['weibull'] + TRAIN_FAMILIES:
        for n in SWEEP_LENGTHS if family == 'weibull' else [80, 500, 5000]:
            count = max(SWEEP_ITEMS // n, 10)
            if family == 'weibull':
                cases = [Instance(weibull_items(f'{n}/{i}', n, namespace='bp-ceiling-v1/sweep'), 'weibull')
                         for i in range(count)]
            else:
                cases = [Instance(falsify_items(f'bp-ceiling-v1/sweep/{family}/{n}/{i}', family, n), family)
                         for i in range(count)]
            bounds = [l2_bound(c.items) for c in cases]
            reference = policy_bins('best_fit', cases)
            row = {'family': family, 'n': n, 'instances': count,
                   'best_fit_excess_percent': excess_percent(reference, bounds)}
            policies = ['first_fit', 'funsearch_weibull'] + (['funsearch_or'] if n <= 5000 else [])
            for policy in ['best_fit'] + policies:
                if policy == 'best_fit':
                    traces, bins = [policy_trace(policy, c) for c in cases[:10]], reference
                else:
                    traces = [policy_trace(policy, c) for c in cases]
                    bins = [len(set(t)) for t in traces]
                stats = [decision_stats(c.items, t) for c, t in zip(cases, traces[:10])]
                row[policy] = {'excess_percent': excess_percent(bins, bounds),
                               'delta_pp': excess_percent(bins, bounds) - row['best_fit_excess_percent'],
                               'delta_pp_ci95_instances': instance_ci(bins, reference, bounds, cases, [family]),
                               **{k: statistics.mean(x[k] for x in stats) for k in stats[0]}}
            rows.append(row)
            print(family, n, round(row['best_fit_excess_percent'], 3),
                  {p: round(row[p]['delta_pp'], 3) for p in policies}, flush=True)
    write_json(out / 'length_sweep.json', rows)


def headroom(out, per_family=200):
    """Best fit against the exact offline optimum on fresh 80-item instances (namespace
    bp-ceiling-v1/headroom): the most any online rule could gain there."""
    from .optimum import optimal_bins
    rows = {}
    for family in TRAIN_FAMILIES + ['weibull']:
        bf, l2, lo, hi = [], [], [], []
        for i in range(per_family):
            items = (weibull_items(f'80/{i}', 80, namespace='bp-ceiling-v1/headroom') if family == 'weibull'
                     else falsify_items(f'bp-ceiling-v1/headroom/{family}/{i}', family, 80))
            low, high = optimal_bins(items)
            bf.append(pack_rule(items, 'best_fit'))
            l2.append(l2_bound(items))
            lo.append(low)
            hi.append(high)
        proven = [i for i in range(per_family) if lo[i] == hi[i]]
        rows[family] = {'instances': per_family, 'optimum_proven': len(proven),
                        'best_fit_excess_percent_over_l2': excess_percent(bf, l2),
                        'best_fit_excess_percent_over_optimum': excess_percent([bf[i] for i in proven],
                                                                               [hi[i] for i in proven]),
                        'instances_where_best_fit_is_optimal': sum(bf[i] == hi[i] for i in proven),
                        'mean_bins_best_fit_minus_optimum': statistics.mean(bf[i] - hi[i] for i in proven)}
        print(family, rows[family], flush=True)
    write_json(Path(out) / 'headroom_80.json', rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['search', 'tune-ab', 'audit', 'sweep', 'headroom'],
                        help='search: one linear-policy search; tune-ab: grid-tune the ab-heuristics for '
                             'every regime and seed; audit: fresh-instance audit of everything; '
                             'sweep: length sweep of the fixed heuristics; headroom: best fit against '
                             'the exact optimum on 80-item instances')
    parser.add_argument('--out', default='experiments/bp-ceiling-v1')
    parser.add_argument('--regime', choices=list(REGIMES))
    parser.add_argument('--representation', choices=list(REPRESENTATIONS))
    parser.add_argument('--optimizer', choices=OPTIMIZERS)
    parser.add_argument('--seed', type=int, default=0)
    parser.add_argument('--evaluations', type=int, default=8000)
    args = parser.parse_args()
    if args.command == 'search':
        result = run_search(args.regime, args.representation, args.optimizer, args.seed, args.evaluations)
        name = run_name(args.regime, args.representation, args.optimizer, args.seed)
        write_json(Path(args.out) / 'runs' / f'{name}.json.gz', result)
        print(name, result['train_excess_bins'], round(result['seconds'], 1))
    elif args.command == 'tune-ab':
        seeds = read_json(Path(args.out) / 'config.json')['seeds']
        for regime in REGIMES:
            for seed in range(seeds):
                path = Path(args.out) / 'runs' / f'ab-{regime}-{seed}.json.gz'
                if not path.exists():
                    result = tune_ab(regime, seed)
                    write_json(path, result)
                    print(path.name, result['weights'], result['train_excess_bins'], round(result['seconds'], 1),
                          flush=True)
    elif args.command == 'audit':
        audit(args.out)
    elif args.command == 'sweep':
        sweep(args.out)
    else:
        headroom(args.out)


if __name__ == '__main__':
    main()
