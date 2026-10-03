"""A deterministic stand-in for autoresearch.claude.Claude, for tests and dry runs.

It recognises the three prompt types used by the idea table (propose ideas, judge ideas,
implement an idea) and returns canned text with made-up token usage. Implementations are
drawn from a small set of erdos_squares programs (improved, unchanged, invalid, rejected,
no code, refusal) so every outcome path of the pipeline is exercised. No network access.
"""
import hashlib
import json
import re
import time

from .claude import CallResult, PRICES

IDEAS = [
    "Merge an a x a block of cells in an m x m grid into one big square and keep n - 1 small squares.",
    "Search over grid size m and merged block size a to maximise (n - 1 + a) / m.",
    "Rotate a subset of squares by 45 degrees to fill corner gaps.",
    "Use simulated annealing on square positions and sides starting from the grid.",
    "Place squares greedily from largest to smallest along the diagonal.",
    "Shrink every square slightly so a larger central square fits.",
    "Use a hexagonal arrangement of squares.",
    "Return the k x k grid but give the leftover squares tiny positive sides in the gaps.",
    "Solve a linear program over side lengths for a fixed combinatorial layout.",
    "Split the unit square into two rectangles and pack grids in each.",
    "Use the Campbell-Staton construction with k + c/k structure directly.",
    "Try both the k x k grid and the merged-block family and keep the better one.",
    "Randomly perturb the grid and keep valid improvements (hill climbing).",
    "Use a spiral layout of decreasing squares.",
    "Place one large square and recursively pack the L-shaped remainder.",
    "Stack rows of equal squares with different row heights.",
]

GOOD = '''
import math


def solve(n):
    """Grid of m x m cells with an a x a block merged into one square; keep the best family."""
    k = math.isqrt(n)
    best = (k, None)
    for m in range(1, n + 1):
        for a in range(1, m + 1):
            if m * m - a * a >= n - 1 and (n - 1 + a) / m > best[0] + 1e-12:
                best = ((n - 1 + a) / m, (m, a))
    if best[1] is None:
        side = 1.0 / k
        sq = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side) for i in range(k) for j in range(k)]
        return (sq + [(0.5, 0.5, 0.0, 0.0)] * n)[:n]
    m, a = best[1]
    s = 1.0 / m
    sq = [(a * s / 2, a * s / 2, 0.0, a * s)]
    for i in range(m):
        for j in range(m):
            if i < a and j < a:
                continue
            if len(sq) < n:
                sq.append(((i + 0.5) * s, (j + 0.5) * s, 0.0, s))
    return (sq + [(0.5, 0.5, 0.0, 0.0)] * n)[:n]
'''

SAME = '''
import math


def solve(n):
    k = math.isqrt(n)
    side = 1.0 / k
    squares = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side) for i in range(k) for j in range(k)]
    squares += [(0.5, 0.5, 0.0, 0.0)] * (n - len(squares))
    return squares[:n]
'''

INVALID = '''
def solve(n):
    return [(0.5, 0.5, 0.0, 0.6)] * n
'''

REJECTED = '''
def solve(n):
    open("/tmp/x").read()
    return [(0.5, 0.5, 0.0, 0.0)] * n
'''

PROGRAMS = {"good": GOOD, "same": SAME, "invalid": INVALID, "rejected": REJECTED}
# Probability-like weights per model for the canned outcomes (good, same, invalid, rejected, no_code, refusal).
WEIGHTS = {
    "claude-opus-5-5": (6, 2, 1, 0, 0, 0),
    "claude-sonnet-5-5": (4, 3, 2, 0, 1, 0),
    "claude-haiku-4-5": (2, 4, 2, 1, 0, 1),
}
OUTCOMES = ("good", "same", "invalid", "rejected", "no_code", "refusal")
THINKING_TOKENS = {"claude-opus-5-5": 6000, "claude-sonnet-5-5": 4000, "claude-haiku-4-5": 800}


def _h(*parts) -> int:
    return int(hashlib.sha256("|".join(map(str, parts)).encode()).hexdigest()[:12], 16)


class MockClaude:
    def __init__(self, seed: int = 0):
        self.seed = seed
        self.calls = []

    def _result(self, model, system, user, text, refused=False):
        tin = (len(system) + len(user)) // 4
        tout = len(text or "") // 4 + THINKING_TOKENS.get(model, 1000)
        pin, pout = PRICES[model]
        self.calls.append({"model": model, "system": system[:60], "user_len": len(user)})
        return CallResult(text=None if refused else text, model=model, cost=(tin * pin + tout * pout) / 1e6,
                          input_tokens=tin, output_tokens=tout, seconds=0.01, refused=refused, served_by=model)

    def call(self, model, system, user, max_tokens=32000, effort=None):
        time.sleep(0.001)
        if system.startswith("You are a research mathematician"):
            k = int(re.search(r"Propose (\d+) new ideas", user).group(1))
            start = len(re.findall(r"^- ", user, re.M))
            ideas = [IDEAS[(start + i) % len(IDEAS)] for i in range(k)]
            if start == 0 and k > 1:
                ideas[1] = ideas[0].upper() + " "   # a near-duplicate, to exercise dedupe
            return self._result(model, system, user, "\n".join(f"<idea>{i}</idea>" for i in ideas))
        if system.startswith("You judge research ideas"):
            listing = re.search(r"IDEAS\n(.*?)\n\nReturn a JSON list", user, re.S).group(1)
            items = []
            for line in listing.splitlines():
                idea = line.split(": ", 1)[-1].lower()
                good = any(w in idea for w in ("merge", "block", "family", "campbell", "l-shaped"))
                noise = (_h(self.seed, model, idea) % 100) / 100
                if model == "claude-haiku-4-5":
                    good = good if noise > 0.3 else not good
                p = min(0.95, max(0.05, (0.7 if good else 0.2) + 0.2 * (noise - 0.5)))
                items.append({"promise": "favourite" if p > 0.6 else "middle" if p > 0.3 else "long_shot",
                              "p_improve": round(p, 3), "p_repeat": 0.0, "kind": "new_construction"})
            return self._result(model, system, user, json.dumps(items))
        # implementation request
        idea = user.rsplit("Implement this idea:\n", 1)[-1].strip().lower()
        good_idea = any(w in idea for w in ("merge", "block", "family", "campbell", "l-shaped"))
        w = list(WEIGHTS.get(model, WEIGHTS["claude-sonnet-5-5"]))
        if not good_idea:
            w[0] = 0
        draw = _h(self.seed, model, idea, len(self.calls)) % sum(w)
        outcome = next(o for o, cum in zip(OUTCOMES, _cumsum(w)) if draw < cum)
        if outcome == "refusal":
            return self._result(model, system, user, "", refused=True)
        if outcome == "no_code":
            return self._result(model, system, user, "I would merge squares, but here is no code.")
        return self._result(model, system, user, f"Here is the program.\n```python\n{PROGRAMS[outcome]}```\n")


def _cumsum(w):
    out, s = [], 0
    for x in w:
        s += x
        out.append(s)
    return out
