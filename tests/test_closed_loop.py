import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from falsify.backends import FEATURE_KEYS, WeightsBackend, first_divergence, shrink_failure
from falsify.closed_loop import DEFAULTS, harness_seed, run_one
from falsify.core import read_json
from falsify.llm import BudgetExceeded, MockClient, Proposer, SpendLedger, prior_spend, worst_case_cost
from falsify.memory import TokenFitter, memory_section

ROOT = Path(__file__).resolve().parents[1]
# The Codex pilot's reserve-quarter proposal (12 features) and its counterexample.
RESERVE_QUARTER = [-0.2, 0, 0.05, 1, -0.1, 0, 0, -1.5, 0, 0, 0, 0] + [0.0] * 8


def as_obj(weights):
    return {'name': 'x', 'hypothesis': 'h', 'falsification': 'f', 'weights': dict(zip(FEATURE_KEYS, weights))}


class LedgerTests(unittest.TestCase):
    def test_cap_refuses_before_sending_and_logs_every_attempt(self):
        with tempfile.TemporaryDirectory() as d:
            ledger = SpendLedger(Path(d) / 'usage.jsonl', cap_usd=0.05)
            proposer = Proposer(ledger, client=MockClient(seed=1))
            backend = WeightsBackend()
            calls = 0
            with self.assertRaises(BudgetExceeded):
                for _ in range(100):
                    proposer.propose(backend.system_prompt(), 'u' * 500, backend.proposal_schema(), 't')
                    calls += 1
            self.assertGreater(calls, 0)
            self.assertLessEqual(ledger.spent, 0.05)
            self.assertEqual(ledger.reserved, 0)
            lines = [json.loads(l) for l in (Path(d) / 'usage.jsonl').read_text().splitlines()]
            self.assertEqual(len(lines), calls)
            self.assertTrue(all(l['charged_usd'] <= l['reserved_usd'] for l in lines))

    def test_total_cap_counts_earlier_spend_but_not_mock(self):
        with tempfile.TemporaryDirectory() as d:
            old = Path(d) / 'old.jsonl'
            old.write_text(json.dumps({'charged_usd': 14.99, 'client': 'anthropic'}) + '\n' +
                           json.dumps({'charged_usd': 5.0, 'client': 'mock'}) + '\n')
            prior = prior_spend([old])
            self.assertAlmostEqual(prior, 14.99)
            ledger = SpendLedger(Path(d) / 'u.jsonl', cap_usd=3, prior_usd=prior, total_cap_usd=15)
            with self.assertRaises(BudgetExceeded):
                ledger.reserve(0.02)
            ledger.reserve(0.005)

    def test_connection_error_is_retried_logged_and_charged_conservatively(self):
        with tempfile.TemporaryDirectory() as d:
            ledger = SpendLedger(Path(d) / 'usage.jsonl', cap_usd=1)
            backend = WeightsBackend()
            proposer = Proposer(ledger, client=MockClient(seed=2, fail_first=1), backoff_s=0)
            reply = proposer.propose(backend.system_prompt(), 'hello', backend.proposal_schema(), 't')
            self.assertEqual(reply['status'], 'ok')
            self.assertEqual([a['status'] for a in reply['attempts']], ['error', 'ok'])
            self.assertTrue(reply['attempts'][0]['charged_is_upper_bound'])
            lines = (Path(d) / 'usage.jsonl').read_text().splitlines()
            self.assertEqual(len(lines), 2)

    def test_worst_case_bound_exceeds_mock_usage(self):
        backend = WeightsBackend()
        client = MockClient(seed=3)
        system, user = backend.system_prompt(), 'x' * 3000
        msg = client.messages.create(model='claude-haiku-4-5', max_tokens=1024, system=system,
                                     messages=[{'role': 'user', 'content': user}])
        actual = (msg.usage.input_tokens * 1 + msg.usage.output_tokens * 5) / 1e6
        self.assertGreater(worst_case_cost('claude-haiku-4-5', system, user, backend.proposal_schema(), 1024), actual)


class BackendTests(unittest.TestCase):
    def test_parse_validates_keys_bounds_and_types(self):
        b = WeightsBackend()
        self.assertEqual(b.parse(as_obj(b.baseline['weights'])), b.baseline)
        bad = [dict(as_obj([0] * 20), weights={k: 0 for k in FEATURE_KEYS[:19]}),
               as_obj([0] * 19 + [12.5]), as_obj([0] * 19 + [float('nan')]), as_obj([0] * 19 + [True])]
        for obj in bad:
            with self.assertRaises(ValueError):
                b.parse(obj)

    def test_known_counterexample_divergence_and_shrink(self):
        b = WeightsBackend()
        policy = {'weights': RESERVE_QUARTER}
        items = [63, 44, 32, 56]
        cb, ca = b.pack(policy, items, True)
        rb, ra = b.pack(b.baseline, items, True)
        self.assertEqual((cb, rb), (3, 2))
        d = first_divergence(items, ca, ra)
        self.assertEqual((d['index'], d['item'], d['candidate_free'], d['reference_free']), (2, 32, 56, 37))
        # A longer failing input: shrinking keeps it failing and makes it 1-minimal.
        padded = [36, 39, 39, 63, 35, 29, 44, 32, 56]
        self.assertGreater(b.pack(policy, padded), b.pack(b.baseline, padded))
        small, work = shrink_failure(b, padded, policy, budget=4000)
        self.assertGreater(b.pack(policy, small), b.pack(b.baseline, small))
        self.assertLess(work, 4000)
        self.assertLess(len(small), len(padded))
        for i in range(len(small)):
            trial = small[:i] + small[i + 1:]
            self.assertLessEqual(b.pack(policy, trial), b.pack(b.baseline, trial))


def fake_record(call, counterexamples=True, promoted=False):
    cx = {'items': [63, 44, 32, 56], 'candidate_bins': 3, 'reference_bins': 2,
          'candidate_packing': [[63], [44, 32], [56]], 'reference_packing': [[63, 32], [44, 56]],
          'divergence': {'index': 2, 'item': 32, 'candidate_free': 56, 'reference_free': 37}}
    return {'call': call, 'status': 'ok', 'promoted': promoted, 'name': f'idea{call}',
            'hypothesis': 'Reserve room for large items.', 'policy': {'weights': RESERVE_QUARTER},
            'fixed': {'mean_excess': 0.05, 'wins': 1, 'losses': 9, 'ties': 390,
                      'by_family': {'uniform': 0.1, 'small': 0.0}},
            'probe': {'losses': 3}, 'same_as_incumbent': False,
            'counterexamples': [cx, cx] if counterexamples else []}


class MemoryTests(unittest.TestCase):
    def setUp(self):
        self.render = WeightsBackend().render
        self.history = [fake_record(i) for i in range(20)]
        self.count = lambda text, tag: len(text) // 3

    def section(self, arm, budget=600):
        fitter = TokenFitter(self.count, budget)
        return memory_section(arm, self.history, None, self.render, fitter, 400, 100, 8, 't')

    def test_arms_differ_only_in_kind_of_evidence_and_respect_budget(self):
        none, prose, execu = self.section('none'), self.section('prose'), self.section('executable')
        self.assertEqual(none['text'], '')
        for m in (prose, execu):
            self.assertLessEqual(m['tokens'], 600)
            self.assertGreater(m['tokens'], 400)
        self.assertNotIn('[63, 44, 32, 56]', prose['text'])
        self.assertIn('[63, 44, 32, 56]', execu['text'])
        self.assertIn('roomier bin', prose['text'])
        self.assertLessEqual(execu['counterexamples'], 8)
        self.assertTrue(execu['text'].index('proposal 20') < execu['text'].index('proposal 19')
                        if 'proposal 19' in execu['text'] else True)
        self.assertIn('Proposal 20', prose['text'])

    def test_promoted_and_counterexample_free_proposals(self):
        self.history = [fake_record(0, counterexamples=False), fake_record(1, promoted=True)]
        execu, prose = self.section('executable'), self.section('prose')
        self.assertEqual(execu['entries'], 0)
        self.assertIn('None yet.', execu['text'])
        self.assertEqual(prose['entries'], 1)


class LoopTests(unittest.TestCase):
    def test_paired_harness_promotion_rule_and_trace_contents(self):
        backend = WeightsBackend()
        cfg = {**DEFAULTS, 'calls': 5, 'fixed_cases': 60, 'probe_cases': 20}
        with tempfile.TemporaryDirectory() as d:
            traces = {}
            for arm in ('none', 'executable'):
                ledger = SpendLedger(Path(d) / 'usage.jsonl', cap_usd=1)
                proposer = Proposer(ledger, client=MockClient(seed=4))
                traces[arm] = run_one(7, arm, backend, proposer, cfg, Path(d) / f'{arm}.json.gz')
            self.assertEqual(read_json(Path(d) / 'none.json.gz')['run_id'], 'none-s7')
        for t in traces.values():
            self.assertTrue(t['complete'])
            self.assertEqual(len(t['history']), 5)
            best = t['history'][0]['user_prompt'].split('## This call')[0]
            self.assertIn('w00_gap=-1', best)
            incumbent_total = None
            for r in t['history']:
                self.assertIn('user_prompt', r)
                self.assertIn('response_text', r)
                if r['status'] == 'ok':
                    total = r['fixed']['total_bins']
                    if incumbent_total is None:
                        incumbent_total = sum(backend.evaluate(backend.baseline, backend.cases(
                            harness_seed(7, 'fixed'), 60, 'train')))
                    self.assertEqual(r['promoted'], total < incumbent_total)
                    if r['promoted']:
                        incumbent_total = total
        # Same seed, different arms: identical starting prompt apart from the memory section.
        heads = [t['history'][0]['user_prompt'].split('## Counterexamples')[0].rstrip()
                 for t in traces.values()]
        self.assertEqual(heads[0].replace('\n\nPropose one policy.', ''), heads[1])

    def test_budget_stop_marks_run_incomplete(self):
        backend = WeightsBackend()
        cfg = {**DEFAULTS, 'calls': 50, 'fixed_cases': 20, 'probe_cases': 10}
        with tempfile.TemporaryDirectory() as d:
            ledger = SpendLedger(Path(d) / 'usage.jsonl', cap_usd=0.03)
            proposer = Proposer(ledger, client=MockClient(seed=5))
            t = run_one(1, 'prose', backend, proposer, cfg, Path(d) / 't.json.gz')
            self.assertFalse(t['complete'])
            self.assertTrue(t['stopped'].startswith('budget'))
            self.assertLessEqual(ledger.spent, 0.03)

    def test_cli_mock_runs_then_audit_from_hashed_seed(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / 'study'
            run = [sys.executable, '-m', 'falsify.closed_loop', 'run', '--out', str(out), '--seeds', '1', '2',
                   '--calls', '3', '--cap-usd', '1', '--mock', '--workers', '2']
            audit = [sys.executable, '-m', 'falsify.closed_loop', 'audit', '--out', str(out)]
            subprocess.run(run + ['--arms', 'none', 'executable'], check=True, capture_output=True, cwd=ROOT)
            subprocess.run(run + ['--arms', 'prose'], check=True, capture_output=True, cwd=ROOT)
            (out / 'runs' / 'prose-s2.json.gz').rename(out / 'hold.gz')
            refused = subprocess.run(audit, capture_output=True, text=True, cwd=ROOT)
            self.assertNotEqual(refused.returncode, 0)
            (out / 'hold.gz').rename(out / 'runs' / 'prose-s2.json.gz')
            subprocess.run(audit, check=True, capture_output=True, cwd=ROOT)
            summary = json.loads((out / 'summary.json').read_text())
            self.assertEqual(set(summary['arms']), {'none', 'prose', 'executable'})
            self.assertEqual(summary['audit_cases'], 1600)
            self.assertTrue(any(c['comparison'] == 'executable - prose' for c in summary['comparisons']))
            self.assertTrue(re.fullmatch(r'[0-9a-f]{64}', summary['trace_digest']))
            self.assertEqual(summary['arms']['none']['memory_tokens_mean'], 0)
            usage = (out / 'usage.jsonl').read_text().splitlines()
            self.assertTrue(all(json.loads(l)['client'] == 'mock' for l in usage))


if __name__ == '__main__':
    unittest.main()
