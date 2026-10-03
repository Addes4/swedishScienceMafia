"""Long-instance evaluator: agreement with the existing packers, independent references and
FunSearch's own evaluator and published numbers."""
import bisect
import gzip
import importlib.util
import json
import random
from pathlib import Path

import numpy as np

from falsify.contextual import CONTEXT_BEST_FIT, anchors, mutate_contextual, pack_contextual
from falsify.core import BEST_FIT, SHIFT_FAMILIES, TRAIN_FAMILIES, pack
from falsify.funsearch_heuristics import best_fit as best_fit_priority, funsearch_weibull
from falsify.longpack import (LINEAR_OPEN_BEST_FIT, Instance, falsify_items, l1_bound, l2_bound, pack_linear,
                              pack_priority, pack_rule, weibull_items)

ROOT = Path(__file__).resolve().parents[1]


def bins_best_fit(items, capacity=100):
    remaining = []                      # sorted remaining capacities of all bins
    for x in items:
        i = bisect.bisect_left(remaining, x)
        r = remaining.pop(i) - x if i < len(remaining) else capacity - x
        bisect.insort(remaining, r)
    return len(remaining)


def reference_first_fit(items, capacity=100):
    loads = []
    for x in items:
        for i, load in enumerate(loads):
            if load + x <= capacity:
                loads[i] += x
                break
        else:
            loads.append(x)
    return len(loads)


def funsearch_skeleton(items, capacity, priority):
    """Verbatim logic of FunSearch's notebook skeleton (online_binpack + evaluate), one instance."""
    bins = np.array([capacity for _ in range(len(items))])
    for item in items:
        valid_bin_indices = np.nonzero((bins - item) >= 0)[0]
        priorities = priority(item, bins[valid_bin_indices])
        best_bin = valid_bin_indices[np.argmax(priorities)]
        bins[best_bin] -= item
    return (bins != capacity).sum()


def test_linear_matches_contextual_packer_exactly():
    rng = random.Random(11)
    weights = [list(CONTEXT_BEST_FIT)] + [a['weights'] for a in anchors()]
    for _ in range(30):
        weights.append(mutate_contextual(rng.choice(weights), rng))
    for k, family in enumerate(TRAIN_FAMILIES + SHIFT_FAMILIES):
        for n in (80, 1500):
            items = falsify_items(1000 + k * 7 + n, family, n)
            inst = Instance(items)
            for w in weights[::3]:
                assert pack_linear(w, inst, trace=True) == pack_contextual(items, w, trace=True)


def test_linear_with_new_bin_option_at_zero_weight_is_best_fit():
    for seed in range(5):
        items = weibull_items(seed, 2000)
        assert pack_linear(LINEAR_OPEN_BEST_FIT, items) == pack_rule(items, 'best_fit')


def test_new_bin_feature_changes_decisions():
    items = weibull_items(3, 2000)
    eager = list(LINEAR_OPEN_BEST_FIT)
    eager[20] = 5.0                     # always prefer an unused bin
    assert pack_linear(eager, items) == len(items)


def test_rules_match_independent_references():
    for seed in range(4):
        for items in (weibull_items(seed, 3000), falsify_items(seed, TRAIN_FAMILIES[seed], 600)):
            assert pack_rule(items, 'best_fit') == bins_best_fit(items)
            assert pack_rule(items, 'first_fit') == reference_first_fit(items)
        short = falsify_items(seed, 'uniform', 80)
        assert pack_rule(short, 'best_fit') == pack(short, BEST_FIT)


def test_priority_packer_is_funsearch_skeleton():
    for seed in range(3):
        items = weibull_items(seed, 800)
        assert pack_priority(funsearch_weibull, items) == funsearch_skeleton(items, 100, funsearch_weibull)
        assert pack_priority(best_fit_priority, items) == pack_rule(items, 'best_fit')


def test_ab_heuristics_match_the_papers_priority_functions():
    from falsify.funsearch_heuristics import AB_VARIANTS, ab_priority
    from falsify.longpack import pack_ab
    rng = random.Random(4)
    for k in range(9):
        variant = AB_VARIANTS[k % 3]
        a = rng.randint(0, 8)
        b = rng.randint(a + 1, 40)
        items = weibull_items(k, 400) if k % 2 else falsify_items(k, TRAIN_FAMILIES[k % 5], 300)
        assert pack_ab(items, variant, a, b, trace=True) == pack_priority(ab_priority(variant, a, b), items, trace=True)


def test_positive_control_on_funsearch_test_instances():
    with gzip.open(ROOT / 'experiments' / 'bp-ceiling-v1' / 'funsearch_weibull5k_test.json.gz', 'rt') as f:
        data = json.load(f)['instances']
    bf = [pack_rule(v['items'], 'best_fit') for v in data.values()]
    fs = [pack_priority(funsearch_weibull, v['items']) for v in data.values()]
    bound = [l2_bound(v['items']) for v in data.values()]
    # Notebook output: best fit 2067.0 and FunSearch 2001.4 mean bins, bound 1987.8 (3.98% / 0.68%).
    assert np.mean(bf) == 2067.0 and np.mean(fs) == 2001.4 and np.mean(bound) == 1987.8


def test_bounds_and_generator_agree_with_the_problem_adapter():
    spec = importlib.util.spec_from_file_location('bpo', ROOT / 'problems' / 'bin_packing_online' / 'verify.py')
    verify = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(verify)
    assert weibull_items(7, 500, namespace=verify._SALT) == list(verify.items_for(7, 500))
    rng = random.Random(2)
    for _ in range(50):
        items = [rng.randint(1, 100) for _ in range(rng.randint(1, 300))]
        assert l2_bound(items) == verify.l2_bound(items) >= l1_bound(items)
