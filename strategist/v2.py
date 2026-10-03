"""Strategist v2: v1's three proposed fixes, developed on many seeds, validated once, confirmed once.

    python -m strategist.v2 dev --modal                 # grid on dev seeds 40-239 -> dev/selection.json
    python -m strategist.v2 freeze                      # dev/selection.json -> frozen.json (commit it)
    python -m strategist.v2 validate --modal            # frozen design once on validation seeds 240-439
    python -m strategist.v2 confirm --modal             # every arm once on seeds 3000-3199, proxy costs
    python -m strategist.v2 confirm --costs uniform --modal     # cost sensitivity (patience re-tuned on dev)
    python -m strategist.v2 confirm --costs measured --modal    # after filling costs/measured_llm.json
    python -m strategist.v2 forks --modal               # counterfactual forks, v1 and v2, seeds 4000-4039
    python -m strategist.v2 report                      # tables.md, headline in summary.json, figure
    python -m strategist.v2 cost                        # cost.json: Modal spend, runs, evaluations

Without --modal, jobs run locally on --workers processes (default 2).
"""
import argparse
import gzip
import hashlib
import json
import statistics
import sys
import time
import copy
from pathlib import Path
from .controller import Adaptive, AdaptiveV2, Fixed, Patience, shuffled
from .costs import CostTableError, load as load_costs
from .problems import BENCHMARKS
from .search import Run
from .stats import cluster_interval, holm, paired

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT/'experiments'/'strategist-v2'
BENCHES = ('labs', 'heilbronn', 'nk')
BUDGET = 3000.
DEV, VALIDATION = range(40, 240), range(240, 440)
CONFIRM, FORK_SEEDS = range(3000, 3200), range(4000, 4040)
USED_BY_V1 = (range(0, 40), range(1000, 1200), range(2000, 2040))   # never used for v2 decisions
PATIENCE_GRID = (8, 16, 32, 64, 128, 256, 512, 1024)

# The three changes, one factor each. The first level of each factor is v1's behaviour.
XO = {'off': {}, 'gate02': {'xo_gate': True, 'xo_probe': .02}, 'gate10': {'xo_gate': True, 'xo_probe': .1},
      'none': {'moves': ('edit', 'rewrite')}}          # 'none' = v1's no-crossover ablation; reference only
EXCURSION = {'inherit': {}, 'cap16': {'excursion': 'cap', 'excursion_len': 16},
             'cap64': {'excursion': 'cap', 'excursion_len': 64},
             'fixed16': {'excursion': 'fixed', 'excursion_len': 16},
             'fixed64': {'excursion': 'fixed', 'excursion_len': 64}}
LEAVE = {'point': {}, 'improving16': {'leave_test': 'improving', 'window': 16},
         'improving64': {'leave_test': 'improving', 'window': 64},
         'yield64': {'leave_test': 'yield', 'window': 64},
         'upper90': {'leave_test': 'upper', 'quantile': .9}}
FACTORS = (('xo', XO), ('excursion', EXCURSION), ('leave', LEAVE))
STATIC_MIX = {'edit': .6, 'rewrite': .3, 'crossover': .1}
PRIMARY = ('adaptive_v1', 'timing_shuffled', 'patience_dev', 'patience_256', 'static_mix', 'edits_only')


def label(levels): return '/'.join(levels)


def v2_spec(levels):
    options = {}
    for (_, table), level in zip(FACTORS, levels): options.update(table[level])
    return {'kind': 'v2', 'options': options, 'levels': list(levels)}


def make_policy(spec, costs, seed, ops_of=None):
    kind = spec['kind']
    if kind == 'v1': return Adaptive(costs, seed)
    if kind == 'v2': return AdaptiveV2(costs, seed, rng_key='adaptive', **spec['options'])
    if kind == 'patience': return Patience(spec['T'])
    if kind == 'fixed': return Fixed(spec['weights'], seed, spec['name'])
    if kind == 'shuffled': return shuffled(ops_of[spec['of']], seed)
    raise ValueError(kind)


def run_job(job):
    """All arms of one (benchmark, seed) at equal budget. Arms that replay another arm come after it."""
    bench, seed, budget, costs = job['bench'], job['seed'], job['budget'], job['costs']
    problem = BENCHMARKS[bench](seed)
    checkpoints = [budget*i/30 for i in range(1, 31)]
    out, ops_of = [], {}
    for arm, spec in job['arms']:
        start = time.monotonic()
        run = Run(problem, make_policy(spec, costs, seed, ops_of), budget, seed, costs).run()
        ops_of[arm] = run.ops
        r = {'phase': job['phase'], 'benchmark': bench, 'seed': seed, 'arm': arm, 'final': problem.display(run.f_best),
             'spent': run.spent, 'steps': run.steps, 'ops': {op: run.ops.count(op) for op in costs},
             'seconds': round(time.monotonic()-start, 4)}
        if job.get('curves'): r['curve'] = [problem.display(f) for f in run.best_at(checkpoints)]
        if job.get('usage') and spec['kind'] in ('v1', 'v2'): r['usage'] = run.usage
        out.append(r)
    return out


# ---------------------------------------------------------------- counterfactual forks

def fork_job(job):
    """v1's fork procedure (strategist/forks.py) for any controller spec."""
    from .forks import switch_points
    bench, seed, budget, window, forks, moments = (job[k] for k in ('bench', 'seed', 'budget', 'window', 'forks', 'moments'))
    costs, problem = job['costs'], BENCHMARKS[job['bench']](seed)
    snaps = switch_points(problem, seed, budget, make_policy(job['spec'], costs, seed), costs)
    leaves = len(snaps)
    snaps = [s for s in snaps if s.spent+window <= budget]
    if len(snaps) > moments: snaps = [snaps[round(i*(len(snaps)-1)/(moments-1))] for i in range(moments)]
    out = []
    for i, snap in enumerate(snaps):
        result = {'controller': job['controller'], 'benchmark': bench, 'seed': seed, 'leaves_in_run': leaves,
                  'spent': snap.spent, 'stall': snap.stall, 'before': problem.display(snap.f_best)}
        for arm in ('switch', 'stay'):
            gains = []
            for k in range(forks):
                policy = copy.deepcopy(snap.policy) if arm == 'switch' else Fixed({'edit': 1}, seed, 'stay')
                fork = snap.fork(policy, f'{arm}/{i}/{k}', window).run()
                gains.append(problem.oriented(problem.display(fork.f_best)-problem.display(snap.f_best)))
            result[arm] = {'p_improve': sum(g > 0 for g in gains)/forks, 'mean_gain': statistics.fmean(gains)}
        out.append(result)
    if not out:   # keep the seed visible even without usable switch points
        out.append({'controller': job['controller'], 'benchmark': bench, 'seed': seed, 'leaves_in_run': leaves,
                    'empty': True})
    return out


def dispatch(job): return fork_job(job) if job['type'] == 'forks' else run_job(job)


def execute(jobs, use_modal=False, workers=2, label=''):
    """Run jobs locally (<= workers processes) or on Modal; returns the concatenated records."""
    records, start = [], time.monotonic()
    if use_modal:
        from .modal_app import map_jobs
        stream = map_jobs(jobs)
    else:
        from multiprocessing import Pool
        pool = Pool(min(workers, 2))
        stream = pool.imap_unordered(dispatch, jobs)
    for i, rs in enumerate(stream, 1):
        records.extend(rs)
        if i % max(1, len(jobs)//10) == 0 or i == len(jobs):
            print(f'{label} {i}/{len(jobs)} jobs  {time.monotonic()-start:.0f}s', flush=True)
    if not use_modal: pool.close(); pool.join()
    return records


# ---------------------------------------------------------------- bookkeeping

def source_hashes():
    files = sorted((ROOT/'strategist').glob('*.py'))
    return {f.name: hashlib.sha256(f.read_bytes()).hexdigest()[:16] for f in files}


def write_records(path, records):
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, 'wt') as f:
        for r in sorted(records, key=lambda r: (r.get('benchmark', ''), r.get('seed', 0), r.get('arm', r.get('controller', '')))):
            f.write(json.dumps(r)+'\n')


def read_records(path):
    with gzip.open(path, 'rt') as f: return [json.loads(line) for line in f]


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2)+'\n')


def check_seeds(seeds):
    for block in USED_BY_V1:
        assert not set(seeds) & set(block), f'seeds overlap a block used by v1: {block}'


def orient(bench): return 1 if BENCHMARKS[bench](0).higher_is_better else -1


def by_arm(records, bench):
    out = {}
    for r in records:
        if r['benchmark'] == bench: out.setdefault(r['arm'], {})[r['seed']] = r['final']
    return out


def standardised(finals, arm, reference, bench):
    """Mean paired difference arm - reference, oriented (positive = better), in units of the reference's SD."""
    seeds = sorted(finals[reference])
    sd = statistics.stdev(finals[reference][s] for s in seeds) or 1.
    return statistics.fmean(orient(bench)*(finals[arm][s]-finals[reference][s]) for s in seeds)/sd


# ---------------------------------------------------------------- development

def dev_arms(full_grid=True):
    arms = [('adaptive_v1', {'kind': 'v1'})]
    if full_grid:
        for xo in XO:
            for exc in EXCURSION:
                for leave in LEAVE:
                    if (xo, exc, leave) != ('off', 'inherit', 'point'):   # identical to adaptive_v1 (tested)
                        arms.append((label((xo, exc, leave)), v2_spec((xo, exc, leave))))
        arms += [('static_mix', {'kind': 'fixed', 'weights': STATIC_MIX, 'name': 'static_mix'}),
                 ('edits_only', {'kind': 'fixed', 'weights': {'edit': 1}, 'name': 'edits_only'})]
    arms += [(f'patience_{t}', {'kind': 'patience', 'T': t}) for t in PATIENCE_GRID]
    return arms


def select(records, benches=BENCHES):
    """The selection rule fixed in PROTOCOL.md stage 1: v2 = argmax J over the 32 full configurations;
    patience T per benchmark = best dev mean. Also returns J for every configuration, for the record."""
    finals = {b: by_arm(records, b) for b in benches}
    candidates = [label((x, e, l)) for x in XO for e in EXCURSION for l in LEAVE
                  if x not in ('off', 'none') and e != 'inherit' and l != 'point']
    table = {}
    for arm in finals[benches[0]]:
        if arm == 'adaptive_v1' or arm.startswith('patience_') or arm in ('static_mix', 'edits_only'): continue
        d = {b: standardised(finals[b], arm, 'adaptive_v1', b) for b in benches}
        table[arm] = {'J': statistics.fmean(d.values()), 'by_benchmark': d,
                      'mean': {b: statistics.fmean(finals[b][arm].values()) for b in benches}}
    chosen = max(candidates, key=lambda a: table[a]['J']) if table else None
    patience = {}
    for b in benches:
        means = {t: statistics.fmean(finals[b][f'patience_{t}'].values()) for t in PATIENCE_GRID}
        patience[b] = {'T': max(PATIENCE_GRID, key=lambda t: orient(b)*means[t]), 'means': means}
    joint = {t: statistics.fmean(standardised(finals[b], f'patience_{t}', 'adaptive_v1', b) for b in benches)
             for t in PATIENCE_GRID}
    reference = {b: {arm: statistics.fmean(finals[b][arm].values()) for arm in finals[b]
                     if arm in ('adaptive_v1', 'static_mix', 'edits_only')} for b in benches}
    return {'rule': 'v2 = argmax J over the 32 configs with all three changes on (crossover gate02 or gate10, '
                    'excursion cap/fixed, leave test not point); J = mean over benchmarks of '
                    '(mean paired difference vs adaptive_v1) / SD(adaptive_v1); patience T per benchmark = '
                    'best dev mean', 'chosen': chosen, 'levels': chosen.split('/') if chosen else None,
            'patience_dev': {b: patience[b]['T'] for b in benches}, 'patience_means': patience,
            'patience_joint': {'T': max(joint, key=joint.get), 'J': joint},
            'reference_means': reference,
            'ranking': sorted(table.items(), key=lambda kv: -kv[1]['J'])}


# ---------------------------------------------------------------- confirmatory arms

def confirm_arms(frozen, patience_dev):
    """Primary and secondary arms. patience_dev maps benchmark -> T chosen on dev seeds."""
    levels = frozen['levels']
    defaults = [next(iter(table)) for _, table in FACTORS]
    arms = [('adaptive_v2', v2_spec(levels)), ('adaptive_v1', {'kind': 'v1'}),
            ('timing_shuffled', {'kind': 'shuffled', 'of': 'adaptive_v2'})]
    for i, (name, _) in enumerate(FACTORS):          # each change alone on top of v1, and v2 without it
        alone = list(defaults); alone[i] = levels[i]
        without = list(levels); without[i] = defaults[i]
        arms += [(f'only_{name}', v2_spec(alone)), (f'without_{name}', v2_spec(without))]
    arms += [('v2_crossover_removed', v2_spec(['none']+list(levels[1:]))),    # gate vs simply dropping crossover
             ('v1_crossover_removed', v2_spec(['none']+defaults[1:])),        # v1's no-crossover ablation
             ('static_mix', {'kind': 'fixed', 'weights': STATIC_MIX, 'name': 'static_mix'}),
             ('edits_only', {'kind': 'fixed', 'weights': {'edit': 1}, 'name': 'edits_only'}),
             ('patience_256', {'kind': 'patience', 'T': 256})]
    per_bench = {b: [('patience_dev', {'kind': 'patience', 'T': patience_dev[b]})] for b in patience_dev}
    return arms, per_bench


def summarise(records, benches=BENCHES, reference='adaptive_v2', primary=PRIMARY):
    summary = {}
    for bench in benches:
        rs = [r for r in records if r['benchmark'] == bench]
        if not rs: continue
        sign, arms_of = orient(bench), {}
        for r in rs: arms_of.setdefault(r['arm'], {})[r['seed']] = r
        seeds = sorted(arms_of[reference])
        arms = {}
        for arm, runs in arms_of.items():
            finals = [runs[s]['final'] for s in seeds]
            total = sum(sum(runs[s]['ops'].values()) for s in seeds)
            a = {'mean': statistics.fmean(finals), 'median': statistics.median(finals),
                 'sd': statistics.stdev(finals) if len(finals) > 1 else 0.,
                 'op_share': {op: sum(runs[s]['ops'][op] for s in seeds)/total for op in runs[seeds[0]]['ops']},
                 'restarts_per_run': statistics.fmean(runs[s]['ops']['restart'] for s in seeds)}
            if 'curve' in runs[seeds[0]]:
                a['auc'] = statistics.fmean(statistics.fmean(runs[s]['curve']) for s in seeds)
                for name, q in (('curve_q25', .25), ('curve_median', .5), ('curve_q75', .75)):
                    a[name] = [sorted(runs[s]['curve'][i] for s in seeds)[int(q*(len(seeds)-1))] for i in range(30)]
            arms[arm] = a

        def compare(x, y):
            out = {'final': paired([sign*(arms_of[x][s]['final']-arms_of[y][s]['final']) for s in seeds])}
            if 'curve' in arms_of[x][seeds[0]]:
                out['auc'] = paired([sign*(statistics.fmean(arms_of[x][s]['curve'])-statistics.fmean(arms_of[y][s]['curve']))
                                     for s in seeds])
            return out
        comparisons = {arm: compare(reference, arm) for arm in arms_of if arm != reference}
        for metric in ('final', 'auc'):
            if all(metric in comparisons.get(a, {}) for a in primary):
                for arm, p in zip(primary, holm([comparisons[a][metric]['sign_p'] for a in primary])):
                    comparisons[arm][metric]['holm_p'] = p
        secondary = {}
        for name, _ in FACTORS:
            if f'only_{name}' in arms_of: secondary[f'only_{name} vs adaptive_v1'] = compare(f'only_{name}', 'adaptive_v1')
            if f'without_{name}' in arms_of: secondary[f'adaptive_v2 vs without_{name}'] = compare(reference, f'without_{name}')
        for arm in ('patience_dev', 'patience_256', 'static_mix', 'edits_only'):
            if arm in arms_of and 'adaptive_v1' in arms_of: secondary[f'adaptive_v1 vs {arm}'] = compare('adaptive_v1', arm)
        usage = {}
        for arm in ('adaptive_v2', 'adaptive_v1'):
            for s in seeds:
                for state, counts in (arms_of.get(arm, {}).get(s, {}).get('usage') or {}).items():
                    row = usage.setdefault(arm, {}).setdefault(state, dict.fromkeys(counts, 0))
                    for op, n in counts.items(): row[op] += n
        summary[bench] = {'higher_is_better': sign > 0, 'seeds': len(seeds), 'reference': reference,
                          'primary': list(primary), 'arms': arms, 'comparisons': comparisons,
                          'secondary': secondary, 'usage': usage}
    return summary


def summarise_forks(moments, benches=BENCHES, window=300.):
    """Per benchmark and controller, plus each controller minus adaptive_v1 (seeds resampled as clusters)."""
    controllers = sorted({m['controller'] for m in moments}, key=lambda c: (c != 'adaptive_v1', c != 'adaptive_v2', c))
    premature = lambda ms: statistics.fmean(m['stay']['mean_gain'] > m['switch']['mean_gain'] for m in ms)
    gain = lambda ms: statistics.fmean(m['switch']['mean_gain']-m['stay']['mean_gain'] for m in ms)
    out = {}
    for bench in benches:
        out[bench] = {}
        seeds = sorted({m['seed'] for m in moments if m['benchmark'] == bench})
        per_seed = {c: {s: [] for s in seeds} for c in controllers}
        for ctl in controllers:
            rows = [m for m in moments if m['benchmark'] == bench and m['controller'] == ctl]
            ms = [m for m in rows if not m.get('empty')]
            for m in ms: per_seed[ctl][m['seed']].append(m)
            leaves = {m['seed']: m['leaves_in_run'] for m in rows}
            g = list(per_seed[ctl].values())
            entry = {'moments': len(ms), 'seeds_with_moments': sum(bool(x) for x in g),
                     'leaves_per_run': statistics.fmean(leaves.values()) if leaves else 0.}
            if ms:
                stay_wins = sum(m['stay']['mean_gain'] > m['switch']['mean_gain'] for m in ms)
                switch_wins = sum(m['stay']['mean_gain'] < m['switch']['mean_gain'] for m in ms)
                entry.update({
                    'p_improve': {a: statistics.fmean(m[a]['p_improve'] for m in ms) for a in ('switch', 'stay')},
                    'mean_gain': {a: statistics.fmean(m[a]['mean_gain'] for m in ms) for a in ('switch', 'stay')},
                    'gain_difference': paired([m['switch']['mean_gain']-m['stay']['mean_gain'] for m in ms]),
                    'p_improve_difference': paired([m['switch']['p_improve']-m['stay']['p_improve'] for m in ms]),
                    'gain_difference_seed_cluster_ci': cluster_interval(
                        [[m['switch']['mean_gain']-m['stay']['mean_gain'] for m in grp] for grp in g]),
                    'premature_share': premature(ms),
                    'premature_share_seed_cluster_ci': cluster_interval(
                        [[float(m['stay']['mean_gain'] > m['switch']['mean_gain']) for m in grp] for grp in g]),
                    'stay_better': stay_wins, 'switch_better': switch_wins, 'ties': len(ms)-stay_wins-switch_wins,
                    'premature_share_excluding_ties': stay_wins/(stay_wins+switch_wins) if stay_wins+switch_wins else None,
                    'mean_stall_at_switch': statistics.fmean(m['stall'] for m in ms),
                    'median_spent_at_switch': statistics.median(m['spent'] for m in ms)})
            out[bench][ctl] = entry
        if 'adaptive_v1' not in controllers or not out[bench]['adaptive_v1'].get('moments'): continue
        for ctl in controllers:
            if ctl == 'adaptive_v1' or not out[bench][ctl].get('moments'): continue
            groups = [[(c, m) for c in ('adaptive_v1', ctl) for m in per_seed[c][s]] for s in seeds]

            def diff(stat, ctl=ctl):
                def f(pooled):
                    a = [m for c, m in pooled if c == ctl]; b = [m for c, m in pooled if c == 'adaptive_v1']
                    return stat(a)-stat(b) if a and b else 0.
                return f
            pooled = [x for grp in groups for x in grp]
            key = 'v2_minus_v1' if ctl == 'adaptive_v2' else f'{ctl}_minus_v1'
            out[bench][key] = {
                'premature_share': diff(premature)(pooled), 'premature_share_ci': cluster_interval(groups, diff(premature)),
                'gain_difference': diff(gain)(pooled), 'gain_difference_ci': cluster_interval(groups, diff(gain)),
                'leaves_per_run': out[bench][ctl]['leaves_per_run']-out[bench]['adaptive_v1']['leaves_per_run']}
    return out


# ---------------------------------------------------------------- commands

def jobs_for(phase, seeds, arms, costs, curves=False, usage=False, per_bench=None, benches=BENCHES):
    check_seeds(seeds)
    return [{'type': 'runs', 'phase': phase, 'bench': b, 'seed': s, 'budget': BUDGET, 'costs': costs,
             'arms': arms+(per_bench or {}).get(b, []), 'curves': curves, 'usage': usage}
            for b in benches for s in seeds]


def config(args, **extra):
    return {'argv': sys.argv, **{k: v for k, v in vars(args).items() if k != 'func'}, 'budget': BUDGET,
            'benchmarks': list(BENCHES), 'source_sha256_16': source_hashes(), 'python': sys.version, **extra}


def cmd_dev(args):
    name, costs = load_costs(args.costs)
    seeds = range(*map(int, args.seeds.split(':'))) if args.seeds else DEV
    full = name == 'llm_proxy'                 # other cost tables only re-tune patience (design is frozen)
    folder = OUT/'dev' if full else OUT/'costs'/name
    records = execute(jobs_for('dev', seeds, dev_arms(full), costs), args.modal, args.workers, 'dev')
    write_records(folder/('dev_runs.jsonl.gz' if not full else 'runs.jsonl.gz'), records)
    selection = select(records)
    write_json(folder/('dev_selection.json' if not full else 'selection.json'),
               {**selection, 'config': config(args, cost_table=costs, cost_name=name, seeds=[seeds.start, seeds.stop])})
    print(json.dumps({k: selection[k] for k in ('chosen', 'patience_dev', 'patience_joint')}, indent=2))
    for arm, row in selection['ranking'][:12]:
        print(f"  {arm:32s} J={row['J']:+.3f}  " + '  '.join(f'{b}={v:+.3f}' for b, v in row['by_benchmark'].items()))
    return selection


def cmd_freeze(args):
    selection = json.loads((OUT/'dev'/'selection.json').read_text())
    frozen = {'levels': selection['levels'], 'label': selection['chosen'],
              'options': v2_spec(selection['levels'])['options'], 'patience_dev': selection['patience_dev'],
              'patience_joint': selection['patience_joint']['T'], 'frozen_at': time.strftime('%Y-%m-%d %H:%M:%S %Z'),
              'source_sha256_16': source_hashes()}
    write_json(OUT/'frozen.json', frozen)
    print(json.dumps(frozen, indent=2))


def frozen_design():
    path = OUT/'frozen.json'
    if not path.exists(): raise SystemExit('run `python -m strategist.v2 dev` and `freeze` first')
    return json.loads(path.read_text())


def cmd_validate(args):
    frozen = frozen_design()
    if (OUT/'validation'/'summary.json').exists() and not args.force:
        raise SystemExit('validation already ran once; refusing to run it again (use --force only to reproduce)')
    _, costs = load_costs('llm_proxy')
    arms, per_bench = confirm_arms(frozen, frozen['patience_dev'])
    records = execute(jobs_for('validation', VALIDATION, arms, costs, per_bench=per_bench), args.modal, args.workers, 'validation')
    write_records(OUT/'validation'/'runs.jsonl.gz', records)
    summary = summarise(records)
    finals = {b: by_arm(records, b) for b in BENCHES}
    summary['J'] = {arm: statistics.fmean(standardised(finals[b], arm, 'adaptive_v1', b) for b in BENCHES)
                    for arm in finals[BENCHES[0]] if arm != 'adaptive_v1'}
    write_json(OUT/'validation'/'summary.json', {**summary, 'config': config(args, frozen=frozen)})
    print_summary(summary)


def cmd_confirm(args):
    frozen = frozen_design()
    name, costs = load_costs(args.costs)
    if name == 'llm_proxy':
        folder, patience = OUT, frozen['patience_dev']
    else:   # cost sensitivity: same frozen controller; the patience baseline is re-tuned on dev seeds
        folder = OUT/'costs'/name
        selection_path = folder/'dev_selection.json'
        if not selection_path.exists() or args.retune:
            args_dev = argparse.Namespace(**{**vars(args), 'seeds': None})
            cmd_dev(args_dev)
        patience = json.loads(selection_path.read_text())['patience_dev']
    if (folder/'summary.json').exists() and not args.force:
        raise SystemExit(f'{folder}/summary.json exists: the confirmatory run is run once (use --force only to reproduce)')
    arms, per_bench = confirm_arms(frozen, patience)
    records = execute(jobs_for('confirm', CONFIRM, arms, costs, curves=True, usage=True, per_bench=per_bench),
                      args.modal, args.workers, f'confirm[{name}]')
    write_records(folder/'runs.jsonl.gz', records)
    summary = summarise(records)
    write_json(folder/'summary.json', {**summary, 'config': config(args, frozen=frozen, cost_table=costs,
                                                                    cost_name=name, patience_dev=patience)})
    print_summary(summary)
    from .report_v2 import main as report
    report()                                  # refresh tables.md (and the headline) with the new run


def cmd_cost(args):
    """Record spend and compute: Modal cost of app ssm-strategist-v2 (from `modal billing report`),
    evaluator executions and CPU seconds from the saved records. Writes cost.json."""
    import subprocess
    out = {'anthropic_usd': 0., 'anthropic_note': 'no LLM calls in this experiment (no usage.jsonl)'}
    try:
        modal_cli = str(Path(sys.executable).with_name('modal'))
        rows = json.loads(subprocess.run([modal_cli, 'billing', 'report', '--for', args.billing, '--json'],
                                         capture_output=True, text=True, check=True).stdout)
        rows = [r for r in rows if r.get('description') == 'ssm-strategist-v2']
        out.update({'modal_usd': round(sum(float(r['cost']) for r in rows), 4), 'modal_app_runs': len(rows),
                    'modal_note': f'modal billing report --for {args.billing!r}, app ssm-strategist-v2, queried '
                                  + time.strftime('%Y-%m-%d %H:%M %Z')})
    except (OSError, subprocess.CalledProcessError, ValueError) as error:
        out['modal_note'] = f'billing query failed: {error}'
    runs, seconds, evaluations = 0, 0., 0
    for path in [OUT/'dev'/'runs.jsonl.gz', OUT/'validation'/'runs.jsonl.gz', OUT/'runs.jsonl.gz',
                 *sorted((OUT/'costs').glob('*/*runs.jsonl.gz'))]:
        if not path.exists(): continue
        for r in read_records(path):
            runs += 1; seconds += r['seconds']; evaluations += r['steps']+1     # +1: the initial solution
    out.update({'runs': runs, 'run_cpu_seconds': round(seconds), 'evaluations': evaluations})
    fork_moments = 0
    for name in ('forks.json', 'forks_ablations.json'):
        if (OUT/name).exists():
            fork_moments += sum(not m.get('empty') for m in json.loads((OUT/name).read_text())['moments'])
    # Fork evaluations are not logged; estimate: 20 stay forks x ~250 edits + 20 switch forks x ~220 moves
    # per moment, plus one ~2,300-move base run per fork job (3 benchmarks x 40 seeds per controller).
    out['fork_moments'] = fork_moments
    out['fork_evaluations_estimate'] = fork_moments*20*(250+220)
    write_json(OUT/'cost.json', out)
    print(json.dumps(out, indent=2))


def cmd_forks(args):
    """Pre-registered: adaptive_v1 and adaptive_v2 -> forks.json. With --controllers (exploratory, added
    after the confirmatory run): any confirmatory arm names, plus adaptive_v1 as reference -> --out."""
    frozen = frozen_design()
    _, costs = load_costs('llm_proxy')
    check_seeds(FORK_SEEDS)
    arms = dict(confirm_arms(frozen, frozen['patience_dev'])[0])
    names = args.controllers.split(',') if args.controllers else ['adaptive_v2']
    specs = {'adaptive_v1': {'kind': 'v1'}, **{c: arms[c] for c in names}}
    jobs = [{'type': 'forks', 'controller': c, 'spec': spec, 'bench': b, 'seed': s, 'budget': BUDGET,
             'window': args.window, 'forks': args.forks, 'moments': args.moments, 'costs': costs}
            for c, spec in specs.items() for b in BENCHES for s in FORK_SEEDS]
    moments = execute(jobs, args.modal, args.workers, 'forks')
    summary = summarise_forks(moments)
    path = OUT/(args.out or 'forks.json')
    write_json(path, {'config': config(args, frozen=frozen), 'summary': summary, 'moments': moments})
    print_forks(summary)


def print_forks(summary):
    for b, s in summary.items():
        for c, e in s.items():
            if c.endswith('_minus_v1'): print(f"{b:10s} {c}: {e}"); continue
            if not e.get('moments'): print(b, c, 'no moments'); continue
            print(f"{b:10s} {c}: leaves/run={e['leaves_per_run']:.1f} moments={e['moments']} "
                  f"premature={e['premature_share']:.2f} gain switch-stay={e['gain_difference']['mean']:+.4g} "
                  f"CI(seed)={[round(x, 5) for x in e['gain_difference_seed_cluster_ci']]}")


def print_summary(summary):
    for bench, s in summary.items():
        if bench == 'J': continue
        print(f"\n== {bench} ({s['seeds']} seeds; positive = {s['reference']} better)")
        for arm, a in sorted(s['arms'].items(), key=lambda kv: -kv[1]['mean']*(1 if s['higher_is_better'] else -1)):
            c = s['comparisons'].get(arm, {}).get('final')
            extra = (f"  diff={c['mean']:+.4g} CI=[{c['interval95'][0]:+.3g},{c['interval95'][1]:+.3g}] "
                     f"W/T/L={c['wins']}/{c['ties']}/{c['losses']} p={c['sign_p']:.2g}"
                     + (f" holm={c['holm_p']:.2g}" if 'holm_p' in c else '')) if c else ''
            print(f'  {arm:22s} mean={a["mean"]:.5g}{extra}')
    if 'J' in summary:
        print('\nJ (standardised gain over adaptive_v1, mean over benchmarks):')
        for arm, j in sorted(summary['J'].items(), key=lambda kv: -kv[1]): print(f'  {arm:22s} {j:+.3f}')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest='command', required=True)
    for name, func in (('dev', cmd_dev), ('freeze', cmd_freeze), ('validate', cmd_validate),
                       ('confirm', cmd_confirm), ('forks', cmd_forks), ('report', None), ('cost', cmd_cost)):
        p = sub.add_parser(name)
        p.set_defaults(func=func)
        p.add_argument('--modal', action='store_true', help='fan out on Modal (app ssm-strategist-v2)')
        p.add_argument('--workers', type=int, default=2, help='local processes (capped at 2)')
        p.add_argument('--force', action='store_true', help='allow re-running a run-once phase')
        p.add_argument('--costs', default='llm_proxy', help='llm_proxy | uniform | measured | path.json | edit=1,...')
        p.add_argument('--retune', action='store_true', help='re-tune patience on dev for this cost table')
        p.add_argument('--seeds', default=None, help='dev only: start:stop (default 40:240)')
        p.add_argument('--window', type=float, default=300., help='forks: cost units each fork runs')
        p.add_argument('--forks', type=int, default=20, help='forks: forks per arm per switch moment')
        p.add_argument('--moments', type=int, default=6, help='forks: switch moments sampled per seed')
        p.add_argument('--billing', default='today', help="cost: billing range, e.g. 'today' or 'this month'")
        p.add_argument('--controllers', default=None, help='forks only, exploratory: arm names, comma-separated')
        p.add_argument('--out', default=None, help='forks only: output file name in experiments/strategist-v2')
    args = parser.parse_args(argv)
    if args.command == 'report':
        from .report_v2 import main as report
        return report()
    try:
        args.func(args)
    except CostTableError as error:
        raise SystemExit(f'cost table: {error}')


if __name__ == '__main__': main()
