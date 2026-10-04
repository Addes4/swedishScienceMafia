"""Independent verification of a packing: float separating-axis test at zero tolerance and a high-precision audit.

Binary float coordinates are interpreted exactly and every corner, projection and gap is computed with mpmath at 80
and at 160 digits. Pairs whose centres are more than sqrt(2) + 0.01 apart are skipped: their circumscribed circles
(radius sqrt(2)/2) cannot meet. This is a high-precision numerical check, not interval arithmetic or a proof of
optimality.
"""
from __future__ import annotations

import numpy as np

from .kernel import MARGIN, clearances, vertices


def _exact(mp, value):
    numerator, denominator = float(value).as_integer_ratio()
    return mp.mpf(numerator)/denominator


def high_precision_check(poses, side, digits):
    import mpmath as mp
    with mp.workdps(digits):
        q = [[_exact(mp, v) for v in row] for row in poses]
        length = _exact(mp, side)
        half = mp.mpf(1)/2
        corners = [[(x+u*mp.cos(t)-w*mp.sin(t), y+u*mp.sin(t)+w*mp.cos(t))
                    for u, w in ((-half, -half), (half, -half), (half, half), (-half, half))] for x, y, t in q]
        wall = min(min(c, length-c) for square in corners for point in square for c in point)
        pair = mp.inf
        far = 2.0284  # (sqrt 2 + 0.01)^2
        for i in range(len(q)):
            for j in range(i):
                if (poses[i][0]-poses[j][0])**2+(poses[i][1]-poses[j][1])**2 > far:
                    continue
                axes = [(mp.cos(q[k][2]), mp.sin(q[k][2])) for k in (i, j)]
                axes += [(-b, a) for a, b in axes]
                gap = -mp.inf
                for a, b in axes:
                    pi = [x*a+y*b for x, y in corners[i]]
                    pj = [x*a+y*b for x, y in corners[j]]
                    gap = max(gap, min(pi)-max(pj), min(pj)-max(pi))
                pair = min(pair, gap)
        return {"digits": digits, "valid": bool(wall >= 0 and pair >= 0),
                "min_wall_gap": mp.nstr(wall, 12), "min_pair_gap": mp.nstr(pair, 12)}


def finalize(poses):
    """The packing shifted so its lowest corners sit MARGIN inside the walls, and its side: highest corner + MARGIN."""
    q = np.asarray(poses, dtype=float).copy()
    q[:, :2] += MARGIN-vertices(q).min(axis=(0, 1))
    return q, float(vertices(q).max())+MARGIN


def verify(poses, n, reference_side):
    """Certificate for a candidate record: side, clearances and the zero-tolerance and high-precision verdicts."""
    q, side = finalize(poses)
    wall, pair = clearances(q, side)
    float_valid = len(q) == n and bool(wall >= 0 and pair >= 0)
    audits = [high_precision_check(q.tolist(), side, digits) for digits in (80, 160)] if float_valid else []
    valid = float_valid and all(a["valid"] for a in audits)
    return {"n": n, "side": side, "reference_side": reference_side, "improvement": reference_side-side,
            "valid": bool(valid), "record": bool(valid and side < reference_side-1e-9),
            "float_zero_tolerance": float_valid, "min_wall_clearance": float(wall), "min_pair_clearance": float(pair),
            "high_precision": audits, "poses": q.tolist()}
