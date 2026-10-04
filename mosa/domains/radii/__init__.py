"""Circles in the unit square maximizing the sum of their radii: the benchmark AlphaEvolve, OpenEvolve and ShinkaEvolve
report (n = 26).

A candidate is (x, value): x an (n, 3) array of [cx, cy, r], value = -(sum of radii), so smaller is better as for every
problem in Mosa. Feasibility is exact: every circle inside the square and no two overlapping, at zero tolerance.
Published values for n = 26: AlphaEvolve 2.63586276 (zero tolerance); ShinkaEvolve 2.63598283 (overlaps up to 1e-7
allowed); ThetaEvolve 2.63598308 (1e-6). The best known value used here is the highest of these, so a record must beat
every published value while satisfying a stricter check than any of them.
"""
from __future__ import annotations

import math

import numpy as np
from numba import njit
from scipy.optimize import minimize

from ...domain import Domain

KNOWN = {26: -2.63598308}
STRENGTHS = (10., 100., 1e3, 1e4, 1e5, 1e6)


@njit(cache=True)
def penalty(z):
    """Squared violations (overlaps, walls, negative radii) and their gradient; z = [cx, cy, r]*n."""
    n = len(z)//3
    g = np.zeros_like(z)
    e = 0.
    for i in range(n):
        x, y, r = z[3*i], z[3*i+1], z[3*i+2]
        for k in range(2):  # coordinate k against the walls at 0 and 1
            c = z[3*i+k]
            low, high = r-c, c+r-1.
            if low > 0:
                e += low*low
                g[3*i+k] -= 2*low
                g[3*i+2] += 2*low
            if high > 0:
                e += high*high
                g[3*i+k] += 2*high
                g[3*i+2] += 2*high
        if r < 0:
            e += r*r
            g[3*i+2] += 2*r
        for j in range(i):
            dx, dy = x-z[3*j], y-z[3*j+1]
            d = math.sqrt(dx*dx+dy*dy)
            o = r+z[3*j+2]-d
            if o > 0:
                e += o*o
                if d > 0:
                    g[3*i] -= 2*o*dx/d
                    g[3*i+1] -= 2*o*dy/d
                    g[3*j] += 2*o*dx/d
                    g[3*j+1] += 2*o*dy/d
                g[3*i+2] += 2*o
                g[3*j+2] += 2*o
    return e, g


def repair(x, margin=1e-12):
    """Shrink radii until the packing is exactly feasible: inside the square and no overlaps."""
    x = np.asarray(x, dtype=float).copy()
    c, r = np.clip(x[:, :2], 0., 1.), x[:, 2]
    r = np.maximum(0., np.minimum.reduce([r, c[:, 0], 1-c[:, 0], c[:, 1], 1-c[:, 1]])-margin)
    d = np.sqrt(((c[:, None]-c[None])**2).sum(-1))
    for _ in range(200):
        over = np.triu((r[:, None]+r[None]) > d-margin, 1)
        if not over.any():
            break
        for i, j in zip(*np.nonzero(over)):
            if r[i]+r[j] > d[i, j]-margin:
                f = max(0., d[i, j]-margin)/(r[i]+r[j]) if r[i]+r[j] > 0 else 0.
                r[i] *= f
                r[j] *= f
    x[:, :2], x[:, 2] = c, r
    return x


def feasible(x, tolerance=0.):
    c, r = x[:, :2], x[:, 2]
    d = np.sqrt(((c[:, None]-c[None])**2).sum(-1))+np.eye(len(x))*9.
    return bool((r >= 0).all() and (c-r[:, None] >= -tolerance).all() and (c+r[:, None] <= 1+tolerance).all()
                and ((r[:, None]+r[None]) <= d+tolerance).all())


class CircleRadii(Domain):
    name = "circle-radii"
    family = "circles in a square, sum of radii"
    title = "Circles in a square, maximizing the sum of radii"
    problem = ("Place n circles of any sizes inside the unit square without overlap so that the sum of their radii is as large "
               "as possible. The objective is minus the sum of radii (smaller is better).")
    evidence = """What is known about this landscape:
- n = 26 is the benchmark of AlphaEvolve (2.63586276), OpenEvolve and ShinkaEvolve (2.63598283, with overlaps up to 1e-7
  tolerated); the human best before them was 2.634. Here feasibility is checked at zero tolerance.
- Optimal packings mix circle sizes: large circles in the interior, smaller ones filling the corners and edges, with
  many tangencies; small changes of the contact graph change the sum by 1e-4 to 1e-3.
- The landscape has many local optima with sums within 1e-3 of each other; a good start (e.g. a hexagonal or
  ring-and-core layout with sizes graded towards the walls) matters more than local refinement."""
    api = '''def initialize(record, neighbours, rng, count):
    """record is None (no packing is stored). neighbours: dict {m: (x, value)}, the best packings found so far in this
    workspace for nearby n (possibly empty). The global n is the number of circles. Return up to `count` candidates
    (x, value): x an (n, 3) array of [cx, cy, r] (centre in the unit square, radius), value = -(sum of radii).
    Overlaps and circles sticking out are fine: each candidate is relaxed to a feasible packing."""

def vary(parents, rng, count):
    """parents: list of (x, value), the current population of distinct relaxed packings for this n, best first.
    Return `count` new candidates (x of shape (n, 3), value) derived from the population; overlaps are fine."""'''
    same = 1e-9

    def targets(self):
        return list(range(5, 41))

    def reference(self, n):
        return None, KNOWN.get(n)

    def best_known(self, n):
        return KNOWN.get(n)

    def info(self, n):
        return {"best_known": self.best_known(n), "source": "ShinkaEvolve / ThetaEvolve (n = 26)" if n in KNOWN else "no published value"}

    def random(self, n, rng):
        x = np.c_[rng.uniform(.1, .9, (n, 2)), np.full(n, .5/math.sqrt(n))]
        return x, -float(x[:, 2].sum())

    def validate(self, x, value, n):
        x = np.asarray(x, dtype=float)
        if x.shape != (n, 3) or not np.isfinite(x).all() or np.abs(x).max() > 10:
            raise ValueError(f"a candidate has shape {x.shape} (expected ({n}, 3)) or non-finite or out-of-range values")
        return x

    def relax(self, x, value=None):
        z = np.asarray(x, dtype=float).ravel().copy()
        z[2::3] = np.abs(z[2::3])
        used = 0
        sign = np.zeros_like(z)
        sign[2::3] = -1.
        for strength in STRENGTHS:
            def fun(w, s=strength):
                e, g = penalty(w)
                return float(sign @ w+s*e), sign+s*g
            result = minimize(fun, z, jac=True, method="L-BFGS-B", options={"maxiter": 2000, "gtol": 1e-12, "ftol": 1e-15})
            z, used = result.x, used+result.nfev
        x = repair(z.reshape(-1, 3))
        return x, -float(x[:, 2].sum()), used

    def polish(self, x, value=None):
        """SLSQP on the exact constraints (walls; pairs within reach of each other); kept if feasible after repair and better."""
        x = np.asarray(x, dtype=float)
        n = len(x)
        d = np.sqrt(((x[:, None, :2]-x[None, :, :2])**2).sum(-1))
        i, j = np.nonzero(np.triu(d < x[:, 2][:, None]+x[:, 2][None]+.05, 1))

        def cons(w):
            v = w.reshape(n, 3)
            c, r = v[:, :2], v[:, 2]
            return np.r_[((c[i]-c[j])**2).sum(1)-(r[i]+r[j])**2, c[:, 0]-r, 1-c[:, 0]-r, c[:, 1]-r, 1-c[:, 1]-r, r]

        def jac(w):
            v = w.reshape(n, 3)
            c, r = v[:, :2], v[:, 2]
            J = np.zeros((len(i)+5*n, 3*n))
            k = np.arange(len(i))
            diff = c[i]-c[j]
            for a in range(2):
                J[k, 3*i+a] = 2*diff[:, a]
                J[k, 3*j+a] = -2*diff[:, a]
            J[k, 3*i+2] = -2*(r[i]+r[j])
            J[k, 3*j+2] = -2*(r[i]+r[j])
            m = np.arange(n)
            base = len(i)
            J[base+m, 3*m], J[base+m, 3*m+2] = 1, -1
            J[base+n+m, 3*m], J[base+n+m, 3*m+2] = -1, -1
            J[base+2*n+m, 3*m+1], J[base+2*n+m, 3*m+2] = 1, -1
            J[base+3*n+m, 3*m+1], J[base+3*n+m, 3*m+2] = -1, -1
            J[base+4*n+m, 3*m+2] = 1
            return J
        sign = np.zeros(3*n)
        sign[2::3] = -1.
        result = minimize(lambda w: float(sign @ w), x.ravel(), jac=lambda w: sign, method="SLSQP",
                          constraints=[{"type": "ineq", "fun": cons, "jac": jac}], options={"maxiter": 500, "ftol": 1e-16})
        y = repair(result.x.reshape(n, 3))
        if feasible(y) and -y[:, 2].sum() < -x[:, 2].sum():
            return y, -float(y[:, 2].sum())
        return x, -float(x[:, 2].sum())

    def verify(self, x, n):
        import mpmath as mp
        x = np.asarray(x, dtype=float)
        with mp.workdps(50):
            v = [[mp.mpf(float(a)) for a in row] for row in x]
            walls = min(min(c[0]-c[2], 1-c[0]-c[2], c[1]-c[2], 1-c[1]-c[2], c[2]) for c in v)
            gaps = min((mp.sqrt((v[a][0]-v[b][0])**2+(v[a][1]-v[b][1])**2)-v[a][2]-v[b][2] for a in range(n) for b in range(a)),
                       default=mp.mpf(1))
            total = sum(c[2] for c in v)
        value = -float(total)
        best = self.best_known(n)
        valid = bool(len(v) == n and walls >= 0 and gaps >= 0)
        return {"n": n, "value": value, "side": value, "reference_side": best, "improvement": None if best is None else best-value,
                "valid": valid, "record": bool(valid and best is not None and value < best-1e-9), "sum_of_radii": float(total),
                "min_pair_clearance": float(gaps), "min_wall_clearance": float(walls), "float_zero_tolerance": valid,
                "high_precision": [{"digits": 50, "valid": valid}], "poses": x.tolist()}

    def svg(self, x, value):
        x = np.asarray(x, dtype=float)
        circles = "".join(f'<circle cx="{cx:.6f}" cy="{1-cy:.6f}" r="{r:.6f}"/>' for cx, cy, r in x)
        return ('<svg viewBox="-0.01 -0.01 1.02 1.02" xmlns="http://www.w3.org/2000/svg" style="fill:#B2B2B2;stroke:black;'
                f'stroke-width:0.002"><rect x="0" y="0" width="1" height="1" style="fill:white"/>{circles}</svg>')
