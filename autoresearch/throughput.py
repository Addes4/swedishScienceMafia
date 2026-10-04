"""Opt-in, cross-process rate scheduling; spend accounting stays in LiveClient.

One in-flight request per model, at most two per ledger. Only numeric rate headers
are recorded. Other clients and model-family limits can still cause rejections.
"""
import fcntl
import hashlib
import json
import math
import os
import re
import time
import uuid
from contextlib import contextmanager
from email.utils import parsedate_to_datetime
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .env import require
from .live import LiveClient, append


def duration(value):
    """Parse provider reset durations (e.g. 1m2.5s or 500ms), not arbitrary text."""
    s = str(value or '').strip()
    if re.fullmatch(r'\d+(?:\.\d+)?', s):
        return float(s)
    parts = re.findall(r'(\d+(?:\.\d+)?)(ms|s|m|h)', s)
    if not parts or ''.join(n + u for n, u in parts) != s:
        return None
    return sum(float(n) * {'ms': .001, 's': 1, 'm': 60, 'h': 3600}[u] for n, u in parts)


def retry_after(headers, now):
    value = headers.get('retry-after', '')
    seconds = duration(value)
    if seconds is not None:
        return seconds
    try:
        return max(0., parsedate_to_datetime(value).timestamp() - now)
    except (TypeError, ValueError, OverflowError):
        return None


def rate_headers(headers):
    safe = {}
    for kind in ('requests', 'tokens', 'project-tokens'):
        for field in ('limit', 'remaining', 'reset'):
            name = f'x-ratelimit-{field}-{kind}'
            raw = headers.get(name)
            if raw is None:
                continue
            try:
                value = duration(raw) if field == 'reset' else float(raw)
                if value is not None and math.isfinite(value) and value >= 0:
                    safe[name] = value
            except (ValueError, TypeError):
                pass
    return safe


class RateCoordinator:
    def __init__(self, ledger_path, max_inflight=2, max_wait=300):
        self.path = ledger_path.with_suffix('.rates.json')
        self.max_inflight, self.max_wait = max_inflight, max_wait

    @contextmanager
    def state(self):
        with self.path.with_suffix('.lock').open('a') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            data = json.loads(self.path.read_text()) if self.path.exists() else {'leases': {}, 'buckets': {}}
            yield data
            temporary = self.path.with_suffix('.tmp')
            temporary.write_text(json.dumps(data, allow_nan=False))
            os.replace(temporary, self.path)

    def acquire(self, model, tokens, timeout):
        started = time.monotonic()
        while True:
            now = time.time()
            with self.state() as data:
                leases = data['leases'] = {k: v for k, v in data['leases'].items() if v['expires'] > now}
                delay = .1 if len(leases) >= self.max_inflight or any(v['model'] == model for v in leases.values()) else 0.
                scopes = ((model + ':requests', 1), (model + ':tokens', tokens), ('project-tokens', tokens))
                for scope, amount in scopes:
                    b = data['buckets'].get(scope, {})
                    delay = max(delay, b.get('blocked_until', 0) - now)
                    if b.get('reset_at', 0) > now and b.get('remaining', amount) < amount:
                        delay = max(delay, b['reset_at'] - now)
                    if amount and b.get('limit', amount) < amount:
                        raise RuntimeError('Request token allowance exceeds observed rate limit; reduce max output/input allowance')
                if delay <= 0:
                    ticket = uuid.uuid4().hex
                    leases[ticket] = {'model': model, 'expires': now + timeout + 30}
                    for scope, amount in scopes:
                        b = data['buckets'].get(scope, {})
                        if b.get('reset_at', 0) > now and 'remaining' in b:
                            b['remaining'] = max(0, b['remaining'] - amount)
                    return ticket, time.monotonic() - started
            if time.monotonic() - started + delay > self.max_wait:
                raise RuntimeError('Rate-limit wait exceeds 300 seconds; defer this run')
            time.sleep(min(delay, 1.))

    def release(self, ticket, model, headers, cooldown=0):
        now = time.time()
        safe = rate_headers(headers)
        with self.state() as data:
            data['leases'].pop(ticket, None)
            for kind in ('requests', 'tokens', 'project-tokens'):
                scope = kind if kind == 'project-tokens' else model + ':' + kind
                b = data['buckets'].setdefault(scope, {})
                reset = safe.get(f'x-ratelimit-reset-{kind}')
                remaining = safe.get(f'x-ratelimit-remaining-{kind}')
                limit = safe.get(f'x-ratelimit-limit-{kind}')
                if remaining is not None:
                    # Concurrent models may return project snapshots out of order.
                    if kind == 'project-tokens' and b.get('reset_at', 0) > now:
                        remaining = min(remaining, b.get('remaining', remaining))
                    b['remaining'] = remaining
                    b['reset_at'] = now + (reset if reset is not None else 60.)
                if limit is not None:
                    b['limit'] = limit
            if cooldown:
                b = data['buckets'][model + ':requests']
                b['blocked_until'] = max(b.get('blocked_until', 0), now + cooldown)
        return safe


class HeaderClient(LiveClient):
    """Use the same reservations/usage artifacts as LiveClient, with a new transport."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rates = RateCoordinator(self.ledger.path)
        self.counts = {}

    def request(self, endpoint, payload):
        require('OPENAI_API_KEY', 'live research requires it')
        model = payload['model']
        count_payload = {k: payload[k] for k in ('model', 'instructions', 'input', 'text') if k in payload}
        count_key = hashlib.sha256(json.dumps(count_payload, sort_keys=True).encode()).hexdigest()
        tokens = self.counts.get(count_key, self.input_limit) + payload.get('max_output_tokens', 0) if endpoint == 'responses' else 0
        request = Request('https://api.openai.com/v1/' + endpoint,
                          data=json.dumps(payload).encode(), method='POST',
                          headers={'Authorization': 'Bearer ' + os.environ['OPENAI_API_KEY'],
                                   'Content-Type': 'application/json'})
        for attempt in range(4):
            ticket, waited = self.rates.acquire(model, tokens, self.timeout)
            headers, cooldown, status, code = {}, 0., None, None
            started = time.monotonic()
            try:
                with urlopen(request, timeout=self.timeout) as response:
                    headers, status = response.headers, response.status
                    result = json.load(response)
                    if endpoint == 'responses/input_tokens':
                        self.counts[count_key] = result['input_tokens']
                    return result
            except HTTPError as exc:
                headers, status = exc.headers or {}, exc.code
                try:
                    code = json.loads(exc.read()).get('error', {}).get('code', 'unknown')
                except (ValueError, AttributeError):
                    code = 'unknown'
                if not isinstance(code, str) or not re.fullmatch(r'[a-zA-Z0-9_-]{1,80}', code):
                    code = 'unknown'
                retryable = ((status == 429 and code in ('rate_limit_exceeded', 'slow_down')) or
                             (status == 503 and code == 'server_is_overloaded'))
                if retryable:
                    cooldown = retry_after(headers, time.time())
                    if cooldown is None:
                        cooldown = min(60., 2. ** (attempt + 1))
                    cooldown = max(.1, cooldown)
                    if attempt < 3 and cooldown <= self.rates.max_wait:
                        continue
                raise RuntimeError(f'OpenAI HTTP {status}; code={code}; response body withheld') from None
            except (URLError, TimeoutError, OSError):
                # Unknown completion state: no resubmission; inherited ledger retains reservation.
                raise RuntimeError('OpenAI network request failed; response body withheld') from None
            finally:
                safe = self.rates.release(ticket, model, headers, cooldown)
                append(self.out / 'transport.jsonl', {
                    'endpoint': endpoint, 'model': model, 'attempt': attempt + 1,
                    'http_status': status, 'code': code, 'queue_seconds': waited,
                    'http_seconds': time.monotonic() - started, 'cooldown_seconds': cooldown,
                    'rate_headers': safe})
