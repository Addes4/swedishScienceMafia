"""Paired soft-gate experiment; fresh validation and bounded loss allowances."""
import argparse
import hashlib
import random
import shutil
import time
from pathlib import Path
from .core import TRAIN_FAMILIES, SHIFT_FAMILIES, identity, read_json, write_json
from .contextual import CONTEXT_BEST_FIT, CONTEXT_FEATURES, anchors, evaluate_cases, mutate_contextual
from .gated_search import make_cases, mean, evaluate_audit, bootstrap

ARMS=['strict','loss_budget','validated_budget']
VALIDATION_SEED_BASE=140000000

def gate_decision(mode,fixed_excess,stress_deltas,validation_deltas):
    """Classifier only: fixed-score incumbent comparison happens separately."""
    if mode not in ARMS or not stress_deltas or not validation_deltas:
        raise ValueError('Known mode and nonempty stress/validation evidence required')
    losses=[max(0,x) for x in stress_deltas]
    stats={'loss_count':sum(x>0 for x in stress_deltas),'max_loss':max(losses),
           'total_loss':sum(losses),'validation_excess':mean(validation_deltas),
           'fixed_excess':fixed_excess}
    if mode=='strict':
        stats['allowance']=0
        stats['pass']=stats['total_loss']==0
    else:
        gain=max(0,-fixed_excess*24) if mode=='loss_budget' else max(0,-sum(validation_deltas))
        stats['allowance']=1+gain
        stats['pass']=(stats['loss_count']<=2 and stats['max_loss']<=1 and
            stats['total_loss']<=stats['allowance']+1e-12 and
            (mode!='validated_budget' or stats['validation_excess']<=0))
    return stats

def run_seed(seed,generations):
    fixed=make_cases(610000+seed,24);initial=make_cases(620000+seed,16)
    fixed_refs=evaluate_cases(fixed,CONTEXT_BEST_FIT)
    initial_refs=evaluate_cases(initial,CONTEXT_BEST_FIT)
    fixed_baseline=mean(fixed_refs)
    def entry(case,ref,gap=0,generation=-1):
        return {'case':case,'reference_bins':ref,'gap':gap,'generation':generation,'id':identity(case.items)}
    archive=[entry(x,b) for x,b in zip(initial,initial_refs)]
    explorer=list(CONTEXT_BEST_FIT)
    deployed={a:list(CONTEXT_BEST_FIT) for a in ARMS}
    deployed_scores={a:fixed_baseline for a in ARMS}
    counts={a:{'executions':0,'promotions':0,'eligible_proposals':0,'gate_rejections':0} for a in ARMS}
    history=[];reservoir=[];eligible_seen=0;digest=hashlib.sha256()
    diagnostic_rng=random.Random(700000+seed)
    anchor_bank=anchors();started=time.monotonic()
    for generation in range(generations):
        rng=random.Random(80000000+seed*10000+generation)
        proposals=[list(CONTEXT_BEST_FIT),list(explorer),mutate_contextual(explorer,rng),
                   mutate_contextual(rng.choice(anchor_bank)['weights'],rng)]
        digest.update(str(proposals).encode())
        probes=make_cases(900000+seed*1000+generation,8)
        validation=make_cases(VALIDATION_SEED_BASE+seed*1000+generation,64)
        gate_rng=random.Random(100000000+seed*10000+generation)
        # Match V3's counterexample sampling stream after its random-gate draw.
        # Sampling consumes the same RNG draws for equal-length archives;
        # contents of that unused draw do not matter.
        gate_rng.sample(archive,16)
        stress=gate_rng.sample(archive,16)
        stress_cases=[x['case'] for x in stress]
        stress_refs=[x['reference_bins'] for x in stress]
        matrices={};incoming=[]
        for arm in ARMS:
            validation_refs=evaluate_cases(validation,CONTEXT_BEST_FIT)
            counts[arm]['executions']+=64
            evaluated=[]
            for idx,weights in enumerate(proposals):
                values=evaluate_cases(fixed+stress_cases+validation+probes,weights)
                probe_refs=evaluate_cases(probes,CONTEXT_BEST_FIT)
                counts[arm]['executions']+=len(values)+len(probe_refs)
                score=mean(values[:24])
                stress_deltas=[a-b for a,b in zip(values[24:40],stress_refs)]
                validation_deltas=[a-b for a,b in zip(values[40:104],validation_refs)]
                decision=gate_decision(arm,score-fixed_baseline,stress_deltas,validation_deltas)
                score_eligible=score<=deployed_scores[arm]
                if score_eligible and idx!=0:
                    counts[arm]['eligible_proposals']+=1
                    if not decision['pass']:counts[arm]['gate_rejections']+=1
                evaluated.append({'fixed_score':score,'gate':decision,'eligible':score_eligible and decision['pass']})
                if arm=='strict':
                    incoming.extend(entry(x,b,a-b,generation) for x,a,b in zip(probes,values[104:],probe_refs))
            matrices[arm]=evaluated
            eligible=[i for i,r in enumerate(evaluated) if r['eligible']]
            selected=None
            if eligible:
                best=min(evaluated[i]['fixed_score'] for i in eligible)
                tied=[i for i in eligible if evaluated[i]['fixed_score']==best]
                selected=random.Random(110000000+seed*10000+generation).choice(tied)
                if proposals[selected]!=deployed[arm]:counts[arm]['promotions']+=1
                deployed[arm]=list(proposals[selected]);deployed_scores[arm]=best
            matrices[arm+'_selected']=selected
        fixed_scores=[r['fixed_score'] for r in matrices['strict']]
        assert all(fixed_scores==[r['fixed_score'] for r in matrices[a]] for a in ARMS)
        best=min(fixed_scores)
        explorer=list(proposals[rng.choice([i for i,s in enumerate(fixed_scores) if s==best])])
        for idx,weights in enumerate(proposals):
            if weights==CONTEXT_BEST_FIT or fixed_scores[idx]>fixed_baseline:continue
            eligible_seen+=1
            sample={'generation':generation,'proposal':idx,'weights':list(weights),
                    'fixed_excess_bins':fixed_scores[idx]-fixed_baseline,
                    'gates':{a:matrices[a][idx]['gate'] for a in ARMS}}
            if len(reservoir)<24:reservoir.append(sample)
            else:
                replace=diagnostic_rng.randrange(eligible_seen)
                if replace<24:reservoir[replace]=sample
        unique={}
        for x in archive+incoming:
            previous=unique.get(x['id'])
            if previous is None or (x['gap'],x['generation'])>(previous['gap'],previous['generation']):
                unique[x['id']]=x
        archive=sorted(unique.values(),key=lambda x:(x['gap'],x['generation']),reverse=True)[:64]
        history.append({'generation':generation,'proposals':proposals,'evaluation':matrices,
            'deployed_weights':{a:list(w) for a,w in deployed.items()},
            'deployed_fixed_excess':{a:s-fixed_baseline for a,s in deployed_scores.items()}})
    expected=generations*544
    assert all(c['executions']==expected for c in counts.values())
    return {'seed':seed,'generations':generations,'weights':deployed,'counts':counts,
        'candidate_stream_sha256':digest.hexdigest(),'history':history,'initialization_executions':40,
        'item_steps_per_arm':expected*80,'diagnostic_sample':reservoir,
        'diagnostic_eligible_seen':eligible_seen,'seconds_all_arms':time.monotonic()-started}

def finish_audit(final,samples,args,out):
    cases=make_cases(args.audit_seed,args.audit_cases,TRAIN_FAMILIES+SHIFT_FAMILIES)
    refs=evaluate_cases(cases,CONTEXT_BEST_FIT)
    for r in final:r['audit']={a:evaluate_audit(r['weights'][a],cases,refs) for a in ARMS}
    diagnostic=make_cases(86028121,args.diagnostic_cases,TRAIN_FAMILIES+SHIFT_FAMILIES)
    diagnostic_refs=evaluate_cases(diagnostic,CONTEXT_BEST_FIT)
    for sample in samples:
        sample['audit']=evaluate_audit(sample['weights'],diagnostic,diagnostic_refs)
        excess=sample['audit']['mean_excess_bins']
        sample['empirical_class']='better' if excess<0 else 'worse' if excess>0 else 'tied'
    arms=[]
    for arm in ARMS:
        arms.append({'arm':arm,'seeds':args.seeds,
            'mean_excess_bins':mean(r['audit'][arm]['mean_excess_bins'] for r in final),
            'mean_promotions':mean(r['counts'][arm]['promotions'] for r in final),
            'mean_gate_rejections':mean(r['counts'][arm]['gate_rejections'] for r in final),
            'executions_per_seed':args.generations*544,
            'by_family':{f:mean(r['audit'][arm]['by_family'][f] for r in final) for f in TRAIN_FAMILIES+SHIFT_FAMILIES}})
    comparisons=[]
    for arm in ARMS[1:]:
        ds=[r['audit'][arm]['mean_excess_bins']-r['audit']['strict']['mean_excess_bins'] for r in final]
        comparisons.append({'arm_minus_strict':arm,'mean':mean(ds),'bootstrap_95_interval':bootstrap(ds),'paired_seed_differences':ds})
    classes={}
    for cls in ['better','worse','tied']:
        sub=[s for s in samples if s['empirical_class']==cls]
        classes[cls]={'n':len(sub),'gate_rejections':{a:sum(not s['gates'][a]['pass'] for s in sub) for a in ARMS}}
    write_json(out/'audit_cases.json',[x.to_json() for x in cases])
    write_json(out/'audit.json',final)
    write_json(out/'diagnostic_cases.json',[x.to_json() for x in diagnostic])
    write_json(out/'diagnostic.json',samples)
    summary={'arms':arms,'paired_comparisons':comparisons,'proposal_diagnostics':classes,
        'total_search_executions':args.seeds*args.generations*544*3,
        'common_initialization_executions':40*args.seeds,
        'final_audit_executions':args.audit_cases*(1+args.seeds*3),
        'diagnostic_executions':args.diagnostic_cases*(1+len(samples))}
    write_json(out/'summary.json',summary)
    return summary

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--seeds',type=int,default=40)
    parser.add_argument('--generations',type=int,default=200)
    parser.add_argument('--audit-seed',type=int,default=67867967)
    parser.add_argument('--audit-cases',type=int,default=1600)
    parser.add_argument('--diagnostic-cases',type=int,default=800)
    parser.add_argument('--out',default='experiments/soft-gate-v4')
    parser.add_argument('--resume-audit',action='store_true')
    args=parser.parse_args();out=Path(args.out)
    if args.resume_audit:
        if (out/'summary.json').exists():raise SystemExit('Audit already completed')
        config=read_json(out/'config.json')
        for k in ['seeds','generations','audit_seed','audit_cases','diagnostic_cases']:setattr(args,k,config[k])
    if args.seeds<2 or not 1<=args.generations<1000 or min(args.audit_cases,args.diagnostic_cases)<8:
        raise SystemExit('Need >=2 seeds, 1..999 generations and >=8 audit/diagnostic cases')
    if not args.resume_audit:
        if out.exists():raise SystemExit('Choose a fresh output directory')
        out.mkdir(parents=True);source=out/'source';source.mkdir()
        for p in Path(__file__).parent.iterdir():
            if p.suffix in ['.py','.cpp']:shutil.copyfile(p,source/p.name)
        write_json(out/'source_hashes.json',{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in source.iterdir()})
        write_json(out/'config.json',{**vars(args),'arms':ARMS,'features':CONTEXT_FEATURES,
            'anchors':anchors(),'llm_used':False,'validation_cases_per_generation':64,
            'max_stress_loss':1,'max_stress_losses':2,'free_loss_allowance':1,'diagnostic_seed':86028121})
    final=[];samples=[]
    for seed in range(args.seeds):
        if args.resume_audit:
            r=read_json(out/f'seed-{seed}.json.gz')
            if r['seed']!=seed or r['generations']!=args.generations or any(r['counts'][a]['executions']!=args.generations*544 for a in ARMS):
                raise ValueError('Saved trace does not match configuration')
        else:
            r=run_seed(seed,args.generations)
            write_json(out/f'seed-{seed}.json.gz',r)
            print(f'seed={seed} seconds={r["seconds_all_arms"]:.2f} promotions='+str({a:r['counts'][a]['promotions'] for a in ARMS}),flush=True)
        final.append({k:v for k,v in r.items() if k!='history'})
        samples.extend({'seed':seed,**x} for x in r['diagnostic_sample'])
    print(finish_audit(final,samples,args,out)['arms'],flush=True)

if __name__=='__main__':main()
