"""Common fresh confirmation of frozen pilots; never feeds the search loop."""
import argparse
import json
import sys
import platform
import subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from autoresearch.evidence_adapters import ADAPTERS,digest
from autoresearch.evidence_stats import comparison
from autoresearch.live import dump


def main():
    ap=argparse.ArgumentParser();ap.add_argument('runs',nargs='+')
    ap.add_argument('--out',default='runs/confirmation');args=ap.parse_args()
    out=Path(args.out);out.mkdir(parents=True,exist_ok=False)
    selected={}
    for name in args.runs:
        run=Path(name)
        config=json.loads((run/'config.json').read_text())
        summary=json.loads((run/'summary.json').read_text())
        frozen=json.loads((run/'frozen.json').read_text())
        simple=json.loads((run/'simplification.json').read_text())
        for arm,entry in frozen.items():
            for variant,payload in [('original',entry['payload']),('simplified',simple[entry['id']]['payload'])]:
                key=config['problem']+':'+digest(payload)
                row=selected.setdefault(key,{'problem':config['problem'],'payload':payload,'sources':[]})
                row['sources'].append({'run':run.name,'arm':arm,'variant':variant,'primary':arm==config['actual_gate'],'terminal_status':summary['status']})
    # Freeze the complete candidate set before generating any confirmation inputs.
    dump(out/'frozen_inputs.json',selected)
    dump(out/'config.json',{'kind':'common_fresh_confirmation','backend':'local','workers':4,'timeout':30,
        'python':platform.python_version(),'platform':platform.platform(),
        'git_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'source_hashes':{str(p.relative_to(ROOT)):digest(p.read_text()) for p in [Path(__file__).resolve(),ROOT/'autoresearch/evidence_adapters.py',ROOT/'autoresearch/research_worker.py',ROOT/'autoresearch/evidence_stats.py',ROOT/'problems/circle_packing/verify.py']}})
    results={}
    for problem in sorted({x['problem'] for x in selected.values()}):
        adapter=ADAPTERS[problem](out/problem,timeout=30,workers=4,backend='local')
        count=1600 if problem=='bounded' else 100 if problem=='rich' else 10
        seed={'bounded':8902615,'rich':8902715,'circle':8902815}[problem]
        cases=adapter.cases(seed,count,audit=True)
        dump(out/problem/'cases.json',cases)
        reference=adapter.evaluate(adapter.initial,cases,'confirmation_reference')
        rows=[]
        for key,entry in selected.items():
            if entry['problem']!=problem:continue
            evaluated=adapter.evaluate(entry['payload'],cases,'confirmation_candidate')
            rows.append({'id':key.split(':')[1],'sources':entry['sources'],
                         'objective':evaluated['objective'],'vs_reference':comparison(evaluated,reference,cases)})
        extra={}
        if hasattr(adapter,'first_fit'):
            first=adapter.evaluate(adapter.first_fit,cases,'confirmation_first_fit')
            extra['first_fit_vs_reference']=comparison(first,reference,cases)
        results[problem]={'seed':seed,'cases':count,'reference_objective':reference['objective'],'candidates':rows,'work':adapter.metrics(),**extra}
        dump(out/'results.json',results)
        print(problem,'confirmed',len(rows),'unique programs',flush=True)
    lines=['# Common fresh confirmation\n',
           'All programs were frozen before these inputs were generated. No outputs return to the search loops. Comparisons condition on these selected programs; they do not establish a causal framework advantage.\n',
           '| Problem | Program | Mean difference | 95% case interval | Wins / ties / losses |',
           '|---|---|---:|---|---|']
    for problem,data in results.items():
        for row in data['candidates']:
            c=row['vs_reference']
            lines.append(f'| {problem} | `{row["id"][:12]}` | {c.get("mean_difference")} | {c.get("bootstrap_95_interval")} | {c.get("wins")} / {c.get("ties")} / {c.get("losses")} |')
    lines+=['\nNegative favors the candidate. Units: bins for packing, negative radius sum for circle. Source run/arm/variant mapping is in [results.json](results.json).\n']
    (out/'report.md').write_text('\n'.join(lines))


if __name__=='__main__':main()
