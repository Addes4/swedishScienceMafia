"""Sandboxed evaluation of model-written priority(item, bins) code for the memory study.

The candidate interface and online semantics are those of problems/bin_packing_online
(FunSearch's evaluator: as many bins as items, unused bins included, argmax with first
index on ties). Model code never runs in this process:

- Long instances (fixed suite, diagnostic and audit) run through the integrity gate's own
  online runner, autoresearch.sandbox.run_online, with the problem's trusted DRIVER: one
  fresh process per instance, items revealed one at a time, credentials stripped.
- Short probe streams and shrinking run hundreds of tiny instances, so they use a
  persistent child with the same protocol: items still arrive one at a time, and the
  candidate module is re-executed for every instance so no state carries over. Every
  counterexample that is kept is re-checked in a fresh run_online process.
- Programs are screened with the gate's static checks (autoresearch.gate.static_violations)
  before anything runs. Best-fit references are computed natively (falsify.longpack).

`assess(payload)` evaluates one proposal and `pack_shard(payload)` packs a list of long
instances; both are pure functions of JSON payloads so they run locally or on Modal
(falsify/memory_ablation_modal.py).
"""
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from autoresearch.gate import static_violations
from autoresearch.sandbox import _child_env, _read_line, run_online
from falsify.longpack import l2_bound, pack_rule, weibull_items

ROOT = Path(__file__).resolve().parents[1]
CAPACITY = 100
GENERIC_REJECTION = 'rejected by the integrity gate'


def _verify():
    spec = importlib.util.spec_from_file_location('bp_verify', ROOT / 'problems' / 'bin_packing_online' / 'verify.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


VERIFY = _verify()
DRIVER = VERIFY.DRIVER


def screen(source):
    """None if the program may run, else the reason it is rejected (shown generically)."""
    if not isinstance(source, str) or 'def priority' not in source:
        return 'no priority function'
    violations = static_violations(source)
    return ', '.join(violations) if violations else None


def canonical(assignments):
    """Relabel bins in order of first use, so equivalent packings compare equal."""
    labels = {}
    return [labels.setdefault(b, len(labels)) for b in assignments]


def packing_hash(assignments):
    return hashlib.sha256(json.dumps(canonical(assignments)).encode()).hexdigest()[:16]


def bins_from(items, assignments):
    bins = {}
    for item, b in zip(items, canonical(assignments)):
        bins.setdefault(b, []).append(item)
    return [bins[b] for b in sorted(bins)]


def divergence(items, candidate, reference):
    """First arrival where the two policies make different choices from the same state."""
    a_lab, b_lab, free = canonical(candidate), canonical(reference), {}
    for k, (item, a, b) in enumerate(zip(items, a_lab, b_lab)):
        if a != b:
            return {'index': k, 'item': item, 'candidate_free': free.get(a, CAPACITY),
                    'reference_free': free.get(b, CAPACITY), 'candidate_new': a not in free,
                    'reference_new': b not in free}
        free[a] = free.get(a, CAPACITY) - item
    return None


def best_fit(items, trace=False):
    return pack_rule(list(items), 'best_fit', CAPACITY, trace)


class CandidateError(RuntimeError):
    pass


def pack_fresh(path, items, timeout_s):
    """One instance in a fresh gate process. Returns (bins, assignments)."""
    run = run_online(str(path), VERIFY.FUNCTION, DRIVER, {'capacity': CAPACITY, 'num_items': len(items)},
                     list(items), timeout_s)
    if not run.ok:
        raise CandidateError(run.error or 'program failed')
    try:
        bins = VERIFY.bins_used(run.construction, list(items))
    except ValueError as exc:
        raise CandidateError(f'invalid decisions: {exc}') from None
    return bins, run.construction, run.seconds


_PERSISTENT_CHILD = r"""
import importlib.util, json, os, sys
path, fn_name, driver_source, rfd, wfd = sys.argv[1:6]
reader = os.fdopen(int(rfd), "r")
writer = os.fdopen(int(wfd), "w")
driver = {}
exec(compile(driver_source, "<driver>", "exec"), driver)

def emit(decision):
    writer.write(json.dumps(decision) + "\n")
    writer.flush()

def next_input():
    line = reader.readline()
    if not line:
        raise SystemExit(0)
    value = json.loads(line)
    return None if isinstance(value, dict) else value

while True:
    line = reader.readline()
    if not line:
        break
    header = json.loads(line)
    spec = importlib.util.spec_from_file_location("candidate", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    driver["drive"](getattr(mod, fn_name), header, next_input, emit)
    emit({"done": True})
"""


class PersistentPacker:
    """Packs many short instances in one child; the module is reloaded per instance and
    items are revealed one at a time, as in the gate's online protocol."""

    def __init__(self, path):
        self.path = str(path)
        self.proc = None
        self.executions = 0

    def _start(self):
        to_r, self._to_w = os.pipe()
        self._from_r, from_w = os.pipe()
        self._log = tempfile.NamedTemporaryFile('w+', suffix='.log', delete=False)
        self._tmp = tempfile.mkdtemp(prefix='candidate_')
        self.proc = subprocess.Popen(
            [sys.executable, '-c', _PERSISTENT_CHILD, self.path, VERIFY.FUNCTION, DRIVER, str(to_r), str(from_w)],
            pass_fds=(to_r, from_w), cwd=self._tmp, env=_child_env(), stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL, stderr=self._log)
        os.close(to_r)
        os.close(from_w)
        self._writer = os.fdopen(self._to_w, 'w')
        self._buffer = bytearray()

    def _fail(self, why):
        tail = ''
        try:
            self._log.flush()
            self._log.seek(0)
            tail = '\n'.join(self._log.read().strip().splitlines()[-4:])
        except (OSError, ValueError):
            pass
        self.close()
        raise CandidateError(tail or why)

    def pack(self, items, timeout_s=10.0):
        if self.proc is None:
            self._start()
        self.executions += 1
        deadline = time.monotonic() + timeout_s
        decisions = []
        try:
            self._writer.write(json.dumps({'capacity': CAPACITY, 'num_items': len(items)}) + '\n')
            for value in items:
                self._writer.write(json.dumps(value) + '\n')
                self._writer.flush()
                line = _read_line(self._from_r, self._buffer, deadline)
                if line is None:
                    self._fail('timed out' if time.monotonic() >= deadline else 'program stopped')
                decisions.append(json.loads(line))
            self._writer.write(json.dumps({'end': True}) + '\n')
            self._writer.flush()
            line = _read_line(self._from_r, self._buffer, deadline)
        except (BrokenPipeError, ValueError):
            self._fail('protocol error')
        if line is None or json.loads(line) != {'done': True}:
            self._fail('program did not finish the instance')
        try:
            bins = VERIFY.bins_used(decisions, list(items))
        except ValueError as exc:
            self._fail(f'invalid decisions: {exc}')
        return bins, decisions

    def close(self):
        if self.proc is not None:
            for f in (self._writer,):
                try:
                    f.close()
                except (OSError, BrokenPipeError):
                    pass
            try:
                os.close(self._from_r)
            except OSError:
                pass
            try:
                self.proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.proc.kill()
                self.proc.wait()
            self._log.close()
            os.unlink(self._log.name)
            self.proc = None


class Reference:
    """Native best-fit, or another program through a persistent packer."""

    def __init__(self, path=None):
        self.packer = PersistentPacker(path) if path else None

    def pack(self, items):
        return self.packer.pack(items) if self.packer else best_fit(items, True)

    def close(self):
        if self.packer:
            self.packer.close()


def shrink(candidate, reference, items, max_trials):
    """Greedy single-item deletion keeping candidate bins > reference bins (falsify/backends.py)."""
    current, trials, changed = list(items), 0, True
    while changed and trials < max_trials:
        changed, i = False, 0
        while i < len(current) and trials < max_trials:
            trial = current[:i] + current[i + 1:]
            trials += 1
            if candidate.pack(trial)[0] > reference.pack(trial)[0]:
                current, changed = trial, True
            else:
                i += 1
    return current, trials


def mine(candidate, reference, windows, cfg, deadline):
    """Short-stream comparison and shrunk counterexamples against one reference."""
    gaps = []
    for w in windows:
        if time.monotonic() > deadline:
            return {'gaps': gaps, 'counterexamples': [], 'trials': 0, 'stopped': 'mining time limit'}
        gaps.append(candidate.pack(w)[0] - reference.pack(w)[0])
    order = sorted((i for i, g in enumerate(gaps) if g > 0), key=lambda i: (-gaps[i], i))
    shrunk, trials = [], 0
    for i in order[:cfg['failure_candidates']]:
        if time.monotonic() > deadline:
            break
        small, used = shrink(candidate, reference, windows[i], cfg['shrink_trials'])
        trials += used
        if len(small) <= cfg['max_counterexample_items']:
            shrunk.append({'items': small, 'original_length': len(windows[i]), 'original_gap': gaps[i],
                           'shrink_trials': used})
    shrunk.sort(key=lambda c: len(c['items']))
    return {'gaps': gaps, 'counterexamples': shrunk, 'trials': trials, 'stopped': None}


def finish_counterexamples(cand_path, ref_path, found, keep, timeout_s):
    """Re-run kept inputs in fresh gate processes and attach both packings."""
    out = []
    for cx in found:
        if len(out) == keep:
            break
        try:
            cb, ca, _ = pack_fresh(cand_path, cx['items'], timeout_s)
            rb, ra, _ = pack_fresh(ref_path, cx['items'], timeout_s) if ref_path else (*best_fit(cx['items'], True), 0)
        except CandidateError:
            continue
        if cb <= rb:
            continue  # did not reproduce from a fresh process; never shown
        out.append({**cx, 'candidate_bins': cb, 'reference_bins': rb,
                    'candidate_packing': bins_from(cx['items'], ca),
                    'reference_packing': bins_from(cx['items'], ra),
                    'divergence': divergence(cx['items'], ca, ra), 'verified_fresh': True})
    return out


def write_program(directory, name, source):
    path = Path(directory) / f'{name}.py'
    path.write_text(source)
    return path


def assess(payload):
    """Evaluate one proposal. payload keys: code, incumbent_code (None = best-fit),
    fixed (list of [namespace, seed, n]), probe ([namespace, seed, n]), window, cfg."""
    started = time.monotonic()
    cfg = payload['cfg']
    reason = screen(payload['code'])
    if reason:
        return {'status': 'static', 'error': GENERIC_REJECTION, 'private_reason': reason,
                'seconds': time.monotonic() - started}
    result = {'status': 'ok', 'fixed_bins': [], 'fixed_hashes': [], 'fixed_seconds': []}
    with tempfile.TemporaryDirectory(prefix='assess_') as tmp:
        cand_path = write_program(tmp, 'candidate', payload['code'])
        inc_path = write_program(tmp, 'incumbent', payload['incumbent_code']) if payload['incumbent_code'] else None
        for namespace, seed, n in payload['fixed']:
            items = weibull_items(seed, n, namespace)
            try:
                bins, decisions, seconds = pack_fresh(cand_path, items, cfg['timeout_s'])
            except CandidateError as exc:
                return {'status': 'error', 'error': str(exc)[-400:], 'seconds': time.monotonic() - started}
            result['fixed_bins'].append(bins)
            result['fixed_hashes'].append(packing_hash(decisions))
            result['fixed_seconds'].append(seconds)
        namespace, seed, n = payload['probe']
        stream = weibull_items(seed, n, namespace)
        w = cfg['window']
        windows = [stream[k:k + w] for k in range(0, n - w + 1, w)]
        deadline = time.monotonic() + cfg['mining_seconds']
        candidate = PersistentPacker(cand_path)
        references = [('incumbent', inc_path)] + ([('best_fit', None)] if inc_path else [])
        result['mining'] = {}
        try:
            for label, ref_path in references:
                ref = Reference(ref_path)
                try:
                    m = mine(candidate, ref, windows, cfg, deadline)
                except CandidateError as exc:
                    m = {'gaps': [], 'counterexamples': [], 'trials': 0, 'stopped': f'program failed: {str(exc)[-200:]}'}
                finally:
                    ref.close()
                m['counterexamples'] = finish_counterexamples(cand_path, ref_path, m['counterexamples'],
                                                              cfg['counterexamples'], cfg['timeout_s'])
                m['losses'] = sum(g > 0 for g in m['gaps'])
                m['wins'] = sum(g < 0 for g in m['gaps'])
                result['mining'][label] = m
        finally:
            candidate.close()
        if not inc_path:
            result['mining']['best_fit'] = result['mining']['incumbent']
        result['short_executions'] = candidate.executions
    result['seconds'] = time.monotonic() - started
    return result


def pack_shard(payload):
    """Bins per long instance for one program (None = native best-fit). payload keys:
    code, instances (list of [namespace, seed, n]), timeout_s."""
    started = time.monotonic()
    out = {'bins': [], 'l2': [], 'best_fit': [], 'error': None}
    with tempfile.TemporaryDirectory(prefix='shard_') as tmp:
        path = write_program(tmp, 'program', payload['code']) if payload['code'] else None
        if path and screen(payload['code']):
            out['error'] = GENERIC_REJECTION
        for namespace, seed, n in payload['instances']:
            items = weibull_items(seed, n, namespace)
            out['best_fit'].append(best_fit(items))
            out['l2'].append(l2_bound(items))
            if out['error']:
                out['bins'].append(None)
                continue
            if path is None:
                out['bins'].append(out['best_fit'][-1])
                continue
            try:
                bins, decisions, _ = pack_fresh(path, items, payload['timeout_s'])
                out['bins'].append(bins)
                if payload.get('return_decisions'):
                    out.setdefault('decisions', []).append(decisions)
            except CandidateError as exc:
                out['bins'].append(None)
                out['error'] = str(exc)[-300:]
    out['seconds'] = time.monotonic() - started
    return out


def agreement(items, decisions, priority):
    """Share of steps at which trusted `priority` (e.g. FunSearch's heuristic), shown the
    bins of the candidate's own trajectory, would pick a bin with the same remaining
    capacity as the candidate did. 1.0 means the same policy up to equivalent ties."""
    import numpy as np
    bins = np.full(len(items), CAPACITY, dtype=np.int64)
    same = 0
    for item, chosen in zip(items, decisions):
        valid = np.nonzero((bins - item) >= 0)[0]
        ref = int(valid[np.argmax(priority(item, bins[valid]))])
        same += int(bins[ref] == bins[chosen])
        bins[chosen] -= item
    return same / len(items)
