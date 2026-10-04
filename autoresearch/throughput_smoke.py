"""Small execution-path validation, not a search experiment or performance claim.

No model calls. --backend modal creates paid CPU Sandboxes, then terminates them.
"""
import argparse
import platform
import time
from pathlib import Path

from .evidence_adapters import RichAdapter, CircleAdapter, BEST_CODE
from .live import dump


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--backend',choices=['local','modal'],required=True)
    ap.add_argument('--workers',type=int,default=4)
    ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args()
    if 'experiments' in args.out.resolve().parts:raise ValueError('Experiment evidence is read-only')
    args.out.mkdir(parents=True,exist_ok=False)
    started=time.monotonic()
    adapter=RichAdapter(args.out/'rich',workers=args.workers,backend=args.backend,timeout=30)
    setup=time.monotonic()-started
    cases=adapter.cases(98217,4)
    best=adapter.evaluate(BEST_CODE,cases,'best_fit')
    assert best['valid']
    # Explicit latency fixture; NOT model-generated or evidence of search quality.
    delayed='import time\ntime.sleep(2)\n'+BEST_CODE
    delayed_ev=adapter.evaluate(delayed,cases,'two_second_latency_fixture')
    assert delayed_ev['valid']
    assert [r['assignments'] for r in best['rows']]==[r['assignments'] for r in delayed_ev['rows']]
    # Reuse the prepared backend, retaining independent circle validation.
    circle=CircleAdapter(args.out/'circle',workers=args.workers)
    circle.remote=adapter.remote;circle.backend=adapter.backend
    geometry=circle.evaluate(circle.initial,circle.cases(98217,1),'seed_geometry')
    assert geometry['valid']
    adapter.timeout=2
    timeout=adapter.evaluate('def priority(item,bins):\n    while True: pass\n',cases[:1],'timeout_fixture')
    assert not timeout['valid'] and 'timeout' in timeout['rows'][0]['reason']
    summary={'purpose':'Execution-path smoke and artificial latency fixture; no search-quality inference',
             'backend':args.backend,'workers':args.workers,'host':platform.platform(),
             'setup_seconds':setup,'best_fit_wall_seconds':best['wall_seconds'],
             'best_fit_bins':[r['bins'] for r in best['rows']],
             'latency_fixture_wall_seconds':delayed_ev['wall_seconds'],
             'circle_score':geometry['rows'][0]['score'],
             'timeout_rejected':True,'wall_seconds':time.monotonic()-started,
             'evaluations':adapter.metrics()}
    dump(args.out/'summary.json',summary)
    print(summary)


if __name__=='__main__':main()
