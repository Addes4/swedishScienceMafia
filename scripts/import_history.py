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


def lab(name, directory, brief="", references=(), polish=4):
    directory = Path(directory)
    summary = json.loads((directory/"strategy_lab.json").read_text()) if (directory/"strategy_lab.json").exists() else {}
    chains = sorted(directory.glob("chain-*"), key=lambda p: int(p.name.split("-")[1]))
    first = min(mtime(next(c.glob("round-01")) / "prompt.txt") for c in chains)
    book = Book(name)
    targets = sorted({int(k.split("/")[0]) for c in chains for r in json.loads((c/"chain.json").read_text())["rounds"]
                      for k in r["results"]})
    seeds = sorted({k.split("/")[1] for c in chains for r in json.loads((c/"chain.json").read_text())["rounds"]
                    for k in r["results"] if "/" in k}) or ["0"]
    rounds = max(len(json.loads((c/"chain.json").read_text())["rounds"]) for c in chains)
    book.add("lab", first-1, kind="lab", domain="squares", title=D.title, targets=targets, chains=len(chains),
             rounds=rounds, seeds=list(range(len(seeds))), backend="modal", brief=brief, references=list(references),
             budget={**OLD_BUDGET, "polish": polish}, model="codex", library=[],
             foci=[json.loads((c/"chain.json").read_text())["focus"] for c in chains], imported_from=str(directory))
    for c in chains:
        index = int(c.name.split("-")[1])
        data = json.loads((c/"chain.json").read_text())
        for r in data["rounds"]:
            k = r["round"]
            rd = c/f"round-{k:02}"
            tag = {"chain": index, "round": k}
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
        book.add("done", first+summary["wall_seconds"])
    book.save()


def candidates(name, directory, source, targets, pattern=r"n(\d+)"):
    """A run of one fixed strategy, imported from its saved candidate records only."""
    directory = Path(directory)
    files = sorted(directory.glob("candidate-record-*.npy"), key=mtime)
    if not files:
        return
    book = Book(name)
    start = min(map(mtime, files))-60
    book.add("lab", start, kind="apply", domain="squares", title=D.title, targets=targets, backend="modal", source=source,
             imported_from=str(directory))
    book.add("strategy", start, chain=0, round=1, decision="apply", builds_on=source, source=source, mapping="", strategy="", code="")
    for f in files:
        n = int(re.search(pattern, f.name).group(1))
        seed = int(m.group(1)) if (m := re.search(r"seed(\d+)", f.name)) else 0
        record(book, mtime(f), n, f, chain=0, round=1, seed=seed)
    book.save()


def main(runs):
    runs = Path(runs)
    lab("2026-10-04-strategy-lab", runs/"strategy-lab")
    if (runs/"lab-67").exists():
        lab("2026-10-04-lab-67-goebel", runs/"lab-67", brief=(OUT.parent/"briefs"/"n67-goebel.md").read_text()
            if (OUT.parent/"briefs"/"n67-goebel.md").exists() else "", references=[17], polish=16)
    candidates("2026-10-04-splice-126", runs/"splice-126", "Cut-and-splice recombination (Deaven & Ho 1995), chosen by hand", [126])
    candidates("2026-10-04-apply-below-100", runs/"modal-below-100", "library: cut-and-splice (strategy lab, chain 3, round 3)",
               list(range(11, 100)))
    candidates("2026-10-04-apply-local", runs/"local-below-100", "library: cut-and-splice (strategy lab, chain 3, round 3)",
               [88, 83, 70, 54, 37])


if __name__ == "__main__":
    main(sys.argv[1])
