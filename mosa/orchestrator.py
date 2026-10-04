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

from .domain import get, library
from .llm import ask
from .store import Notebook

SCHEMA = {"type": "object", "additionalProperties": False,
          "required": ["action", "reply", "problem_request", "base", "idea", "scale", "name", "problems", "targets", "researchers", "rounds", "seeds", "brief", "references"],
          "properties": {"action": {"type": "string", "enum": ["start", "answer", "draft", "apply"]}, "reply": {"type": "string"},
                         "problem_request": {"type": "string"}, "base": {"type": "string"}, "idea": {"type": "string"},
                         "scale": {"type": "string", "enum": ["quick", "full"]},
                         "name": {"type": "string"}, "problems": {"type": "array", "items": {"type": "string"}},
                         "targets": {"type": "array", "items": {"type": "integer"}},
                         "researchers": {"type": "integer"}, "rounds": {"type": "integer"}, "seeds": {"type": "integer"},
                         "brief": {"type": "string"}, "references": {"type": "array", "items": {"type": "integer"}}}}
QUICK_BUDGET = dict(init=96, children=32, generations=5, population=16, polish=8)
COMPUTE = {"modal": "Modal (a few hundred cores, on a limited budget): up to 4 researchers, 3 rounds, 8 instances and 3 seeds per instance.",
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
            ideas[key] = {"id": ":".join(map(str, key)), "researcher": e.get("chain", 0)+1, "round": e.get("round"), "idea": e.get("name") or e.get("source", "")[:90],
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
    instances = sorted({tuple(i) for e in events if e["type"] == "lab" for i in (e.get("instances") or [[e.get("domain"), n] for n in e.get("targets", [])])})
    return {"family": get(head.get("domain")).family, "instances": [f"{p} n={n}" for p, n in instances],
            "best_gap_per_instance": best, "ideas": list(ideas.values()),
            "running": sum(e["type"] == "lab" for e in events) > sum(e["type"] == "done" for e in events)}


def respond(message, events=(), model=None, directory=None, backend="modal", context=None):
    events = list(events)
    state = workspace_state(events)
    conversation = [{"user": e["request"]} if e["type"] == "request" else {"agent": e["reply"]}
                    for e in events if e["type"] == "request" or (e["type"] in ("plan", "reply") and e.get("reply"))][-12:]
    text = f"""You are the research agent of a Mosa workspace. In Mosa, LLM researchers write search strategies for hard
optimization problems and trusted tools test every strategy on every instance at equal budget; a workspace is one problem,
its instances, and a shared memory of what has been found.

The problem library (each problem has a trusted harness; problems in one family share a representation, so one strategy
runs on all of them; "riesz-<s>" stands for any exponent, e.g. riesz-2 or riesz-0.5):
{json.dumps(library(), indent=1)}

Workspace state: {json.dumps(state, separators=(",", ":")) if state else "new workspace, nothing run yet"}
Conversation so far: {json.dumps(conversation, separators=(",", ":"))}
Compute available: {COMPUTE[backend]}

{f"The user is looking at {context} while writing this; 'this' refers to it." if context else ""}
The user says: {message}

Either answer in words (action "answer": questions, explanations, or when nothing should run; the plan fields are then
ignored, fill them with anything valid); or, when the user wants to research a problem that is NOT in the library, ask
for a harness to be drafted for it (action "draft": put a precise statement of the problem as a minimization over sizes n
in "problem_request", and in "base" the name of the closest library problem to fork from, e.g. a triangles-in-a-triangle
harness for squares in a square, or "" if none is close; it will be built from that base, self-tested, and you will be
asked again with it in the library); or plan and
start a research session (action "start"). A session is "quick" (a first look or proof of concept: 2 researchers, 2
rounds, 1 seed, up to 3 instances, a small budget per run; it finishes in minutes) unless the user asks for a thorough,
large or long run ("full"); a new workspace starts quick; or run an existing idea of this workspace, as it is and without a
researcher, on more instances (action "apply": its id in "idea", the sizes in "targets", and seeds). A session's plan: the
problems from the library (one or more, all from one family; an existing workspace keeps its family; related problems
in one workspace share what they find); the sizes n to run on each of them (4-24 in all; contiguous blocks let
researchers share what they find between neighbouring sizes; for problems with published values, sizes that have one); researchers (2-6, more for open questions);
rounds per researcher (2-5); seeds per instance (1-4, more when single runs are noisy); reference sizes whose best
solutions strategies may borrow from (may be empty); a workspace name of 2-5 words; and a brief for the researchers from
the user's request. In an existing workspace, researchers continue from their earlier ideas. "reply" is what you say to
the user: one to three sentences, plain and specific (for a session: what will run and why)."""
    answer = ask(text, SCHEMA, directory or Path("runs")/".agent", model, timeout=600)
    problems = []
    for p in answer["problems"]:
        try:
            problems.append(get(p.strip().lower()))
        except ValueError:
            pass
    head = next((e for e in events if e["type"] == "lab"), None)
    family = get(head["domain"]).family if head else (problems[0].family if problems else "unit squares")
    problems = [d for d in problems if d.family == family] or [get(head["domain"] if head else "squares")]
    answer["problems"] = [d.name for d in problems]
    answer["instances"] = [[d.name, n] for d in problems for n in sorted(set(answer["targets"])) if n in set(d.targets())][:24] \
        or [[problems[0].name, n] for n in problems[0].targets()[:6]]
    answer["researchers"] = max(1, min(4, answer["researchers"]))
    answer["rounds"] = max(1, min(3, answer["rounds"]))
    answer["seeds"] = max(1, min(3, answer["seeds"]))
    answer["instances"] = answer["instances"][:8]
    if answer["scale"] != "full":  # a quick look: minutes, not hours
        answer.update(researchers=min(answer["researchers"], 2), rounds=min(answer["rounds"], 2), seeds=1, instances=answer["instances"][:3])
    if backend == "local":  # keep a local session small enough to finish
        answer.update(researchers=min(answer["researchers"], 2), rounds=min(answer["rounds"], 2), seeds=1, instances=answer["instances"][:4])
    return answer


def describe_context(context, events):
    """What the user is looking at, in words for the agent: an idea (by id) or an instance."""
    if not context:
        return None
    if context.get("idea"):
        key = [int(v) for v in str(context["idea"]).split(":")]
        strategy = next((e for e in events if e["type"] == "strategy" and (e.get("idea") or [e.get("session", 0), e.get("chain", 0), e.get("round", 1)]) == key), {})
        return f"idea {context['idea']} (researcher {key[1]+1}, round {key[2]}: {strategy.get('name') or strategy.get('source', '')[:90]})"
    if context.get("n"):
        return f"the instance n = {context['n']}" + (f" of {context['problem']}" if context.get("problem") else "")
    return None


def run(message, out, backend="modal", model=None, workers=None, budget=None, context=None):
    from .research import Lab
    book = Notebook(out)
    events = book.read()
    book.write("request", request=message, session=sum(e["type"] == "lab" for e in events), context=context)
    first = next((e for e in events if e["type"] == "lab"), None)
    about = describe_context(context, events)
    p = respond(message, events, model, Path(out)/"agent", backend, about)
    if p["action"] == "draft":
        from .harness import draft
        book.write("reply", drafting=True,
                   reply=p["reply"] or f"That problem is not in the library yet; drafting a harness for it: {p['problem_request']}")
        request, report = p["problem_request"], None
        for attempt in range(3):  # retries are told what failed
            base = p.get("base") or None
            try:
                get(base) if base else None
            except Exception:
                base = None  # not a library problem: draft from scratch
            name, answer, report = draft(request, Path(out)/"harness", model, base)
            book.write("harness", name=name, title=answer["title"], family=answer["family"], about=answer["about"],
                       code=answer["code"], report=report, forked_from=report.get("forked_from"))
            if report.get("passed"):
                break
            request = f"{p['problem_request']}\n\nA previous draft failed its self-test: {json.dumps(report)[:1500]}"
        if not report.get("passed"):
            book.write("reply", reply="The drafted harness failed its self-test three times, so nothing was run. Its code and tests are above.")
            return
        p = respond(message+f"\n(The harness {name} has been drafted and passed its self-test: use it.)", book.read(), model, Path(out)/"agent", backend)
        if p["action"] != "start":
            book.write("reply", reply=p["reply"])
            return
    if p["action"] == "apply" and first:
        try:
            key = tuple(int(v) for v in p["idea"].split(":"))
        except ValueError:
            key = None
        lab = Lab(first["domain"], backend, out, budget, p["references"], workers)
        if key not in lab.ideas:
            book.write("reply", reply=p["reply"] or f"There is no idea {p['idea']} in this workspace.")
            return
        known = set(lab.domain.targets())
        targets = sorted({n for n in p["targets"] if n in known})[:4 if backend == "local" else 24]
        seeds = list(range(1, 1+max(1, min(1 if backend == "local" else 4, p["seeds"]))))
        lab.write("plan", request=message, reply=p["reply"], action="apply", idea=list(key), targets=targets, seeds=len(seeds),
                  instances=[[lab.domain.name, n] for n in targets])
        lab.apply(None, None, targets, seeds, idea=key)
        return
    if p["action"] in ("answer", "apply"):
        book.write("reply", reply=p["reply"])
        return
    if p.get("scale") != "full" and budget is None:  # a quick session also runs each strategy at a small budget
        from .evaluate import Budget
        budget = Budget(**QUICK_BUDGET)
    lab = Lab(p["instances"][0][0], backend, out, budget, p["references"], workers)
    lab.write("plan", request=message, **p)
    lab.lab([tuple(i) for i in p["instances"]], p["researchers"], p["rounds"], list(range(p["seeds"])), p["brief"], model,
            None if first else p["name"])
