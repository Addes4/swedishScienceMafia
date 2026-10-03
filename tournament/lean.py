"""Lean: the smallest complete autoresearch loop, and two add-ons from this project.

lean            one call per step proposes and implements a change to the current best program;
                the best valid program is kept; the prompt lists recent attempts and outcomes.
+ gate          non-regression gate (from Falsify) on problems with several public instances: a
                candidate is not accepted if it scores below its parent on any instance in an
                archive of instances where earlier valid candidates scored below their parents.
+ patience      the Patience restart rule from strategist/controller.py: after T consecutive
                non-improving steps on the working line, restart with a fresh program written
                from the problem statement. The best program found so far is always kept.
independent     the baseline without any loop: every call writes a program from the problem
                statement and the starting program only (no history, no parent); the best valid
                program is kept. Independent sampling in Gideoni, Risi & Gal (2026).

Plain lean is greedy sequential best-of-N: each call conditions on the current best and the
recent outcomes, and only improvements are kept.

Only public-instance results are used for any decision. Hidden-instance scores exist only in
the private evaluation log.
"""
import re
import time
from dataclasses import dataclass
from types import SimpleNamespace
from typing import Optional

from autoresearch.claude import Claude, parse_code
from strategist.controller import Patience, context

from .budget import BudgetExhausted
from .context import Context, Evaluation

DEFAULTS = {"model": "claude-sonnet-5-5", "effort": "high", "max_tokens": 32000, "history": 8,
            "max_iters": 10_000, "max_consecutive_errors": 6, "error_backoff_s": 10.0, "gate": False, "patience": None,
            "independent": False}
EPS = 1e-9

SYSTEM = """You are an expert researcher and programmer improving a program for the problem below.
Each turn you propose one change to the current program and implement it; the new program is then
scored, and you see the outcome on the next turn.

PROBLEM
{problem}

RULES
- Reply with the change in one or two sentences inside <change></change> tags, then the complete
  new program in a single ```python block, and nothing after it.
- Keep the required function name and signature.
- Use only the standard library, numpy and scipy. Do not read or write files, start processes,
  use the network, or use eval/exec/importlib: such programs are rejected.
- Respect the time limit stated in the problem."""

EDIT_USER = """Current program (score {score:.6g}, where 1.0 means matching the best known result):
```python
{code}
```

Evaluator feedback on it:
{feedback}

Recent attempts and their outcomes (most recent last):
{history}

Propose one change that you expect to improve the score, and implement it."""

INDEPENDENT_SYSTEM = """You are an expert researcher and programmer. Write a program for the problem below
that scores as high as possible.

PROBLEM
{problem}

RULES
- Reply with your approach in one or two sentences inside <change></change> tags, then the
  complete program in a single ```python block, and nothing after it.
- Keep the required function name and signature.
- Use only the standard library, numpy and scipy. Do not read or write files, start processes,
  use the network, or use eval/exec/importlib: such programs are rejected.
- Respect the time limit stated in the problem."""

INDEPENDENT_USER = """The starting program below is a simple baseline that shows the required interface:
```python
{initial}
```

Write a complete program that scores as high as possible."""

RESTART_USER = """Write a new program for this problem from scratch. Use a different approach from the ones
already explored{explored}.

The starting program shows the required interface:
```python
{initial}
```"""


@dataclass
class Program:
    ev: Evaluation
    summary: str

    @property
    def score(self) -> float:
        return self.ev.combined


def parse_change(text: str) -> str:
    m = re.search(r"<change>(.*?)</change>", text or "", re.S)
    return re.sub(r"\s+", " ", m.group(1)).strip()[:300] if m else "(no description)"


def regressions(cand: Evaluation, parent: Evaluation, eps: float = EPS):
    """Public instances where the candidate scores below its parent."""
    return {i for i, (c, p) in enumerate(zip(cand.public, parent.public)) if c < p - eps}


class Gate:
    """Archive of instances where earlier valid candidates regressed; candidates may not regress there."""

    def __init__(self, enabled: bool):
        self.enabled = enabled
        self.archive = set()

    def check(self, cand: Evaluation, parent: Evaluation):
        """(passes, archived instances the candidate regressed on), judged before this candidate is archived."""
        if not self.enabled:
            return True, set()
        hit = regressions(cand, parent) & self.archive
        return not hit, hit

    def record(self, cand: Evaluation, parent: Evaluation):
        if self.enabled and cand.valid and len(cand.public) > 1:
            self.archive |= regressions(cand, parent)


def describe(outcome: str, cand: Optional[Evaluation], parent_score: float, gate_hits=(), labels=()) -> str:
    if outcome == "improved":
        return f"improved {parent_score:.6g} -> {cand.combined:.6g}"
    if outcome == "not_better":
        return f"valid, score {cand.combined:.6g} (not better than {parent_score:.6g})"
    if outcome == "gate_rejected":
        names = ", ".join(labels[i] for i in sorted(gate_hits)) if labels else str(sorted(gate_hits))
        return (f"score {cand.combined:.6g} but rejected: it scored worse on {names}, where earlier "
                f"candidates also regressed")
    if outcome in ("invalid", "rejected") and cand is not None:
        first = next((line for line in cand.feedback.splitlines() if "score" not in line), cand.feedback[:200])
        return f"{outcome}: {first[:200]}"
    return outcome


def run(ctx: Context):
    cfg = {**DEFAULTS, **ctx.config}
    independent = bool(cfg["independent"])
    if independent and (cfg["gate"] or cfg["patience"]):
        raise ValueError("independent sampling has no parent, so it takes neither a gate nor a restart rule")
    claude = Claude()
    system = (INDEPENDENT_SYSTEM if independent else SYSTEM).format(problem=ctx.problem)
    gate = Gate(bool(cfg["gate"]))
    policy = Patience(int(cfg["patience"])) if cfg["patience"] else None

    first = ctx.evaluate(ctx.initial, "initial")
    best = working = Program(first, "the starting program")
    ctx.incumbent(first, "initial")
    state = SimpleNamespace(stall=0, line=0, leader_line=0)
    history, explored = [], []
    errors, stop = 0, "max_iters"

    for it in range(1, cfg["max_iters"] + 1):
        if ctx.out_of_time():
            stop = "wall"
            break
        op = policy.choose(context(state.stall, state.line == state.leader_line), state) if policy else "edit"
        if independent:
            op, user = "sample", INDEPENDENT_USER.format(initial=ctx.initial)
        elif op == "restart":
            explored_txt = "".join(f"\n- {s}" for s in explored[-6:])
            user = RESTART_USER.format(initial=ctx.initial, explored=(":" + explored_txt) if explored else "")
        else:
            hist = "\n".join(f"- {h}" for h in history[-cfg["history"]:]) or "(none yet)"
            user = EDIT_USER.format(score=working.score, code=working.ev.code, feedback=working.ev.feedback, history=hist)

        rec = {"event": "step", "iter": it, "op": op, "line": state.line}
        try:
            call = claude.call(cfg["model"], system, user, max_tokens=cfg["max_tokens"], effort=cfg["effort"])
        except BudgetExhausted:
            stop = "budget"
            break
        except Exception as e:  # API errors must not kill the run
            errors += 1
            ctx.event(**rec, outcome="api_error", detail=f"{type(e).__name__}: {str(e)[:300]}")
            if errors >= cfg["max_consecutive_errors"]:
                stop = "api_errors"
                break
            time.sleep(min(120.0, cfg["error_backoff_s"] * 2 ** (errors - 1)))
            continue
        errors = 0
        rec.update(cost=call.cost, input_tokens=call.input_tokens, output_tokens=call.output_tokens,
                   llm_seconds=round(call.seconds, 2))
        code = None if call.refused else parse_code(call.text)
        summary = parse_change(call.text) if not call.refused else "(refused)"
        cand, hits = None, set()
        if call.refused:
            outcome = "refused"
        elif not code:
            outcome = "no_code"
        else:
            cand = ctx.evaluate(code, f"it{it:04d}")
            parent = working.ev
            if cand.rejected:
                outcome = "rejected"
            elif not cand.correct:
                outcome = "invalid"
            elif op == "restart":
                outcome = "restarted"
            else:
                passes, hits = gate.check(cand, parent)
                if cand.combined <= parent.combined + EPS:
                    outcome = "not_better"
                elif not passes:
                    outcome = "gate_rejected"
                else:
                    outcome = "improved"
            if op != "restart":
                gate.record(cand, parent)

        parent_score = working.score
        if op == "restart":
            if outcome == "restarted":  # the old line is left; its best stays the incumbent until beaten
                state.line += 1
                state.stall = 0
                working = Program(cand, summary)
                explored.append(summary)
            # a failed restart leaves the stall count high, so the next step restarts again
        elif outcome == "improved":
            working = Program(cand, summary)
            state.stall = 0
        else:
            state.stall += 1

        if working.score > best.score + EPS and working is not best:
            best = working
            state.leader_line = state.line
            ctx.incumbent(best.ev, f"iter {it}")

        if op == "restart":
            history.append(f"[fresh start] {summary} -> " + (f"new line, score {cand.combined:.6g}" if outcome == "restarted"
                                                              else describe(outcome, cand, parent_score)))
        else:
            history.append(f"{summary} -> {describe(outcome, cand, parent_score, hits, cand.labels if cand else ())}")
        ctx.event(**rec, outcome=outcome, summary=summary, score=None if cand is None else cand.combined,
                  working=working.score, best=best.score, stall=state.stall,
                  gate_archive=sorted(gate.archive) if gate.enabled else None,
                  gate_hits=sorted(hits) or None)

    ctx.event(event="end", stop=stop, best=best.score, best_tag=best.ev.tag, lines=state.line + 1,
              gate_archive=sorted(gate.archive) if gate.enabled else None)
    return stop
