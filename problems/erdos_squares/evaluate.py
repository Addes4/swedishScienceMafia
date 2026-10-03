"""ShinkaEvolve entry point: python evaluate.py --program_path P --results_dir R"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from autoresearch.gate import evaluate  # noqa: E402

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--program_path", required=True)
    ap.add_argument("--results_dir", required=True)
    args = ap.parse_args()
    evaluate(Path(__file__).resolve().parent, args.program_path, args.results_dir)
