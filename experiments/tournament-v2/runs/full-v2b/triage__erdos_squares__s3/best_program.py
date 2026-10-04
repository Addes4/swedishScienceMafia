import math
import random
import numpy as np

def _to_poly(center, angle, side):
    """Return 4 corner points of square."""
    cx, cy = center
    d = side / 2.0
    corners = np.array([[-d, -d], [d, -d], [d, d], [-d, d]])
    c = math.cos(angle * 2.0 * math.pi)
    s = math.sin(angle * 2.0 * math.pi)
    rot = np.array([[c, -s], [s, c]])
    return corners @ rot.T + np.array([cx, cy])

def _poly_intersect(poly1, poly2):
    """Check if two convex polygons overlap (strict interior intersection)."""
    for poly in (poly1, poly2):
        n = len(poly)
        for i in range(n):
            p1 = poly[i]
            p2 = poly[(i+1) % n]
            edge = p2 - p1
            normal = np.array([-edge[1], edge[0]])
            proj1 = poly1 @ normal
            proj2 = poly2 @ normal
            if proj1.max() <= proj2.min() + 1e-9 or proj2.max() <= proj1.min() + 1e-9:
                return False
    return True

def _poly_inside_unit(poly):
    return np.all((poly >= -1e-9) & (poly <= 1+1e-9))

def _feasible(squares):
    polys = []
    for (cx, cy, ang, s) in squares:
        if s < 0:
            return False
        if s == 0:
            continue
        poly = _to_poly((cx, cy), ang, s)
        if not _poly_inside_unit(poly):
            return False
        polys.append(poly)
    for i in range(len(polys)):
        for j in range(i+1, len(polys)):
            if _poly_intersect(polys[i], polys[j]):
                return False
    return True

def _partial_feasible(squares):
    """Check each square inside unit and store polygons; return list or None."""
    polys = []
    for (cx, cy, ang, s) in squares:
        if s < 0 or s > 1.0 + 1e-9:
            return None
        if s == 0:
            polys.append(None)
            continue
        poly = _to_poly((cx, cy), ang, s)
        if not _poly_inside_unit(poly):
            return None
        polys.append(poly)
    return polys

def _can_place(polys_list, new_poly):
    """Check if new_poly doesn't intersect any in polys_list."""
    for p in polys_list:
        if p is None:
            continue
        if _poly_intersect(p, new_poly):
            return False
    return True

def _largest_square_at(pos, angle, polys, xmin=0.0, xmax=1.0, ymin=0.0, ymax=1.0):
    """Binary search for largest square at (pos, angle) that fits and doesn't overlap."""
    cx, cy = pos
    # upper bound from container
    c = math.cos(angle * 2.0 * math.pi)
    s = math.sin(angle * 2.0 * math.pi)
    halfdiag = math.sqrt(2) / 2.0
    # max radius from container
    dx = min(cx - xmin, xmax - cx)
    dy = min(cy - ymin, ymax - cy)
    hi = 2.0 * min(dx, dy) / math.sqrt(2)
    if hi <= 0:
        return 0.0
    # subtract from other squares
    for p in polys:
        if p is None:
            continue
        # min distance from pos to polygon
        d = _point_poly_distance((cx, cy), p)
        # the square has half-diagonal radius s*sqrt(2)/2, plus rotated
        # approximate constraint
        val = (d / halfdiag) if d > 0 else 0.0
        if val < hi:
            hi = val
    if hi <= 0:
        return 0.0
    lo = 0.0
    for _ in range(20):
        mid = (lo + hi) / 2.0
        if mid < 1e-12:
            lo = mid
            continue
        poly_new = _to_poly((cx, cy), angle, mid)
        if not _poly_inside_unit(poly_new):
            hi = mid
            continue
        ok = True
        for p in polys:
            if p is None:
                continue
            if _poly_intersect(poly_new, p):
                ok = False
                break
        if ok:
            lo = mid
        else:
            hi = mid
    return lo

def _point_poly_distance(pt, poly):
    """Min distance from point to convex polygon boundary or 0 if inside."""
    px, py = pt
    n = len(poly)
    # check inside
    inside = True
    for i in range(n):
        a = poly[i]
        b = poly[(i+1) % n]
        cross = (b[0]-a[0])*(py-a[1]) - (b[1]-a[1])*(px-a[0])
        if cross < -1e-9:
            inside = False
            break
    if inside:
        return 0.0
    best = float('inf')
    for i in range(n):
        a = poly[i]
        b = poly[(i+1) % n]
        best = min(best, _pt_seg_dist(pt, a, b))
    return best

def _pt_seg_dist(p, a, b):
    ab = b - a
    t = np.dot(p - a, ab) / (np.dot(ab, ab) + 1e-12)
    t = max(0.0, min(1.0, t))
    proj = a + t * ab
    return np.hypot(p[0]-proj[0], p[1]-proj[1])

def _greedy_slice(n, seed=0):
    """Greedily place squares: at each step find the largest possible square."""
    rng = random.Random(seed)
    squares = []
    polys = []
    for step in range(n):
        # candidate centers and angles
        best_side = -1.0
        best_sq = (0.5, 0.5, 0.0, 0.0)
        # candidate positions: grid + perturbations
        candidates = []
        G = 8
        for ix in range(G+1):
            for iy in range(G+1):
                candidates.append((ix/G, iy/G))
        # add existing square corners/edges as candidates
        for p in polys:
            if p is None:
                continue
            for pt in p:
                candidates.append((float(pt[0]), float(pt[1])))
        # add random candidates
        for _ in range(20):
            candidates.append((rng.random(), rng.random()))
        angles = [0.0, 0.25, 0.125, 0.375, 0.0625, 0.1875]
        for (cx, cy) in candidates:
            for ang in angles:
                s = _largest_square_at((cx, cy), ang, polys)
                if s > best_side:
                    best_side = s
                    best_sq = (cx, cy, ang, s)
        if best_side <= 1e-9:
            squares.append((0.5, 0.5, 0.0, 0.0))
            polys.append(None)
        else:
            squares.append(best_sq)
            polys.append(_to_poly((best_sq[0], best_sq[1]), best_sq[2], best_sq[3]))
    return squares

def _try_grow(squares, idx, amount, polys=None):
    """Try to grow square idx by tower amount, return new square or None."""
    cx, cy, ang, s = squares[idx]
    new_s = s + amount
    if new_s > 1.0:
        return None
    poly_new = _to_poly((cx, cy), ang, new_s)
    if not _poly_inside_unit(poly_new):
        return None
    others = [_to_poly((x[0], x[1]), x[2], x[3]) if x[3] > 0 else None
              for k, x in enumerate(squares) if k != idx]
    for p in others:
        if p is None:
            continue
        if _poly_intersect(poly_new, p):
            return None
    return (cx, cy, ang, new_s)

def _local_search(squares, iters=2000, seed=0):
    """Monte Carlo search: perturb centers/angles/sizes."""
    rng = random.Random(seed)
    squares = [list(s) for s in squares]
    cur_sum = sum(s[3] for s in squares)
    best = [list(s) for s in squares]
    best_sum = cur_sum
    n = len(squares)
    temp = 0.05
    for it in range(iters):
        idx = rng.randrange(n)
        old = list(squares[idx])
        # random perturbation
        dx = rng.gauss(0, 0.03)
        dy = rng.gauss(0, 0.03)
        da = rng.gauss(0, 0.03)
        ds = rng.gauss(0, 0.03)
        np_sq = (old[0]+dx, old[1]+dy, (old[2]+da) % 1.0, max(0.0, old[3]+ds))
        # check validity
        if not _square_valid(squares, idx, np_sq):
            continue
        old_contrib = old[3]
        new_contrib = np_sq[3]
        delta = new_contrib - old_contrib
        if delta > 0 or rng.random() < math.exp(delta / max(temp, 1e-6)):
            squares[idx] = list(np_sq)
            cur_sum += delta
            if cur_sum > best_sum:
                best_sum = cur_sum
                best = [list(s) for s in squares]
        temp *= 0.9997
        temp = max(temp, 0.001)
    return [(s[0], s[1], s[2], s[3]) for s in best]

def _square_valid(squares, changed_idx, new_sq):
    """Check new square valid against all others and container."""
    cx, cy, ang, s = new_sq
    if s < 0:
        return False
    if s == 0:
        # any position in unit square ok
        return 0 <= cx <= 1 and 0 <= cy <= 1
    poly_new = _to_poly((cx, cy), ang, s)
    if not _poly_inside_unit(poly_new):
        return False
    for k, sq in enumerate(squares):
        if k == changed_idx:
            continue
        if sq[3] <= 0:
            continue
        poly_k = _to_poly((sq[0], sq[1]), sq[2], sq[3])
        if _poly_intersect(poly_new, poly_k):
            return False
    return True

def _grow_all(squares, rounds=20):
    """Try to grow each square a little, repeatedly."""
    squares = [list(s) for s in squares]
    for r in range(rounds):
        improved = False
        for idx in range(len(squares)):
            s = squares[idx][3]
            if s <= 0:
                # try placing a small square
                best_pos = None
                best_s = 0.0
                polys = [None if squares[k][3] <= 0 else _to_poly((squares[k][0], squares[k][1]), squares[k][2], squares[k][3])
                         for k in range(len(squares)) if k != idx]
                for _ in range(50):
                    cx = random.random()
                    cy = random.random()
                    for ang in [0.0, 0.25, 0.125]:
                        s = _largest_square_at((cx, cy), ang, polys)
                        if s > best_s:
                            best_s = s
                            best_pos = (cx, cy, ang, s)
                if best_s > 1e-6:
                    squares[idx] = list(best_pos)
                    improved = True
                continue
            # try grow
            for amount in [0.01, 0.005, 0.002, 0.001]:
                new_sq = _try_grow(squares, idx, amount)
                if new_sq is not None:
                    squares[idx] = list(new_sq)
                    improved = True
                    break
        if not improved:
            break
    return [(s[0], s[1], s[2], s[3]) for s in squares]

def _staircase(n):
    """Known optimal for triangular numbers."""
    k = 1
    while k*(k+1)//2 <= n:
        k += 1
    k -= 1
    Tk = k*(k+1)//2
    side = 1.0 / k
    squares = []
    for i in range(k):
        for j in range(k - i):
            cx = j*side + side/2
            cy = i*side + side/2
            squares.append((cx, cy, 0.0, side))
    if n > Tk:
        squares += [(0.5, 0.5, 0.0, 0.0)] * (n - Tk)
    return squares[:n]

def _grid_solution(n, k):
    """Grid of k x k squares (n <= k*k)."""
    side = 1.0 / k
    squares = []
    for i in range(k):
        for j in range(k):
            if len(squares) >= n:
                break
            squares.append(((i+0.5)*side, (j+0.5)*side, 0.0, side))
    return squares[:n]

def solve(n):
    if n <= 0:
        return []
    if n <= 4:
        # grid optimum
        k = int(math.isqrt(n))
        if k == 0:
            return [(0.5, 0.5, 0.0, 0.0)]
        # for n=3 we can have 3 squares of side 0.5 in 2x2 grid minus one -> side 0.5 each
        # Wait n=3: 3 squares side 0.5 in 2x2 grid works. 
        squares = []
        for i in range(k):
            for j in range(k):
                squares.append(((i+0.5)/k, (j+0.5)/k, 0.0, 1.0/k))
        if len(squares) >= n:
            return squares[:n]
        # try larger grid arrangement
        # for n=3, k=1 gives 1 square, need better
        # use larger squares approach: 3 squares of 0.5
        if n == 3:
            return [(0.25,0.25,0.0,0.5),(0.75,0.25,0.0,0.5),(0.25,0.75,0.0,0.5)]
        return squares[:n]

    # candidate initial solutions
    candidates = []
    # staircase
    candidates.append(_staircase(n))
    # grid with k+1 where k^2 >= n
    k = math.ceil(math.sqrt(n))
    candidates.append(_grid_solution(n, k))

    # greedy slice with multiple seeds
    for seed in range(3):
        candidates.append(_greedy_slice(n, seed=seed))

    results = []
    for cand in candidates:
        if len(cand) != n:
            continue
        # grow
        grown = _grow_all(cand, rounds=15)
        # local search
        best = grown
        best_sum = sum(s[3] for s in best)
        for seed in range(2):
            ls = _local_search(best, iters=1500, seed=seed)
            ls_sum = sum(s[3] for s in ls)
            if ls_sum > best_sum and _feasible(ls):
                best = ls
                best_sum = ls_sum
        # grow again
        grown2 = _grow_all(best, rounds=10)
        g2sum = sum(s[3] for s in grown2)
        if g2sum > best_sum and _feasible(grown2):
            best = grown2
            best_sum = g2sum
        if _feasible(best):
            results.append((best_sum, best))

    if not results:
        # fallback
        return _staircase(n)

    results.sort(key=lambda x: -x[0])
    best_sum, best = results[0]

    # final refinement: multiple local searches
    for seed in range(3):
        ls = _local_search(best, iters=2000, seed=seed+100)
        ls_sum = sum(s[3] for s in ls)
        if ls_sum > best_sum and _feasible(ls):
            best = ls
            best_sum = ls_sum
    best = _grow_all(best, rounds=10)
    if not _feasible(best):
        best = results[0][1]

    # ensure n entries
    best = list(best)[:n]
    while len(best) < n:
        best.append((0.5, 0.5, 0.0, 0.0))

    # final safety: verify and fix if needed - if invalid, fallback
    if not _feasible(best):
        # try staircase
        sc = _staircase(n)
        if _feasible(sc):
            return sc
        # shrink all
        best = [(cx, cy, ang, s*0.99) for (cx, cy, ang, s) in best]
    return best
