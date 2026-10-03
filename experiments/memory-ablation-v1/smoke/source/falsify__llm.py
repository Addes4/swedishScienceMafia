"""Spend-capped Claude proposal calls for closed-loop search, plus an offline mock.

Every request reserves its worst-case cost before it is sent and is refused if that
reservation could take spending past the cap. Every attempt, including failures, is
appended to usage.jsonl. Authentication values are never read, printed or logged here:
the SDK finds ANTHROPIC_API_KEY itself (loaded from .env by autoresearch.env).
"""
import hashlib
import json
import math
import random
import threading
import time
from pathlib import Path
from types import SimpleNamespace

from autoresearch.claude import PRICES

# Margin added to the byte-length bound on input tokens: message framing and the
# structured-output grammar instructions the API adds to the prompt.
INPUT_OVERHEAD_TOKENS = 2000


class BudgetExceeded(RuntimeError):
    """A request was refused because its worst-case cost could break the cap."""


def worst_case_cost(model, system, user, schema, max_tokens):
    """Upper bound in USD: at most one input token per UTF-8 byte, plus overhead."""
    pin, pout = PRICES[model]
    nbytes = len(system.encode()) + len(user.encode()) + len(json.dumps(schema).encode())
    return ((nbytes + INPUT_OVERHEAD_TOKENS) * pin + max_tokens * pout) / 1e6


def actual_cost(model, usage):
    pin, pout = PRICES[model]
    cached = (getattr(usage, 'cache_read_input_tokens', 0) or 0) * pin * 0.1
    written = (getattr(usage, 'cache_creation_input_tokens', 0) or 0) * pin * 1.25
    return (usage.input_tokens * pin + usage.output_tokens * pout + cached + written) / 1e6


def prior_spend(paths):
    """Sum of charged USD in earlier usage.jsonl files (for a cap across invocations)."""
    total = 0.0
    for path in paths:
        path = Path(path)
        if not path.exists():
            continue
        for line in path.read_text().splitlines():
            if line.strip():
                record = json.loads(line)
                if record.get('client') != 'mock':
                    total += record.get('charged_usd', 0.0)
    return total


class SpendLedger:
    """Thread-safe reservation ledger. `cap_usd` covers this invocation; `total_cap_usd`
    also counts `prior_usd` spent by earlier invocations."""

    def __init__(self, usage_path, cap_usd, prior_usd=0.0, total_cap_usd=None, client_label='anthropic'):
        self.client_label = client_label
        self.path = Path(usage_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.cap, self.prior, self.total_cap = cap_usd, prior_usd, total_cap_usd
        self.spent = 0.0
        self.reserved = 0.0
        self.lock = threading.Lock()

    def reserve(self, amount):
        with self.lock:
            committed = self.spent + self.reserved + amount
            if committed > self.cap + 1e-12:
                raise BudgetExceeded(f'reservation ${amount:.4f} would exceed the ${self.cap:.2f} cap '
                                     f'(spent ${self.spent:.4f}, reserved ${self.reserved:.4f})')
            if self.total_cap is not None and self.prior + committed > self.total_cap + 1e-12:
                raise BudgetExceeded(f'reservation would exceed the ${self.total_cap:.2f} total cap '
                                     f'(earlier ${self.prior:.4f})')
            self.reserved += amount

    def settle(self, reserved, charged, record):
        record = {**record, 'reserved_usd': reserved, 'charged_usd': charged}
        with self.lock:
            self.reserved -= reserved
            self.spent += charged
            self._append(record)
        return record

    def log(self, record):
        with self.lock:
            self._append({**record, 'reserved_usd': 0.0, 'charged_usd': 0.0})

    def _append(self, record):
        record = {'time': time.time(), 'client': self.client_label, **record}
        with self.path.open('a') as f:
            f.write(json.dumps(record) + '\n')


def _retryable(exc):
    import anthropic
    if isinstance(exc, (anthropic.APIConnectionError, anthropic.APITimeoutError)):
        return True
    if isinstance(exc, anthropic.APIStatusError):
        return exc.status_code == 429 or exc.status_code >= 500
    return False


class Proposer:
    """One structured proposal per call. Retries transport failures (each attempt is
    reserved and logged separately) so that every run makes the same number of calls."""

    def __init__(self, ledger, model='claude-haiku-4-5', max_tokens=1024, client=None,
                 max_attempts=5, backoff_s=2.0):
        if model not in PRICES:
            raise ValueError(f'No price for {model}; cannot enforce the spend cap')
        if client is None:
            import anthropic
            client = anthropic.Anthropic(max_retries=0, timeout=90.0)
        self.client, self.ledger, self.model = client, ledger, model
        self.max_tokens, self.max_attempts, self.backoff_s = max_tokens, max_attempts, backoff_s

    def count_tokens(self, text, tag):
        """Exact input-token count of `text` as a lone user message (free endpoint)."""
        try:
            n = self.client.messages.count_tokens(
                model=self.model, messages=[{'role': 'user', 'content': text}]).input_tokens
        except Exception as exc:  # noqa: BLE001 - logged, caller falls back to an estimate
            self.ledger.log({'kind': 'count_tokens', 'tag': tag, 'status': 'error',
                             'error': type(exc).__name__})
            return None
        self.ledger.log({'kind': 'count_tokens', 'tag': tag, 'status': 'ok', 'input_tokens': n})
        return n

    def propose(self, system, user, schema, tag):
        import anthropic
        reserve = worst_case_cost(self.model, system, user, schema, self.max_tokens)
        attempts = []
        for attempt in range(self.max_attempts):
            self.ledger.reserve(reserve)  # raises BudgetExceeded before anything is sent
            started = time.time()
            base = {'kind': 'messages', 'tag': tag, 'attempt': attempt, 'model': self.model}
            try:
                msg = self.client.messages.create(
                    model=self.model, max_tokens=self.max_tokens, system=system,
                    messages=[{'role': 'user', 'content': user}],
                    output_config={'format': {'type': 'json_schema', 'schema': schema}})
            except Exception as exc:  # noqa: BLE001
                status_code = getattr(exc, 'status_code', None)
                # HTTP error responses are not billed; a dropped connection might have been.
                charged = 0.0 if isinstance(exc, anthropic.APIStatusError) else reserve
                record = {**base, 'status': 'error', 'error': type(exc).__name__,
                          'http_status': status_code, 'seconds': time.time() - started,
                          'charged_is_upper_bound': charged > 0}
                attempts.append(self.ledger.settle(reserve, charged, record))
                if not _retryable(exc) or attempt + 1 == self.max_attempts:
                    return {'status': 'api_error', 'text': None, 'attempts': attempts}
                time.sleep(self.backoff_s * 2 ** attempt)
                continue
            served = getattr(msg, 'model', self.model) or self.model
            cost = actual_cost(served if served in PRICES else self.model, msg.usage)
            text = ''.join(b.text for b in msg.content if getattr(b, 'type', None) == 'text')
            status = {'end_turn': 'ok', 'max_tokens': 'truncated', 'refusal': 'refusal'}.get(
                msg.stop_reason, str(msg.stop_reason))
            record = {**base, 'status': status, 'served_by': served,
                      'request_id': getattr(msg, 'id', None),
                      'input_tokens': msg.usage.input_tokens, 'output_tokens': msg.usage.output_tokens,
                      'seconds': time.time() - started, 'cost_usd': cost}
            attempts.append(self.ledger.settle(reserve, cost, record))
            return {'status': status, 'text': text, 'attempts': attempts,
                    'input_tokens': msg.usage.input_tokens, 'output_tokens': msg.usage.output_tokens,
                    'cost_usd': cost, 'request_id': getattr(msg, 'id', None), 'served_by': served}
        raise AssertionError('unreachable')


class MockClient:
    """Offline stand-in shaped like anthropic.Anthropic for end-to-end tests.

    Proposes a random small perturbation of best-fit (20 weights), occasionally an
    out-of-range weight. Token counts are len(text)/3.3. `fail_first` raises a
    connection error on the first n create calls to exercise the retry path."""

    def __init__(self, seed=0, fail_first=0, n_features=20, keys=None):
        self.rng = random.Random(seed)
        self.lock = threading.Lock()
        self.fail_first = fail_first
        self.calls = 0
        self.keys = keys or [f'w{j:02d}' for j in range(n_features)]
        self.messages = SimpleNamespace(create=self._create, count_tokens=self._count)

    @staticmethod
    def _tokens(text):
        return max(1, math.ceil(len(text) / 3.3))

    def _count(self, model, messages, **_):
        return SimpleNamespace(input_tokens=sum(self._tokens(m['content']) for m in messages))

    def _create(self, model, max_tokens, system, messages, output_config=None, **_):
        with self.lock:
            self.calls += 1
            if self.calls <= self.fail_first:
                import anthropic
                import httpx2
                raise anthropic.APIConnectionError(request=httpx2.Request('POST', 'https://mock.invalid'))
            prompt = system + messages[-1]['content']
            rng = random.Random(hashlib.sha256(f'{self.rng.random()}{prompt}'.encode()).hexdigest())
        keys = self.keys
        try:  # use the weight keys of the requested schema when there is one
            keys = output_config['format']['schema']['properties']['weights']['required']
        except (TypeError, KeyError):
            pass
        weights = {k: 0.0 for k in keys}
        weights[keys[0]] = -1.0
        for _ in range(rng.choice([1, 2, 3])):
            weights[rng.choice(keys)] += rng.gauss(0, rng.choice([0.05, 0.3, 1.0]))
        if rng.random() < 0.05:
            weights[keys[-1]] = 40.0  # out of range: exercises invalid-proposal handling
        body = json.dumps({'name': f'mock_{rng.randrange(10**6)}', 'hypothesis': 'Mock perturbation.',
                           'falsification': 'More bins than best-fit on the fixed suite.',
                           'weights': weights})
        usage = SimpleNamespace(input_tokens=self._tokens(prompt), output_tokens=self._tokens(body),
                                cache_read_input_tokens=0, cache_creation_input_tokens=0)
        return SimpleNamespace(content=[SimpleNamespace(type='text', text=body)], stop_reason='end_turn',
                               model=model, usage=usage, id=f'mock_{self.calls}')
