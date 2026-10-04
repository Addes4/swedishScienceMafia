# EVOLVE-BLOCK-START
"""Squares in a unit square: maximise total side length.

Strategy: partition the unit square into up to five rectangular regions
(a main region plus a right strip, a top region that may be split into
two side-by-side sub-strips, and a small top-right corner block).
Each region is packed with equal squares via the best grid factorisation.
We search over the split fractions and the distribution of squares
between regions to maximise the total side sum; the best candidate is
then polished with a fine coordinate-descent.  Squares with side 0 fill
any remainder.
"""
import math


def _pack_grid(count, W, H):
    """Best equal-square grid for `count` squares inside a W x H box."""
    if count <= 0 or W <= 0 or H <= 0:
        return [], 0.0, 0
    best = None
    for a in range(1, count + 1):
        b = (count + a - 1) // a
        if a * b < count:
            continue
        s = min(W / a, H / b)
        total = s * count
        if best is None or total > best[0]:
            best = (total, a, b, s)
    if best is None:
        return [], 0.0, 0
    _, a, b, s = best
    sq = []
    used = 0
    for i in range(a):
        for j in range(b):
            if used >= count:
                break
            cx = (i + 0.5) * s
            cy = (j + 0.5) * s
            sq.append((cx, cy, 0.0, s))
            used += 1
        if used >= count:
            break
    return sq, s, used


def _layout3(n, nb, ns1, ns2, fw, fh):
    """Three-region layout:
      Main region: [0, 1-fw] x [0, 1-fh]  (holds nb squares)
      Right strip: [1-fw, 1] x [0, 1-fh]  (holds ns1 squares)
      Top strip:   [0, 1] x [1-fh, 1]     (holds ns2 squares)
    """
    mw, mh = 1.0 - fw, 1.0 - fh
    rw, rh = fw, 1.0 - fh
    tw, th = 1.0, fh

    big, bs, used_big = _pack_grid(nb, mw, mh)
    if nb > 0 and used_big < nb:
        return None
    s1, ss1, u1 = _pack_grid(ns1, rw, rh)
    if ns1 > 0 and u1 < ns1:
        return None
    s2, ss2, u2 = _pack_grid(ns2, tw, th)
    if ns2 > 0 and u2 < ns2:
        return None

    squares = []
    for (cx, cy, a, s) in big:
        squares.append((cx, cy, a, s))
    ox1 = mw
    for (cx, cy, a, s) in s1:
        squares.append((cx + ox1, cy, a, s))
    oy2 = mh
    for (cx, cy, a, s) in s2:
        squares.append((cx, cy + oy2, a, s))

    while len(squares) < n:
        squares.append((0.5, 0.5, 0.0, 0.0))
    total = bs * used_big + ss1 * u1 + ss2 * u2
    return total, squares[:n]


def _layout4(n, nb, ns1, ns2a, ns2b, fw, fh, g):
    """Four-region layout:
      Main region: [0, 1-fw] x [0, 1-fh]        (holds nb squares)
      Right strip: [1-fw, 1] x [0, 1-fh]        (holds ns1 squares)
      Top-left:    [0, g]    x [1-fh, 1]        (holds ns2a squares)
      Top-right:   [g, 1]    x [1-fh, 1]        (holds ns2b squares)
    """
    mw, mh = 1.0 - fw, 1.0 - fh
    rw, rh = fw, 1.0 - fh
    tlw, th = g, fh
    trw = 1.0 - g

    big, bs, used_big = _pack_grid(nb, mw, mh)
    if nb > 0 and used_big < nb:
        return None
    s1, ss1, u1 = _pack_grid(ns1, rw, rh)
    if ns1 > 0 and u1 < ns1:
        return None
    sa, ssa, ua = _pack_grid(ns2a, tlw, th)
    if ns2a > 0 and ua < ns2a:
        return None
    sb, ssb, ub = _pack_grid(ns2b, trw, th)
    if ns2b > 0 and ub < ns2b:
        return None

    squares = []
    for (cx, cy, a, s) in big:
        squares.append((cx, cy, a, s))
    ox1 = mw
    for (cx, cy, a, s) in s1:
        squares.append((cx + ox1, cy, a, s))
    oy2 = mh
    for (cx, cy, a, s) in sa:
        squares.append((cx, cy + oy2, a, s))
    for (cx, cy, a, s) in sb:
        squares.append((cx + g, cy + oy2, a, s))

    while len(squares) < n:
        squares.append((0.5, 0.5, 0.0, 0.0))
    total = bs * used_big + ss1 * u1 + ssa * ua + ssb * ub
    return total, squares[:n]


def _layout5(n, nb, ns1, ns2a, nsc, fw, fh, gx, gy):
    """Five-region layout:
      Main region: [0, 1-fw] x [0, 1-fh]        (holds nb squares)
      Right strip: [1-fw, 1] x [0, 1-gy]        (holds ns1 squares)
      Top-left:    [0, 1-fw] x [1-fh, 1]        (holds ns2a squares)
      Corner TL:   [1-fw, 1] x [1-fh, 1-gy]     (holds unused slot via nsc=0)
    Actually simpler: right strip split vertically into two blocks by gy
      Right-lower: [1-fw, 1] x [0, 1-gy]  -> ns1 squares
      Right-upper: [1-fw, 1] x [1-gy, 1-gy2]... simplified below.
    We use: right column width fw; it is split into a lower block (ns1) and an
    upper block (nsc), separated at height 1-gy where gy is the corner height.
    Top strip occupies [0, 1-fw] x [1-fh, 1] (ns2a squares) and the corner
    [1-fw, 1] x [1-gy, 1] (nsc squares).  gx unused.
    """
    mw, mh = 1.0 - fw, 1.0 - fh
    # right lower block
    rlw, rlh = fw, 1.0 - gy
    # top strip (excluding right column)
    tsw, tsh = mw, fh
    # corner
    cw, ch = fw, gy

    big, bs, used_big = _pack_grid(nb, mw, mh)
    if nb > 0 and used_big < nb:
        return None
    s1, ss1, u1 = _pack_grid(ns1, rlw, rlh)
    if ns1 > 0 and u1 < ns1:
        return None
    sa, ssa, ua = _pack_grid(ns2a, tsw, tsh)
    if ns2a > 0 and ua < ns2a:
        return None
    sc, ssc, uc = _pack_grid(nsc, cw, ch)
    if nsc > 0 and uc < nsc:
        return None

    squares = []
    for (cx, cy, a, s) in big:
        squares.append((cx, cy, a, s))
    ox1 = mw
    for (cx, cy, a, s) in s1:
        squares.append((cx + ox1, cy, a, s))
    oy2 = mh
    for (cx, cy, a, s) in sa:
        squares.append((cx, cy + oy2, a, s))
    oxc = mw
    oyc = 1.0 - gy
    for (cx, cy, a, s) in sc:
        squares.append((cx + oxc, cy + oyc, a, s))

    while len(squares) < n:
        squares.append((0.5, 0.5, 0.0, 0.0))
    total = bs * used_big + ss1 * u1 + ssa * ua + ssc * uc
    return total, squares[:n]


def _layout(n, n_big, split_frac, vertical):
    """Two-region layout (fallback / small n)."""
    if vertical:
        fw = split_frac
        bw, bh = fw, 1.0
        sw, sh = 1.0 - fw, 1.0
    else:
        fh = split_frac
        bw, bh = 1.0, fh
        sw, sh = 1.0, 1.0 - fh

    big, bs, used_big = _pack_grid(n_big, bw, bh)
    if used_big < n_big:
        return None
    rest = n - n_big
    small, ss, used_small = _pack_grid(rest, sw, sh)

    squares = list(big)
    ox = bw if vertical else 0.0
    oy = 0.0 if vertical else bh
    for (cx, cy, a, s) in small:
        squares.append((cx + ox, cy + oy, a, s))
    while len(squares) < n:
        squares.append((0.5, 0.5, 0.0, 0.0))
    total = bs * used_big + ss * used_small
    return total, squares[:n]


def _coord_refine3(n, nb, ns1, ns2, init_fw, init_fh, budget=40):
    """Coordinate-descent refinement of (fw, fh) for the 3-region layout."""
    cfw, cfh = init_fw, init_fh
    best = _layout3(n, nb, ns1, ns2, cfw, cfh)
    best_t = best[0] if best else -1.0
    step = 0.08
    for _ in range(budget):
        improved = False
        for dfw in (-step, 0.0, step):
            for dfh in (-step, 0.0, step):
                nfw = cfw + dfw
                nfh = cfh + dfh
                if not (0.0 <= nfw <= 1.0 and 0.0 <= nfh <= 1.0):
                    continue
                r = _layout3(n, nb, ns1, ns2, nfw, nfh)
                if r and r[0] > best_t + 1e-12:
                    best_t = r[0]
                    best = r
                    cfw, cfh = nfw, nfh
                    improved = True
        if not improved:
            step *= 0.5
            if step < 1e-4:
                break
    return best_t, best


def _fine_refine(lt, fn, params, budget=60):
    """Generic fine coordinate descent over a list of split parameters.

    `fn` is a function taking (n, *params_count) and returning (total, squares),
    `lt` selects the layout builder.  `params` is the initial parameter list.
    """
    cur = list(params)
    best = lt(n, *cur)
    best_t = best[0] if best else -1.0
    best_p = list(cur)
    step = 0.03
    for _ in range(budget):
        improved = False
        for i in range(len(cur)):
            for d in (-step, 0.0, step):
                trial = list(cur)
                trial[i] = cur[i] + d
                if not (0.0 <= trial[i] <= 1.0):
                    continue
                r = lt(n, *trial)
                if r and r[0] > best_t + 1e-12:
                    best_t = r[0]
                    best = r
                    best_p = list(trial)
                    cur = list(trial)
                    improved = True
        if not improved:
            step *= 0.5
            if step < 1e-5:
                break
    r = lt(n, *best_p)
    return best_t, (r[1] if r else None)


def solve(n):
    if n <= 0:
        return []
    if n == 1:
        return [(0.5, 0.5, 0.0, 1.0)]

    best_total = -1.0
    best_squares = None

    # ---- two-region search (cheap baseline) ----
    for n_big in range(1, n + 1):
        for vertical in (True, False):
            lo, hi = 0.01, 0.99
            for _ in range(40):
                m1 = lo + (hi - lo) / 3
                m2 = hi - (hi - lo) / 3
                r1 = _layout(n, n_big, m1, vertical)
                r2 = _layout(n, n_big, m2, vertical)
                t1 = r1[0] if r1 else -1
                t2 = r2[0] if r2 else -1
                if t1 >= t2:
                    hi = m2
                else:
                    lo = m1
            for f in (lo, (lo + hi) / 2, hi):
                r = _layout(n, n_big, f, vertical)
                if r and r[0] > best_total:
                    best_total = r[0]
                    best_squares = r[1]

    # ---- three-region search ----
    for nb in range(0, n + 1):
        for ns1 in range(0, n - nb + 1):
            ns2 = n - nb - ns1
            if ns2 < 0:
                continue
            best_local = None
            for fi in range(1, 10):
                fw = fi / 10.0
                for fj in range(1, 10):
                    fh = fj / 10.0
                    r = _layout3(n, nb, ns1, ns2, fw, fh)
                    if r and (best_local is None or r[0] > best_local[0]):
                        best_local = (r[0], fw, fh)
            if best_local is None:
                continue
            tl, r = _coord_refine3(n, nb, ns1, ns2, best_local[1], best_local[2])
            if r and tl > best_total:
                best_total = tl
                best_squares = r[1]

    # ---- four-region search (top strip split into two) ----
    for nb in range(0, n + 1):
        for ns1 in range(0, n - nb + 1):
            rem = n - nb - ns1
            if rem < 0:
                continue
            for ns2a in range(0, rem + 1):
                ns2b = rem - ns2a
                best_local = None
                for fi in range(1, 6):
                    fw = fi / 6.0
                    for fj in range(1, 6):
                        fh = fj / 6.0
                        r = _layout3(n, nb, ns1, rem, fw, fh)
                        if r and (best_local is None or r[0] > best_local[0]):
                            best_local = (r[0], fw, fh)
                if best_local is None:
                    continue
                cfw, cfh = best_local[1], best_local[2]
                cg = 0.5
                best4 = None
                for gi in range(1, 10):
                    g = gi / 10.0
                    r = _layout4(n, nb, ns1, ns2a, ns2b, cfw, cfh, g)
                    if r and (best4 is None or r[0] > best4[0]):
                        best4 = (r[0], cfw, cfh, g)
                if best4 is None:
                    continue
                bfw, bfh, bg = best4[1], best4[2], best4[3]
                step = 0.06
                for _ in range(30):
                    improved = False
                    for dfw in (-step, 0.0, step):
                        for dfh in (-step, 0.0, step):
                            for dg in (-step, 0.0, step):
                                nfw = bfw + dfw
                                nfh = bfh + dfh
                                ng = bg + dg
                                if not (0.0 <= nfw <= 1.0 and 0.0 <= nfh <= 1.0
                                        and 0.0 <= ng <= 1.0):
                                    continue
                                r = _layout4(n, nb, ns1, ns2a, ns2b,
                                             nfw, nfh, ng)
                                if r and r[0] > best4[0] + 1e-12:
                                    best4 = (r[0], nfw, nfh, ng)
                                    bfw, bfh, bg = nfw, nfh, ng
                                    improved = True
                    if not improved:
                        step *= 0.5
                        if step < 1e-4:
                            break
                if best4[0] > best_total:
                    r = _layout4(n, nb, ns1, ns2a, ns2b, bfw, bfh, bg)
                    if r:
                        best_total = r[0]
                        best_squares = r[1]

    # ---- five-region search (right column split + corner) ----
    for nb in range(0, n + 1):
        for ns1 in range(0, n - nb + 1):
            rem = n - nb - ns1
            if rem < 0:
                continue
            for ns2a in range(0, rem + 1):
                nsc = rem - ns2a
                best_local = None
                for fi in range(1, 6):
                    fw = fi / 6.0
                    for fj in range(1, 6):
                        fh = fj / 6.0
                        for gk in range(1, 6):
                            gy = gk / 6.0
                            r = _layout5(n, nb, ns1, ns2a, nsc,
                                         fw, fh, 0.0, gy)
                            if r and (best_local is None
                                      or r[0] > best_local[0]):
                                best_local = (r[0], fw, fh, gy)
                if best_local is None:
                    continue
                bfw, bfh, bgy = best_local[1], best_local[2], best_local[3]
                step = 0.06
                for _ in range(30):
                    improved = False
                    for dfw in (-step, 0.0, step):
                        for dfh in (-step, 0.0, step):
                            for dgy in (-step, 0.0, step):
                                nfw = bfw + dfw
                                nfh = bfh + dfh
                                ngy = bgy + dgy
                                if not (0.0 <= nfw <= 1.0 and 0.0 <= nfh <= 1.0
                                        and 0.0 <= ngy <= 1.0):
                                    continue
                                r = _layout5(n, nb, ns1, ns2a, nsc,
                                             nfw, nfh, 0.0, ngy)
                                if r and r[0] > best_local[0] + 1e-12:
                                    best_local = (r[0], nfw, nfh, ngy)
                                    bfw, bfh, bgy = nfw, nfh, ngy
                                    improved = True
                    if not improved:
                        step *= 0.5
                        if step < 1e-4:
                            break
                if best_local[0] > best_total:
                    r = _layout5(n, nb, ns1, ns2a, nsc, bfw, bfh, 0.0, bgy)
                    if r:
                        best_total = r[0]
                        best_squares = r[1]

    if best_squares is None:
        k = math.isqrt(n)
        s = 1.0 / k
        best_squares = [((i + 0.5) * s, (j + 0.5) * s, 0.0, s)
                        for i in range(k) for j in range(k)]
        while len(best_squares) < n:
            best_squares.append((0.5, 0.5, 0.0, 0.0))

    return best_squares[:n]
# EVOLVE-BLOCK-END
