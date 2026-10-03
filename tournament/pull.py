"""Copy a grid's results from the Modal Volume into experiments/tournament-v1/runs/<grid>/ and rebuild the report.

    python -m tournament.pull mock-v1
    python -m tournament.pull mock-v1 --no-report
"""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

from .modal_app import VOLUME_NAME

REPO = Path(__file__).resolve().parents[1]
RUNS = REPO / "experiments" / "tournament-v1" / "runs"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("grid")
    ap.add_argument("--dest", default=str(RUNS))
    ap.add_argument("--no-report", action="store_true")
    a = ap.parse_args(argv)
    dest = Path(a.dest)
    dest.mkdir(parents=True, exist_ok=True)
    target = dest / a.grid
    if target.exists():
        shutil.rmtree(target)
    modal = str(Path(sys.executable).with_name("modal"))
    subprocess.run([modal, "volume", "get", VOLUME_NAME, f"/{a.grid}", str(dest)], check=True)
    print(f"pulled {len(list(target.glob('*/summary.json')))} finished runs into {target}")
    if not a.no_report:
        from .report import main as report
        report([str(target)])


if __name__ == "__main__":
    main()
