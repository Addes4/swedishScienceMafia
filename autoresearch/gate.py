"""Integrity gate: independent scoring, exploit checks, and generic rejection feedback.

Every problem's evaluate.py calls `evaluate(problem_dir, program_path, results_dir)`.
It writes the files ShinkaEvolve reads (metrics.json, correct.json) plus integrity.json,
a detailed log for humans that is never shown to the LLM.

Problem contract (problems/<name>/verify.py), all scores higher-is-better:
    FUNCTION = "solve"                 # function the candidate defines; called as solve(**instance)
    PUBLIC = [{...}, ...]              # instances whose results the LLM sees
    HIDDEN = [{...}, ...]              # instances it never sees (overfitting check)
    TIMEOUT_S = 60                     # per-instance time limit
    def check(construction, instance) -> {"valid": bool, "score": float, "reason": str}
    def best_known(instance) -> float | None
    def check_strict(construction, instance) -> bool       # optional, independent re-check
    def label(instance) -> str                              # optional, for feedback text

Optional online protocol (for problems where the candidate must decide per input, e.g. online
bin packing). If verify.py defines both of these, the gate does not call FUNCTION(**instance):
    DRIVER = "def drive(fn, header, next_input, emit): ..."   # trusted source run in the child
    def online(instance) -> (header: dict, inputs: list)     # inputs revealed one at a time
The parent sends input k+1 only after the child has emitted its decision for input k, so the
candidate never holds future inputs. The construction passed to check() is the list of decisions.
"""
import importlib.util
import io
import json
import os
import re
import tokenize
from pathlib import Path

from .sandbox import run_candidate, run_online

GENERIC_REJECTION = "rejected by the integrity gate"
# Any gain over the best known value above float noise triggers the independent strict check.
# Strict checks use a 1e-12 tolerance: enough for float rounding of exact constructions,
# far below the 1e-9 tolerance an exploit would hide in.
EXCEED_EPS = 1e-12

# Candidate programs have no business touching files, processes, the network or the evaluator.
_FORBIDDEN = [
    (r"\bopen\s*\(|\bpathlib\b|\bio\s*\.\s*open\b|\btempfile\b|\bpickle\b|\bshelve\b", "file access"),
    (r"(?<![.\w])(eval|exec|compile)\s*\(", "dynamic code execution"),
    (r"\b(subprocess|socket|urllib|requests|httpx|http\.client|ftplib|shutil)\b", "process or network access"),
    (r"\bos\s*\.\s*(system|popen|exec\w*|spawn\w*|remove|unlink|rmdir|environ|getenv|kill|fork)", "os access"),
    (r"\b(importlib|__import__|sys\s*\.\s*modules|builtins|ctypes|gc\s*\.\s*get_objects)\b", "import or runtime tampering"),
    (r"(verify|evaluate|gate|sandbox)\.py|metrics\.json|correct\.json|integrity\.json", "evaluator access"),
]


def _load_verify(problem_dir: Path):
    spec = importlib.util.spec_from_file_location("verify", problem_dir / "verify.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _blank_literals(source: str) -> str:
    """Return source with comment and string-literal *contents* blanked out (replaced by
    spaces, positions preserved), so the static scan reacts to code, not to words that merely
    appear in a comment or string. Code tokens and their adjacency are untouched, so e.g.
    `open(` is still caught while `obj.eval(` (a method, not the builtin) still is not.
    Falls back to the raw source if it will not tokenise (such a program fails to run anyway)."""
    try:
        toks = list(tokenize.generate_tokens(io.StringIO(source).readline))
    except (tokenize.TokenError, IndentationError, SyntaxError):
        return source
    blank = {tokenize.STRING, tokenize.COMMENT}
    for name in ("FSTRING_MIDDLE",):  # 3.12+ splits f-strings; blank only their literal text
        if hasattr(tokenize, name):
            blank.add(getattr(tokenize, name))
    rows = [list(line) for line in source.splitlines(keepends=True)]
    for tok in toks:
        if tok.type not in blank:
            continue
        (sr, sc), (er, ec) = tok.start, tok.end
        for r in range(sr, er + 1):
            row = rows[r - 1]
            a = sc if r == sr else 0
            b = ec if r == er else len(row)
            for c in range(a, min(b, len(row))):
                if row[c] != "\n":
                    row[c] = " "
    return "".join("".join(r) for r in rows)


def static_violations(source: str) -> list:
    scanned = _blank_literals(source)
    return sorted({why for pattern, why in _FORBIDDEN if re.search(pattern, scanned)})


def _label(verify, instance) -> str:
    if hasattr(verify, "label"):
        return verify.label(instance)
    return ", ".join(f"{k}={v}" for k, v in instance.items()) or "default"


def _run_instance(verify, program_path, instance) -> dict:
    rec = {"instance": instance, "label": _label(verify, instance)}
    if hasattr(verify, "online") and hasattr(verify, "DRIVER"):
        header, inputs = verify.online(instance)
        run = run_online(program_path, verify.FUNCTION, verify.DRIVER, header, inputs, verify.TIMEOUT_S)
    else:
        run = run_candidate(program_path, verify.FUNCTION, instance, verify.TIMEOUT_S)
    rec["seconds"] = run.seconds
    if not run.ok:
        rec.update(status="error", score=None, normalized=0.0, reason=run.error)
        return rec
    try:
        res = verify.check(run.construction, instance)
    except Exception as e:  # malformed constructions must not crash the gate
        res = {"valid": False, "score": None, "reason": f"malformed construction ({type(e).__name__})"}
    best = verify.best_known(instance)
    rec["best_known"] = best
    if not res["valid"]:
        rec.update(status="invalid", score=None, normalized=0.0, reason=res["reason"])
        return rec
    score = float(res["score"])
    rec.update(status="valid", score=score, reason=res.get("reason", ""))
    if best is not None and score > best + EXCEED_EPS:
        # Beating the best known result is either a discovery or an exploit. Re-check independently.
        strict_ok = verify.check_strict(run.construction, instance) if hasattr(verify, "check_strict") else None
        if strict_ok is False:
            rec.update(status="integrity", normalized=0.0,
                       reason="beats the best known value but fails the independent strict check")
            return rec
        rec["flag"] = "exceeds best known value: needs human review" + (
            "" if strict_ok else " (no independent check available)")
    rec["normalized"] = score / best if best else score
    return rec


def evaluate(problem_dir, program_path: str, results_dir: str) -> dict:
    problem_dir = Path(problem_dir)
    os.makedirs(results_dir, exist_ok=True)
    verify = _load_verify(problem_dir)
    source = Path(program_path).read_text()

    integrity_log = {"program": os.path.abspath(program_path), "static_violations": static_violations(source)}
    if integrity_log["static_violations"]:
        metrics = {"combined_score": 0.0, "public": {}, "private": {"integrity": "static"},
                   "text_feedback": f"Program {GENERIC_REJECTION}."}
        _write(results_dir, metrics, correct=False, error=GENERIC_REJECTION, integrity=integrity_log)
        return metrics

    public = [_run_instance(verify, program_path, inst) for inst in verify.PUBLIC]
    hidden = [_run_instance(verify, program_path, inst) for inst in getattr(verify, "HIDDEN", [])]
    integrity_log["public"], integrity_log["hidden"] = public, hidden

    caught = [r for r in public + hidden if r["status"] == "integrity"]
    combined = sum(r["normalized"] for r in public) / max(len(public), 1)
    lines = []
    for r in public:
        if r["status"] == "valid":
            best = f" (best known {r['best_known']:.6g})" if r.get("best_known") else ""
            lines.append(f"{r['label']}: score {r['score']:.6g}{best}")
        elif r["status"] == "invalid":
            lines.append(f"{r['label']}: invalid construction: {r['reason']}")
        elif r["status"] == "error":
            lines.append(f"{r['label']}: program failed: {r['reason']}")
        else:
            lines.append(f"{r['label']}: {GENERIC_REJECTION}")  # C': never leak why
    private = {"hidden_normalized": [round(r["normalized"], 6) for r in hidden],
               "hidden_mean": sum(r["normalized"] for r in hidden) / len(hidden) if hidden else None,
               "integrity_rejections": len(caught),
               "flags": [f"{r['label']}: {r['flag']}" for r in public + hidden if r.get("flag")]}
    metrics = {
        "combined_score": 0.0 if caught else combined,
        "public": {r["label"]: r["score"] for r in public},
        "private": private,
        "text_feedback": "\n".join(lines),
    }
    correct = not caught and any(r["status"] == "valid" for r in public)
    error = GENERIC_REJECTION if caught else (None if correct else "no valid construction on public instances")
    _write(results_dir, metrics, correct=correct, error=error, integrity=integrity_log)
    return metrics


def _write(results_dir, metrics, correct, error, integrity):
    with open(os.path.join(results_dir, "metrics.json"), "w") as f:
        json.dump(metrics, f, indent=2)
    with open(os.path.join(results_dir, "correct.json"), "w") as f:
        json.dump({"correct": correct, "error": error}, f, indent=2)
    with open(os.path.join(results_dir, "integrity.json"), "w") as f:
        json.dump(integrity, f, indent=2, default=str)
