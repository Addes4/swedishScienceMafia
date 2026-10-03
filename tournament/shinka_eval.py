"""ShinkaEvolve evaluation program for tournament runs: problems/<name>/evaluate.py plus logging.

    python tournament/shinka_eval.py --program_path P --results_dir R      (TOURNAMENT_PROBLEM_DIR set)
"""
import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tournament.evallog import PROBLEM_ENV, evaluate_logged  # noqa: E402

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--program_path", required=True)
    ap.add_argument("--results_dir", required=True)
    args = ap.parse_args()
    evaluate_logged(os.environ[PROBLEM_ENV], args.program_path, args.results_dir, tag="shinka")
