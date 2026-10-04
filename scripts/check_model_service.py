"""A minimal, ledger-charged service diagnostic with redacted error metadata."""
import argparse
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from autoresearch.live import LiveClient,Ledger

ap=argparse.ArgumentParser()
ap.add_argument('--model',default='gpt-6.1-sol')
ap.add_argument('--out',required=True)
ap.add_argument('--api-scheduler',choices=['legacy','headers'],default='headers')
ap.add_argument('--count-only',action='store_true')
args=ap.parse_args()
path=Path(args.out);path.mkdir(parents=True,exist_ok=False)
if args.api_scheduler=='headers':
    from autoresearch.throughput import HeaderClient
    client_type=HeaderClient
else:client_type=LiveClient
client=client_type(path,Ledger(ROOT/'runs/campaign_usage.jsonl'),.10)
try:
    if args.count_only:print(client.request('responses/input_tokens',{'model':args.model,'instructions':'Reply briefly.','input':'Return OK.'}))
    else:
        result=client.call(args.model,'Reply briefly.','Return OK.',max_tokens=64,tag='service_check')
        print({k:result[k] for k in ('model','status','usage','usd')})
except (RuntimeError,ValueError) as e:print(str(e))
if (path/'service_errors.jsonl').exists():print((path/'service_errors.jsonl').read_text())
if (path/'transport.jsonl').exists():print((path/'transport.jsonl').read_text())
