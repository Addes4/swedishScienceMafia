"""Import the night's research (runs of the squarelab prototype, 2026-10-04) into Mosa notebooks under history/.

Each lab becomes history/<name>/events.jsonl in the same event format Mosa writes, with times taken from the files
(prompt written = round start, answer written = strategy, results written = round end). Every saved candidate record
is re-verified here with Mosa's independent audit; nothing is copied as a record without a fresh certificate. Fields
the prototype did not record (e.g. the researcher's decision in the first lab) are left out, not inferred.

    python scripts/import_history.py /path/to/swedishScienceMafia/runs
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import sys

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from mosa.domain import get  # noqa: E402

D = get("squares")
OUT = Path(__file__).resolve().parents[1]/"history"
CUT_AND_SPLICE = "Symmetry-aware cut-and-splice genetic search from molecular and atomic cluster optimization"
OLD_BUDGET = {"init": 512, "children": 128, "generations": 12, "population": 32}


def mtime(path):
    return os.path.getmtime(path)


class Book:
    def __init__(self, name):
        self.directory = OUT/name
        self.directory.mkdir(parents=True, exist_ok=True)
        self.events = []

    def add(self, event, time, **fields):
        self.events.append({"type": event, "time": time, **fields})

    def save(self):
        self.events.sort(key=lambda e: e["time"])
        (self.directory/"events.jsonl").write_text("".join(json.dumps(e, separators=(",", ":"))+"\n" for e in self.events))
        print(f"{self.directory.name}: {len(self.events)} events, {sum(e['type'] == 'record' for e in self.events)} verified records")


def record(book, time, n, path, **tag):
    poses = np.load(path)
    certificate = D.verify(poses, n)
    if certificate["record"]:
        book.add("record", time, **tag, **certificate, imported_from=str(path))
        (book.directory/"records").mkdir(exist_ok=True)
        stem = book.directory/"records"/f"n{n}-{'-'.join(f'{k}{v}' for k, v in tag.items())}"
        stem.with_suffix(".svg").write_text(D.svg(certificate["poses"], certificate["side"]))
    return certificate


def answer(round_directory):
    """The researcher's final JSON answer from the model's event stream."""
    for line in reversed((round_directory/"events.jsonl").read_text().splitlines()):
        event = json.loads(line)
        item = event.get("item", {})
        if event.get("type") == "item.completed" and item.get("type") == "agent_message":
            return json.loads(item["text"])
    raise ValueError(f"no answer in {round_directory}")


def lab(name, directory, brief="", references=(), polish=4, title=None, save=True, book=None, session=0):
    directory = Path(directory)
    summary = json.loads((directory/"strategy_lab.json").read_text()) if (directory/"strategy_lab.json").exists() else {}
    chains = sorted(directory.glob("chain-*"), key=lambda p: int(p.name.split("-")[1]))
    first = min(mtime(next(c.glob("round-01")) / "prompt.txt") for c in chains)
    book = book or Book(name)
    targets = sorted({int(k.split("/")[0]) for c in chains for r in json.loads((c/"chain.json").read_text())["rounds"]
                      for k in r["results"]})
    seeds = sorted({k.split("/")[1] for c in chains for r in json.loads((c/"chain.json").read_text())["rounds"]
                    for k in r["results"] if "/" in k}) or ["0"]
    rounds = max(len(json.loads((c/"chain.json").read_text())["rounds"]) for c in chains)
    book.add("lab", first-1, session=session, kind="lab", name=title, domain="squares", title=D.title, targets=targets, chains=len(chains),
             rounds=rounds, seeds=list(range(len(seeds))), backend="modal", brief=brief, references=list(references),
             budget={**OLD_BUDGET, "polish": polish}, model="codex", library=[],
             foci=[json.loads((c/"chain.json").read_text())["focus"] for c in chains], imported_from=str(directory))
    for c in chains:
        index = int(c.name.split("-")[1])
        data = json.loads((c/"chain.json").read_text())
        for r in data["rounds"]:
            k = r["round"]
            rd = c/f"round-{k:02}"
            tag = {"session": session, "idea": [session, index, k], "chain": index, "round": k}
            book.add("prompt", mtime(rd/"prompt.txt"), **tag, focus=data["focus"], prompt=(rd/"prompt.txt").read_text())
            a = answer(rd)
            book.add("strategy", mtime(rd/"events.jsonl"), **tag, **{f: a[f] for f in ("source", "mapping", "strategy", "code")},
                     **({"decision": a["decision"]} if "decision" in a else {}))
            finished = mtime(c/f"round-{k+1:02}"/"prompt.txt") if (c/f"round-{k+1:02}").exists() else mtime(c/"chain.json")
            verified = 0
            for key, row in r["results"].items():
                n = int(key.split("/")[0])
                seed = int(key.split("seed")[1]) if "/" in key else 0
                result = {"n": n, "seed": seed}
                if "error" in row:
                    result["error"] = row["error"]
                else:
                    result.update(best_known=row["best_known"], polished=row["polished"], gap=row["gap"], record=row["beaten"],
                                  runner_up_gap=row.get("runner_up_gap"), initial_gap=row.get("initial_population_best_gap"),
                                  dropped=row.get("invalid_candidates_dropped", 0), failed=0)
                book.add("result", finished-0.5, **tag, **result)
                if row.get("beaten"):
                    files = list(c.glob(f"candidate-record-n{n}-round{k}*.npy"))
                    if files and record(book, finished-0.4, n, files[0], **tag, seed=seed)["record"]:
                        verified += 1
            book.add("round", finished-0.3, **tag, records=verified, errors=sum("error" in v for v in r["results"].values()))
    if summary.get("wall_seconds"):
        book.add("done", first+summary["wall_seconds"], session=session)
    if save:
        book.save()
    return book


def rerun(book, session, directory, idea, source, targets=None, seeds=None, begun=None):
    """A later session that ran an existing idea on more instances: its results and records attach to that idea. Runs
    that ended before writing apply.json kept only their record-breaking packings."""
    directory = Path(directory)
    rows = json.loads((directory/"apply.json").read_text())["rows"] if (directory/"apply.json").exists() else None
    files = sorted(directory.glob("candidate-record-*.npy"), key=mtime)
    times = [mtime(f) for f in files]+([mtime(directory/"apply.json")] if rows else [])
    if not times:
        return
    start, end = begun or min(times)-60, max(times)
    tag = {"session": session, "idea": list(idea), "chain": idea[1], "round": idea[2]}
    book.add("lab", start, session=session, kind="apply", domain="squares", title=D.title, idea=list(idea), source=source,
             targets=targets or sorted({r["n"] for r in rows}), seeds=seeds or sorted({r["seed"] for r in rows}), backend="modal",
             results_saved=None if rows else "records only", imported_from=str(directory))
    for r in rows or []:
        book.add("result", end-1, **tag, n=r["n"], seed=r["seed"], best_known=r.get("best_known"), polished=r.get("polished"),
                 gap=r.get("gap"), record=r.get("beaten", False), runner_up_gap=r.get("runner_up_gap"),
                 initial_gap=r.get("initial_population_best_gap"), dropped=r.get("invalid_candidates_dropped", 0), failed=0)
    verified = 0
    for f in files:
        n = int(re.search(r"n(\d+)", f.name).group(1))
        seed = int(m.group(1)) if (m := re.search(r"seed(\d+)", f.name)) else 0
        verified += record(book, mtime(f), n, f, **tag, seed=seed)["record"]
    book.add("round", end+1, **tag, records=verified, errors=0)
    book.add("done", end+2, session=session)


def single(book, session, directory, source, targets, seeds, title=None):
    """A session with one fixed strategy (no researcher), imported from its saved records."""
    directory = Path(directory)
    files = sorted(directory.glob("candidate-record-*.npy"), key=mtime)
    start, end = min(map(mtime, files))-60, max(map(mtime, files))
    tag = {"session": session, "idea": [session, 0, 1], "chain": 0, "round": 1}
    book.add("lab", start, session=session, kind="apply", name=title, domain="squares", title=D.title, targets=targets, seeds=seeds,
             backend="modal", source=source, results_saved="records only", imported_from=str(directory))
    book.add("strategy", start, **tag, decision="apply", builds_on=source, source=source, mapping="", strategy="", code="")
    for f in files:
        record(book, mtime(f), int(re.search(r"n(\d+)", f.name).group(1)), f, **tag, seed=1)
    book.add("round", end+1, **tag, records=len(files), errors=0)
    book.add("done", end+2, session=session)


def started(directory):
    """When a run began: its folder's creation time (each run created its folder first)."""
    return os.stat(directory).st_birthtime


def main(runs):
    """All of the night's squares work becomes one workspace, its runs sessions in time order, as Mosa would run it now.
    (These sessions ran before workspaces existed, so they did not yet share memory with each other.)"""
    runs = Path(runs)
    for old in [*OUT.glob("2026-10-04-*")]:  # earlier imports: one notebook per run
        for f in sorted(old.rglob("*"), reverse=True):
            f.unlink() if f.is_file() else f.rmdir()
        old.rmdir()
    below_100 = [n for n in D.targets() if 11 <= n < 100]
    sessions = sorted([(started(runs/d), d) for d in ("splice-126", "strategy-lab", "local-below-100", "modal-below-100", "modal-67", "lab-67")
                       if (runs/d).exists()])
    index = {d: k for k, (_, d) in enumerate(sessions)}
    cut_and_splice = (index["strategy-lab"], 3, 3)  # Researcher 4, round 3 of the researchers on n = 101-132
    book = Book("squares")
    for d, k in index.items():
        if d == "splice-126":
            single(book, k, runs/d, "Cut-and-splice recombination (Deaven & Ho 1995), a method chosen by hand", [126], [1], "Squares in a square")
        elif d == "strategy-lab":
            lab(None, runs/d, book=book, session=k, save=False)
        elif d == "lab-67":
            lab(None, runs/d, brief=(OUT.parent/"briefs"/"n67-goebel.md").read_text(), references=[17], polish=16, book=book, session=k, save=False)
        elif d == "local-below-100":
            rerun(book, k, runs/d, cut_and_splice, CUT_AND_SPLICE, [37, 54, 70, 83, 88], list(range(2, 22)), begun=started(runs/d))
        elif d == "modal-below-100":
            rerun(book, k, runs/d, cut_and_splice, CUT_AND_SPLICE, below_100, list(range(101, 109)), begun=started(runs/d))
        else:
            rerun(book, k, runs/d, cut_and_splice, CUT_AND_SPLICE, begun=started(runs/d))
    book.add("name", min(e["time"] for e in book.events)-2, name="Squares in a square")
    book.save()
    print("sessions:", [d for _, d in sessions])

if __name__ == "__main__":
    main(sys.argv[1])
