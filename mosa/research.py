"""Research labs: researcher chains that write search strategies, run them at equal budget and learn from the results.

Each chain is a researcher. Every round it sees the problem, the measured evidence about the landscape, an optional
brief for the targets, the library of strategies that already broke records, and its own previous strategies with
their per-target, per-seed results, including near misses (how close the best other basin came). It answers with a
decision (new idea, refinement or combination), the idea's source and why it fits, and code for the strategy template
(see evaluate.py). The framework runs that code on every target and seed, verifies any candidate record independently
and writes everything to the lab's notebook (store.py), which the workbench reads.

    python -m mosa lab --targets 101 102 103 --chains 4 --rounds 3 --backend modal --out runs/lab
"""
from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from dataclasses import asdict
import json
import os
from pathlib import Path
import threading

from .backends import Local, Modal, session
from .domain import get
from .evaluate import Budget, run
from .llm import ask
from .store import Notebook

FOCI = ["a strategy imported from another field (physics, chemistry, biology, operations research, ...) whose search landscapes "
        "share these properties",
        "a strategy imported from another field whose landscapes share these properties; prefer a different field from the obvious one",
        "a strategy that exploits how the best known solutions are built (see the evidence)",
        "any strategy you expect to beat the best known solutions"]
SCHEMA = {"type": "object", "additionalProperties": False,
          "required": ["name", "decision", "builds_on", "source", "mapping", "strategy", "code"],
          "properties": {"decision": {"type": "string", "enum": ["new", "refine", "combine"]},
                         **{k: {"type": "string"} for k in ("name", "builds_on", "source", "mapping", "strategy", "code")}}}
SHOWN = ("record", "gap", "runner_up_gap", "initial_gap", "dropped", "failed", "error")  # per-run fields the researcher sees


def span(targets):
    targets = sorted(targets)
    return f"{targets[0]}-{targets[-1]}" if targets == list(range(targets[0], targets[-1]+1)) else ", ".join(map(str, targets))


def prompt(domain, targets, seeds, budget, focus, history, library, brief):
    text = [f"""You are a researcher developing search strategies for a hard optimization problem. {domain.problem} The goal is
to beat the best known solutions for n = {span(targets)}. You write the strategy, not individual solutions.

{domain.evidence}

The strategy fills an evolutionary template. The framework calls initialize once ({budget.init} candidates), keeps the best
{budget.population} distinct basins (the best known solution is always included), then for {budget.generations} generations calls vary
({budget.children} candidates each), relaxes every candidate to convergence and keeps the best {budget.population} distinct basins of
parents and children. The best {budget.polish} are finally polished to their exact local optimum. A polished value below the best
known one is a candidate record, verified independently. Every strategy gets the same compute, on {len(seeds)} random seed(s) per
target.

Write Python implementing exactly these functions (only np, math and numba are available; rng is a numpy Generator).
Every call runs in a fresh process, so keep no state between calls: vary gets everything it needs from its parents:
{domain.api}

Focus: {focus}. Name the method or idea you draw on and its source field, and explain why its assumptions match the
measured landscape. Return JSON with "name" (the idea in at most six words), "decision" (new, refine or combine), "builds_on" (the earlier round or library
strategy it builds on, or "none"), "source" (method and field), "mapping" (why it fits this landscape), "strategy" (what
initialize and vary do) and "code"."""]
    if brief:
        text.append("Research brief for these targets:\n"+brief)
    if library:
        text.append("Strategies that have already broken records on this problem (build on them, combine them, or find what they "
                    "miss; a copy of one is not a contribution):\n"+json.dumps(library, separators=(",", ":")))
    if history:
        text.append("Your previous strategies and their per-target results. gap = polished value minus the best known value "
                    "(negative is a new record; 0 means the best known solution stayed best). runner_up_gap = the same for the best "
                    "other basin found, after polish (small is a near miss); initial_gap = the same for the best initial candidate. "
                    "One run is a single random sample of a noisy search: a run without records does not refute an idea, and a near "
                    "miss or a mis-scaled implementation (one that never gets close to the best known value) may succeed when "
                    "refined. Decide from this evidence whether to refine a previous strategy (its scale, implementation or "
                    "parameters; every round uses new seeds), combine strategies, or try a new idea:\n"
                    +json.dumps(history, separators=(",", ":")))
    return "\n\n".join(text)


def _local_run(job):
    """One run in a worker process (local backend): progress goes straight to the notebook."""
    name, code, n, seed, budget, references, notebook, tag = job
    domain = get(name)
    book = Notebook(notebook)
    return run(domain, Local(domain), code, n, seed, Budget(**budget), references,
               progress=lambda g, best: book.write("progress", **tag, n=n, seed=seed, generation=g, best=best))


class Lab:
    def __init__(self, domain, backend, out, budget=None, references=(), library_path=None, workers=None):
        self.domain, self.backend, self.budget, self.references = get(domain), backend, budget or Budget(), tuple(references)
        self.notebook = Notebook(out)
        self.out = Path(out)
        self.library_path = Path(library_path) if library_path else None
        self.library = json.loads(self.library_path.read_text()) if self.library_path and self.library_path.exists() else []
        self.lock = threading.Lock()
        self.pool = ProcessPoolExecutor(workers or max(1, (os.cpu_count() or 2)-1)) if backend == "local" else None
        self.remote = Modal(self.domain) if backend == "modal" else None

    def runs(self, code, targets, seeds, tag):
        """Run code on every target and seed; write each result (and verified record) to the notebook as it arrives."""
        jobs = [(n, seed) for n in targets for seed in seeds]
        if self.pool:
            futures = [self.pool.submit(_local_run, (self.domain.name, code, n, seed, asdict(self.budget), self.references,
                                                     self.notebook.path.parent, tag)) for n, seed in jobs]
            return [self.keep(f.result(), tag) for f in futures]

        def one(job):
            n, seed = job
            result = run(self.domain, self.remote, code, n, seed, self.budget, self.references,
                         progress=lambda g, best: self.notebook.write("progress", **tag, n=n, seed=seed, generation=g, best=best))
            return self.keep(result, tag)
        with ThreadPoolExecutor(len(jobs)) as pool:
            return list(pool.map(one, jobs))

    def keep(self, result, tag):
        self.notebook.write("result", **tag, **result)
        if result.get("record"):
            n, seed = result["n"], result["seed"]
            certificate = self.domain.verify(result["best"]["x"], n)
            self.notebook.write("record", **tag, seed=seed, **certificate)
            name = self.out/"records"/f"n{n}-{'-'.join(f'{k}{v}' for k, v in tag.items())}-seed{seed}"
            name.parent.mkdir(exist_ok=True)
            name.with_suffix(".json").write_text(json.dumps(certificate))
            name.with_suffix(".svg").write_text(self.domain.svg(certificate["poses"], certificate["side"]))
            result["verified"] = certificate["record"]
        return result

    def learn(self, answer, results, origin):
        """Add a strategy whose round produced a verified record to the library."""
        records = {str(r["n"]): r["polished"] for r in results if r.get("verified")}
        if not records:
            return
        entry = {"source": answer["source"], "strategy": answer["strategy"], "code": answer["code"], "records_broken": records,
                 "origin": origin}
        with self.lock:
            self.library.append(entry)
            if self.library_path:
                self.library_path.write_text(json.dumps(self.library, indent=1))
        self.notebook.write("library", **entry)

    def chain(self, index, rounds, targets, seeds, brief, model):
        history, tag0 = [], {"chain": index}
        for r in range(1, rounds+1):
            tag = {**tag0, "round": r}
            focus = FOCI[index % len(FOCI)]
            text = prompt(self.domain, targets, seeds, self.budget, focus, history, self.library, brief)
            self.notebook.write("prompt", **tag, focus=focus, prompt=text)
            try:
                answer = ask(text, SCHEMA, self.out/f"chain-{index}"/f"round-{r:02}", model)
            except Exception as error:
                self.notebook.write("error", **tag, error=str(error))
                raise
            self.notebook.write("strategy", **tag, **answer)
            results = self.runs(answer["code"], targets, [1000*index+r+100000*k for k in seeds], tag)
            self.learn(answer, results, f"{self.out}:chain {index}:round {r}")
            history.append({"round": r, "decision": answer["decision"], "source": answer["source"], "strategy": answer["strategy"],
                            "code": answer["code"], "results": {(str(x["n"]) if len(seeds) == 1 else f"{x['n']}/seed{x['seed']}"):
                                                                {k: x[k] for k in SHOWN if k in x} for x in results}})
            self.notebook.write("round", **tag, records=sum(bool(x.get("verified")) for x in results),
                                errors=sum("error" in x for x in results))

    def lab(self, targets, chains, rounds, seeds, brief="", model=None):
        self.notebook.write("lab", kind="lab", domain=self.domain.name, title=self.domain.title, targets=list(targets),
                            chains=chains, rounds=rounds, seeds=list(seeds), backend=self.backend, brief=brief,
                            references=list(self.references), budget=asdict(self.budget), model=model,
                            library=[e["source"] for e in self.library], foci=FOCI[:chains])
        with session(self.backend):
            with ThreadPoolExecutor(chains) as pool:
                list(pool.map(lambda i: self.chain(i, rounds, targets, seeds, brief, model), range(chains)))
        self.notebook.write("done")

    def apply(self, code, source, targets, seeds):
        """Run one strategy (no model) on targets and seeds, e.g. a library strategy on new sizes."""
        self.notebook.write("lab", kind="apply", domain=self.domain.name, title=self.domain.title, targets=list(targets),
                            seeds=list(seeds), backend=self.backend, references=list(self.references), budget=asdict(self.budget),
                            source=source)
        self.notebook.write("strategy", chain=0, round=1, decision="apply", builds_on=source, source=source, mapping="",
                            strategy="", code=code)
        with session(self.backend):
            results = self.runs(code, targets, list(seeds), {"chain": 0, "round": 1})
        self.notebook.write("round", chain=0, round=1, records=sum(bool(x.get("verified")) for x in results),
                            errors=sum("error" in x for x in results))
        self.notebook.write("done")
