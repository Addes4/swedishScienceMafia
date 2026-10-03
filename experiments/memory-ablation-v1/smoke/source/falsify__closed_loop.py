"""Closed-loop LLM search with three memory arms (none / prose / executable).

One model call per step proposes one policy; the harness evaluates it, decides promotion
and writes the next prompt with no human in the loop. Arms share the model, call count,
max tokens, evaluator rule and promotion rule; only the memory section differs
(falsify/memory.py). Seeds fix harness randomness (fixed suite, probes, gate samples),
not model sampling.

    python -m falsify.closed_loop run --out DIR --seeds 100 101 --cap-usd 3
    python -m falsify.closed_loop audit --out DIR
"""
import argparse
import hashlib
import json
import random
import shutil
import statistics
import sys
import time
import traceback
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from .backends import bins_from_assignments, first_divergence, get_backend, shrink_failure
from .core import identity, read_json, write_json
from .llm import BudgetExceeded, MockClient, Proposer, SpendLedger, prior_spend
from .memory import ARMS, TokenFitter, memory_section
from .soft_gates import gate_decision

ROOT = Path(__file__).resolve().parents[1]
DEFAULTS = {'calls': 30, 'model': 'claude-haiku-4-5', 'max_tokens': 1024, 'fixed_cases': 400,
            'probe_cases': 100, 'failure_candidates': 4, 'counterexamples_per_proposal': 2, 'memory_token_budget': 1500,
            'max_counterexamples': 8, 'archive_size': 64, 'archive_initial': 16, 'gate_sample': 16,
            'max_prompt_chars': 16000, 'audit_cases': 1600, 'diagnostic_cases': 800,
            'bootstrap_resamples': 10000, 'bootstrap_seed': 49999}
PROMOTION_RULE = ('score-only: promote iff the proposal uses strictly fewer total bins than the '
                  'incumbent on the fixed suite; a strict counterexample gate is computed in shadow '
                  'and never affects promotion')


def harness_seed(seed, stream, index=0):
    """Deterministic integer seeds per run seed; identical across arms (paired design)."""
    return int(hashlib.sha256(f'memory-ablation-v1|{seed}|{stream}|{index}'.encode()).hexdigest()[:12], 16)


def mean(xs):
    xs = list(xs)
    return sum(xs) / len(xs)


def fixed_summary(backend, cases, bins, refs):
    gaps = [a - b for a, b in zip(bins, refs)]
    fams = {}
    for c, g in zip(cases, gaps):
        fams.setdefault(backend.family(c), []).append(g)
    return {'mean_excess': mean(gaps), 'total_bins': sum(bins), 'wins': sum(g < 0 for g in gaps),
            'losses': sum(g > 0 for g in gaps), 'ties': sum(g == 0 for g in gaps),
            'by_family': {f: mean(v) for f, v in fams.items()}}


def signature(bins):
    return hashlib.sha256(json.dumps(bins).encode()).hexdigest()[:16]


def counterexample(backend, policy, case, gap, budget):
    items, work = shrink_failure(backend, backend.items(case), policy, budget)
    cb, ca = backend.pack(policy, items, True)
    rb, ra = backend.pack(backend.baseline, items, True)
    return {'family': backend.family(case), 'original_length': len(backend.items(case)),
            'original_gap': gap, 'items': items, 'candidate_bins': cb, 'reference_bins': rb,
            'candidate_packing': bins_from_assignments(items, ca),
            'reference_packing': bins_from_assignments(items, ra),
            'divergence': first_divergence(items, ca, ra), 'shrink_executions': work}


def user_prompt(backend, incumbent, call, cfg, memory_text):
    f = incumbent['fixed']
    fams = ', '.join(f'{k} {v:+.4f}' for k, v in f['by_family'].items())
    origin = ('the starting policy' if incumbent['call'] is None
              else f'promoted from proposal {incumbent["call"] + 1}')
    memory = f'\n{memory_text}' if memory_text else ''
    return (f'## Current incumbent\n'
            f'Name: {incumbent["name"]} ({origin})\n'
            f'Weights: {backend.render(incumbent["policy"])}\n'
            f'Fixed search suite ({cfg["fixed_cases"]} instances, the same at every call): '
            f'{f["mean_excess"]:+.4f} bins per instance versus best-fit; {f["wins"]} wins, {f["ties"]} ties, '
            f'{f["losses"]} losses. By family: {fams}.\n\n'
            f'## This call\n'
            f'Call {call + 1} of {cfg["calls"]}. Your proposal is evaluated on the fixed suite and replaces the '
            f'incumbent only if it uses fewer bins in total than the incumbent there. The final incumbent is '
            f'then tested on fresh held-out instances.\n'
            f'{memory}\n'
            f'Propose one policy.')


def run_one(seed, arm, backend, proposer, cfg, trace_path):
    run_id = f'{arm}-s{seed}'
    started = time.time()
    system = backend.system_prompt()
    schema = backend.proposal_schema()
    fixed = backend.cases(harness_seed(seed, 'fixed'), cfg['fixed_cases'], 'train')
    fixed_refs = backend.evaluate(backend.baseline, fixed)
    executions = 2 * len(fixed)
    initial = backend.cases(harness_seed(seed, 'archive'), cfg['archive_initial'], 'train')
    archive = [{'case': c, 'reference_bins': r, 'gap': 0, 'generation': -1, 'id': identity(backend.items(c))}
               for c, r in zip(initial, backend.evaluate(backend.baseline, initial))]
    executions += len(initial)
    base_bins = list(fixed_refs)
    incumbent = {'name': backend.baseline_name, 'policy': backend.baseline, 'call': None,
                 'fixed': fixed_summary(backend, fixed, base_bins, fixed_refs), 'signature': signature(base_bins),
                 'bins': base_bins}
    incumbent_rec = None
    history, failed_signatures = [], {}
    fitter = TokenFitter(proposer.count_tokens, cfg['memory_token_budget'])
    stopped = None
    for call in range(cfg['calls']):
        tag = f'{run_id}/c{call}'
        mem = memory_section(arm, history, incumbent_rec, backend.render, fitter, cfg['fixed_cases'],
                             cfg['probe_cases'], cfg['max_counterexamples'], tag + '/memory')
        user = user_prompt(backend, incumbent, call, cfg, mem['text'])
        if len(system) + len(user) > cfg['max_prompt_chars']:
            raise ValueError(f'{tag}: prompt exceeds {cfg["max_prompt_chars"]} characters')
        rec = {'call': call, 'user_prompt': user, 'memory': {k: v for k, v in mem.items() if k != 'text'},
               'incumbent_before': incumbent['name'], 'promoted': False, 'counterexamples': []}
        try:
            reply = proposer.propose(system, user, schema, tag)
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
                policy = backend.parse(obj)
                rec.update({'name': str(obj['name'])[:80], 'hypothesis': str(obj['hypothesis']),
                            'falsification': str(obj['falsification']), 'policy': policy})
            except (ValueError, KeyError, TypeError) as exc:
                status, rec['invalid_reason'] = 'invalid', str(exc)[:200]
        rec['status'] = status
        if status == 'ok':
            bins = backend.evaluate(policy, fixed)
            probes = backend.cases(harness_seed(seed, 'probe', call), cfg['probe_cases'], 'train')
            probe_bins = backend.evaluate(policy, probes)
            probe_refs = backend.evaluate(backend.baseline, probes)
            executions += len(fixed) + 2 * len(probes)
            probe_gaps = [a - b for a, b in zip(probe_bins, probe_refs)]
            order = sorted(range(len(probes)), key=lambda i: (-probe_gaps[i], i))
            shrunk = []
            for i in order[:cfg['failure_candidates']]:
                if probe_gaps[i] > 0:
                    cx = counterexample(backend, policy, probes[i], probe_gaps[i], backend.failure_shrink_executions)
                    executions += cx['shrink_executions'] + 2
                    shrunk.append(cx)
            # Keep the shortest shrunk failures (stable sort keeps larger original losses first).
            shrunk.sort(key=lambda cx: len(cx['items']))
            rec['counterexamples'] = shrunk[:cfg['counterexamples_per_proposal']]
            rec['failures_shrunk'] = len(shrunk)
            gate_rng = random.Random(harness_seed(seed, 'gate', call))
            stress = gate_rng.sample(archive, min(cfg['gate_sample'], len(archive)))
            stress_bins = backend.evaluate(policy, [x['case'] for x in stress])
            executions += len(stress)
            summary = fixed_summary(backend, fixed, bins, fixed_refs)
            gate = gate_decision('strict', summary['mean_excess'],
                                 [a - x['reference_bins'] for a, x in zip(stress_bins, stress)], [0.0])
            sig = signature(bins)
            rec.update({'fixed': summary, 'signature': sig,
                        'probe': {'losses': sum(g > 0 for g in probe_gaps), 'wins': sum(g < 0 for g in probe_gaps),
                                  'max_loss': max(probe_gaps)},
                        'shadow_gate': {k: gate[k] for k in ('pass', 'loss_count', 'max_loss', 'total_loss')},
                        'same_as_incumbent': sig == incumbent['signature'],
                        'repeat_of_failed_call': failed_signatures.get(sig)})
            if sum(bins) < sum(incumbent['bins']):
                rec['promoted'] = True
                incumbent = {'name': rec['name'], 'policy': policy, 'call': call, 'fixed': summary,
                             'signature': sig, 'bins': bins}
                incumbent_rec = rec
            else:
                failed_signatures.setdefault(sig, call)
            unique = {}
            for x in archive + [{'case': c, 'reference_bins': r, 'gap': g, 'generation': call,
                                 'id': identity(backend.items(c))} for c, r, g in zip(probes, probe_refs, probe_gaps)]:
                prev = unique.get(x['id'])
                if prev is None or (x['gap'], x['generation']) > (prev['gap'], prev['generation']):
                    unique[x['id']] = x
            archive = sorted(unique.values(), key=lambda x: (x['gap'], x['generation']),
                             reverse=True)[:cfg['archive_size']]
        history.append(rec)
    trace = {'run_id': run_id, 'seed': seed, 'arm': arm, 'backend': backend.name, 'config': cfg,
             'promotion_rule': PROMOTION_RULE, 'system_prompt': system,
             'system_prompt_sha256': hashlib.sha256(system.encode()).hexdigest(),
             'schema': schema, 'calls_completed': len(history), 'stopped': stopped,
             'complete': stopped is None and len(history) == cfg['calls'],
             'final': {'name': incumbent['name'], 'policy': incumbent['policy'], 'call': incumbent['call'],
                       'fixed': incumbent['fixed']},
             'evaluator_executions': executions, 'history': history, 'seconds': time.time() - started}
    write_json(trace_path, trace)
    return trace


def snapshot_sources(out):
    source = out / 'source'
    source.mkdir(parents=True, exist_ok=True)
    files = [p for p in (ROOT / 'falsify').iterdir() if p.suffix in ('.py', '.cpp')]
    files += [ROOT / 'autoresearch' / 'claude.py']
    hashes = {}
    for p in sorted(files):
        name = f'{p.parent.name}__{p.name}'
        shutil.copyfile(p, source / name)
        hashes[name] = hashlib.sha256(p.read_bytes()).hexdigest()
    return hashes


def cmd_run(args):
    out = Path(args.out)
    cfg = {**DEFAULTS, 'calls': args.calls, 'model': args.model, 'memory_token_budget': args.memory_tokens}
    config = {'backend': args.backend, 'arms': args.arms, 'seeds': args.seeds, 'loop': cfg,
              'promotion_rule': PROMOTION_RULE, 'mock': args.mock, 'workers': args.workers,
              'cap_usd': args.cap_usd, 'total_cap_usd': args.total_cap_usd}
    if (out / 'config.json').exists():
        old = read_json(out / 'config.json')
        if {k: old[k] for k in ('backend', 'loop', 'mock')} != {k: config[k] for k in ('backend', 'loop', 'mock')}:
            raise SystemExit('config.json in this directory differs; use a fresh --out')
        config['seeds'] = sorted(set(old['seeds']) | set(args.seeds))
        config['arms'] = [a for a in ARMS if a in set(old['arms']) | set(args.arms)]
        config['invocations'] = old.get('invocations', [])
    out.mkdir(parents=True, exist_ok=True)
    config.setdefault('invocations', []).append({'time': time.time(), 'argv': sys.argv[1:],
                                                 'source_sha256': snapshot_sources(out)})
    write_json(out / 'config.json', config)
    backend = get_backend(args.backend)
    usage_path = out / 'usage.jsonl'
    if args.mock:
        client = MockClient(seed=args.mock_seed)
        prior = 0.0
    else:
        from autoresearch.env import load_env, require
        load_env()
        require('ANTHROPIC_API_KEY', 'live proposal calls')
        client = None
        prior = prior_spend(sorted(Path(args.ledger_root).rglob('usage.jsonl')))
    ledger = SpendLedger(usage_path, args.cap_usd, prior_usd=prior, total_cap_usd=args.total_cap_usd,
                         client_label='mock' if args.mock else 'anthropic')
    proposer = Proposer(ledger, model=args.model, max_tokens=cfg['max_tokens'], client=client)
    backend.evaluate(backend.baseline, backend.cases(0, 1))  # compile/load the evaluator before threads
    jobs = []
    for seed in args.seeds:
        for arm in args.arms:
            path = out / 'runs' / f'{arm}-s{seed}.json.gz'
            if path.exists():
                print(f'skip {path.name}: exists', flush=True)
                continue
            jobs.append((seed, arm, path))
    print(f'{len(jobs)} runs; earlier spend ${prior:.4f}; cap ${args.cap_usd:.2f} '
          f'(total cap ${args.total_cap_usd:.2f})', flush=True)

    def work(job):
        seed, arm, path = job
        try:
            t = run_one(seed, arm, backend, proposer, cfg, path)
        except Exception:  # noqa: BLE001 - one broken run must not kill the others
            traceback.print_exc()
            return f'{arm}-s{seed}: crashed'
        promos = sum(r['promoted'] for r in t['history'])
        return (f'{t["run_id"]}: calls={t["calls_completed"]} promotions={promos} final={t["final"]["name"]} '
                f'fixed={t["final"]["fixed"]["mean_excess"]:+.4f} stopped={t["stopped"]}')

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        for line in pool.map(work, jobs):
            print(line, f'spent=${ledger.spent:.4f}', flush=True)
    print(f'done; this invocation charged ${ledger.spent:.4f}', flush=True)


def bootstrap(diffs, resamples, seed):
    rng = random.Random(seed)
    draws = sorted(mean(rng.choices(diffs, k=len(diffs))) for _ in range(resamples))
    return [draws[int(0.025 * resamples)], draws[int(0.975 * resamples) - 1]]


def trace_digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def audit_seeds(paths):
    """Audit and diagnostic seeds derived from every finished trace: they cannot be
    known, and the instances cannot exist, before all search runs have ended."""
    digest = hashlib.sha256('|'.join(sorted(trace_digest(p) for p in paths)).encode()).hexdigest()
    return int(digest[:12], 16), int(digest[12:24], 16), digest


def run_metrics(trace, audit_result, diag):
    hist = trace['history']
    valid = [r for r in hist if r['status'] == 'ok']
    labels = [d['class'] for d in diag]
    return {'final_audit_excess': audit_result['mean_excess_bins'],
            'final_is_baseline': trace['final']['call'] is None,
            'promotions': sum(r['promoted'] for r in hist),
            'valid_proposals': len(valid), 'invalid_or_failed_calls': len(hist) - len(valid),
            'harmful_fraction': (labels.count('worse') / len(valid)) if valid else None,
            'harmful_or_invalid_fraction': ((labels.count('worse') + len(hist) - len(valid)) / len(hist)) if hist else None,
            'beneficial_proposals': labels.count('better'),
            'mean_proposal_diagnostic_excess': mean(d['mean_excess_bins'] for d in diag) if diag else None,
            'repeated_failed': sum(r.get('repeat_of_failed_call') is not None for r in valid),
            'same_as_incumbent': sum(bool(r.get('same_as_incumbent')) for r in valid),
            'shadow_gate_pass_rate': mean(r['shadow_gate']['pass'] for r in valid) if valid else None,
            'memory_tokens_mean': mean(r['memory']['tokens'] for r in hist) if hist else 0,
            'memory_counterexamples_mean': mean(r['memory']['counterexamples'] for r in hist) if hist else 0,
            'memory_entries_mean': mean(r['memory']['entries'] for r in hist) if hist else 0,
            'input_tokens': sum(r.get('input_tokens', 0) for r in hist),
            'output_tokens': sum(r.get('output_tokens', 0) for r in hist),
            'cost_usd': sum(r.get('cost_usd', 0.0) for r in hist),
            'evaluator_executions': trace['evaluator_executions']}


def evaluate_audit(backend, policy, cases, refs):
    gaps = [a - b for a, b in zip(backend.evaluate(policy, cases), refs)]
    fams = {}
    for c, g in zip(cases, gaps):
        fams.setdefault(backend.family(c), []).append(g)
    return {'mean_excess_bins': mean(gaps), 'wins': sum(g < 0 for g in gaps), 'losses': sum(g > 0 for g in gaps),
            'ties': sum(g == 0 for g in gaps), 'by_family': {f: mean(v) for f, v in fams.items()}}


def cmd_audit(args):
    out = Path(args.out)
    if (out / 'summary.json').exists() and not args.force:
        raise SystemExit('Audit already done (summary.json exists)')
    config = read_json(out / 'config.json')
    cfg = config['loop']
    backend = get_backend(config['backend'])
    paths = [out / 'runs' / f'{a}-s{s}.json.gz' for s in config['seeds'] for a in config['arms']]
    missing = [p.name for p in paths if not p.exists()]
    if missing:
        raise SystemExit(f'Runs missing, audit refused: {missing}')
    traces = {(t['seed'], t['arm']): t for t in (read_json(p) for p in paths)}
    incomplete = [k for k, t in traces.items() if not t['complete']]
    audit_seed, diagnostic_seed, digest = audit_seeds(paths)
    cases = backend.cases(audit_seed, cfg['audit_cases'], 'audit')
    refs = backend.evaluate(backend.baseline, cases)
    diag_cases = backend.cases(diagnostic_seed, cfg['diagnostic_cases'], 'audit')
    diag_refs = backend.evaluate(backend.baseline, diag_cases)
    per_run = {}
    for (seed, arm), t in sorted(traces.items()):
        result = evaluate_audit(backend, t['final']['policy'], cases, refs)
        diag = []
        for r in t['history']:
            if r['status'] != 'ok':
                diag.append({'call': r['call'], 'class': 'invalid', 'mean_excess_bins': None})
                continue
            d = evaluate_audit(backend, r['policy'], diag_cases, diag_refs)
            x = d['mean_excess_bins']
            diag.append({'call': r['call'], 'mean_excess_bins': x,
                         'class': 'better' if x < 0 else 'worse' if x > 0 else 'tied'})
        valid_diag = [d for d in diag if d['class'] != 'invalid']
        per_run[f'{arm}-s{seed}'] = {'seed': seed, 'arm': arm, 'audit': result, 'diagnostic': diag,
                                     'metrics': run_metrics(t, result, valid_diag),
                                     'final': t['final']}
    keys = ['final_audit_excess', 'harmful_fraction', 'harmful_or_invalid_fraction', 'mean_proposal_diagnostic_excess',
            'repeated_failed', 'same_as_incumbent', 'promotions', 'beneficial_proposals', 'invalid_or_failed_calls',
            'shadow_gate_pass_rate', 'memory_tokens_mean', 'memory_counterexamples_mean', 'memory_entries_mean',
            'input_tokens', 'output_tokens', 'cost_usd']
    arms = {}
    for arm in config['arms']:
        rows = [v['metrics'] for v in per_run.values() if v['arm'] == arm]
        arms[arm] = {k: mean(r[k] for r in rows if r[k] is not None) if any(r[k] is not None for r in rows) else None
                     for k in keys}
        arms[arm]['runs'] = len(rows)
        arms[arm]['final_is_baseline'] = sum(r['final_is_baseline'] for r in rows)
        arms[arm]['by_family'] = {f: mean(v['audit']['by_family'][f] for v in per_run.values() if v['arm'] == arm)
                                  for f in backend.audit_families}
    comparisons = []
    for a, b in [('executable', 'none'), ('executable', 'prose'), ('prose', 'none')]:
        if a not in config['arms'] or b not in config['arms']:
            continue
        for k in ['final_audit_excess', 'harmful_fraction', 'mean_proposal_diagnostic_excess', 'repeated_failed']:
            diffs = []
            for s in config['seeds']:
                x, y = per_run[f'{a}-s{s}']['metrics'][k], per_run[f'{b}-s{s}']['metrics'][k]
                if x is not None and y is not None:
                    diffs.append(x - y)
            if diffs:
                comparisons.append({'comparison': f'{a} - {b}', 'metric': k, 'mean': mean(diffs),
                                    'bootstrap_95': bootstrap(diffs, cfg['bootstrap_resamples'], cfg['bootstrap_seed']),
                                    'paired_seed_differences': diffs})
    usage = [json.loads(l) for l in (out / 'usage.jsonl').read_text().splitlines() if l.strip()]
    summary = {'backend': config['backend'], 'seeds': config['seeds'], 'arms': arms, 'comparisons': comparisons,
               'incomplete_runs': [f'{a}-s{s}' for s, a in incomplete],
               'audit_seed': audit_seed, 'diagnostic_seed': diagnostic_seed, 'trace_digest': digest,
               'audit_cases': len(cases), 'diagnostic_cases': len(diag_cases),
               'usage': {'charged_usd': sum(u.get('charged_usd', 0.0) for u in usage),
                         'message_attempts': sum(u['kind'] == 'messages' for u in usage),
                         'message_failures': sum(u['kind'] == 'messages' and u['status'] != 'ok' for u in usage),
                         'count_tokens_calls': sum(u['kind'] == 'count_tokens' for u in usage)}}
    write_json(out / 'audit.json', per_run)
    write_json(out / 'audit_cases.json.gz', [{'family': backend.family(c), 'items': backend.items(c)} for c in cases])
    write_json(out / 'summary.json', summary)
    print(json.dumps({'arms': {a: {k: arms[a][k] for k in ('final_audit_excess', 'harmful_fraction', 'repeated_failed',
                                                            'promotions', 'memory_tokens_mean', 'cost_usd')}
                               for a in arms}}, indent=1))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest='cmd', required=True)
    run = sub.add_parser('run')
    run.add_argument('--out', required=True)
    run.add_argument('--backend', default='weights20_synthetic80')
    run.add_argument('--seeds', type=int, nargs='+', required=True)
    run.add_argument('--arms', nargs='+', default=list(ARMS), choices=ARMS)
    run.add_argument('--calls', type=int, default=DEFAULTS['calls'])
    run.add_argument('--model', default=DEFAULTS['model'])
    run.add_argument('--memory-tokens', type=int, default=DEFAULTS['memory_token_budget'])
    run.add_argument('--workers', type=int, default=6)
    run.add_argument('--cap-usd', type=float, required=True, help='spend cap for this invocation')
    run.add_argument('--total-cap-usd', type=float, default=15.0, help='cap including earlier usage under --ledger-root')
    run.add_argument('--ledger-root', default='experiments/memory-ablation-v1')
    run.add_argument('--mock', action='store_true', help='offline mock client; no API calls')
    run.add_argument('--mock-seed', type=int, default=0)
    audit = sub.add_parser('audit')
    audit.add_argument('--out', required=True)
    audit.add_argument('--force', action='store_true')
    args = parser.parse_args(argv)
    if args.cmd == 'run':
        cmd_run(args)
    else:
        cmd_audit(args)


if __name__ == '__main__':
    main()
