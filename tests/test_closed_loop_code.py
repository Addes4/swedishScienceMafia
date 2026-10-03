import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from falsify import code_eval as ce
from falsify.closed_loop_code import BEST_FIT_CODE, DEFAULTS, FUNSEARCH_PATH, LocalExecutor, run_one, user_prompt
from falsify.funsearch_heuristics import funsearch_weibull
from falsify.llm import MockClient, Proposer, SpendLedger
from falsify.longpack import pack_priority, weibull_items
from falsify.memory import TokenFitter
from falsify.memory_code import memory_section, short_error

ROOT = Path(__file__).resolve().parents[1]
FUNSEARCH = FUNSEARCH_PATH.read_text()
SMALL = {**DEFAULTS, 'fixed_instances': 2, 'items': 600, 'windows': 10, 'window': 30, 'shrink_trials': 120,
         'mining_seconds': 30}


def write(tmp, name, code):
    path = Path(tmp) / f'{name}.py'
    path.write_text(code)
    return path


class SandboxTests(unittest.TestCase):
    def test_gate_process_matches_native_and_funsearch_evaluator(self):
        items = weibull_items(5, 800, 'test')
        with tempfile.TemporaryDirectory() as tmp:
            bf, assign, _ = ce.pack_fresh(write(tmp, 'bf', BEST_FIT_CODE), items, 30)
            native, native_assign = ce.best_fit(items, True)
            self.assertEqual(bf, native)
            self.assertEqual(ce.packing_hash(assign), ce.packing_hash(native_assign))
            fs, _, _ = ce.pack_fresh(write(tmp, 'fs', FUNSEARCH), items, 30)
            self.assertEqual(fs, pack_priority(funsearch_weibull, items))

    def test_persistent_packer_reloads_module_state_per_instance(self):
        stateful = ('import numpy as np\nSEEN = []\n\ndef priority(item, bins):\n    SEEN.append(item)\n'
                    '    return -(bins - item) if len(SEEN) < 3 else (bins - item)\n')
        items = [30, 40, 20, 50, 60, 10, 35]
        with tempfile.TemporaryDirectory() as tmp:
            path = write(tmp, 'stateful', stateful)
            packer = ce.PersistentPacker(path)
            try:
                first, second = packer.pack(items), packer.pack(items)
            finally:
                packer.close()
            fresh = ce.pack_fresh(path, items, 30)
        self.assertEqual(first, second)
        self.assertEqual(first[0], fresh[0])

    def test_static_rejection_runtime_errors_and_timeouts(self):
        cfg = {**SMALL, 'timeout_s': 3}
        payload = {'incumbent_code': None, 'fixed': [['t', 1, 300]], 'probe': ['t', 2, 60], 'cfg': cfg}
        r = ce.assess({**payload, 'code': 'import subprocess\ndef priority(item, bins):\n    return bins'})
        self.assertEqual((r['status'], r['error']), ('static', ce.GENERIC_REJECTION))
        r = ce.assess({**payload, 'code': 'def priority(item, bins):\n    raise ValueError("boom")\n'})
        self.assertEqual(r['status'], 'error')
        self.assertEqual(short_error(r['error']), 'ValueError: boom')
        slow = 'import time\ndef priority(item, bins):\n    time.sleep(1)\n    return -(bins - item)\n'
        r = ce.assess({**payload, 'code': slow})
        self.assertEqual(r['status'], 'error')
        self.assertIn('timed out', r['error'])

    def test_counterexamples_are_short_verified_and_really_lose(self):
        payload = {'code': FUNSEARCH, 'incumbent_code': None, 'fixed': [['t', 3, 600]],
                   'probe': ['t', 4, 300], 'cfg': SMALL}
        r = ce.assess(payload)
        self.assertEqual(r['status'], 'ok')
        cxs = r['mining']['incumbent']['counterexamples']
        self.assertTrue(cxs)
        for cx in cxs:
            self.assertLessEqual(len(cx['items']), SMALL['max_counterexample_items'])
            self.assertTrue(cx['verified_fresh'])
            self.assertEqual(cx['candidate_bins'], pack_priority(funsearch_weibull, cx['items']))
            self.assertEqual(cx['reference_bins'], ce.best_fit(cx['items']))
            self.assertGreater(cx['candidate_bins'], cx['reference_bins'])
        # Against a non-best-fit incumbent, both references are mined.
        r2 = ce.assess({**payload, 'code': BEST_FIT_CODE, 'incumbent_code': FUNSEARCH})
        self.assertEqual(set(r2['mining']), {'incumbent', 'best_fit'})
        self.assertEqual(r2['mining']['best_fit']['losses'], 0)

    def test_divergence_handles_new_bins_and_relabelling(self):
        d = ce.divergence([39, 16], [0, 7], [0, 0])
        self.assertTrue(d['candidate_new'])
        self.assertEqual((d['index'], d['reference_free']), (1, 61))
        self.assertIsNone(ce.divergence([10, 20], [3, 9], [0, 1]))


class LoopTests(unittest.TestCase):
    def run_arm(self, arm, tmp, seed=2, calls=4):
        ledger = SpendLedger(Path(tmp) / 'usage.jsonl', cap_usd=1)
        proposer = Proposer(ledger, client=MockClient(seed=seed), max_tokens=2048)
        cfg = {**SMALL, 'calls': calls}
        return run_one(seed, arm, proposer, LocalExecutor(), cfg, Path(tmp) / f'{arm}.json.gz')

    def test_mock_runs_promotion_rule_no_op_and_memory_budget(self):
        with tempfile.TemporaryDirectory() as tmp:
            traces = {arm: self.run_arm(arm, tmp) for arm in ('none', 'prose', 'executable')}
        for arm, t in traces.items():
            self.assertTrue(t['complete'])
            inc_total = sum(t['fixed_best_fit_bins'])
            for r in t['history']:
                self.assertIn('A proposal that packs every fixed-suite instance exactly like', r['user_prompt'])
                self.assertLessEqual(r['memory']['tokens'], SMALL['memory_token_budget'])
                if r['status'] == 'ok':
                    self.assertEqual(r['promoted'], r['fixed']['total_bins'] < inc_total)
                    if r['promoted']:
                        inc_total = r['fixed']['total_bins']
        self.assertEqual(traces['none']['history'][-1]['memory']['tokens'], 0)
        # Same seed: identical fixed suites across arms.
        self.assertEqual(traces['none']['fixed_best_fit_bins'], traces['executable']['fixed_best_fit_bins'])

    def test_memory_arms_show_different_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            t = self.run_arm('executable', tmp, seed=3, calls=5)
        hist = t['history']
        fitter = TokenFitter(lambda text, tag: len(text) // 3, 1500)
        inc = next((r for r in reversed(hist) if r.get('promoted')), None)
        prose = memory_section('prose', hist, inc, fitter, SMALL['windows'], SMALL['window'], 8, 't')
        execu = memory_section('executable', hist, inc, fitter, SMALL['windows'], SMALL['window'], 8, 't')
        self.assertNotIn('Input A', prose['text'])
        if any(r['status'] == 'ok' and r['mining']['incumbent']['counterexamples'] for r in hist if not r['promoted']):
            self.assertIn('Input A', execu['text'])
        self.assertLessEqual(execu['counterexamples'], 8)

    def test_user_prompt_shows_incumbent_code_and_scores(self):
        inc = {'name': 'best_fit', 'code': BEST_FIT_CODE, 'call': None, 'bins': [10, 12], 'best_fit_bins': [10, 12]}
        text = user_prompt(inc, 0, DEFAULTS, 11.0, 10.0, '')
        self.assertIn('return -(bins - item)', text)
        self.assertIn('+0, +0', text)


class CliTests(unittest.TestCase):
    def test_help_and_mock_cli_run_then_audit(self):
        help_text = subprocess.run([sys.executable, '-m', 'falsify.closed_loop_code', '--help'], cwd=ROOT,
                                   capture_output=True, text=True, check=True).stdout
        self.assertIn('audit', help_text)
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / 'study'
            run = [sys.executable, '-m', 'falsify.closed_loop_code', 'run', '--out', str(out), '--seeds', '1', '2',
                   '--calls', '3', '--cap-usd', '1', '--mock', '--workers', '3', '--items', '400',
                   '--fixed-instances', '2', '--windows', '8', '--audit-instances', '40', '--diagnostic-instances', '2']
            audit = [sys.executable, '-m', 'falsify.closed_loop_code', 'audit', '--out', str(out)]
            subprocess.run(run + ['--arms', 'none', 'prose'], cwd=ROOT, check=True, capture_output=True)
            refused = subprocess.run(audit, cwd=ROOT, capture_output=True, text=True)
            self.assertNotEqual(refused.returncode, 0)  # an arm is missing, so the audit must refuse
            subprocess.run(run + ['--arms', 'executable'], cwd=ROOT, check=True, capture_output=True)
            wrong = subprocess.run(audit + ['--expect-seeds', '1', '2', '3'], cwd=ROOT, capture_output=True)
            self.assertNotEqual(wrong.returncode, 0)
            subprocess.run(audit + ['--expect-seeds', '1', '2'], cwd=ROOT, check=True, capture_output=True)
            summary = json.loads((out / 'summary.json').read_text())
            self.assertEqual(set(summary['arms']), {'none', 'prose', 'executable'})
            self.assertEqual(summary['audit_instances'], 40)
            fs = summary['references']['funsearch_weibull']
            # At 400 items FunSearch's heuristic is still behind best-fit; only check the row is complete.
            self.assertEqual(fs['wins'] + fs['ties'] + fs['losses'], 40)
            self.assertIn('no_op_fraction', summary['arms']['prose'])
            self.assertTrue(any(c['comparison'] == 'executable - prose' for c in summary['comparisons']))


if __name__ == '__main__':
    unittest.main()
