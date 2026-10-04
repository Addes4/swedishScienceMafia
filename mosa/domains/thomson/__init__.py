"""The Thomson problem: n unit charges on a sphere, minimizing the Coulomb energy sum_{i<j} 1/|x_i - x_j|.

Best known energies (putative global minima) come from the Cambridge Cluster Database
(data/thomson/reference.json). Strategies get no known configuration: they start from nothing but what their
workspace has already found for other sizes. A candidate is (points, value) with points an (n, 3) array (any nonzero
rows; they are projected onto the unit sphere) and value ignored.
"""
from __future__ import annotations

from functools import cached_property
import json
import math
from pathlib import Path

import numpy as np
from numba import njit
from scipy.optimize import minimize

from ...domain import Domain

DATA = Path(__file__).resolve().parents[3]/"data"/"thomson"


@njit(cache=True)
def energy_gradient(y):
    """Energy of the points y_i/|y_i| and its gradient with respect to the unconstrained y (flat, 3n)."""
    n = len(y)//3
    x = np.empty((n, 3))
    norms = np.empty(n)
    for i in range(n):
        norms[i] = math.sqrt(y[3*i]**2+y[3*i+1]**2+y[3*i+2]**2)
        for k in range(3):
            x[i, k] = y[3*i+k]/norms[i]
    g = np.zeros((n, 3))
    e = 0.
    for i in range(n):
        for j in range(i):
            d0, d1, d2 = x[i, 0]-x[j, 0], x[i, 1]-x[j, 1], x[i, 2]-x[j, 2]
            r2 = d0*d0+d1*d1+d2*d2
            r = math.sqrt(r2)
            e += 1./r
            s = 1./(r2*r)
            g[i, 0] -= d0*s
            g[i, 1] -= d1*s
            g[i, 2] -= d2*s
            g[j, 0] += d0*s
            g[j, 1] += d1*s
            g[j, 2] += d2*s
    out = np.empty(3*n)
    for i in range(n):
        dot = g[i, 0]*x[i, 0]+g[i, 1]*x[i, 1]+g[i, 2]*x[i, 2]
        for k in range(3):
            out[3*i+k] = (g[i, k]-dot*x[i, k])/norms[i]
    return e, out


def _minimize(x, gtol, ftol):
    y = (np.asarray(x, dtype=float)/np.linalg.norm(x, axis=1, keepdims=True)).ravel()
    result = minimize(energy_gradient, y, jac=True, method="L-BFGS-B", options={"maxiter": 50000, "gtol": gtol, "ftol": ftol})
    points = result.x.reshape(-1, 3)
    points /= np.linalg.norm(points, axis=1, keepdims=True)
    return points, float(energy_gradient(points.ravel())[0]), int(result.nfev)


class Thomson(Domain):
    name = "thomson"
    title = "Charges on a sphere (the Thomson problem)"
    problem = ("Place n identical unit point charges on the unit sphere to minimize their Coulomb energy, the sum over all pairs "
               "of 1/distance. The objective is the energy.")
    evidence = """What is known about this landscape (from the literature; no measurements of our own yet):
- The number of local minima grows roughly exponentially with n; random starts relaxed by gradient descent land in many
  different minima above the best known energy for n beyond about 100.
- Low-energy configurations are close to triangulations in which most charges have six neighbours and twelve or more have
  five; for larger n the five-fold defects form short chains ("scars").
- Best known configurations for nearby n are often related: adding or removing a charge near a defect, followed by
  relaxation, can lead to the best known configuration of the neighbouring size, but not always.
- Packings whose energies differ by less than 1e-7 are treated as the same basin."""
    api = '''# The global n is the number of charges in this run.
def initialize(record, neighbours, rng, count):
    """record: None (no known configuration is given for this n). neighbours: dict {m: (points, energy)}, the best
    configurations found so far in this workspace for nearby sizes m (possibly empty); points is an (m, 3) array of
    unit vectors. Return up to `count` candidates (points, 0.0) with points an (n, 3) array of nonzero rows (they are
    projected onto the sphere and relaxed)."""

def vary(parents, rng, count):
    """parents: list of (points, energy), the current population of distinct relaxed configurations for this n, best
    first. Return `count` new candidates (points, 0.0) derived from the population."""'''
    same = 1e-7

    @cached_property
    def _reference(self):
        return {int(k): v for k, v in json.loads((DATA/"reference.json").read_text())["energies"].items()}

    def targets(self):
        return sorted(self._reference)

    def reference(self, n):
        return None, self._reference[n]["energy"]

    def best_known(self, n):
        return self._reference[n]["energy"]

    def info(self, n):
        return {"best_known": self.best_known(n), "point_group": self._reference[n].get("point_group"),
                "source": "Cambridge Cluster Database"}

    def validate(self, x, value, n):
        x = np.asarray(x, dtype=float)
        if x.shape != (n, 3) or not np.isfinite(x).all():
            raise ValueError(f"a candidate has shape {x.shape} (expected ({n}, 3)) or non-finite values")
        norms = np.linalg.norm(x, axis=1)
        if norms.min() < 1e-9:
            raise ValueError("a candidate has a zero point")
        u = x/norms[:, None]
        gaps = np.linalg.norm(u[:, None]-u[None], axis=-1)+2*np.eye(n)
        if gaps.min() < 1e-6:
            raise ValueError("a candidate places two charges at the same point")
        return x

    def relax(self, x, value=None):
        return _minimize(x, 1e-9, 1e-14)

    def polish(self, x, value=None):
        points, energy, _ = _minimize(x, 1e-12, 1e-16)
        return points, energy

    def verify(self, x, n):
        """Energy recomputed at 50 digits from the points (normalized in high precision)."""
        import mpmath as mp
        with mp.workdps(50):
            p = []
            for row in np.asarray(x, dtype=float):
                v = [mp.mpf(float(c)) for c in row]
                norm = mp.sqrt(sum(c*c for c in v))
                p.append([c/norm for c in v])
            energy = mp.mpf(0)
            closest = mp.inf
            for i in range(len(p)):
                for j in range(i):
                    r = mp.sqrt(sum((p[i][k]-p[j][k])**2 for k in range(3)))
                    closest = min(closest, r)
                    energy += 1/r
            value = float(energy)
        best = self.best_known(n)
        valid = len(p) == n and closest > 1e-9
        return {"n": n, "value": value, "side": value, "reference_side": best, "improvement": best-value, "valid": bool(valid),
                "record": bool(valid and value < best-1e-6), "reached": bool(valid and abs(value-best) <= 1e-6),
                "min_distance": float(closest), "high_precision": [{"digits": 50, "valid": bool(valid), "energy": mp.nstr(energy, 20)}],
                "poses": np.asarray(x).tolist(), "float_zero_tolerance": bool(valid), "min_pair_clearance": float(closest)}

    def svg(self, x, value=None):
        """Orthographic view of the sphere: charges on the near side filled, on the far side hollow."""
        p = np.asarray(x, dtype=float)
        p = p/np.linalg.norm(p, axis=1, keepdims=True)
        dots = "".join(f'<circle cx="{u:.4f}" cy="{-v:.4f}" r="0.035" style="fill:{"var(--sq-edge)" if w > 0 else "none"};stroke:var(--sq-edge)" stroke-width="0.008"/>'
                       for u, v, w in sorted(p.tolist(), key=lambda q: q[2]))
        return (f'<svg viewBox="-1.1 -1.1 2.2 2.2" xmlns="http://www.w3.org/2000/svg"><circle cx="0" cy="0" r="1" '
                f'style="fill:var(--paper);stroke:var(--sq-edge)" stroke-width="0.008"/>{dots}</svg>')
