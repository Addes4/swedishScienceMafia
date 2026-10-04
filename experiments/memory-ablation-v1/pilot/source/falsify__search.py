"""Matched-budget mechanistic ablation. No language model is used in this script."""
import argparse
import hashlib
import shutil
import random
import statistics
import time
from pathlib import Path
from .core import BEST_FIT, FEATURES, TRAIN_FAMILIES, SHIFT_FAMILIES, identity, mutate, pack, suite, write_json

ARMS = ['random_replay', 'counterexample_replay', 'counterexample_tail']

def run(seed, arm, generations, initial_policy='best_fit', neutral_drift=False):
    rng = random.Random(seed)
    fixed = suite(10000+seed,24)
    initial = suite(20000+seed,8)
    archive = [{**x,'gap':0,'id':identity(x['items'])} for x in initial]
    incumbent = list(BEST_FIT) if initial_policy=='best_fit' else [0.]*12
    fixed_refs=[pack(x['items'],BEST_FIT) for x in fixed]
    for entry in archive: entry['reference_bins']=pack(entry['items'],BEST_FIT)
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
            if arm=='counterexample_tail':
                objective += .25*max(a-x['reference_bins'] for a,x in zip(scores[-8:],replay))
            outcomes.append((objective, weights, probe_scores, refs))
        selected=min(range(len(outcomes)),key=lambda i:outcomes[i][0])
        if neutral_drift:
            tied=[i for i,r in enumerate(outcomes) if abs(r[0]-outcomes[selected][0])<1e-12]
            selected=proposal_rng.choice(tied)
        objective,incumbent,probe_scores,refs=outcomes[selected]
        incoming=[{**x,'gap':a-b,'reference_bins':b,'id':identity(x['items']), 'generation':generation} for x,a,b in zip(probes,probe_scores,refs)]
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
            'reference_initialization_executions':len(fixed_refs)+len(initial),
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
    parser.add_argument('--initial-policy',choices=['best_fit','first_fit'],default='best_fit')
    parser.add_argument('--neutral-drift',action='store_true')
    parser.add_argument('--out',default='experiments/local-v1')
    args=parser.parse_args()
    out=Path(args.out); out.mkdir(parents=True,exist_ok=True)
    if (out/'summary.json').exists():raise SystemExit('Output directory already contains a completed experiment; choose a new --out.')
    source=out/'source';source.mkdir(exist_ok=True)
    for p in Path(__file__).parent.iterdir():
        if p.suffix in ['.py','.cpp']:shutil.copyfile(p,source/p.name)
    write_json(out/'config.json',vars(args))
    write_json(out/'source_hashes.json',{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in source.iterdir() if p.is_file()})
    runs=[]
    # Audit instances are generated only after every search has completed.
    for seed in range(args.seeds):
        for arm in ARMS:
            result=run(seed,arm,args.generations,args.initial_policy,args.neutral_drift)
            write_json(out/f'{arm}-{seed}.json.gz',result)
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
