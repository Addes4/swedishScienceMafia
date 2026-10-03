"""Build the figure, the Markdown tables and the folder-level summary.json from saved data.

Every number in RESULTS.md comes from the files this script reads; it never retypes one.

    /Users/adriansohrabi/.venvs/ssm/bin/python experiments/memory-ablation-v1/build_report.py

Reads pilot/summary.json, pilot/audit.json, confirmatory/summary.json, confirmatory/audit.json,
confirmatory/runs/*.json.gz and every usage.jsonl / modal_usage.jsonl under this folder. Writes
summary.json, tables.md and confirmatory_figure.png next to this file.
"""
import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))

from falsify.core import read_json  # noqa: E402

ARMS = ['none', 'prose', 'executable']
COLORS = {'none': '#2a78d6', 'prose': '#eb6834', 'executable': '#1baf7a'}  # validated slots 1-3
INK, MUTED = '#0b0b0b', '#52514e'


def usage_totals():
    rows = {}
    for path in sorted(HERE.rglob('usage.jsonl')):
        if path.name != 'usage.jsonl':
            continue
        recs = [json.loads(l) for l in path.read_text().splitlines() if l.strip()]
        live = [r for r in recs if r.get('client') != 'mock']
        msgs = [r for r in live if r['kind'] == 'messages']
        rows[str(path.parent.relative_to(HERE))] = {
            'charged_usd': sum(r.get('charged_usd', 0.0) for r in live),
            'message_attempts': len(msgs), 'failed_attempts': sum(r['status'] != 'ok' for r in msgs),
            'input_tokens': sum(r.get('input_tokens', 0) for r in msgs if r['status'] == 'ok'),
            'output_tokens': sum(r.get('output_tokens', 0) for r in msgs if r['status'] == 'ok'),
            'count_tokens_calls': sum(r['kind'] == 'count_tokens' for r in live),
            'mock_records': len(recs) - len(live)}
    modal = {}
    for path in sorted(HERE.rglob('modal_usage.jsonl')):
        recs = [json.loads(l) for l in path.read_text().splitlines() if l.strip()]
        modal[str(path.parent.relative_to(HERE))] = {
            'estimated_usd': sum(r.get('estimated_usd', 0.0) for r in recs),
            'calls': sum(r['kind'] == 'assess' for r in recs),
            'shard_inputs': sum(r.get('inputs', 0) for r in recs if r['kind'] == 'shards'),
            'remote_seconds': sum(r.get('remote_seconds') or 0 for r in recs),
            'failures': sum((r['kind'] == 'assess' and not r.get('ok', True)) or bool(r.get('failures')) for r in recs)}
    return rows, modal


def fmt(x, nd=3, sign=True):
    if x is None:
        return 'n/a'
    return f'{x:+.{nd}f}' if sign else f'{x:.{nd}f}'


def ci(c, nd=3):
    lo, hi = c['bootstrap_95']
    return f'{fmt(c["mean"], nd)} [{fmt(lo, nd)}, {fmt(hi, nd)}]'


def pilot_section(lines):
    s = read_json(HERE / 'pilot' / 'summary.json')
    lines.append('## Pilot tables (weights regime, seeds 100-101)\n')
    lines.append('| Arm | Final audited excess (bins/instance) | Harmful proposals | Mean diagnostic excess of proposals '
                 '| Proposals packing like the incumbent (mean per run) | Memory tokens (mean) | Cost per run (USD) |')
    lines.append('|---|---:|---:|---:|---:|---:|---:|')
    for arm in ARMS:
        a = s['arms'][arm]
        lines.append(f'| {arm} | {fmt(a["final_audit_excess"], 4)} | {a["harmful_fraction"]:.3f} | '
                     f'{fmt(a["mean_proposal_diagnostic_excess"], 3)} | {a["same_as_incumbent"]:.1f} of 30 | '
                     f'{a["memory_tokens_mean"]:.0f} | {a["cost_usd"]:.4f} |')
    lines.append('')
    return s


def confirmatory_section(lines):
    s = read_json(HERE / 'confirmatory' / 'summary.json')
    a = s['arms']
    lines.append('## Confirmatory tables (Weibull 5k, code, seeds 0-9)\n')
    lines.append('### Primary endpoint: final incumbent on 400 fresh 5,000-item instances\n')
    lines.append('Mean excess bins per instance over best-fit (lower is better; 0 = best-fit). Mean over 10 seeds.\n')
    lines.append('| Arm | Mean excess bins/instance | Runs whose final incumbent is still best-fit | Promotions per run | '
                 'Delta vs best-fit, percentage points of L2 excess |')
    lines.append('|---|---:|---:|---:|---:|')
    for arm in ARMS:
        lines.append(f'| {arm} | {fmt(a[arm]["final_audit_excess"], 2)} | {a[arm]["final_is_best_fit"]} of '
                     f'{a[arm]["runs"]} | {a[arm]["promotions"]:.1f} | {fmt(a[arm]["final_delta_pp_vs_best_fit"], 3)} |')
    ref = s['references']['funsearch_weibull']
    lines.append(f'| FunSearch Weibull heuristic (fixed reference, not an arm) | {fmt(ref["mean_excess_vs_best_fit"], 2)} '
                 f'(instance 95% CI [{fmt(ref["instance_bootstrap_95"][0], 2)}, {fmt(ref["instance_bootstrap_95"][1], 2)}]; '
                 f'{ref["wins"]}/{ref["ties"]}/{ref["losses"]} wins/ties/losses) | | | {fmt(ref["delta_pp_vs_best_fit"], 3)} |')
    lines.append(f'\nBest-fit: {s["references"]["best_fit_mean_bins"]:.2f} bins per instance, '
                 f'{s["references"]["best_fit_excess_percent_over_l2"]:.3f}% above the L2 lower bound.\n')
    lines.append('### Paired contrasts (difference of arm means, paired by seed; 95% bootstrap interval)\n')
    lines.append('| Metric | executable - prose | executable - none | prose - none |')
    lines.append('|---|---|---|---|')
    by = {(c['comparison'], c['metric']): c for c in s['comparisons']}
    names = {'final_audit_excess': 'Final audited excess (bins/instance)',
             'harmful_fraction': 'Harmful proposals (share of valid)',
             'worse_than_incumbent_fraction': 'Worse than incumbent of the time (share of valid)',
             'no_op_fraction': 'No-op proposals (share of valid)',
             'repeated_failed': 'Repeats of an earlier failed proposal (count per run)',
             'reverts_to_former_incumbent': 'Reverts to a former incumbent (count per run)',
             'best_fixed_vs_best_fit': 'Best fixed-suite result (bins/instance vs best-fit)'}
    for metric, label in names.items():
        cells = []
        for comp in ['executable - prose', 'executable - none', 'prose - none']:
            c = by.get((comp, metric))
            cells.append(ci(c, 2 if 'excess' in metric or 'best_fixed' in metric else 3) if c else 'n/a')
        lines.append(f'| {label} | ' + ' | '.join(cells) + ' |')
    lines.append('\n### Secondary endpoints per arm (means over 10 runs)\n')
    lines.append('| Arm | Valid proposals | Gate rejections | Runtime failures | Harmful | Worse than incumbent | No-op | '
                 'Repeats | Reverts | Memory tokens | Counterexamples shown | Input tokens/run | Output tokens/run | USD/run |')
    lines.append('|---|' + '---:|' * 13)
    for arm in ARMS:
        x = a[arm]
        lines.append(f'| {arm} | {x["valid_proposals"]:.1f} | {x["static_rejections"]:.1f} | {x["runtime_errors"]:.1f} | '
                     f'{x["harmful_fraction"]:.3f} | {x["worse_than_incumbent_fraction"]:.3f} | {x["no_op_fraction"]:.3f} | '
                     f'{x["repeated_failed"]:.1f} | {x["reverts_to_former_incumbent"]:.1f} | {x["memory_tokens_mean"]:.0f} | '
                     f'{x["memory_counterexamples_mean"]:.2f} | {x["input_tokens"]:.0f} | {x["output_tokens"]:.0f} | '
                     f'{x["cost_usd"]:.4f} |')
    lines += memory_fill_lines()
    lines.append('\n### Similarity of promoted and final candidates to FunSearch\'s heuristic\n')
    lines.append('Agreement = share of decisions on 2 fresh 5,000-item instances where FunSearch\'s heuristic (or best-fit), '
                 'given the same bins, picks a bin with the same remaining capacity. Near-copy = agreement >= 0.99. '
                 f'{conf_summary_sim(s)}\n')
    lines.append('| Arm | Near-copies among promoted candidates | Runs with a non-best-fit final | '
                 'Their mean agreement with FunSearch | Their mean agreement with best-fit |')
    lines.append('|---|---:|---:|---:|---:|')
    for arm in ARMS:
        x = a[arm]
        lines.append(f'| {arm} | {x["promoted_near_copies_of_funsearch"] * x["runs"]:.0f} | {x["runs"] - x["final_is_best_fit"]} of '
                     f'{x["runs"]} | {fmt(x["final_agreement_with_funsearch"], 3, False)} | '
                     f'{fmt(x["final_agreement_with_best_fit"], 3, False)} |')
    lines.append('')
    return s


def memory_fill_lines():
    """Why realized memory tokens differ between arms, and what the counterexamples look like."""
    import statistics
    out = ['\n### Memory fill and counterexample composition (all 10 runs per arm)\n',
           '| Arm | Calls | Mean memory tokens (budget 1,500) | Median candidate entries per prompt | '
           'Calls where the 8-counterexample cap was within 1 | Kept counterexamples | Of which 2 items long | '
           'Of which first difference = policy opened a new bin |', '|---|---:|---:|---:|---:|---:|---:|---:|']
    for arm in ('prose', 'executable'):
        calls = tokens = near_cap = kept = two = new = 0
        cands = []
        for path in sorted((HERE / 'confirmatory' / 'runs').glob(f'{arm}-s*.json.gz')):
            for r in read_json(path)['history']:
                calls += 1
                tokens += r['memory']['tokens']
                cands.append(r['memory']['candidates'])
                near_cap += r['memory']['counterexamples'] >= 7
                mining = r.get('mining') or {}
                # With best-fit as incumbent both keys hold the same mining pass; count it once.
                refs = ['incumbent'] if r['incumbent_before'] == 'best_fit' else list(mining)
                for m in (mining[w] for w in refs if w in mining):
                    for cx in m['counterexamples']:
                        kept += 1
                        two += len(cx['items']) == 2
                        new += bool(cx['divergence'] and cx['divergence']['candidate_new'])
        out.append(f'| {arm} | {calls} | {tokens / calls:.0f} | {statistics.median(cands):g} | {near_cap} | {kept} | {two} | {new} |')
    out.append('\nKept counterexamples: shrunk losing streams of at most 30 items, re-verified in fresh processes, over all '
               'proposals of the arm and both references. The prose arm computes them too but shows only a verbal summary.')
    return out


def conf_summary_sim(s):
    audit = read_json(HERE / 'confirmatory' / 'audit.json')
    sims = [v['agreement_with_funsearch'] for v in audit['similarity'].values() if 'agreement_with_funsearch' in v]
    return (f'{s["distinct_promoted_candidates"]} distinct promoted candidates were checked; the highest agreement with '
            f'FunSearch was {max(sims):.3f}; near-copies: {s["promoted_near_copies_of_funsearch"]}.')


def figure(path):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from falsify.funsearch_heuristics import funsearch_weibull
    from falsify.longpack import pack_priority, weibull_items
    traces = {(t['arm'], t['seed']): t for t in (read_json(p) for p in sorted((HERE / 'confirmatory' / 'runs').glob('*.json.gz')))}
    audit = read_json(HERE / 'confirmatory' / 'audit.json')
    summary = read_json(HERE / 'confirmatory' / 'summary.json')
    seeds = sorted({s for _, s in traces})
    fs_fixed = {}
    for seed in seeds:
        t = traces[('none', seed)]
        bins = [pack_priority(funsearch_weibull, weibull_items(sd, n, ns)) for ns, sd, n in t['fixed_specs']]
        # FunSearch's heuristic on each run's fixed search suite (reported in summary.json).
        fs_fixed[seed] = sum(b - r for b, r in zip(bins, t['fixed_best_fit_bins'])) / len(bins)
    fs_mean = sum(fs_fixed.values()) / len(fs_fixed)
    fig, ax2 = plt.subplots(figsize=(6.4, 4.4))
    ax2.spines[['top', 'right']].set_visible(False)
    ax2.grid(axis='y', color='#e4e3df', linewidth=0.8)
    ax2.set_axisbelow(True)
    ax2.tick_params(colors=MUTED)
    for i, arm in enumerate(ARMS):
        vals = [audit['per_run'][f'{arm}-s{s}']['metrics']['final_audit_excess'] for s in seeds]
        xs = [i + (j - 4.5) * 0.04 for j in range(len(vals))]
        ax2.scatter(xs, vals, s=36, color=COLORS[arm], edgecolor='white', linewidth=1.5, zorder=3)
        mean_v = summary['arms'][arm]['final_audit_excess']
        ax2.plot([i - 0.25, i + 0.25], [mean_v, mean_v], color=INK, linewidth=2, zorder=4)
    ref = summary['references']['funsearch_weibull']['mean_excess_vs_best_fit']
    ax2.axhline(ref, color=MUTED, linestyle='--', linewidth=1)
    ax2.annotate("FunSearch's heuristic", (-0.45, ref), xytext=(0, 4), textcoords='offset points', color=MUTED, fontsize=8)
    ax2.axhline(0, color=MUTED, linewidth=1)
    ax2.annotate('best-fit', (-0.45, 0), xytext=(0, 4), textcoords='offset points', color=MUTED, fontsize=8)
    ax2.set_xticks(range(len(ARMS)), ARMS, color=INK)
    ax2.set_xlim(-0.5, 2.5)
    ax2.set_ylabel('Final incumbent bins per instance minus best-fit\n(400 fresh audit instances; dot = seed, bar = mean)',
                   color=INK)
    ax2.set_title('Final incumbent after 30 calls, per arm', color=INK, loc='left', fontsize=11)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    return {'funsearch_fixed_suite_mean_vs_best_fit': fs_mean}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--no-figure', action='store_true')
    args = parser.parse_args()
    lines = ['<!-- Generated by build_report.py from the saved JSON; do not edit by hand. -->\n']
    pilot = pilot_section(lines)
    conf = confirmatory_section(lines) if (HERE / 'confirmatory' / 'summary.json').exists() else None
    usage, modal = usage_totals()
    lines.append('## Spend by folder\n')
    lines.append('| Folder | Anthropic USD | Message attempts | Failed attempts | Input tokens | Output tokens |')
    lines.append('|---|---:|---:|---:|---:|---:|')
    for k, v in usage.items():
        lines.append(f'| {k} | {v["charged_usd"]:.4f} | {v["message_attempts"]} | {v["failed_attempts"]} | '
                     f'{v["input_tokens"]} | {v["output_tokens"]} |')
    total = sum(v['charged_usd'] for v in usage.values())
    modal_total = sum(v['estimated_usd'] for v in modal.values())
    lines.append(f'| **total** | **{total:.4f}** | | | | |\n')
    lines.append('| Folder | Modal USD (estimate) | Evaluation calls | Shard inputs | Remote seconds | Failures |')
    lines.append('|---|---:|---:|---:|---:|---:|')
    for k, v in modal.items():
        lines.append(f'| {k} | {v["estimated_usd"]:.4f} | {v["calls"]} | {v["shard_inputs"]} | {v["remote_seconds"]:.0f} | '
                     f'{v["failures"]} |')
    lines.append(f'| **total** | **{modal_total:.4f}** | | | | |\n')
    extra = figure(HERE / 'confirmatory_figure.png') if conf and not args.no_figure else {}
    out = {'experiment': 'memory-ablation-v1',
           'question': 'Does executable counterexample memory beat no memory or token-matched prose memory in a '
                       'closed-loop LLM search, on audited final quality?',
           'pilot': {'regime': 'weights20_synthetic80', 'seeds': pilot['seeds'], 'calls_per_run': 30,
                     'arms': {arm: {k: pilot['arms'][arm][k] for k in ('final_audit_excess', 'harmful_fraction',
                                                                         'mean_proposal_diagnostic_excess',
                                                                         'same_as_incumbent', 'promotions',
                                                                         'memory_tokens_mean', 'cost_usd')}
                              for arm in ARMS},
                     'verdict': 'primary endpoint at its floor: no promotions, every final incumbent is best-fit'},
           'spend': {'anthropic_usd_by_folder': {k: v['charged_usd'] for k, v in usage.items()},
                     'anthropic_usd_total': total, 'modal_usd_estimate_by_folder': {k: v['estimated_usd'] for k, v in modal.items()},
                     'modal_usd_estimate_total': modal_total}}
    if conf:
        out['confirmatory'] = {'regime': 'weibull5k_code', 'seeds': conf['seeds'], 'calls_per_run': 30,
                               'primary_endpoint': 'audited mean excess bins per instance of the final incumbent over best-fit '
                                                   '(400 fresh 5,000-item instances; lower is better)',
                               'arms': conf['arms'], 'comparisons': [{k: c[k] for k in ('comparison', 'metric', 'mean',
                                                                                          'bootstrap_95', 'n')}
                                                                     for c in conf['comparisons']],
                               'funsearch_reference': conf['references']['funsearch_weibull'],
                               'best_fit_mean_bins': conf['references']['best_fit_mean_bins'],
                               'audit_seed': conf['audit_seed'], 'trace_digest': conf['trace_digest'], **extra}
    (HERE / 'summary.json').write_text(json.dumps(out, indent=2) + '\n')
    (HERE / 'tables.md').write_text('\n'.join(lines) + '\n')
    print('\n'.join(lines))


if __name__ == '__main__':
    main()
