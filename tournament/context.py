"""What an arm gets: the problem, an output folder, the budget, its config, and a scoring function."""
import hashlib
import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from .budget import Budget
from .evallog import evaluate_logged


@dataclass
class Evaluation:
    tag: str
    code: str
    combined: float
    correct: bool
    rejected: bool                  # integrity gate: static violation or failed strict re-check
    feedback: str                   # what the LLM may see
    public: List[float]             # normalized score per public instance (0 when invalid)
    labels: List[str]
    sha: str

    @property
    def valid(self) -> bool:
        return self.correct and not self.rejected


@dataclass
class Context:
    problem_dir: Path
    out: Path
    seed: int
    budget: Budget
    config: dict = field(default_factory=dict)
    deadline: float = float("inf")

    def __post_init__(self):
        self.problem_dir = Path(self.problem_dir)
        self.out = Path(self.out)
        self.problem = (self.problem_dir / "problem.md").read_text()
        self.initial = (self.problem_dir / "initial.py").read_text()
        self.events_path = self.out / "events.jsonl"

    def option(self, key, default):
        return self.config.get(key, default)

    def out_of_time(self) -> bool:
        return time.time() > self.deadline

    def event(self, **rec):
        rec = {"t": time.time(), "spent_usd": round(self.budget.total, 6), **rec}
        with open(self.events_path, "a") as f:
            f.write(json.dumps(rec, default=str) + "\n")

    def evaluate(self, code: str, tag: str) -> Evaluation:
        d = self.out / "programs" / tag
        d.mkdir(parents=True, exist_ok=True)
        prog = d / "program.py"
        prog.write_text(code)
        metrics = evaluate_logged(self.problem_dir, str(prog), str(d / "results"), tag=tag)
        correct = json.loads((d / "results" / "correct.json").read_text())
        integrity = json.loads((d / "results" / "integrity.json").read_text())
        public = integrity.get("public", [])
        private = metrics.get("private", {})
        rejected = bool(private.get("integrity_rejections")) or private.get("integrity") == "static"
        return Evaluation(tag=tag, code=code, combined=float(metrics["combined_score"]), correct=bool(correct["correct"]),
                          rejected=rejected, feedback=metrics.get("text_feedback", ""),
                          public=[float(r["normalized"]) for r in public], labels=[r["label"] for r in public],
                          sha=hashlib.sha256(code.encode()).hexdigest()[:16])

    def incumbent(self, ev: Evaluation, note: Optional[str] = None):
        """Record the program this arm would submit if the run ended now."""
        self.event(event="incumbent", tag=ev.tag, sha=ev.sha, score=ev.combined, note=note)
        (self.out / "best_program.py").write_text(ev.code)
