import random
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from falsify.core import BEST_FIT, pack, suite
from falsify.contextual import CONTEXT_BEST_FIT, PreparedCase, anchors, evaluate_cases, mutate_contextual, pack_contextual
from falsify.gated_search import allowed, run_seed

def independent_context_reference(items,weights):
    """Slow Python specification, without native prefix sums or distance caches."""
    remaining=[];past=[];trace=[]
    for item in items:
        scores=[]
        for b,r in enumerate(remaining):
            if r<item:continue
            g=r-item;x=g/100
            denominator=len(past)+25
            fit=(sum(v<=g for v in past)+.25*g)/denominator
            before=(sum(v<=r for v in past)+.25*r)/denominator
            near=(sum(abs(v-g)<=2 for v in past)+.25*len(range(max(1,g-2),min(100,g+2)+1)))/denominator
            distance=(min(abs(g-v) for v in past) if past else abs(g-50.5))/100
            past_mean=(sum(past)+1262.5)/denominator
            f=[x,x*x,1/(g+1),g==0,0<g<10,0<g<item,g>=item,
               abs(x-.25),abs(x-.5),abs(x-.75),0<g<33,0<g<50,
               x*(1-fit),(g>0)*(1-fit),near,distance,fit,x*fit,before-fit,x*past_mean/100]
            scores.append((sum(a*w for a,w in zip(f,weights)),b))
        if scores:
            chosen=max(scores,key=lambda x:x[0])[1]
        else:
            chosen=len(remaining);remaining.append(100)
        remaining[chosen]-=item;trace.append(chosen);past.append(item)
    return len(remaining),trace

class ContextualTests(unittest.TestCase):
    def test_cli_finishes_audit_and_resumes_from_saved_config(self):
        with tempfile.TemporaryDirectory() as directory:
            out=Path(directory)/'study'
            command=[sys.executable,'-m','falsify.gated_search','--out',str(out)]
            subprocess.run(command+['--seeds','2','--generations','2','--audit-cases','8','--diagnostic-cases','8'],check=True,capture_output=True)
            before=json.loads((out/'summary.json').read_text())
            (out/'summary.json').unlink()
            subprocess.run(command+['--resume-audit'],check=True,capture_output=True)
            self.assertEqual(before,json.loads((out/'summary.json').read_text()))

    def test_native_context_scoring_matches_independent_specification(self):
        rng=random.Random(431)
        for case in suite(91,20):
            weights=[rng.uniform(-3,3) for _ in range(20)]
            self.assertEqual(pack_contextual(case['items'],weights,True),
                independent_context_reference(case['items'],weights))

    def test_zero_context_weights_match_original_packer(self):
        rng=random.Random(10)
        for x in suite(19,100):
            weights=[rng.uniform(-2,2) for _ in range(12)]
            self.assertEqual(pack(x['items'],weights,True),pack_contextual(x['items'],weights+[0.]*8,True))

    def test_future_suffix_cannot_change_prefix_decisions(self):
        prefix=[63,44,32,11,25,9,23]
        for candidate in anchors():
            a=pack_contextual(prefix+[56,10,20],candidate['weights'],True)[1]
            b=pack_contextual(prefix+[1,1,1,1],candidate['weights'],True)[1]
            self.assertEqual(a[:len(prefix)],b[:len(prefix)])

    def test_context_mutations_preserve_capacity_and_items(self):
        rng=random.Random(12)
        for case in suite(18,100):
            weights=mutate_contextual(rng.choice(anchors())['weights'],rng)
            bins,trace=pack_contextual(case['items'],weights,True)
            loads=[0]*bins
            for item,b in zip(case['items'],trace):loads[b]+=item
            self.assertEqual(sum(loads),sum(case['items']))
            self.assertTrue(all(0<x<=100 for x in loads))

    def test_prepared_evaluation_matches_public_api(self):
        cases=suite(15,20)
        for candidate in anchors():
            prepared=[PreparedCase(x) for x in cases]
            self.assertEqual(evaluate_cases(prepared,candidate['weights']),
                [pack_contextual(x['items'],candidate['weights']) for x in cases])

    def test_gate_rejects_regression_even_when_fixed_score_improves(self):
        self.assertFalse(allowed(2,3,[3],[2],True))
        self.assertTrue(allowed(2,3,[3],[2],False))
        self.assertTrue(allowed(2,3,[2],[2],True))
        self.assertFalse(allowed(4,3,[2],[2],True))

    def test_common_proposals_matched_budget_and_reproduction(self):
        r=run_seed(3,3);s=run_seed(3,3)
        self.assertEqual(r['history'],s['history'])
        self.assertEqual(r['candidate_stream_sha256'],s['candidate_stream_sha256'])
        self.assertEqual({x['executions'] for x in r['counts'].values()},{3*4*56})
        for h in r['history']:
            for a in ['random_gate','counterexample_gate']:
                i=h['evaluation'][a+'_selected']
                if i is not None:self.assertEqual(h['evaluation'][a][i]['violations'],0)

if __name__=='__main__':unittest.main()
