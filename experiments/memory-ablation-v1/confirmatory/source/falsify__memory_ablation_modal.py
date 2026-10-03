"""Modal back end for the code-regime memory study (app ssm-memory-ablation), with a spend cap.

Model-written programs are evaluated in Modal containers that have no secrets, no outbound
network (block_network) and no access to Modal resources (restrict_modal_access); inside a
container each program still runs in the gate's separate process (falsify/code_eval.py).

Every remote call reserves its worst case (the function timeout at list prices, plus 25%)
before it is submitted and is refused if settled spending plus open reservations could pass
the cap. Calls are settled with their observed wall time, which includes queueing and cold
starts and so overstates billed compute; idle containers (scaledown window) are added as an
estimate at the end of each phase. Every call is logged to modal_usage.jsonl.
"""
import json
import threading
import time
from pathlib import Path

import modal

ROOT = Path(__file__).resolve().parents[1]
APP_NAME = 'ssm-memory-ablation'
CPU, MEMORY_MB = 1.0, 1024
# Modal list prices (USD per second) for one CPU core and one GiB, as in falsify/ceiling_modal.py.
RATE = CPU * 0.0000131 + MEMORY_MB / 1024 * 0.00000222
ASSESS_TIMEOUT, SHARD_TIMEOUT = 600, 900
SCALEDOWN_S, MAX_CONTAINERS = 15, 40
_IGNORE = ['__pycache__', '*.dylib', '*.so', '*.pyc']

image = (modal.Image.debian_slim(python_version='3.12')
         .apt_install('g++')
         .pip_install('numpy==2.*')
         .add_local_dir(ROOT / 'falsify', '/root/falsify', copy=True, ignore=_IGNORE)
         .add_local_dir(ROOT / 'autoresearch', '/root/autoresearch', copy=True, ignore=_IGNORE)
         .add_local_dir(ROOT / 'problems' / 'bin_packing_online', '/root/problems/bin_packing_online', copy=True,
                        ignore=_IGNORE)
         .run_commands('cd /root && python -c "import falsify.longpack as l; l._lib()"'))
app = modal.App(APP_NAME, image=image)
_SANDBOXED = dict(cpu=CPU, memory=MEMORY_MB, scaledown_window=SCALEDOWN_S, max_containers=MAX_CONTAINERS,
                  restrict_modal_access=True, block_network=True)


@app.function(timeout=ASSESS_TIMEOUT, **_SANDBOXED)
def assess_remote(payload):
    from falsify.code_eval import assess
    return assess(payload)


@app.function(timeout=SHARD_TIMEOUT, **_SANDBOXED)
def shard_remote(payload):
    from falsify.code_eval import pack_shard
    return pack_shard(payload)


class ModalBudgetExceeded(RuntimeError):
    pass


class ModalLedger:
    def __init__(self, path, cap_usd, prior_usd=0.0):
        self.path, self.cap, self.prior = Path(path), cap_usd, prior_usd
        self.spent = self.reserved = 0.0
        self.lock = threading.Lock()

    def reserve(self, amount):
        with self.lock:
            if self.prior + self.spent + self.reserved + amount > self.cap + 1e-12:
                raise ModalBudgetExceeded(f'Modal reservation ${amount:.4f} could pass the ${self.cap:.2f} cap '
                                          f'(earlier ${self.prior:.4f}, spent ${self.spent:.4f}, open ${self.reserved:.4f})')
            self.reserved += amount

    def settle(self, reserved, charged, record):
        with self.lock:
            self.reserved -= reserved
            self.spent += charged
            with self.path.open('a') as f:
                f.write(json.dumps({'time': time.time(), **record, 'reserved_usd': reserved,
                                    'estimated_usd': charged}) + '\n')


def prior_modal_spend(paths):
    total = 0.0
    for p in paths:
        for line in Path(p).read_text().splitlines():
            if line.strip():
                total += json.loads(line).get('estimated_usd', 0.0)
    return total


class ModalExecutor:
    """Context manager: runs the app ephemerally and exposes assess() and shards()."""

    def __init__(self, ledger):
        self.ledger = ledger
        self._ctx = None
        self.phase_started = None

    def __enter__(self):
        self._ctx = app.run()
        self._ctx.__enter__()
        self.phase_started = time.time()
        return self

    def __exit__(self, *exc):
        self.close_phase('end of app run')
        return self._ctx.__exit__(*exc)

    def close_phase(self, label):
        """Charge the idle tail of every container that may still be up (upper bound)."""
        idle = SCALEDOWN_S * MAX_CONTAINERS * RATE
        self.ledger.settle(0.0, idle, {'kind': 'idle_estimate', 'label': label,
                                       'seconds': SCALEDOWN_S * MAX_CONTAINERS})

    def assess(self, payload, tag=''):
        reserve = 1.25 * ASSESS_TIMEOUT * RATE
        self.ledger.reserve(reserve)
        started = time.time()
        try:
            result = assess_remote.remote(payload)
        except Exception as exc:  # noqa: BLE001 - logged and reported as an evaluation failure
            wall = time.time() - started
            self.ledger.settle(reserve, wall * RATE, {'kind': 'assess', 'tag': tag, 'ok': False,
                                                      'error': repr(exc)[:300], 'wall_seconds': wall})
            return {'status': 'infrastructure_error', 'error': repr(exc)[:300]}
        wall = time.time() - started
        self.ledger.settle(reserve, wall * RATE, {'kind': 'assess', 'tag': tag, 'ok': True, 'wall_seconds': wall,
                                                  'remote_seconds': result.get('seconds')})
        return result

    def shards(self, payloads, batch=100, tag=''):
        results = []
        for start in range(0, len(payloads), batch):
            chunk = payloads[start:start + batch]
            reserve = 1.25 * SHARD_TIMEOUT * RATE * len(chunk)
            self.ledger.reserve(reserve)
            started = time.time()
            out = list(shard_remote.map(chunk, return_exceptions=True))
            wall = time.time() - started
            remote = sum(r['seconds'] for r in out if isinstance(r, dict))
            failures = [repr(r)[:200] for r in out if not isinstance(r, dict)]
            # Remote compute plus a 3-second start-up allowance per input.
            charged = (remote + 3 * len(chunk)) * RATE
            self.ledger.settle(reserve, charged, {'kind': 'shards', 'tag': tag, 'inputs': len(chunk),
                                                  'remote_seconds': remote, 'wall_seconds': wall,
                                                  'failures': failures})
            results += [r if isinstance(r, dict) else {'error': repr(r)[:300], 'bins': None} for r in out]
        return results
