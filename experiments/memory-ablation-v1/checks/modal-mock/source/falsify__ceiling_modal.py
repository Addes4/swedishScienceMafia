"""Fan the bp-ceiling-v1 searches out on Modal (app ssm-bp-ceiling), with a hard spend cap.

    modal run falsify/ceiling_modal.py --out experiments/bp-ceiling-v1 --seeds 20 --evaluations 8000

Before submitting anything, the worst case (every job running to its timeout) is priced and
the run is refused if it could exceed --cap-usd. Runs already on disk are skipped, so an
interrupted fan-out can be resumed. Each finished run is written as soon as it returns.
"""
import json
import sys
import time
from pathlib import Path

import modal

ROOT = Path(__file__).resolve().parents[1]
APP_NAME = 'ssm-bp-ceiling'
# Modal list prices (USD per second): one physical CPU core, one GiB of memory. The cap check
# adds a 25% margin on top.
CPU_CORE_SECOND = 0.0000131
GIB_SECOND = 0.00000222
CPU, MEMORY_MB = 1.0, 1024
TIMEOUTS = {'falsify80': 900, 'weibull500': 1800, 'weibull5k': 3600}

image = (modal.Image.debian_slim(python_version='3.12')
         .apt_install('g++')
         .pip_install('numpy==2.*', 'cma==4.5.0')
         .add_local_dir(ROOT / 'falsify', '/root/falsify', copy=True,
                        ignore=['__pycache__', '*.dylib', '*.so', '*.pyc'])
         .run_commands('cd /root && python -c "import falsify.longpack as l; l._lib()"'))
app = modal.App(APP_NAME, image=image)


def _search(job):
    from falsify.ceiling import run_search
    return run_search(**job)


@app.function(cpu=CPU, memory=MEMORY_MB, timeout=TIMEOUTS['falsify80'])
def search_falsify80(job):
    return _search(job)


@app.function(cpu=CPU, memory=MEMORY_MB, timeout=TIMEOUTS['weibull500'])
def search_weibull500(job):
    return _search(job)


@app.function(cpu=CPU, memory=MEMORY_MB, timeout=TIMEOUTS['weibull5k'])
def search_weibull5k(job):
    return _search(job)


FUNCTIONS = {'falsify80': search_falsify80, 'weibull500': search_weibull500, 'weibull5k': search_weibull5k}


def worst_case_usd(jobs):
    per_second = CPU * CPU_CORE_SECOND + MEMORY_MB / 1024 * GIB_SECOND
    return 1.25 * per_second * sum(TIMEOUTS[j['regime']] for j in jobs)


@app.local_entrypoint()
def main(out: str = 'experiments/bp-ceiling-v1', seeds: int = 20, evaluations: int = 8000,
         cap_usd: float = 15.0, regimes: str = 'falsify80,weibull500,weibull5k'):
    sys.path.insert(0, str(ROOT))
    from falsify.ceiling import OPTIMIZERS, REPRESENTATIONS, run_name, snapshot_source
    from falsify.core import write_json
    out = Path(out)
    (out / 'runs').mkdir(parents=True, exist_ok=True)
    config_path = out / 'config.json'
    config = {'seeds': seeds, 'evaluations': evaluations, 'regimes': regimes.split(','),
              'representations': list(REPRESENTATIONS), 'optimizers': OPTIMIZERS, 'modal_app': APP_NAME,
              'cpu': CPU, 'memory_mb': MEMORY_MB, 'timeouts_s': TIMEOUTS, 'cap_usd': cap_usd, 'llm_used': False}
    if config_path.exists():
        saved = json.loads(config_path.read_text())
        if {k: saved[k] for k in ['seeds', 'evaluations']} != {'seeds': seeds, 'evaluations': evaluations}:
            raise SystemExit('config.json differs from these arguments')
    else:
        write_json(config_path, config)
        snapshot_source(out)
    jobs = [{'regime': r, 'representation': rep, 'optimizer': opt, 'seed': s, 'evaluations': evaluations}
            for r in regimes.split(',') for rep in REPRESENTATIONS for opt in OPTIMIZERS for s in range(seeds)]
    jobs = [j for j in jobs if not (out / 'runs' / f"{run_name(j['regime'], j['representation'], j['optimizer'], j['seed'])}.json.gz").exists()]
    reserve = worst_case_usd(jobs)
    print(f'{len(jobs)} jobs; worst-case cost ${reserve:.2f} (cap ${cap_usd:.2f})', flush=True)
    if reserve > cap_usd:
        raise SystemExit('refusing: worst case could exceed the Modal cap')
    ledger = out / 'modal_usage.jsonl'
    started = time.time()
    for regime in regimes.split(','):
        batch = [j for j in jobs if j['regime'] == regime]
        if not batch:
            continue
        for job, result in zip(batch, FUNCTIONS[regime].map(batch, return_exceptions=True)):
            name = run_name(job['regime'], job['representation'], job['optimizer'], job['seed'])
            entry = {'run': name, 'ok': not isinstance(result, BaseException), 'time': time.time()}
            if entry['ok']:
                write_json(out / 'runs' / f'{name}.json.gz', result)
                entry['seconds'] = result['seconds']
                entry['estimated_usd'] = result['seconds'] * (CPU * CPU_CORE_SECOND + MEMORY_MB / 1024 * GIB_SECOND)
            else:
                entry['error'] = repr(result)[:500]
            with open(ledger, 'a') as f:
                f.write(json.dumps(entry) + '\n')
            print(name, 'ok' if entry['ok'] else entry['error'], flush=True)
    print(f'done in {time.time() - started:.0f}s', flush=True)
