"""overfit-gates-v1: re-score memory-ablation-v1's saved proposals on fresh instances (CPU only).

Run from the repository root with the project venv:
    python experiments/overfit-gates-v1/score.py control            # positive control 1
    python experiments/overfit-gates-v1/score.py pool --workers 2   # every behaviour group on the 40-instance pool
    python experiments/overfit-gates-v1/score.py dedup --workers 2  # second members of up to 20 groups, pool seeds 0-3
    python experiments/overfit-gates-v1/score.py archive --workers 2  # archived and random-veto short inputs
    python experiments/overfit-gates-v1/analyze.py                  # gates, gaps, summary.json, tables.md

Every scoring step is resumable: results are appended to JSONL files in this folder and skipped
on a re-run. No API or Modal calls. See PROTOCOL.md.
"""
import argparse
import concurrent.futures as cf
import glob
import gzip
import hashlib
import json
import os
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))

from falsify.code_eval import (CandidateError, PersistentPacker, pack_fresh, packing_hash,  # noqa: E402
                               screen, write_program)
from falsify.longpack import l2_bound, pack_rule, weibull_items  # noqa: E402

RUNS = ROOT / 'experiments' / 'memory-ablation-v1' / 'confirmatory' / 'runs'
POOL_NS = 'overfit-gates-v1/fresh'
RANDOM_NS = 'overfit-gates-v1/random-veto'
POOL_SEEDS = list(range(40))
N_ITEMS = 5000
TIMEOUT_S, RETRY_TIMEOUT_S = 30, 60


def load_runs():
    """Runs with their valid proposals, each tagged with a behaviour-group key."""
    runs = []
    for f in sorted(glob.glob(str(RUNS / '*.json.gz'))):
        d = json.load(gzip.open(f))
        props = []
        for h in d['history']:
            ev = h.get('evaluation') or {}
            if h.get('status') != 'ok' or not h.get('code') or ev.get('status') != 'ok':
                continue
            props.append({'call': h['call'], 'code': h['code'], 'fixed_bins': ev['fixed_bins'],
                          'hashes': ev['fixed_hashes'], 'promoted': bool(h['promoted']),
                          'group': hashlib.sha256('|'.join(ev['fixed_hashes']).encode()).hexdigest()[:16],
                          'code_sha': hashlib.sha256(h['code'].encode()).hexdigest()[:16]})
        mining = {}
        for h in d['history']:
            m = h.get('mining') or {}
            cxs = []
            for label in ('incumbent', 'best_fit'):
                for cx in (m.get(label) or {}).get('counterexamples', []) if isinstance(m.get(label), dict) else []:
                    cxs.append(list(cx['items']))
            mining[h['call']] = cxs
        runs.append({'run_id': d['run_id'], 'arm': d['arm'], 'seed': d['seed'], 'fixed_specs': d['fixed_specs'],
                     'fixed_best_fit_bins': d['fixed_best_fit_bins'], 'fixed_l2': d['fixed_l2'],
                     'proposals': props, 'mining': mining})
    return runs


def groups_of(runs):
    """group key -> {'rep': first proposal in run/call order, 'members': [(run_id, call, code_sha)]}"""
    groups = {}
    for r in runs:
        for p in r['proposals']:
            g = groups.setdefault(p['group'], {'rep': {**p, 'run_id': r['run_id']}, 'members': [], 'codes': {}})
            g['members'].append((r['run_id'], p['call'], p['code_sha']))
            g['codes'].setdefault(p['code_sha'], p['code'])
    return groups


def done_keys(path, key):
    if not path.exists():
        return set()
    return {tuple(json.loads(line)[k] for k in key) if isinstance(key, tuple) else json.loads(line)[key]
            for line in path.read_text().splitlines() if line.strip()}


def append(path, row):
    with open(path, 'a') as f:
        f.write(json.dumps(row) + '\n')


def wait_for_load(workers):
    """Report the load; the caller already caps workers at 2 while load > 6 (protocol)."""
    load = os.getloadavg()[0]
    if load > 6 and workers > 2:
        raise SystemExit(f'load {load:.1f} > 6: use --workers 2 or fewer (protocol)')
    return load


def score_on(code, specs, want_hash=False):
    """Bins per long instance via the integrity gate's online runner, with one retry at 60 s."""
    out = {'bins': [], 'hashes': [], 'errors': [], 'seconds': 0.0}
    started = time.monotonic()
    reason = screen(code)
    with tempfile.TemporaryDirectory(prefix='ogv1_') as tmp:
        path = write_program(tmp, 'program', code)
        for ns, seed, n in specs:
            if reason:
                out['bins'].append(None)
                out['errors'].append('static: ' + reason)
                continue
            items = weibull_items(seed, n, ns)
            res, err = None, None
            for timeout in (TIMEOUT_S, RETRY_TIMEOUT_S):
                try:
                    res = pack_fresh(path, items, timeout)
                    break
                except CandidateError as exc:
                    err = str(exc)[-200:]
            out['bins'].append(res[0] if res else None)
            out['errors'].append(None if res else err)
            if want_hash:
                out['hashes'].append(packing_hash(res[1]) if res else None)
    out['seconds'] = time.monotonic() - started
    return out


def _pool_job(args):
    group, code = args
    specs = [[POOL_NS, s, N_ITEMS] for s in POOL_SEEDS]
    return {'group': group, **score_on(code, specs)}


def _dedup_job(args):
    group, code_sha, code = args
    specs = [[POOL_NS, s, N_ITEMS] for s in POOL_SEEDS[:4]]
    return {'group': group, 'code_sha': code_sha, **score_on(code, specs, want_hash=True)}


def _short_job(args):
    """Bins of one program on many short inputs, through a persistent online packer."""
    group, code, inputs = args
    out = {'group': group, 'bins': [], 'error': None}
    reason = screen(code)
    if reason:
        return {**out, 'error': 'static: ' + reason}
    with tempfile.TemporaryDirectory(prefix='ogv1s_') as tmp:
        packer = PersistentPacker(write_program(tmp, 'program', code))
        try:
            for items in inputs:
                try:
                    out['bins'].append(packer.pack(items, timeout_s=10.0)[0])
                except CandidateError as exc:
                    out['bins'].append(None)
                    out['error'] = str(exc)[-200:]
                    packer = PersistentPacker(write_program(tmp, 'program', code))
        finally:
            packer.close()
    return out


def run_jobs(fn, jobs, workers, sink, label):
    print(f'{label}: {len(jobs)} jobs, {workers} workers, load {os.getloadavg()[0]:.1f}', flush=True)
    t0, k = time.monotonic(), 0
    if workers <= 1:
        it = map(fn, jobs)
        for row in it:
            k += 1
            sink(row)
            print(f'  {k}/{len(jobs)} {time.monotonic() - t0:.0f}s load {os.getloadavg()[0]:.1f}', flush=True)
        return
    with cf.ProcessPoolExecutor(max_workers=workers) as ex:
        for row in ex.map(fn, jobs):
            k += 1
            sink(row)
            print(f'  {k}/{len(jobs)} {time.monotonic() - t0:.0f}s load {os.getloadavg()[0]:.1f}', flush=True)


def cmd_control(a):
    runs = load_runs()
    picks = []
    for r in runs:  # promoted proposals first, then any, until 6 programs from different runs
        for p in r['proposals']:
            if p['promoted'] and len([x for x in picks if x[2]]) < 3 and r['run_id'] not in {x[0] for x in picks}:
                picks.append((r['run_id'], p, True, r['fixed_specs']))
    for r in runs[::7]:
        p = r['proposals'][len(r['proposals']) // 2]
        if len(picks) < 6:
            picks.append((r['run_id'], p, False, r['fixed_specs']))
    rows = []
    for run_id, p, promoted, specs in picks:
        got = score_on(p['code'], specs, want_hash=True)
        ok = got['bins'] == p['fixed_bins'] and got['hashes'] == p['hashes']
        rows.append({'run_id': run_id, 'call': p['call'], 'promoted': promoted, 'saved_bins': p['fixed_bins'],
                     'rescored_bins': got['bins'], 'hashes_match': got['hashes'] == p['hashes'], 'reproduced': ok,
                     'seconds': got['seconds']})
        print(json.dumps(rows[-1]), flush=True)
    (HERE / 'control.json').write_text(json.dumps({'programs': rows, 'all_reproduced': all(r['reproduced'] for r in rows)},
                                                  indent=1))
    print('ALL REPRODUCED' if all(r['reproduced'] for r in rows) else 'MISMATCH: stop and investigate')


def cmd_pool(a):
    wait_for_load(a.workers)
    groups = groups_of(load_runs())
    path = HERE / 'pool_scores.jsonl'
    done = done_keys(path, 'group')
    jobs = [(g, v['rep']['code']) for g, v in groups.items() if g not in done]
    if a.limit:
        jobs = jobs[:a.limit]
    run_jobs(_pool_job, jobs, a.workers, lambda row: append(path, row), 'pool')
    bf = HERE / 'pool_best_fit.json'
    if not bf.exists():
        rows = []
        for s in POOL_SEEDS:
            items = weibull_items(s, N_ITEMS, POOL_NS)
            rows.append({'seed': s, 'best_fit': pack_rule(items, 'best_fit', 100), 'l2': l2_bound(items)})
        bf.write_text(json.dumps(rows, indent=0))


def cmd_dedup(a):
    wait_for_load(a.workers)
    groups = groups_of(load_runs())
    path = HERE / 'dedup_check.jsonl'
    done = done_keys(path, ('group', 'code_sha'))
    multi = [(g, v) for g, v in groups.items() if len(v['codes']) >= 2][:20]
    jobs = []
    for g, v in multi:
        rep_sha = v['rep']['code_sha']
        other = next(s for s in v['codes'] if s != rep_sha)
        for sha in (rep_sha, other):
            if (g, sha) not in done:
                jobs.append((g, sha, v['codes'][sha]))
    run_jobs(_dedup_job, jobs, a.workers, lambda row: append(path, row), 'dedup')


def archive_inputs(run):
    """Distinct counterexample inputs in order of first mining, with the call that mined each."""
    seen, out = set(), []
    for call in sorted(run['mining']):
        for items in run['mining'][call]:
            key = tuple(items)
            if key not in seen:
                seen.add(key)
                out.append({'mined_at': call, 'items': items})
    return out


def random_inputs(run_index, inputs):
    return [weibull_items(run_index * 1000 + k, len(x['items']), RANDOM_NS) for k, x in enumerate(inputs)]


def cmd_archive(a):
    wait_for_load(a.workers)
    runs = load_runs()
    groups = groups_of(runs)
    path = HERE / 'archive_scores.jsonl'
    done = done_keys(path, ('run_id', 'group'))
    meta = []
    jobs = []
    for i, r in enumerate(runs):
        inputs = archive_inputs(r)
        rand = random_inputs(i, inputs)
        bf = [pack_rule(list(x['items']), 'best_fit', 100) for x in inputs]
        bf_r = [pack_rule(list(x), 'best_fit', 100) for x in rand]
        meta.append({'run_id': r['run_id'], 'inputs': inputs, 'random': rand, 'best_fit': bf, 'best_fit_random': bf_r})
        for g in sorted({p['group'] for p in r['proposals']}):
            if (r['run_id'], g) not in done and inputs:
                jobs.append((r['run_id'], g, groups[g]['rep']['code'], [x['items'] for x in inputs] + rand))
    (HERE / 'archive_inputs.json').write_text(json.dumps(meta))

    def fn_wrap(job):
        return job

    def sink(row):
        append(path, row)

    run_jobs(_archive_job, jobs, a.workers, sink, 'archive')


def _archive_job(args):
    run_id, group, code, inputs = args
    out = _short_job((group, code, inputs))
    return {'run_id': run_id, **out}


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    sub = ap.add_subparsers(dest='cmd', required=True)
    sub.add_parser('control')
    for name in ('pool', 'dedup', 'archive'):
        p = sub.add_parser(name)
        p.add_argument('--workers', type=int, default=2)
        p.add_argument('--limit', type=int, default=0, help='score at most this many jobs (pilot)')
    a = ap.parse_args()
    {'control': cmd_control, 'pool': cmd_pool, 'dedup': cmd_dedup, 'archive': cmd_archive}[a.cmd](a)
