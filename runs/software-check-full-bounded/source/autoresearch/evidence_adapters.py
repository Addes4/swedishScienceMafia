"""Problem boundaries for the unified research loop; all objectives minimized."""
import ast
import hashlib
import json
import math
import os
import random
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from .gate import static_violations, _load_verify
from .sandbox import _child_env
from .live import dump
from falsify.core import BEST_FIT, FEATURES, TRAIN_FAMILIES, SHIFT_FAMILIES, pack, suite

ROOT = Path(__file__).resolve().parents[1]
WORKER = Path(__file__).with_name('research_worker.py')
BEST_CODE = 'import numpy as np\n\ndef priority(item, bins):\n    return -(bins - item)\n'
FIRST_CODE = 'import numpy as np\n\ndef priority(item, bins):\n    return -np.arange(len(bins), dtype=float)\n'
WEIGHT_SCHEMA = {'type': 'object', 'properties': {
    'hypothesis': {'type': 'string'}, 'falsification': {'type': 'string'},
    'weights': {'type': 'array', 'items': {'type': 'number'}, 'minItems': 12, 'maxItems': 12}},
    'required': ['hypothesis', 'falsification', 'weights'], 'additionalProperties': False}


def digest(value):
    s = value if isinstance(value, str) else json.dumps(value, sort_keys=True)
    return hashlib.sha256(s.encode()).hexdigest()


def case_id(case):
    return digest({k: v for k, v in case.items() if k not in ('id', 'family', 'source')})


def code_from_text(text):
    import re
    blocks = re.findall(r'```(?:python)?\s*\n(.*?)```', text, re.S)
    return max(blocks, key=len).strip()+'\n' if blocks else text.strip()+'\n'


def check_code(source):
    errors = static_violations(source)
    try: tree = ast.parse(source)
    except SyntaxError: return errors + ['invalid Python syntax']
    for node in ast.walk(tree):
        if isinstance(node, ast.Import): names = [a.name.split('.')[0] for a in node.names]
        elif isinstance(node, ast.ImportFrom): names = [(node.module or '').split('.')[0]]
        else: names = []
        if any(n not in {'numpy', 'scipy', 'math', 'random', 'itertools', 'functools', 'collections', 'time'} for n in names):
            errors.append('unsupported import')
        if isinstance(node, ast.Attribute) and node.attr.startswith('__'): errors.append('runtime introspection')
        if isinstance(node, ast.Name) and node.id in {'globals', 'locals', 'vars', 'getattr', 'setattr', '__builtins__'}:
            errors.append('runtime introspection')
    return sorted(set(errors))


class BaseAdapter:
    schema = None
    tolerance = .002
    def __init__(self, out, timeout=30):
        self.out, self.timeout = Path(out), timeout
        self.cache, self.executions, self.item_steps, self.elapsed = {}, 0, 0, 0.
        (self.out/'evaluations').mkdir(parents=True, exist_ok=True)

    def evaluate(self, payload, cases, split):
        rows = []
        for case in cases:
            key = digest([payload, case, self.timeout])
            if key not in self.cache:
                t = time.monotonic()
                result = self.one(payload, case)
                seconds = time.monotonic()-t
                self.executions += 1; self.item_steps += len(case.get('items', [])); self.elapsed += seconds
                self.cache[key] = {'case_id': case_id(case), 'family': case['family'], 'seconds': seconds, **result}
                dump(self.out/'evaluations'/f'{key}.json', self.cache[key])
            rows.append(self.cache[key])
        valid = bool(rows) and all(x['valid'] for x in rows)
        return {'valid': valid, 'objective': sum(r['objective'] for r in rows)/len(rows) if valid else None,
                'rows': rows, 'split': split, 'logical_executions': len(cases),
                'logical_item_steps': sum(len(c.get('items', [])) for c in cases)}

    def metrics(self):
        return {'physical_executions': self.executions, 'physical_item_steps': self.item_steps,
                'evaluation_seconds': self.elapsed}

    def complexity(self, payload):
        return len(list(ast.walk(ast.parse(payload))))

    def child(self, source, case):
        errors = check_code(source)
        if errors: return {'valid': False, 'reason': 'rejected by integrity gate', 'private_reason': errors}
        with tempfile.TemporaryDirectory(prefix='ssm-candidate-') as d:
            p = Path(d); (p/'candidate.py').write_text(source); dump(p/'input.json', case)
            env = _child_env()
            env.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1')
            try:
                proc = subprocess.run([sys.executable, '-I', str(WORKER), str(p/'candidate.py'), self.mode,
                                       str(p/'input.json'), str(p/'output.json')], cwd=d, env=env,
                                      capture_output=True, text=True, timeout=self.timeout)
            except subprocess.TimeoutExpired:
                return {'valid': False, 'reason': f'timeout after {self.timeout}s'}
            if proc.returncode != 0 or not (p/'output.json').exists():
                # Candidate stderr only; stripped environment and no credential-bearing paths.
                return {'valid': False, 'reason': (proc.stderr[-1200:] or 'no candidate result')}
            try: return {'valid': True, **json.loads((p/'output.json').read_text())}
            except (ValueError, OSError): return {'valid': False, 'reason': 'malformed result'}


class BoundedAdapter(BaseAdapter):
    name, mode, schema = 'bounded', 'weights', WEIGHT_SCHEMA
    initial, first_fit = [float(x) for x in BEST_FIT], [0.]*12
    description = ('Online bin packing: capacity 100, 80 arriving integer items, five development families. '
                   'Fixed packer scores each feasible bin by a weighted sum; maximum wins, earliest-index ties. '
                   'Only open a bin when no existing bin fits. No future items. Return JSON with hypothesis, '
                   'falsification, and exactly 12 finite weights in [-12,12], ordered as: '+json.dumps(FEATURES)+
                   '. Previous studies did not beat best-fit on fresh data; strong quarter/half reservation '
                   'and tiny-gap penalties regressed. Do not repeat these unchanged. Seek a distinct testable revision.')

    def parse(self, text):
        obj = json.loads(text); w = obj['weights']
        if len(w) != 12 or any(isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(x) or abs(x)>12 for x in w):
            raise ValueError('Expected twelve finite bounded weights')
        return [float(x) if x else 0. for x in w], obj.get('hypothesis', '')

    def cases(self, seed, count, audit=False):
        return [{**c, 'capacity': 100} for c in suite(seed, count, TRAIN_FAMILIES+SHIFT_FAMILIES if audit else TRAIN_FAMILIES)]

    def complexity(self, payload): return sum(x != 0 for x in payload)

    def one(self, payload, case):
        try:
            bins, assignments = pack(case['items'], payload, True)
            return {'valid': True, 'objective': bins, 'bins': bins, 'assignments': assignments}
        except ValueError as e: return {'valid': False, 'reason': str(e)}


class CircleAdapter(BaseAdapter):
    name, mode, tolerance = 'circle', 'circle', 1e-6
    description = ('Write complete Python defining solve(n=26) returning (centers, radii) of 26 nonoverlapping '
                   'circles contained in the unit square. Maximize sum of radii. Only standard safe libraries, '
                   'numpy and scipy. No files, network, subprocesses, runtime introspection or verifier access. '
                   'Each run has a 30-second limit including imports. Respect the requested limit; use bounded '
                   'iterations. RNGs are seeded by the harness. Return one Python code block. Do not hardcode '
                   'a published construction. Develop a construction or optimization algorithm.')
    initial = (ROOT/'problems/circle_packing/initial.py').read_text()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.verify = _load_verify(ROOT/'problems/circle_packing')

    def parse(self, text):
        code = code_from_text(text); ast.parse(code)
        return code, 'Model-generated circle solver'

    def cases(self, seed, count, audit=False):
        return [{'n': 26, 'seed': seed+i, 'family': 'circle26'} for i in range(count)]

    def one(self, payload, case):
        r = self.child(payload, case)
        if not r['valid']: return r
        try:
            check = self.verify.check(r['result'], case)
            strict = self.verify.check_strict(r['result'], case)
            valid = check['valid'] and strict and math.isfinite(check['score'])
            return {'valid': valid, 'objective': -check['score'] if valid else None,
                    'score': check['score'], 'reason': check['reason'] if check['valid'] is False else ('strict geometry check failed' if not strict else ''),
                    'construction': r['result'], 'strict_valid': strict, 'solver_seconds': r['seconds']}
        except (ValueError, TypeError, OverflowError): return {'valid': False, 'reason': 'malformed geometry'}


class RichAdapter(BaseAdapter):
    name, mode, initial, first_fit = 'rich', 'rich', BEST_CODE, FIRST_CODE
    description = ('Improve online bin packing. Return complete Python defining priority(item, bins), where bins '
                   'is a numpy array of ALL feasible remaining bin capacities, including unused bins. Return a '
                   'finite score per bin; maximum wins, earliest-index ties. The fixed packer preallocates as '
                   'many bins as items, as in the public FunSearch notebook. The heuristic sees no future items. '
                   'Development data mix uniform integer items 20..100, capacity 150 (OR-style), and rounded '
                   'clipped Weibull(shape=3, scale=45) integer items 1..100, capacity 100. Objective: mean '
                   'candidate-minus-best-fit bins, each case weighted equally. Python, numpy, scipy, math only; '
                   'no file/process/network/introspection/evaluator access. Return one complete Python block. '
                   'Favor fast vector operations. Do not copy a published heuristic verbatim.')

    def parse(self, text):
        code = code_from_text(text); ast.parse(code)
        return code, 'Model-generated online priority function'

    def cases(self, seed, count, audit=False):
        import numpy as np
        rng = np.random.default_rng(seed)
        out = []
        for i in range(count):
            if i % 2 == 0:
                n = 500 if audit else 120
                items, capacity, family = rng.integers(20, 101, n).tolist(), 150, 'or_uniform'
            else:
                items = np.clip(np.rint(rng.weibull(3, 5000)*45), 1, 100).astype(int).tolist()
                capacity, family = 100, 'weibull_5k'
            out.append({'items': items, 'capacity': capacity, 'family': family, 'seed': seed+i})
        return out

    def one(self, payload, case):
        r = self.child(payload, case)
        if not r['valid']: return r
        result = r['result']; xs = result.get('assignments', [])
        if len(xs) != len(case['items']) or any(type(i) is not int or not 0<=i<len(xs) for i in xs):
            return {'valid': False, 'reason': 'invalid assignment vector'}
        loads = {}
        for item, index in zip(case['items'], xs): loads[index] = loads.get(index, 0)+item
        if any(load > case['capacity'] for load in loads.values()) or result.get('bins') != len(loads):
            return {'valid': False, 'reason': 'packing fails independent capacity/count check'}
        return {'valid': True, 'objective': len(loads), 'bins': len(loads), 'assignments': xs,
                'l1': math.ceil(sum(case['items'])/case['capacity']), 'solver_seconds': r['seconds']}


ADAPTERS = {'bounded': BoundedAdapter, 'circle': CircleAdapter, 'rich': RichAdapter}
