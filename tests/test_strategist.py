import copy
import random
import unittest
from strategist.controller import OPS, Adaptive, Fixed, Patience, shuffled
from strategist.problems import BENCHMARKS, LABS, Heilbronn
from strategist.search import COSTS, Run
from strategist.stats import holm, sign_test


def labs_energy(bits, n):
    s = [1 if bits >> i & 1 else -1 for i in range(n)]
    return sum(sum(s[i]*s[i+k] for i in range(n-k))**2 for k in range(1, n))


class ProblemTests(unittest.TestCase):
    def test_labs_matches_definition(self):
        rng, p = random.Random(3), LABS(23)
        for _ in range(50):
            x = p.random(rng)
            self.assertEqual(p.score(x), labs_energy(x, 23))
        barker13 = int('1111100110101'[::-1], 2)
        self.assertEqual(LABS(13).score(barker13), 6)

    def test_heilbronn_area(self):
        self.assertAlmostEqual(Heilbronn(3).score(((0, 0), (1, 0), (0, 1))), -.5)

    def test_moves_do_not_mutate_inputs_and_stay_valid(self):
        rng = random.Random(5)
        for name, make in BENCHMARKS.items():
            p = make(0)
            x, y = p.random(rng), p.random(rng)
            frozen = copy.deepcopy((x, y))
            for child in (p.edit(x, rng), p.rewrite(x, rng), p.crossover(x, y, rng)):
                self.assertEqual((x, y), frozen, name)
                self.assertTrue(p.score(child) == p.score(child), name)   # finite and deterministic
            if isinstance(x, tuple) and name == 'heilbronn':
                self.assertEqual(len(p.crossover(x, y, rng)), p.n)


class RunTests(unittest.TestCase):
    def test_budget_determinism_and_shuffled_control(self):
        p = BENCHMARKS['labs'](0)
        a = Run(p, Adaptive(COSTS, 7), 600, 7).run()
        b = Run(p, Adaptive(COSTS, 7), 600, 7).run()
        self.assertLessEqual(a.spent, 600+1e-9)
        self.assertEqual((a.ops, a.f_best), (b.ops, b.f_best))
        c = Run(p, shuffled(a.ops, 7), 600, 7).run()
        self.assertEqual(sorted(c.ops), sorted(a.ops))
        self.assertAlmostEqual(c.spent, a.spent)

    def test_every_arm_starts_from_the_same_solution(self):
        p = BENCHMARKS['nk'](1)
        runs = [Run(p, policy, 10, 1) for policy in (Adaptive(COSTS, 1), Fixed({'edit': 1}, 1, 'e'), Patience(4))]
        self.assertEqual(len({r.f_start for r in runs}), 1)

    def test_resume_returns_to_the_leader(self):
        p = BENCHMARKS['labs'](0)
        run = Run(p, Fixed({'edit': 1}, 0, 'e'), 1000, 0)
        for _ in range(30): run.step()
        best, leader = run.f_best, run.leader_line
        run.policy = Fixed({'restart': 1}, 0, 'r'); run.step()
        self.assertFalse(run.leader and run.f_work != best)
        run.resume()
        self.assertEqual((run.line, run.f_work), (run.leader_line, run.f_best))
        self.assertEqual(run.f_best, min(best, run.f_best))

    def test_fork_is_independent_of_the_original(self):
        p = BENCHMARKS['labs'](2)
        run = Run(p, Adaptive(COSTS, 2), 3000, 2)
        for _ in range(200): run.step()
        state = (run.spent, run.f_best, list(run.ops))
        f1 = run.fork(copy.deepcopy(run.policy), 'x', 200).run()
        f2 = run.fork(copy.deepcopy(run.policy), 'x', 200).run()
        self.assertEqual((run.spent, run.f_best, run.ops), state)
        self.assertEqual((f1.ops, f1.f_best), (f2.ops, f2.f_best))
        self.assertLessEqual(f1.spent, state[0]+200+1e-9)


class FakeRun:
    def __init__(self, leader, stall, leader_stall=0, spent=1000., rate=1e-3):
        self.leader, self.stall, self.leader_stall, self.spent, self.rate = leader, stall, leader_stall, spent, rate
    def progress_rate(self): return self.rate


class ControllerTests(unittest.TestCase):
    def test_leaves_a_stagnant_leader_but_not_a_productive_one(self):
        policy = Adaptive(COSTS, 0)
        for _ in range(300): policy.update('lead/fresh', 'edit', 1.2, .05)        # every edit improves
        for _ in range(300): policy.update('lead/frozen', 'edit', 1.2, 0.)        # edits never improve
        excursions_pay = dict(rate=.01)                                             # 1% progress per cost unit
        self.assertIsNone(policy.leaves('lead/fresh', FakeRun(True, 0, **excursions_pay)))
        # Rewrite and crossover are untried, so their optimistic prior keeps it on the line for now.
        self.assertIsNone(policy.leaves('lead/frozen', FakeRun(True, 300, **excursions_pay)))
        for _ in range(300):
            for op in ('edit', 'rewrite', 'crossover'): policy.update('lead/frozen', op, COSTS[op], 0.)
        self.assertEqual(policy.leaves('lead/frozen', FakeRun(True, 300, **excursions_pay)), 'restart')

    def test_failed_excursions_make_it_more_patient_until_forgotten(self):
        policy = Adaptive(COSTS, 0)
        for _ in range(100): policy.update('lead/stuck', 'edit', 1.2, 0.)
        before = policy.explore_rate(FakeRun(True, 20))
        policy.excursion_done(0., 400., 1000.)
        self.assertLess(policy.explore_rate(FakeRun(True, 20)), before)
        self.assertAlmostEqual(policy.explore_rate(FakeRun(True, 20, spent=1e6)), before)

    def test_excursion_gets_the_leaders_patience(self):
        policy = Adaptive(COSTS, 0)
        self.assertIsNone(policy.leaves('trail/stuck', FakeRun(False, 20, leader_stall=64)))
        self.assertEqual(policy.leaves('trail/stuck', FakeRun(False, 64, leader_stall=64)), 'resume')

    def test_moves_are_only_from_the_allowed_set(self):
        p = BENCHMARKS['heilbronn'](0)
        run = Run(p, Adaptive(COSTS, 3, moves=('edit', 'rewrite')), 800, 3).run()
        self.assertNotIn('crossover', run.ops)
        self.assertTrue(set(run.ops) <= set(OPS) | {'resume'})


class StatsTests(unittest.TestCase):
    def test_sign_test_and_holm(self):
        self.assertAlmostEqual(sign_test(6, 0), 2/64)
        self.assertEqual(sign_test(3, 3), 1.)
        self.assertEqual(holm([.01, .04, .03]), [.03, .06, .06])


if __name__ == '__main__': unittest.main()
