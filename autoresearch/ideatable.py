"""Counterfactual idea table: every idea implemented by every model, so triage policies and
rankers can be scored offline without running a loop per policy.

    python -m autoresearch.ideatable ideas     DIR --calls 8 --k 10       # Opus proposes, dedupe
    python -m autoresearch.ideatable implement DIR --ideas 0:3            # probe: 3 ideas x 3 models
    python -m autoresearch.ideatable rank      DIR --n 48 --rankers random,claude-haiku-4-5,claude-opus-5-5,jev,codex
    python -m autoresearch.ideatable implement DIR --ideas 0:48           # main table
    python -m autoresearch.ideatable implement DIR --replicates 12        # same cell, second sample
    python -m autoresearch.ideatable evaluate  DIR --host modal           # integrity gate on every program
    python -m autoresearch.ideatable table     DIR                        # write table.jsonl
    python -m autoresearch.ideatable status    DIR

Each step resumes: finished cells are skipped. All Claude calls go through a hard spend cap
(autoresearch/spend.py) that reserves the worst-case cost before sending and logs every call
to DIR/usage.jsonl. Prompts and model settings are the triage loop's (autoresearch/claude.py,
autoresearch/triage.py defaults). `--mock` swaps in a canned client for dry runs.
"""
import argparse
import difflib
import hashlib
import json
import os
import random
import re
import subprocess
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from .claude import IDEA_SYSTEM, IDEA_USER, IMPLEMENT_SYSTEM, IMPLEMENT_USER, parse_code, parse_ideas
from .evalcode import evaluate_code
from .gate import evaluate
from .rankers import KINDS, TIERS, ClaudeRanker, RandomRanker, Ranking
from .spend import BudgetExceeded, CappedClaude, SpendLedger

ROOT = Path(__file__).resolve().parents[1]
MODELS = ("claude-haiku-4-5", "claude-sonnet-5-5", "claude-opus-5-5")
SHORT = {"claude-haiku-4-5": "haiku", "claude-sonnet-5-5": "sonnet", "claude-opus-5-5": "opus"}
# triage.py defaults: --efforts "high,high," for opus,sonnet,haiku; --max-tokens 32000.
EFFORT = {"claude-opus-5-5": "high", "claude-sonnet-5-5": "high", "claude-haiku-4-5": None}
IMPL_MAX_TOKENS = 32000
# triage.py defaults for proposals: --idea-model claude-opus-5-5 --idea-effort medium, max_tokens 16000.
IDEA_MODEL, IDEA_EFFORT, IDEA_MAX_TOKENS = "claude-opus-5-5", "medium", 16000
BATCH = 6               # ideas per triage round (triage.py --ideas default); rankers judge one batch per call
ORDER_SEED = 20261003   # presentation order of ideas (rankers, batches, probe, main run)
REPLICATE_SEED = 7      # which cells get a second implementation
MAX_ATTEMPTS = 3        # API errors are retried up to this many attempts per cell
EPS = 1e-9              # triage.py: improved = score > parent + 1e-9


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


class BillingStop(RuntimeError):
    """The API account cannot pay (e.g. credit exhausted): stop starting new cells."""


def is_billing_error(e: Exception) -> bool:
    return "credit balance" in str(e).lower()


def _real_attempts(rec: dict) -> int:
    """Attempts that failed for reasons other than billing (older records lack the counter)."""
    n = rec.get("attempts", 1) - rec.get("billing_failures", 0)
    if "billing_failures" not in rec and "credit balance" in rec.get("detail", "").lower():
        n = 0
    return n


def _read_json(path, default=None):
    path = Path(path)
    return json.loads(path.read_text()) if path.exists() else default


def _write_json(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, indent=2, default=str))
    tmp.replace(path)


# -- ideas -------------------------------------------------------------------------------------

def _norm(text: str) -> list:
    return re.findall(r"[a-z0-9]+", text.lower())


def similarity(a: str, b: str) -> float:
    """Max of word-sequence similarity and word-set Jaccard, both in [0, 1]."""
    wa, wb = _norm(a), _norm(b)
    if not wa or not wb:
        return 0.0
    seq = difflib.SequenceMatcher(None, wa, wb).ratio()
    jac = len(set(wa) & set(wb)) / len(set(wa) | set(wb))
    return max(seq, jac)


def dedupe(candidates, kept=(), threshold=0.75):
    """Keep candidates that are not near-copies of an already kept idea (or of each other)."""
    kept_texts = list(kept)
    new, dropped = [], []
    for text in candidates:
        sims = [(similarity(text, k), k) for k in kept_texts]
        best = max(sims, default=(0.0, None))
        if best[0] >= threshold:
            dropped.append({"text": text, "dup_of": best[1], "similarity": round(best[0], 3)})
        else:
            new.append(text)
            kept_texts.append(text)
    return new, dropped


class IdeaTable:
    def __init__(self, out, problem="problems/erdos_squares", cap=40.0, client=None, mock=False):
        self.out = Path(out)
        self.out.mkdir(parents=True, exist_ok=True)
        self.problem_dir = (ROOT / problem).resolve() if not Path(problem).is_absolute() else Path(problem)
        self.problem = (self.problem_dir / "problem.md").read_text()
        self.ledger = SpendLedger(cap, self.out / "usage.jsonl")
        self._client = client
        self.mock = mock
        self._claude = None

    # lazily build the Claude client so offline commands work without a key
    @property
    def claude(self) -> CappedClaude:
        if self._claude is None:
            if self._client is None:
                if self.mock:
                    from .mock_claude import MockClaude
                    self._client = MockClaude()
                else:
                    from .claude import Claude
                    from .env import load_env, require
                    load_env()
                    require("ANTHROPIC_API_KEY", "the idea table calls Claude")
                    self._client = Claude()
            self._claude = CappedClaude(self._client, self.ledger, trace_dir=self.out / "traces")
        return self._claude

    # -- parent program --------------------------------------------------------------------
    def parent(self) -> dict:
        path = self.out / "parent.json"
        info = _read_json(path)
        if info:
            return info
        code = (self.problem_dir / "initial.py").read_text()
        with tempfile.TemporaryDirectory() as tmp:
            prog = Path(tmp) / "program.py"
            prog.write_text(code)
            metrics = evaluate(self.problem_dir, str(prog), str(Path(tmp) / "results"))
        info = {"problem": self.problem_dir.name, "path": str(self.problem_dir.relative_to(ROOT) / "initial.py")
                if self.problem_dir.is_relative_to(ROOT) else str(self.problem_dir / "initial.py"),
                "code": code, "sha256": sha256(code), "score": metrics["combined_score"],
                "hidden_mean": metrics["private"]["hidden_mean"], "feedback": metrics["text_feedback"]}
        _write_json(path, info)
        return info

    # -- step 1: ideas ------------------------------------------------------------------------
    def generate_ideas(self, calls=8, k=10, threshold=0.75) -> dict:
        path = self.out / "ideas.json"
        state = _read_json(path) or {"generation": {"model": IDEA_MODEL, "effort": IDEA_EFFORT,
                                                    "max_tokens": IDEA_MAX_TOKENS, "k_per_call": k,
                                                    "dedupe_threshold": threshold, "order_seed": ORDER_SEED},
                                     "calls": [], "ideas": [], "dropped": []}
        parent = self.parent()
        system = IDEA_SYSTEM.format(problem=self.problem)
        for c in range(len(state["calls"]), calls):
            kept = [i["text"] for i in state["ideas"]]
            # Later calls see earlier proposals (untested) so they propose different ideas.
            history = "\n".join(f"- {t} -> proposed, not yet tested" for t in kept) or "(none yet)"
            user = IDEA_USER.format(score=parent["score"], code=parent["code"], feedback=parent["feedback"],
                                    history=history, k=k)
            with self.claude.tagged(f"ideas/c{c}"):
                res = self.claude.call(IDEA_MODEL, system, user, max_tokens=IDEA_MAX_TOKENS, effort=IDEA_EFFORT)
            raw = parse_ideas(res.text, k)
            new, dropped = dedupe(raw, kept, threshold)
            for pos, text in enumerate(new):
                state["ideas"].append({"id": f"i{len(state['ideas']):03d}", "text": text, "call": c, "pos": pos})
            state["dropped"] += [dict(d, call=c) for d in dropped]
            state["calls"].append({"call": c, "cost": res.cost, "input_tokens": res.input_tokens,
                                   "output_tokens": res.output_tokens, "seconds": round(res.seconds, 2),
                                   "refused": res.refused, "n_parsed": len(raw), "n_kept": len(new),
                                   "response": res.text})
            _write_json(path, state)          # order is assigned once, over the whole new batch, below
            print(f"[ideas] call {c}: parsed {len(raw)}, kept {len(new)}, pool {len(state['ideas'])}, "
                  f"spent ${self.ledger.spent:.3f}")
        self._assign_order(state)
        _write_json(path, state)
        return state

    @staticmethod
    def _assign_order(state):
        """Random presentation order. Append-only: ideas that already have a position keep it and
        new ideas are shuffled among themselves after them, so extending the pool never reorders it."""
        ideas = state["ideas"]
        start = 1 + max((d["order"] for d in ideas if "order" in d), default=-1)
        new = [d for d in ideas if "order" not in d]
        rng = random.Random(f"{ORDER_SEED}:{start}")
        rng.shuffle(new)
        for k, d in enumerate(new):
            d["order"] = start + k

    def ideas_in_order(self) -> list:
        state = _read_json(self.out / "ideas.json")
        if not state:
            raise SystemExit("no ideas.json yet: run the `ideas` step first")
        return sorted(state["ideas"], key=lambda d: d["order"])

    def batches(self, n) -> list:
        ids = [d["id"] for d in self.ideas_in_order()[:n]]
        return [ids[i:i + BATCH] for i in range(0, len(ids), BATCH)]

    # -- step 2: rankers --------------------------------------------------------------------
    def run_rankers(self, names, n) -> dict:
        path = self.out / "rankings.json"
        data = _read_json(path) or {"n": n, "batch_size": BATCH, "batches": self.batches(n), "rankers": {}}
        if data["n"] != n:
            raise SystemExit(f"rankings.json was made for n={data['n']}; refusing to mix with n={n}")
        parent = self.parent()
        text = {d["id"]: d["text"] for d in self.ideas_in_order()}
        for name in names:
            if name in data["rankers"]:
                print(f"[rank] {name}: already done")
                continue
            t0 = time.time()
            ranker, meta = self._make_ranker(name)
            out = {}
            groups = [sum(data["batches"], [])] if getattr(ranker, "all_at_once", False) else data["batches"]
            for b, ids in enumerate(groups):
                # Each ranker sees each batch in its own random order (position bias); positions are recorded.
                ids = list(ids)
                random.Random(f"{ORDER_SEED}:{name}:{b}").shuffle(ids)
                ideas = [text[i] for i in ids]
                ranks = self._rank_batch(ranker, name, b, parent, ideas, meta)
                for pos, (i, r) in enumerate(zip(ids, ranks)):
                    out[i] = dict(r.to_dict(), batch=b, position=pos)
            meta.update(seconds=round(time.time() - t0, 2), cost=round(sum(r["cost"] for r in out.values()), 6))
            data["rankers"][name] = {"meta": meta, "ideas": out}
            _write_json(path, data)
            print(f"[rank] {name}: {len(out)} ideas, ${meta['cost']:.4f}, {meta['seconds']:.1f}s, "
                  f"parse failures {meta.get('parse_failures', 0)}")
        return data

    def _make_ranker(self, name):
        meta = {"name": name}
        if name == "random":
            return RandomRanker(seed=0), dict(meta, seed=0)
        if name.startswith("claude-"):
            return ClaudeRanker(self.claude, model=name), dict(meta, model=name, max_tokens=4000, effort=None)
        if name == "jev":
            from .env import load_env, require
            from .rankers import JevRanker
            load_env()
            require("TYPESAFE_API_KEY", "the Jev ranker needs it")
            return JevRanker(), meta
        if name == "codex":
            return CodexRanker(trace_dir=self.out / "traces"), dict(meta, all_at_once=True, **codex_config())
        raise SystemExit(f"unknown ranker {name}")

    def _rank_batch(self, ranker, name, b, parent, ideas, meta):
        """Rank one batch; for Claude rankers retry once if the JSON reply does not parse."""
        for attempt in range(2):
            with self.claude.tagged(f"rank/{name}/b{b:02d}/a{attempt}") if name.startswith("claude-") \
                    else _nullcontext():
                try:
                    ranks = ranker.rank(self.problem, parent["score"], parent["code"], [], ideas)
                except TypeError:
                    # ClaudeRanker's parser crashes on a non-string "kind" (e.g. a list). The call was
                    # made and paid for; parse the same reply with the tolerant parser instead.
                    last = self.claude.last if name.startswith("claude-") else None
                    if last is None:
                        raise
                    ranks = parse_rankings(last.text, len(ideas), cost=last.cost, seconds=last.seconds)
                    meta["tolerant_parses"] = meta.get("tolerant_parses", 0) + 1
            if not name.startswith("claude-"):
                return ranks
            last = self.claude.last
            if last is not None and _parses_as_ranking(last.text, len(ideas)):
                return ranks
            meta["parse_failures"] = meta.get("parse_failures", 0) + 1
        meta.setdefault("defaulted_batches", []).append(b)   # ClaudeRanker's defaults (middle, 0.5) stand
        return ranks

    # -- step 3: implementations ---------------------------------------------------------------
    def cell_dir(self, idea_id, model, rep) -> Path:
        return self.out / "cells" / f"{idea_id}__{SHORT[model]}__r{rep}"

    def implement_cell(self, idea, model, rep) -> dict:
        d = self.cell_dir(idea["id"], model, rep)
        call_path = d / "call.json"
        prev = _read_json(call_path)
        if prev and (prev["status"] != "api_error" or _real_attempts(prev) >= MAX_ATTEMPTS):
            return prev
        parent = self.parent()
        user = IMPLEMENT_USER.format(score=parent["score"], code=parent["code"], feedback=parent["feedback"],
                                     idea=idea["text"])
        prev = prev or {}
        rec = {"cell": d.name, "idea_id": idea["id"], "idea": idea["text"], "model": model, "replicate": rep,
               "effort": EFFORT[model], "max_tokens": IMPL_MAX_TOKENS,
               "attempts": prev.get("attempts", 0) + 1, "billing_failures": prev.get("billing_failures", 0),
               "time": time.time()}
        try:
            with self.claude.tagged(f"implement/{d.name}/a{rec['attempts']}"):
                res = self.claude.call(model, IMPLEMENT_SYSTEM.format(problem=self.problem), user,
                                       max_tokens=IMPL_MAX_TOKENS, effort=EFFORT[model])
        except BudgetExceeded:
            raise
        except Exception as e:  # API errors must not kill the run; the cell is retried later
            rec.update(status="api_error", detail=f"{type(e).__name__}: {str(e)[:300]}", cost=0.0)
            billing = is_billing_error(e)
            if billing:   # an account problem, not the cell's: it does not use up the cell's retries
                rec["billing_failures"] += 1
            _write_json(call_path, rec)
            if billing:
                raise BillingStop(rec["detail"])
            return rec
        rec.update(cost=res.cost, input_tokens=res.input_tokens, output_tokens=res.output_tokens,
                   llm_seconds=round(res.seconds, 2), served_by=res.served_by, refused=res.refused)
        code = None if res.refused else parse_code(res.text)
        if res.refused:
            rec["status"] = "refused"
        elif not code:
            rec["status"] = "no_code"
        else:
            rec.update(status="pending_eval", code_sha256=sha256(code))
            d.mkdir(parents=True, exist_ok=True)
            (d / "program.py").write_text(code)
        _write_json(call_path, rec)
        return rec

    def implement(self, cells, workers=6, stop_at=None) -> list:
        """cells: list of (idea, model, replicate). Runs up to `workers` calls at once.
        `stop_at`: soft limit in dollars; no new cell starts once total spend reaches it
        (the hard cap still applies to every call)."""
        results = []
        stop = {"budget": False}

        def job(cell):
            if stop["budget"]:
                return None
            done = _read_json(self.cell_dir(cell[0]["id"], cell[1], cell[2]) / "call.json")
            fresh = done is None or done["status"] == "api_error"
            if fresh and stop_at is not None and self.ledger.spent >= stop_at:
                stop["budget"] = True
                print(f"[implement] soft stop: spent ${self.ledger.spent:.2f} >= ${stop_at:.2f}")
                return None
            try:
                rec = self.implement_cell(*cell)
            except (BudgetExceeded, BillingStop) as e:
                stop["budget"] = True
                print(f"[implement] stopped ({type(e).__name__}): {str(e)[:200]}")
                return None
            except Exception as e:  # a bug or disk error in one cell must not lose the others
                print(f"[implement] {cell[0]['id']}/{cell[1]}/r{cell[2]} crashed: {type(e).__name__}: {e}")
                return None
            print(f"[implement] {rec['cell']}: {rec['status']}  ${rec.get('cost', 0):.4f}  "
                  f"(spent ${self.ledger.spent:.2f})", flush=True)
            return rec

        with ThreadPoolExecutor(max_workers=workers) as pool:
            for rec in pool.map(job, cells):
                if rec is not None:
                    results.append(rec)
        return results

    def main_cells(self, start, stop) -> list:
        return [(idea, m, 0) for idea in self.ideas_in_order()[start:stop] for m in MODELS]

    def replicate_cells(self, n_ideas, count) -> list:
        """`count` cells chosen at random among the first n_ideas, balanced over models."""
        ideas = self.ideas_in_order()[:n_ideas]
        rng = random.Random(REPLICATE_SEED)
        cells = []
        per_model = [count // len(MODELS) + (i < count % len(MODELS)) for i in range(len(MODELS))]
        for m, c in zip(MODELS[::-1], per_model):       # opus first if count is not a multiple of 3
            for idea in rng.sample(ideas, c):
                cells.append((idea, m, 1))
        return cells

    # -- step 4: evaluation -------------------------------------------------------------------
    def pending_evals(self) -> list:
        out = []
        for d in sorted((self.out / "cells").glob("*")):
            rec = _read_json(d / "call.json")
            if rec and rec["status"] == "pending_eval" and not (d / "eval.json").exists():
                out.append(d)
        return out

    def evaluate_pending(self, host="local", workers=2, modal_cap=5.0, eval_replicates=0):
        jobs = [(d, "eval.json") for d in self.pending_evals()]
        self._run_evals(jobs, host, workers, modal_cap)
        if eval_replicates:
            # Re-run the gate on evaluated programs (until `eval_replicates` exist) to measure evaluation noise.
            evaluated = sorted(d for d in (self.out / "cells").glob("*") if (d / "eval.json").exists())
            have = sum((d / "eval_repeat.json").exists() for d in evaluated)
            todo = [d for d in evaluated if not (d / "eval_repeat.json").exists()]
            rng = random.Random(11)
            pick = rng.sample(todo, max(0, min(eval_replicates - have, len(todo))))
            self._run_evals([(d, "eval_repeat.json") for d in pick], host, workers, modal_cap)

    def _run_evals(self, jobs, host, workers, modal_cap):
        if not jobs:
            print("[evaluate] nothing to evaluate")
            return
        print(f"[evaluate] {len(jobs)} programs on {host}")
        codes = [(d / "program.py").read_text() for d, _ in jobs]
        if host == "modal":
            from .modal_eval import evaluate_many
            results = evaluate_many(self.problem_dir, codes, ledger_path=self.out / "modal_usage.jsonl",
                                    cap=modal_cap, labels=[d.name for d, _ in jobs])
        else:
            with ThreadPoolExecutor(max_workers=workers) as pool:
                results = list(pool.map(lambda c: evaluate_code(self.problem_dir, c), codes))
        for (d, name), res in zip(jobs, results):
            if res is None:
                continue
            res["host"] = host
            _write_json(d / name, res)
        print(f"[evaluate] wrote {sum(r is not None for r in results)} results")

    # -- step 5: the table --------------------------------------------------------------------
    def build_table(self) -> list:
        parent = self.parent()
        rows = []
        for d in sorted((self.out / "cells").glob("*")):
            rec = _read_json(d / "call.json")
            if not rec:
                continue
            ev = _read_json(d / "eval.json")
            row = {k: rec.get(k) for k in ("cell", "idea_id", "model", "replicate", "effort", "max_tokens",
                                           "cost", "input_tokens", "output_tokens", "llm_seconds",
                                           "served_by", "attempts", "code_sha256")}
            row["refused"] = rec["status"] == "refused"
            if (d / "program.py").exists():   # program on disk is the one the call record describes
                row["code_consistent"] = sha256((d / "program.py").read_text()) == rec.get("code_sha256")
            row.update(classify(rec, ev, parent["score"]))
            rep = _read_json(d / "eval_repeat.json")
            if rep:
                row["eval_repeat"] = {"score": rep["metrics"]["combined_score"],
                                      "hidden_mean": rep["metrics"]["private"].get("hidden_mean"),
                                      "outcome": classify(rec, rep, parent["score"])["outcome"]}
            rows.append(row)
        with open(self.out / "table.jsonl", "w") as f:
            for r in rows:
                f.write(json.dumps(r) + "\n")
        return rows

    def missing_cells(self, replicates=12) -> list:
        """Cells of the pre-registered design (N ideas x 3 models, plus replicates) without a finished call."""
        n = _read_json(self.out / "rankings.json")["n"]
        cells = self.main_cells(0, n) + self.replicate_cells(n, replicates)
        out = []
        for c in cells:
            rec = _read_json(self.cell_dir(c[0]["id"], c[1], c[2]) / "call.json")
            if rec is None or (rec["status"] == "api_error" and _real_attempts(rec) < MAX_ATTEMPTS):
                out.append(c)
        return out

    def fill_estimate(self, replicates=12) -> dict:
        """Cost of the missing cells at the mean measured cost per finished cell of each model."""
        todo = self.missing_cells(replicates)
        costs = {m: [] for m in MODELS}
        for d in (self.out / "cells").glob("*"):
            rec = _read_json(d / "call.json")
            if rec and rec["status"] != "api_error":
                costs[rec["model"]].append(rec.get("cost") or 0.0)
        mean = {m: sum(v) / len(v) for m, v in costs.items() if v}
        top = {m: max(v) for m, v in costs.items() if v}
        by_model = {SHORT[m]: sum(c[1] == m for c in todo) for m in MODELS}
        est = sum(mean[c[1]] for c in todo)
        return {"cells": len(todo), "by_model": by_model, "ideas_touched": len({c[0]["id"] for c in todo}),
                "mean_cost_per_cell": {SHORT[m]: round(v, 4) for m, v in mean.items()},
                "max_cost_per_cell": {SHORT[m]: round(v, 4) for m, v in top.items()},
                "estimate_usd": round(est, 2), "spent_so_far": round(self.ledger.spent, 4),
                "cap": self.ledger.cap, "fits_cap": self.ledger.spent + est <= self.ledger.cap}

    def fill(self, replicates=12, workers=6, host="modal", modal_cap=5.0, dry_run=False) -> dict:
        """One command to complete the table: implement every missing cell, evaluate, rebuild table.jsonl."""
        est = self.fill_estimate(replicates)
        print(json.dumps(est, indent=2))
        if dry_run or not est["cells"]:
            return est
        soft = self.ledger.cap - 1.0     # keep $1 of the cap unspent (in-flight calls can overshoot a soft stop)
        self.implement(self.missing_cells(replicates), workers=workers, stop_at=soft)
        self.evaluate_pending(host=host, modal_cap=modal_cap, eval_replicates=12)
        self.build_table()
        return est

    def size(self, probe_ideas=3, reserve=6.0, replicates=12) -> dict:
        """The protocol's sizing rule: largest multiple of BATCH with
        spent + reserve + N*c + (replicates/3)*c <= cap, where c = mean probe cost per idea."""
        ideas = self.ideas_in_order()
        costs = []
        for idea in ideas[:probe_ideas]:
            recs = [_read_json(self.cell_dir(idea["id"], m, 0) / "call.json") for m in MODELS]
            if any(r is None for r in recs):
                raise SystemExit(f"probe incomplete for {idea['id']}")
            costs.append(sum(r.get("cost") or 0.0 for r in recs))
        c = sum(costs) / len(costs)
        rep_cost = replicates / len(MODELS) * c
        avail = self.ledger.cap - self.ledger.spent - reserve - rep_cost
        n = min(len(ideas), int(avail // c)) // BATCH * BATCH
        out = {"probe_cost_per_idea": costs, "c": c, "spent_after_probe": self.ledger.spent, "reserve": reserve,
               "replicate_cost_estimate": rep_cost, "pool": len(ideas), "N": n,
               "soft_stop": round(self.ledger.cap - rep_cost - 1.0, 4)}
        _write_json(self.out / "sizing.json", out)
        return out

    def provenance(self) -> dict:
        """config.json: settings, package versions and SHA-256 of every source file the study depends on."""
        import platform
        import numpy
        import scipy
        files = ["autoresearch/claude.py", "autoresearch/rankers.py", "autoresearch/gate.py", "autoresearch/sandbox.py",
                 "autoresearch/triage.py", "autoresearch/spend.py", "autoresearch/ideatable.py",
                 "autoresearch/evalcode.py", "autoresearch/modal_eval.py", "autoresearch/policy_eval.py",
                 "autoresearch/mock_claude.py", f"problems/{self.problem_dir.name}/problem.md",
                 f"problems/{self.problem_dir.name}/initial.py", f"problems/{self.problem_dir.name}/verify.py"]
        cfg = {"problem": self.problem_dir.name, "cap_usd": self.ledger.cap, "models": list(MODELS),
               "effort": EFFORT, "impl_max_tokens": IMPL_MAX_TOKENS, "idea_model": IDEA_MODEL,
               "idea_effort": IDEA_EFFORT, "idea_max_tokens": IDEA_MAX_TOKENS, "batch": BATCH,
               "order_seed": ORDER_SEED, "replicate_seed": REPLICATE_SEED, "max_attempts": MAX_ATTEMPTS,
               "python": platform.python_version(), "numpy": numpy.__version__, "scipy": scipy.__version__,
               "source_sha256": {f: sha256((ROOT / f).read_text()) for f in files if (ROOT / f).exists()}}
        try:
            import anthropic
            cfg["anthropic"] = anthropic.__version__
        except ImportError:
            pass
        _write_json(self.out / "config.json", cfg)
        return cfg

    def status(self) -> dict:
        rows = self.build_table() if (self.out / "cells").exists() else []
        from collections import Counter
        out = {"spent": round(self.ledger.spent, 4), "cap": self.ledger.cap,
               "ideas": len(_read_json(self.out / "ideas.json", {"ideas": []})["ideas"]),
               "cells": len(rows), "outcomes": dict(Counter(r["outcome"] for r in rows)),
               "pending_eval": len(self.pending_evals()) if (self.out / "cells").exists() else 0}
        by_model = {}
        for m in MODELS:
            rs = [r for r in rows if r["model"] == m]
            if rs:
                by_model[SHORT[m]] = {"cells": len(rs), "mean_cost": round(sum(r["cost"] or 0 for r in rs) / len(rs), 4),
                                      "improved": sum(r["improved"] for r in rs),
                                      "mean_llm_s": round(sum(r["llm_seconds"] or 0 for r in rs) / len(rs), 1)}
        out["by_model"] = by_model
        return out


def classify(rec: dict, ev, parent_score: float) -> dict:
    """Outcome exactly as triage.Run.implement assigns it."""
    base = {"outcome": rec["status"], "valid": False, "improved": False, "score": None, "hidden_mean": None,
            "integrity_rejections": None, "flags": [], "eval_seconds": None, "eval_host": None}
    if rec["status"] != "pending_eval":
        return base
    if ev is None:
        return dict(base, outcome="pending_eval")
    m, correct = ev["metrics"], ev["correct"]
    score = m["combined_score"]
    if m["private"].get("integrity_rejections") or m["private"].get("integrity") == "static":
        outcome = "rejected"
    elif not correct["correct"]:
        outcome = "invalid"
    elif score > parent_score + EPS:
        outcome = "improved"
    else:
        outcome = "not_better"
    return {"outcome": outcome, "valid": outcome in ("improved", "not_better"), "improved": outcome == "improved",
            "score": score, "hidden_mean": m["private"].get("hidden_mean"),
            "hidden_normalized": m["private"].get("hidden_normalized"), "public": m.get("public"),
            "integrity_rejections": m["private"].get("integrity_rejections"),
            "static": m["private"].get("integrity") == "static", "flags": m["private"].get("flags", []),
            "eval_seconds": ev.get("seconds"), "eval_host": ev.get("host")}


def _parses_as_ranking(text, n) -> bool:
    try:
        items = json.loads(re.search(r"\[.*\]", text or "", re.S).group(0))
    except (AttributeError, ValueError):
        return False
    return isinstance(items, list) and len(items) >= n and all(isinstance(i, dict) for i in items[:n])


class _nullcontext:
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


# -- Codex ranker (ChatGPT-authenticated CLI, read-only sandbox, one batched prompt) ----------------

CODEX_SYSTEM = ("You judge research ideas before anyone implements them. For each idea, estimate how likely it is "
                "to beat the current best program. Answer with JSON only. Do not run commands or read files; "
                "everything you need is in this message.")


def ranking_prompt(problem, best_score, best_code, history, ideas) -> str:
    """The ClaudeRanker's user prompt (autoresearch/rankers.py), reproduced for other rankers."""
    listing = "\n".join(f"{i}: {idea}" for i, idea in enumerate(ideas))
    return (f"PROBLEM\n{problem[:6000]}\n\nCURRENT BEST (score {best_score:.6g})\n```python\n{best_code[:12000]}\n```\n\n"
            f"RECENT HISTORY\n{json.dumps(history[-20:])}\n\nIDEAS\n{listing}\n\n"
            'Return a JSON list with one object per idea, in order: {"promise": "favourite"|"middle"|"long_shot", '
            '"p_improve": 0..1, "p_repeat": 0..1, "kind": ' + json.dumps(list(KINDS)) + "}")


def _prob(x, default):
    try:
        return min(1.0, max(0.0, float(x)))
    except (TypeError, ValueError):
        return default


def parse_rankings(text, n, cost=0.0, seconds=0.0) -> list:
    """ClaudeRanker's JSON format, parsed tolerantly (missing or malformed fields get its defaults)."""
    try:
        items = json.loads(re.search(r"\[.*\]", text or "", re.S).group(0))
    except (AttributeError, ValueError):
        items = []
    if not isinstance(items, list):
        items = []
    out = []
    for i in range(n):
        it = items[i] if i < len(items) and isinstance(items[i], dict) else {}
        promise, kind = it.get("promise"), it.get("kind")
        tier = promise if isinstance(promise, str) and promise in TIERS else "middle"
        out.append(Ranking(promise={t: float(t == tier) for t in TIERS}, p_improve=_prob(it.get("p_improve"), 0.5),
                           p_repeat=_prob(it.get("p_repeat"), 0.0),
                           kind=kind if isinstance(kind, str) and kind in KINDS else "other",
                           cost=cost / max(n, 1), seconds=seconds / max(n, 1), raw={"parsed": bool(it)}))
    return out


def codex_config() -> dict:
    """Codex CLI version and the model/effort lines of ~/.codex/config.toml (nothing else is read)."""
    out = {}
    try:
        out["codex_version"] = subprocess.run(["codex", "--version"], capture_output=True, text=True,
                                              timeout=30).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        pass
    cfg = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")) / "config.toml"
    if cfg.exists():
        for line in cfg.read_text().splitlines():
            m = re.match(r'\s*(model|model_reasoning_effort)\s*=\s*"([^"]*)"', line)
            if m:
                out[m.group(1)] = m.group(2)
    return out


def _codex_env():
    keep = ("HOME", "PATH", "USER", "LOGNAME", "SHELL", "TMPDIR", "LANG", "LC_ALL", "CODEX_HOME", "TERM")
    return {k: v for k, v in os.environ.items() if k in keep}


def run_codex(prompt: str, timeout: float = 1200.0, trace_path=None) -> str:
    """`codex exec` in an empty scratch directory with a read-only sandbox and no secrets in its env."""
    with tempfile.TemporaryDirectory(prefix="codex_rank_") as tmp:
        out = Path(tmp) / "last_message.txt"
        work = Path(tmp) / "work"
        work.mkdir()
        cmd = ["codex", "exec", "--sandbox", "read-only", "--skip-git-repo-check", "--ephemeral",
               "--color", "never", "--json", "-C", str(work), "-o", str(out), "-"]
        proc = subprocess.run(cmd, input=prompt, capture_output=True, text=True, timeout=timeout, env=_codex_env())
        if trace_path is not None:
            import gzip
            Path(trace_path).parent.mkdir(parents=True, exist_ok=True)
            with gzip.open(trace_path, "wt") as f:
                json.dump({"cmd": cmd, "returncode": proc.returncode, "stdout": proc.stdout[-200000:],
                           "stderr": proc.stderr[-20000:]}, f)
        if proc.returncode != 0 and not out.exists():
            raise RuntimeError(f"codex exited {proc.returncode}: {proc.stderr[-500:]}")
        return out.read_text() if out.exists() else ""


class CodexRanker:
    """All ideas in one prompt to the Codex CLI (logged in through ChatGPT; no API spend tracked)."""
    name = "codex"
    all_at_once = True

    def __init__(self, runner=None, trace_dir=None):
        self.runner = runner or run_codex
        self.trace_dir = Path(trace_dir) if trace_dir else None

    def rank(self, problem, best_score, best_code, history, ideas) -> list:
        prompt = CODEX_SYSTEM + "\n\n" + ranking_prompt(problem, best_score, best_code, history, ideas)
        t0 = time.time()
        kwargs = {}
        if self.runner is run_codex and self.trace_dir is not None:
            kwargs["trace_path"] = self.trace_dir / "rank__codex.json.gz"
        text = self.runner(prompt, **kwargs)
        return parse_rankings(text, len(ideas), cost=0.0, seconds=time.time() - t0)


# -- CLI ---------------------------------------------------------------------------------------------

def _span(s: str):
    a, b = s.split(":")
    return int(a or 0), int(b)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("step", choices=["ideas", "rank", "implement", "evaluate", "table", "status", "provenance", "size", "fill"])
    ap.add_argument("out")
    ap.add_argument("--problem", default="problems/erdos_squares")
    ap.add_argument("--cap", type=float, default=40.0, help="hard Anthropic spend cap in dollars (whole folder)")
    ap.add_argument("--mock", action="store_true", help="canned Claude client, no network")
    ap.add_argument("--calls", type=int, default=8)
    ap.add_argument("--k", type=int, default=10)
    ap.add_argument("--n", type=int, help="number of ideas (in presentation order) to rank")
    ap.add_argument("--rankers", default="random,claude-haiku-4-5,claude-opus-5-5")
    ap.add_argument("--ideas", help="span of ideas in presentation order to implement, e.g. 0:3")
    ap.add_argument("--models", default=",".join(MODELS))
    ap.add_argument("--replicates", type=int, default=0, help="implement this many cells a second time")
    ap.add_argument("--replicate-pool", type=int, help="choose replicate cells among the first N ideas")
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--dry-run", action="store_true", help="fill: print the cost estimate and stop")
    ap.add_argument("--stop-at", type=float, help="soft limit: start no new cell once spend reaches this")
    ap.add_argument("--host", choices=["local", "modal"], default="local")
    ap.add_argument("--modal-cap", type=float, default=5.0)
    ap.add_argument("--eval-replicates", type=int, default=0)
    args = ap.parse_args()

    t = IdeaTable(args.out, problem=args.problem, cap=args.cap, mock=args.mock)
    if args.step == "ideas":
        t.generate_ideas(calls=args.calls, k=args.k)
    elif args.step == "rank":
        t.run_rankers([r for r in args.rankers.split(",") if r], args.n)
    elif args.step == "implement":
        models = [m for m in args.models.split(",") if m]
        cells = []
        if args.ideas:
            a, b = _span(args.ideas)
            cells += [c for c in t.main_cells(a, b) if c[1] in models]
        if args.replicates:
            cells += t.replicate_cells(args.replicate_pool or len(t.ideas_in_order()), args.replicates)
        # idea-major order, so a budget stop leaves few half-finished ideas
        t.implement(cells, workers=args.workers, stop_at=args.stop_at)
    elif args.step == "evaluate":
        t.evaluate_pending(host=args.host, workers=min(args.workers, 2), modal_cap=args.modal_cap,
                           eval_replicates=args.eval_replicates)
    elif args.step == "table":
        rows = t.build_table()
        print(f"[table] {len(rows)} rows -> {t.out / 'table.jsonl'}")
    elif args.step == "provenance":
        t.provenance()
    elif args.step == "fill":
        t.fill(replicates=args.replicates or 12, workers=args.workers, host=args.host, modal_cap=args.modal_cap,
               dry_run=args.dry_run)
    elif args.step == "size":
        print(json.dumps(t.size(replicates=args.replicates or 12), indent=2))
    print(json.dumps(t.status(), indent=2))


if __name__ == "__main__":
    main()
