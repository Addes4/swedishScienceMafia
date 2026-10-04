"""Baseline: a plain coding agent asked to beat the records, with the same harness and the same evaluation budget.

    python baselines/coding_agent.py --targets 85-90 --out baselines/out/squares
    python baselines/coding_agent.py --problem circle-radii --targets 26 --relaxes 73728 --polishes 576 --out baselines/out/radii

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

RELAXES = 4*(96+5*32)  # defaults: a local Mosa session of 2 researchers x 2 rounds
POLISHES = 4*8
FORMAT = {"squares": "x is an (n, 3) array of [x, y, angle in radians] of unit-square centres in [0, value]^2; value is the side",
          "circle-radii": "x is an (n, 3) array of [cx, cy, r] (circles in the unit square); value is minus the sum of radii",
          "sphere": "x is an (n, 3) array of points (rows are projected onto the unit sphere); value is the energy (pass 0.0 for a new candidate)"}
TOOLS = '''"""The harness, as a library. Every relax and polish call is logged to calls.jsonl and refused past the budget."""
import json, os, sys, time
os.environ.setdefault("NUMBA_CACHE_DIR", os.path.join(os.path.dirname(os.path.abspath(__file__)), ".numba"))
sys.path.insert(0, {root!r})
import numpy as np
from mosa.domain import get

_D = get({problem!r})
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
    """The best known solution for n: (x, value); x is None when no solution is stored, only its value."""
    return _D.reference(n)


def relax(x, value):
    """Relax a candidate (overlaps allowed) to a feasible solution with a penalty method: (x, value)."""
    x = np.asarray(x, dtype=float)
    _spend("relax", len(x))
    y, v, _ = _D.relax(_D.validate(x, value, len(x)), value)
    return np.asarray(y), float(v)


def polish(x, value):
    """Polish a feasible solution to its exact local optimum (SQP): (x, value)."""
    x = np.asarray(x, dtype=float)
    _spend("polish", len(x))
    y, v = _D.polish(x, value)
    return np.asarray(y), float(v)


def check(x):
    """Independent verification (zero tolerance, high precision): dict with valid, value, record, best_known."""
    out = _D.verify(np.asarray(x, dtype=float), len(x))
    return {{"valid": out["valid"], "value": out["value"], "record": out["record"], "best_known": out["reference_side"]}}


def submit(x):
    """Submit a solution; the best valid one per n is kept in solutions/n<n>.json."""
    x = np.asarray(x, dtype=float)
    out = check(x)
    path = os.path.join(_HERE, "solutions", f"n{{len(x)}}.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if out["valid"] and (not os.path.exists(path) or out["value"] < json.load(open(path))["value"]):
        json.dump({{"x": x.tolist(), "value": out["value"]}}, open(path, "w"))
    return out
'''
PROMPT = """Your task: {problem} Beat the best known values for n = {targets} (best known: {known}; smaller is better).

You work in this directory and can write and run any code with {python} (numpy, scipy and numba are installed).
tools.py is the evaluation harness; import it. A solution is (x, value): {format}.
  known(n) -> (x, value): the best known solution (x is None when only its value is published)
  relax(x, value) -> (x, value): a fast local optimizer from any candidate (overlaps allowed) to a feasible solution
  polish(x, value) -> (x, value): exact local optimization of a feasible solution
  check(x) -> dict: independent verification
  submit(x) -> dict: verify and keep your best solution per n
Budget per size n: {relaxes} relax calls and {polishes} polish calls (the tools refuse more). Your own code may compute
anything else. Submit your best solution for every n with submit() before you finish, then reply with a short summary of
what you tried and the values you reached."""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--problem", default="squares")
    parser.add_argument("--targets", nargs="+", default=["85-90"])
    parser.add_argument("--relaxes", type=int, default=RELAXES)
    parser.add_argument("--polishes", type=int, default=POLISHES)
    parser.add_argument("--out", default="baselines/out/coding-agent", help="the agent's working directory (not runs/: that holds Mosa's workspaces)")
    parser.add_argument("--model", default=None)
    parser.add_argument("--timeout", type=int, default=5400, help="seconds")
    args = parser.parse_args()
    from mosa.cli import sizes
    targets = sizes(args.targets)
    out = (ROOT/args.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    from mosa.domain import get
    domain = get(args.problem)
    (out/"tools.py").write_text(TOOLS.format(root=str(ROOT), problem=args.problem, relaxes=args.relaxes, polishes=args.polishes))
    prompt = PROMPT.format(problem=domain.problem, targets=", ".join(map(str, targets)), python=str(ROOT/".venv"/"bin"/"python"),
                           known=", ".join(f"n = {n}: {domain.best_known(n)}" for n in targets) if any(domain.best_known(n) is not None for n in targets)
                           else "none published: you are compared with other methods at the same budget", format=FORMAT["sphere" if args.problem.startswith("riesz-") or args.problem == "thomson" else args.problem],
                           relaxes=args.relaxes, polishes=args.polishes)
    (out/"prompt.txt").write_text(prompt)
    command = ["codex", "exec", "--ignore-user-config", "--ignore-rules", "--sandbox", "workspace-write", "--skip-git-repo-check",
               "-C", str(out), "--json", "-o", str(out/"answer.txt")]
    if args.model:
        command += ["--model", args.model]
    started = time.time()
    with open(out/"codex-events.jsonl", "w") as events, open(out/"stderr.txt", "w") as errors:
        try:
            subprocess.run(command+["-"], input=prompt, text=True, stdout=events, stderr=errors, timeout=args.timeout,
                           env={k: v for k, v in os.environ.items() if not k.endswith("_API_KEY") or k == "OPENAI_API_KEY"})
        except subprocess.TimeoutExpired:
            pass
    # verify what it submitted, independently of its own tools
    report = {"problem": args.problem, "seconds": time.time()-started, "budget": {"relax": args.relaxes, "polish": args.polishes}, "sizes": {}}
    calls = [json.loads(line) for line in open(out/"calls.jsonl")] if (out/"calls.jsonl").exists() else []
    for n in targets:
        path = out/"solutions"/f"n{n}.json"
        entry = {"best_known": domain.best_known(n), "relax_calls": sum(c["n"] == n and c["kind"] == "relax" for c in calls),
                 "polish_calls": sum(c["n"] == n and c["kind"] == "polish" for c in calls)}
        if path.exists():
            saved = json.loads(path.read_text())
            certificate = domain.verify(saved.get("x", saved.get("poses")), n)
            entry.update(value=certificate["value"], valid=certificate["valid"], record=certificate["record"],
                         gap=None if domain.best_known(n) is None else certificate["value"]-domain.best_known(n))
        report["sizes"][n] = entry
    (out/"report.json").write_text(json.dumps(report, indent=1))
    print(json.dumps(report, indent=1))


if __name__ == "__main__":
    main()
