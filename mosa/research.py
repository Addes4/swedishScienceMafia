"""Research labs: researcher chains that write search strategies, run them at equal budget and learn from the results.

Each chain is a researcher. Every round it sees the problem, the measured evidence about the landscape, an optional
brief for the targets, the library of strategies that already broke records, and its own previous strategies with
their per-target, per-seed results, including near misses (how close the best other basin came). It answers with a
decision (new idea, refinement or combination), the idea's source and why it fits, and code for the strategy template
(see evaluate.py). The framework runs that code on every target and seed, verifies any candidate record independently
and writes everything to the lab's notebook (store.py), which the workbench reads.

    python -m mosa lab --targets 101-110 --chains 4 --rounds 3 --backend modal --out runs/squares
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
from .evaluate import Budget, neighbours_for, run
from .llm import ask
from .sandbox import violations
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


def describe(instances):
    """Instances in words: n = 124-127, or per problem when the session spans several related problems."""
    by = {}
    for p, n in instances:
        by.setdefault(p, []).append(n)
    if len(by) == 1:
        return f"n = {span(next(iter(by.values())))}"
    return "; ".join(f"{get(p).title}, n = {span(ns)}" for p, ns in by.items())


def prompt(domain, instances, seeds, budget, focus, history, library, brief):
    problems = sorted({p for p, _ in instances})
    related = "" if len(problems) == 1 else (f" The instances span related problems ({', '.join(problems)}); they share the "
                                             "representation below, and the global `problem` names the one your code is running on.")
    given = ("record is None in initialize: no known solution is given for these instances, so build candidates from scratch "
             "(or from neighbours);") if all(get(p).reference(n)[0] is None for p, n in instances) else \
        "record may be None for an instance without a known solution;"
    text = [f"""You are a researcher developing search strategies for a hard optimization problem. {domain.problem} The goal is
to beat the best known solutions for {describe(instances)}.{related} You write the strategy, not individual solutions.

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

Guaranteed by the framework, whatever the description above says: the globals n (the size) and problem (the problem's
name) are set in every call; {given} neighbours may be an empty dict; every candidate is a pair (x, value).

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
    name, code, n, seed, budget, neighbours, notebook, tag = job
    domain = get(name)
    book = Notebook(notebook)
    return run(domain, Local(domain), code, n, seed, Budget(**budget), neighbours,
               progress=lambda g, best: book.write("progress", **tag, n=n, seed=seed, generation=g, best=best))


def code_problem(code):
    """Why strategy code cannot run, found before any compute is spent: a syntax error or the integrity scan."""
    try:
        compile(code, "strategy", "exec")
    except SyntaxError as error:
        return f"SyntaxError: {error.msg} (line {error.lineno}: {(error.text or '').strip()})"
    flagged = violations(code)
    return f"the integrity scan rejects it: {', '.join(flagged)}" if flagged else None


class Lab:
    """A session in a workspace. The workspace is the notebook directory: every session appends to it, and the shared
    memory (the best solution found for each instance) is rebuilt from everything already in it, so what one session
    found for n = 118 is offered to strategies working on n = 88 in the next. Ideas are identified by
    (session, researcher, round); running an idea on more instances adds results to that same idea."""

    def __init__(self, domain, backend, out, budget=None, references=(), workers=None):
        self.domain, self.backend, self.budget, self.references = get(domain), backend, budget or Budget(), tuple(references)
        self.domains = {self.domain.name: self.domain}
        self.notebook = Notebook(out)
        self.out = Path(out)
        past = self.notebook.read()
        first = next((e for e in past if e["type"] == "lab"), None)
        if first and get(first.get("domain")).family != self.domain.family:
            raise ValueError(f"this workspace holds {get(first['domain']).family} problems, not {self.domain.family}")
        self.session = sum(e["type"] == "lab" for e in past)
        self.past = past
        # the workspace's library: its ideas that produced verified records, offered to every researcher in it
        self.library = [{k: e[k] for k in ("source", "strategy", "code", "records_broken")} for e in past if e["type"] == "library"]
        self.ideas = {tuple(e.get("idea") or (e.get("session", 0), e.get("chain", 0), e.get("round", 1))): e.get("code", "")
                      for e in past if e["type"] == "strategy"}
        self.lock = threading.Lock()
        self.goal, self.goal_met = None, threading.Event()
        # the workspace's shared memory: best solution found so far for each instance, {(problem, n): (x, value)}
        self.memory = {}
        for e in past:
            key = (e.get("problem") or (first or {}).get("domain"), e.get("n"))
            if e["type"] == "result" and e.get("best") and (key not in self.memory or e["best"]["value"] < self.memory[key][1]):
                self.memory[key] = (e["best"]["x"], e["best"]["value"])
        self.pool = ProcessPoolExecutor(workers or max(1, (os.cpu_count() or 2)-1)) if backend == "local" else None
        self.remote = {}

    def problem(self, name):
        if name not in self.domains:
            self.domains[name] = get(name)
        return self.domains[name]

    def instances(self, targets):
        """Instances as (problem, n): a bare n means this session's default problem."""
        return [tuple(t) if isinstance(t, (list, tuple)) else (self.domain.name, int(t)) for t in targets]

    def write(self, event, **fields):
        self.notebook.write(event, session=self.session, **fields)

    def tag(self, chain, round_, idea=None):
        return {"idea": list(idea or (self.session, chain, round_)), "chain": chain, "round": round_}

    def runs(self, code, instances, seeds, tag):
        """Run code on every instance and seed; write each result (and verified record) to the notebook as it arrives."""
        jobs = [(p, n, seed) for p, n in instances for seed in seeds]
        if self.pool:
            futures = [self.pool.submit(_local_run, (p, code, n, seed, asdict(self.budget), self.neighbours(p, n),
                                                     self.notebook.path.parent, {**tag, "session": self.session, "problem": p}))
                       for p, n, seed in jobs]
            return [self.keep(f.result(), tag) for f in futures]

        def one(job):
            p, n, seed = job
            if p not in self.remote:
                self.remote[p] = Modal(self.problem(p))
            result = run(self.problem(p), self.remote[p], code, n, seed, self.budget, self.neighbours(p, n),
                         progress=lambda g, best: self.write("progress", **tag, problem=p, n=n, seed=seed, generation=g, best=best))
            return self.keep(result, tag)
        with ThreadPoolExecutor(len(jobs)) as pool:
            return list(pool.map(one, jobs))

    def neighbours(self, p, n):
        """Best solutions for nearby sizes of the same problem; under key n itself, the best solution of the same size under
        a related problem in this workspace (when this problem has none yet)."""
        with self.lock:
            memory = dict(self.memory)
        own = neighbours_for(self.problem(p), n, self.references, {m: v for (q, m), v in memory.items() if q == p})
        related = [v for (q, m), v in memory.items() if m == n and q != p]
        if related and n not in own:
            own[n] = min(related, key=lambda v: v[1])
        return own

    def keep(self, result, tag):
        self.write("result", **tag, **result)
        if result.get("best"):
            with self.lock:
                key, value = (result.get("problem", self.domain.name), result["n"]), result["best"]["value"]
                if key not in self.memory or value < self.memory[key][1]:
                    self.memory[key] = (result["best"]["x"], value)
        if result.get("record"):
            n, seed = result["n"], result["seed"]
            domain = self.problem(result.get("problem", self.domain.name))
            certificate = domain.verify(result["best"]["x"], n)
            self.write("record", **tag, seed=seed, problem=domain.name, **certificate)
            name = self.out/"records"/f"n{n}-idea{'-'.join(map(str, tag['idea']))}-seed{seed}"
            name.parent.mkdir(exist_ok=True)
            name.with_suffix(".json").write_text(json.dumps(certificate))
            name.with_suffix(".svg").write_text(domain.svg(certificate["poses"], certificate["side"]))
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
            self.library.append({k: entry[k] for k in ("source", "strategy", "code", "records_broken")})
        self.write("library", **entry)

    def history_of(self, index):
        """Researcher index's earlier ideas in this workspace, with every result they have had (including later runs on
        more instances): researchers continue across sessions."""
        researcher_sessions = {e["session"] for e in self.past if e["type"] == "lab" and e.get("kind") == "lab"}
        out = []
        for e in self.past:
            if e["type"] == "strategy" and e.get("chain") == index and e.get("session", 0) in researcher_sessions:
                key = e.get("idea") or [e.get("session", 0), e["chain"], e["round"]]
                results = [x for x in self.past if x["type"] == "result" and (x.get("idea") or [x.get("session", 0), x.get("chain"), x.get("round")]) == key]
                out.append({"round": e["round"], "decision": e.get("decision"), "source": e.get("source"), "strategy": e.get("strategy"),
                            "code": e.get("code"), "results": {f"{x.get('problem', '')} {x['n']}/seed{x['seed']}".strip(): {k: x[k] for k in SHOWN if k in x} for x in results}})
        return sorted(out, key=lambda h: h["round"])

    def stopped(self):
        """Why this session should stop before its last round: its goal is met, or the user asked to stop."""
        if self.goal and self.goal_met.is_set():
            return "goal"
        if any(e["type"] == "stop" and e.get("session") == self.session for e in self.notebook.read()):
            return "stop"
        return None

    def chain(self, index, rounds, targets, seeds, brief, model):
        history = self.history_of(index)
        first = (history[-1]["round"]+1) if history else 1
        for r in range(first, first+rounds):
            if r > first and self.stopped():
                break
            tag = self.tag(index, r)
            focus = FOCI[index % len(FOCI)]
            text = prompt(self.domain, targets, seeds, self.budget, focus, history, self.library, brief)
            self.write("prompt", **tag, focus=focus, prompt=text)
            directory = self.out/f"session-{self.session}"/f"chain-{index}"/f"round-{r:02}"
            try:
                answer = ask(text, SCHEMA, directory, model)
                problem = code_problem(answer["code"])
                if problem:  # one repair call: a typo should not cost a whole round of compute
                    answer = ask(f"{text}\n\nYour previous answer could not be run: {problem}\nReturn the same idea with that fixed.",
                                 SCHEMA, directory/"repair", model)
            except Exception as error:
                self.write("error", **tag, error=str(error))
                raise
            self.write("strategy", **tag, **answer)
            results = self.runs(answer["code"], targets, [1000*index+r+100000*k for k in seeds], tag)
            self.learn(answer, results, f"{self.out}:chain {index}:round {r}")
            history.append({"round": r, "decision": answer["decision"], "source": answer["source"], "strategy": answer["strategy"],
                            "code": answer["code"], "results": {(str(x["n"]) if len(seeds) == 1 else f"{x['n']}/seed{x['seed']}"):
                                                                {k: x[k] for k in SHOWN if k in x} for x in results}})
            self.write("round", **tag, records=sum(bool(x.get("verified")) for x in results), errors=sum("error" in x for x in results))
            if self.goal == "record" and any(x.get("verified") for x in results):
                self.goal_met.set()  # a verified new best-known: every researcher stops after its current round
            elif self.goal == "best_known" and any(x.get("verified") or (x.get("gap") is not None and x["gap"] <= 1e-9) for x in results):
                self.goal_met.set()

    def lab(self, targets, chains, rounds, seeds, brief="", model=None, name=None, goal=None):
        """A session: chains researchers, each up to `rounds` rounds. With a goal ("record": a verified new best-known;
        "best_known": reaching the best known), every researcher stops once any of them meets it; "stop" events from the
        conversation end the session early too."""
        targets = self.instances(targets)
        if goal == "best_known" and all(self.problem(p).reference(n)[0] is not None for p, n in targets):
            goal = "record"  # strategies start from the best known solution: reaching it is no goal
        self.goal, self.goal_met = goal, threading.Event()
        self.write("lab", kind="lab", name=name, domain=self.domain.name, title=self.domain.title, family=self.domain.family,
                   instances=[list(i) for i in targets], targets=sorted({n for _, n in targets}), problems=sorted({p for p, _ in targets}),
                            chains=chains, rounds=rounds, seeds=list(seeds), backend=self.backend, brief=brief,
                            references=list(self.references), budget=asdict(self.budget), model=model,
                            library=[e["source"] for e in self.library], foci=FOCI[:chains], goal=goal)
        with session(self.backend):
            with ThreadPoolExecutor(chains) as pool:
                list(pool.map(lambda i: self.chain(i, rounds, targets, seeds, brief, model), range(chains)))
        self.write("done", ended=self.stopped() or "rounds", goal=goal)

    def apply(self, code, source, targets, seeds, idea=None, name=None):
        """Run one strategy (no model) on targets and seeds. With idea = (session, researcher, round), the code is that
        idea's and its results are added to it; otherwise the strategy (e.g. a baseline file) becomes a new idea."""
        targets = self.instances(targets)
        if idea:
            code, tag = self.ideas[tuple(idea)], self.tag(idea[1], idea[2], idea)
        else:
            tag = self.tag(0, 1)
        self.write("lab", kind="apply", name=name, domain=self.domain.name, title=self.domain.title, family=self.domain.family,
                   instances=[list(i) for i in targets], targets=sorted({n for _, n in targets}), problems=sorted({p for p, _ in targets}),
                   seeds=list(seeds), backend=self.backend, references=list(self.references), budget=asdict(self.budget),
                   source=source, idea=list(idea) if idea else None)
        if not idea:
            self.write("strategy", **tag, decision="apply", builds_on=source, source=source, mapping="", strategy="", code=code)
        with session(self.backend):
            results = self.runs(code, targets, list(seeds), tag)
        self.write("round", **tag, records=sum(bool(x.get("verified")) for x in results), errors=sum("error" in x for x in results))
        self.write("done")
