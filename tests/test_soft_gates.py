import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from falsify.soft_gates import ARMS, gate_decision, run_seed

class SoftGateTests(unittest.TestCase):
    def test_isolated_loss_can_pass_with_neutral_validation(self):
        losses=[1]+[0]*15;validation=[0]*64
        self.assertFalse(gate_decision('strict',0,losses,validation)['pass'])
        self.assertTrue(gate_decision('loss_budget',0,losses,validation)['pass'])
        self.assertTrue(gate_decision('validated_budget',0,losses,validation)['pass'])

    def test_severe_or_repeated_losses_stay_blocked(self):
        for losses in [[2]+[0]*15,[1,1,1]+[0]*13]:
            for mode in ARMS:
                self.assertFalse(gate_decision(mode,-1,losses,[-1]*64)['pass'])

    def test_fresh_validation_can_reject_training_overfit(self):
        losses=[1]+[0]*15
        self.assertTrue(gate_decision('loss_budget',-1,losses,[1]+[0]*63)['pass'])
        self.assertFalse(gate_decision('validated_budget',-1,losses,[1]+[0]*63)['pass'])

    def test_second_loss_needs_compensating_evidence(self):
        losses=[1,1]+[0]*14
        self.assertFalse(gate_decision('validated_budget',0,losses,[0]*64)['pass'])
        self.assertTrue(gate_decision('validated_budget',0,losses,[-1]+[0]*63)['pass'])

    def test_matched_budgets_common_trajectory_and_reproduction(self):
        from falsify.gated_search import run_seed as strict_run
        r=run_seed(3,3);s=run_seed(3,3);old=strict_run(3,3)
        self.assertEqual(r['history'],s['history'])
        self.assertEqual(r['candidate_stream_sha256'],old['candidate_stream_sha256'])
        self.assertEqual({x['executions'] for x in r['counts'].values()},{3*544})
        for h in r['history']:
            for a in ARMS:
                idx=h['evaluation'][a+'_selected']
                if idx is not None:self.assertTrue(h['evaluation'][a][idx]['gate']['pass'])

    def test_cli_audit_and_saved_configuration_resume(self):
        with tempfile.TemporaryDirectory() as directory:
            out=Path(directory)/'study'
            command=[sys.executable,'-m','falsify.soft_gates','--out',str(out)]
            subprocess.run(command+['--seeds','2','--generations','2','--audit-cases','8','--diagnostic-cases','8'],check=True,capture_output=True)
            result=json.loads((out/'summary.json').read_text())
            (out/'summary.json').unlink()
            subprocess.run(command+['--resume-audit'],check=True,capture_output=True)
            self.assertEqual(result,json.loads((out/'summary.json').read_text()))

if __name__=='__main__':unittest.main()
