"""Triage research loop: a fast ranker (Jev) decides which model implements each idea.

    python -m autoresearch.triage problems/erdos_squares --rounds 10
    python -m autoresearch.triage problems/erdos_squares --ranker random          # control: same model mix, random assignment
    python -m autoresearch.triage problems/erdos_squares --uniform claude-opus-5-5 # control: every idea on one model

Each round:
  1. Claude proposes K one-sentence ideas for improving the current best program.
  2. The ranker judges every idea (promise, P(improve), P(repeat of a failure), kind).
  3. Ideas are sorted and split into thirds: favourites -> top model, middle -> middle model,
     long shots -> cheap model. A fraction of assignments is swapped at random so we can tell
     a bad idea from a weak implementer.
  4. Every idea is implemented and scored by the integrity gate. Nothing is skipped.
  5. Promotion: an improvement found by a cheaper model is refined by the top model.
  6. Everything is logged to log.jsonl; notebook.md is a readable research log.
"""
import argparse
import json
import random
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from .claude import (IDEA_SYSTEM, IDEA_USER, IMPLEMENT_SYSTEM, IMPLEMENT_USER, REFINE_USER, Claude,
                     parse_code, parse_ideas)
from .env import load_env, require
from .gate import evaluate

TIER_NAMES = ("favourite", "middle", "long_shot")


class Run:
    def __init__(self, args):
        self.args = args
        self.problem_dir = Path(args.problem).resolve()
        self.problem = (self.problem_dir / "problem.md").read_text()
        self.out = Path(args.out or f"results/triage_{self.problem_dir.name}_{args.ranker}_{time.strftime('%Y%m%d_%H%M%S')}")
        self.out.mkdir(parents=True, exist_ok=True)
        self.log_path = self.out / "log.jsonl"
        self.rng = random.Random(args.seed)
        self.claude = Claude()
        self.tiers = args.tiers.split(",")
        self.efforts = args.efforts.split(",")
        self.spent = 0.0
        self.history = []
        self.ranker = self._make_ranker()

    def _make_ranker(self):
        from . import rankers
        if self.args.ranker == "jev":
            require("TYPESAFE_API_KEY", "the Jev ranker needs it")
            return rankers.JevRanker()
        if self.args.ranker == "claude":
            return rankers.ClaudeRanker(self.claude, model=self.args.ranker_model)
        return rankers.RandomRanker(seed=self.args.seed)

    def log(self, event: dict):
        event["time"] = time.time()
        event["spent_total"] = round(self.spent, 6)
        with open(self.log_path, "a") as f:
            f.write(json.dumps(event, default=str) + "\n")

    def score_program(self, code: str, tag: str):
        d = self.out / "programs" / tag
        d.mkdir(parents=True, exist_ok=True)
        prog = d / "program.py"
        prog.write_text(code)
        t0 = time.time()
        metrics = evaluate(self.problem_dir, str(prog), str(d / "results"))
        correct = json.loads((d / "results" / "correct.json").read_text())
        return metrics, correct, time.time() - t0

    # -- one implementation (or refinement) of one idea ----------------------------------------
    def implement(self, idea, tier, model, effort, parent, tag, refine_of=None):
        if refine_of is None:
            user = IMPLEMENT_USER.format(score=parent["score"], code=parent["code"], feedback=parent["feedback"], idea=idea)
        else:
            user = REFINE_USER.format(idea=idea, score=refine_of["score"], prev=parent["score"],
                                      code=refine_of["code"], feedback=refine_of["feedback"])
        rec = {"tag": tag, "idea": idea, "tier": tier, "model": model}
        try:
            call = self.claude.call(model, IMPLEMENT_SYSTEM.format(problem=self.problem), user,
                                    max_tokens=self.args.max_tokens, effort=effort)
        except Exception as e:  # API errors must not kill the run
            rec.update(outcome="api_error", detail=f"{type(e).__name__}: {e}", cost=0.0)
            return rec
        rec.update(cost=call.cost, input_tokens=call.input_tokens, output_tokens=call.output_tokens,
                   llm_seconds=round(call.seconds, 2), served_by=call.served_by)
        if call.refused:
            rec.update(outcome="refused")
            return rec
        code = parse_code(call.text)
        if not code:
            rec.update(outcome="no_code")
            return rec
        metrics, correct, eval_s = self.score_program(code, tag)
        score = metrics["combined_score"]
        if metrics["private"].get("integrity_rejections") or metrics["private"].get("integrity") == "static":
            outcome = "rejected"
        elif not correct["correct"]:
            outcome = "invalid"
        elif score > parent["score"] + 1e-9:
            outcome = "improved"
        else:
            outcome = "not_better"
        rec.update(outcome=outcome, score=score, delta=score - parent["score"], eval_seconds=round(eval_s, 2),
                   code=code, feedback=metrics["text_feedback"])
        return rec

    # -- the loop ------------------------------------------------------------------------------
    def run(self):
        a = self.args
        init = (self.problem_dir / "initial.py").read_text()
        metrics, _, _ = self.score_program(init, "initial")
        best = {"score": metrics["combined_score"], "code": init, "feedback": metrics["text_feedback"], "tag": "initial"}
        self.log({"event": "start", "problem": self.problem_dir.name, "ranker": a.ranker, "tiers": self.tiers,
                  "uniform": a.uniform, "ideas_per_round": a.ideas, "swap_rate": a.swap, "seed": a.seed,
                  "initial_score": best["score"]})
        print(f"[start] {self.problem_dir.name}: initial score {best['score']:.6f}  ->  {self.out}")

        for rnd in range(1, a.rounds + 1):
            if a.budget and self.spent >= a.budget:
                print(f"[stop] budget ${a.budget:.2f} reached")
                break
            # 1. propose
            hist = "\n".join(f"- {h['idea']} -> {h['outcome']}" for h in self.history[-30:]) or "(none yet)"
            prop = self.claude.call(a.idea_model, IDEA_SYSTEM.format(problem=self.problem),
                                    IDEA_USER.format(score=best["score"], code=best["code"], feedback=best["feedback"],
                                                     history=hist, k=a.ideas),
                                    max_tokens=16000, effort=a.idea_effort)
            self.spent += prop.cost
            ideas = parse_ideas(prop.text, a.ideas)
            self.log({"event": "propose", "round": rnd, "model": a.idea_model, "cost": prop.cost, "ideas": ideas,
                      "refused": prop.refused})
            if not ideas:
                print(f"[round {rnd}] no ideas parsed; skipping")
                continue

            # 2. rank
            t0 = time.time()
            ranks = self.ranker.rank(self.problem, best["score"], best["code"], self.history, ideas)
            rank_cost = sum(r.cost for r in ranks)
            self.spent += rank_cost
            self.log({"event": "rank", "round": rnd, "ranker": self.ranker.name, "cost": rank_cost,
                      "seconds": round(time.time() - t0, 3), "rankings": [r.to_dict() for r in ranks]})

            # 3. assign tiers (sorted thirds), with random swaps
            order = sorted(range(len(ideas)), key=lambda i: -ranks[i].key)
            jobs = []
            for pos, i in enumerate(order):
                planned = min(2, pos * 3 // len(ideas))
                tier, swapped = planned, False
                if not a.uniform and self.rng.random() < a.swap:
                    tier = self.rng.choice([t for t in range(3) if t != planned])
                    swapped = True
                model = a.uniform or self.tiers[tier]
                effort = None if a.uniform else self.efforts[tier]
                jobs.append(dict(i=i, planned=planned, tier=tier, swapped=swapped, model=model,
                                 effort=effort or a.uniform_effort))

            # 4. implement and score everything in parallel
            parent = dict(best)
            with ThreadPoolExecutor(max_workers=a.workers) as pool:
                futs = [pool.submit(self.implement, ideas[j["i"]], TIER_NAMES[j["tier"]], j["model"], j["effort"],
                                    parent, f"r{rnd:02d}_i{j['i']}") for j in jobs]
                results = [f.result() for f in futs]
            round_best = None
            for j, rec in zip(jobs, results):
                self.spent += rec.get("cost", 0.0)
                rank = ranks[j["i"]]
                rec.update(event="result", round=rnd, idea_index=j["i"], planned_tier=TIER_NAMES[j["planned"]],
                           swapped=j["swapped"], ranker_key=rank.key, p_improve=rank.p_improve,
                           p_repeat=rank.p_repeat, kind=rank.kind)
                self.log({k: v for k, v in rec.items() if k != "code"})
                self.history.append({"idea": rec["idea"], "model": rec["model"], "outcome": rec["outcome"],
                                     "score": rec.get("score")})
                if rec["outcome"] == "improved" and (round_best is None or rec["score"] > round_best["score"]):
                    round_best = rec

            # 5. promotion: a cheaper model found an improvement -> the top model refines it
            if round_best is not None and round_best["model"] != self.tiers[0] and not a.no_promotion and not a.uniform:
                ref = self.implement(round_best["idea"], "promotion", self.tiers[0], self.efforts[0], parent,
                                     f"r{rnd:02d}_promote", refine_of=round_best)
                self.spent += ref.get("cost", 0.0)
                ref.update(event="promotion", round=rnd, promoted_from=round_best["model"])
                self.log({k: v for k, v in ref.items() if k != "code"})
                if ref.get("outcome") == "improved" and ref["score"] > round_best["score"]:
                    round_best = ref

            if round_best is not None:
                best = {"score": round_best["score"], "code": round_best["code"],
                        "feedback": round_best["feedback"], "tag": round_best["tag"]}
                (self.out / "best_program.py").write_text(best["code"])
            outcomes = ", ".join(f"{r['model'].replace('claude-', '')}:{r['outcome']}" for r in results)
            print(f"[round {rnd}] best {best['score']:.6f}  spent ${self.spent:.2f}  |  {outcomes}")
            self.log({"event": "round_end", "round": rnd, "best_score": best["score"], "best_tag": best["tag"]})

        self.log({"event": "end", "best_score": best["score"], "best_tag": best["tag"]})
        from .analyze import summarize, write_notebook
        summary = summarize(self.log_path)
        (self.out / "summary.json").write_text(json.dumps(summary, indent=2))
        write_notebook(self.log_path, self.out / "notebook.md")
        print(json.dumps(summary, indent=2))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("problem")
    ap.add_argument("--rounds", type=int, default=10)
    ap.add_argument("--ideas", type=int, default=6, help="ideas proposed (and implemented) per round")
    ap.add_argument("--ranker", choices=["jev", "claude", "random"], default="jev")
    ap.add_argument("--ranker-model", default="claude-haiku-4-5", help="model for --ranker claude")
    ap.add_argument("--tiers", default="claude-opus-5-5,claude-sonnet-5-5,claude-haiku-4-5",
                    help="models for favourite,middle,long_shot")
    ap.add_argument("--efforts", default="high,high,", help="effort per tier (empty = model default)")
    ap.add_argument("--uniform", default=None, help="control: implement every idea with this one model")
    ap.add_argument("--uniform-effort", default="high")
    ap.add_argument("--idea-model", default="claude-opus-5-5")
    ap.add_argument("--idea-effort", default="medium")
    ap.add_argument("--swap", type=float, default=0.15, help="fraction of tier assignments randomised")
    ap.add_argument("--no-promotion", action="store_true")
    ap.add_argument("--budget", type=float, default=None, help="stop after this many dollars")
    ap.add_argument("--max-tokens", type=int, default=32000)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    load_env()
    require("ANTHROPIC_API_KEY", "Claude proposes and implements ideas")
    args.efforts = args.efforts if args.efforts.count(",") == 2 else "high,high,"
    Run(args).run()


if __name__ == "__main__":
    main()
