"""overfit-gates-v1 analysis: selection gaps, offline best-of-K, and the gate replay.

Reads pool_scores.jsonl, pool_best_fit.json, archive_scores.jsonl and archive_inputs.json
(written by score.py) and writes summary.json and tables.md. No scoring happens here.
    python experiments/overfit-gates-v1/analyze.py
"""
import json
import math
import os
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
DATA = Path(os.environ.get('OGV1_DATA', HERE))  # data files; a different folder only for testing
sys.path.insert(0, str(HERE))
from score import load_runs  # noqa: E402

A = list(range(0, 24))      # truth
B = list(range(24, 36))     # Thresholdout holdout
C = list(range(36, 40))     # soft-gate validation
MATERIAL = 0.5
BOOT, BOOT_SEED = 10000, 4242
GATES = ['G0 score-only', 'G1 sign test', 'G2 Ladder', 'G3 Thresholdout', 'G4 strict archive',
         'G5 random veto', 'G6 soft gate']


def load_jsonl(path):
    return [json.loads(x) for x in path.read_text().splitlines() if x.strip()] if path.exists() else []


def binom_tail(w, m):
    return sum(math.comb(m, k) for k in range(w, m + 1)) / 2 ** m


def boot_mean(x, rng, n=BOOT):
    x = np.asarray(x, float)
    idx = rng.integers(0, len(x), size=(n, len(x)))
    means = x[idx].mean(axis=1)
    lo, hi = np.percentile(means, [2.5, 97.5])
    zero = (means == 0).mean()  # mid-p: resamples with a mean of exactly 0 count half each way
    p = 2 * min((means < 0).mean() + zero / 2, (means > 0).mean() + zero / 2)
    return float(x.mean()), [float(lo), float(hi)], float(min(1.0, p))


def holm(pvals):
    order = sorted(range(len(pvals)), key=lambda i: pvals[i])
    adj, running = [0.0] * len(pvals), 0.0
    for rank, i in enumerate(order):
        running = max(running, min(1.0, (len(pvals) - rank) * pvals[i]))
        adj[i] = running
    return adj


class Program:
    """Bins of one program (or best fit) on the fixed suite, the pool and a run's short inputs."""

    def __init__(self, fixed, pool, short=None, short_random=None, name='best_fit', call=-1):
        self.fixed, self.pool = np.asarray(fixed, float), pool
        self.short, self.short_random, self.name, self.call = short, short_random, name, call

    def mean(self, idx):
        vals = [self.pool[i] for i in idx]
        return None if any(v is None for v in vals) else float(np.mean(vals))


def thresholdout(train, hold, state, T, sigma, rng):
    if state['budget'] <= 0:
        return None
    eta = rng.laplace(0, 4 * sigma)
    if abs(train - hold) > T + state['gamma'] + eta:
        state['budget'] -= 1
        state['gamma'] = rng.laplace(0, 2 * sigma)
        return hold + rng.laplace(0, sigma)
    return train


def replay(run, props, bf, inputs, run_index, gate, T=2.0, sigma=0.5):
    """Replay one run's stream through one gate. Returns per-proposal decisions and the final incumbent."""
    inc = bf
    rng = np.random.default_rng(20261004 + run_index)
    state = {'budget': 30, 'gamma': rng.laplace(0, 2 * sigma)}
    rows, cost = [], 0
    for p in props:
        truth_p, truth_i = p.mean(A), inc.mean(A)
        valid = truth_p is not None and p.short is not None
        delta = p.fixed - inc.fixed
        promote = False
        if valid:
            g0 = delta.sum() < 0
            active = [i for i, x in enumerate(inputs) if x['mined_at'] < p.call]
            if gate == 'G0 score-only':
                promote = g0
            elif gate == 'G1 sign test':
                w, l = int((delta < 0).sum()), int((delta > 0).sum())
                promote = w + l > 0 and binom_tail(w, w + l) <= 0.05
            elif gate == 'G2 Ladder':
                sd = delta.std(ddof=1)
                promote = delta.mean() < 0 and (sd == 0 or -delta.mean() > sd / math.sqrt(len(delta)))
            elif gate == 'G3 Thresholdout':
                hp, hi = p.mean(B), inc.mean(B)
                cost += len(B) * 5000 if state['budget'] > 0 else 0
                if hp is not None:
                    ans = thresholdout(delta.mean(), hp - hi, state, T, sigma, rng)
                    promote = ans is not None and ans < 0
            elif gate in ('G4 strict archive', 'G5 random veto'):
                if g0:
                    key = 'short' if gate == 'G4 strict archive' else 'short_random'
                    cb, ib = getattr(p, key), getattr(inc, key)
                    cost += sum(len(inputs[i]['items']) for i in active)
                    promote = all(cb[i] is not None and cb[i] <= ib[i] for i in active)
            elif gate == 'G6 soft gate':
                if g0:
                    cost += sum(len(inputs[i]['items']) for i in active) + len(C) * 5000
                    regs = [10 ** 6 if cb is None else cb - ib
                            for cb, ib in ((p.short[i], inc.short[i]) for i in active) if cb is None or cb > ib]
                    ok_arch = len(regs) <= 2 and all(r == 1 for r in regs)
                    cp, ci = p.mean(C), inc.mean(C)
                    promote = ok_arch and cp is not None and cp <= ci
        better = valid and truth_p < truth_i
        material = valid and truth_i - truth_p >= MATERIAL
        rows.append({'call': p.call, 'valid': valid, 'promote': bool(promote), 'better': bool(better),
                     'material': bool(material), 'truth_delta': (truth_p - truth_i) if valid else None})
        if promote:
            inc = p
    return rows, inc, cost


def main():
    runs = load_runs()
    pool = {r['group']: r for r in load_jsonl(DATA / 'pool_scores.jsonl')}
    bf_pool = json.loads((DATA / 'pool_best_fit.json').read_text())
    bf_bins = [r['best_fit'] for r in bf_pool]
    shorts = {(r['run_id'], r['group']): r for r in load_jsonl(DATA / 'archive_scores.jsonl')}
    meta = {m['run_id']: m for m in json.loads((DATA / 'archive_inputs.json').read_text())}
    missing = [g for r in runs for g in {p['group'] for p in r['proposals']} if g not in pool]
    if missing:
        raise SystemExit(f'{len(set(missing))} groups not yet scored on the pool; run score.py pool')

    import hashlib
    summary = {'protocol_sha256': hashlib.sha256((HERE / 'PROTOCOL.md').read_bytes()).hexdigest(), 'runs': len(runs), 'valid_proposals': sum(len(r['proposals']) for r in runs),
               'groups': len(pool), 'pool_best_fit_mean_bins_A': float(np.mean([bf_bins[i] for i in A]))}
    fails = {g: sum(b is None for b in v['bins']) for g, v in pool.items()}
    summary['groups_with_pool_failures'] = sum(1 for v in fails.values() if v)

    # ---------------- 1. as-run selection gap ----------------
    rng = np.random.default_rng(BOOT_SEED)
    promos, finals = [], []
    for r in runs:
        bf_fixed = np.asarray(r['fixed_best_fit_bins'], float)
        last = None
        for p in r['proposals']:
            if p['promoted']:
                pb = pool[p['group']]['bins']
                if any(pb[i] is None for i in A):
                    continue
                fixed_adv = float((bf_fixed - np.asarray(p['fixed_bins'], float)).mean())
                fresh_adv = float(np.mean([bf_bins[i] - pb[i] for i in A]))
                promos.append({'run_id': r['run_id'], 'call': p['call'], 'fixed_adv': fixed_adv,
                               'fresh_adv': fresh_adv, 'gap': fixed_adv - fresh_adv})
                last = promos[-1]
        finals.append({'run_id': r['run_id'], 'fixed_adv': last['fixed_adv'] if last else 0.0,
                       'fresh_adv': last['fresh_adv'] if last else 0.0, 'promoted': last is not None})
    by_run = {}
    for x in promos:
        by_run.setdefault(x['run_id'], []).append(x['gap'])
    run_gaps = [np.mean(v) for v in by_run.values()]
    m, ci, p = boot_mean(run_gaps, rng)
    early = [x['gap'] for x in promos if x['call'] < 10]
    late = [x['gap'] for x in promos if x['call'] >= 10]
    summary['as_run'] = {
        'promotions': len(promos), 'runs_with_promotion': len(by_run), 'promotions_detail': promos,
        'mean_gap_bins_per_instance_runs_resampled': m, 'ci95': ci,
        'mean_gap_calls_0_9': float(np.mean(early)) if early else None, 'n_calls_0_9': len(early),
        'mean_gap_calls_10_29': float(np.mean(late)) if late else None, 'n_calls_10_29': len(late),
        'final_incumbents': finals,
        'final_fixed_adv_mean': float(np.mean([f['fixed_adv'] for f in finals])),
        'final_fresh_adv_mean': float(np.mean([f['fresh_adv'] for f in finals])),
    }

    # ---------------- 2. offline best-of-K ----------------
    rng2 = np.random.default_rng(BOOT_SEED + 1)
    offline = []
    pool_idx = np.arange(40)
    for n in (1, 2, 5, 10):
        for K in (1, 2, 5, 10, 20, 30):
            gaps, sig = [], []
            for r in runs:
                cands = [np.asarray(pool[p['group']]['bins'], float) for p in r['proposals'][:K]
                         if all(b is not None for b in pool[p['group']]['bins'])]
                if not cands:
                    continue
                adv = np.vstack([np.zeros(40)] + [np.asarray(bf_bins, float) - c for c in cands])  # row 0 = best fit
                distinct = np.unique(adv[1:], axis=0)
                if len(distinct):
                    sig.append(float(np.sqrt(np.mean(distinct.var(axis=1, ddof=1)))))
                for _ in range(500):
                    pub = rng2.choice(pool_idx, size=n, replace=False)
                    rest = np.setdiff1d(pool_idx, pub)
                    j = int(np.argmax(adv[:, pub].mean(axis=1)))
                    gaps.append(adv[j, pub].mean() - adv[j, rest].mean())
            s = float(np.mean(sig)) if sig else 0.0
            offline.append({'n': n, 'K': K, 'mean_gap': float(np.mean(gaps)), 'sigma': s,
                            'bound_sigma_sqrt_2lnK_over_n': s * math.sqrt(2 * math.log(K) / n) if K > 1 else 0.0})
    summary['offline_best_of_K'] = offline

    # ---------------- 3. gate replay ----------------
    def program(r, p):
        sh = shorts.get((r['run_id'], p['group']))
        k = len(meta[r['run_id']]['inputs'])
        s = sh['bins'][:k] if sh and len(sh['bins']) == 2 * k else (None if k else [])
        sr = sh['bins'][k:] if sh and len(sh['bins']) == 2 * k else (None if k else [])
        return Program(p['fixed_bins'], pool[p['group']]['bins'], s, sr, p['group'], p['call'])

    per_run_final = {g: {} for g in GATES}
    fa_split = {g: {'tie': 0, 'worse': 0} for g in GATES}
    per_gate = {g: {'final_adv': [], 'promotions': 0, 'FA': 0, 'FR': 0, 'FA_mat': 0, 'FR_mat': 0, 'better': 0,
                    'material': 0, 'valid': 0, 'cost_items': 0, 'per_run_FR': [], 'per_run_FA': []} for g in GATES}
    sens = {T: [] for T in (1.0, 4.0)}
    asrun_match = True
    bf_A = float(np.mean([bf_bins[i] for i in A]))
    for ri, r in enumerate(runs):
        mm = meta[r['run_id']]
        bf = Program(r['fixed_best_fit_bins'], bf_bins, mm['best_fit'], mm['best_fit_random'])
        props = [program(r, p) for p in r['proposals']]
        for g in GATES:
            rows, inc, cost = replay(r, props, bf, mm['inputs'], ri, g)
            st = per_gate[g]
            st['final_adv'].append(bf_A - inc.mean(A))
            per_run_final[g][r['run_id']] = bf_A - inc.mean(A)
            for x in rows:
                if x['promote'] and not x['better']:
                    fa_split[g]['tie' if x['truth_delta'] == 0 else 'worse'] += 1
            st['promotions'] += sum(x['promote'] for x in rows)
            fa = sum(x['promote'] and not x['better'] for x in rows)
            fr = sum(x['better'] and not x['promote'] for x in rows)
            st['FA'] += fa
            st['FR'] += fr
            st['per_run_FA'].append(fa)
            st['per_run_FR'].append(fr)
            st['FA_mat'] += sum(x['promote'] and not x['material'] for x in rows)
            st['FR_mat'] += sum(x['material'] and not x['promote'] for x in rows)
            st['better'] += sum(x['better'] for x in rows)
            st['material'] += sum(x['material'] for x in rows)
            st['valid'] += sum(x['valid'] for x in rows)
            st['cost_items'] += cost
            if g == 'G0 score-only':
                asrun = [p['promoted'] for p in r['proposals']]
                asrun_match &= asrun == [x['promote'] for x in rows]
        for T in sens:
            rows, inc, _ = replay(r, props, bf, mm['inputs'], ri, 'G3 Thresholdout', T=T)
            sens[T].append(bf_A - inc.mean(A))
    summary['positive_control_2_G0_reproduces_as_run'] = bool(asrun_match)
    rng3 = np.random.default_rng(BOOT_SEED + 2)
    gate_rows, contrasts = [], []
    for g in GATES:
        st = per_gate[g]
        m, ci, _ = boot_mean(st['final_adv'], rng3)
        gate_rows.append({'gate': g, 'promotions': st['promotions'], 'false_accept': st['FA'],
                          'false_reject': st['FR'], 'truly_better': st['better'],
                          'FA_share_of_promotions': st['FA'] / st['promotions'] if st['promotions'] else None,
                          'FR_share_of_truly_better': st['FR'] / st['better'] if st['better'] else None,
                          'false_accept_material': st['FA_mat'], 'false_reject_material': st['FR_mat'],
                          'materially_better': st['material'], 'valid_proposals': st['valid'],
                          'final_fresh_adv_mean': m, 'final_fresh_adv_ci95': ci,
                          'extra_items_packed': st['cost_items']})
        if g != 'G0 score-only':
            d = np.asarray(st['final_adv']) - np.asarray(per_gate['G0 score-only']['final_adv'])
            dm, dci, dp = boot_mean(d, rng3)
            contrasts.append({'contrast': f'{g} - G0', 'mean': dm, 'ci95': dci, 'p_boot': dp})
    for c, adj in zip(contrasts, holm([c['p_boot'] for c in contrasts])):
        c['p_holm'] = adj
    d45 = np.asarray(per_gate['G4 strict archive']['per_run_FR']) - np.asarray(per_gate['G5 random veto']['per_run_FR'])
    m45, ci45, p45 = boot_mean(d45, rng3)
    summary['gates'] = gate_rows
    summary['contrasts_final_fresh_adv_vs_G0'] = contrasts
    summary['G4_minus_G5_false_rejections_per_run'] = {'mean': m45, 'ci95': ci45, 'p_boot': p45}
    summary['post_hoc'] = {
        'note': 'Diagnostics added after the first analysis run; not in PROTOCOL.md.',
        'false_accept_split_tie_vs_worse_on_A': fa_split,
        'per_run_final_fresh_adv': {g: per_run_final[g] for g in
                                    ('G0 score-only', 'G4 strict archive', 'G5 random veto', 'G6 soft gate')},
        'paired_sigma': paired_sigma(runs, pool, bf_bins),
    }
    summary['G3_sensitivity'] = {f'T={T:g}': float(np.mean(v)) for T, v in sens.items()}
    summary['units'] = ('advantage = best-fit bins minus program bins, per instance (positive = fewer bins); '
                        'fresh = split A, 24 instances')
    (DATA / 'summary.json').write_text(json.dumps(summary, indent=1))
    write_tables(summary)
    print(json.dumps({k: summary[k] for k in ('positive_control_2_G0_reproduces_as_run',)}, indent=1))
    print((DATA / 'tables.md').read_text())


def paired_sigma(runs, pool, bf_bins):
    """SD over the 40 pool instances of the per-instance difference between a run's best proposal
    (by pool mean) and each other distinct proposal within 2 bins/instance of it: the noise that
    actually separates competitive candidates."""
    sds, n_close = [], []
    for r in runs:
        progs = {p['group']: np.asarray(pool[p['group']]['bins'], float) for p in r['proposals']}
        progs['best_fit'] = np.asarray(bf_bins, float)
        best = min(progs.values(), key=lambda b: b.mean())
        close = [b for b in progs.values() if b is not best and b.mean() - best.mean() <= 2.0]
        n_close.append(len(close))
        sds += [float((b - best).std(ddof=1)) for b in close]
    return {'median_sd_of_paired_difference': float(np.median(sds)) if sds else None,
            'mean_sd_of_paired_difference': float(np.mean(sds)) if sds else None,
            'pairs': len(sds), 'runs_with_a_close_competitor': int(sum(k > 0 for k in n_close))}


def f(x, d=2):
    return '—' if x is None else f'{x:.{d}f}'


def write_tables(s):
    a = s['as_run']
    out = ['# overfit-gates-v1 tables (generated by analyze.py from summary.json)', '',
           f"Valid proposals {s['valid_proposals']}, behaviour groups {s['groups']}, runs {s['runs']}. "
           f"Advantage = best-fit bins minus program bins per instance; fresh = split A (24 instances).", '',
           '## 1. As-run promotions: fixed-suite vs fresh advantage', '',
           '| run | call | fixed adv | fresh adv | gap |', '|---|---|---|---|---|']
    for x in a['promotions_detail']:
        out.append(f"| {x['run_id']} | {x['call']} | {f(x['fixed_adv'])} | {f(x['fresh_adv'])} | {f(x['gap'])} |")
    out += ['', f"Mean gap (runs resampled): {f(a['mean_gap_bins_per_instance_runs_resampled'])} "
                f"[{f(a['ci95'][0])}, {f(a['ci95'][1])}] bins/instance over {a['promotions']} promotions in "
                f"{a['runs_with_promotion']} runs. Calls 0-9: {f(a['mean_gap_calls_0_9'])} (n={a['n_calls_0_9']}); "
                f"calls 10-29: {f(a['mean_gap_calls_10_29'])} (n={a['n_calls_10_29']}).",
            f"Final incumbents, mean over 30 runs: fixed adv {f(a['final_fixed_adv_mean'])}, "
            f"fresh adv {f(a['final_fresh_adv_mean'])}.", '',
            '## 2. Offline best-of-K (selection only)', '',
            '| n public | K | mean gap | σ | σ√(2 ln K / n) |', '|---|---|---|---|---|']
    for x in s['offline_best_of_K']:
        out.append(f"| {x['n']} | {x['K']} | {f(x['mean_gap'])} | {f(x['sigma'])} | "
                   f"{f(x['bound_sigma_sqrt_2lnK_over_n'])} |")
    out += ['', '## 3. Gate replay (open loop)', '',
            '| gate | promotions | false acc. | false rej. | truly better | FA share | FR share | '
            'FA (material) | FR (material) | final fresh adv [95% CI] | extra items |',
            '|---|---|---|---|---|---|---|---|---|---|---|']
    for g in s['gates']:
        out.append(f"| {g['gate']} | {g['promotions']} | {g['false_accept']} | {g['false_reject']} | "
                   f"{g['truly_better']} | {f(g['FA_share_of_promotions'])} | {f(g['FR_share_of_truly_better'])} | "
                   f"{g['false_accept_material']} | {g['false_reject_material']} | {f(g['final_fresh_adv_mean'])} "
                   f"[{f(g['final_fresh_adv_ci95'][0])}, {f(g['final_fresh_adv_ci95'][1])}] | {g['extra_items_packed']:,} |")
    out += ['', '| contrast (final fresh adv) | mean | 95% CI | p (bootstrap) | p (Holm) |', '|---|---|---|---|---|']
    for c in s['contrasts_final_fresh_adv_vs_G0']:
        out.append(f"| {c['contrast']} | {f(c['mean'])} | [{f(c['ci95'][0])}, {f(c['ci95'][1])}] | "
                   f"{f(c['p_boot'], 3)} | {f(c['p_holm'], 3)} |")
    g45 = s['G4_minus_G5_false_rejections_per_run']
    out += ['', f"G4 − G5 false rejections per run: {f(g45['mean'])} [{f(g45['ci95'][0])}, {f(g45['ci95'][1])}]"
                f" (p {f(g45['p_boot'], 3)}).",
            f"Thresholdout sensitivity, final fresh adv: " + ', '.join(f'{k}: {f(v)}' for k, v in s['G3_sensitivity'].items()),
            f"Positive control 2 (G0 replay reproduces the as-run promotions): {s['positive_control_2_G0_reproduces_as_run']}."]
    (DATA / 'tables.md').write_text('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
