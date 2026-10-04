"""Baseline: a plain coding agent asked to beat the records, with the same harness and the same evaluation budget.

    python baselines/coding_agent.py --targets 85-90 --out runs/coding-agent

The agent (Codex, the model Mosa's researchers use) works free-form in its own directory: it can write and run any
code. It gets the problem in words, the best known packing for each size, and the harness as a small library
(tools.py): relax and polish (the same trusted tools Mosa uses; each call is counted and refused past the budget) and
check (the independent verifier, free). The budget per size equals a Mosa session of 2 researchers x 2 rounds at the
local budget (4 x (96 + 5 x 32) relaxations and 4 x 8 polishes). Whatever it submits is verified independently
afterwards. It gets none of Mosa's structure: no measured evidence about the landscape, no rounds with near-miss
feedback, no library of strategies, no shared memory between sizes.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

RELAXES = 4*(96+5*32)
POLISHES = 4*8
TOOLS = '''"""The harness, as a library. Every relax and polish call is logged to calls.jsonl and refused past the budget."""
import json, os, sys, time
os.environ.setdefault("NUMBA_CACHE_DIR", os.path.join(os.path.dirname(os.path.abspath(__file__)), ".numba"))
sys.path.insert(0, {root!r})
import numpy as np
from mosa.domain import get

_D = get("squares")
_HERE = os.path.dirname(os.path.abspath(__file__))
BUDGET = {{"relax": {relaxes}, "polish": {polishes}}}  # per size n


def _spend(kind, n):
    path = os.path.join(_HERE, "calls.jsonl")
    used = 0
    if os.path.exists(path):
        used = sum(1 for line in open(path) if json.loads(line)["kind"] == kind and json.loads(line)["n"] == n)
    if used >= BUDGET[kind]:
        raise RuntimeError(f"budget exhausted: {{BUDGET[kind]}} {{kind}} calls for n = {{n}}")
    with open(path, "a") as f:
        f.write(json.dumps({{"kind": kind, "n": n, "time": time.time()}})+"\\n")


def known(n):
    """The best known packing for n: (poses, side); poses is an (n, 3) array of [x, y, angle] of unit-square centres
    in [0, side]^2."""
    return _D.reference(n)


def relax(poses, side):
    """Relax a candidate (overlaps allowed) to a feasible packing with an L-BFGS penalty method: (poses, side)."""
    poses = np.asarray(poses, dtype=float)
    _spend("relax", len(poses))
    x, value, _ = _D.relax(_D.validate(poses, side, len(poses)), side)
    return np.asarray(x), float(value)


def polish(poses, side):
    """Polish a feasible packing to its exact local optimum (SQP): (poses, side)."""
    poses = np.asarray(poses, dtype=float)
    _spend("polish", len(poses))
    x, value = _D.polish(poses, side)
    return np.asarray(x), float(value)


def check(poses):
    """Independent verification (zero tolerance, high precision): dict with valid, side, record."""
    out = _D.verify(np.asarray(poses, dtype=float), len(poses))
    return {{"valid": out["valid"], "side": out["side"], "record": out["record"], "best_known": out["reference_side"]}}


def submit(poses):
    """Submit a packing; the best valid one per n is kept in solutions/n<n>.json."""
    poses = np.asarray(poses, dtype=float)
    out = check(poses)
    path = os.path.join(_HERE, "solutions", f"n{{len(poses)}}.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if out["valid"] and (not os.path.exists(path) or out["side"] < json.load(open(path))["side"]):
        json.dump({{"poses": poses.tolist(), "side": out["side"]}}, open(path, "w"))
    return out
'''
PROMPT = """Your task: find packings of n unit squares in the smallest possible square container that beat the best known
packings, for n = {targets}. Each square has side 1 and may be translated and rotated freely; squares may not overlap.
The objective is the side of the container. The best known sides are from the squares-in-squares catalogue (Friedman,
Ellsworth); some were improved as recently as 2024.

You work in this directory and can write and run any code with {python} (numpy, scipy and numba are installed).
tools.py is the evaluation harness; import it:
  known(n) -> (poses, side): the best known packing (poses: (n, 3) array of [x, y, angle in radians] of square centres)
  relax(poses, side) -> (poses, side): a fast local optimizer from any candidate (overlaps allowed) to a feasible packing
  polish(poses, side) -> (poses, side): exact local optimization of a feasible packing
  check(poses) -> dict: independent verification
  submit(poses) -> dict: verify and keep your best packing per n
Budget per size n: {relaxes} relax calls and {polishes} polish calls (the tools refuse more). Your own code may compute
anything else. Submit your best packing for every n with submit() before you finish, then reply with a short summary of
what you tried and the sides you reached."""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--targets", nargs="+", default=["85-90"])
    parser.add_argument("--out", default="runs/coding-agent")
    parser.add_argument("--model", default=None)
    parser.add_argument("--timeout", type=int, default=5400, help="seconds")
    args = parser.parse_args()
    from mosa.cli import sizes
    targets = sizes(args.targets)
    out = (ROOT/args.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    (out/"tools.py").write_text(TOOLS.format(root=str(ROOT), relaxes=RELAXES, polishes=POLISHES))
    prompt = PROMPT.format(targets=", ".join(map(str, targets)), python=str(ROOT/".venv"/"bin"/"python"), relaxes=RELAXES,
                           polishes=POLISHES)
    (out/"prompt.txt").write_text(prompt)
    command = ["codex", "exec", "--ignore-user-config", "--ignore-rules", "--sandbox", "workspace-write", "--skip-git-repo-check",
               "-C", str(out), "--json", "-o", str(out/"answer.txt")]
    if args.model:
        command += ["--model", args.model]
    started = time.time()
    with open(out/"events.jsonl", "w") as events, open(out/"stderr.txt", "w") as errors:
        try:
            subprocess.run(command+["-"], input=prompt, text=True, stdout=events, stderr=errors, timeout=args.timeout,
                           env={k: v for k, v in os.environ.items() if not k.endswith("_API_KEY") or k == "OPENAI_API_KEY"})
        except subprocess.TimeoutExpired:
            pass
    # verify what it submitted, independently of its own tools
    from mosa.domain import get
    squares = get("squares")
    report = {"seconds": time.time()-started, "budget": {"relax": RELAXES, "polish": POLISHES}, "sizes": {}}
    calls = [json.loads(line) for line in open(out/"calls.jsonl")] if (out/"calls.jsonl").exists() else []
    for n in targets:
        path = out/"solutions"/f"n{n}.json"
        entry = {"best_known": squares.best_known(n), "relax_calls": sum(c["n"] == n and c["kind"] == "relax" for c in calls),
                 "polish_calls": sum(c["n"] == n and c["kind"] == "polish" for c in calls)}
        if path.exists():
            certificate = squares.verify(json.loads(path.read_text())["poses"], n)
            entry.update(side=certificate["side"], valid=certificate["valid"], record=certificate["record"],
                         gap=certificate["side"]-squares.best_known(n))
        report["sizes"][n] = entry
    (out/"report.json").write_text(json.dumps(report, indent=1))
    print(json.dumps(report, indent=1))


if __name__ == "__main__":
    main()
