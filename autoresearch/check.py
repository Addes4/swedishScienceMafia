"""Score a program on a problem without any LLM: checks a problem folder end to end.

    python -m autoresearch.check problems/erdos_squares              # scores initial.py
    python -m autoresearch.check problems/erdos_squares my_prog.py   # scores another program
    python -m autoresearch.check --all                               # every problem's initial.py
"""
import argparse
import json
import tempfile
import time
from pathlib import Path

from .gate import evaluate

ROOT = Path(__file__).resolve().parents[1]


def check(problem_dir: Path, program: Path) -> dict:
    with tempfile.TemporaryDirectory() as out:
        t0 = time.time()
        metrics = evaluate(problem_dir, str(program), out)
        correct = json.loads(Path(out, "correct.json").read_text())
        integrity = json.loads(Path(out, "integrity.json").read_text())
    print(f"== {problem_dir.name}  ({program.name}, {time.time() - t0:.1f}s)")
    print(f"combined_score {metrics['combined_score']:.4f}   correct {correct['correct']}   error {correct['error']}")
    print("feedback shown to the LLM:")
    print("  " + metrics["text_feedback"].replace("\n", "\n  "))
    print(f"private (hidden from the LLM): {json.dumps(metrics['private'])}")
    if integrity.get("static_violations"):
        print(f"static violations (hidden from the LLM): {integrity['static_violations']}")
    return metrics


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("problem", nargs="?")
    ap.add_argument("program", nargs="?")
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args()
    if args.all:
        for p in sorted((ROOT / "problems").iterdir()):
            if (p / "verify.py").exists():
                check(p, p / "initial.py")
        return
    problem = Path(args.problem).resolve()
    check(problem, Path(args.program).resolve() if args.program else problem / "initial.py")


if __name__ == "__main__":
    main()
