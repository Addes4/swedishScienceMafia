"""The planning agent: turns a request in plain words into a session plan, then runs it.

    python -m mosa run "Beat the best known square packings near n = 120" --backend modal
    python -m mosa run "Now focus on n = 67 and borrow from n = 17" --out runs/squares

The plan picks the problem (one of the available harnesses; a workspace keeps one problem family, because one strategy
must run on all of its instances), the instances, the number of researchers, rounds and seeds, and a brief for the
researchers. It is written to the workspace as a 'plan' event with its reasoning, then executed as a normal session.
"""
from __future__ import annotations

import json
from pathlib import Path

from .domain import get
from .llm import ask
from .store import Notebook

DOMAINS = ("squares", "thomson")
SCHEMA = {"type": "object", "additionalProperties": False,
          "required": ["name", "domain", "targets", "researchers", "rounds", "seeds", "brief", "references", "reasoning"],
          "properties": {"name": {"type": "string"}, "domain": {"type": "string", "enum": list(DOMAINS)},
                         "targets": {"type": "array", "items": {"type": "integer"}},
                         "researchers": {"type": "integer"}, "rounds": {"type": "integer"}, "seeds": {"type": "integer"},
                         "brief": {"type": "string"}, "references": {"type": "array", "items": {"type": "integer"}},
                         "reasoning": {"type": "string"}}}


def workspace_state(events):
    """What the workspace already has, in a few lines: its problem, instances, best results and ideas so far."""
    if not events:
        return ""
    head = next(e for e in events if e["type"] == "lab")
    best = {}
    for e in events:
        if e["type"] == "result" and not e.get("error") and e.get("gap") is not None:
            best[e["n"]] = min(best.get(e["n"], 9e9), e["gap"])
    ideas = [e.get("name") or e.get("source", "")[:80] for e in events if e["type"] == "strategy"]
    return json.dumps({"problem": head.get("domain"), "instances": sorted(best), "best_gap_per_instance": best,
                       "researchers_so_far": max([e.get("chain", 0)+1 for e in events if e["type"] == "strategy"] or [0]),
                       "ideas_so_far": ideas}, separators=(",", ":"))


COMPUTE = {"modal": "Modal (thousands of cores): up to 6 researchers, 5 rounds, 24 instances and 4 seeds per instance.",
           "local": "this machine (a few cores, each run takes minutes): at most 2 researchers, 2 rounds, 4 instances and 1 seed."}


def plan(request, events=(), model=None, directory=None, backend="modal"):
    domains = {name: get(name) for name in DOMAINS}
    catalogue = {name: {"title": d.title, "problem": d.problem, "sizes_with_best_known": f"{min(d.targets())}-{max(d.targets())}"}
                 for name, d in domains.items()}
    state = workspace_state(list(events))
    text = f"""You plan research sessions for Mosa, a framework in which LLM researchers write search strategies for hard
optimization problems and trusted tools test every strategy on every instance at equal budget.

Available problems (harnesses):
{json.dumps(catalogue, indent=1)}

{"This is a new workspace." if not state else "The session goes into an existing workspace (keep its problem):"}
{state}

Compute available: {COMPUTE[backend]}

The user asks: {request}

Plan one session. Choose the problem; the instances (sizes n that have a best known value; 4-24 instances, contiguous
blocks help researchers share what they find between neighbouring sizes); the number of researchers (2-6; more for open
questions); rounds per researcher (2-5; more when ideas need refining); seeds per instance (1-4; more when single runs
are noisy); reference sizes whose best solutions strategies may borrow from (may be empty); a short workspace name (2-5
words); and a brief: what the researchers should know or focus on, from the user's request (empty if nothing to add).
Explain the plan in one or two sentences in "reasoning"."""
    answer = ask(text, SCHEMA, directory or Path("runs")/".plans", model, timeout=600)
    known = set(domains[answer["domain"]].targets())
    answer["targets"] = sorted({n for n in answer["targets"] if n in known})[:24] or sorted(known)[:6]
    answer["researchers"] = max(1, min(6, answer["researchers"]))
    answer["rounds"] = max(1, min(5, answer["rounds"]))
    answer["seeds"] = max(1, min(4, answer["seeds"]))
    return answer


def run(request, out, backend="modal", model=None, workers=None, budget=None):
    from .research import Lab
    book = Notebook(out)
    events = book.read()
    book.write("request", request=request, session=sum(e["type"] == "lab" for e in events))
    first = next((e for e in events if e["type"] == "lab"), None)
    p = plan(request, events, model, Path(out)/"plans", backend)
    if backend == "local":  # keep a local session small enough to finish
        p.update(researchers=min(p["researchers"], 2), rounds=min(p["rounds"], 2), seeds=1, targets=p["targets"][:4])
    if first and p["domain"] != first.get("domain"):
        p["domain"] = first["domain"]  # a workspace keeps one problem family
    lab = Lab(p["domain"], backend, out, budget, p["references"], workers)
    lab.write("plan", request=request, **p)
    lab.lab(p["targets"], p["researchers"], p["rounds"], list(range(p["seeds"])), p["brief"], model, None if first else p["name"])
