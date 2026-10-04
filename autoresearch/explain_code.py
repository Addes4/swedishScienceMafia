"""Explain a found program by two-sided ablation: which parts of it does the score depend on?

    python -m autoresearch.explain_code problems/bin_packing_online runs/x/best_program.py

The parts are the statements in the body of the problem's function (verify.FUNCTION), searched
recursively into if/for/while/with/try bodies and nested functions, except each function's final
`return`, plus each operand of a top-level `+`/`-` chain in a return or assignment. Each part is
removed on its own (a statement becomes `pass`, a term is dropped from its sum) and the variant is
scored by the gate; only the public score is used for any decision.

Then a minimal program is built greedily: parts are removed one at a time, in order of smallest
single effect first, and a removal is kept only if the public score stays within `tol` of the
original on both sides. The check is two-sided on purpose. A removal that raises the score by
more than `tol` is not an explanation of the program that was found: it is a repair, and it is
reported as `REPAIRED (not an explanation)`. (One-sided simplification, keeping any removal that
does not hurt, produced false "rediscovered best fit" readings in this project: see
experiments/simplify-v1.) The minimal program is then also scored on the hidden instances.

Only the function itself is ablated: module-level helpers and constants are left as they are.
"""
import argparse
import ast
import json
import os
import tempfile
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Callable, List, Optional

from .gate import _load_verify, _timeout, evaluate

DEFAULT_TOL = 0.002
DEFAULT_MAX_EVALS = 40
REPAIRED = "REPAIRED (not an explanation)"


@dataclass
class Score:
    public: float
    hidden: Optional[float]
    valid: bool
    seconds: float = 0.0          # slowest instance, from integrity.json


@dataclass
class Part:
    id: int
    kind: str                     # "statement" or "term"
    line: int
    text: str
    inside: List[int] = field(default_factory=list)   # statement parts that contain this part
    delta: Optional[float] = None                     # public score change when removed alone
    valid: Optional[bool] = None                      # the program still runs and is valid without it
    verdict: str = "not tested"


# -- finding and removing parts --------------------------------------------------------------------
def find_function(tree: ast.AST, name: str):
    return next((n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == name),
                None)


def chain(expr):
    """Signed operands of a top-level +/- chain, left to right: a - b + c -> [(1, a), (-1, b), (1, c)].
    Only the left spine is flattened, so a parenthesised right operand stays one term."""
    if isinstance(expr, ast.BinOp) and isinstance(expr.op, (ast.Add, ast.Sub)):
        return chain(expr.left) + [(1 if isinstance(expr.op, ast.Add) else -1, expr.right)]
    return [(1, expr)]


def rebuild(terms):
    if not terms:
        return ast.Constant(0)
    sign, first = terms[0]
    out = first if sign > 0 else ast.UnaryOp(ast.USub(), first)
    for sign, e in terms[1:]:
        out = ast.BinOp(out, ast.Add() if sign > 0 else ast.Sub(), e)
    return out


def _is_docstring(stmt):
    return isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant) and isinstance(stmt.value.value, str)


def collect(func):
    """[(kind, handle, node, inside)] in a fixed order, so the same source always gives the same ids.
    handle is (body list, index) for a statement and (owner statement, term index) for a term."""
    out = []

    def body(stmts, inside, is_function_body):
        for i, s in enumerate(stmts):
            final_return = is_function_body and i == len(stmts) - 1 and isinstance(s, ast.Return)
            if not (final_return or _is_docstring(s) or isinstance(s, ast.Pass)):
                out.append(("statement", (stmts, i), s, list(inside)))
                me = len(out) - 1
                inner = inside + [me]
            else:
                inner = inside
            value = getattr(s, "value", None) if isinstance(s, (ast.Return, ast.Assign, ast.AugAssign, ast.AnnAssign)) else None
            if value is not None:
                terms = chain(value)
                if len(terms) > 1:
                    for k in range(len(terms)):
                        out.append(("term", (s, k), terms[k][1], list(inner)))
            if isinstance(s, (ast.FunctionDef, ast.AsyncFunctionDef)):
                body(s.body, inner, True)
            else:
                for attr in ("body", "orelse", "finalbody"):
                    sub = getattr(s, attr, None)
                    if isinstance(sub, list) and sub and isinstance(sub[0], ast.stmt):
                        body(sub, inner, False)
                for h in getattr(s, "handlers", []) or []:
                    body(h.body, inner, False)
    body(func.body, [], True)
    return out


def describe(kind, node, owner_terms=None, k=None):
    if kind == "term":
        sign = "+" if owner_terms[k][0] > 0 else "-"
        return f"term {sign} {ast.unparse(node)}"
    text = ast.unparse(node).splitlines()[0]
    return text + (" ..." if isinstance(node, (ast.If, ast.For, ast.While, ast.With, ast.Try, ast.FunctionDef)) else "")


def parts_of(source: str, function: str) -> List[Part]:
    tree = ast.parse(source)
    func = find_function(tree, function)
    if func is None:
        raise LookupError(f"no function named {function!r}")
    parts = []
    for i, (kind, handle, node, inside) in enumerate(collect(func)):
        terms = chain(handle[0].value) if kind == "term" else None
        parts.append(Part(id=i, kind=kind, line=getattr(node, "lineno", 0),
                          text=describe(kind, node, terms, handle[1] if kind == "term" else None), inside=inside))
    return parts


def variant(source: str, function: str, drop) -> str:
    """The program with the given parts removed, as normalised source (ast.unparse)."""
    tree = ast.parse(source)
    cands = collect(find_function(tree, function))
    drop = set(drop)
    by_owner = {}
    for i in drop:
        kind, handle, _, _ = cands[i]
        if kind == "term":
            by_owner.setdefault(id(handle[0]), (handle[0], set()))[1].add(handle[1])
    for owner, ks in by_owner.values():   # terms first: they edit expressions inside statements
        owner.value = rebuild([t for k, t in enumerate(chain(owner.value)) if k not in ks])
    for i in drop:
        kind, handle, _, _ = cands[i]
        if kind == "statement":
            stmts, idx = handle
            stmts[idx] = ast.Pass()
    _tidy(tree)
    return ast.unparse(ast.fix_missing_locations(tree)) + "\n"


def _tidy(tree):
    """Drop `pass` from every body that has other statements, so a removal leaves no trace."""
    for node in ast.walk(tree):
        for attr in ("body", "orelse", "finalbody"):
            stmts = getattr(node, attr, None)
            if isinstance(stmts, list) and stmts and isinstance(stmts[0], ast.stmt):
                kept = [s for s in stmts if not isinstance(s, ast.Pass)]
                if len(kept) != len(stmts):
                    stmts[:] = kept or [ast.Pass()]


# -- scoring ----------------------------------------------------------------------------------------
def gate_scorer(problem_dir, workdir) -> Callable[[str], Score]:
    """Score source code with autoresearch.gate.evaluate, exactly as the search loop does."""
    problem_dir, workdir = Path(problem_dir), Path(workdir)
    counter = [0]

    def score(code: str) -> Score:
        counter[0] += 1
        d = workdir / f"v{counter[0]:03d}"
        d.mkdir(parents=True, exist_ok=True)
        (d / "program.py").write_text(code)
        metrics = evaluate(problem_dir, str(d / "program.py"), str(d / "results"))
        correct = json.loads((d / "results" / "correct.json").read_text())["correct"]
        integrity = json.loads((d / "results" / "integrity.json").read_text())
        slowest = max([r.get("seconds") or 0.0 for r in integrity.get("public", []) + integrity.get("hidden", [])] or [0.0])
        return Score(public=float(metrics["combined_score"]), hidden=metrics.get("private", {}).get("hidden_mean"),
                     valid=bool(correct), seconds=float(slowest))
    return score


# -- the analysis -----------------------------------------------------------------------------------
def explain(source: str, function: str, score: Callable[[str], Score], tol: float = DEFAULT_TOL,
            max_evals: int = DEFAULT_MAX_EVALS) -> dict:
    """Single-part ablations, then a greedy two-sided minimal program. Pure apart from `score`."""
    try:
        parts = parts_of(source, function)
    except SyntaxError as e:
        return {"skipped": f"the program does not parse ({e.msg}, line {e.lineno})"}
    except LookupError as e:
        return {"skipped": str(e)}
    if not parts:
        return {"skipped": f"{function} has nothing to remove (a single return without a +/- chain)"}

    evals = 0

    def run(drop):
        nonlocal evals
        evals += 1
        return score(variant(source, function, drop))

    original_code = variant(source, function, ())
    base = run(())
    if not base.valid:
        return {"skipped": "the program is not valid on the public instances", "evals": evals}
    singles = {}
    for p in parts:                           # one removal at a time
        if evals >= max_evals:
            break
        s = run({p.id})
        singles[p.id] = s
        p.valid = s.valid
        p.delta = (s.public if s.valid else 0.0) - base.public
        if not s.valid:
            p.verdict = "essential: the program fails or turns invalid without it"
        elif p.delta > tol:
            p.verdict = REPAIRED
        elif p.delta < -tol:
            p.verdict = "matters"
        else:
            p.verdict = "no effect alone"

    # Greedy minimal program: smallest single effect first; a removal is kept only if the score
    # stays within tol of the original on BOTH sides.
    order = sorted((p for p in parts if p.delta is not None),
                   key=lambda p: (0 if p.valid else 1, abs(p.delta)))
    dropped, current = set(), base
    for p in order:
        if set(p.inside) & dropped:
            continue                          # already gone with a statement around it
        trial = dropped | {p.id}
        if not dropped:
            s = singles[p.id]
        elif evals < max_evals:
            s = run(trial)
        else:
            break
        if s.valid and abs(s.public - base.public) <= tol:
            dropped, current = trial, s
    for p in parts:
        if p.id in dropped:
            p.verdict = "can go" + (" (with others)" if p.verdict != "no effect alone" else "")
        elif set(p.inside) & dropped:
            p.verdict = "can go (inside a removed statement)"

    minimal = variant(source, function, dropped)
    return {
        "function": function, "tol": tol, "max_evals": max_evals, "evals": evals,
        "original": {"public": base.public, "hidden": base.hidden, "code": original_code},
        "minimal": {"public": current.public, "hidden": current.hidden, "code": minimal,
                    "removed": sorted(dropped)},
        "parts": [asdict(p) for p in parts],
        "repaired": [p.id for p in parts if p.verdict == REPAIRED],
        "untested": [p.id for p in parts if p.delta is None],
    }


def explain_program(problem_dir, program_path, workdir=None, tol: float = DEFAULT_TOL,
                    max_evals: int = DEFAULT_MAX_EVALS) -> dict:
    """explain() on a program file with the gate as the scorer. Variants that run much longer than the
    original count as failures: the per-instance limit is lowered to 5x the original's slowest instance."""
    problem_dir = Path(problem_dir)
    verify = _load_verify(problem_dir)
    source = Path(program_path).read_text()
    workdir = Path(workdir or tempfile.mkdtemp(prefix="explain-"))
    scorer = gate_scorer(problem_dir, workdir)
    saved = os.environ.get("GATE_TIMEOUT_S")
    limit = _timeout(verify)

    def score(code):
        s = scorer(code)
        if score.first:
            score.first = False
            os.environ["GATE_TIMEOUT_S"] = str(min(limit, max(5.0, 5 * s.seconds)))
        return s
    score.first = True
    try:
        result = explain(source, verify.FUNCTION, score, tol, max_evals)
    finally:
        if saved is None:
            os.environ.pop("GATE_TIMEOUT_S", None)
        else:
            os.environ["GATE_TIMEOUT_S"] = saved
    result["program"] = str(program_path)
    return result


def to_markdown(r: dict) -> str:
    if r.get("skipped"):
        return f"Skipped: {r['skipped']}.\n"
    fmt = lambda x: "n/a" if x is None else f"{x:.4f}"
    parts = r["parts"]
    o, m = r["original"], r["minimal"]
    lines = [f"Two-sided ablation of `{r['function']}` ({len(parts)} parts, {r['evals']} evaluations, "
             f"tolerance ±{r['tol']:g} on the public score). A part \"can go\" only if removing it leaves the "
             "public score within the tolerance on both sides, so the explanation describes the program "
             "actually found, not a repaired one.", ""]
    matter = sorted((p for p in parts if p["delta"] is not None and p["id"] not in m["removed"]
                     and not any(i in m["removed"] for i in p["inside"]) and p["verdict"] != REPAIRED),
                    key=lambda p: -abs(p["delta"]))
    if matter:
        lines += ["**Parts that matter** (largest effect first; Δ = public score without the part minus with it):", "",
                  "| line | part | Δ public | verdict |", "|---|---|---|---|"]
        lines += [f"| {p['line']} | `{_cell(p['text'])}` | {p['delta']:+.4f} | {p['verdict']} |" for p in matter]
        lines.append("")
    gone = [p for p in parts if p["verdict"].startswith("can go")]
    if gone:
        lines += ["**Parts that can go** (removed together without moving the public score beyond the tolerance):", ""]
        lines += [f"- line {p['line']}: `{_cell(p['text'])}`" for p in gone]
        lines.append("")
    rep = [p for p in parts if p["verdict"] == REPAIRED]
    if rep:
        lines += [f"**{REPAIRED}**: removing these raises the public score by more than the tolerance. "
                  "The found program is worse than a simpler one; these are repairs, not parts of an explanation.", ""]
        lines += [f"- line {p['line']}: `{_cell(p['text'])}` (Δ {p['delta']:+.4f})" for p in rep]
        lines.append("")
    if r["untested"]:
        lines += [f"Not tested (evaluation limit {r['max_evals']}): {len(r['untested'])} parts.", ""]
    lines += ["| program | public | hidden |", "|---|---|---|",
              f"| found (normalised source) | {fmt(o['public'])} | {fmt(o['hidden'])} |",
              f"| minimal ({len(m['removed'])} parts removed) | {fmt(m['public'])} | {fmt(m['hidden'])} |", "",
              "Minimal program:", "", "```python", m["code"].rstrip("\n"), "```", ""]
    return "\n".join(lines)


def _cell(text: str) -> str:
    text = text.replace("|", "\\|").replace("`", "'")
    return text if len(text) <= 90 else text[:87] + "..."


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("problem")
    ap.add_argument("program")
    ap.add_argument("--tol", type=float, default=DEFAULT_TOL)
    ap.add_argument("--max-evals", type=int, default=DEFAULT_MAX_EVALS)
    ap.add_argument("--json", help="also write the full result here")
    a = ap.parse_args(argv)
    r = explain_program(a.problem, a.program, tol=a.tol, max_evals=a.max_evals)
    if a.json:
        Path(a.json).write_text(json.dumps(r, indent=2))
    print(to_markdown(r))


if __name__ == "__main__":
    main()
