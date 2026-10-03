"""Matched-budget mechanistic ablation. No language model is used in this script."""
import argparse
import random
import statistics
import time
from pathlib import Path
from .core import BEST_FIT, FEATURES, TRAIN_FAMILIES, SHIFT_FAMILIES, identity, mutate, pack, suite, write_json

ARMS = ['random_replay', 'counterexample_replay', 'counterexample_tail']

def run(seed, arm, generations):
    rng = random.Random(seed)
    fixed = suite(10000+seed,24)
    initial = suite(20000+seed,8)
    archive = [{**x,'gap':0,'id':identity(x['items'])} for x in initial]
    incumbent = list(BEST_FIT)
    history = []
    executions = 0
    start = time.monotonic()
    for generation in range(generations):
        # Separate streams keep probe inputs and mutation perturbations paired across arms.
        proposal_rng = random.Random(seed*1000000+generation)
        replay_rng = random.Random(seed*2000000+generation)
        replay = replay_rng.sample(archive,min(8,len(archive)))
        probes = suite(300000+seed*1000+generation,8)
        candidates = [incumbent] + [mutate(incumbent,proposal_rng) for _ in range(3)]
        outcomes=[]
        for weights in candidates:
            scores=[pack(x['items'],weights) for x in fixed+replay]
            probe_scores=[pack(x['items'],weights) for x in probes]
            refs=[pack(x['items'],BEST_FIT) for x in probes]
            executions += len(scores)+len(probe_scores)+len(refs)
            objective=statistics.mean(scores)
            if arm=='counterexample_tail': objective += .25*max(scores[-8:])
            outcomes.append((objective, weights, probe_scores, refs))
        selected=min(range(len(outcomes)),key=lambda i:outcomes[i][0])
        objective,incumbent,probe_scores,refs=outcomes[selected]
        incoming=[{**x,'gap':a-b,'id':identity(x['items']), 'generation':generation} for x,a,b in zip(probes,probe_scores,refs)]
        unique={x['id']:x for x in archive+incoming}
        if arm=='random_replay':
            archive=list(unique.values())
            if len(archive)>64: archive=rng.sample(archive,64)
        else:
            # Persist the largest *observed* regressions; this is deliberately simple.
            archive=sorted(unique.values(),key=lambda x:(x['gap'],x.get('generation',-1)),reverse=True)[:64]
        history.append({'generation':generation,'objective':objective,'selected':selected,
                        'probe_excess':statistics.mean(a-b for a,b in zip(probe_scores,refs)),
                        'archive_max_observed_gap':max(x['gap'] for x in archive),
                        'packing_executions':executions, 'weights':incumbent})
    return {'seed':seed,'arm':arm,'weights':incumbent,'history':history,'archive':archive,
            'search_packing_executions':executions,'search_item_steps':executions*80,
            'seconds':time.monotonic()-start}

def audit(run, cases):
    out={}
    for family in TRAIN_FAMILIES+SHIFT_FAMILIES:
        xs=[x for x in cases if x['family']==family]
        gaps=[pack(x['items'],run['weights'])-pack(x['items'],BEST_FIT) for x in xs]
        out[family]={'mean_excess_bins':statistics.mean(gaps),'wins':sum(g<0 for g in gaps),
                     'ties':sum(g==0 for g in gaps),'losses':sum(g>0 for g in gaps),'n':len(gaps)}
    return out

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--seeds',type=int,default=20)
    parser.add_argument('--generations',type=int,default=120)
    parser.add_argument('--audit-seed',type=int,default=982451653)
    parser.add_argument('--out',default='experiments/local-v1')
    args=parser.parse_args()
    out=Path(args.out); out.mkdir(parents=True,exist_ok=True)
    write_json(out/'config.json',vars(args))
    runs=[]
    # Audit instances are generated only after every search has completed.
    for seed in range(args.seeds):
        for arm in ARMS:
            result=run(seed,arm,args.generations)
            write_json(out/f'{arm}-{seed}.json',result)
            runs.append(result)
            print(f'{arm} seed={seed} seconds={result["seconds"]:.2f}',flush=True)
    cases=suite(args.audit_seed,800,TRAIN_FAMILIES+SHIFT_FAMILIES)
    for result in runs: result['audit']=audit(result,cases)
    summary=[]
    for arm in ARMS:
        rs=[r for r in runs if r['arm']==arm]
        summary.append({'arm':arm,'seeds':args.seeds,
            'mean_excess_bins':statistics.mean(v['mean_excess_bins'] for r in rs for v in r['audit'].values()),
            'by_family':{f:statistics.mean(r['audit'][f]['mean_excess_bins'] for r in rs) for f in TRAIN_FAMILIES+SHIFT_FAMILIES},
            'executions_per_seed':rs[0]['search_packing_executions'],
            'mean_seconds':statistics.mean(r['seconds'] for r in rs)})
    differences=[]
    for arm in ARMS[1:]:
        ds=[]
        for seed in range(args.seeds):
            a=next(r for r in runs if r['seed']==seed and r['arm']==arm)
            b=next(r for r in runs if r['seed']==seed and r['arm']==ARMS[0])
            ds.append(statistics.mean(v['mean_excess_bins'] for v in a['audit'].values())-
                      statistics.mean(v['mean_excess_bins'] for v in b['audit'].values()))
        boot_rng=random.Random(739)
        boot=sorted(statistics.mean(boot_rng.choices(ds,k=len(ds))) for _ in range(10000))
        differences.append({'arm_minus_random':arm,'paired_seed_differences':ds,'mean':statistics.mean(ds),
                            'bootstrap_95_interval':[boot[250],boot[9749]]})
    write_json(out/'audit_cases.json',cases)
    write_json(out/'audit.json',[{'seed':r['seed'],'arm':r['arm'],'weights':r['weights'],'audit':r['audit']} for r in runs])
    write_json(out/'summary.json',{'arms':summary,'paired_comparisons':differences})
    print(summary,flush=True)

if __name__=='__main__': main()
