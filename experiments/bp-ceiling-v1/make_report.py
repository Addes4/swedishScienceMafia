"""Print RESULTS.md tables from the saved JSON and draw the figure, so no number is retyped.

    python experiments/bp-ceiling-v1/make_report.py            # tables to stdout, writes length_gain.png
    python experiments/bp-ceiling-v1/make_report.py --write-headline   # also adds summary.json['headline']
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
REGIMES = ['falsify80', 'weibull500', 'weibull5k']
ARMS = [('linear20', 'hc'), ('linear20', 'cmaes'), ('linear21', 'hc'), ('linear21', 'cmaes'), ('ab_rules', 'grid')]
FIXED = ['first_fit', 'funsearch_weibull', 'funsearch_or']


def ci(x):
    return f'[{x[0]:+.3f}, {x[1]:+.3f}]'


def main():
    s = json.loads((HERE / 'summary.json').read_text())
    cells = {(c['regime'], c['representation'], c['optimizer']): c for c in s['cells']}
    fixed = s['fixed_heuristics']

    print('### Decision table: delta vs best fit, percentage points of the L2 bound (negative = better)\n')
    print('| Regime | best-fit excess over L2 | ' + ' | '.join(f'{r} {o}' for r, o in ARMS) + ' | '
          + ' | '.join(FIXED) + ' |')
    print('|---|---:|' + '---:|' * (len(ARMS) + len(FIXED)))
    for regime in REGIMES:
        row = [regime, f"{fixed[regime]['best_fit']['primary']['excess_percent']:.3f}%"]
        for r, o in ARMS:
            c = cells[(regime, r, o)]
            row.append(f"{c['delta_pp_mean']:+.3f} {ci(c['delta_pp_ci95_seeds'])}")
        for p in FIXED:
            f = fixed[regime][p]['primary']
            row.append(f"{f['delta_pp']:+.3f} {ci(f['delta_pp_ci95_instances'])}")
        print('| ' + ' | '.join(row) + ' |')

    print('\n### Searched arms in detail (audit, 20 seeds each)\n')
    print('| Regime | Arm | Delta pp mean [95% CI over seeds] | Seeds better / identical to best fit | '
          'Best and worst seed | Training change, % of best-fit bins | New bin while an open bin fits | '
          'Bins ending full | Mean seconds |')
    print('|---|---|---:|---:|---:|---:|---:|---:|---:|')
    for regime in REGIMES:
        for r, o in ARMS:
            c = cells[(regime, r, o)]
            print(f"| {regime} | {r} {o} | {c['delta_pp_mean']:+.3f} {ci(c['delta_pp_ci95_seeds'])} | "
                  f"{c['seeds_better_than_best_fit']} / {c['seeds_identical_to_best_fit']} | "
                  f"{c['delta_pp_min']:+.3f} / {c['delta_pp_max']:+.3f} | "
                  f"{c['train_change_percent_of_best_fit_bins_mean']:+.3f} | "
                  f"{100 * c['new_bin_while_open_fits_mean']:.1f}% | {100 * c['full_bins_mean']:.1f}% | "
                  f"{c['mean_seconds']:.0f} |")

    print('\n### Fixed heuristics on the audit sets\n')
    print('| Regime | Policy | Excess over L2 | Delta pp [95% CI over instances] | Wins / ties / losses vs best fit |')
    print('|---|---|---:|---:|---:|')
    for regime in REGIMES:
        for p in ['best_fit'] + FIXED:
            f = fixed[regime][p]['primary']
            print(f"| {regime} | {p} | {f['excess_percent']:.3f}% | {f['delta_pp']:+.3f} "
                  f"{ci(f['delta_pp_ci95_instances'])} | {f['wins']} / {f['ties']} / {f['losses']} |")

    print('\n### falsify80 by family (delta pp vs best fit; searched arms: mean over seeds)\n')
    audit = json.loads((HERE / 'audit.json').read_text())
    families = ['uniform', 'small', 'large', 'bimodal', 'complementary', 'near_thirds', 'near_halves', 'bands']
    print('| Policy | ' + ' | '.join(families) + ' |')
    print('|---|' + '---:|' * len(families))
    for p in FIXED:
        print(f'| {p} | ' + ' | '.join(f"{fixed['falsify80'][p][f]['delta_pp']:+.3f}" for f in families) + ' |')
    for r, o in ARMS:
        rs = [a for a in audit if (a['regime'], a['representation'], a['optimizer']) == ('falsify80', r, o)]
        print(f'| {r} {o} | ' + ' | '.join(
            f"{sum(a['audit'][f]['delta_pp'] for a in rs) / len(rs):+.3f}" for f in families) + ' |')

    pc = s['positive_control']
    print('\n### Positive control: FunSearch Weibull 5k test data (5 instances)\n')
    print(f"Mean L2 bound {pc['mean_l2_bound']}.\n")
    print('| Policy | Mean bins | Excess over L2 | Published |')
    print('|---|---:|---:|---:|')
    for p in ['best_fit', 'first_fit', 'funsearch_weibull', 'funsearch_or']:
        pub = pc['published'].get(p)
        print(f"| {p} | {pc[p]['mean_bins']} | {pc[p]['excess_percent_l2']:.2f}% | "
              f"{'' if pub is None else f'{pub:.2f}%'} |")

    sweep_path = HERE / 'length_sweep.json'
    if sweep_path.exists():
        sweep = json.loads(sweep_path.read_text())
        print('\n### Length sweep (fixed heuristics; delta pp vs best fit, 95% CI over instances)\n')
        print('| Family | n | Instances | Best-fit excess over L2 | first_fit | funsearch_weibull | funsearch_or |')
        print('|---|---:|---:|---:|---:|---:|---:|')
        for row in sweep:
            cols = []
            for p in FIXED:
                cols.append(f"{row[p]['delta_pp']:+.3f} {ci(row[p]['delta_pp_ci95_instances'])}" if p in row else 'n/a')
            print(f"| {row['family']} | {row['n']} | {row['instances']} | {row['best_fit_excess_percent']:.3f}% | "
                  + ' | '.join(cols) + ' |')
        figure(sweep, cells)

    head_path = HERE / 'headroom_80.json'
    if head_path.exists():
        head = json.loads(head_path.read_text())
        print('\n### Headroom at 80 items: best fit against the exact optimum\n')
        print('| Family | Instances (optimum proven) | Best-fit excess over L2 | Best-fit excess over optimum | '
              'Best fit optimal on | Mean bins above optimum |')
        print('|---|---:|---:|---:|---:|---:|')
        for fam, h in head.items():
            print(f"| {fam} | {h['instances']} ({h['optimum_proven']}) | {h['best_fit_excess_percent_over_l2']:.3f}% | "
                  f"{h['best_fit_excess_percent_over_optimum']:.3f}% | {h['instances_where_best_fit_is_optimal']} | "
                  f"{h['mean_bins_best_fit_minus_optimum']:.3f} |")


def write_headline():
    """Add a 'headline' block to summary.json, computed from the saved JSON files."""
    path = HERE / 'summary.json'
    s = json.loads(path.read_text())
    table = s['decision_table']
    usage = [json.loads(line) for line in (HERE / 'modal_usage.jsonl').read_text().splitlines()]
    sweep = json.loads((HERE / 'length_sweep.json').read_text())
    head = json.loads((HERE / 'headroom_80.json').read_text()) if (HERE / 'headroom_80.json').exists() else None
    pick = ['linear20_hc', 'linear21_hc', 'ab_rules_grid', 'funsearch_weibull', 'funsearch_or']
    s['headline'] = {
        'question': 'Is the best-fit ceiling in Falsify the representation (per-bin linear features) or the '
                    'instances (80 items, Falsify families)?',
        'units': 'delta = excess over the L2 bound (percentage points) minus best fit; negative = fewer bins',
        'delta_pp': {regime: {k: {kk: row[k][kk] for kk in row[k] if kk != 'headroom'} | {'headroom': row[k]['headroom']}
                              for k in pick} | {'best_fit_excess_percent': row['best_fit_excess_percent']}
                     for regime, row in table.items()},
        'funsearch_weibull_delta_pp_by_length': {r['n']: r['funsearch_weibull']['delta_pp']
                                                 for r in sweep if r['family'] == 'weibull'},
        'new_bin_while_open_fits_weibull5000': {p: r[p]['new_bin_while_open_fits'] for r in sweep
                                                if r['family'] == 'weibull' and r['n'] == 5000
                                                for p in ['best_fit', 'funsearch_weibull', 'funsearch_or']},
        'positive_control_excess_percent': {p: s['positive_control'][p]['excess_percent_l2']
                                            for p in ['best_fit', 'first_fit', 'funsearch_weibull']},
        'headroom_80_best_fit_excess_over_optimum_percent': (
            {f: h['best_fit_excess_percent_over_optimum'] for f, h in head.items()} if head else None),
        'cost': {'anthropic_usd': 0.0, 'modal_cpu_hours': sum(u.get('seconds', 0) for u in usage) / 3600,
                 'modal_usd_estimate': sum(u.get('estimated_usd', 0) for u in usage),
                 'modal_runs': len(usage), 'modal_failures': sum(not u['ok'] for u in usage)},
        'adapter_commits': {'problems/bin_packing_online': 'ffd72cf', 'generator truncation fix': '6092cae'},
    }
    path.write_text(json.dumps(s, indent=2) + '\n')


def figure(sweep, cells):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    rows = [r for r in sweep if r['family'] == 'weibull']
    ns = [r['n'] for r in rows]
    fig, ax = plt.subplots(figsize=(7.5, 4.6), dpi=150)
    ax.axhline(0, color='#8a8986', linewidth=1)
    ax.text(ns[-1] * 1.1, -0.12, 'best fit', color='#52514e', fontsize=8, va='top', ha='right')
    lines = [('funsearch_weibull', "FunSearch Weibull heuristic (code)", '#2a78d6'),
             ('funsearch_or', "FunSearch OR heuristic (code)", '#eb6834'),
             ('first_fit', 'first fit', '#1baf7a')]
    for key, label, colour in lines:
        pts = [(r['n'], r[key]['delta_pp']) for r in rows if key in r]
        ax.plot([p[0] for p in pts], [p[1] for p in pts], color=colour, linewidth=2, marker='o', markersize=4,
                label=label)
    marks = [(('linear20', 'hc'), 'linear20, searched (hill climb)', '#eda100', 's'),
             (('linear21', 'hc'), 'linear20 + new-bin option, searched', '#e87ba4', 'D'),
             (('ab_rules', 'grid'), 'ab two-threshold rules, grid-tuned', '#008300', '^')]
    for ((rep, opt), label, colour, marker), shift in zip(marks, [0.92, 1.0, 1.08]):
        xs, ys, lo, hi = [], [], [], []
        for regime, n in [('weibull500', 500), ('weibull5k', 5000)]:
            c = cells[(regime, rep, opt)]
            xs.append(n * shift)
            ys.append(c['delta_pp_mean'])
            lo.append(c['delta_pp_mean'] - c['delta_pp_ci95_seeds'][0])
            hi.append(c['delta_pp_ci95_seeds'][1] - c['delta_pp_mean'])
        ax.errorbar(xs, ys, yerr=[lo, hi], fmt=marker, color=colour, markersize=7, capsize=3, linestyle='none',
                    label=label, markeredgecolor='white', markeredgewidth=0.8)
    ax.set_xscale('log')
    ax.set_ylim(-4.5, 4.5)
    ax.set_xlabel('Items per instance (log scale), Weibull(45, 3) sizes, capacity 100')
    ax.set_ylabel('Bins vs best fit\n(percentage points of the L2 bound; lower is better)')
    ax.set_title('Weibull items: bins used relative to best fit, by instance length', fontsize=11, loc='left')
    ax.grid(axis='y', color='#e6e5e1', linewidth=0.6)
    for side in ['top', 'right']:
        ax.spines[side].set_visible(False)
    ax.legend(fontsize=7.5, frameon=False, loc='upper right')
    clipped = [(r['n'], r['funsearch_weibull']['delta_pp']) for r in rows if r['funsearch_weibull']['delta_pp'] > 4.5]
    for n, v in clipped:
        ax.annotate(f'+{v:.1f}', (n, 4.5), xytext=(0, -10), textcoords='offset points', ha='center', fontsize=7,
                    color='#2a78d6')
    fig.tight_layout()
    fig.savefig(HERE / 'length_gain.png')


if __name__ == '__main__':
    import sys
    if '--write-headline' in sys.argv:
        write_headline()
    main()
