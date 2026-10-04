"""Optional fresh Modal Sandbox per case. No API keys or repository mounts."""
import json
import math
import time
from pathlib import Path

PROFILE = {'backend': 'modal-sandbox', 'cpu': 1, 'memory_mib': 2048,
           'python': '3.14', 'numpy': '2.5.3', 'scipy': '1.18.1',
           'network': 'blocked', 'worker_threads': 1}


class ModalEvaluator:
    def __init__(self):
        try:
            import modal
            from modal.stream_type import StreamType
        except ImportError:
            raise RuntimeError('Install requirements-modal.txt to use --eval-backend modal') from None
        self.modal = modal
        self.stream_type = StreamType
        self.app = modal.App.lookup('ssm-throughput-evaluators', create_if_missing=True)
        self.image = (modal.Image.debian_slim(python_version=PROFILE['python'])
                      .pip_install('numpy==' + PROFILE['numpy'], 'scipy==' + PROFILE['scipy'])
                      .add_local_file(Path(__file__).with_name('research_worker.py'),
                                      '/opt/research_worker.py', copy=True))
        # Resolve/build once before worker threads begin creating Sandboxes.
        self.image.build(app=self.app)

    def run(self, source, case, mode, timeout):
        started = time.monotonic()
        sb = self.modal.Sandbox.create(
            'sleep', str(math.ceil(timeout) + 90), app=self.app, image=self.image,
            cpu=(1., 1.), memory=(2048, 2048), timeout=math.ceil(timeout) + 90,
            block_network=True, env={'OPENBLAS_NUM_THREADS': '1', 'OMP_NUM_THREADS': '1',
                                     'MKL_NUM_THREADS': '1'})
        result = None
        try:
            sb.filesystem.write_text(source, '/tmp/candidate.py')
            sb.filesystem.write_text(json.dumps(case, allow_nan=False), '/tmp/input.json')
            proc = sb.exec('timeout', '-k', '1s', str(timeout) + 's',
                           'python', '-I', '/opt/research_worker.py', '/tmp/candidate.py', mode,
                           '/tmp/input.json', '/tmp/output.json', timeout=math.ceil(timeout) + 5,
                           stdout=self.stream_type.DEVNULL, stderr=self.stream_type.DEVNULL)
            status = proc.wait()
            if status in (124, 137):
                result = {'valid': False, 'reason': f'timeout after {timeout}s'}
            elif status != 0:
                result = {'valid': False, 'reason': f'candidate process exited {status}'}
            else:
                try:
                    raw = sb.filesystem.read_text('/tmp/output.json')
                    result = {'valid': True, **json.loads(raw)}
                except (ValueError, FileNotFoundError):
                    result = {'valid': False, 'reason': 'malformed or missing result'}
        finally:
            # Infrastructure errors propagate and stop the run, rather than scoring
            # candidates as failures. Termination is attempted even on those errors.
            sb.terminate(wait=True)
        result['execution'] = {**PROFILE, 'sandbox_id': sb.object_id,
                               'wall_seconds': time.monotonic() - started, 'terminated': True}
        return result
