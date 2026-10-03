"""Evaluate a recorded Codex candidate batch and extract executable counterexamples."""
import argparse
import json
import statistics
from pathlib import Path
from .core import BEST_FIT, TRAIN_FAMILIES, pack, suite, write_json

def shrink(items, weights, budget=1000):
    """Greedy deletion; preserves candidate > best-fit, not a proof of global minimality."""
    current=list(items)
    executions=0
    changed=True
    while changed and executions+2<=budget:
        changed=False
        for i in range(len(current)):
            trial=current[:i]+current[i+1:]
            candidate=pack(trial,weights); ref=pack(trial,BEST_FIT); executions+=2
            if candidate>ref:
                current=trial;changed=True;break
            if executions+2>budget:break
    return current,executions

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--candidates',default='experiments/codex_candidates.json')
    parser.add_argument('--out',default='experiments/codex-pilot-v1')
    args=parser.parse_args()
    candidates=json.loads(Path(args.candidates).read_text())['candidates']
    cases=suite(431,1000,TRAIN_FAMILIES)
    refs=[pack(x['items']) for x in cases]
    results=[]
    for c in candidates:
        gaps=[pack(x['items'],c['weights'])-ref for x,ref in zip(cases,refs)]
        failures=sorted(range(len(cases)),key=lambda i:gaps[i],reverse=True)
        examples=[]
        for i in failures[:2]:
            if gaps[i]<=0:continue
            small,work=shrink(cases[i]['items'],c['weights'])
            cb,ct=pack(small,c['weights'],True);rb,rt=pack(small,BEST_FIT,True)
            examples.append({'family':cases[i]['family'],'original_gap':gaps[i],
                'items':small,'candidate_bins':cb,'reference_bins':rb,
                'candidate_assignments':ct,'reference_assignments':rt,
                'shrink_packing_executions':work})
        r={**c,'mean_excess_bins':statistics.mean(gaps),'wins':sum(g<0 for g in gaps),
           'ties':sum(g==0 for g in gaps),'losses':sum(g>0 for g in gaps),
           'by_family':{f:statistics.mean(g for x,g in zip(cases,gaps) if x['family']==f) for f in TRAIN_FAMILIES},
           'counterexamples':examples,'candidate_packing_executions':len(cases)}
        results.append(r)
        print(c['name'],r['mean_excess_bins'], 'wins',r['wins'],'losses',r['losses'],flush=True)
    write_json(Path(args.out)/'results.json',{'provenance':'Codex-guided exploratory pilot; no final held-out claim.',
        'cases':len(cases),'reference_packing_executions':len(cases),'results':results})

if __name__=='__main__':main()
