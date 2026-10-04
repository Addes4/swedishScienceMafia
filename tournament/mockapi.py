"""A local stand-in for the Anthropic Messages API, for zero-cost end-to-end runs.

    with MockAnthropic(seed=0) as mock:      # sets ANTHROPIC_BASE_URL and a dummy key
        ...                                  # every SDK client in the process now talks to it

Point ANTHROPIC_BASE_URL at it and the real SDK, the budget guard, ShinkaEvolve and the arms
all run unchanged; only the network is replaced. It answers POST /v1/messages, as plain JSON or
as a server-sent-event stream, and reports usage that is priced like a real call (input about
1 token per 3.5 characters; output = visible text plus a simulated 1,000-4,000 thinking tokens,
capped at max_tokens), so dollar caps bind in mock runs as they would live.

It also answers the OpenAI-compatible routes of the Hugging Face router (GET /v1/models with
per-provider prices, POST /v1/chat/completions with reasoning tokens in the usage), so the HF
path (tournament/hf.py, ShinkaEvolve's local_openai client) is exercised the same way.

Replies are shaped by the prompt: idea lists for "<idea>" prompts, a JSON list for rankers,
SEARCH/REPLACE diffs for ShinkaEvolve's diff prompts, <CODE> blocks for its rewrites, and
otherwise the current program with one numeric constant perturbed by up to 10%.
"""
import json
import os
import random
import re
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

CHARS_PER_TOKEN = 3.5
MOCK_HF_PRICES = {"deepseek-ai/DeepSeek-V4.1-Flash:deepinfra": (0.2, 0.6),
                  "deepseek-ai/DeepSeek-V4-Pro:deepinfra": (1.3, 2.6),
                  "Qwen/Qwen3.5-9B:together": (0.17, 0.25)}
FLOAT = re.compile(r"(?<![\w.])(\d+\.\d+)(?![\w.])")


def _text_of(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(b.get("text", "") for b in content if isinstance(b, dict))
    return ""


def _code_blocks(text: str):
    return re.findall(r"```(?:python)?\s*\n(.*?)```", text or "", re.S)


def _perturb_line(line: str, rng: random.Random):
    nums = list(FLOAT.finditer(line))
    if not nums:
        return None
    m = rng.choice(nums)
    value = float(m.group(1)) * rng.uniform(0.9, 1.1)
    return line[:m.start()] + f"{value:.4f}" + line[m.end():]


def mutate(code: str, rng: random.Random):
    """Perturb one float literal inside the EVOLVE block (or anywhere). Returns (new_code, old_line, new_line)."""
    lines = code.splitlines()
    start = next((i for i, l in enumerate(lines) if "EVOLVE-BLOCK-START" in l), -1)
    end = next((i for i, l in enumerate(lines) if "EVOLVE-BLOCK-END" in l), len(lines))
    candidates = [i for i in range(start + 1, end) if FLOAT.search(lines[i]) and not lines[i].lstrip().startswith("#")]
    if not candidates:
        new = code.rstrip("\n") + f"\n# mock revision {rng.randint(0, 10**6)}\n"
        return new, None, None
    i = rng.choice(candidates)
    old_line, new_line = lines[i], _perturb_line(lines[i], rng)
    lines[i] = new_line
    return "\n".join(lines) + "\n", old_line, new_line


def respond(body: dict, rng: random.Random) -> str:
    system = _text_of(body.get("system"))
    msgs = body.get("messages") or []
    user = _text_of(msgs[-1].get("content")) if msgs else ""
    blocks = _code_blocks(user)
    code = max(blocks, key=len) if blocks else ""

    if "<idea>" in user:
        k = int(re.search(r"Propose (\d+)", user).group(1)) if re.search(r"Propose (\d+)", user) else 3
        return "\n".join(f"<idea>Mock idea {rng.randint(0, 9999)}: retune constant {j} of the construction.</idea>"
                         for j in range(k))
    if "Return a JSON list with one object per idea" in user:
        n = len(re.findall(r"^\d+: ", user, re.M)) or 1
        tiers = ["favourite", "middle", "long_shot"]
        return json.dumps([{"promise": rng.choice(tiers), "p_improve": round(rng.random(), 3), "p_repeat": 0.0,
                            "kind": "parameter_tweak"} for _ in range(n)])
    if "NOVEL" in system and "NOT_NOVEL" in system:
        return "NOVEL: the mock judge considers every program novel."
    if "SEARCH/REPLACE" in system and code:
        _, old, new = mutate(code, rng)
        if old is None:
            return "<NAME>noop</NAME>\n<DESCRIPTION>No constant to change.</DESCRIPTION>\n<DIFF>\n</DIFF>"
        return ("<NAME>mock_retune</NAME>\n<DESCRIPTION>Retune one constant.</DESCRIPTION>\n<DIFF>\n"
                f"<<<<<<< SEARCH\n{old}\n=======\n{new}\n>>>>>>> REPLACE\n\n</DIFF>")
    if "<CODE>" in system and code:
        new, _, _ = mutate(code, rng)
        return (f"<NAME>mock_rewrite</NAME>\n<DESCRIPTION>Retune one constant.</DESCRIPTION>\n<CODE>\n```python\n"
                f"{new}```\n</CODE>")
    if code:
        new, _, _ = mutate(code, rng)
        return f"<change>Mock change: retune one constant of the construction.</change>\n```python\n{new}```"
    return "Mock reply: no program found in the prompt."


class _Handler(BaseHTTPRequestHandler):
    server_version = "MockAnthropic/1.0"

    def log_message(self, *args):  # keep test and job logs quiet
        pass

    def _json(self, status, payload):
        data = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("content-type", "application/json")
        self.send_header("retry-after-ms", "5")
        self.send_header("content-length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if not self.path.startswith("/v1/models"):
            self.send_error(404)
            return
        models = {}
        for pinned, (pin, pout) in self.server.mock.hf_prices.items():
            name, _, provider = pinned.partition(":")
            models.setdefault(name, []).append({"provider": provider, "status": "live",
                                                "pricing": {"input": pin, "output": pout}})
        self._json(200, {"object": "list", "data": [{"id": k, "providers": v} for k, v in models.items()]})

    def do_POST(self):
        mock = self.server.mock
        length = int(self.headers.get("content-length") or 0)
        body = json.loads(self.rfile.read(length) or b"{}")
        openai_route = self.path.startswith("/v1/chat/completions")
        if not (self.path.startswith("/v1/messages") or openai_route):
            self.send_error(404)
            return
        if openai_route:   # translate to the Messages shape respond() reads
            msgs = body.get("messages") or []
            body = dict(body, system="\n".join(m.get("content") or "" for m in msgs if m.get("role") == "system"),
                        messages=[m for m in msgs if m.get("role") != "system"],
                        max_tokens=body.get("max_tokens") or body.get("max_completion_tokens"))
        with mock.lock:
            failing = mock.fail_next > 0 or (mock.fail_after is not None and mock.requests >= mock.fail_after)
            mock.fail_next -= mock.fail_next > 0 and failing
            mock.failed += failing
        if failing:  # simulated API error (rate limit, overload, no credit, bad key), as the real API sends it
            self._json(mock.fail_status, {"type": "error", "error": {"type": mock.fail_type, "message": mock.fail_message}})
            return
        with mock.lock:
            mock.requests += 1
            rng = random.Random(f"{mock.seed}/{mock.requests}")
            mock.log.append({"model": body.get("model"), "max_tokens": body.get("max_tokens"),
                             "stream": bool(body.get("stream")), "has_fallbacks": "fallbacks" in body})
        if mock.latency:
            time.sleep(mock.latency)
        text = respond(body, rng)
        max_tokens = int(body.get("max_tokens") or 1024)
        prompt = json.dumps({"system": body.get("system"), "messages": body.get("messages")})
        input_tokens = int(len(prompt) / CHARS_PER_TOKEN) + 10
        visible = int(len(text) / CHARS_PER_TOKEN) + 1
        output_tokens = visible + rng.randint(1000, 4000)
        stop_reason = "end_turn"
        if output_tokens > max_tokens:
            output_tokens, stop_reason = max_tokens, "max_tokens"
            keep = max(0, int((max_tokens - 4000) * CHARS_PER_TOKEN))
            text = text[:keep]
        model = body.get("model", "mock")
        if openai_route:
            reasoning = output_tokens - visible if stop_reason != "max_tokens" else output_tokens
            self._json(200, {"id": f"chatcmpl-mock-{mock.requests}", "object": "chat.completion", "model": model,
                             "choices": [{"index": 0, "finish_reason": "length" if stop_reason == "max_tokens" else "stop",
                                          "message": {"role": "assistant", "content": text or None,
                                                      "reasoning_content": "mock reasoning"}}],
                             "usage": {"prompt_tokens": input_tokens, "completion_tokens": output_tokens,
                                       "total_tokens": input_tokens + output_tokens,
                                       "completion_tokens_details": {"reasoning_tokens": max(reasoning, 0)}}})
            return
        usage = {"input_tokens": input_tokens, "output_tokens": output_tokens,
                 "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0}
        if body.get("stream"):
            self._stream(model, text, usage, stop_reason)
        else:
            msg = {"id": f"msg_mock_{mock.requests}", "type": "message", "role": "assistant", "model": model,
                   "content": [{"type": "thinking", "thinking": "", "signature": "mock"}, {"type": "text", "text": text}],
                   "stop_reason": stop_reason, "stop_sequence": None, "usage": usage}
            data = json.dumps(msg).encode()
            self.send_response(200)
            self.send_header("content-type", "application/json")
            self.send_header("content-length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

    def _stream(self, model, text, usage, stop_reason):
        self.send_response(200)
        self.send_header("content-type", "text/event-stream")
        self.send_header("cache-control", "no-cache")
        self.end_headers()

        def event(kind, payload):
            self.wfile.write(f"event: {kind}\ndata: {json.dumps(payload)}\n\n".encode())

        mock = self.server.mock
        with mock.lock:
            in_stream_error = mock.stream_error_next > 0
            mock.stream_error_next -= in_stream_error
            mock.failed += in_stream_error
        if in_stream_error:  # an error delivered inside an opened stream, as the API sometimes does
            event("error", {"type": "error", "error": {"type": mock.fail_type, "message": mock.fail_message}})
            self.wfile.flush()
            return

        start_usage = dict(usage, output_tokens=1)
        event("message_start", {"type": "message_start", "message": {
            "id": "msg_mock", "type": "message", "role": "assistant", "model": model, "content": [],
            "stop_reason": None, "stop_sequence": None, "usage": start_usage}})
        event("content_block_start", {"type": "content_block_start", "index": 0,
                                      "content_block": {"type": "text", "text": ""}})
        for i in range(0, len(text), 2000):
            event("content_block_delta", {"type": "content_block_delta", "index": 0,
                                          "delta": {"type": "text_delta", "text": text[i:i + 2000]}})
        event("content_block_stop", {"type": "content_block_stop", "index": 0})
        event("message_delta", {"type": "message_delta", "delta": {"stop_reason": stop_reason, "stop_sequence": None},
                                "usage": {"output_tokens": usage["output_tokens"]}})
        event("message_stop", {"type": "message_stop"})
        self.wfile.flush()


class MockAnthropic:
    """Runs the mock API on 127.0.0.1 in a background thread."""

    def __init__(self, seed: int = 0, latency: float = 0.05, set_env: bool = True):
        self.seed, self.latency, self.set_env = seed, latency, set_env
        self.requests = 0
        self.fail_next = 0            # answer this many requests with fail_status first
        self.fail_status = 429
        self.fail_type = "rate_limit_error"
        self.fail_message = "mock"
        self.failed = 0               # requests answered with an error
        self.stream_error_next = 0    # streaming requests that get an error event inside the stream
        self.fail_after = None        # once this many requests have succeeded, fail every later one
        self.hf_prices = dict(MOCK_HF_PRICES)   # pinned "model:provider" -> ($/M input, $/M output)
        self.log = []
        self.lock = threading.Lock()
        self.server = None
        self._saved = {}

    @property
    def url(self) -> str:
        return f"http://127.0.0.1:{self.server.server_address[1]}"

    def start(self):
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
        self.server.daemon_threads = True
        self.server.mock = self
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        if self.set_env:
            for k, v in (("ANTHROPIC_BASE_URL", self.url), ("ANTHROPIC_API_KEY", "mock-key-not-a-secret"),
                         ("TOURNAMENT_HF_BASE_URL", self.url + "/v1"), ("HF_TOKEN", "mock-hf-token-not-a-secret")):
                self._saved[k] = os.environ.get(k)
                os.environ[k] = v
            os.environ.pop("ANTHROPIC_AUTH_TOKEN", None)
        return self

    def stop(self):
        if self.server:
            self.server.shutdown()
            self.server.server_close()
        for k, v in self._saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v

    def __enter__(self):
        return self.start()

    def __exit__(self, *exc):
        self.stop()
