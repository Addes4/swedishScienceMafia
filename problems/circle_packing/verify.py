"""Circle packing in a square, n = 26: maximise the sum of radii (problem 36).

Best known value: the n = 26 construction in the AlphaEvolve problem repository
(experiments/packing_circles_max_sum_of_radii), whose radii sum to 2.6359830849.
The same value is reported by ShinkaEvolve (Lange et al. 2025).
"""
import math
from fractions import Fraction

FUNCTION = "solve"
PUBLIC = [{"n": 26}]
HIDDEN = []
TIMEOUT_S = 300
TOL = 1e-9
STRICT_TOL = 1e-12
BEST_KNOWN = {26: 2.6359830849176076}


def label(instance):
    return f"n={instance['n']}"


def best_known(instance):
    return BEST_KNOWN.get(instance["n"])


def _parse(construction, n):
    if isinstance(construction, dict):
        centers, radii = construction.get("centers"), construction.get("radii")
    elif isinstance(construction, list) and len(construction) >= 2:
        centers, radii = construction[0], construction[1]
    else:
        raise ValueError("return (centers, radii)")
    if not (isinstance(centers, list) and isinstance(radii, list) and len(centers) == n and len(radii) == n):
        raise ValueError(f"expected {n} centres and {n} radii")
    cs = [(float(c[0]), float(c[1])) for c in centers]
    rs = [float(r) for r in radii]
    if any(math.isnan(v) or math.isinf(v) for c in cs for v in c) \
            or any(math.isnan(r) or math.isinf(r) or r < 0 for r in rs):
        raise ValueError("centres must be finite and radii finite and non-negative")
    return cs, rs


def _check(construction, instance, tol):
    n = instance["n"]
    try:
        cs, rs = _parse(construction, n)
    except (ValueError, TypeError, IndexError) as e:
        return {"valid": False, "score": None, "reason": str(e)}
    for i, ((x, y), r) in enumerate(zip(cs, rs)):
        if x - r < -tol or x + r > 1 + tol or y - r < -tol or y + r > 1 + tol:
            return {"valid": False, "score": None, "reason": f"circle {i} sticks out of the unit square"}
    for i in range(n):
        for j in range(i + 1, n):
            if math.dist(cs[i], cs[j]) < rs[i] + rs[j] - tol:
                return {"valid": False, "score": None, "reason": f"circles {i} and {j} overlap"}
    return {"valid": True, "score": sum(rs), "reason": ""}


def check(construction, instance):
    return _check(construction, instance, TOL)


def check_strict(construction, instance):
    """Independent re-check in exact rational arithmetic with a 1e-12 slack (float rounding
    only): containment, and d(i,j) >= r_i + r_j - 1e-12 via squared distances."""
    try:
        cs, rs = _parse(construction, instance["n"])
    except (ValueError, TypeError, IndexError):
        return False
    eps = Fraction(STRICT_TOL)
    C = [(Fraction(x), Fraction(y)) for x, y in cs]
    R = [Fraction(r) for r in rs]
    for (x, y), r in zip(C, R):
        if x - r < -eps or x + r > 1 + eps or y - r < -eps or y + r > 1 + eps:
            return False
    for i in range(len(C)):
        for j in range(i + 1, len(C)):
            dx, dy = C[i][0] - C[j][0], C[i][1] - C[j][1]
            need = R[i] + R[j] - eps
            if need > 0 and dx * dx + dy * dy < need * need:
                return False
    return True
