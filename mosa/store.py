"""The lab notebook: one append-only JSON-lines file of events per lab (runs/<lab>/events.jsonl).

Every event is one line {"type": ..., "time": ..., ...}: the lab's configuration, each prompt, strategy, per-run
progress and result, verified record and the end. Appends hold an exclusive file lock, so the lab process and its
worker processes can write to the same notebook; the workbench and replay read it back in order.
"""
from __future__ import annotations

import fcntl
import json
from pathlib import Path
import time

import numpy as np


def _plain(value):
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, (np.floating, np.integer)):
        return value.item()
    raise TypeError(f"not JSON serializable: {type(value)}")


class Notebook:
    def __init__(self, directory):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self.path = self.directory/"events.jsonl"

    def write(self, event, **fields):
        line = json.dumps({"type": event, "time": time.time(), **fields}, default=_plain, separators=(",", ":"))+"\n"
        with open(self.path, "a") as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            f.write(line)

    def read(self):
        if not self.path.exists():
            return []
        return [json.loads(line) for line in self.path.read_text().splitlines() if line.endswith("}")]
