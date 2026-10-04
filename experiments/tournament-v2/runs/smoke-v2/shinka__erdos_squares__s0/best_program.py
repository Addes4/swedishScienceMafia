# EVOLVE-BLOCK-START
"""Adaptive rectangular-partition packer for squares in a unit square.

Model: partition [0,1]x[0,1] into a small number of horizontal strips.
Each strip is filled with an integer number of equal squares of a chosen size.
A recursive / beam search over strip decompositions finds the layout that
maximises total side length for a given n.  A short local-search pass then
perturbs strip boundaries and per-strip square counts to improve the score.
"""

import math
from dataclasses import dataclass
from typing import List, Tuple, Optional

Square = Tuple[float, float, float, float]  # cx, cy, angle, side


# ---------------------------------------------------------------------------
# Strip primitives
# ---------------------------------------------------------------------------

@dataclass
class Strip:
    """A horizontal strip of height h, filled with `count` equal squares."""
    height: float
    count: int
    side: float

    @property
    def width_used(self) -> float:
        return self.count * self.side


def _make_strip(height: float, count: int) -> Optional[Strip]:
    """Build a strip of given height holding `count` squares.

    The squares must fit side-by-side in the unit width, so side <= 1/count.
    We use the largest side that also respects the strip height.
    """
    if count <= 0 or height <= 0:
        return None
    side = min(height, 1.0 / count)
    if side <= 0:
        return None
    return Strip(height=height, count=count, side=side)


def _strip_total(strips: List[Strip]) -> float:
    return sum(s.count * s.side for s in strips)


def _strip_count(strips: List[Strip]) -> int:
    return sum(s.count for s in strips)


def _strips_to_squares(strips: List[Strip], n: int) -> List[Square]:
    """Convert a list of strips into exactly n square tuples."""
    squares: List[Square] = []
    y = 0.0
    for st in strips:
        if st.count <= 0:
            continue
        side = st.side
        # centre the row horizontally
        total_w = st.count * side
        x0 = (1.0 - total_w) * 0.5
        cy = y + st.height * 0.5
        for i in range(st.count):
            cx = x0 + (i + 0.5) * side
            squares.append((cx, cy, 0.0, side))
        y += st.height
    # pad with zero-size squares if short
    while len(squares) < n:
        squares.append((0.5, 0.5, 0.0, 0.0))
    return squares[:n]


# ---------------------------------------------------------------------------
# Search for the best strip decomposition
# ---------------------------------------------------------------------------

def _candidate_heights(num_strips: int, base: float) -> List[float]:
    """Generate a few plausible height profiles for `num_strips` strips."""
    profiles = []
    # uniform
    profiles.append([base] * num_strips)
    # slightly varied: taper
    for delta in (0.02, 0.05, -0.02, -0.05):
        prof = [max(1e-6, base + delta * (i - num_strips / 2))
                for i in range(num_strips)]
        s = sum(prof)
        prof = [h / s for h in prof]
        profiles.append(prof)
    return profiles


def _best_strips_for_profile(profile: List[float], n: int) -> Optional[List[Strip]]:
    """Given strip heights (summing to 1), choose integer square counts.

    We want total squares == n and maximise sum(count_i * min(h_i, 1/count_i)).
    A small DP over strips and used-square count solves this exactly for the
    given profile.
    """
    m = len(profile)
    if m == 0 or n <= 0:
        return None
    # DP: dp[i][k] = best value using first i strips with k squares total
    NEG = -1e18
    dp = [[NEG] * (n + 1) for _ in range(m + 1)]
    choice = [[0] * (n + 1) for _ in range(m + 1)]
    dp[0][0] = 0.0
    for i in range(m):
        h = profile[i]
        for k in range(n + 1):
            if dp[i][k] == NEG:
                continue
            # try c squares in this strip
            max_c = n - k
            for c in range(0, max_c + 1):
                if c == 0:
                    val = 0.0
                else:
                    side = min(h, 1.0 / c)
                    val = c * side
                nk = k + c
                if dp[i][k] + val > dp[i + 1][nk]:
                    dp[i + 1][nk] = dp[i][k] + val
                    choice[i + 1][nk] = c
    if dp[m][n] == NEG:
        return None
    # reconstruct
    counts = [0] * m
    k = n
    for i in range(m, 0, -1):
        c = choice[i][k]
        counts[i - 1] = c
        k -= c
    strips = []
    for h, c in zip(profile, counts):
        st = _make_strip(h, c)
        if st is not None:
            strips.append(st)
    return strips


def _search_strips(n: int) -> Optional[List[Strip]]:
    """Beam search over the number of strips and their height profiles."""
    if n <= 0:
        return None
    best_strips: Optional[List[Strip]] = None
    best_val = -1.0

    # Try a range of strip counts.  More strips = more flexibility but slower.
    max_strips = min(n, 12)
    for m in range(1, max_strips + 1):
        base = 1.0 / m
        for profile in _candidate_heights(m, base):
            strips = _best_strips_for_profile(profile, n)
            if strips is None:
                continue
            val = _strip_total(strips)
            if val > best_val:
                best_val = val
                best_strips = strips
    return best_strips


# ---------------------------------------------------------------------------
# Local improvement
# ---------------------------------------------------------------------------

def _perturb(strips: List[Strip], n: int) -> List[Strip]:
    """Try small integer perturbations to the square counts per strip."""
    if not strips:
        return strips
    improved = True
    best = strips
    best_val = _strip_total(best)
    while improved:
        improved = False
        for i in range(len(best)):
            for dc in (-1, 1):
                new_strips = []
                for j, st in enumerate(best):
                    c = st.count + (dc if j == i else 0)
                    c = max(0, c)
                    ns = _make_strip(st.height, c)
                    if ns is not None:
                        new_strips.append(ns)
                    else:
                        new_strips.append(Strip(st.height, 0, 0.0))
                if _strip_count(new_strips) != n:
                    continue
                val = _strip_total(new_strips)
                if val > best_val + 1e-12:
                    best_val = val
                    best = new_strips
                    improved = True
    return best


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def solve(n: int) -> List[Square]:
    """Return n squares inside [0,1]^2 with disjoint interiors,
    maximising the sum of side lengths.
    """
    if n <= 0:
        return []

    # Trivial case: a single square fills the unit square.
    if n == 1:
        return [(0.5, 0.5, 0.0, 1.0)]

    # Search for a good strip decomposition.
    strips = _search_strips(n)
    if strips is None:
        # fallback: pure k x k grid
        k = max(1, math.isqrt(n))
        side = 1.0 / k
        squares = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side)
                   for i in range(k) for j in range(k)]
        while len(squares) < n:
            squares.append((0.5, 0.5, 0.0, 0.0))
        return squares[:n]

    # Local improvement.
    strips = _perturb(strips, n)

    squares = _strips_to_squares(strips, n)
    return squares[:n]
# EVOLVE-BLOCK-END
