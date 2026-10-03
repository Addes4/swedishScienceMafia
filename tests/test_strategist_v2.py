import json
import tempfile
import unittest
from pathlib import Path
from strategist import v2
from strategist.controller import Adaptive, AdaptiveV2
from strategist.costs import CostTableError, MEASURED, load
from strategist.problems import BENCHMARKS
from strategist.search import COSTS, Run
from strategist.stats import cluster_interval


class FakeRun:
    def __init__(self, leader, stall, leader_stall=0, spent=1000., rate=1e-3, line=0):
        self.leader, self.stall, self.leader_stall, self.spent, self.rate = leader, stall, leader_stall, spent, rate
        self.line, self.leader_line = line, 0
    def progress_rate(self): return self.rate


class V2ControllerTests(unittest.TestCase):
    def test_defaults_reproduce_v1_move_for_move(self):
        for bench in ('labs', 'heilbronn', 'nk'):
            p = BENCHMARKS[bench](41)
            a = Run(p, Adaptive(COSTS, 41), 1500, 41).run()
            b = Run(p, AdaptiveV2(COSTS, 41, rng_key='adaptive'), 1500, 41).run()
            self.assertEqual((a.ops, a.f_best), (b.ops, b.f_best), bench)

    def test_crossover_starts_locked_and_earns_entry(self):
        policy = AdaptiveV2(COSTS, 0, xo_gate=True)
        self.assertNotIn('crossover', policy.eligible(policy.estimates('lead/stuck')))
        for _ in range(50): policy.update('lead/stuck', 'edit', COSTS['edit'], 0.)
        self.assertNotIn('crossover', policy.eligible(policy.estimates('lead/stuck')))   # no evidence yet
        for _ in range(50):
            policy.update('lead/stuck', 'rewrite', COSTS['rewrite'], 0.)
            policy.update('lead/stuck', 'crossover', COSTS['crossover'], .05)
        self.assertIn('crossover', policy.eligible(policy.estimates('lead/stuck')))
        run = Run(BENCHMARKS['labs'](0), AdaptiveV2(COSTS, 0, xo_gate=True), 300, 0).run()
        self.assertNotIn('crossover', run.ops)                    # never probed, never used
        run = Run(BENCHMARKS['labs'](0), AdaptiveV2(COSTS, 0, xo_gate=True, xo_probe=.1), 600, 0).run()
        self.assertIn('crossover', run.ops)

    def test_excursion_rules(self):
        trail = lambda stall, leader_stall: FakeRun(False, stall, leader_stall=leader_stall)
        inherit, cap, fixed = (AdaptiveV2(COSTS, 0, excursion=e, excursion_len=16) for e in ('inherit', 'cap', 'fixed'))
        self.assertIsNone(inherit.leaves('trail/stuck', trail(20, 100)))
        self.assertEqual(cap.leaves('trail/stuck', trail(16, 100)), 'resume')
        self.assertIsNone(cap.leaves('trail/warm', trail(2, 3)))
        self.assertEqual(cap.leaves('trail/warm', trail(3, 3)), 'resume')
        self.assertIsNone(fixed.leaves('trail/warm', trail(3, 3)))      # fixed ignores a short leader stall
        self.assertEqual(fixed.leaves('trail/slowing', trail(16, 3)), 'resume')

    def _stuck_policy(self, **kw):
        policy = AdaptiveV2(COSTS, 0, **kw)
        for _ in range(300):
            for op in ('edit', 'rewrite', 'crossover'): policy.update('lead/slowing', op, COSTS[op], 0.)
        return policy

    def test_improving_test_needs_a_long_enough_stall(self):
        pays = dict(rate=.01)
        self.assertEqual(self._stuck_policy().leaves('lead/slowing', FakeRun(True, 5, **pays)), 'restart')
        policy = self._stuck_policy(leave_test='improving', window=16)
        self.assertIsNone(policy.leaves('lead/slowing', FakeRun(True, 5, **pays)))
        self.assertEqual(policy.leaves('lead/slowing', FakeRun(True, 16, **pays)), 'restart')

    def test_yield_test_keeps_a_leader_whose_recent_moves_paid(self):
        policy = self._stuck_policy(leave_test='yield', window=8)
        policy.line, policy.keep = 0, (0,)
        policy.update('lead/fresh', 'edit', 1.2, 1.)      # one large recent gain on line 0
        self.assertIsNone(policy.leaves('lead/slowing', FakeRun(True, 5, rate=.01)))
        for _ in range(8): policy.update('lead/slowing', 'edit', 1.2, 0.)
        self.assertEqual(policy.leaves('lead/slowing', FakeRun(True, 5, rate=.01)), 'restart')

    def test_upper_test_needs_more_evidence_than_point(self):
        point, upper = AdaptiveV2(COSTS, 0), AdaptiveV2(COSTS, 0, leave_test='upper', quantile=.99)
        for policy in (point, upper):
            for _ in range(6):
                for op in ('edit', 'rewrite', 'crossover'): policy.update('lead/slowing', op, COSTS[op], 0.)
        run = FakeRun(True, 5, rate=.05)
        self.assertEqual(point.leaves('lead/slowing', run), 'restart')
        self.assertIsNone(upper.leaves('lead/slowing', run))


class CostTableTests(unittest.TestCase):
    def test_named_inline_and_placeholder(self):
        self.assertEqual(load('llm_proxy')[1], COSTS)
        self.assertEqual(set(load('uniform')[1].values()), {0., 1.})
        name, table = load('edit=1,rewrite=3,crossover=2,restart=4')
        self.assertAlmostEqual(table['edit'], 1.2)
        self.assertAlmostEqual(table['restart'], 4.8)
        self.assertEqual(table['resume'], 0.)
        self.assertTrue(MEASURED.exists())
        if json.loads(MEASURED.read_text())['relative']['edit'] is None:
            with self.assertRaises(CostTableError): load('measured')
        with tempfile.TemporaryDirectory() as d:
            path = Path(d)/'t.json'
            path.write_text(json.dumps({'relative': {'edit': 2, 'rewrite': 6, 'crossover': 4, 'restart': 8},
                                        'normalise': False}))
            self.assertEqual(load(str(path))[1]['rewrite'], 6)
        with self.assertRaises(CostTableError): load('edit=1,rewrite=0,crossover=1,restart=1')


class PipelineTests(unittest.TestCase):
    def test_seed_blocks_avoid_v1_blocks(self):
        for block in (v2.DEV, v2.VALIDATION, v2.CONFIRM, v2.FORK_SEEDS): v2.check_seeds(block)
        with self.assertRaises(AssertionError): v2.check_seeds(range(30, 50))
        blocks = [set(b) for b in (v2.DEV, v2.VALIDATION, v2.CONFIRM, v2.FORK_SEEDS)]
        self.assertEqual(sum(map(len, blocks)), len(set().union(*blocks)))

    def test_jobs_are_deterministic_and_matched(self):
        frozen = {'levels': ['gate10', 'cap16', 'improving16']}
        arms, per_bench = v2.confirm_arms(frozen, {'labs': 64})
        job = v2.jobs_for('test', range(3000, 3001), arms, COSTS, curves=True, per_bench=per_bench, benches=('labs',))[0]
        job['budget'] = 300.
        a, b = v2.run_job(job), v2.run_job(job)
        self.assertEqual([r['final'] for r in a], [r['final'] for r in b])
        runs = {r['arm']: r for r in a}
        self.assertEqual(runs['timing_shuffled']['ops'], runs['adaptive_v2']['ops'])
        self.assertTrue(all(r['spent'] <= 300+1e-9 for r in a))
        self.assertEqual(runs['only_xo']['final'], v2.run_job({**job, 'arms': [('x', v2.v2_spec(['gate10', 'inherit', 'point']))]})[0]['final'])

    def test_summary_and_fork_summary(self):
        records = []
        for s in range(6):
            for arm, val in zip(v2.PRIMARY+('adaptive_v2',), (1, 2, 3, 4, 5, 6, 7)):
                records.append({'benchmark': 'labs', 'seed': s, 'arm': arm, 'final': val+s/10,
                                'ops': {'edit': 1, 'restart': 0}})
        summary = v2.summarise(records, benches=('labs',))
        self.assertEqual(summary['labs']['comparisons']['adaptive_v1']['final']['wins'], 6)
        self.assertIn('holm_p', summary['labs']['comparisons']['edits_only']['final'])
        moments = [{'controller': c, 'benchmark': 'labs', 'seed': s, 'leaves_in_run': 3, 'stall': 20, 'spent': 500.,
                    'switch': {'p_improve': .5, 'mean_gain': g}, 'stay': {'p_improve': .5, 'mean_gain': .2}}
                   for s in range(5) for c, g in (('adaptive_v1', .1), ('adaptive_v2', .3))]
        f = v2.summarise_forks(moments, benches=('labs',))['labs']
        self.assertEqual(f['adaptive_v1']['premature_share'], 1.)
        self.assertEqual(f['v2_minus_v1']['premature_share'], -1.)

    def test_cluster_interval_is_wider_when_clusters_are_correlated(self):
        groups = [[float(i)]*10 for i in range(10)]
        lo, hi = cluster_interval(groups, resamples=2000)
        self.assertLess(lo, 4.5); self.assertGreater(hi, 4.5)


class ReportTests(unittest.TestCase):
    def test_results_blocks_are_refreshed_from_tables(self):
        from strategist.report_v2 import refresh_results
        tables = '# t\n\n## Primary comparisons (Holm)\n\n| a |\n|---|\n| 1 |\n\n## Other\n\n| b |\n'
        with tempfile.TemporaryDirectory() as d:
            path = Path(d)/'RESULTS.md'
            path.write_text('intro\n<!-- tables.md: Primary -->\nstale\n<!-- /tables.md -->\nend\n')
            refresh_results(tables, path)
            self.assertEqual(path.read_text(), 'intro\n<!-- tables.md: Primary -->\n| a |\n|---|\n| 1 |\n'
                                               '<!-- /tables.md -->\nend\n')

    def test_measured_table_versions_get_distinct_names(self):
        with tempfile.TemporaryDirectory() as d:
            names = []
            for edit in (1, 2):
                path = Path(d)/f'm{edit}.json'
                path.write_text(json.dumps({'name': 'measured_llm', 'relative':
                                            {'edit': edit, 'rewrite': 3, 'crossover': 2, 'restart': 4}}))
                names.append(load(str(path))[0])
            self.assertTrue(all(n.startswith('measured_llm-') for n in names))
            self.assertNotEqual(*names)


if __name__ == '__main__': unittest.main()
