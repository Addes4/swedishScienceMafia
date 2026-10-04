"""Erdős squares in a square (problem 55, Georgiev, Gómez-Serrano, Tao, Wagner 2025).

check() ports the official checker from the problem repository's
experiments/erdos_squares_in_a_square notebook: squares are (centre_x, centre_y, angle, side)
with every number in [0, 1], angle a fraction of a full turn, separating-axis overlap test,
tolerance 1e-9, and squares of side <= 1e-9 treated as points.

One deliberate change: the notebook's test demands a gap of more than 1e-9 between squares,
so squares that merely touch count as overlapping, contradicting "disjoint interiors" (it
rejects a plain k x k grid). Here touching is allowed and overlaps up to 1e-9 are tolerated;
check_strict() re-checks with a 1e-12 tolerance, so the 1e-9 cannot be exploited.
"""
import math
from fractions import Fraction

FUNCTION = "solve"
PUBLIC = [{"n": n} for n in (5, 6, 7, 8, 11, 12, 13, 14, 15)]
HIDDEN = [{"n": n} for n in (18, 21, 23, 27)]
TIMEOUT_S = 60
TOL = 1e-9
STRICT_TOL = 1e-12


def label(instance):
    return f"n={instance['n']}"


def best_known(instance):
    """k + c/k with n = k^2 + 2c + 1, |c| <= k: the best known value (Campbell-Staton conjecture)."""
    n = instance["n"]
    best = None
    for k in range(1, math.isqrt(n) + 3):
        if (n - k * k - 1) % 2 == 0:
            c = (n - k * k - 1) // 2
            if abs(c) <= k and (best is None or k + c / k > best):
                best = k + c / k
    return best


def _parse(construction, n):
    if not isinstance(construction, list) or len(construction) != n:
        raise ValueError(f"expected a list of {n} squares")
    squares = []
    for i, sq in enumerate(construction):
        if not isinstance(sq, list) or len(sq) != 4:
            raise ValueError(f"square {i} must be (centre_x, centre_y, angle, side)")
        vals = [float(v) for v in sq]
        if any(math.isnan(v) or v < 0 or v > 1 for v in vals):
            raise ValueError(f"square {i}: every value must lie in [0, 1]")
        squares.append(vals)
    return squares


def _vertices(x, y, a, s):
    t = a * 2 * math.pi
    c, d = math.cos(t), math.sin(t)
    h = s / 2
    dx1, dy1, dx2, dy2 = h * c, h * d, -h * d, h * c
    return [(x + dx1 + dx2, y + dy1 + dy2), (x - dx1 + dx2, y - dy1 + dy2),
            (x - dx1 - dx2, y - dy1 - dy2), (x + dx1 - dx2, y + dy1 - dy2)]


def _axes(v):
    axes = []
    for i in range(2):
        ex, ey = v[i + 1][0] - v[i][0], v[i + 1][1] - v[i][1]
        norm = math.hypot(ex, ey)
        if norm > 1e-12:
            axes.append((-ey / norm, ex / norm))
    return axes


def _overlap(p, q, tol):
    vp, vq = _vertices(*p), _vertices(*q)
    for ax in _axes(vp) + _axes(vq):
        a = [x * ax[0] + y * ax[1] for x, y in vp]
        b = [x * ax[0] + y * ax[1] for x, y in vq]
        if max(a) <= min(b) + tol or max(b) <= min(a) + tol:
            return False                      # separating axis found (touching is allowed)
    return True


def _check(construction, instance, tol):
    n = instance["n"]
    try:
        squares = _parse(construction, n)
    except (ValueError, TypeError) as e:
        return {"valid": False, "score": None, "reason": str(e)}
    for i, (x, y, a, s) in enumerate(squares):
        if s > tol and any(not (-tol <= vx <= 1 + tol and -tol <= vy <= 1 + tol) for vx, vy in _vertices(x, y, a, s)):
            return {"valid": False, "score": None, "reason": f"square {i} sticks out of the unit square"}
    for i in range(n):
        for j in range(i + 1, n):
            if squares[i][3] > tol and squares[j][3] > tol and _overlap(squares[i], squares[j], tol):
                return {"valid": False, "score": None, "reason": f"squares {i} and {j} overlap"}
    return {"valid": True, "score": sum(s for *_, s in squares), "reason": ""}


def check(construction, instance):
    return _check(construction, instance, TOL)


def check_strict(construction, instance):
    """Independent re-check with tolerance 1e-12 (float rounding only). For squares that are
    not rotated it uses exact rational arithmetic on the given coordinates."""
    try:
        squares = _parse(construction, instance["n"])
    except (ValueError, TypeError):
        return False
    if not all(a in (0.0, 0.25, 0.5, 0.75, 1.0) for _, _, a, _ in squares):
        return _check(construction, instance, STRICT_TOL)["valid"]
    eps = Fraction(STRICT_TOL)
    boxes = [(Fraction(x) - Fraction(s) / 2, Fraction(y) - Fraction(s) / 2, Fraction(s)) for x, y, _, s in squares]
    for x0, y0, s in boxes:
        if s > eps and (x0 < -eps or y0 < -eps or x0 + s > 1 + eps or y0 + s > 1 + eps):
            return False
    for i, (xi, yi, si) in enumerate(boxes):
        for xj, yj, sj in boxes[i + 1:]:
            if si > eps and sj > eps and xi + eps < xj + sj and xj + eps < xi + si \
                    and yi + eps < yj + sj and yj + eps < yi + si:
                return False
    return True
