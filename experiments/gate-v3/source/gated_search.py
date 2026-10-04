"""Common-proposal, matched-budget promotion-gate experiment. No LLM calls."""
import argparse
import hashlib
import random
import shutil
import statistics
import time
from pathlib import Path
from .core import TRAIN_FAMILIES, SHIFT_FAMILIES, identity, suite, write_json
from .contextual import CONTEXT_BEST_FIT, CONTEXT_FEATURES, PreparedCase, anchors, evaluate_cases, mutate_contextual

ARMS=['fixed_only','random_gate','counterexample_gate']

def allowed(fixed_score,incumbent_score,gate_scores,reference_scores,use_gate):
    return fixed_score<=incumbent_score and (not use_gate or all(a<=b for a,b in zip(gate_scores,reference_scores)))

def make_cases(seed,count,families=TRAIN_FAMILIES):
    return [PreparedCase(x) for x in suite(seed,count,families)]

def mean(values):return sum(values)/len(values)

def run_seed(seed,generations):
    fixed=make_cases(610000+seed,24)
    initial=make_cases(620000+seed,16)
    fixed_refs=evaluate_cases(fixed,CONTEXT_BEST_FIT)
    initial_refs=evaluate_cases(initial,CONTEXT_BEST_FIT)
    def entry(case,ref,gap=0,generation=-1):
        return {'case':case,'reference_bins':ref,'gap':gap,'generation':generation,'id':identity(case.items)}
    random_archive=[entry(x,b) for x,b in zip(initial,initial_refs)]
    counter_archive=list(random_archive)
    explorer=list(CONTEXT_BEST_FIT)
    deployed={arm:list(CONTEXT_BEST_FIT) for arm in ARMS}
    deployed_scores={arm:mean(fixed_refs) for arm in ARMS}
    counts={arm:{'promotions':0,'gate_rejections':0,'eligible_proposals':0,'executions':0} for arm in ARMS}
    history=[];reservoir=[];eligible_seen=0
    diagnostic_rng=random.Random(700000+seed)
    candidate_digest=hashlib.sha256()
    anchor_bank=anchors()
    started=time.monotonic()
    for generation in range(generations):
        rng=random.Random(80000000+seed*10000+generation)
        common=[list(CONTEXT_BEST_FIT),list(explorer),mutate_contextual(explorer,rng),
                mutate_contextual(rng.choice(anchor_bank)['weights'],rng)]
        candidate_digest.update(str(common).encode())
        probes=make_cases(900000+seed*1000+generation,8)
        gate_rng=random.Random(100000000+seed*10000+generation)
        random_gate=gate_rng.sample(random_archive,16)
        counter_gate=gate_rng.sample(counter_archive,16)
        matrices={};incoming=[]
        for arm in ARMS:
            gate=counter_gate if arm=='counterexample_gate' else random_gate
            gate_cases=[x['case'] for x in gate]
            gate_refs=[x['reference_bins'] for x in gate]
            evaluated=[]
            for idx,weights in enumerate(common):
                values=evaluate_cases(fixed+gate_cases+probes,weights)
                probe_refs=evaluate_cases(probes,CONTEXT_BEST_FIT)
                counts[arm]['executions']+=len(values)+len(probe_refs)
                score=mean(values[:24])
                violations=sum(a>b for a,b in zip(values[24:40],gate_refs))
                score_eligible=score<=deployed_scores[arm]
                if score_eligible and idx!=0:
                    counts[arm]['eligible_proposals']+=1
                    if violations and arm!='fixed_only':counts[arm]['gate_rejections']+=1
                accepted=allowed(score,deployed_scores[arm],values[24:40],gate_refs,arm!='fixed_only')
                evaluated.append({'fixed_score':score,'violations':violations,'eligible':accepted})
                if arm=='fixed_only':
                    incoming.extend(entry(x,b,a-b,generation) for x,a,b in zip(probes,values[40:],probe_refs))
            matrices[arm]=evaluated
            eligible=[i for i,r in enumerate(evaluated) if r['eligible']]
            selected=None
            if eligible:
                best=min(evaluated[i]['fixed_score'] for i in eligible)
                tied=[i for i in eligible if evaluated[i]['fixed_score']==best]
                # Independent, deterministic selection stream; no effect on proposals.
                selected=random.Random(110000000+seed*10000+generation).choice(tied)
                if common[selected]!=deployed[arm]:counts[arm]['promotions']+=1
                deployed[arm]=list(common[selected]);deployed_scores[arm]=best
            matrices[arm+'_selected']=selected
        fixed_scores=[r['fixed_score'] for r in matrices['fixed_only']]
        for arm in ARMS[1:]:
            assert fixed_scores==[r['fixed_score'] for r in matrices[arm]],'Unmatched proposal evaluations'
        best=min(fixed_scores)
        explorer=list(common[rng.choice([i for i,s in enumerate(fixed_scores) if s==best])])
        for idx,weights in enumerate(common):
            if weights==CONTEXT_BEST_FIT or fixed_scores[idx]>mean(fixed_refs):continue
            eligible_seen+=1
            diagnostic={'generation':generation,'proposal':idx,'weights':list(weights),
                        'fixed_excess_bins':fixed_scores[idx]-mean(fixed_refs),
                        'gate_passes':{a:matrices[a][idx]['violations']==0 for a in ARMS[1:]}}
            if len(reservoir)<24:reservoir.append(diagnostic)
            else:
                replace=diagnostic_rng.randrange(eligible_seen)
                if replace<24:reservoir[replace]=diagnostic
        unique={x['id']:x for x in random_archive+incoming}
        random_archive=list(unique.values())
        if len(random_archive)>64:
            random_archive=random.Random(120000000+seed*10000+generation).sample(random_archive,64)
        unique={x['id']:x for x in counter_archive+incoming}
        # Preserve the greatest observed regression when the same input recurs.
        for x in counter_archive:
            if unique[x['id']]['gap']<x['gap']:unique[x['id']]=x
        counter_archive=sorted(unique.values(),key=lambda x:(x['gap'],x['generation']),reverse=True)[:64]
        history.append({'generation':generation,'proposals':common,'evaluation':matrices,
            'deployed_weights':{a:list(w) for a,w in deployed.items()},
            'deployed_fixed_excess':{a:s-mean(fixed_refs) for a,s in deployed_scores.items()},
            'counterexample_max_gap':max(x['gap'] for x in counter_archive)})
    expected=generations*4*56
    assert all(c['executions']==expected for c in counts.values()),'Unmatched budgets'
    return {'seed':seed,'generations':generations,'weights':deployed,'counts':counts,
        'candidate_stream_sha256':candidate_digest.hexdigest(),'history':history,
        'initialization_executions':40,'item_steps_per_arm':expected*80,
        'diagnostic_sample':reservoir,'diagnostic_eligible_seen':eligible_seen,
        'seconds_all_arms':time.monotonic()-started,
        'counterexample_archive':[{**{k:v for k,v in x.items() if k!='case'},**x['case'].to_json()} for x in counter_archive]}

def evaluate_audit(weights,cases,refs):
    values=evaluate_cases(cases,weights)
    gaps=[a-b for a,b in zip(values,refs)]
    return {'mean_excess_bins':mean(gaps),'wins':sum(x<0 for x in gaps),
        'losses':sum(x>0 for x in gaps),'ties':sum(x==0 for x in gaps),
        'by_family':{f:mean(g for x,g in zip(cases,gaps) if x.family==f) for f in TRAIN_FAMILIES+SHIFT_FAMILIES}}

def bootstrap(differences):
    rng=random.Random(49999)
    draws=sorted(mean(rng.choices(differences,k=len(differences))) for _ in range(10000))
    return [draws[250],draws[9749]]

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--seeds',type=int,default=40)
    parser.add_argument('--generations',type=int,default=400)
    parser.add_argument('--out',default='experiments/gate-v3')
    parser.add_argument('--audit-seed',type=int,default=32452843)
    parser.add_argument('--audit-cases',type=int,default=1600)
    parser.add_argument('--diagnostic-cases',type=int,default=160)
    args=parser.parse_args()
    if args.seeds<2 or not 1<=args.generations<1000 or args.audit_cases<8 or args.diagnostic_cases<8:
        raise SystemExit('Need >=2 seeds, 1..999 generations, and >=8 audit/diagnostic cases')
    out=Path(args.out)
    if out.exists():raise SystemExit('Choose a new output directory')
    out.mkdir(parents=True)
    source=out/'source';source.mkdir()
    for p in Path(__file__).parent.iterdir():
        if p.suffix in ['.py','.cpp']:shutil.copyfile(p,source/p.name)
    write_json(out/'source_hashes.json',{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in source.iterdir()})
    write_json(out/'config.json',{**vars(args),'features':CONTEXT_FEATURES,'anchors':anchors(),
        'diagnostic_seed':49979687,'bootstrap_seed':49999,'llm_used':False})
    final=[];samples=[]
    for seed in range(args.seeds):
        r=run_seed(seed,args.generations)
        write_json(out/f'seed-{seed}.json.gz',r)
        final.append({k:v for k,v in r.items() if k not in ['history','counterexample_archive']})
        samples.extend({'seed':seed,**x} for x in r['diagnostic_sample'])
        print(f'seed={seed} seconds={r["seconds_all_arms"]:.2f} promotions='+str({a:r['counts'][a]['promotions'] for a in ARMS}),flush=True)
    # No audit or diagnostic instances exist until every search is complete.
    cases=make_cases(args.audit_seed,args.audit_cases,TRAIN_FAMILIES+SHIFT_FAMILIES)
    refs=evaluate_cases(cases,CONTEXT_BEST_FIT)
    for r in final:
        r['audit']={a:evaluate_audit(r['weights'][a],cases,refs) for a in ARMS}
    diagnostic_cases=make_cases(49979687,args.diagnostic_cases,TRAIN_FAMILIES+SHIFT_FAMILIES)
    diagnostic_refs=evaluate_cases(diagnostic_cases,CONTEXT_BEST_FIT)
    for s in samples:
        s['audit']=evaluate_audit(s['weights'],diagnostic_cases,diagnostic_refs)
        excess=s['audit']['mean_excess_bins']
        s['empirical_class']='better' if excess<0 else 'worse' if excess>0 else 'tied'
    arm_summary=[]
    for arm in ARMS:
        arm_summary.append({'arm':arm,'seeds':args.seeds,
            'mean_excess_bins':mean([r['audit'][arm]['mean_excess_bins'] for r in final]),
            'mean_promotions':mean([r['counts'][arm]['promotions'] for r in final]),
            'mean_gate_rejections':mean([r['counts'][arm]['gate_rejections'] for r in final]),
            'executions_per_seed':args.generations*4*56,
            'by_family':{f:mean([r['audit'][arm]['by_family'][f] for r in final]) for f in TRAIN_FAMILIES+SHIFT_FAMILIES}})
    comparisons=[]
    for other in ARMS[:2]:
        differences=[r['audit']['counterexample_gate']['mean_excess_bins']-r['audit'][other]['mean_excess_bins'] for r in final]
        comparisons.append({'counterexample_minus':other,'mean':mean(differences),
            'paired_seed_differences':differences,'bootstrap_95_interval':bootstrap(differences)})
    diagnostics={}
    for cls in ['better','worse','tied']:
        sub=[s for s in samples if s['empirical_class']==cls]
        diagnostics[cls]={'n':len(sub),'gate_rejections':{a:sum(not s['gate_passes'][a] for s in sub) for a in ARMS[1:]}}
    write_json(out/'audit_cases.json',[x.to_json() for x in cases])
    write_json(out/'audit.json',final)
    write_json(out/'diagnostic_cases.json',[x.to_json() for x in diagnostic_cases])
    write_json(out/'diagnostic.json',samples)
    summary={'arms':arm_summary,'paired_comparisons':comparisons,'proposal_diagnostics':diagnostics,
        'common_initialization_executions':40*args.seeds,
        'final_audit_executions':args.audit_cases*(1+args.seeds*3),
        'diagnostic_executions':args.diagnostic_cases*(1+len(samples)),
        'total_search_executions':args.seeds*args.generations*4*56*3,
        'mean_seconds_all_arms_per_seed':mean([r['seconds_all_arms'] for r in final])}
    write_json(out/'summary.json',summary)
    print(arm_summary,flush=True)

if __name__=='__main__':main()
