"""One strategy on one target and seed: the evolutionary template every strategy fills.

initialize builds INIT candidates from the best known solution and its neighbours; every candidate is relaxed; the
population is the reference plus the best distinct basins. For GENERATIONS generations, vary makes CHILDREN candidates
from the population, they are relaxed, and the best POPULATION distinct basins of parents and children survive.
Finally the best POLISH basins are polished: a relaxed value can sit 1e-3 above the polished optimum of its basin, so
a basin that ranked 4th can polish below the reference. Every strategy gets this same budget.

The result reports the gap of the best polished basin to the best known value (negative: a candidate record, to be
verified), the runner-up gap (the best other basin: how near the strategy came) and the best initial gap.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np


@dataclass
class Budget:
    init: int = 512
    children: int = 128
    generations: int = 12
    population: int = 32
    polish: int = 16


def distinct(xs, values, size, same):
    """The best `size` candidates from distinct basins (values more than `same` apart), best first."""
    keep, seen = [], []
    for i in np.argsort(values):
        if all(abs(values[i]-s) > same for s in seen):
            keep.append((xs[i], float(values[i])))
            seen.append(values[i])
        if len(keep) == size:
            break
    return keep


def neighbours_for(domain, n, references=(), memory=None):
    """Best solutions offered to a strategy for nearby sizes (n +- 1, n +- 2) and any reference sizes: the domain's best
    known solution where it has one, or what this workspace has found (memory: {m: (x, value)}) if that is better."""
    out = {}
    for m in (n-2, n-1, n+1, n+2, *references):
        x, value = None, None
        try:
            x, value = domain.reference(m)
        except (KeyError, ValueError):
            pass
        if memory and m in memory and (x is None or memory[m][1] < value):
            x, value = memory[m]
        if x is not None:
            out[m] = (np.asarray(x), float(value))
    return out


def run(domain, backend, code, n, seed, budget=Budget(), neighbours=None, progress=None):
    """Result dict for one run; progress(generation, best) is called after every generation."""
    record, reference = domain.reference(n)
    neighbours = neighbours_for(domain, n) if neighbours is None else neighbours
    dropped, failed, evaluations = 0, 0, 0

    def relaxed(made):
        nonlocal dropped, failed, evaluations
        dropped += made.get("dropped", 0)
        out = backend.relax(made["x"], made["values"])
        good = [r for r in out if "error" not in r]
        failed += len(out)-len(good)
        evaluations += sum(r["used"] for r in good)
        return [np.asarray(r["x"]) for r in good], np.array([r["value"] for r in good])

    made = backend.step(code, "initialize", {"record": None if record is None else (record, reference), "neighbours": neighbours},
                        budget.init, seed, n)
    if "error" in made:
        return {"n": n, "seed": seed, "error": "initialize: "+made["error"][-600:]}
    xs, values = relaxed(made)
    if not len(values):
        return {"n": n, "seed": seed, "error": "initialize: no candidate relaxed"}
    initial_gap = float(values.min())-domain.best_known(n)
    if record is None:  # no known solution for this size: the population is built from the candidates alone
        population = distinct(xs, values, budget.population, domain.same)
    else:
        population = [(record, reference)]+[p for p in distinct(xs, values, budget.population, domain.same)
                                           if abs(p[1]-reference) > domain.same][:budget.population-1]
    history = []
    for g in range(budget.generations):
        made = backend.step(code, "vary", {"parents": population}, budget.children, seed*1000+g, n)
        if "error" in made:
            return {"n": n, "seed": seed, "error": f"vary (generation {g+1}): "+made["error"][-600:]}
        xs, values = relaxed(made)
        merged = population+list(zip(xs, values.tolist()))
        population = distinct([p[0] for p in merged], np.array([p[1] for p in merged]), budget.population, domain.same)
        history.append(population[0][1])
        if progress:
            progress(g+1, population[0][1])
    polished = sorted(backend.polish(population[:budget.polish]), key=lambda p: p[1])
    best_known = domain.best_known(n)
    others = [p for p in polished if p[1] > best_known+1e-7]  # basins other than the best known one
    best = polished[0]
    return {"n": n, "seed": seed, "best_known": best_known, "polished": best[1], "gap": best[1]-best_known,
            "record": bool(best[1] < best_known-1e-9), "runner_up_gap": others[0][1]-best_known if others else None,
            "initial_gap": initial_gap, "generations": history, "dropped": dropped, "failed": failed,
            "evaluations": evaluations, "budget": asdict(budget),
            "best": {"x": np.asarray(best[0]).tolist(), "value": best[1]},
            "runner_up": {"x": np.asarray(others[0][0]).tolist(), "value": others[0][1]} if others else None}
