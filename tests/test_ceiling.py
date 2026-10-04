"""bp-ceiling-v1 search harness: matched budgets, determinism, and separation of train and audit."""
import random

from falsify.ceiling import (AUDIT_NAMESPACE, REGIMES, TRAIN_NAMESPACE, audit_cases, compare, hill_climb, mutate,
                             regime_cases, run_search, start_weights, training_cases)
from falsify.contextual import CONTEXT_BEST_FIT, mutate_contextual
from falsify.longpack import pack_rule


def test_mutation_is_mutate_contextual_for_twenty_weights():
    for seed in range(50):
        a, b = random.Random(seed), random.Random(seed)
        assert mutate(CONTEXT_BEST_FIT, a) == mutate_contextual(CONTEXT_BEST_FIT, b)


def test_every_regime_charges_the_same_item_steps():
    steps = {r: sum(len(c) for c in training_cases(r, 0)) for r in REGIMES}
    assert set(steps.values()) == {20000}


def test_training_and_audit_instances_never_overlap():
    assert TRAIN_NAMESPACE != AUDIT_NAMESPACE
    train = {c.items for s in range(3) for c in training_cases('weibull500', s)}
    assert not train & {c.items for c in regime_cases('weibull500', AUDIT_NAMESPACE, 'final', 40)}
    families = {c.family for c in audit_cases('falsify80')}
    assert len(families) == 8


def test_hill_climb_is_deterministic_and_never_worse_than_best_fit_on_training():
    cases = training_cases('weibull500', 3)[:6]
    a = hill_climb(cases, 'linear21', 3, 40)
    b = hill_climb(cases, 'linear21', 3, 40)
    assert a == b and a['evaluations'] == 40
    assert a['train_excess_bins'] <= 0
    assert a['reference_bins'] == sum(pack_rule(c, 'best_fit') for c in cases)


def test_both_optimizers_spend_exactly_the_budget():
    for optimizer in ('hc', 'cmaes'):
        run = run_search('falsify80', 'linear20', optimizer, 0, 60)
        assert run['evaluations'] == 60 and run['search_item_steps'] == 60 * 20000
        assert len(run['weights']) == 20 and run['train_excess_bins'] <= 0
    assert start_weights('linear21')[:20] == list(CONTEXT_BEST_FIT)


def test_compare_reports_percentage_points_against_best_fit():
    class C:
        family = 'weibull'
    cases = [C(), C()]
    out = compare([11, 10], [10, 10], [10, 10], cases, ['weibull'])
    assert abs(out['delta_pp'] - 5.0) < 1e-12 and out['losses'] == 1 and out['ties'] == 1


def test_exact_optimum_matches_brute_force_on_tiny_instances():
    import itertools
    from falsify.optimum import optimal_bins

    def brute(items, cap):
        for k in range(1, len(items) + 1):
            for assignment in itertools.product(range(k), repeat=len(items)):
                loads = [0] * k
                for b, x in zip(assignment, items):
                    loads[b] += x
                if max(loads) <= cap:
                    return k

    rng = random.Random(9)
    for _ in range(25):
        items = [rng.randint(15, 70) for _ in range(rng.randint(2, 7))]
        assert optimal_bins(items) == (brute(items, 100), brute(items, 100))
