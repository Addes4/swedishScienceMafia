import math
import numpy as np
from scipy.optimize import minimize

# ----------------------------- utilities -----------------------------

def _sq_points(cx, cy, angle, s):
    """Return the 4 corners of a square."""
    a = angle * 2.0 * math.pi
    ca, sa = math.cos(a), math.sin(a)
    h = s * 0.5
    pts = []
    for dx, dy in ((1, 1), (-1, 1), (-1, -1), (1, -1)):
        x = cx + h * (dx * ca - dy * sa)
        y = cy + h * (dx * sa + dy * ca)
        pts.append((x, y))
    return pts

def _pair_gap(cx1, cy1, a1, s1, cx2, cy2, a2, s2):
    """
    Approximate signed separation between two rotated squares.
    Positive means disjoint (with margin), negative means overlap.
    Uses separating axis theorem (max over axes of gap projections).
    """
    p1 = _sq_points(cx1, cy1, a1, s1)
    p2 = _sq_points(cx2, cy2, a2, s2)

    axes = []
    a = a1 * 2.0 * math.pi
    ca, sa = math.cos(a), math.sin(a)
    axes.append((ca, sa))
    axes.append((-sa, ca))
    a = a2 * 2.0 * math.pi
    ca, sa = math.cos(a), math.sin(a)
    axes.append((ca, sa))
    axes.append((-sa, ca))

    best = -1e18
    for ax, ay in axes:
        mn1 = min(x * ax + y * ay for x, y in p1)
        mx1 = max(x * ax + y * ay for x, y in p1)
        mn2 = min(x * ax + y * ay for x, y in p2)
        mx2 = max(x * ax + y * ay for x, y in p2)
        # separation along this axis
        gap = max(mn2 - mx1, mn1 - mx2)
        if gap > best:
            best = gap
    return best

def _containment_margin(cx, cy, angle, s):
    """Minimum distance from square to boundary (positive = inside)."""
    pts = _sq_points(cx, cy, angle, s)
    m = 1e18
    for x, y in pts:
        m = min(m, x, 1.0 - x, y, 1.0 - y)
    # This is conservative: positive means all corners inside,
    # but square could still cross boundary between corners? No, square is convex.
    return m

def _total_side(x):
    n = len(x) // 4
    return sum(x[i * 4 + 3] for i in range(n))

# ----------------------------- objective / constraints -----------------------------

def _unpack(x):
    n = len(x) // 4
    return [(x[i*4], x[i*4+1], x[i*4+2], x[i*4+3]) for i in range(n)]

def _pack(sqs):
    x = []
    for cx, cy, a, s in sqs:
        x.extend([cx, cy, a, s])
    return np.array(x, dtype=float)

def _initial_layout(n):
    """Try several layouts and return the one with largest total side."""
    candidates = []

    # 1) k x k grid plus leftovers as tiny points
    k = math.isqrt(n)
    if k >= 1:
        side = 1.0 / k
        sqs = []
        for i in range(k):
            for j in range(k):
                sqs.append(((i + 0.5) * side, (j + 0.5) * side, 0.0, side))
        # leftover squares as zero-size at random-ish spots
        for t in range(n - len(sqs)):
            sqs.append((0.5, 0.5, 0.0, 0.0))
        candidates.append(sqs)

    # 2) k x (k+1) grid with side = 1/max(k, ceil(n/k))
    # try several near-square grids
    for r in range(1, n + 1):
        c = int(math.ceil(n / r))
        if r * c >= n and r <= n and c <= n:
            side = min(1.0 / r, 1.0 / c)
            if side > 0:
                sqs = []
                for i in range(r):
                    for j in range(c):
                        if len(sqs) < n:
                            sqs.append(((i + 0.5) * side, (j + 0.5) * side, 0.0, side))
                while len(sqs) < n:
                    sqs.append((0.5, 0.5, 0.0, 0.0))
                candidates.append(sqs)

    # 3) all squares in a row (if n small)
    if n > 0:
        side = 1.0 / n
        sqs = [((i + 0.5) * side, 0.5, 0.0, side) for i in range(n)]
        candidates.append(sqs)

    # 4) strip packing: greedy fill rows
    def strip_pack(sizes):
        # not used for initial, but keep structure
        pass

    # pick best by sum of sides
    best = None
    best_val = -1
    for sqs in candidates:
        val = sum(s for _, _, _, s in sqs)
        if val > best_val:
            best_val = val
            best = sqs
    return best

def _constraints(n, x):
    """Return list of constraint dicts for SLSQP."""
    cons = []
    sqs = _unpack(x)
    # containment constraints: all corners inside unit square
    for i, (cx, cy, a, s) in enumerate(sqs):
        if s <= 1e-12:
            continue
        def make_inside(cx, cy, a, s):
            def f(xx):
                # we recompute with current x values
                return None
            return f
        # We'll use direct inequality constraints on coordinates and angles
        # xi >= 0, xi <= 1 etc. handled via bounds.
        # Containment: for each corner, 0 <= x <= 1, 0 <= y <= 1
        # Add 4*4 = 16 constraints per square? That's a lot but okay for moderate n.
        pts = _sq_points(cx, cy, a, s)
        for px, py in pts:
            # px >= 0
            cons.append({'type': 'ineq', 'fun': (lambda xx, i=i, px=px: _corner_x(xx, i) - 0.0)})
            # px <= 1
            cons.append({'type': 'ineq', 'fun': (lambda xx, i=i, px=px: 1.0 - _corner_x(xx, i))})
            cons.append({'type': 'ineq', 'fun': (lambda xx, i=i, px=px: _corner_y(xx, i) - 0.0)})
            cons.append({'type': 'ineq', 'fun': (lambda xx, i=i, px=px: 1.0 - _corner_y(xx, i))})

    # pairwise non-overlap constraints
    for i in range(n):
        for j in range(i + 1, n):
            def make_gap(i, j):
                def f(xx):
                    sqs = _unpack(xx)
                    cx1, cy1, a1, s1 = sqs[i]
                    cx2, cy2, a2, s2 = sqs[j]
                    if s1 <= 1e-12 or s2 <= 1e-12:
                        return 1.0  # zero-size always fine
                    return _pair_gap(cx1, cy1, a1, s1, cx2, cy2, a2, s2)
                return f
            cons.append({'type': 'ineq', 'fun': make_gap(i, j)})
    return cons

def _corner_x(xx, i):
    sqs = _unpack(xx)
    cx, cy, a, s = sqs[i]
    # return min x coordinate of square? Actually we need each corner.
    # This function just placeholder; we will implement direct constraints below.
    return 0.0

def _corner_y(xx, i):
    return 0.0

# The above constraint function design is inefficient.  Instead, use
# a simpler penalty-based approach with L-BFGS-B or SLSQP on a reduced set.

# ----------------------------- refined approach -----------------------------

def _refine(sqs, n, maxiter=200):
    """
    Local optimization: adjust centres, angles, sides to maximize sum of sides
    subject to non-overlap and containment.  Uses SLSQP with numerical gradients.
    """
    sqs = [list(s) for s in sqs]
    # We only optimize non-zero squares; zero-size stay zero.
    idx = [i for i, s in enumerate(sqs) if s[3] > 1e-9]
    m = len(idx)
    if m == 0:
        return sqs

    # Variables: for each active square: cx, cy, angle, side
    x0 = []
    for i in idx:
        cx, cy, a, s = sqs[i]
        x0.extend([cx, cy, a, s])
    x0 = np.array(x0, dtype=float)

    # bounds: cx,cy in [0,1]; angle in [0,1); side in [0,1]
    bounds = []
    for _ in range(m):
        bounds.append((0.0, 1.0))
        bounds.append((0.0, 1.0))
        bounds.append((0.0, 1.0))
        bounds.append((0.0, 1.0))

    # objective: minimize negative sum of sides
    def obj(x):
        return -sum(x[i*4+3] for i in range(m))

    # constraints
    cons = []

    # containment: all 4 corners inside [0,1]^2
    def make_contain(i, k):
        def f(x):
            cx, cy, a, s = x[i*4], x[i*4+1], x[i*4+2], x[i*4+3]
            pts = _sq_points(cx, cy, a, s)
            px, py = pts[k]
            return min(px, 1-px, py, 1-py)
        return f

    for i in range(m):
        for k in range(4):
            cons.append({'type': 'ineq', 'fun': make_contain(i, k)})

    # pairwise non-overlap
    def make_pair(i, j):
        def f(x):
            cx1, cy1, a1, s1 = x[i*4], x[i*4+1], x[i*4+2], x[i*4+3]
            cx2, cy2, a2, s2 = x[j*4], x[j*4+1], x[j*4+2], x[j*4+3]
            if s1 <= 1e-12 or s2 <= 1e-12:
                return 1.0
            return _pair_gap(cx1, cy1, a1, s1, cx2, cy2, a2, s2)
        return f

    for i in range(m):
        for j in range(i+1, m):
            cons.append({'type': 'ineq', 'fun': make_pair(i, j)})

    # SLSQP
    try:
        res = minimize(obj, x0, method='SLSQP', bounds=bounds,
                       constraints=cons, options={'maxiter': maxiter, 'ftol': 1e-10,
                                                  'disp': False})
        if res.success or res.fun < obj(x0):
            xs = res.x
        else:
            xs = x0
    except Exception:
        xs = x0

    # unpack back
    new_sqs = [list(s) for s in sqs]
    for k, i in enumerate(idx):
        new_sqs[i][0] = xs[k*4]
        new_sqs[i][1] = xs[k*4+1]
        new_sqs[i][2] = xs[k*4+2] % 1.0
        new_sqs[i][3] = max(0.0, xs[k*4+3])
    # Clip tiny negatives
    for s in new_sqs:
        if s[3] < 0:
            s[3] = 0.0
    return new_sqs

def _postprocess(sqs):
    """Ensure all coordinates in [0,1] and no gross overlaps; shrink if needed."""
    sqs = [list(s) for s in sqs]
    for s in sqs:
        s[0] = min(1.0, max(0.0, s[0]))
        s[1] = min(1.0, max(0.0, s[1]))
        s[2] = s[2] % 1.0
        s[3] = min(1.0, max(0.0, s[3]))
    # Verify containment and shrink if outside
    for i, (cx, cy, a, s) in enumerate(sqs):
        if s <= 0:
            continue
        pts = _sq_points(cx, cy, a, s)
        minx = min(p[0] for p in pts)
        maxx = max(p[0] for p in pts)
        miny = min(p[1] for p in pts)
        maxy = max(p[1] for p in pts)
        if minx < 0 or maxx > 1 or miny < 0 or maxy > 1:
            # scale down about centre until inside
            scale = 1.0
            if maxx - minx > 0:
                scale = min(scale, 1.0/max(maxx-minx, 1e-9))
            if maxy - miny > 0:
                scale = min(scale, 1.0/max(maxy-miny, 1e-9))
            # also shift center to fit
            new_s = s * scale
            # try to keep center
            pts = _sq_points(cx, cy, a, new_s)
            minx = min(p[0] for p in pts)
            maxx = max(p[0] for p in pts)
            miny = min(p[1] for p in pts)
            maxy = max(p[1] for p in pts)
            if minx < 0:
                cx -= minx
            if maxx > 1:
                cx -= (maxx - 1)
            if miny < 0:
                cy -= miny
            if maxy > 1:
                cy -= (maxy - 1)
            sqs[i] = [cx, cy, a, new_s]

    # Remove overlaps by shrinking smaller squares
    changed = True
    iters = 0
    while changed and iters < 200:
        changed = False
        iters += 1
        for i in range(len(sqs)):
            for j in range(i+1, len(sqs)):
                cx1, cy1, a1, s1 = sqs[i]
                cx2, cy2, a2, s2 = sqs[j]
                if s1 <= 1e-12 or s2 <= 1e-12:
                    continue
                gap = _pair_gap(cx1, cy1, a1, s1, cx2, cy2, a2, s2)
                if gap < -1e-9:
                    # shrink smaller square proportionally
                    if s1 <= s2:
                        factor = max(0.0, 1.0 + gap / max(s1, 1e-9))
                        sqs[i][3] *= (factor * 0.999)
                    else:
                        factor = max(0.0, 1.0 + gap / max(s2, 1e-9))
                        sqs[j][3] *= (factor * 0.999)
                    changed = True
    return sqs

# ----------------------------- main solver -----------------------------

def solve(n):
    if n <= 0:
        return []
    if n == 1:
        return [(0.5, 0.5, 0.0, 1.0)]

    # 1) Get initial layout
    sqs = _initial_layout(n)

    # 2) Refine using local optimization
    best_sqs = sqs
    best_val = sum(s for _, _, _, s in sqs)

    # Try a few restarts with slight perturbations to avoid local minima
    import random
    random.seed(12345)

    trials = 3 if n <= 200 else 2
    for t in range(trials):
        if t == 0:
            cur = [list(s) for s in sqs]
        else:
            # perturb
            cur = [list(s) for s in sqs]
            scale = 0.02 * (1.0 + t)
            for s in cur:
                if s[3] > 1e-9:
                    s[0] += random.uniform(-scale, scale)
                    s[1] += random.uniform(-scale, scale)
                    s[0] = min(1.0, max(0.0, s[0]))
                    s[1] = min(1.0, max(0.0, s[1]))
                    s[2] += random.uniform(-0.1, 0.1)
                    s[2] %= 1.0
            cur = _postprocess(cur)  # fix overlaps from perturbation
        refined = _refine(cur, n, maxiter=100 if n <= 50 else 50)
        refined = _postprocess(refined)
        val = sum(s for _, _, _, s in refined)
        if val > best_val:
            best_val = val
            best_sqs = refined

    # 3) Try to improve by adding small squares / adjusting
    final = _postprocess(best_sqs)

    # Ensure exactly n squares (pad with zero-size if needed)
    while len(final) < n:
        final.append([0.5, 0.5, 0.0, 0.0])
    final = final[:n]

    # Convert angles to [0,1)
    for s in final:
        s[2] = s[2] % 1.0

    return [tuple(s) for s in final]
