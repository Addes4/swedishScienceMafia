"""Copy a grid's results from the Modal Volume into experiments/tournament-v1/runs/<grid>/ and rebuild the report.

    python -m tournament.pull full-v1
    python -m tournament.pull full-v1 --no-report

After download, runs that were stopped from outside (and so never packed their own files) get
their arm folders packed into artifacts.tar.gz, and logs over 1 MB are gzipped (metrics reads
either form), so a grid folder stays small enough to commit. Every run gets summary.json and
curve.csv recomputed from its raw logs.
"""
import argparse
import gzip
import json
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path

from .metrics import summarize, write_curve
from .modal_app import VOLUME_NAME
from .run import ARM_DIRS

REPO = Path(__file__).resolve().parents[1]
RUNS = REPO / "experiments" / "tournament-v1" / "runs"
GZIP_ABOVE_BYTES = 1_000_000


def compact(grid_dir: Path) -> None:
    for run in sorted(p for p in grid_dir.iterdir() if p.is_dir()):
        dirs = [d for d in ARM_DIRS if (run / d).is_dir()]
        if dirs and not (run / "artifacts.tar.gz").exists():
            with tarfile.open(run / "artifacts.tar.gz", "w:gz") as tar:
                for d in dirs:
                    tar.add(run / d, arcname=d)
            for d in dirs:
                shutil.rmtree(run / d)
        for log in list(run.glob("*.jsonl")) + list(run.glob("*.log")):
            if log.stat().st_size > GZIP_ABOVE_BYTES:
                with open(log, "rb") as src, gzip.open(log.with_name(log.name + ".gz"), "wb") as dst:
                    shutil.copyfileobj(src, dst)
                log.unlink()
        if (run / "job.json").exists():   # recompute from the raw logs: covers runs killed before writing one
            summary = summarize(run)
            (run / "summary.json").write_text(json.dumps(summary, indent=2, default=str))
            write_curve(summary, run / "curve.csv")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("grid", help="grid name (the folder on the Volume)")
    ap.add_argument("--dest", default=str(RUNS))
    ap.add_argument("--no-report", action="store_true")
    a = ap.parse_args(argv)
    dest = Path(a.dest)
    dest.mkdir(parents=True, exist_ok=True)
    target = dest / a.grid
    if target.exists():
        shutil.rmtree(target)
    modal = str(Path(sys.executable).with_name("modal"))
    subprocess.run([modal, "volume", "get", "--force", VOLUME_NAME, f"/{a.grid}", str(dest)], check=True)
    compact(target)
    print(f"pulled {len(list(target.glob('*/job.json')))} runs into {target}")
    if not a.no_report:
        from .report import main as report
        report([str(target), "--recompute"])


if __name__ == "__main__":
    main()
