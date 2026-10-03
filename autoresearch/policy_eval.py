"""Offline evaluation of rankers and triage policies against a counterfactual idea table.

Every idea in the table was implemented by every model, so any policy that decides, idea by
idea, which model (if any) implements it can be replayed without new API calls:

    python -m autoresearch.policy_eval experiments/idea-table-v1
    python -m autoresearch.policy_eval experiments/idea-table-v1 --extra-rankings my_ranker.json

A new ranker costs nothing to score: write its judgements of the ideas in rankings.json's
format and pass them with --extra-rankings:

    {"my_ranker": {"meta": {"cost": 0.0}, "ideas": {"i000": {"key": 0.8, "p_improve": 0.6}, ...}}}

`key` orders ideas (higher = more promising); `p_improve` is the probability the idea improves
the parent (used for the Brier score; defaults to `key`).

Uncertainty: bootstrap over ideas (resampled with replacement). In every draw, cells that were
implemented twice contribute one of their two replicates at random, so implementation noise
measured there enters the intervals; batches of six (one triage round) are re-formed at
random, and the random ranker draws fresh keys. Point estimates average the same randomness
over the observed ideas without resampling.
"""
import argparse
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from scipy.stats import rankdata, spearmanr

MODELS = ("claude-haiku-4-5", "claude-sonnet-5-5", "claude-opus-5-5")
SHORT = ("haiku", "sonnet", "opus")
TIER_TO_MODEL = (2, 1, 0)          # favourite -> opus, middle -> sonnet, long shot -> haiku (triage defaults)
TIER_NAMES = ("favourite", "middle", "long_shot")
BATCH = 6
SWAP = 0.15                        # triage.py --swap default
EXCLUDED_OUTCOMES = ("api_error", "pending_eval")


# -- data ------------------------------------------------------------------------------------------

class Data:
    def __init__(self, folder, extra_rankings=None):
        folder = Path(folder)
        self.folder = folder
        parent = json.loads((folder / "parent.json").read_text())
        self.parent_score, self.parent_hidden = parent["score"], parent["hidden_mean"]
        rankings = json.loads((folder / "rankings.json").read_text())
        order = [i for b in rankings["batches"] for i in b]
        rows = [json.loads(l) for l in (folder / "table.jsonl").read_text().splitlines() if l.strip()]
        cells = defaultdict(list)
        for r in rows:
            if r["outcome"] not in EXCLUDED_OUTCOMES:
                cells[(r["idea_id"], r["model"])].append(r)
        for v in cells.values():
            v.sort(key=lambda r: r["replicate"])
        self.rows = rows
        self.ids = [i for i in order if all(any(r["replicate"] == 0 for r in cells[(i, m)]) for m in MODELS)]
        self.excluded_ids = [i for i in order if i not in self.ids]
        self.n = len(self.ids)
        if self.n == 0:
            raise SystemExit("no idea has a finished cell for every model")
        # reps[i][m] = list of (improved, score, hidden, cost) over replicates
        self.reps = [[[(bool(r["improved"]), r["score"] if r["score"] is not None else math.nan,
                        r["hidden_mean"] if r["hidden_mean"] is not None else math.nan, float(r["cost"] or 0.0))
                       for r in cells[(i, m)]] for m in MODELS] for i in self.ids]
        self.cells = cells
        self.rankers = {}
        self.ranker_cost = {}
        sources = dict(rankings["rankers"])
        if extra_rankings:
            sources.update(extra_rankings)
        for name, entry in sources.items():
            ideas = entry["ideas"]
            key = np.array([float(ideas.get(i, {}).get("key", 0.5)) for i in self.ids])
            p = np.array([float(ideas.get(i, {}).get("p_improve", ideas.get(i, {}).get("key", 0.5))) for i in self.ids])
            self.rankers[name] = (key, np.clip(p, 0, 1))
            total = entry.get("meta", {}).get("cost")
            if total is None:
                total = sum(float(v.get("cost", 0.0)) for v in ideas.values())
            self.ranker_cost[name] = float(total) / max(len(ideas), 1)
        if "random" not in self.rankers:
            self.rankers["random"] = (np.zeros(self.n), np.zeros(self.n))
            self.ranker_cost["random"] = 0.0


class Draw:
    """One realisation: which ideas, which replicate per cell, how ideas fall into batches."""

    def __init__(self, data: Data, rng, resample: bool):
        n = data.n
        self.idx = rng.integers(0, n, n) if resample else np.arange(n)
        self.imp = np.zeros((n, 3), bool)
        self.score = np.full((n, 3), np.nan)
        self.hidden = np.full((n, 3), np.nan)
        self.cost = np.zeros((n, 3))
        self.single = np.zeros((n, 3), bool)      # cell has only one replicate
        for j, i in enumerate(self.idx):
            for m in range(3):
                reps = data.reps[i][m]
                imp, s, h, c = reps[rng.integers(len(reps))] if len(reps) > 1 else reps[0]
                self.imp[j, m], self.score[j, m], self.hidden[j, m], self.cost[j, m] = imp, s, h, c
                self.single[j, m] = len(reps) == 1
        self.perm = rng.permutation(n)
        self.batches = [self.perm[k:k + BATCH] for k in range(0, n, BATCH)]
        self.tie = rng.random(n)
        self.rand_key = rng.random(n)
        self.rand_p = rng.random(n)
        self.swap_u = rng.random(n)
        self.swap_alt = rng.integers(0, 2, n)
        self.flip_u = rng.random((n, 3))

    def keys(self, data: Data, ranker: str):
        if ranker == "random":
            return self.rand_key, self.rand_p
        key, p = data.rankers[ranker]
        return key[self.idx], p[self.idx]


# -- policies: each returns assign[j] in {-1 skip, 0 haiku, 1 sonnet, 2 opus} --------------------------

def tiers(draw, key, swap=False):
    assign = np.empty(len(key), int)
    for batch in draw.batches:
        order = sorted(batch, key=lambda j: (-key[j], draw.tie[j]))
        for pos, j in enumerate(order):
            planned = min(2, pos * 3 // len(order))
            tier = planned
            if swap and draw.swap_u[j] < SWAP:
                tier = [t for t in range(3) if t != planned][draw.swap_alt[j]]
            assign[j] = TIER_TO_MODEL[tier]
    return assign


def topk(draw, key, k):
    assign = np.full(len(key), -1)
    for batch in draw.batches:
        for j in sorted(batch, key=lambda j: (-key[j], draw.tie[j]))[:k]:
            assign[j] = 2
    return assign


def uniform(draw, m):
    return np.full(len(draw.idx), m)


def oracle(draw):
    """Unattainable reference: the cheapest model that succeeds on each idea, nothing when none does."""
    assign = np.full(len(draw.idx), -1)
    for j in range(len(draw.idx)):
        ok = np.where(draw.imp[j])[0]
        if len(ok):
            assign[j] = ok[np.argmin(draw.cost[j, ok])]
    return assign


def policy_specs(rankers):
    """(name, ranker or None, builder). Builders take (draw, key)."""
    specs = [(f"uniform:{SHORT[m]}", None, lambda d, k, m=m: uniform(d, m)) for m in range(3)]
    for r in rankers:
        specs.append((f"tiers:{r}", r, lambda d, k: tiers(d, k)))
        specs.append((f"tiers+swap:{r}", r, lambda d, k: tiers(d, k, swap=True)))
        for kk in (1, 2, 3):
            specs.append((f"top{kk}-opus:{r}", r, lambda d, k, kk=kk: topk(d, k, kk)))
    specs.append(("oracle-cheapest", None, lambda d, k: oracle(d)))
    return specs


def policy_metrics(data, draw, assign, ranker_cost_per_idea, imp=None):
    imp = draw.imp if imp is None else imp
    n = len(assign)
    j = np.where(assign >= 0)[0]
    m = assign[j]
    cost = float(draw.cost[j, m].sum() + ranker_cost_per_idea * n)
    found = np.zeros(n, bool)
    found[j] = imp[j, m]
    best_pub, best_hid = data.parent_score, data.parent_hidden
    for jj in draw.perm:                      # triage keeps the first strictly better program
        if found[jj] and draw.score[jj, assign[jj]] > best_pub:
            best_pub, best_hid = draw.score[jj, assign[jj]], draw.hidden[jj, assign[jj]]
    any_ok = imp.any(1)
    n_imp = int(found.sum())

    def recall(mask):
        return float((found & mask).sum() / mask.sum()) if mask.sum() else math.nan

    return {"cost": cost, "cells": int(len(j)), "improvements": n_imp,
            "improvements_per_dollar": n_imp / cost if cost > 0 else math.nan,
            "best_public": float(best_pub), "best_hidden": float(best_hid),
            "recall_any": recall(any_ok), "recall_haiku_success": recall(imp[:, 0]),
            "recall_sonnet_success": recall(imp[:, 1])}


def budget_metrics(data, draw, assign, ranker_cost_per_idea, budget):
    """Run batches in order until spend reaches `budget` (checked before each batch, as triage does)."""
    spent, best_pub, best_hid, exhausted, n_imp = 0.0, data.parent_score, data.parent_hidden, True, 0
    for batch in draw.batches:
        if spent >= budget:
            exhausted = False
            break
        spent += ranker_cost_per_idea * len(batch)
        for j in batch:
            a = assign[j]
            if a < 0:
                continue
            spent += draw.cost[j, a]
            if draw.imp[j, a]:
                n_imp += 1
                if draw.score[j, a] > best_pub:
                    best_pub, best_hid = draw.score[j, a], draw.hidden[j, a]
    return {"spent": spent, "best_public": float(best_pub), "best_hidden": float(best_hid),
            "improvements": n_imp, "pool_exhausted": exhausted}


# -- ranker quality --------------------------------------------------------------------------------

def auc(scores, labels):
    labels = np.asarray(labels, bool)
    pos, neg = labels.sum(), (~labels).sum()
    if pos == 0 or neg == 0:
        return math.nan
    ranks = rankdata(scores)
    return float((ranks[labels].sum() - pos * (pos + 1) / 2) / (pos * neg))


def ranker_metrics(draw, key, p, parent_score, imp=None):
    imp = draw.imp if imp is None else imp
    n = len(key)
    # graded outcome: mean public-score gain over the three models (a cell that did not improve counts as 0)
    gain = np.where(imp, np.nan_to_num(draw.score, nan=parent_score) - parent_score, 0.0).mean(1)
    rho = spearmanr(key, gain).statistic if np.ptp(key) > 0 and np.ptp(gain) > 0 else math.nan
    out = {"auc_pooled": auc(np.repeat(key, 3), imp.reshape(-1)),
           "auc_any": auc(key, imp.any(1)),
           "spearman_gain": float(rho),
           "brier_pooled": float(np.mean((p[:, None] - imp) ** 2))}
    for m in range(3):
        out[f"auc_{SHORT[m]}"] = auc(key, imp[:, m])
        out[f"brier_{SHORT[m]}"] = float(np.mean((p - imp[:, m]) ** 2))
    order = sorted(range(n), key=lambda j: (-key[j], draw.tie[j]))
    tier = np.empty(n, int)
    for pos, j in enumerate(order):
        tier[j] = min(2, pos * 3 // n)
    for t in range(3):
        mask = tier == t
        for m in range(3):
            out[f"success_{TIER_NAMES[t]}_{SHORT[m]}"] = float(imp[mask, m].mean()) if mask.any() else math.nan
        out[f"success_{TIER_NAMES[t]}_any"] = float(imp[mask].any(1).mean()) if mask.any() else math.nan
    return out


# -- implementation noise --------------------------------------------------------------------------

def replicate_pairs(data):
    pairs = []
    for (i, m), rows in data.cells.items():
        r0 = next((r for r in rows if r["replicate"] == 0), None)
        for r in rows:
            if r["replicate"] > 0 and r0 is not None:
                pairs.append({"idea_id": i, "model": m, "outcome": [r0["outcome"], r["outcome"]],
                              "improved": [r0["improved"], r["improved"]], "score": [r0["score"], r["score"]],
                              "hidden_mean": [r0["hidden_mean"], r["hidden_mean"]], "cost": [r0["cost"], r["cost"]]})
    return pairs


def noise_summary(data):
    pairs = replicate_pairs(data)
    out = {"pairs": len(pairs)}
    if pairs:
        out["improved_disagreement"] = float(np.mean([p["improved"][0] != p["improved"][1] for p in pairs]))
        out["outcome_disagreement"] = float(np.mean([p["outcome"][0] != p["outcome"][1] for p in pairs]))
        diffs = [abs(p["score"][0] - p["score"][1]) for p in pairs if None not in p["score"]]
        out["mean_abs_score_diff_valid_pairs"] = float(np.mean(diffs)) if diffs else None
        out["by_model"] = {SHORT[MODELS.index(m)]: {
            "pairs": len(ps), "improved_disagreement": float(np.mean([p["improved"][0] != p["improved"][1] for p in ps]))}
            for m in MODELS if (ps := [p for p in pairs if p["model"] == m])}
        out["detail"] = pairs
    reps = [r for r in data.rows if r.get("eval_repeat")]
    if reps:
        out["eval_repeats"] = len(reps)
        out["eval_outcome_disagreement"] = float(np.mean([r["eval_repeat"]["outcome"] != r["outcome"] for r in reps]))
        out["eval_max_abs_score_diff"] = float(max(abs((r["eval_repeat"]["score"] or 0) - (r["score"] or 0)) for r in reps))
    return out


def flipped_labels(draw, data, d, rates):
    """Sensitivity: resample single-replicate cells' improved label so two draws disagree at rate d,
    keeping each model's success rate (P(flip | 1) = d/2 / r, P(flip | 0) = d/2 / (1 - r))."""
    imp = draw.imp.copy()
    for m in range(3):
        r = rates[m]
        if r <= 0 or r >= 1:
            continue
        p1, p0 = min(1.0, d / 2 / r), min(1.0, d / 2 / (1 - r))
        col = imp[:, m]
        flip = draw.single[:, m] & np.where(col, draw.flip_u[:, m] < p1, draw.flip_u[:, m] < p0)
        imp[flip, m] = ~col[flip]
    return imp


# -- driver ----------------------------------------------------------------------------------------

def _summ(values):
    """Percentile interval over draws where the statistic is defined (e.g. AUC needs both classes)."""
    a = np.asarray(values, float)
    fin = a[~np.isnan(a)]
    if len(fin) == 0:
        return {"lo": None, "hi": None, "undefined_frac": 1.0}
    return {"lo": float(np.percentile(fin, 2.5)), "hi": float(np.percentile(fin, 97.5)),
            "undefined_frac": round(1 - len(fin) / len(a), 4)}


def _mean(values):
    a = np.asarray(values, float)
    a = a[~np.isnan(a)]
    return float(a.mean()) if len(a) else math.nan


def analyse(data: Data, n_boot=2000, n_point=500, seed=0, budgets=None, noise_sensitivity=True):
    rng = np.random.default_rng(seed)
    rankers = sorted(data.rankers, key=lambda r: (r != "random", r))
    specs = policy_specs(rankers)
    noise = noise_summary(data)
    rates = [float(np.mean([data.reps[i][m][0][0] for i in range(data.n)])) for m in range(3)]
    d = noise.get("improved_disagreement")

    def one(draw, budgets_):
        res = {"policy": {}, "ranker": {}, "budget": {}, "sens": {}}
        assigns = {}
        for name, r, build in specs:
            key = draw.keys(data, r)[0] if r else None
            a = build(draw, key)
            assigns[name] = a
            res["policy"][name] = policy_metrics(data, draw, a, data.ranker_cost.get(r, 0.0) if r else 0.0)
            for b in budgets_ or []:
                res["budget"].setdefault(name, {})[str(b)] = budget_metrics(
                    data, draw, a, data.ranker_cost.get(r, 0.0) if r else 0.0, b)
        for r in rankers:
            key, p = draw.keys(data, r)
            res["ranker"][r] = ranker_metrics(draw, key, p, data.parent_score)
        if noise_sensitivity and d is not None:
            imp_f = flipped_labels(draw, data, d, rates)
            for r in rankers:
                key, p = draw.keys(data, r)
                res["sens"][f"auc_pooled:{r}"] = auc(np.repeat(key, 3), imp_f.reshape(-1))
            for name, r, _ in specs:
                res["sens"][f"improvements:{name}"] = policy_metrics(
                    data, draw, assigns[name], 0.0, imp=imp_f)["improvements"]
        return res

    # budgets: fractions of the mean full-pool cost of random-ranked tiers (pre-registered rule)
    if budgets is None:
        probe = [one(Draw(data, rng, False), None)["policy"]["tiers:random"]["cost"] for _ in range(50)]
        full = float(np.mean(probe))
        budgets = [round(full * f, 4) for f in (0.25, 0.5)]
    point = [one(Draw(data, rng, False), budgets) for _ in range(n_point)]
    boot = [one(Draw(data, rng, True), budgets) for _ in range(n_boot)]

    def collect(runs, path):
        out = []
        for run in runs:
            x = run
            for p in path:
                x = x[p]
            out.append(x)
        return out

    def stat(path):
        pt = collect(point, path)
        bt = collect(boot, path)
        return dict(mean=_mean(pt), **_summ(bt))

    result = {"n_ideas": data.n, "excluded_ideas": data.excluded_ids, "parent_score": data.parent_score,
              "parent_hidden": data.parent_hidden, "n_boot": n_boot, "n_point": n_point, "seed": seed,
              "budgets": budgets, "ranker_cost_per_idea": data.ranker_cost, "noise": noise,
              "policies": {}, "rankers": {}, "budget": {}, "contrasts": {}, "sensitivity": {}}
    for name, _, _ in specs:
        result["policies"][name] = {k: stat(("policy", name, k)) for k in point[0]["policy"][name]}
        # $ per improvement as a ratio of means (finite even when some draws find nothing)
        c, n_imp = stat(("policy", name, "cost"))["mean"], stat(("policy", name, "improvements"))["mean"]
        result["policies"][name]["dollars_per_improvement"] = c / n_imp if n_imp > 0 else None
        result["budget"][name] = {str(b): {k: stat(("budget", name, str(b), k))
                                           for k in ("spent", "best_public", "best_hidden", "improvements",
                                                     "pool_exhausted")} for b in budgets}
    for r in rankers:
        result["rankers"][r] = {k: stat(("ranker", r, k)) for k in point[0]["ranker"][r]}
    if point[0]["sens"]:
        result["sensitivity"] = {k: stat(("sens", k)) for k in point[0]["sens"]}
        result["sensitivity"]["disagreement_rate_used"] = d
        result["sensitivity"]["success_rates_used"] = dict(zip(SHORT, rates))

    def contrast(a, b, metric):
        pt = [x["policy"][a][metric] - x["policy"][b][metric] for x in point]
        bt = [x["policy"][a][metric] - x["policy"][b][metric] for x in boot]
        return dict(mean=_mean(pt), **_summ(bt))

    for r in rankers:
        if r == "random":
            continue
        for metric in ("improvements", "best_public", "best_hidden", "cost", "recall_any"):
            result["contrasts"][f"tiers:{r} - tiers:random | {metric}"] = contrast(f"tiers:{r}", "tiers:random", metric)
            result["contrasts"][f"tiers:{r} - uniform:opus | {metric}"] = contrast(f"tiers:{r}", "uniform:opus", metric)
        for kk in (1, 2, 3):
            for metric in ("improvements", "best_public", "best_hidden"):
                result["contrasts"][f"top{kk}-opus:{r} - top{kk}-opus:random | {metric}"] = contrast(
                    f"top{kk}-opus:{r}", f"top{kk}-opus:random", metric)
    return result


# -- report ----------------------------------------------------------------------------------------

def _f(s, digits=3):
    if s is None or s.get("mean") is None or (isinstance(s["mean"], float) and math.isnan(s["mean"])):
        return "-"
    if s.get("lo") is None:
        return f"{s['mean']:.{digits}f}"
    return f"{s['mean']:.{digits}f} [{s['lo']:.{digits}f}, {s['hi']:.{digits}f}]"


def data_summary(data):
    rows = [r for r in data.rows if r["idea_id"] in data.ids and r["replicate"] == 0]
    out = {}
    for m in MODELS:
        rs = [r for r in rows if r["model"] == m]
        out[m] = {"cells": len(rs), "outcomes": dict(Counter(r["outcome"] for r in rs)),
                  "success_rate": float(np.mean([r["improved"] for r in rs])) if rs else None,
                  "mean_cost": float(np.mean([r["cost"] or 0 for r in rs])) if rs else None,
                  "mean_output_tokens": float(np.mean([r["output_tokens"] or 0 for r in rs])) if rs else None,
                  "mean_llm_seconds": float(np.mean([r["llm_seconds"] or 0 for r in rs])) if rs else None,
                  "refusals": sum(bool(r.get("refused")) for r in rs),
                  "max_score": max((r["score"] for r in rs if r["valid"]), default=None)}
    any_ok = [any(data.reps[i][m][0][0] for m in range(3)) for i in range(data.n)]
    out["ideas_improved_by_any_model"] = int(sum(any_ok))
    return out


def report(result, summary) -> str:
    L = [f"# Offline policy evaluation ({result['n_ideas']} ideas, parent score {result['parent_score']:.4f}, "
         f"parent hidden {result['parent_hidden']:.4f})", "",
         f"Bootstrap over ideas: {result['n_boot']} resamples; point estimates average {result['n_point']} "
         "draws of replicate choice, batching and random keys. Intervals are 2.5-97.5 percentiles.", ""]
    if result["excluded_ideas"]:
        L += [f"Excluded (a model's cell missing): {', '.join(result['excluded_ideas'])}", ""]
    L += ["## Cells (replicate 0)", "", "| model | cells | success rate | mean $ | mean output tokens | mean LLM s | refusals | outcomes |",
          "|---|---|---|---|---|---|---|---|"]
    for m in MODELS:
        s = summary[m]
        L.append(f"| {m} | {s['cells']} | {s['success_rate']:.3f} | {s['mean_cost']:.4f} | {s['mean_output_tokens']:.0f} | "
                 f"{s['mean_llm_seconds']:.0f} | {s['refusals']} | {s['outcomes']} |")
    L += ["", f"Ideas improved by at least one model: {summary['ideas_improved_by_any_model']} of {result['n_ideas']}.", ""]

    L += ["## Rankers", "", "| ranker | $/idea | AUC pooled | AUC haiku | AUC sonnet | AUC opus | AUC any | Spearman gain | Brier pooled |",
          "|---|---|---|---|---|---|---|---|---|"]
    for r, s in result["rankers"].items():
        L.append(f"| {r} | {result['ranker_cost_per_idea'].get(r, 0):.5f} | {_f(s['auc_pooled'])} | {_f(s['auc_haiku'])} | "
                 f"{_f(s['auc_sonnet'])} | {_f(s['auc_opus'])} | {_f(s["auc_any"])} | {_f(s["spearman_gain"])} | {_f(s["brier_pooled"])} |")
    L += ["", "Success rate by ranker tier (global thirds of the ranker's key), per implementing model:", "",
          "| ranker | tier | haiku | sonnet | opus | any |", "|---|---|---|---|---|---|"]
    for r, s in result["rankers"].items():
        for t in TIER_NAMES:
            L.append(f"| {r} | {t} | {_f(s[f'success_{t}_haiku'], 2)} | {_f(s[f'success_{t}_sonnet'], 2)} | "
                     f"{_f(s[f'success_{t}_opus'], 2)} | {_f(s[f'success_{t}_any'], 2)} |")

    L += ["", "## Policies over the whole pool", "",
          "| policy | $ | improvements | impr. per $ | $ per impr. | best public | best hidden | recall (any success) | recall (haiku successes) |",
          "|---|---|---|---|---|---|---|---|---|"]
    for name, s in result["policies"].items():
        dpi = s["dollars_per_improvement"]
        L.append(f"| {name} | {_f(s['cost'], 2)} | {_f(s['improvements'], 1)} | {_f(s['improvements_per_dollar'], 2)} | "
                 f"{'-' if dpi is None else f'{dpi:.3f}'} | {_f(s['best_public'], 4)} | {_f(s['best_hidden'], 4)} | "
                 f"{_f(s['recall_any'], 2)} | {_f(s['recall_haiku_success'], 2)} |")
    L += ["", "## Paired contrasts", "", "| contrast | difference |", "|---|---|"]
    for k, s in result["contrasts"].items():
        L.append(f"| {k} | {_f(s, 4)} |")
    L += ["", "## Budget-matched (batches of six until the budget is reached)", ""]
    for b in result["budgets"]:
        L += [f"Budget ${b:.2f}:", "", "| policy | spent | improvements | best public | best hidden | pool exhausted |",
              "|---|---|---|---|---|---|"]
        for name, per in result["budget"].items():
            s = per[str(b)]
            L.append(f"| {name} | {_f(s['spent'], 2)} | {_f(s['improvements'], 1)} | {_f(s['best_public'], 4)} | "
                     f"{_f(s['best_hidden'], 4)} | {_f(s['pool_exhausted'], 2)} |")
        L.append("")
    n = result["noise"]
    L += ["## Implementation noise", ""]
    if n["pairs"]:
        L += [f"{n['pairs']} cells implemented twice. Improved/not disagreement {n['improved_disagreement']:.2f}; "
              f"outcome disagreement {n['outcome_disagreement']:.2f}. By model: "
              + ", ".join(f"{k} {v['improved_disagreement']:.2f} ({v['pairs']} pairs)" for k, v in n["by_model"].items()), ""]
    if n.get("eval_repeats"):
        L += [f"{n['eval_repeats']} programs re-evaluated: outcome disagreement {n['eval_outcome_disagreement']:.2f}, "
              f"max |score difference| {n['eval_max_abs_score_diff']:.2e}.", ""]
    if result["sensitivity"]:
        s = result["sensitivity"]
        L += [f"Sensitivity (single-replicate labels resampled at disagreement rate {s['disagreement_rate_used']:.2f}):", "",
              "| quantity | value |", "|---|---|"]
        for k, v in s.items():
            if isinstance(v, dict) and "mean" in v:
                L.append(f"| {k} | {_f(v)} |")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("folder")
    ap.add_argument("--extra-rankings", help="JSON file: {name: {meta: {cost}, ideas: {id: {key, p_improve}}}}")
    ap.add_argument("--boot", type=int, default=2000)
    ap.add_argument("--point", type=int, default=500)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", help="write analysis.json and analysis.md here (default: the folder)")
    args = ap.parse_args()
    extra = json.loads(Path(args.extra_rankings).read_text()) if args.extra_rankings else None
    data = Data(args.folder, extra)
    result = analyse(data, n_boot=args.boot, n_point=args.point, seed=args.seed)
    result["cells"] = data_summary(data)
    out = Path(args.out or args.folder)
    out.mkdir(parents=True, exist_ok=True)
    (out / "analysis.json").write_text(json.dumps(result, indent=2, default=float))
    md = report(result, result["cells"])
    (out / "analysis.md").write_text(md)
    print(md)


if __name__ == "__main__":
    main()
