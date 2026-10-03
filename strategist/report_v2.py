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


def v1_vs_v2_table(confirm, forks, uniform=None):
    """What changed between the controllers and whether it helped, confirmatory seeds."""
    rows = ['| | ' + ' | '.join(TITLES[b] for b in BENCHES) + ' |', '|---|' + '---|'*len(BENCHES)]
    a = lambda b, arm: confirm[b]['arms'][arm]
    rows.append('| mean final score, v1 → v2 | ' + ' | '.join(
        f"{fmt(a(b, 'adaptive_v1')['mean'], b)} → {fmt(a(b, 'adaptive_v2')['mean'], b)}" for b in BENCHES) + ' |')
    rows.append('| v2 − v1, proxy costs (primary) | ' + ' | '.join(
        cell(confirm[b]['comparisons']['adaptive_v1']['final'], b) for b in BENCHES) + ' |')
    if uniform:
        rows.append('| v2 − v1, uniform costs (secondary) | ' + ' | '.join(
            cell(uniform[b]['comparisons']['adaptive_v1']['final'], b) for b in BENCHES) + ' |')
    rows.append('| v1 → v2, each minus patience T tuned on dev (negative = patience better) | ' + ' | '.join(
        f"{fmt(confirm[b]['secondary']['adaptive_v1 vs patience_dev']['final']['mean'], b)} → "
        f"{fmt(confirm[b]['comparisons']['patience_dev']['final']['mean'], b)}" for b in BENCHES) + ' |')
    rows.append('| crossover share of moves, v1 → v2 | ' + ' | '.join(
        f"{a(b, 'adaptive_v1')['op_share']['crossover']:.0%} → {a(b, 'adaptive_v2')['op_share']['crossover']:.0%}"
        for b in BENCHES) + ' |')
    rows.append('| restarts per run, v1 → v2 | ' + ' | '.join(
        f"{a(b, 'adaptive_v1')['restarts_per_run']:.1f} → {a(b, 'adaptive_v2')['restarts_per_run']:.1f}" for b in BENCHES) + ' |')
    if forks:
        f = forks['summary']
        rows.append('| premature share at switch points (forks), v1 → v2 | ' + ' | '.join(
            f"{f[b]['adaptive_v1']['premature_share']:.0%} → {f[b]['adaptive_v2']['premature_share']:.0%} "
            f"(diff {f[b]['v2_minus_v1']['premature_share']:+.0%} [{f[b]['v2_minus_v1']['premature_share_ci'][0]:+.0%}, "
            f"{f[b]['v2_minus_v1']['premature_share_ci'][1]:+.0%}])" for b in BENCHES) + ' |')
    return '\n'.join(rows)


def headline(confirm, frozen, validation, forks, cost_runs, dev_j, j_conf):
    """Machine-readable headline numbers, stored under summary.json['headline']."""
    def comp(c):
        c = c['final']
        return {'mean': c['mean'], 'ci95': c['interval95'], 'wins': c['wins'], 'ties': c['ties'],
                'losses': c['losses'], 'sign_p': c['sign_p'], 'holm_p': c.get('holm_p'),
                'verdict': {'**better**': 'better', '**worse**': 'worse', '~': 'no clear difference'}[sig(c)]}
    out = {'experiment': 'strategist-v2',
           'question': 'Do v1\'s three proposed fixes (crossover gate, excursion cap, recent-improvement leave '
                       'test) make the adaptive controller better at equal cost, and does it now match a patience '
                       'rule tuned on dev seeds?',
           'design': frozen['label'], 'options': frozen['options'], 'patience_dev_T': frozen['patience_dev'],
           'seeds': {'dev': '40-239', 'validation': '240-439', 'confirmatory': '3000-3199', 'forks': '4000-4039'},
           'budget_cost_units': 3000, 'primary_cost_table': 'llm_proxy', 'units': {
               'labs': 'merit factor, higher is better', 'heilbronn': 'smallest triangle area, higher is better',
               'nk': 'fitness, higher is better'},
           'differences': 'adaptive_v2 minus the other arm, per seed, positive = v2 better; 200 seeds',
           'means': {b: {arm: confirm[b]['arms'][arm]['mean'] for arm in MAIN_ARMS+('timing_shuffled',)} for b in BENCHES},
           'primary': {b: {arm: comp(confirm[b]['comparisons'][arm]) for arm in confirm[b]['primary']} for b in BENCHES},
           'v1_vs_patience_dev': {b: comp(confirm[b]['secondary']['adaptive_v1 vs patience_dev']) for b in BENCHES},
           'J': {'definition': 'mean over benchmarks of (mean paired difference to adaptive_v1) / SD(adaptive_v1)',
                 'adaptive_v2': {'dev': dev_j, 'validation': validation['J']['adaptive_v2'] if validation else None,
                                 'confirmatory': j_conf.get('adaptive_v2')},
                 'patience_dev': {'validation': validation['J']['patience_dev'] if validation else None,
                                  'confirmatory': j_conf.get('patience_dev')}}}
    if forks:
        out['forks'] = {b: {'premature_share_v1': forks['summary'][b]['adaptive_v1']['premature_share'],
                            'premature_share_v2': forks['summary'][b]['adaptive_v2']['premature_share'],
                            'v2_minus_v1': forks['summary'][b]['v2_minus_v1']} for b in BENCHES}
    out['cost_sensitivity'] = {name: {b: {arm: comp(s[b]['comparisons'][arm]) for arm in ('adaptive_v1', 'patience_dev')}
                                      for b in BENCHES} for name, s in cost_runs.items()}
    cost = load(OUT/'cost.json')
    if cost: out['spend'] = cost
    return out


def figure(confirm, path):
    """Dot-and-interval chart of v2 minus each primary arm, one panel per benchmark. Needs matplotlib."""
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
    except ImportError:
        print('matplotlib not installed: skipping the figure'); return
    ink, muted, grid, blue = '#0b0b0b', '#52514e', '#e4e3df', '#2a78d6'
    arms = list(confirm['labs']['primary'])
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.4), sharey=True)
    units = {'labs': 'merit factor', 'heilbronn': 'smallest triangle area ×10⁻³', 'nk': 'fitness'}
    scale = {'labs': 1., 'heilbronn': 1e3, 'nk': 1.}
    from matplotlib.ticker import MaxNLocator
    for ax, b in zip(axes, BENCHES):
        for i, arm in enumerate(arms):
            c = confirm[b]['comparisons'][arm]['final']
            y = len(arms)-1-i
            ax.plot([v*scale[b] for v in c['interval95']], [y, y], color=blue, lw=2, solid_capstyle='round')
            significant = c['holm_p'] < .05
            ax.plot([c['mean']*scale[b]], [y], 'o', ms=8, color=blue, mfc=blue if significant else 'white', mew=2)
        ax.xaxis.set_major_locator(MaxNLocator(5))
        ax.axvline(0, color=muted, lw=1)
        ax.set_title(f"{TITLES[b]} ({units[b]})", color=ink, fontsize=11, loc='left')
        ax.set_xlabel('v2 minus arm (right = v2 better)', color=muted, fontsize=9)
        ax.grid(axis='x', color=grid, lw=.8); ax.set_axisbelow(True)
        for side in ('top', 'right', 'left'): ax.spines[side].set_visible(False)
        ax.spines['bottom'].set_color(grid)
        ax.tick_params(colors=muted, labelsize=8, length=0)
    axes[0].set_yticks(range(len(arms)), [NAMES[a] for a in reversed(arms)], color=ink, fontsize=9)
    fig.suptitle('Adaptive v2 against each primary comparison arm: mean paired difference and 95% bootstrap '
                 'interval, 200 confirmatory seeds\nfilled dot = Holm-adjusted sign test p < 0.05; hollow = no clear '
                 'difference', x=.01, y=.99, ha='left', color=ink, fontsize=10)
    fig.tight_layout(rect=(0, 0, 1, .93))
    fig.savefig(path, dpi=150, facecolor='#fcfcfb')
    plt.close(fig)
    print(f'wrote {path}')


def refresh_results(tables_text, path):
    """Replace each `<!-- tables.md: PREFIX -->` ... `<!-- /tables.md -->` block in RESULTS.md with the
    section of tables.md whose heading starts with PREFIX, so tables in RESULTS.md are never retyped."""
    if not path.exists(): return
    sections, heading = {}, None
    for line in tables_text.splitlines():
        if line.startswith('## '): heading = line[3:].strip(); sections[heading] = []
        elif heading: sections[heading].append(line)
    out, lines, i = [], path.read_text().splitlines(), 0
    while i < len(lines):
        line = lines[i]; out.append(line); i += 1
        if line.startswith('<!-- tables.md: ') and line.endswith('-->'):
            prefix = line[len('<!-- tables.md: '):-3].strip()
            match = [h for h in sections if h.startswith(prefix)]
            if len(match) != 1: raise SystemExit(f'RESULTS.md block {prefix!r} matches {len(match)} sections')
            while i < len(lines) and lines[i] != '<!-- /tables.md -->': i += 1
            out += [l for l in '\n'.join(sections[match[0]]).strip('\n').splitlines()]
            if i < len(lines): out.append(lines[i]); i += 1
    path.write_text('\n'.join(out)+'\n')
    print(f'refreshed tables in {path}')


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
             '## v1 vs v2: what changed and whether it helped (confirmatory seeds 3000-3199)\n',
             v1_vs_v2_table(confirm, forks, cost_runs.get('uniform')),
             '\n## Mean final score, confirmatory seeds 3000-3199, proxy costs\n',
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
    refresh_results('\n'.join(parts), OUT/'RESULTS.md')
    if dev and validation:
        selection = json.loads((OUT/'dev'/'selection.json').read_text())
        dev_j = next(r['J'] for a, r in selection['ranking'] if a == frozen['label'])
        confirm['headline'] = headline(confirm, frozen, validation, forks, cost_runs, dev_j, jc)
        ordered = {'headline': confirm.pop('headline'), **confirm}
        (OUT/'summary.json').write_text(json.dumps(ordered, indent=2)+'\n')
        print(f'wrote headline into {OUT/"summary.json"}')
    figure(confirm, OUT/'comparisons.png')


if __name__ == '__main__': main()
