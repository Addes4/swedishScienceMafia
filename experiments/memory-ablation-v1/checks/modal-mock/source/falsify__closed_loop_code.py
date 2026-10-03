"""Closed-loop memory study in the code regime: priority(item, bins) on 5,000-item Weibull streams.

claude-haiku-4-5 writes one complete priority(item, bins) program per call. The harness
evaluates it in the sandbox (falsify/code_eval.py, on Modal or locally), promotes it if it
uses strictly fewer bins than the incumbent on the run's fixed suite, and writes the next
prompt with no human edits. The three arms (none / prose / executable) differ only in the
memory section (falsify/memory_code.py). Seeds fix harness randomness (fixed suite, probe
streams), not model sampling.

    python -m falsify.closed_loop_code run --out DIR --seeds 0 1 --cap-usd 8 --modal
    python -m falsify.closed_loop_code audit --out DIR --modal
    python -m falsify.closed_loop_code run --out /tmp/x --seeds 1 --calls 3 --cap-usd 1 --mock   # offline
"""
import argparse
import hashlib
import json
import shutil
import sys
import time
import traceback
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from . import code_eval
from .closed_loop import audit_seeds, bootstrap, harness_seed, mean
from .core import read_json, write_json
from .funsearch_heuristics import SOURCE as FUNSEARCH_SOURCE
from .llm import BudgetExceeded, MockClient, Proposer, SpendLedger, prior_spend
from .longpack import l2_bound, weibull_items
from .memory import ARMS, TokenFitter
from .memory_code import memory_section

ROOT = Path(__file__).resolve().parents[1]
NAMESPACE = 'memory-ablation-v1'
BEST_FIT_CODE = 'import numpy as np\n\n\ndef priority(item, bins):\n    return -(bins - item)\n'
FUNSEARCH_PATH = ROOT / 'experiments' / 'bp-ceiling-v1' / 'programs' / 'funsearch_weibull.py'
DEFAULTS = {'calls': 30, 'model': 'claude-haiku-4-5', 'max_tokens': 2048, 'fixed_instances': 5, 'items': 5000,
            'window': 40, 'windows': 50, 'failure_candidates': 4, 'shrink_trials': 300,
            'max_counterexample_items': 30, 'counterexamples': 2, 'mining_seconds': 120, 'timeout_s': 30,
            'memory_token_budget': 1500, 'max_counterexamples': 8, 'max_prompt_chars': 30000,
            'audit_instances': 400, 'audit_shard': 20, 'diagnostic_instances': 10,
            'bootstrap_resamples': 10000, 'bootstrap_seed': 49999}
PROMOTION_RULE = ('score-only: promote iff the proposal uses strictly fewer total bins than the incumbent '
                  'on the run\'s fixed suite (5 Weibull instances of 5,000 items)')
NO_OP_SENTENCE = ('A proposal that packs every fixed-suite instance exactly like the incumbent cannot be '
                  'promoted and uses up a call.')

SYSTEM_PROMPT = """You are researching online bin-packing heuristics.

Items arrive one at a time and must be placed immediately, without seeing later items, into bins
of capacity 100. Use as few bins as possible.

You write a Python function priority(item, bins). It is called once per arriving item:
- item is the integer size of the item, 1 to 100.
- bins is a numpy int64 array with the remaining capacity of every bin the item fits in. There
  are as many bins as items in the instance; unused bins have remaining capacity 100 and are
  included. Bins appear in a fixed order (bin index), and the array is a copy.
- Return a numpy array (or list) of the same length with one score per bin (no NaN). The item
  goes into the bin with the highest score; ties go to the first such bin.

The harness owns the bins and enforces capacity; your function only ranks the bins it is shown.
It may keep state between calls within an instance (state is reset between instances), but it
never sees future items.

Instances have 5,000 items with integer sizes drawn independently from one fixed distribution:
Weibull with scale 45 and shape 3, truncated to integers and clipped to 1..100 (mean about 40).

Best-fit, `return -(bins - item)`, puts each item into the feasible bin it fills most tightly.
It is the starting incumbent and a strong baseline.

Rules: use only the standard library and numpy. Do not read or write files, start processes,
use the network, or use eval, exec, compile, importlib or ctypes; such programs are rejected.
Each 5,000-item instance must finish within 30 seconds (about 6 ms per call), so vectorise with
numpy rather than looping over bins in Python.

Reply with one proposal: a short snake_case name, a one- or two-sentence hypothesis, what result
would falsify it, and the complete Python source of a module defining priority(item, bins)."""

SCHEMA = {'type': 'object', 'additionalProperties': False,
          'required': ['name', 'hypothesis', 'falsification', 'code'],
          'properties': {'name': {'type': 'string'}, 'hypothesis': {'type': 'string'},
                         'falsification': {'type': 'string'}, 'code': {'type': 'string'}}}


class LocalExecutor:
    """Runs evaluations in this machine's processes (tests, mock runs, small checks)."""

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def assess(self, payload, tag=''):
        return code_eval.assess(payload)

    def shards(self, payloads, batch=100, tag=''):
        with ThreadPoolExecutor(max_workers=2) as pool:
            return list(pool.map(code_eval.pack_shard, payloads))

    def close_phase(self, label):
        pass


def fixed_specs(seed, cfg):
    return [[f'{NAMESPACE}/fixed', harness_seed(seed, 'fixed', i), cfg['items']] for i in range(cfg['fixed_instances'])]


def code_sha(code):
    return hashlib.sha256((code or '').encode()).hexdigest()[:16]


def user_prompt(incumbent, call, cfg, bf_mean, l2_mean, memory_text):
    inc_mean = mean(incumbent['bins'])
    origin = ('the starting policy' if incumbent['call'] is None
              else f'promoted from proposal {incumbent["call"] + 1}')
    per = ', '.join(f'{b - r:+d}' for b, r in zip(incumbent['bins'], incumbent['best_fit_bins']))
    memory = f'\n{memory_text}' if memory_text else ''
    return (f'## Current incumbent\n'
            f'Name: {incumbent["name"]} ({origin})\n'
            f'```python\n{incumbent["code"].rstrip()}\n```\n'
            f'Fixed search suite ({cfg["fixed_instances"]} instances of {cfg["items"]:,} items, the same at every '
            f'call): the incumbent uses {inc_mean:.1f} bins per instance; best-fit uses {bf_mean:.1f}; the lower '
            f'bound (L2) is {l2_mean:.1f}. Incumbent versus best-fit per instance: {per}.\n\n'
            f'## This call\n'
            f'Call {call + 1} of {cfg["calls"]}. Your proposal is evaluated on the fixed suite and replaces the '
            f'incumbent only if it uses fewer bins in total than the incumbent there. {NO_OP_SENTENCE} The final '
            f'incumbent is then tested on fresh held-out instances from the same distribution.\n'
            f'{memory}\n'
            f'Propose one policy.')


def run_one(seed, arm, proposer, executor, cfg, trace_path):
    run_id = f'{arm}-s{seed}'
    started = time.time()
    specs = fixed_specs(seed, cfg)
    fixed_items = [weibull_items(s, n, ns) for ns, s, n in specs]
    bf_runs = [code_eval.best_fit(items, True) for items in fixed_items]
    bf_bins = [b for b, _ in bf_runs]
    l2s = [l2_bound(items) for items in fixed_items]
    incumbent = {'name': 'best_fit', 'code': BEST_FIT_CODE, 'call': None, 'bins': bf_bins,
                 'best_fit_bins': bf_bins, 'hashes': [code_eval.packing_hash(a) for _, a in bf_runs],
                 'is_best_fit': True}
    former_incumbents = {}  # packing hashes of earlier incumbents -> call (None = best-fit)
    incumbent_rec, history, failed_hashes = None, [], {}
    fitter = TokenFitter(proposer.count_tokens, cfg['memory_token_budget'])
    stopped = None
    for call in range(cfg['calls']):
        tag = f'{run_id}/c{call}'
        mem = memory_section(arm, history, incumbent_rec, fitter, cfg['windows'], cfg['window'],
                             cfg['max_counterexamples'], tag + '/memory')
        user = user_prompt(incumbent, call, cfg, mean(bf_bins), mean(l2s), mem['text'])
        if len(SYSTEM_PROMPT) + len(user) > cfg['max_prompt_chars']:
            raise ValueError(f'{tag}: prompt exceeds {cfg["max_prompt_chars"]} characters')
        rec = {'call': call, 'user_prompt': user, 'memory': {k: v for k, v in mem.items() if k != 'text'},
               'incumbent_before': incumbent['name'], 'incumbent_before_call': incumbent['call'], 'promoted': False}
        try:
            reply = proposer.propose(SYSTEM_PROMPT, user, SCHEMA, tag)
        except BudgetExceeded as exc:
            stopped = f'budget: {exc}'
            break
        rec.update({'response_text': reply['text'], 'attempts': reply['attempts'],
                    'input_tokens': reply.get('input_tokens', 0), 'output_tokens': reply.get('output_tokens', 0),
                    'cost_usd': sum(a['charged_usd'] for a in reply['attempts'])})
        status = reply['status']
        if status == 'ok':
            try:
                obj = json.loads(reply['text'])
                rec.update({'name': str(obj['name'])[:80], 'hypothesis': str(obj['hypothesis']),
                            'falsification': str(obj['falsification']), 'code': str(obj['code'])})
            except (ValueError, KeyError, TypeError) as exc:
                status, rec['invalid_reason'] = 'invalid', str(exc)[:200]
        if status == 'ok':
            payload = {'code': rec['code'], 'incumbent_code': None if incumbent['is_best_fit'] else incumbent['code'],
                       'fixed': specs, 'probe': [f'{NAMESPACE}/probe', harness_seed(seed, 'probe', call),
                                                 cfg['window'] * cfg['windows']], 'cfg': cfg}
            try:
                result = executor.assess(payload, tag)
            except Exception as exc:  # noqa: BLE001 - e.g. Modal budget refusal
                stopped = f'evaluator: {exc}'
                rec['status'] = 'not_evaluated'
                history.append(rec)
                break
            status = result['status']
            rec['evaluation'] = {k: v for k, v in result.items() if k != 'mining'}
            if status == 'infrastructure_error':
                stopped = f'evaluator infrastructure: {result.get("error")}'
            elif status in ('static', 'error'):
                rec['error'] = result.get('error')
        rec['status'] = status
        if status == 'ok':
            bins = result['fixed_bins']
            gaps_inc = [a - b for a, b in zip(bins, incumbent['bins'])]
            rec['fixed'] = {'bins': bins, 'total_bins': sum(bins), 'instances': len(bins),
                            'mean_vs_incumbent': mean(gaps_inc),
                            'mean_vs_best_fit': mean(a - b for a, b in zip(bins, bf_bins)),
                            'losses_vs_incumbent': sum(g > 0 for g in gaps_inc),
                            'wins_vs_incumbent': sum(g < 0 for g in gaps_inc)}
            rec['mining'] = result['mining']
            hashes = tuple(result['fixed_hashes'])
            rec['no_op'] = list(hashes) == list(incumbent['hashes'])
            rec['repeat_of_failed_call'] = failed_hashes.get(hashes)
            rec['reverts_to_former_incumbent'] = (hashes in former_incumbents and not rec['no_op'])
            if sum(bins) < sum(incumbent['bins']):
                rec['promoted'] = True
                former_incumbents[tuple(incumbent['hashes'])] = incumbent['call']
                incumbent = {'name': rec['name'], 'code': rec['code'], 'call': call, 'bins': bins,
                             'best_fit_bins': bf_bins, 'hashes': list(hashes), 'is_best_fit': False}
                incumbent_rec = rec
            else:
                failed_hashes.setdefault(hashes, call)
        history.append(rec)
        if stopped:
            break
    trace = {'run_id': run_id, 'seed': seed, 'arm': arm, 'regime': 'weibull5k_code', 'config': cfg,
             'promotion_rule': PROMOTION_RULE, 'system_prompt': SYSTEM_PROMPT,
             'system_prompt_sha256': hashlib.sha256(SYSTEM_PROMPT.encode()).hexdigest(), 'schema': SCHEMA,
             'fixed_specs': specs, 'fixed_best_fit_bins': bf_bins, 'fixed_l2': l2s,
             'calls_completed': len(history), 'stopped': stopped,
             'complete': stopped is None and len(history) == cfg['calls'],
             'final': {'name': incumbent['name'], 'code': incumbent['code'], 'call': incumbent['call'],
                       'bins': incumbent['bins'], 'is_best_fit': incumbent['is_best_fit']},
             'history': history, 'seconds': time.time() - started}
    write_json(trace_path, trace)
    return trace


def snapshot_sources(out):
    source = out / 'source'
    source.mkdir(parents=True, exist_ok=True)
    files = [p for p in (ROOT / 'falsify').iterdir() if p.suffix in ('.py', '.cpp')]
    files += [ROOT / 'autoresearch' / n for n in ('claude.py', 'gate.py', 'sandbox.py')]
    files += [ROOT / 'problems' / 'bin_packing_online' / 'verify.py']
    hashes = {}
    for p in sorted(files):
        name = f'{p.parent.name}__{p.name}'
        shutil.copyfile(p, source / name)
        hashes[name] = hashlib.sha256(p.read_bytes()).hexdigest()
    return hashes


def make_executor(args, out):
    if not args.modal:
        return LocalExecutor()
    from .memory_ablation_modal import ModalExecutor, ModalLedger, prior_modal_spend
    prior = prior_modal_spend(sorted(Path(args.ledger_root).rglob('modal_usage.jsonl')))
    return ModalExecutor(ModalLedger(out / 'modal_usage.jsonl', args.modal_cap_usd, prior))


def cmd_run(args):
    out = Path(args.out)
    cfg = {**DEFAULTS, 'calls': args.calls, 'model': args.model}
    for key in ('items', 'fixed_instances', 'windows', 'audit_instances', 'diagnostic_instances'):
        if getattr(args, key) is not None:
            cfg[key] = getattr(args, key)
    config = {'regime': 'weibull5k_code', 'arms': args.arms, 'seeds': args.seeds, 'loop': cfg,
              'promotion_rule': PROMOTION_RULE, 'mock': args.mock, 'modal': args.modal, 'workers': args.workers,
              'cap_usd': args.cap_usd, 'total_cap_usd': args.total_cap_usd, 'modal_cap_usd': args.modal_cap_usd}
    if (out / 'config.json').exists():
        old = read_json(out / 'config.json')
        if {k: old[k] for k in ('regime', 'loop', 'mock')} != {k: config[k] for k in ('regime', 'loop', 'mock')}:
            raise SystemExit('config.json in this directory differs; use a fresh --out')
        config['seeds'] = sorted(set(old['seeds']) | set(args.seeds))
        config['arms'] = [a for a in ARMS if a in set(old['arms']) | set(args.arms)]
        config['invocations'] = old.get('invocations', [])
    out.mkdir(parents=True, exist_ok=True)
    config.setdefault('invocations', []).append({'time': time.time(), 'argv': sys.argv[1:],
                                                 'source_sha256': snapshot_sources(out)})
    write_json(out / 'config.json', config)
    if args.mock:
        client, prior = MockClient(seed=args.mock_seed), 0.0
    else:
        from autoresearch.env import load_env, require
        load_env()
        require('ANTHROPIC_API_KEY', 'live proposal calls')
        client, prior = None, prior_spend(sorted(Path(args.ledger_root).rglob('usage.jsonl')))
    ledger = SpendLedger(out / 'usage.jsonl', args.cap_usd, prior_usd=prior, total_cap_usd=args.total_cap_usd,
                         client_label='mock' if args.mock else 'anthropic')
    proposer = Proposer(ledger, model=args.model, max_tokens=cfg['max_tokens'], client=client)
    jobs = [(s, a, out / 'runs' / f'{a}-s{s}.json.gz') for s in args.seeds for a in args.arms]
    jobs = [j for j in jobs if not j[2].exists()]
    print(f'{len(jobs)} runs; earlier Anthropic spend ${prior:.4f}; cap ${args.cap_usd:.2f} '
          f'(total ${args.total_cap_usd:.2f})', flush=True)
    with make_executor(args, out) as executor:
        def work(job):
            seed, arm, path = job
            try:
                t = run_one(seed, arm, proposer, executor, cfg, path)
            except Exception:  # noqa: BLE001
                traceback.print_exc()
                return f'{arm}-s{seed}: crashed'
            promos = sum(r['promoted'] for r in t['history'])
            return (f'{t["run_id"]}: calls={t["calls_completed"]} promotions={promos} final={t["final"]["name"]} '
                    f'vs_best_fit={mean(a - b for a, b in zip(t["final"]["bins"], t["fixed_best_fit_bins"])):+.1f} '
                    f'stopped={t["stopped"]}')

        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            for line in pool.map(work, jobs):
                print(line, f'anthropic=${ledger.spent:.4f}', flush=True)
    print(f'done; Anthropic charged ${ledger.spent:.4f} in this invocation', flush=True)


def excess_percent(bins, l2):
    return 100.0 * (sum(bins) - sum(l2)) / sum(l2)


def cmd_audit(args):
    out = Path(args.out)
    if (out / 'summary.json').exists() and not args.force:
        raise SystemExit('Audit already done (summary.json exists)')
    config = read_json(out / 'config.json')
    cfg = config['loop']
    if set(config['arms']) != set(ARMS):
        raise SystemExit(f'Audit refused: the design has three arms, runs exist for {config["arms"]}')
    if args.expect_seeds and sorted(args.expect_seeds) != sorted(config['seeds']):
        raise SystemExit(f'Audit refused: expected seeds {args.expect_seeds}, config has {config["seeds"]}')
    paths = [out / 'runs' / f'{a}-s{s}.json.gz' for s in config['seeds'] for a in config['arms']]
    missing = [p.name for p in paths if not p.exists()]
    if missing:
        raise SystemExit(f'Runs missing, audit refused: {missing}')
    traces = {(t['seed'], t['arm']): t for t in (read_json(p) for p in paths)}
    audit_seed, diagnostic_seed, digest = audit_seeds(paths)
    audit_specs = [[f'{NAMESPACE}/audit', audit_seed + i, cfg['items']] for i in range(cfg['audit_instances'])]
    diag_specs = [[f'{NAMESPACE}/diagnostic', diagnostic_seed + i, cfg['items']]
                  for i in range(cfg['diagnostic_instances'])]
    funsearch_code = FUNSEARCH_PATH.read_text()
    finals = {}
    for t in traces.values():
        code = None if t['final']['is_best_fit'] else t['final']['code']
        finals[code_sha(code)] = code
    finals[code_sha(funsearch_code)] = funsearch_code
    proposals = {}
    for t in traces.values():
        for r in t['history']:
            if r['status'] == 'ok':
                proposals[code_sha(r['code'])] = r['code']
    k = cfg['audit_shard']
    audit_payloads, audit_keys = [], []
    for sha, code in finals.items():
        for start in range(0, len(audit_specs), k):
            audit_payloads.append({'code': code, 'instances': audit_specs[start:start + k], 'timeout_s': cfg['timeout_s']})
            audit_keys.append(sha)
    diag_keys = list(proposals)
    diag_payloads = [{'code': proposals[sha], 'instances': diag_specs, 'timeout_s': cfg['timeout_s']} for sha in diag_keys]
    diag_payloads.append({'code': None, 'instances': diag_specs, 'timeout_s': cfg['timeout_s']})
    started = time.time()
    with make_executor(args, out) as executor:
        audit_results = executor.shards(audit_payloads, tag='audit')
        executor.close_phase('audit')
        diag_results = executor.shards(diag_payloads, tag='diagnostic')
    audit_bins = {}
    for sha, res in zip(audit_keys, audit_results):
        audit_bins.setdefault(sha, {'bins': [], 'best_fit': [], 'l2': [], 'errors': []})
        a = audit_bins[sha]
        a['bins'] += res.get('bins') or [None] * k
        a['best_fit'] += res.get('best_fit') or [None] * k
        a['l2'] += res.get('l2') or [None] * k
        if res.get('error'):
            a['errors'].append(res['error'])
    ref = next(iter(audit_bins.values()))
    bf_audit, l2_audit = ref['best_fit'], ref['l2']
    if None in bf_audit:
        raise SystemExit('Audit shards failed; see modal_usage.jsonl')

    def policy_row(sha):
        a = audit_bins[sha]
        if a['errors'] or None in a['bins']:
            return {'mean_excess_vs_best_fit': None, 'errors': a['errors'][:3]}
        gaps = [x - y for x, y in zip(a['bins'], bf_audit)]
        return {'mean_excess_vs_best_fit': mean(gaps), 'mean_bins': mean(a['bins']),
                'excess_percent_over_l2': excess_percent(a['bins'], l2_audit),
                'delta_pp_vs_best_fit': excess_percent(a['bins'], l2_audit) - excess_percent(bf_audit, l2_audit),
                'wins': sum(g < 0 for g in gaps), 'ties': sum(g == 0 for g in gaps), 'losses': sum(g > 0 for g in gaps),
                'instance_bootstrap_95': bootstrap(gaps, cfg['bootstrap_resamples'], cfg['bootstrap_seed'])}

    policy_rows = {sha: policy_row(sha) for sha in audit_bins}
    diag = {sha: res for sha, res in zip(diag_keys + ['best_fit'], diag_results)}
    bf_diag = mean(diag['best_fit']['bins'])

    def diag_mean(code):
        res = diag[code_sha(code)] if code else diag['best_fit']
        return None if res.get('error') or None in (res.get('bins') or [None]) else mean(res['bins'])

    per_run = {}
    for (seed, arm), t in sorted(traces.items()):
        hist = t['history']
        valid = [r for r in hist if r['status'] == 'ok']
        labels, worse_than_inc = [], 0
        inc_code_at = {}
        current = None
        for r in hist:
            inc_code_at[r['call']] = current
            if r.get('promoted'):
                current = r['code']
        for r in valid:
            d = diag_mean(r['code'])
            labels.append('error' if d is None else 'worse' if d > bf_diag else 'better' if d < bf_diag else 'tied')
            inc_d = diag_mean(inc_code_at[r['call']])
            if d is not None and inc_d is not None and d > inc_d:
                worse_than_inc += 1
        final_sha = code_sha(None if t['final']['is_best_fit'] else t['final']['code'])
        row = policy_rows[final_sha]
        n_valid = len(valid)
        metrics = {
            'final_audit_excess': row['mean_excess_vs_best_fit'],
            'final_delta_pp_vs_best_fit': row.get('delta_pp_vs_best_fit'),
            'final_is_best_fit': t['final']['is_best_fit'], 'promotions': sum(r.get('promoted', False) for r in hist),
            'calls': len(hist), 'valid_proposals': n_valid,
            'static_rejections': sum(r['status'] == 'static' for r in hist),
            'runtime_errors': sum(r['status'] == 'error' for r in hist),
            'other_failed_calls': sum(r['status'] not in ('ok', 'static', 'error') for r in hist),
            'harmful_fraction': labels.count('worse') / n_valid if n_valid else None,
            'beneficial_fraction': labels.count('better') / n_valid if n_valid else None,
            'worse_than_incumbent_fraction': worse_than_inc / n_valid if n_valid else None,
            'no_op_fraction': sum(bool(r.get('no_op')) for r in valid) / n_valid if n_valid else None,
            'repeated_failed': sum(r.get('repeat_of_failed_call') is not None for r in valid),
            'reverts_to_former_incumbent': sum(bool(r.get('reverts_to_former_incumbent')) for r in valid),
            'best_fixed_vs_best_fit': min((r['fixed']['mean_vs_best_fit'] for r in valid), default=None),
            'memory_tokens_mean': mean(r['memory']['tokens'] for r in hist) if hist else 0,
            'memory_counterexamples_mean': mean(r['memory']['counterexamples'] for r in hist) if hist else 0,
            'input_tokens': sum(r.get('input_tokens', 0) for r in hist),
            'output_tokens': sum(r.get('output_tokens', 0) for r in hist),
            'cost_usd': sum(r.get('cost_usd', 0.0) for r in hist),
            # When the incumbent of the time was best-fit, both references are the same mining pass.
            'shrink_trials': sum(m['trials'] for r in valid for w, m in r['mining'].items()
                                 if w == 'incumbent' or r['incumbent_before'] != 'best_fit'),
            'short_stream_executions': sum(r['evaluation'].get('short_executions', 0) for r in valid),
            'evaluation_seconds': sum(r['evaluation'].get('seconds', 0) for r in hist if 'evaluation' in r)}
        per_run[f'{arm}-s{seed}'] = {'seed': seed, 'arm': arm, 'complete': t['complete'], 'metrics': metrics,
                                    'final_code_sha': final_sha, 'labels': labels}
    keys = [k for k in next(iter(per_run.values()))['metrics'] if k != 'final_is_best_fit']
    arms = {}
    for arm in config['arms']:
        rows = [v['metrics'] for v in per_run.values() if v['arm'] == arm]
        arms[arm] = {k: (mean(r[k] for r in rows if r[k] is not None) if any(r[k] is not None for r in rows) else None)
                     for k in keys}
        arms[arm]['runs'] = len(rows)
        arms[arm]['final_is_best_fit'] = sum(r['final_is_best_fit'] for r in rows)
    comparisons = []
    for a, b in [('executable', 'prose'), ('executable', 'none'), ('prose', 'none')]:
        if a not in config['arms'] or b not in config['arms']:
            continue
        for metric in ['final_audit_excess', 'harmful_fraction', 'worse_than_incumbent_fraction', 'no_op_fraction',
                       'repeated_failed', 'reverts_to_former_incumbent', 'best_fixed_vs_best_fit']:
            diffs = []
            for s in config['seeds']:
                x, y = per_run[f'{a}-s{s}']['metrics'][metric], per_run[f'{b}-s{s}']['metrics'][metric]
                if x is not None and y is not None:
                    diffs.append(x - y)
            if diffs:
                comparisons.append({'comparison': f'{a} - {b}', 'metric': metric, 'mean': mean(diffs), 'n': len(diffs),
                                    'bootstrap_95': bootstrap(diffs, cfg['bootstrap_resamples'], cfg['bootstrap_seed']),
                                    'paired_seed_differences': diffs})
    usage = [json.loads(l) for l in (out / 'usage.jsonl').read_text().splitlines() if l.strip()]
    modal_path = out / 'modal_usage.jsonl'
    modal_usage = [json.loads(l) for l in modal_path.read_text().splitlines() if l.strip()] if modal_path.exists() else []
    summary = {'regime': 'weibull5k_code', 'seeds': config['seeds'], 'arms': arms, 'comparisons': comparisons,
               'references': {'funsearch_weibull': policy_rows[code_sha(funsearch_code)],
                              'funsearch_source': FUNSEARCH_SOURCE,
                              'best_fit_mean_bins': mean(bf_audit), 'best_fit_excess_percent_over_l2':
                                  excess_percent(bf_audit, l2_audit)},
               'incomplete_runs': [k for k, v in per_run.items() if not v['complete']],
               'audit_seed': audit_seed, 'diagnostic_seed': diagnostic_seed, 'trace_digest': digest,
               'audit_instances': len(audit_specs), 'diagnostic_instances': len(diag_specs),
               'distinct_final_policies': len(finals) - 1, 'distinct_valid_proposals': len(proposals),
               'audit_source_sha256': {f'falsify__{p.name}': hashlib.sha256(p.read_bytes()).hexdigest()
                                       for p in sorted((ROOT / 'falsify').glob('*.py'))},
               'audit_wall_seconds': time.time() - started,
               'usage': {'anthropic_charged_usd': sum(u.get('charged_usd', 0.0) for u in usage),
                         'message_attempts': sum(u['kind'] == 'messages' for u in usage),
                         'message_failures': sum(u['kind'] == 'messages' and u['status'] != 'ok' for u in usage),
                         'count_tokens_calls': sum(u['kind'] == 'count_tokens' for u in usage),
                         'modal_estimated_usd': sum(u.get('estimated_usd', 0.0) for u in modal_usage)}}
    write_json(out / 'audit.json', {'per_run': per_run, 'policies': policy_rows,
                                    'diagnostic_mean_bins': {k: (mean(v['bins']) if not v.get('error') and None not in (v.get('bins') or [None]) else None)
                                                             for k, v in diag.items()},
                                    'diagnostic_best_fit_mean_bins': bf_diag,
                                    'audit_best_fit_bins': bf_audit, 'audit_l2': l2_audit,
                                    'audit_bins': {k: v['bins'] for k, v in audit_bins.items()}})
    write_json(out / 'summary.json', summary)
    print(json.dumps({a: {k: arms[a][k] for k in ('final_audit_excess', 'harmful_fraction', 'no_op_fraction',
                                                   'promotions', 'memory_tokens_mean', 'cost_usd')} for a in arms},
                     indent=1))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest='cmd', required=True)
    run = sub.add_parser('run', help='run closed-loop searches (one per seed and arm)')
    run.add_argument('--out', required=True)
    run.add_argument('--seeds', type=int, nargs='+', required=True)
    run.add_argument('--arms', nargs='+', default=list(ARMS), choices=ARMS)
    run.add_argument('--calls', type=int, default=DEFAULTS['calls'])
    run.add_argument('--model', default=DEFAULTS['model'])
    run.add_argument('--workers', type=int, default=15, help='runs in parallel (API calls are I/O bound)')
    run.add_argument('--cap-usd', type=float, required=True, help='Anthropic cap for this invocation')
    run.add_argument('--total-cap-usd', type=float, default=15.0, help='Anthropic cap including earlier usage')
    run.add_argument('--modal-cap-usd', type=float, default=5.0, help='Modal cap including earlier usage')
    run.add_argument('--ledger-root', default='experiments/memory-ablation-v1')
    run.add_argument('--modal', action='store_true', help='evaluate on Modal (app ssm-memory-ablation)')
    run.add_argument('--mock', action='store_true', help='offline mock model; no API calls')
    run.add_argument('--mock-seed', type=int, default=0)
    small = run.add_argument_group('size overrides (smoke tests only; the study uses the defaults)')
    small.add_argument('--items', type=int)
    small.add_argument('--fixed-instances', type=int)
    small.add_argument('--windows', type=int)
    small.add_argument('--audit-instances', type=int)
    small.add_argument('--diagnostic-instances', type=int)
    audit = sub.add_parser('audit', help='fresh audit and diagnostic suites after all runs end')
    audit.add_argument('--out', required=True)
    audit.add_argument('--modal', action='store_true')
    audit.add_argument('--modal-cap-usd', type=float, default=5.0)
    audit.add_argument('--ledger-root', default='experiments/memory-ablation-v1')
    audit.add_argument('--force', action='store_true', help='redo an audit (it is a pure function of the traces)')
    audit.add_argument('--expect-seeds', type=int, nargs='+', help='refuse unless exactly these seeds were run')
    args = parser.parse_args(argv)
    cmd_run(args) if args.cmd == 'run' else cmd_audit(args)


if __name__ == '__main__':
    main()
