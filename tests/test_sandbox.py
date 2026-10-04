"""The static integrity scan rejects code that reaches outside the strategy template, and nothing else."""
import json
from pathlib import Path
import unittest

from mosa.domain import get
from mosa.sandbox import step, violations

ROOT = Path(__file__).resolve().parents[1]


class SandboxTest(unittest.TestCase):
    def test_scan_rejects_cheats(self):
        cheats = {"import os\nkey = os.environ['OPENAI_API_KEY']": "os access",
                  "from urllib.request import urlopen": "process or network access",
                  "data = open('data/squares/known-best.jsonl').read()": "file access",
                  "m = __import__('subprocess')": "import or runtime tampering",
                  "exec('x = 1')": "dynamic code execution"}
        for code, reason in cheats.items():
            self.assertIn(reason, violations(code), code)

    def test_scan_reads_code_not_words(self):
        self.assertEqual(violations("def vary(p, rng, c):\n    # never open( files or use urllib\n    return 'open(' and p"), [])

    def test_every_real_strategy_passes(self):
        codes = [e["code"] for e in json.loads((ROOT/"data"/"strategy-library.json").read_text())]
        for path in (ROOT/"history").glob("*/events.jsonl"):
            codes += [e["code"] for e in map(json.loads, path.read_text().splitlines()) if e["type"] == "strategy" and e.get("code")]
        self.assertGreater(len(codes), 20)
        self.assertEqual([c for c in codes if violations(c)], [])

    def test_rejected_code_never_runs(self):
        out = step(get("squares"), "import os\nos.system('touch /tmp/mosa-should-not-exist')", "initialize",
                   {"record": None, "neighbours": {}}, 8, 0, 40)
        self.assertIn("integrity scan", out["error"])
        self.assertFalse(Path("/tmp/mosa-should-not-exist").exists())


if __name__ == "__main__":
    unittest.main()
