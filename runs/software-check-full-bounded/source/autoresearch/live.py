"""Auditable OpenAI calls with a campaign-wide, crash-safe spend reservation.

No SDK retries, tools, remote execution, or secret values in artifacts.
Prices are standard short-context USD/MTok, checked 2026-10-03.
"""
import fcntl
import json
import math
import os
import time
import uuid
from contextlib import contextmanager
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .env import load_env, require

PRICE_SOURCE = 'https://developers.openai.com/api/docs/pricing'
PRICES = {
    'gpt-6.1-sol': (2., .10, 2.5, 10.),
    'gpt-6-sol': (2., .20, 2.5, 10.),
    'gpt-6-luna': (.10, .01, .125, .50),
    'gpt-6-astra': (10., 1., 12.5, 50.),
    'gpt-5.4-mini': (.75, .075, .9375, 4.5),
}


def dump(path, value):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')


def append(path, value):
    with Path(path).open('a') as f:
        f.write(json.dumps(value, allow_nan=False) + '\n')
        f.flush()
        os.fsync(f.fileno())


class BudgetExceeded(RuntimeError):
    pass


class Ledger:
    def __init__(self, path, cap=25.):
        self.path, self.cap = Path(path), float(cap)
        if not 0 < self.cap <= 25:
            raise ValueError('Campaign cap must be within the user-approved USD 25')
        self.path.parent.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def locked(self):
        with self.path.with_suffix('.lock').open('a') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            yield
            fcntl.flock(lock, fcntl.LOCK_UN)

    def records(self):
        return [json.loads(s) for s in self.path.read_text().splitlines()] if self.path.exists() else []

    def totals(self, run=None):
        recs = self.records()
        opened, settled = {}, {}
        for r in recs:
            if run is not None and r.get('run') != run:
                continue
            if r['event'] == 'reserve': opened[r['id']] = r['usd']
            elif r['event'] == 'settle': settled[r['id']] = r['usd']
        pending = {k: v for k, v in opened.items() if k not in settled}
        usage = [r.get('usage', {}) for r in recs if r['event'] == 'settle']
        return {'actual_usd': sum(settled.values()), 'reserved_usd': sum(pending.values()),
                'committed_usd': sum(settled.values()) + sum(pending.values()),
                'unresolved_requests': len(pending), 'attempts': len(opened),
                'settled_requests': len(settled),
                'input_tokens': sum(u.get('input_tokens', 0) for u in usage),
                'output_tokens': sum(u.get('output_tokens', 0) for u in usage)}

    def reserve(self, run, usd, run_cap, metadata):
        if not math.isfinite(usd) or usd <= 0: raise ValueError('Invalid reservation')
        with self.locked():
            if self.totals()['committed_usd'] + usd > self.cap + 1e-10:
                raise BudgetExceeded('Campaign spend ceiling reached')
            if self.totals(run)['committed_usd'] + usd > run_cap + 1e-10:
                raise BudgetExceeded('Run spend ceiling reached')
            rid = uuid.uuid4().hex
            append(self.path, {'event': 'reserve', 'id': rid, 'run': run, 'usd': usd,
                               'time': time.time(), **metadata})
            return rid

    def settle(self, rid, run, usd, **metadata):
        if not math.isfinite(usd) or usd < 0: raise ValueError('Invalid settlement')
        with self.locked():
            recs = self.records()
            reservation = next((r for r in recs if r['event'] == 'reserve' and r['id'] == rid), None)
            if reservation is None or reservation['run'] != run:
                raise ValueError('No matching reservation')
            if any(r['event'] == 'settle' and r['id'] == rid for r in recs):
                raise ValueError('Reservation already settled')
            append(self.path, {'event': 'settle', 'id': rid, 'run': run, 'usd': usd,
                               'time': time.time(), **metadata})


def price(model, usage):
    if model not in PRICES: raise ValueError('Unpriced model')
    pin, pcached, pwrite, pout = PRICES[model]
    detail = usage.get('input_tokens_details') or {}
    ni, no = usage['input_tokens'], usage['output_tokens']
    cached, writes = detail.get('cached_tokens', 0), detail.get('cache_write_tokens', 0)
    if min(ni, no, cached, writes) < 0 or cached + writes > ni:
        raise ValueError('Invalid provider usage')
    return ((ni-cached-writes)*pin + cached*pcached + writes*pwrite + no*pout)/1e6


class LiveClient:
    def __init__(self, run_dir, ledger, run_cap, input_limit=6000, timeout=180):
        self.out, self.ledger = Path(run_dir), ledger
        self.run, self.cap = self.out.name, run_cap
        self.input_limit, self.timeout = input_limit, timeout
        (self.out/'calls').mkdir(parents=True, exist_ok=True)
        load_env()

    def request(self, endpoint, payload):
        require('OPENAI_API_KEY', 'live research requires it')
        req = Request('https://api.openai.com/v1/' + endpoint,
                      data=json.dumps(payload).encode(), method='POST',
                      headers={'Authorization': 'Bearer '+os.environ['OPENAI_API_KEY'],
                               'Content-Type': 'application/json'})
        try:
            with urlopen(req, timeout=self.timeout) as r:
                return json.load(r)
        except HTTPError as exc:
            raise RuntimeError(f'OpenAI HTTP {exc.code}; response body withheld') from None
        except (URLError, TimeoutError, OSError):
            raise RuntimeError('OpenAI network request failed; response body withheld') from None

    def call(self, model, system, user, max_tokens=4096, schema=None, effort='low', tag='proposal'):
        if model not in PRICES: raise ValueError('Model requires a verified price entry')
        payload = {'model': model, 'instructions': system, 'input': user,
                   'max_output_tokens': max_tokens, 'store': False,
                   'service_tier': 'default', 'reasoning': {'effort': effort}}
        if schema:
            payload['text'] = {'format': {'type': 'json_schema', 'name': 'research_output',
                                         'strict': True, 'schema': schema}}
        count_payload = {k: payload[k] for k in ('model', 'instructions', 'input', 'text') if k in payload}
        counted = self.request('responses/input_tokens', count_payload)['input_tokens']
        if counted > self.input_limit:
            raise ValueError(f'Input has {counted} tokens; limit {self.input_limit}')
        # Reserve the entire configured input allowance at the larger input/write rate.
        # This covers token-count overhead and any implicit cache-write charge.
        rates = PRICES[model]
        reserve = (self.input_limit * max(rates[:3]) + max_tokens*rates[3])/1e6
        rid = self.ledger.reserve(self.run, reserve, self.cap,
                                  {'model': model, 'tag': tag, 'counted_input': counted,
                                   'max_output_tokens': max_tokens, 'price_source': PRICE_SOURCE})
        dump(self.out/'calls'/f'{rid}-request.json', {'payload': payload, 'counted_input_tokens': counted})
        start = time.monotonic()
        try:
            raw = self.request('responses', payload)
        except Exception:
            append(self.out/'usage.jsonl', {'id': rid, 'tag': tag, 'model': model,
                                          'status': 'unresolved', 'reserved_usd': reserve})
            raise
        dump(self.out/'calls'/f'{rid}-response.json', raw)
        usage = raw.get('usage')
        if not usage:
            raise RuntimeError('Provider response omitted usage; reservation retained')
        served = raw.get('model', model)
        if served != model and not served.startswith(model+'-'):
            raise RuntimeError('Unexpected served model; reservation retained for reconciliation')
        cost = price(model, usage)
        self.ledger.settle(rid, self.run, cost, model=model, served_model=served,
                           usage=usage, request_id=raw.get('id'), status=raw.get('status'))
        text = ''.join(c.get('text', '') for item in raw.get('output', [])
                       if item.get('type') == 'message' for c in item.get('content', [])
                       if c.get('type') == 'output_text')
        rec = {'id': rid, 'tag': tag, 'model': model, 'served_model': served,
               'status': raw.get('status'), 'usage': usage, 'usd': cost,
               'seconds': time.monotonic()-start, 'text': text}
        append(self.out/'usage.jsonl', {k: v for k, v in rec.items() if k != 'text'})
        if cost > reserve + 1e-10:
            raise RuntimeError('Actual cost exceeded reservation; halt and reconcile')
        return rec
