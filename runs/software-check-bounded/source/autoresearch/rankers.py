"""Rankers: judge each idea's promise before any code is written.

Every ranker returns, per idea, a Ranking with
    promise   distribution over "favourite" / "middle" / "long_shot"
    p_improve probability the idea beats the current best (kept for calibration analysis)
    p_repeat  probability it repeats an idea that already failed
    kind      what sort of change it is (for the research log)
The loop sorts ideas by `key` and splits them into thirds, one per model tier.
"""
import json
import random
import re
import time
from dataclasses import asdict, dataclass, field
from typing import List

TIERS = ("favourite", "middle", "long_shot")
KINDS = {
    "new_construction": "A structurally different construction or representation",
    "search_method": "A different search or optimisation procedure",
    "parameter_tweak": "Adjusting constants, sizes or other parameters of the current approach",
    "bug_fix": "Fixing an error or invalid output in the current program",
    "other": "None of the above",
}
TIER_CRITERIA = {
    "favourite": "Likely to beat the current best: a well-founded, substantive change",
    "middle": "Plausible but uncertain",
    "long_shot": "Unlikely to help, though not impossible",
}
JEV_PRICE_PER_MTOK = 0.042   # input; output is free


@dataclass
class Ranking:
    promise: dict
    p_improve: float
    p_repeat: float
    kind: str
    cost: float = 0.0
    seconds: float = 0.0
    raw: dict = field(default_factory=dict)

    @property
    def key(self) -> float:
        # Expected promise (favourite 1, middle 0.5, long shot 0) and P(improve), minus a repeat penalty.
        expected = self.promise.get("favourite", 0) + 0.5 * self.promise.get("middle", 0)
        return 0.5 * expected + 0.5 * self.p_improve - 0.5 * self.p_repeat

    def to_dict(self):
        d = asdict(self)
        d["key"] = self.key
        return d


def _state(problem, best_score, best_code, history, idea):
    return {
        "problem": problem[:6000],
        "current_best_score": round(best_score, 6),
        "current_best_program": best_code[:12000],
        "recent_history": history[-20:],
        "idea": idea,
    }


class JevRanker:
    """TypeSafe's Jev: fast, typed judgements with calibrated probabilities."""
    name = "jev"

    def __init__(self, model: str = None):
        from typesafe_sdk import Choice, Noul, TypeSafeClient
        self.client = TypeSafeClient(model=model)
        self.questions = {
            "promise": Choice(instructions="How promising is the idea for beating the current best score on this problem?",
                              criteria=TIER_CRITERIA),
            "improves": Noul(instructions="Will implementing the idea produce a program that scores higher than the current best program?"),
            "repeat": Noul(instructions="Is the idea essentially the same as one in recent_history whose outcome was not an improvement?"),
            "kind": Choice(instructions="What kind of change is the idea?", criteria=KINDS),
        }

    def rank(self, problem, best_score, best_code, history, ideas) -> List[Ranking]:
        out = []
        for idea in ideas:
            t0 = time.time()
            res = self.client.system_one(state=_state(problem, best_score, best_code, history, idea), questions=self.questions)
            ans = res.answers
            tokens = res.usage.input_tokens or 0
            out.append(Ranking(
                promise=dict(ans["promise"].probabilities),
                p_improve=float(ans["improves"].noul),
                p_repeat=float(ans["repeat"].noul),
                kind=ans["kind"].choice,
                cost=tokens * JEV_PRICE_PER_MTOK / 1e6,
                seconds=time.time() - t0,
                raw={"model": res.model, "input_tokens": tokens},
            ))
        return out


class ClaudeRanker:
    """The same judgement from a Claude model (System 2 comparison), all ideas in one call."""
    name = "claude"

    def __init__(self, claude, model: str = "claude-haiku-4-5"):
        self.claude, self.model = claude, model

    def rank(self, problem, best_score, best_code, history, ideas) -> List[Ranking]:
        system = ("You judge research ideas before anyone implements them. For each idea, estimate how likely it is "
                  "to beat the current best program. Answer with JSON only.")
        listing = "\n".join(f"{i}: {idea}" for i, idea in enumerate(ideas))
        user = (f"PROBLEM\n{problem[:6000]}\n\nCURRENT BEST (score {best_score:.6g})\n```python\n{best_code[:12000]}\n```\n\n"
                f"RECENT HISTORY\n{json.dumps(history[-20:])}\n\nIDEAS\n{listing}\n\n"
                'Return a JSON list with one object per idea, in order: {"promise": "favourite"|"middle"|"long_shot", '
                '"p_improve": 0..1, "p_repeat": 0..1, "kind": ' + json.dumps(list(KINDS)) + "}")
        res = self.claude.call(self.model, system, user, max_tokens=4000)
        try:
            items = json.loads(re.search(r"\[.*\]", res.text or "", re.S).group(0))
        except (AttributeError, ValueError):
            items = []
        out = []
        for i in range(len(ideas)):
            it = items[i] if i < len(items) and isinstance(items[i], dict) else {}
            tier = it.get("promise") if it.get("promise") in TIERS else "middle"
            out.append(Ranking(promise={t: float(t == tier) for t in TIERS},
                               p_improve=float(it.get("p_improve", 0.5)), p_repeat=float(it.get("p_repeat", 0.0)),
                               kind=it.get("kind") if it.get("kind") in KINDS else "other",
                               cost=res.cost / len(ideas), seconds=res.seconds / len(ideas)))
        return out


class RandomRanker:
    """Control: random promise. With the same tier split it gives 'random assignment, same model mix'."""
    name = "random"

    def __init__(self, seed: int = 0):
        self.rng = random.Random(seed)

    def rank(self, problem, best_score, best_code, history, ideas) -> List[Ranking]:
        out = []
        for _ in ideas:
            w = [self.rng.random() for _ in TIERS]
            out.append(Ranking(promise={t: x / sum(w) for t, x in zip(TIERS, w)}, p_improve=self.rng.random(),
                               p_repeat=0.0, kind="other"))
        return out
