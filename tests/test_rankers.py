"""ClaudeRanker must tolerate malformed JSON fields instead of crashing the triage loop."""
import json
from types import SimpleNamespace

from autoresearch.rankers import ClaudeRanker


class _FakeClaude:
    def __init__(self, items):
        self.text = json.dumps(items)

    def call(self, model, system, user, max_tokens=4000):
        return SimpleNamespace(text=self.text, cost=0.02, seconds=1.0)


def _rank(items, n):
    return ClaudeRanker(_FakeClaude(items)).rank("problem", 0.5, "code", [], [f"idea {i}" for i in range(n)])


def test_list_valued_kind_and_promise_fall_back_instead_of_crashing():
    out = _rank([{"promise": ["favourite"], "p_improve": 0.7, "p_repeat": 0.1,
                  "kind": ["search_method", "parameter_tweak"]}], 1)
    assert out[0].kind == "other"
    assert out[0].promise == {"favourite": 0.0, "middle": 1.0, "long_shot": 0.0}
    assert out[0].p_improve == 0.7


def test_missing_or_invalid_probabilities_use_defaults():
    out = _rank([{"promise": "favourite", "p_improve": None, "p_repeat": "often", "kind": "bug_fix"},
                 {"promise": "long_shot", "p_improve": 1.7, "kind": "new_construction"}], 2)
    assert (out[0].p_improve, out[0].p_repeat, out[0].kind) == (0.5, 0.0, "bug_fix")
    assert out[0].promise["favourite"] == 1.0
    assert (out[1].p_improve, out[1].kind) == (0.5, "new_construction")


def test_well_formed_reply_is_unchanged():
    out = _rank([{"promise": "long_shot", "p_improve": 0.2, "p_repeat": 0.4, "kind": "parameter_tweak"}], 1)
    assert (out[0].promise["long_shot"], out[0].p_improve, out[0].p_repeat, out[0].kind) == (1.0, 0.2, 0.4,
                                                                                              "parameter_tweak")
    assert out[0].cost == 0.02
