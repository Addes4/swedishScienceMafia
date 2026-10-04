"""Regenerate the campaign index from saved outcomes and authoritative usage records."""
import json
import sys
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from autoresearch.live import Ledger, dump


def main():
    ledger=Ledger(ROOT/'runs/campaign_usage.jsonl')
    records=[]
    for path in sorted((ROOT/'runs').glob('*/summary.json')):
        cfg=json.loads((path.parent/'config.json').read_text())
        if cfg.get('mock'):continue
        summary=json.loads(path.read_text())
        events_path=path.parent/'events.jsonl'
        events=[json.loads(x) for x in events_path.read_text().splitlines()] if events_path.exists() else []
        attempts=[e for e in events if 'call_id' in e]
        usage=ledger.totals(path.parent.name)
        result=summary['audit'][cfg['actual_gate']]
        records.append({'run':path.parent.name,'problem':cfg['problem'],'approach':cfg['approach'],
            'status':summary['status'],'candidates_evaluated':sum('evaluations' in e for e in attempts),
            'outcomes':dict(Counter(e['outcome'] for e in attempts)),
            'moves':dict(Counter(e['move'] for e in attempts)),
            'usage':usage,'audit':result,'evaluation_work':summary['evaluation_work'],
            'candidate_id':summary['final_candidate']})
    dump(ROOT/'runs/campaign_summary.json',{'ledger':ledger.totals(),'runs':records})
    lines=['# Live campaign findings\n',
        'Generated from saved summaries, events and the shared usage ledger. This file can be regenerated; raw run evidence is retained.\n',
        f'Campaign usage: `{json.dumps(ledger.totals())}`. Costs use recorded tokens and standard API prices; credits/invoice adjustments are not included.\n',
        '| Run | Evaluated candidates | Outcome | Mean audit difference | Actual USD | Reserved USD |',
        '|---|---:|---|---:|---:|---:|']
    for r in records:
        d=r['audit']['original_vs_reference'].get('mean_difference')
        lines.append(f'| [{r["run"]}]({r["run"]}/report.md) | {r["candidates_evaluated"]} | {r["status"]} | {d} | {r["usage"]["actual_usd"]:.6f} | {r["usage"]["reserved_usd"]:.6f} |')
    lines += ['\nNegative differences favor the candidate. Packing units are bins; circle units are negative radius sum. A zero difference can mean the initial best-fit policy remained deployed.\n',
        '## Interpretation limits\n',
        '- Interrupted trajectories retain their own frozen audits. Later runs use new seeds and are separate pilots.\n',
        '- Case bootstrap intervals condition on one search trajectory. They do not establish scheduler or ranker superiority.\n',
        '- Gate arms share proposals and cached evaluation work. Public FunSearch reference results are separate from generated fresh audits.\n',
        '- OpenAI generation/ranking substitutes for Claude/Jev; no result here measures the original providers.\n',
        '- The ledger is authoritative for per-run token totals; early concurrent-run summaries had an aggregation bug, documented in the protocol amendments. Dollar settlements were unaffected.\n',
        '\nProtocol: [CAMPAIGN_PROTOCOL.md](CAMPAIGN_PROTOCOL.md). Narrative methods and findings: [RESEARCH_LOG.md](../RESEARCH_LOG.md).\n']
    (ROOT/'runs/FINDINGS.md').write_text('\n'.join(lines))
    print(json.dumps({'finished_runs':len(records),'ledger':ledger.totals()},indent=2))


if __name__=='__main__':main()
