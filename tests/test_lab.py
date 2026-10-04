"""End-to-end lab round with a stub researcher (no model call): local backend, tiny budget."""
import json
from pathlib import Path
import tempfile
import unittest

import mosa.research as research
from mosa.evaluate import Budget
from mosa.store import Notebook

CODE = """
def initialize(record, neighbours, rng, count):
    poses, side = record
    out = []
    for _ in range(count):
        p = poses.copy()
        p[rng.integers(len(p), size=3), :2] += rng.normal(scale=0.3, size=(3, 2))
        out.append((p, side*1.02))
    return out


def vary(parents, rng, count):
    out = []
    for _ in range(count):
        poses, side = parents[rng.integers(len(parents))]
        p = poses.copy()
        p[rng.integers(len(p), size=3), :2] += rng.normal(scale=0.2, size=(3, 2))
        out.append((p, side*1.02))
    return out
"""


class LabTest(unittest.TestCase):
    def test_round_writes_strategy_progress_results(self):
        code = CODE
        stub = {"name": "stub", "decision": "new", "builds_on": "none", "source": "stub", "mapping": "m", "strategy": "s", "code": code,
                "model_seconds": 0}
        original, research.ask = research.ask, lambda *a, **k: stub
        try:
            with tempfile.TemporaryDirectory() as out:
                research.Lab("squares", "local", out, Budget(16, 16, 1, 4, 2), workers=2).lab([40, 41], 1, 1, [0])
                events = Notebook(out).read()
        finally:
            research.ask = original
        kinds = [e["type"] for e in events]
        self.assertEqual(kinds[0], "lab")
        self.assertEqual(kinds[-1], "done")
        for kind in ("prompt", "strategy", "progress", "result", "round"):
            self.assertIn(kind, kinds)
        results = [e for e in events if e["type"] == "result"]
        self.assertEqual(sorted(r["n"] for r in results), [40, 41])
        for r in results:
            self.assertNotIn("error", r)
            self.assertGreaterEqual(r["gap"], -1e-9)  # no record at n = 40, 41 with this budget
            self.assertEqual(len(r["best"]["x"]), r["n"])
            self.assertEqual(r["idea"], [0, 0, 1])

    def test_sessions_share_memory_and_reruns_attach_to_the_idea(self):
        code = CODE
        stub = {"name": "stub", "decision": "new", "builds_on": "none", "source": "stub", "mapping": "m", "strategy": "s", "code": code,
                "model_seconds": 0}
        original, research.ask = research.ask, lambda *a, **k: stub
        try:
            with tempfile.TemporaryDirectory() as out:
                research.Lab("squares", "local", out, Budget(16, 16, 1, 4, 2), workers=2).lab([40], 1, 1, [0])
                second = research.Lab("squares", "local", out, Budget(16, 16, 1, 4, 2), workers=2)
                self.assertEqual(second.session, 1)
                self.assertIn(("squares", 40), second.memory)  # what session 0 found is in the workspace memory
                second.apply(None, "idea 0:0:1", [41], [1], idea=(0, 0, 1))
                events = Notebook(out).read()
        finally:
            research.ask = original
        rerun = [e for e in events if e["type"] == "result" and e["session"] == 1]
        self.assertEqual([(e["n"], e["idea"]) for e in rerun], [(41, [0, 0, 1])])
        self.assertEqual(sum(e["type"] == "strategy" for e in events), 1)  # the rerun added results, not a new idea


if __name__ == "__main__":
    unittest.main()
