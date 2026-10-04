"""Trusted child harness. Honest-loop isolation, not a hardened security sandbox."""
import importlib.util
import json
import random
import sys
import time
import numpy as np


def pack(priority, case):
    items, capacity = case['items'], case['capacity']
    bins = np.full(len(items), capacity, dtype=float)
    assignments = []
    for item in items:
        feasible = np.flatnonzero(bins >= item)
        # Fancy indexing copies capacities: candidate mutation cannot change the packer.
        scores = np.asarray(priority(item, bins[feasible]), dtype=float)
        if scores.shape != feasible.shape or not np.isfinite(scores).all():
            raise ValueError('priority must return a finite score per feasible bin')
        chosen = int(feasible[int(np.argmax(scores))])
        bins[chosen] -= item
        assignments.append(chosen)
    return {'bins': int(np.count_nonzero(bins != capacity)), 'assignments': assignments}


def plain(x):
    if isinstance(x, np.ndarray): return x.tolist()
    if isinstance(x, np.generic): return x.item()
    if isinstance(x, (list, tuple)): return [plain(v) for v in x]
    if isinstance(x, dict): return {str(k): plain(v) for k, v in x.items()}
    return x


def main():
    program, mode, input_path, output_path = sys.argv[1:]
    case = json.loads(open(input_path).read())
    random.seed(case.get('seed', 0)); np.random.seed(case.get('seed', 0) % (2**32))
    spec = importlib.util.spec_from_file_location('candidate', program)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    t = time.monotonic()
    result = mod.solve(n=case['n']) if mode == 'circle' else pack(mod.priority, case)
    with open(output_path, 'w') as f:
        json.dump({'result': plain(result), 'seconds': time.monotonic()-t}, f, allow_nan=False)


if __name__ == '__main__': main()
