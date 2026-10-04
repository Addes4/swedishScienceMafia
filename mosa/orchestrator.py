"""The research agent: the workspace's conversation partner.

    python -m mosa run "Beat the best known square packings near n = 120" --backend modal
    python -m mosa run "Now focus on n = 126, and borrow from n = 125" --out runs/squares
    python -m mosa run "Why did researcher 2's second idea fail?" --out runs/squares

Each message is answered from the workspace's state and the conversation so far. The agent either answers in words, or
plans a session and starts it: the problem (one of the available harnesses; a workspace keeps one problem family,
because one strategy must run on all of its instances), the instances, researchers, rounds, seeds and a brief, sized to
the compute. Messages, replies and plans are written to the workspace's notebook.
"""
from __future__ import annotations

import json
from pathlib import Path

from .domain import get
from .llm import ask
from .store import Notebook

DOMAINS = ("squares", "thomson")
SCHEMA = {"type": "object", "additionalProperties": False,
          "required": ["action", "reply", "name", "domain", "targets", "researchers", "rounds", "seeds", "brief", "references"],
          "properties": {"action": {"type": "string", "enum": ["start", "answer"]}, "reply": {"type": "string"},
                         "name": {"type": "string"}, "domain": {"type": "string", "enum": list(DOMAINS)},
                         "targets": {"type": "array", "items": {"type": "integer"}},
                         "researchers": {"type": "integer"}, "rounds": {"type": "integer"}, "seeds": {"type": "integer"},
                         "brief": {"type": "string"}, "references": {"type": "array", "items": {"type": "integer"}}}}
COMPUTE = {"modal": "Modal (thousands of cores): up to 6 researchers, 5 rounds, 24 instances and 4 seeds per instance.",
           "local": "this machine (a few cores, each run takes minutes): at most 2 researchers, 2 rounds, 4 instances and 1 seed."}


def workspace_state(events):
    """The workspace in brief: its problem, best result per instance, and every idea with its outcome."""
    head = next((e for e in events if e["type"] == "lab"), None)
    if not head:
        return None
    best, ideas = {}, {}
    for e in events:
        key = tuple(e.get("idea") or ())
        if e["type"] == "strategy" and key:
            ideas[key] = {"researcher": e.get("chain", 0)+1, "round": e.get("round"), "idea": e.get("name") or e.get("source", "")[:90],
                          "records": [], "best_gap": None, "errors": 0, "runs": 0}
        elif e["type"] == "result" and key in ideas:
            i = ideas[key]
            i["runs"] += 1
            if e.get("error"):
                i["errors"] += 1
                i["last_error"] = e["error"].strip().splitlines()[-1][:160]
            elif e.get("gap") is not None:
                best[e["n"]] = min(best.get(e["n"], 9e9), e["gap"])
                i["best_gap"] = e["gap"] if i["best_gap"] is None else min(i["best_gap"], e["gap"])
        elif e["type"] == "record" and e.get("record") and key in ideas:
            ideas[key]["records"].append(e["n"])
    return {"problem": head.get("domain"), "instances": sorted({n for e in events if e["type"] == "lab" for n in e.get("targets", [])}),
            "best_gap_per_instance": best, "ideas": list(ideas.values()),
            "running": sum(e["type"] == "lab" for e in events) > sum(e["type"] == "done" for e in events)}


def respond(message, events=(), model=None, directory=None, backend="modal"):
    domains = {name: get(name) for name in DOMAINS}
    catalogue = {name: {"title": d.title, "problem": d.problem, "sizes_with_best_known": f"{min(d.targets())}-{max(d.targets())}"}
                 for name, d in domains.items()}
    events = list(events)
    state = workspace_state(events)
    conversation = [{"user": e["request"]} if e["type"] == "request" else {"agent": e["reply"]}
                    for e in events if e["type"] == "request" or (e["type"] in ("plan", "reply") and e.get("reply"))][-12:]
    text = f"""You are the research agent of a Mosa workspace. In Mosa, LLM researchers write search strategies for hard
optimization problems and trusted tools test every strategy on every instance at equal budget; a workspace is one problem,
its instances, and a shared memory of what has been found.

Available problems (harnesses):
{json.dumps(catalogue, indent=1)}

Workspace state: {json.dumps(state, separators=(",", ":")) if state else "new workspace, nothing run yet"}
Conversation so far: {json.dumps(conversation, separators=(",", ":"))}
Compute available: {COMPUTE[backend]}

The user says: {message}

Either answer in words (action "answer": questions, explanations, or when nothing should run; the plan fields are then
ignored, fill them with anything valid), or plan and start a research session (action "start"). A session's plan: the
problem (an existing workspace keeps its problem); instances (sizes n with a best known value, 4-24 of them; contiguous
blocks let researchers share what they find between neighbouring sizes); researchers (2-6, more for open questions);
rounds per researcher (2-5); seeds per instance (1-4, more when single runs are noisy); reference sizes whose best
solutions strategies may borrow from (may be empty); a workspace name of 2-5 words; and a brief for the researchers from
the user's request. In an existing workspace, researchers continue from their earlier ideas. "reply" is what you say to
the user: one to three sentences, plain and specific (for a session: what will run and why)."""
    answer = ask(text, SCHEMA, directory or Path("runs")/".agent", model, timeout=600)
    known = set(domains[answer["domain"]].targets())
    answer["targets"] = sorted({n for n in answer["targets"] if n in known})[:24] or sorted(known)[:6]
    answer["researchers"] = max(1, min(6, answer["researchers"]))
    answer["rounds"] = max(1, min(5, answer["rounds"]))
    answer["seeds"] = max(1, min(4, answer["seeds"]))
    if backend == "local":  # keep a local session small enough to finish
        answer.update(researchers=min(answer["researchers"], 2), rounds=min(answer["rounds"], 2), seeds=1, targets=answer["targets"][:4])
    return answer


def run(message, out, backend="modal", model=None, workers=None, budget=None):
    from .research import Lab
    book = Notebook(out)
    events = book.read()
    book.write("request", request=message, session=sum(e["type"] == "lab" for e in events))
    first = next((e for e in events if e["type"] == "lab"), None)
    p = respond(message, events, model, Path(out)/"agent", backend)
    if p["action"] == "answer":
        book.write("reply", reply=p["reply"])
        return
    if first:
        p["domain"] = first["domain"]  # a workspace keeps one problem family
    lab = Lab(p["domain"], backend, out, budget, p["references"], workers)
    lab.write("plan", request=message, **p)
    lab.lab(p["targets"], p["researchers"], p["rounds"], list(range(p["seeds"])), p["brief"], model, None if first else p["name"])
