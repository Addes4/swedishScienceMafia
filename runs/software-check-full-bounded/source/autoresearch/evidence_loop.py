"""One reproducible research loop for bounded rules, code search and the full stack.

python -m autoresearch.evidence_loop --problem bounded --steps 12 --out runs/my-run
No writes to experiments/. Each run gets its own protocol, raw records and fresh audit.
"""
import argparse
import ast
import json
import random
import subprocess
import time
from pathlib import Path

from .live import LiveClient, Ledger, BudgetExceeded, dump, append
from .evidence_adapters import ADAPTERS, ROOT, digest, case_id
from .evidence_stats import comparison
from .evidence_scheduler import Scheduler
from falsify.soft_gates import gate_decision
from falsify.simplify import simplify, explain

ARMS=('score_only','random_strict','strict','validated_budget')
MOVES={
    'edit':'Make a small targeted edit to the current candidate informed by the feedback.',
    'rewrite':'Rewrite the approach substantially while retaining any useful insight.',
    'restart':'Develop a new approach from the problem statement; do not merely perturb the parent.',
    'crossover':'Combine complementary mechanisms from the two supplied parent candidates.'}


def object_schema(properties):
    return {'type':'object','properties':properties,'required':list(properties),'additionalProperties':False}


class MockClient:
    """Deterministic software fixture. Never labelled a live model run."""
    def __init__(self,adapter):self.adapter=adapter;self.i=0
    def call(self,model,system,user,max_tokens=4096,schema=None,**kw):
        self.i+=1
        if schema and 'ideas' in schema.get('properties',{}):text=json.dumps({'ideas':['Tight-fit change','Rewrite scoring','Explore another structure']})
        elif schema and 'rankings' in schema.get('properties',{}):text=json.dumps({'rankings':[{'p_improve':p,'p_repeat':0.} for p in [.8,.5,.2]]})
        elif self.adapter.name=='bounded':
            w=list(self.adapter.initial);w[4]=.1 if self.i%2 else 0
            text=json.dumps({'weights':w,'hypothesis':'MOCK fixture','falsification':'test fixture'})
        else:text='```python\n'+self.adapter.initial+'\n```'
        return {'text':text,'usd':0.,'status':'completed','model':'MOCK','usage':{'input_tokens':0,'output_tokens':0},'id':f'mock-{self.i}'}


def brief(ev):
    return {'valid':ev['valid'],'objective':ev['objective'],
            'logical_executions':ev['logical_executions'],'logical_item_steps':ev['logical_item_steps'],
            'failures':[r.get('reason','invalid') for r in ev['rows'] if not r['valid']][:2]}


class ResearchRun:
    def __init__(self,args):
        self.a=args;self.out=Path(args.out)
        if 'experiments' in self.out.resolve().parts:raise ValueError('Existing experiment tree is read-only evidence')
        self.out.mkdir(parents=True,exist_ok=False)
        self.adapter=ADAPTERS[args.problem](self.out,timeout=args.timeout)
        self.rng=random.Random(args.seed)
        self.ledger=Ledger(args.ledger,25.)
        self.client=MockClient(self.adapter) if args.mock else LiveClient(self.out,self.ledger,args.budget)
        self.history=[];self.archive=[];self.candidates={};self.full=args.approach=='full'
        self.replay_work={a:{'logical_executions':0,'logical_item_steps':0} for a in ARMS}
        self.gate=args.gate or ('validated_budget' if self.full and args.problem!='circle' else 'strict')
        self.counts=({'fixed':24,'stress':16,'validation':64,'probes':8,'audit':1600,'simplify':1000}
                     if args.problem=='bounded' else
                     {'fixed':3,'stress':0,'validation':2,'probes':0,'audit':5,'simplify':3}
                     if args.problem=='circle' else
                     {'fixed':6,'stress':4,'validation':6,'probes':2,'audit':20,'simplify':6})
        if args.mock:
            self.counts={'fixed':2,'stress':2 if args.problem!='circle' else 0,'validation':2,'probes':2 if args.problem!='circle' else 0,'audit':8,'simplify':8}
        self.base=args.seed*100000
        self.fixed=self.adapter.cases(self.base+1,self.counts['fixed'])
        self.fixed_ref=self.adapter.evaluate(self.adapter.initial,self.fixed,'fixed_reference')
        if not self.fixed_ref['valid']:raise ValueError('Initial reference failed validation')
        self.scheduler=Scheduler(args.scheduler or ('adaptive' if self.full else 'patience'),self.adapter.initial,self.fixed_ref['objective'],args.seed)
        self.inc={arm:self.adapter.initial for arm in ARMS}
        self.incscore={arm:self.fixed_ref['objective'] for arm in ARMS}
        initcases=self.adapter.cases(self.base+2,max(16,self.counts['stress'])) if args.problem!='circle' else []
        self.archive=[{'case':c,'gap':0,'generation':-1,'id':case_id(c)} for c in initcases]
        self.save_candidate(self.adapter.initial,'initial','Provided seed; not a discovery',[])
        self.snapshot()

    def snapshot(self):
        try:head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
        except Exception:head='unknown'
        files=[p for base in ('autoresearch','falsify','strategist') for p in (ROOT/base).glob('*.py')]
        files.extend((ROOT/'falsify').glob('*.cpp'))
        src=self.out/'source';src.mkdir()
        for p in files:
            target=src/p.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(p.read_bytes())
        dump(self.out/'source_hashes.json',{str(p.relative_to(ROOT)):digest(p.read_text()) for p in files})
        cfg={**vars(self.a),'git_head':head,'counts':self.counts,'actual_gate':self.gate,
             'live_mode_requested':not self.a.mock,'started_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),
             'note':'One pilot trajectory; fresh audit never feeds selection. Full ranker identity is explicit.'}
        dump(self.out/'config.json',cfg);dump(self.out/'fixed_cases.json',self.fixed)
        (self.out/'protocol.md').write_text('# Frozen run protocol\n\n```json\n'+json.dumps(cfg,indent=2)+'\n```\n\n'
          'Scores are minimized. All required cases must be valid. Packing gate arms share proposals and evaluator work; '
          'they are conditional replay controls, not independent autonomous trajectories. Archive is frozen before each batch. '
          'Final candidates and simplifications are frozen before fresh audit generation. Public reference sets are separately labelled. '
          'All model requests, including incomplete outputs, cost money and are logged. No automatic retries. '
          'Model randomness is not controlled by the harness seed. Generic code simplification is one model proposal plus measured confirmation, not a proof.\n')

    def save_candidate(self,payload,move,hypothesis,parents):
        cid=digest(payload)
        if cid not in self.candidates:
            self.candidates[cid]={'id':cid,'payload':payload,'move':move,'hypothesis':hypothesis,'parents':parents}
            dump(self.out/'candidates'/f'{cid}.json',self.candidates[cid])
            if isinstance(payload,str):(self.out/'candidates'/f'{cid}.py').write_text(payload)
        return cid

    def context(self,op,partner):
        parent=self.scheduler.working
        witnesses=[{'items':x['case'].get('items',[])[:100], 'capacity':x['case'].get('capacity'),
                    'observed_excess':x['gap'],'truncated':len(x['case'].get('items',[]))>100}
                   for x in self.archive if x['gap']>0][:2]
        # Long packing streams are never truncated into misleading executable witnesses.
        witnesses=[w for w in witnesses if not w['truncated']]
        return json.dumps({'move':op,'instruction':MOVES[op],'parent':parent,
                           'second_parent':partner if op=='crossover' else None,
                           'recent_outcomes':self.history[-5:], 'executable_failures':witnesses})

    def propose(self,op,partner,step):
        prompt=self.context(op,partner)
        if not self.full:
            call=self.client.call(self.a.model,self.adapter.description,prompt,
                max_tokens=2048 if self.a.problem=='bounded' else 6000,schema=self.adapter.schema,tag=f'step-{step}')
            return [(call,None)],0.
        ideas_call=self.client.call(self.a.model,self.adapter.description+' Propose three distinct ideas; do not write code yet.',prompt,
             max_tokens=2048,schema=object_schema({'ideas':{'type':'array','items':{'type':'string'},'minItems':3,'maxItems':3}}),tag=f'ideas-{step}')
        if ideas_call['status']!='completed':raise ValueError('Idea proposal incomplete')
        ideas=json.loads(ideas_call['text'])['ideas']
        rank_cost=0.
        if self.a.ranker=='random':
            ranks=[self.rng.random() for _ in ideas]
        elif self.a.ranker=='jev':
            from .rankers import JevRanker
            # Reserve per-call conservative maximum; no raw exception text reaches artifacts.
            rid=self.ledger.reserve(self.out.name,.05,self.a.budget,{'model':'jev','tag':f'rank-{step}'})
            ranker=JevRanker()
            results=ranker.rank(self.adapter.description,-self.scheduler.f_work,str(self.scheduler.working),self.history,ideas)
            rank_cost=sum(x.cost for x in results)
            self.ledger.settle(rid,self.out.name,rank_cost,model='jev',rankings=[r.to_dict() for r in results])
            ranks=[r.key for r in results]
        else:
            call=self.client.call('gpt-6-luna','Rank research ideas. Assess likelihood of reducing the minimized objective, and repetition of a failure.',
                json.dumps({'problem':self.adapter.description,'ideas':ideas,'history':self.history[-5:]}),max_tokens=2048,
                schema=object_schema({'rankings':{'type':'array','items':object_schema({'p_improve':{'type':'number'},'p_repeat':{'type':'number'}}),'minItems':3,'maxItems':3}}),tag=f'rank-{step}')
            rank_cost=call['usd'];ans=json.loads(call['text'])['rankings'];ranks=[r['p_improve']-.5*r['p_repeat'] for r in ans]
        order=sorted(range(len(ideas)),key=lambda i:-ranks[i])
        tiers=['gpt-6-astra','gpt-6.1-sol','gpt-6-luna']
        out=[]
        for pos,i in enumerate(order):
            tier=pos;swapped=False
            if self.rng.random()<.15:
                tier=self.rng.choice([j for j in range(3) if j!=tier]);swapped=True
            call=self.client.call(tiers[tier],self.adapter.description,prompt+'\nImplement this idea: '+ideas[i],
                      max_tokens=2048 if self.a.problem=='bounded' else 6000,schema=self.adapter.schema,tag=f'step-{step}-idea-{i}')
            out.append((call,{'idea':ideas[i],'rank':ranks[i],'planned_tier':pos,'tier':tier,'swapped':swapped,'ranker':self.a.ranker}))
        return out,ideas_call['usd']+rank_cost

    def run(self):
        started=time.monotonic();terminal='completed'
        try:
            for step in range(self.a.steps):
                op,state,partner,why=self.scheduler.choose()
                dump(self.out/f'scheduler-{step}.json',why)
                stress=[r['case'] for r in self.rng.sample(self.archive,min(len(self.archive),self.counts['stress']))]
                random_cases=self.adapter.cases(self.base+100+step*10,self.counts['stress'])
                validation=self.adapter.cases(self.base+101+step*10,self.counts['validation'])
                probes=self.adapter.cases(self.base+102+step*10,self.counts['probes'])
                splits={'fixed':self.fixed,'stress':stress,'random':random_cases,'validation':validation,'probes':probes}
                dump(self.out/'splits'/f'{step}.json',splits)
                parents=[digest(self.scheduler.working)]
                if op=='crossover':parents.append(digest(partner))
                calls,overhead=self.propose(op,partner,step)
                incoming=[]
                for index,(call,rank) in enumerate(calls):
                    rec={'step':step,'index':index,'move':op,'parents':parents,'call_id':call['id'],'model':call['model'],'usd':call['usd']+overhead/len(calls),'rank':rank}
                    if call['status']!='completed':
                        rec.update(outcome='incomplete',status=call['status']);self.scheduler.observe(op,state,None,None,rec['usd'])
                        append(self.out/'events.jsonl',rec);self.history.append(rec);continue
                    try:payload,hypothesis=self.adapter.parse(call['text'])
                    except (ValueError,KeyError,SyntaxError,TypeError) as exc:
                        rec.update(outcome='parse_error',error=type(exc).__name__);self.scheduler.observe(op,state,None,None,rec['usd'])
                        append(self.out/'events.jsonl',rec);self.history.append(rec);continue
                    cid=self.save_candidate(payload,op,hypothesis,parents);rec['candidate']=cid
                    evals={name:self.adapter.evaluate(payload,cases,name) for name,cases in splits.items() if cases}
                    refs={name:self.adapter.evaluate(self.adapter.initial,cases,name+'_reference') for name,cases in splits.items() if cases}
                    rec['evaluations']={k:brief(v) for k,v in evals.items()}
                    # Charge all controls the same evaluated splits, even where a
                    # gate does not need a split. Physical work is shared/cached.
                    for arm in ARMS:
                        for metric in self.replay_work[arm]:
                            self.replay_work[arm][metric]+=sum(v[metric] for v in [*evals.values(),*refs.values()])
                    valid=all(v['valid'] for v in evals.values())
                    score=evals['fixed']['objective'] if valid else None
                    rec['gates']={};promoted=False
                    for arm in ARMS:
                        if self.a.problem=='circle':decision={'pass':valid,'reason':'strict geometry validation'}
                        elif valid:
                            ds=lambda name:[x['objective']-y['objective'] for x,y in zip(evals[name]['rows'],refs[name]['rows'])]
                            decision=({'pass':True} if arm=='score_only' else
                                      gate_decision('strict' if arm in ('strict','random_strict') else arm,
                                                    score-self.fixed_ref['objective'],ds('random' if arm=='random_strict' else 'stress'),ds('validation')))
                        else:decision={'pass':False,'reason':'invalid required evaluation'}
                        eligible=valid and (score<self.incscore[arm]-1e-12 or
                             (abs(score-self.incscore[arm])<=1e-12 and
                              (self.adapter.complexity(payload),cid)<(self.adapter.complexity(self.inc[arm]),digest(self.inc[arm]))))
                        accept=eligible and decision['pass']
                        rec['gates'][arm]={**decision,'eligible':eligible,'promoted':accept}
                        if accept:self.inc[arm],self.incscore[arm]=payload,score
                        if arm==self.gate:promoted=accept
                    if valid and self.a.problem!='circle':
                        for c,r,ref in zip(probes,evals['probes']['rows'],refs['probes']['rows']):
                            incoming.append({'case':c,'gap':r['objective']-ref['objective'],'generation':step,'id':case_id(c)})
                    self.scheduler.observe(op,state,payload,score,rec['usd'])
                    rec['outcome']='promoted' if promoted else ('not_promoted' if valid else 'invalid')
                    rec['incumbents']={a:digest(p) for a,p in self.inc.items()}
                    append(self.out/'events.jsonl',rec)
                    self.history.append({'move':op,'hypothesis':hypothesis,'outcome':rec['outcome'],'score':score,
                                         'gate':rec['gates'][self.gate],'feedback':rec['evaluations']})
                    print(f'{self.out.name} step={step} candidate={cid[:8]} outcome={rec["outcome"]} score={score} cost=${rec["usd"]:.4f}',flush=True)
                unique={}
                for entry in self.archive+incoming:
                    old=unique.get(entry['id'])
                    if old is None or (entry['gap'],entry['generation'])>(old['gap'],old['generation']):unique[entry['id']]=entry
                self.archive=sorted(unique.values(),key=lambda x:(x['gap'],x['generation']),reverse=True)[:64]
                dump(self.out/'checkpoint.json',{'next_step':step+1,'incumbents':self.inc,'archive':self.archive})
        except (BudgetExceeded,RuntimeError,ValueError,KeyError) as e:
            terminal=type(e).__name__+': '+str(e)
            append(self.out/'events.jsonl',{'event':'stopped','reason':terminal})
        self.finish(terminal,time.monotonic()-started)

    def finish(self,terminal,elapsed):
        frozen={arm:{'id':digest(p),'payload':p,'training_objective':self.incscore[arm]} for arm,p in self.inc.items()}
        dump(self.out/'frozen.json',frozen)
        simple={};simplification_cases=self.adapter.cases(self.base+9001,self.counts['simplify'])
        dump(self.out/'simplification_cases.json',simplification_cases)
        for cid,p in {digest(p):p for p in self.inc.values()}.items():
            if self.a.problem=='bounded':
                r=simplify(p,simplification_cases,mode='explain',limit=150000)
                simple[cid]={'payload':r['weights'],'details':r,'explanation':explain(r['weights'])}
            elif self.full and terminal=='completed' and not self.a.mock:
                try:
                    call=self.client.call(self.a.model,self.adapter.description,
                          'Simplify the following program while preserving its algorithm and output quality. Remove unnecessary code; do not repair or replace its strategy.\n'+p,
                          max_tokens=6000,tag='simplify')
                    if call['status']!='completed':continue
                    candidate,_=self.adapter.parse(call['text'])
                    original_ev=self.adapter.evaluate(p,simplification_cases,'simplification_original')
                    simple_ev=self.adapter.evaluate(candidate,simplification_cases,'simplification_candidate')
                    check=comparison(simple_ev,original_ev,simplification_cases)
                    preserved=check['valid'] and abs(check['mean_difference'])<=self.adapter.tolerance
                    simpler=self.adapter.complexity(candidate)<self.adapter.complexity(p)
                    simple[cid]={'payload':candidate if preserved and simpler else p,
                                 'details':{'comparison':check,'preserved':preserved,'simpler':simpler,'candidate':candidate,
                                            'classification':'preservation' if preserved else ('repair' if check.get('mean_difference',0)<0 else 'regression')}}
                except (ValueError,RuntimeError,BudgetExceeded) as e:
                    simple[cid]={'payload':p,'details':{'error':str(e)}}
            else:simple[cid]={'payload':p,'details':{'simplification':'not requested / unsupported'}}
        dump(self.out/'simplification.json',simple)
        # This is the first construction of audit inputs: selection is over.
        audit=self.adapter.cases(self.base+99001,self.counts['audit'],audit=True)
        dump(self.out/'audit_cases.json',audit)
        baseline=self.adapter.evaluate(self.adapter.initial,audit,'audit_reference')
        audit_results={};raw={}
        for arm,r in frozen.items():
            original=self.adapter.evaluate(r['payload'],audit,'audit_original')
            simplified=self.adapter.evaluate(simple[r['id']]['payload'],audit,'audit_simplified')
            audit_results[arm]={'original_vs_reference':comparison(original,baseline,audit),
                               'simplified_vs_original':comparison(simplified,original,audit),
                               'simplified_vs_reference':comparison(simplified,baseline,audit),
                               'original_objective':original['objective'],'reference_objective':baseline['objective']}
            raw[arm]={'original':original,'simplified':simplified}
        if hasattr(self.adapter,'first_fit'):
            first=self.adapter.evaluate(self.adapter.first_fit,audit,'audit_first_fit')
            audit_results['first_fit_vs_best_fit']=comparison(first,baseline,audit)
        dump(self.out/'audit_raw.json',{'reference':baseline,'policies':raw})
        if self.a.problem=='rich':self.public_audit(frozen,audit_results)
        usage=self.ledger.totals(self.out.name) if not self.a.mock else {'actual_usd':0,'attempts':0}
        summary={'problem':self.a.problem,'approach':self.a.approach,'llm_used':usage.get('settled_requests',0)>0,
                 'status':terminal,'search_seconds':elapsed,'usage':usage,'evaluation_work':self.adapter.metrics(),
                 'conditional_replay_work_per_arm':self.replay_work,
                 'audit':audit_results,'final_candidate':frozen[self.gate]['id'],
                 'simplification_packing_executions':sum(s['details'].get('packing_executions',0) for s in simple.values()),
                 'claims_limit':'Single pilot; gate controls share proposals; no causal memory or efficiency claim.'}
        dump(self.out/'summary.json',summary)
        self.report(summary)
        print(json.dumps({'run':str(self.out),'status':terminal,'usage':usage,'audit':audit_results[self.gate]['original_vs_reference']},indent=2),flush=True)

    def public_audit(self,frozen,results):
        data=json.loads((ROOT/'data/funsearch/datasets.json').read_text())
        for family,rows in data.items():
            cases=[{**c,'family':family,'source':name} for name,c in rows.items()]
            baseline=self.adapter.evaluate(self.adapter.initial,cases,'public_reference')
            suffix='or' if family=='OR3' else 'weibull'
            published=(ROOT/f'data/funsearch/priority_{suffix}.py').read_text()
            reference=self.adapter.evaluate(published,cases,'public_funsearch')
            selected=self.adapter.evaluate(frozen[self.gate]['payload'],cases,'public_candidate')
            first=self.adapter.evaluate(self.adapter.first_fit,cases,'public_first_fit')
            lower=sum(r['l1'] for r in baseline['rows'])/len(cases)
            results['public_'+family]={'candidate_vs_best_fit':comparison(selected,baseline,cases),
                'published_vs_best_fit':comparison(reference,baseline,cases),
                'first_fit_vs_best_fit':comparison(first,baseline,cases),
                'mean_l1':lower,'relative_excess_l1':{name:(ev['objective']-lower)/lower if ev['valid'] else None
                    for name,ev in [('candidate',selected),('best_fit',baseline),('funsearch',reference),('first_fit',first)]},
                'note':'Public fixed dataset; L1 as notebook, not paper L2; used only after candidate freeze.'}

    def report(self,s):
        lines=[f'# {self.a.approach}: {self.a.problem}\n',f'Status: **{s["status"]}**. Real LLM: **{s["llm_used"]}**.\n',
               f'API ledger: `{json.dumps(s["usage"])}`.\n',
               '| Gate | Mean difference vs reference | 95% case interval | Wins / ties / losses |',
               '|---|---:|---|---|']
        for arm in ARMS:
            r=s['audit'][arm]['original_vs_reference']
            lines.append(f'| {arm} | {r.get("mean_difference")} | {r.get("bootstrap_95_interval")} | {r.get("wins")} / {r.get("ties")} / {r.get("losses")} |')
        lines += ['\nNegative differences favor the candidate. Packing units are bins; circle units are negative radius sum.\n',
                  s['claims_limit']+'\n','\nFull machine-readable results: [summary.json](summary.json). Method: [protocol.md](protocol.md).\n']
        (self.out/'report.md').write_text('\n'.join(lines))


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--problem',choices=list(ADAPTERS),required=True)
    ap.add_argument('--approach',choices=['lean','full'],default='lean')
    ap.add_argument('--model',default='gpt-6.1-sol')
    ap.add_argument('--steps',type=int,default=12)
    ap.add_argument('--seed',type=int,default=7101)
    ap.add_argument('--budget',type=float,default=3.)
    ap.add_argument('--ledger',default=str(ROOT/'runs/campaign_usage.jsonl'))
    ap.add_argument('--out',required=True)
    ap.add_argument('--ranker',choices=['openai','random','jev'],default='openai')
    ap.add_argument('--scheduler',choices=['patience','adaptive'])
    ap.add_argument('--gate',choices=ARMS)
    ap.add_argument('--timeout',type=int,default=30)
    ap.add_argument('--mock',action='store_true')
    args=ap.parse_args()
    if not 1<=args.steps<=100 or not 0<args.budget<=25:ap.error('Invalid steps or budget')
    ResearchRun(args).run()


if __name__=='__main__':main()
