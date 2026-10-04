"""Harnesses drafted on the spot: when a request is outside the problem library, the research agent writes one.

A harness is a Python module defining `class Problem(Domain)` (see mosa/domain.py): a random candidate, a fast local
optimizer, an optional refinement, an independent verifier that recomputes the objective from the solution, a picture,
and any published best values. It is saved to mosa/domains/generated/<name>.py and must pass a self-test before any
research runs on it: random starts on small sizes are relaxed and verified, the verifier must recompute the relaxed
values, malformed candidates must be rejected, and the results are compared with the published values it states.
Drafted harnesses are LLM-written evaluation code: the self-test, the independent verifier and the visible code are the
safeguards; researchers' strategies still cannot touch them.
"""
from __future__ import annotations

import ast
import importlib
import json
from pathlib import Path
import re
import signal
import time
import traceback

import numpy as np

from .llm import SOURCES, SOURCES_PROMPT, ask
from .sandbox import violations

GENERATED = Path(__file__).resolve().parent/"domains"/"generated"
# What a harness may import: exactly what the Modal image installs (mosa/modal_app.py) plus the standard library pieces
# below. A harness importing anything else would run here but crash in the workers, so its self-test fails instead.
ALLOWED = {"numpy", "scipy", "numba", "mpmath", "math", "cmath", "itertools", "functools", "collections", "dataclasses",
           "typing", "__future__", "random", "heapq", "bisect", "fractions", "decimal", "statistics", "time", "warnings",
           "operator", "copy", "enum", "mosa"}
SCHEMA = {"type": "object", "additionalProperties": False, "required": ["name", "title", "family", "about", "code", "test_sizes", "sources"],
          "properties": {"name": {"type": "string"}, "title": {"type": "string"}, "family": {"type": "string"},
                         "about": {"type": "string"}, "code": {"type": "string"},
                         "test_sizes": {"type": "array", "items": {"type": "integer"}}, "sources": SOURCES}}
CONTRACT = '''import math
import numpy as np
from scipy.optimize import minimize
from mosa.domain import Domain

KNOWN = {}      # published best values {n: value}, looked up (cite every source); may be empty
REFERENCE = {}  # published coordinates of those best solutions {n: x}, only where a source gives them; may be empty


class Problem(Domain):
    family = "..."      # problems with the same representation share a family, e.g. "unit circles"
    title = "..."
    problem = "..."     # one paragraph for the researchers: what is placed where, what is minimized
    evidence = "..."    # what is known about the landscape (from the literature)
    api = """def initialize(record, neighbours, rng, count):
    ...describe the candidate format: x (an array) and value (the objective, or a container size). record is always
    None (no solutions are stored); neighbours is {m: (x, value)}, best solutions found for nearby sizes, possibly
    empty; the global n is the size...
def vary(parents, rng, count):
    ..."""
    same = 1e-7          # objective values closer than this are one basin

    def targets(self):            # the sizes n this harness supports
        return list(range(2, 201))

    def reference(self, n):       # the published best solution (x, value) where coordinates are given, else (None, value)
        return (np.asarray(REFERENCE[n], dtype=float), KNOWN[n]) if n in REFERENCE and n in KNOWN else (None, KNOWN.get(n))

    def best_known(self, n):
        return KNOWN.get(n)

    def random(self, n, rng):     # a random candidate (x, value), overlaps allowed
        ...

    def validate(self, x, value, n):   # reject malformed candidates from model-written code: raise ValueError
        ...
        return np.asarray(x, dtype=float)

    def relax(self, x, value):    # fast local optimizer from any candidate to a FEASIBLE solution: (x, value, evaluations)
        ...                       # e.g. a penalty method with scipy L-BFGS-B, then a repair that guarantees feasibility

    def polish(self, x, value):   # optional exact refinement of a feasible solution: (x, value)
        return x, value

    def verify(self, x, n):       # independent of relax: recompute feasibility and the objective from x alone
        ...                       # (use high precision, e.g. mpmath, where it matters)
        return {"valid": True, "value": 0.0}

    def svg(self, x, value):      # a picture of a solution as an <svg> string (fill:#B2B2B2; stroke:black)
        ...
'''


BUILT_IN = {  # library problems whose harness is part of Mosa: the files a fork starts from
    "squares": ["squares/__init__.py", "squares/kernel.py", "squares/polish.py"],
    "thomson": ["thomson/__init__.py"], "riesz": ["thomson/__init__.py"], "circle-radii": ["radii/__init__.py"]}


def source(name):
    """The code of a library harness, to fork from: a drafted one's module, or a built-in one's files."""
    domains = Path(__file__).resolve().parent/"domains"
    if name.startswith("gen-"):
        path = GENERATED/(name.replace("-", "_")+".py")
        return path.read_text() if path.exists() else ""
    files = BUILT_IN.get(name.split("-")[0] if name.startswith("riesz") else name, [])
    return "\n\n".join(f"# --- mosa/domains/{f} ---\n{(domains/f).read_text()}" for f in files)[:40000]


def draft(request, directory, model=None, base=None):
    """Ask the model for a harness (forked from the library harness `base` when given), save it, and self-test it:
    returns (name, answer, report). Only a harness that passes stays in the library."""
    fork = source(base) if base else ""
    start = (f"""
Start from this existing library harness for a related problem ({base}) and change only what the new problem needs: keep
its structure, numerics and verification approach wherever they still apply. The result must still be one
self-contained module following the contract below (inline anything it imported from its own package).

{fork}
""" if fork else "")
    text = f"""Write a harness for Mosa, a framework in which LLM researchers write search strategies and trusted tools test
them. The user wants to research: {request}
{start}
Turn this into a MINIMIZATION problem over a family of instances indexed by an integer size n (for example "n circles in
the smallest circle": minimize the container radius). Write a complete Python module that follows this contract exactly
(numpy, scipy, numba and mpmath are available; no files, network or subprocesses). The harness must support small sizes
(it is self-tested on n <= 30) as well as the sizes the user asked for:

{CONTRACT}

Requirements: relax must always return a feasible solution (repair it, e.g. by scaling apart or growing the container)
and be fast (well under a second for n around 20); verify must not reuse relax's computations and must reject infeasible
solutions. Look up the published best known values for this exact problem and formulation before writing KNOWN: for
example Erich Friedman's Packing Center (erich-friedman.github.io/packing), Packomania (packomania.com), Sloane's tables,
or papers. Convert each to the objective's convention (smaller is better), put coordinates into REFERENCE only where a
source publishes them, and never invent a value: leave KNOWN empty if you find none. In "sources", """+SOURCES_PROMPT.split(";")[0]+""". Return JSON
with "name" (a short slug, letters, digits and dashes), "title", "family", "about" (one sentence for a problem library),
"code" (the module), "test_sizes" (3 sizes between 5 and 30 for the self-test, ideally ones in KNOWN) and "sources"."""
    answer = ask(text, SCHEMA, directory, model, timeout=900, search=True)
    name = "gen-"+re.sub(r"[^a-z0-9-]+", "-", answer["name"].lower()).strip("-")[:40]
    flagged = violations(answer["code"])
    if flagged:  # the same static scan as strategies: a harness has no business with files, processes or the network
        return name, answer, {"passed": False, "error": "integrity scan: "+", ".join(flagged)}
    try:
        missing = imports_outside(answer["code"])
    except SyntaxError as error:
        return name, answer, {"passed": False, "error": f"SyntaxError: {error.msg} (line {error.lineno})"}
    if missing:
        return name, answer, {"passed": False, "error": f"imports {', '.join(missing)}, which the workers do not have; use only "
                                                         "numpy, scipy, numba, mpmath and the standard math modules"}
    GENERATED.mkdir(exist_ok=True)
    (GENERATED/"__init__.py").touch()
    path = GENERATED/(name.replace("-", "_")+".py")
    path.write_text(answer["code"])
    meta = GENERATED/(name.replace("-", "_")+".json")
    meta.write_text(json.dumps({"name": name, "title": answer["title"], "family": answer["family"], "about": answer["about"],
                                "forked_from": base if fork else None}))
    report = self_test(name, answer["test_sizes"])
    try:  # the published values the harness carries, for the conversation
        module = importlib.import_module(f"mosa.domains.generated.{name.replace('-', '_')}")
        report["published"] = {str(k): float(v) for k, v in sorted(getattr(module, "KNOWN", {}).items())}
        report["published_coordinates"] = sorted(int(k) for k in getattr(module, "REFERENCE", {}))
    except Exception:
        report["published"] = {}
    if not report.get("passed"):  # the library only holds harnesses that passed; the code stays in the notebook
        path.unlink(missing_ok=True)
        meta.unlink(missing_ok=True)
    report["forked_from"] = base if fork else None
    return name, answer, report


def imports_outside(code):
    """Top-level modules the code imports that the workers do not have."""
    found = set()
    for node in ast.walk(ast.parse(code)):
        if isinstance(node, ast.Import):
            found |= {a.name.split(".")[0] for a in node.names}
        elif isinstance(node, ast.ImportFrom) and node.module and not node.level:
            found.add(node.module.split(".")[0])
    return sorted(found-ALLOWED)


def load(name):
    """The generated Problem for a name like gen-circles-in-circle, with the framework's fields filled in."""
    module = importlib.import_module(f"mosa.domains.generated.{name.replace('-', '_')}")
    problem = module.Problem()
    problem.name = name
    verify = problem.verify

    def certified(x, n):  # the framework's certificate fields around the harness's own verdict
        out = dict(verify(x, n))
        best, value, valid = problem.best_known(n), float(out.get("value", float("nan"))), bool(out.get("valid"))
        out.update(n=n, value=value, side=value, reference_side=best, valid=valid, poses=np.asarray(x).tolist(),
                   improvement=None if best is None else best-value, record=bool(valid and best is not None and value < best-1e-9),
                   float_zero_tolerance=valid, min_pair_clearance=out.get("min_pair_clearance", 0.),
                   high_precision=out.get("high_precision", [{"digits": None, "valid": valid}]))
        return out
    problem.verify = certified
    return problem


def library():
    """Generated problems, as library entries."""
    return [json.loads(p.read_text()) for p in sorted(GENERATED.glob("*.json"))] if GENERATED.exists() else []


SLOW = 15.  # seconds one relax may take at a small size, even on a busy machine


def _too_slow(*_):
    raise TimeoutError("the self-test took over 4 minutes: relax is far too slow")


def self_test(name, sizes):
    """Relax random starts on small sizes, verify them, compare with the published values; a dict for the chat."""
    report = {"passed": False, "sizes": []}
    signal.signal(signal.SIGALRM, _too_slow)
    signal.alarm(240)
    try:
        problem = load(name)
        rng = np.random.default_rng(0)
        supported = problem.targets()
        small = [n for n in supported if n <= 30]  # always small sizes: the test checks correctness, not scale
        chosen = sorted({n for n in sizes if n in set(small)})[:3] or small[:1]+small[len(small)//2:len(small)//2+1]+small[-1:]
        problem.relax(*problem.random(chosen[0], rng))  # warm-up: compiling numba code does not count as slow
        for n in chosen:
            started, values, invalid = time.perf_counter(), [], 0
            for _ in range(4):
                x, value = problem.random(n, rng)
                one = time.perf_counter()
                x, value, _ = problem.relax(problem.validate(x, value, n), value)
                if time.perf_counter()-one > SLOW:
                    raise TimeoutError(f"one relax at n = {n} took {time.perf_counter()-one:.0f} s; it must take well under a second")
                cert = problem.verify(x, n)
                if not cert["valid"] or abs(cert["value"]-value) > 1e-6*max(1., abs(value)):
                    invalid += 1
                values.append(value)
            best = problem.best_known(n)
            report["sizes"].append({"n": n, "best_found": min(values), "best_known": best, "invalid": invalid,
                                    "gap": None if best is None else min(values)-best,
                                    "seconds_per_relax": (time.perf_counter()-started)/4})
        try:
            problem.validate(np.zeros((1, 1)), 1., 7)
            rejects = False
        except (ValueError, TypeError, IndexError):
            rejects = True
        report["rejects_malformed"] = rejects
        report["passed"] = rejects and all(s["invalid"] == 0 for s in report["sizes"]) and all(
            s["gap"] is None or s["gap"] > -1e-6 for s in report["sizes"])  # a self-test "beating" a published value means a broken harness
    except Exception:
        report["error"] = traceback.format_exc(limit=3)[-1500:]
    finally:
        signal.alarm(0)
    return report
