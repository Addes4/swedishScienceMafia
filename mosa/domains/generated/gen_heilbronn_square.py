import math
import itertools
from fractions import Fraction
from functools import lru_cache
import numpy as np
from scipy.optimize import minimize
from mosa.domain import Domain

KNOWN = {}


def _size(n):
    if isinstance(n, (bool, np.bool_)) or not isinstance(n, (int, np.integer)) or not 3 <= n <= 30:
        raise ValueError("n must be an integer from 3 through 30")
    return int(n)


def _points(x, n, contained=True):
    n = _size(n)
    try:
        raw = np.asarray(x)
        if raw.dtype.kind not in "iuf":
            raise ValueError("coordinates must be real numbers")
        p = np.asarray(raw, dtype=float)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError("invalid coordinates") from exc
    if p.shape != (n, 2) or not np.isfinite(p).all():
        raise ValueError("expected a finite (n, 2) array")
    if contained and (np.any(p < 0.0) or np.any(p > 1.0)):
        raise ValueError("points must lie in the closed unit square")
    return p.copy()


def _infer(x, contained=True):
    try:
        n = len(x)
    except (TypeError, ValueError) as exc:
        raise ValueError("expected a point array") from exc
    return _points(x, n, contained)


@lru_cache(maxsize=28)
def _triples(n):
    t = np.array(list(itertools.combinations(range(n), 3)), dtype=int)
    t.setflags(write=False)
    return t.T


def _signed(p, indices):
    i, j, k = indices
    u, v = p[j] - p[i], p[k] - p[i]
    return 0.5 * (u[:, 0] * v[:, 1] - u[:, 1] * v[:, 0]), u, v


class Problem(Domain):
    family = "points in the unit square"
    title = "Heilbronn's triangle problem"
    problem = (
        "Place n points in the closed unit square [0,1]^2 and minimize the "
        "negative of the smallest unsigned triangle area among all unordered "
        "triples. The positive score is minus the objective. Repeated points "
        "and collinear triples are feasible and give minimum area zero. "
        "There are no symmetry, separation, or general-position restrictions."
    )
    evidence = (
        "The objective is nonsmooth when the smallest triangle changes, and "
        "absolute determinants make the landscape nonconvex. Sudermann-Merx, "
        "'From Computational Certification to Exact Coordinates: Heilbronn's "
        "Triangle Problem on the Unit Square Using Mixed-Integer Optimization', "
        "arXiv:2603.11107v2 (2026), recovers exact coordinates matching published "
        "best-known configurations for n <= 9 using numerical certification "
        "and symbolic computation: https://arxiv.org/abs/2603.11107v2 . "
        "KNOWN is deliberately empty; no numerical benchmark or claim of "
        "global optimality is encoded. Local self-tests covered n=5,8,9,10,11,12,20,30, "
        "degeneracies, malformed inputs, containment, objective consistency, and "
        "repair. Measured relaxation times were about 0.12 seconds for n=20 and "
        "0.29 seconds for n=30; these are hardware-dependent observations."
    )
    api = """def initialize(record, neighbours, rng, count):
    # Return count candidates (x, value), for the global integer n.
    # x is a real numpy array of shape (n, 2), with coordinates in [0,1].
    # value is -min triangle area, a finite scalar in [-0.5, 0].
    # record is always None; no reference coordinates are stored.
    # neighbours is {m: (x, value)} for nearby sizes, possibly empty.
    # Adapt neighbours by adding/removing points to obtain exactly n points.
    # rng is a numpy.random.Generator. All triples count, including degeneracies.
    ...
def vary(parents, rng, count):
    # parents contains (x, value) candidates for the same global n.
    # Return count candidates in exactly the same format.
    # Perturb or recombine coordinates, clip to [0,1], and recompute value.
    # Values are minimization objectives; smaller (more negative) is better.
    ..."""
    same = 1e-7

    def targets(self):
        return list(range(3, 31))

    def reference(self, n):
        _size(n)
        return None, KNOWN.get(n)

    def best_known(self, n):
        _size(n)
        return KNOWN.get(n)

    def random(self, n, rng):
        p = rng.random((_size(n), 2))
        return p, self.verify(p, n)["value"]

    def validate(self, x, value, n):
        p = _points(x, n)
        try:
            a = np.asarray(value)
            if a.shape != () or a.dtype.kind not in "iuf":
                raise ValueError("value must be a real scalar")
            v = float(a)
        except (TypeError, ValueError, OverflowError) as exc:
            raise ValueError("invalid objective") from exc
        if not math.isfinite(v) or not -0.5 <= v <= 0.0:
            raise ValueError("objective must be finite and in [-0.5, 0]")
        actual = self.verify(p, n)["value"]
        if abs(v - actual) > 1e-12:
            raise ValueError("claimed objective disagrees with the coordinates")
        return p

    def relax(self, x, value):
        # Ignore the untrusted claimed objective. Repair finite input by clipping.
        p = np.clip(_infer(x, contained=False), 0.0, 1.0)
        n = len(p)
        indices = _triples(n)
        best = p.copy()
        best_value = -float(np.min(np.abs(_signed(best, indices)[0])))
        evaluations = 0
        # Smooth-min continuation; track the true objective at every evaluation.
        for tau in (0.003, 0.0005, 0.00008):
            def objective(z):
                nonlocal best, best_value, evaluations
                evaluations += 1
                q = np.clip(z.reshape(n, 2), 0.0, 1.0)
                a, u, v = _signed(q, indices)
                aa = np.abs(a)
                minimum = float(aa.min())
                if -minimum < best_value:
                    best, best_value = q.copy(), -minimum
                weights = np.exp(-(aa - minimum) / tau)
                total = float(weights.sum())
                weights /= total
                c = -0.5 * weights * np.sign(a)
                g = np.zeros_like(q)
                i, j, k = indices
                np.add.at(g, j, c[:, None] * np.column_stack((v[:, 1], -v[:, 0])))
                np.add.at(g, k, c[:, None] * np.column_stack((-u[:, 1], u[:, 0])))
                np.add.at(g, i, c[:, None] * np.column_stack(
                    (u[:, 1] - v[:, 1], v[:, 0] - u[:, 0])))
                return -minimum + tau * math.log(total), g.ravel()

            result = minimize(
                objective, best.ravel(), jac=True, method="L-BFGS-B",
                bounds=[(0.0, 1.0)] * (2 * n),
                options={"maxiter": 25, "maxfun": 80, "maxls": 12, "ftol": 1e-12},
            )
            if np.isfinite(result.x).all():
                q = np.clip(result.x.reshape(n, 2), 0.0, 1.0)
                v = -float(np.min(np.abs(_signed(q, indices)[0])))
                if v < best_value:
                    best, best_value = q.copy(), v
        # Final independent check; returned value never comes from smooth-min.
        best = np.clip(best, 0.0, 1.0)
        return best, self.verify(best, n)["value"], evaluations

    def polish(self, x, value):
        p = _infer(x)
        return p, self.verify(p, len(p))["value"]

    def verify(self, x, n):
        p = _points(x, n)
        # Every finite binary64 coordinate is an exact dyadic rational.
        # A common power-of-two denominator permits exact integer determinants.
        # This uses neither the optimizer's triple table nor its area routine.
        ratios = [[float(c).as_integer_ratio() for c in row] for row in p]
        denominator = max(d for row in ratios for _, d in row)
        points = [
            tuple(a * (denominator // d) for a, d in row)
            for row in ratios
        ]
        least = None
        for i in range(n - 2):
            xi, yi = points[i]
            for j in range(i + 1, n - 1):
                xj, yj = points[j]
                for k in range(j + 1, n):
                    xk, yk = points[k]
                    twice = abs((xj - xi) * (yk - yi) - (yj - yi) * (xk - xi))
                    if least is None or twice < least:
                        least = twice
        area = Fraction(least, 2 * denominator * denominator)
        score = float(area)
        return {"valid": True, "value": -score, "score": score}

    def svg(self, x, value):
        p = _infer(x)
        parts = [
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 440 440">',
            '<rect x="20" y="20" width="400" height="400" '
            'style="fill:#B2B2B2;stroke:black"/>',
        ]
        for px, py in p:
            parts.append(
                '<circle cx="%.8f" cy="%.8f" r="4" '
                'style="fill:#B2B2B2;stroke:black"/>' %
                (20 + 400 * px, 420 - 400 * py)
            )
        parts.append("</svg>")
        return "".join(parts)
