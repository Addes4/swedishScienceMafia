"""Claude calls for the triage loop: propose ideas, implement an idea. Tracks cost per call.

Opus 5.5 and Sonnet 5.5 requests opt into Anthropic's server-side refusal fallback, so a
request a safety classifier declines is retried on a fallback model inside the same call.
"""
import re
import time
from dataclasses import dataclass
from typing import List, Optional

import anthropic

# $ per million tokens (input, output). Thinking tokens are billed as output.
PRICES = {
    "claude-fable-5-1": (10.0, 50.0),
    "claude-opus-5-5": (4.0, 20.0),
    "claude-opus-5": (5.0, 25.0),
    "claude-opus-4-8": (5.0, 25.0),
    "claude-sonnet-5-5": (2.0, 10.0),
    "claude-haiku-4-5": (1.0, 5.0),
}
_FALLBACK_MODELS = ("claude-opus-5-5", "claude-sonnet-5-5")
_EFFORT_MODELS = ("claude-opus-5-5", "claude-sonnet-5-5", "claude-fable-5-1")


@dataclass
class CallResult:
    text: Optional[str]
    model: str
    cost: float
    input_tokens: int
    output_tokens: int
    seconds: float
    refused: bool = False
    served_by: Optional[str] = None


def _cost(model: str, usage) -> float:
    pin, pout = PRICES.get(model, PRICES["claude-opus-5-5"])
    cached = (getattr(usage, "cache_read_input_tokens", 0) or 0) * pin * 0.1
    written = (getattr(usage, "cache_creation_input_tokens", 0) or 0) * pin * 1.25
    return (usage.input_tokens * pin + usage.output_tokens * pout + cached + written) / 1e6


class Claude:
    def __init__(self, timeout: float = 900.0):
        self.client = anthropic.Anthropic(timeout=timeout, max_retries=4)

    def call(self, model: str, system: str, user: str, max_tokens: int = 32000, effort: Optional[str] = None) -> CallResult:
        kwargs = dict(model=model, max_tokens=max_tokens, system=system,
                      messages=[{"role": "user", "content": user}])
        if effort and model in _EFFORT_MODELS:
            kwargs["output_config"] = {"effort": effort}
        if model in _FALLBACK_MODELS:
            kwargs["betas"] = ["server-side-fallback-2026-07-01"]
            kwargs["fallbacks"] = "default"
        t0 = time.time()
        with self.client.beta.messages.stream(**kwargs) as stream:
            msg = stream.get_final_message()
        served = getattr(msg, "model", model) or model
        cost = _cost(served if served in PRICES else model, msg.usage)
        res = CallResult(text=None, model=model, served_by=served, cost=cost,
                         input_tokens=msg.usage.input_tokens, output_tokens=msg.usage.output_tokens,
                         seconds=time.time() - t0)
        if msg.stop_reason == "refusal":
            res.refused = True
            return res
        res.text = "".join(b.text for b in msg.content if getattr(b, "type", None) == "text")
        return res


IDEA_SYSTEM = """You are a research mathematician and algorithm designer working on the problem below.
You propose concrete, distinct ideas for improving the current best program. Each idea must be
implementable as a change to that program in one go. Mix safe refinements with bold long shots:
a structurally new construction is worth proposing even if it might fail.

PROBLEM
{problem}"""

IDEA_USER = """Current best program (score {score:.6g}, where 1.0 means matching the best known result):
```python
{code}
```

Evaluator feedback on it:
{feedback}

Ideas already tried, with outcomes (most recent last):
{history}

Propose {k} new ideas that differ from each other and from ideas already tried.
Return each idea as one or two sentences inside <idea></idea> tags, and nothing else."""

IMPLEMENT_SYSTEM = """You are an expert Python programmer implementing one research idea for the problem below.

PROBLEM
{problem}

RULES
- Return the complete new program in a single ```python code block, and nothing after it.
- Keep the required function name and signature.
- Use only the standard library, numpy and scipy. Do not read or write files, start processes,
  use the network, or use eval/exec/importlib: such programs are rejected.
- Respect the time limit stated in the problem."""

IMPLEMENT_USER = """Current best program (score {score:.6g}):
```python
{code}
```

Evaluator feedback on it:
{feedback}

Implement this idea:
{idea}"""

REFINE_USER = """This program came from the idea "{idea}" and improved the score to {score:.6g}
(the previous best was {prev:.6g}):
```python
{code}
```

Evaluator feedback on it:
{feedback}

Refine it: keep what made it better, fix weaknesses, and push the score further."""


def parse_ideas(text: str, k: int) -> List[str]:
    ideas = [re.sub(r"\s+", " ", m).strip() for m in re.findall(r"<idea>(.*?)</idea>", text or "", re.S)]
    return [i for i in ideas if i][:k]


def parse_code(text: str) -> Optional[str]:
    blocks = re.findall(r"```(?:python)?\s*\n(.*?)```", text or "", re.S)
    return max(blocks, key=len) if blocks else None
