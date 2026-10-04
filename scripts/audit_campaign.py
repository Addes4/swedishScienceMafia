"""Check saved campaign evidence without running candidates or calling providers."""
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from autoresearch.evidence_adapters import digest, case_id
from autoresearch.live import Ledger, dump


def main():
    rows=[]
    for summary_path in sorted((ROOT/'runs').glob('*/summary.json')):
        folder=summary_path.parent
        cfg=json.loads((folder/'config.json').read_text())
        if cfg.get('mock'):continue
        source_hashes=json.loads((folder/'source_hashes.json').read_text())
        source_ok=all(digest((folder/'source'/p).read_text())==h for p,h in source_hashes.items())
        audit={case_id(c) for c in json.loads((folder/'audit_cases.json').read_text())}
        development={case_id(c) for c in json.loads((folder/'fixed_cases.json').read_text())}
        for p in (folder/'splits').glob('*.json'):
            for cases in json.loads(p.read_text()).values():development.update(case_id(c) for c in cases)
        simplification={case_id(c) for c in json.loads((folder/'simplification_cases.json').read_text())}
        events=[json.loads(s) for s in (folder/'events.jsonl').read_text().splitlines()]
        invalid_promotions=[]
        for event in events:
            if 'gates' not in event:continue
            valid=all(r['valid'] for r in event['evaluations'].values())
            if not valid and any(g['promoted'] for g in event['gates'].values()):invalid_promotions.append(event['call_id'])
        row={'run':folder.name,'source_hashes_match':source_ok,
             'audit_development_overlap':len(audit&development),
             'audit_simplification_overlap':len(audit&simplification),
             'invalid_promotions':invalid_promotions,
             'note':'Checks recorded inputs and decisions; does not re-execute candidates or prove adversarial isolation.'}
        row['passed']=source_ok and not (row['audit_development_overlap'] or row['audit_simplification_overlap'] or invalid_promotions)
        rows.append(row)
    ledger=Ledger(ROOT/'runs/campaign_usage.jsonl')
    totals=ledger.totals()
    result={'runs':rows,'campaign_under_ceiling':totals['committed_usd']<=25.,'ledger':totals}
    dump(ROOT/'runs/integrity_checks.json',result)
    print(json.dumps({'runs_checked':len(rows),'all_passed':all(r['passed'] for r in rows),'campaign_under_ceiling':result['campaign_under_ceiling']}))
    if not all(r['passed'] for r in rows) or not result['campaign_under_ceiling']:raise SystemExit(1)


if __name__=='__main__':main()
