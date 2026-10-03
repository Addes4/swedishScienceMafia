"""Markdown tables for experiments/strategist-v2 from its JSON outputs (no plotting dependencies).

    python -m strategist.v2 report            # writes experiments/strategist-v2/tables.md

Every number in RESULTS.md comes from these tables. Re-running after a new cost table has been run
(`confirm --costs measured`) adds that table's columns automatically.
"""
import json
import statistics
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent/'experiments'/'strategist-v2'
BENCHES = ('labs', 'heilbronn', 'nk')
TITLES = {'labs': 'LABS', 'heilbronn': 'Heilbronn', 'nk': 'NK'}
NAMES = {'adaptive_v2': 'adaptive v2', 'adaptive_v1': 'adaptive v1', 'timing_shuffled': 'v2 moves, shuffled timing',
         'patience_dev': 'patience, T tuned on dev', 'patience_256': 'patience, T = 256',
         'static_mix': 'static mix 0.6/0.3/0.1', 'edits_only': 'small edits only',
         'only_xo': 'v1 + crossover gate only', 'only_excursion': 'v1 + excursion cap only',
         'only_leave': 'v1 + leave test only', 'without_xo': 'v2 without crossover gate',
         'without_excursion': 'v2 without excursion cap', 'without_leave': 'v2 without leave test',
         'v2_crossover_removed': 'v2 with crossover removed', 'v1_crossover_removed': 'v1 with crossover removed'}
MAIN_ARMS = ('adaptive_v2', 'adaptive_v1', 'patience_dev', 'patience_256', 'static_mix', 'edits_only')


def fmt(v, bench=None):
    if bench == 'heilbronn' or abs(v) < .01: return f'{v:.5f}'
    if bench == 'nk': return f'{v:.4f}'
    return f'{v:.3f}'


def sig(c, holm=True):
    p = c.get('holm_p', c['sign_p']) if holm else c['sign_p']
    word = '~' if p >= .05 else ('**better**' if c['mean'] > 0 else '**worse**')
    return word


def cell(c, bench, holm=True):
    lo, hi = c['interval95']
    p = c.get('holm_p') if holm and 'holm_p' in c else c['sign_p']
    return (f"{sig(c, holm)} {fmt(c['mean'], bench)} [{fmt(lo, bench)}, {fmt(hi, bench)}] "
            f"({c['wins']}/{c['ties']}/{c['losses']}, p={p:.2g})")


def load(path):
    return json.loads(path.read_text()) if path.exists() else None


def means_table(s, arms):
    rows = ['| arm | ' + ' | '.join(TITLES[b] + (' ↑' if s[b]['higher_is_better'] else ' ↓') for b in BENCHES) + ' |',
            '|---|' + '---|'*len(BENCHES)]
    for arm in arms:
        if arm not in s[BENCHES[0]]['arms']: continue
        rows.append(f'| {NAMES.get(arm, arm)} | ' + ' | '.join(fmt(s[b]['arms'][arm]['mean'], b) for b in BENCHES) + ' |')
    return '\n'.join(rows)


def comparison_table(s, pairs, holm=True, metric='final'):
    """pairs: list of (row label, getter(summary_of_bench) -> comparison dict)."""
    rows = ['| comparison | ' + ' | '.join(TITLES[b] for b in BENCHES) + ' |', '|---|' + '---|'*len(BENCHES)]
    for name, get in pairs:
        cells = []
        for b in BENCHES:
            c = get(s[b])
            cells.append(cell(c[metric], b, holm) if c else 'n/a')
        rows.append(f'| {name} | ' + ' | '.join(cells) + ' |')
    return '\n'.join(rows)


def primary_pairs(s):
    return [(f'v2 vs {NAMES[a]}', (lambda a: lambda sb: sb['comparisons'].get(a))(a)) for a in s['labs']['primary']]


def robustness(s, arms=MAIN_ARMS):
    rows = ['| arm | ' + ' | '.join(TITLES[b] for b in BENCHES) + ' | worst case |', '|---|' + '---|'*(len(BENCHES)+1)]
    gaps = {}
    for b in BENCHES:
        sign = 1 if s[b]['higher_is_better'] else -1
        best = max(sign*s[b]['arms'][a]['mean'] for a in arms)
        for a in arms: gaps.setdefault(a, []).append((best-sign*s[b]['arms'][a]['mean'])/abs(best)*100)
    for a in sorted(arms, key=lambda a: max(gaps[a])):
        rows.append(f'| {NAMES[a]} | ' + ' | '.join(f'−{g:.1f}%' if g > 0 else '0%' for g in gaps[a]) + f' | {max(gaps[a]):.1f}% |')
    return '\n'.join(rows)


def usage_table(s):
    rows = ['| | ' + ' | '.join(f'{TITLES[b]} v1 | {TITLES[b]} v2' for b in BENCHES) + ' |', '|---|' + '---|'*6]
    for op in ('edit', 'rewrite', 'crossover', 'restart'):
        rows.append(f'| {op} share | ' + ' | '.join(f"{s[b]['arms'][a]['op_share'][op]:.1%}" for b in BENCHES
                                                  for a in ('adaptive_v1', 'adaptive_v2')) + ' |')
    rows.append('| restarts per run | ' + ' | '.join(f"{s[b]['arms'][a]['restarts_per_run']:.1f}" for b in BENCHES
                                                     for a in ('adaptive_v1', 'adaptive_v2')) + ' |')
    return '\n'.join(rows)


def shrinkage(dev_records, validation, confirm, frozen):
    """v2 - v1 and v2 - patience_dev on dev, validation and confirmatory seeds."""
    from .stats import paired
    from .v2 import by_arm, orient
    label = frozen['label']
    rows = ['| comparison | block | ' + ' | '.join(TITLES[b] for b in BENCHES) + ' |', '|---|---|' + '---|'*len(BENCHES)]
    for other, dev_name in (('adaptive_v1', lambda b: 'adaptive_v1'),
                            ('patience_dev', lambda b: f"patience_{frozen['patience_dev'][b]}")):
        cells = []
        for b in BENCHES:
            f = by_arm(dev_records, b)
            seeds = sorted(f['adaptive_v1'])
            c = paired([orient(b)*(f[label][s]-f[dev_name(b)][s]) for s in seeds])
            cells.append(f"{fmt(c['mean'], b)} [{fmt(c['interval95'][0], b)}, {fmt(c['interval95'][1], b)}]")
        rows.append(f'| v2 − {NAMES[other]} | dev 40-239 | ' + ' | '.join(cells) + ' |')
        for name, s in (('validation 240-439', validation), ('confirmatory 3000-3199', confirm)):
            cells = []
            for b in BENCHES:
                c = s[b]['comparisons'][other]['final']
                cells.append(f"{fmt(c['mean'], b)} [{fmt(c['interval95'][0], b)}, {fmt(c['interval95'][1], b)}]")
            rows.append(f'| v2 − {NAMES[other]} | {name} | ' + ' | '.join(cells) + ' |')
    return '\n'.join(rows)


def j_scores(records_or_summary_finals, arms):
    from .v2 import by_arm, standardised
    finals = {b: by_arm(records_or_summary_finals, b) for b in BENCHES}
    return {a: statistics.fmean(standardised(finals[b], a, 'adaptive_v1', b) for b in BENCHES) for a in arms
            if a in finals[BENCHES[0]]}


def forks_table(f, controllers=('adaptive_v1', 'adaptive_v2')):
    rows = ['| benchmark | controller | leaves per run | switch moments | stall at switch (mean) | '
            'P(new best) switch / stay | mean gain switch / stay | gain switch − stay [seed-clustered CI] | '
            'stay better / switch better / tie | premature share [seed-clustered CI] | premature share excl. ties |',
            '|---|---|---|---|---|---|---|---|---|---|---|']
    for b in BENCHES:
        for ctl in controllers:
            e = f['summary'][b].get(ctl)
            if not e: continue
            if not e.get('moments'):
                rows.append(f'| {TITLES[b]} | {ctl} | {e["leaves_per_run"]:.1f} | 0 |' + ' |'*7)
                continue
            lo, hi = e['gain_difference_seed_cluster_ci']; plo, phi = e['premature_share_seed_cluster_ci']
            rows.append(f"| {TITLES[b]} | {NAMES[ctl]} | {e['leaves_per_run']:.1f} | {e['moments']} | "
                        f"{e['mean_stall_at_switch']:.0f} | "
                        f"{e['p_improve']['switch']:.1%} / {e['p_improve']['stay']:.1%} | "
                        f"{fmt(e['mean_gain']['switch'], b)} / {fmt(e['mean_gain']['stay'], b)} | "
                        f"{fmt(e['gain_difference']['mean'], b)} [{fmt(lo, b)}, {fmt(hi, b)}] | "
                        f"{e['stay_better']} / {e['switch_better']} / {e['ties']} | "
                        f"{e['premature_share']:.0%} [{plo:.0%}, {phi:.0%}] | "
                        f"{e['premature_share_excluding_ties']:.0%} |")
    rows += ['', '| benchmark | controller − v1 | premature share [CI] | gain difference [CI] | leaves per run |',
             '|---|---|---|---|---|']
    for b in BENCHES:
        for ctl in controllers:
            if ctl == 'adaptive_v1': continue
            d = f['summary'][b].get('v2_minus_v1' if ctl == 'adaptive_v2' else f'{ctl}_minus_v1')
            if not d: continue
            rows.append(f"| {TITLES[b]} | {NAMES[ctl]} | {d['premature_share']:+.0%} "
                        f"[{d['premature_share_ci'][0]:+.0%}, {d['premature_share_ci'][1]:+.0%}] | "
                        f"{fmt(d['gain_difference'], b)} [{fmt(d['gain_difference_ci'][0], b)}, "
                        f"{fmt(d['gain_difference_ci'][1], b)}] | {d['leaves_per_run']:+.1f} |")
    return '\n'.join(rows)


def main():
    from .v2 import read_records
    confirm = load(OUT/'summary.json')
    if confirm is None: raise SystemExit('no confirmatory summary yet')
    frozen, validation = load(OUT/'frozen.json'), load(OUT/'validation'/'summary.json')
    dev = read_records(OUT/'dev'/'runs.jsonl.gz') if (OUT/'dev'/'runs.jsonl.gz').exists() else None
    forks = load(OUT/'forks.json')
    cost_runs = {p.parent.name: load(p) for p in sorted((OUT/'costs').glob('*/summary.json'))}
    parts = [f"# Strategist v2 tables (generated by `python -m strategist.v2 report`)\n",
             f"Frozen design: `{frozen['label']}`; patience_dev T = "
             + ', '.join(f"{TITLES[b]} {t}" for b, t in frozen['patience_dev'].items()) + '.\n',
             'Cells: verdict, mean paired difference (positive favours the first arm) [95% bootstrap interval] '
             '(seed wins/ties/losses, sign-test p; Holm-adjusted for primary comparisons).\n',
             '## Mean final score, confirmatory seeds 3000-3199, proxy costs\n',
             means_table(confirm, list(NAMES)),
             '\n## Primary comparisons (Holm over six per benchmark)\n', comparison_table(confirm, primary_pairs(confirm)),
             '\n## Anytime performance (mean best-so-far over 30 checkpoints), same comparisons\n',
             comparison_table(confirm, primary_pairs(confirm), metric='auc'),
             '\n## Secondary: which change does the work (no multiplicity correction)\n',
             comparison_table(confirm, [(k, (lambda k: lambda sb: sb['secondary'].get(k))(k))
                                        for k in confirm['labs']['secondary'] if 'only_' in k or 'without_' in k], holm=False),
             '\n' + comparison_table(confirm, [(f'v2 vs {NAMES[a]}', (lambda a: lambda sb: sb['comparisons'].get(a))(a))
                                               for a in ('v2_crossover_removed', 'v1_crossover_removed')], holm=False),
             '\n## Secondary: v1 on new seeds (replication)\n',
             comparison_table(confirm, [(k, (lambda k: lambda sb: sb['secondary'].get(k))(k))
                                        for k in confirm['labs']['secondary'] if k.startswith('adaptive_v1 vs')], holm=False),
             '\n## Robustness: gap to the best of the six main arms\n', robustness(confirm),
             '\n## Move usage\n', usage_table(confirm)]
    if dev and validation:
        arms = [a for a in NAMES if a not in ('timing_shuffled',)]
        confirm_records = read_records(OUT/'runs.jsonl.gz')
        jc = j_scores(confirm_records, [a for a in arms if a != 'adaptive_v1'])
        jv = validation.get('J', {})
        dev_map = {'adaptive_v2': frozen['label']}
        parts += ['\n## Winner\'s curse: dev vs validation vs confirmatory\n',
                  shrinkage(dev, validation, confirm, frozen),
                  '\n| arm | J validation | J confirmatory |', '|---|---|---|']
        parts += [f"| {NAMES[a]} | {jv.get(a, float('nan')):+.3f} | {jc[a]:+.3f} |" for a in jc]
        parts.append('\nJ = mean over benchmarks of the paired difference to adaptive v1 in units of v1\'s SD. '
                     f"Dev J of the chosen design: {next(r['J'] for a, r in json.loads((OUT/'dev'/'selection.json').read_text())['ranking'] if a == frozen['label']):+.3f}.")
    for name, s in cost_runs.items():
        parts += [f'\n## Cost sensitivity: `{name}` costs ({s["config"]["cost_table"]}), patience T = '
                  + ', '.join(f"{TITLES[b]} {t}" for b, t in s['config']['patience_dev'].items()) + '\n',
                  means_table(s, MAIN_ARMS), '', comparison_table(s, primary_pairs(s)),
                  '\n' + comparison_table(s, [(k, (lambda k: lambda sb: sb['secondary'].get(k))(k))
                                              for k in s['labs']['secondary'] if 'only_' in k], holm=False)]
    if forks:
        parts += ['\n## Counterfactual forks, seeds 4000-4039, 300-unit window, 20 + 20 forks per moment\n', forks_table(forks)]
    ablation_forks = load(OUT/'forks_ablations.json')
    if ablation_forks:
        parts += ['\n## Exploratory (added after the confirmatory run): forks for each change alone, same seeds\n',
                  forks_table(ablation_forks, ('adaptive_v1', 'only_xo', 'only_excursion', 'only_leave'))]
    (OUT/'tables.md').write_text('\n'.join(parts)+'\n')
    print(f'wrote {OUT/"tables.md"}')


if __name__ == '__main__': main()
