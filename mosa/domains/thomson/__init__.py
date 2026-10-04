"""Points on a sphere: n unit charges minimizing the Riesz s-energy sum_{i<j} 1/|x_i - x_j|^s.

s = 1 is the Thomson problem (Coulomb energy); its best known energies (putative global minima) come from the Cambridge
Cluster Database (data/thomson/reference.json). Other exponents have no published table here: they are problems no
model can have memorized, and results are compared between methods. Strategies get no known configuration: they start from nothing but what their
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
def energy_gradient(y, s=1.):
    """Riesz s-energy of the points y_i/|y_i| and its gradient with respect to the unconstrained y (flat, 3n)."""
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
            e += r**-s
            f = s*r**(-s-2.)
            g[i, 0] -= d0*f
            g[i, 1] -= d1*f
            g[i, 2] -= d2*f
            g[j, 0] += d0*f
            g[j, 1] += d1*f
            g[j, 2] += d2*f
    out = np.empty(3*n)
    for i in range(n):
        dot = g[i, 0]*x[i, 0]+g[i, 1]*x[i, 1]+g[i, 2]*x[i, 2]
        for k in range(3):
            out[3*i+k] = (g[i, k]-dot*x[i, k])/norms[i]
    return e, out


def _minimize(x, gtol, ftol, s=1.):
    y = (np.asarray(x, dtype=float)/np.linalg.norm(x, axis=1, keepdims=True)).ravel()
    result = minimize(energy_gradient, y, args=(float(s),), jac=True, method="L-BFGS-B", options={"maxiter": 50000, "gtol": gtol, "ftol": ftol})
    points = result.x.reshape(-1, 3)
    points /= np.linalg.norm(points, axis=1, keepdims=True)
    return points, float(energy_gradient(points.ravel(), float(s))[0]), int(result.nfev)


class Riesz(Domain):
    """Riesz s-energy on the sphere; Riesz(1) is the Thomson problem."""
    family = "points on a sphere"

    def __init__(self, s=1.):
        self.s = float(s)
        self.name = "thomson" if self.s == 1. else f"riesz-{s:g}"
        self.title = "Charges on a sphere (the Thomson problem)" if self.s == 1. else f"Riesz {s:g}-energy on the sphere"
        self.problem = (f"Place n identical points on the unit sphere to minimize the sum over all pairs of 1/distance^{s:g}"
                        f"{' (the Coulomb energy)' if self.s == 1. else ''}. The objective is the energy.")
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
        if self.s != 1.:
            return {}
        return {int(k): v for k, v in json.loads((DATA/"reference.json").read_text())["energies"].items()}

    def targets(self):
        return sorted(self._reference) if self._reference else list(range(10, 1001))

    def reference(self, n):
        return None, self.best_known(n)

    def best_known(self, n):
        return self._reference[n]["energy"] if n in self._reference else None

    def info(self, n):
        entry = self._reference.get(n, {})
        return {"best_known": self.best_known(n), "point_group": entry.get("point_group"),
                "source": "Cambridge Cluster Database" if entry else "no published value"}

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
        return _minimize(x, 1e-9, 1e-14, self.s)

    def polish(self, x, value=None):
        points, energy, _ = _minimize(x, 1e-12, 1e-16, self.s)
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
                    energy += r**(-mp.mpf(self.s))
            value = float(energy)
        best = self.best_known(n)
        valid = len(p) == n and closest > 1e-9
        return {"n": n, "value": value, "side": value, "reference_side": best, "improvement": None if best is None else best-value,
                "valid": bool(valid), "record": bool(valid and best is not None and value < best-1e-6),
                "reached": bool(valid and best is not None and abs(value-best) <= 1e-6),
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


Thomson = Riesz
