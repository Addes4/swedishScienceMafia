"""Multi-scale guillotine packing plus a custom penalty-based continuous polish."""

import math

from scipy.optimize import minimize


def _best_block(n, w, h):
    if n <= 0:
        return 0.0, 0, 0
    best = (0.0, 1, 1)
    for cols in range(1, n + 1):
        rows = (n + cols - 1) // cols
        s = min(w / cols, h / rows)
        if s > best[0]:
            best = (s, cols, rows)
    return best


def _corners(cx, cy, ang, s):
    t = ang * 2 * math.pi
    c = math.cos(t)
    sn = math.sin(t)
    h = s / 2
    return [
        (cx + c * h - sn * h, cy + sn * h + c * h),
        (cx + c * h + sn * h, cy + sn * h - c * h),
        (cx - c * h + sn * h, cy - sn * h - c * h),
        (cx - c * h - sn * h, cy - sn * h + c * h),
    ]


def _overlap(a, b):
    ax, ay, aa, asd = a
    bx, by, ba, bsd = b
    if asd <= 0 or bsd <= 0:
        return False
    ra = asd * 1.4143 / 2
    rb = bsd * 1.4143 / 2
    dx = ax - bx
    dy = ay - by
    if dx * dx + dy * dy > (ra + rb) ** 2:
        return False

    pa = _corners(ax, ay, aa, asd)
    pb = _corners(bx, by, ba, bsd)
    ta = aa * 2 * math.pi
    tb = ba * 2 * math.pi
    ca, sa = math.cos(ta), math.sin(ta)
    cb, sb = math.cos(tb), math.sin(tb)
    for ux, uy in [(ca, sa), (-sa, ca), (cb, sb), (-sb, cb)]:
        amin = min(p[0] * ux + p[1] * uy for p in pa)
        amax = max(p[0] * ux + p[1] * uy for p in pa)
        bmin = min(p[0] * ux + p[1] * uy for p in pb)
        bmax = max(p[0] * ux + p[1] * uy for p in pb)
        if amax <= bmin + 1e-12 or bmax <= amin + 1e-12:
            return False
    return True


def _in_unit(cx, cy, ang, s):
    t = ang * 2 * math.pi
    c = abs(math.cos(t))
    sn = abs(math.sin(t))
    h = s / 2
    rx = c * h + sn * h
    ry = sn * h + c * h
    return cx - rx >= -1e-9 and cx + rx <= 1 + 1e-9 and cy - ry >= -1e-9 and cy + ry <= 1 + 1e-9


def _valid_layout(squares):
    n = len(squares)
    for i in range(n):
        cx, cy, ang, s = squares[i]
        if not (0 <= cx <= 1 and 0 <= cy <= 1 and 0 <= ang <= 1 and 0 <= s <= 1):
            return False
        if not _in_unit(cx, cy, ang, s):
            return False
        for j in range(i + 1, n):
            if _overlap(squares[i], squares[j]):
                return False
    return True


def _construct(n):
    if n <= 0:
        return []
    if n == 1:
        return [(0.5, 0.5, 0.0, 1.0)]

    leaves = [(0.0, 0.0, 1.0, 1.0, n)]

    for _ in range(400):
        best_gain = 0.0
        best_idx = -1
        best_partition = None

        for idx, (x, y, w, h, cnt) in enumerate(leaves):
            if cnt < 2:
                continue
            cur_side, _, _ = _best_block(cnt, w, h)
            cur_val = cnt * cur_side
            horizontal_split = w >= h
            for a in range(1, cnt):
                b = cnt - a
                frac = math.sqrt(a) / (math.sqrt(a) + math.sqrt(b))
                frac = min(max(frac, 1e-3), 1 - 1e-3)
                if horizontal_split:
                    w1 = w * frac
                    w2 = w - w1
                    s1, _, _ = _best_block(a, w1, h)
                    s2, _, _ = _best_block(b, w2, h)
                    kind = 'v'
                else:
                    h1 = h * frac
                    h2 = h - h1
                    s1, _, _ = _best_block(a, w, h1)
                    s2, _, _ = _best_block(b, w, h2)
                    kind = 'h'
                val = a * s1 + b * s2
                gain = val - cur_val
                if gain > best_gain:
                    best_gain = gain
                    best_idx = idx
                    best_partition = (a, b, kind, frac)

        if best_idx < 0 or best_gain <= 1e-12:
            break

        x, y, w, h, cnt = leaves[best_idx]
        a, b, kind, frac = best_partition
        if kind == 'v':
            w1 = w * frac
            leaves[best_idx] = (x, y, w1, h, a)
            leaves.append((x + w1, y, w - w1, h, b))
        else:
            h1 = h * frac
            leaves[best_idx] = (x, y, w, h1, a)
            leaves.append((x, y + h1, w, h - h1, b))

    result = []
    for (x, y, w, h, cnt) in leaves:
        side, cols, rows = _best_block(cnt, w, h)
        if side <= 0:
            result += [(x + w / 2, y + h / 2, 0.0, 0.0)] * cnt
            continue
        gw = cols * side
        gh = rows * side
        ox = x + (w - gw) / 2
        oy = y + (h - gh) / 2
        placed = 0
        for i in range(cols):
            for j in range(rows):
                placed += 1
                cx = ox + (i + 0.5) * side
                cy = oy + (j + 0.5) * side
                result.append((cx, cy, 0.0, side))
        while placed < cnt:
            result.append((x + w / 2, y + h / 2, 0.0, 0.0))
            placed += 1

    result = result[:n]
    while len(result) < n:
        result.append((0.5, 0.5, 0.0, 0.0))
    return result


def _rot45(squares):
    return [(cx, cy, (ang + 0.125) % 1.0, s) for (cx, cy, ang, s) in squares]


def _slsqp_polish(squares, maxiter=400, free_angle=False, angle_perturb=0.0):
    """Maximise sum(s).  Variables (cx,cy,s) or (cx,cy,s,ang) per square."""
    n = len(squares)
    if n == 0:
        return squares
    k = 4 if free_angle else 3
    x0 = []
    for idx, (cx, cy, ang, s) in enumerate(squares):
        x0.append(cx)
        x0.append(cy)
        x0.append(s)
        if free_angle:
            a = (ang + angle_perturb) % 1.0
            x0.append(a)
    x0 = [min(max(v, 0.0), 1.0) for v in x0]

    def neg_sum(x):
        return -sum(x[k * i + 2] for i in range(n))

    def neg_grad(x):
        g = [0.0] * (k * n)
        for i in range(n):
            g[k * i + 2] = -1.0
        return g

    def constraints_bounds(x):
        c = []
        for i in range(n):
            cx = x[k * i]
            cy = x[k * i + 1]
            s = x[k * i + 2]
            if free_angle:
                t = x[k * i + 3] * 2 * math.pi
                ca = abs(math.cos(t))
                sa = abs(math.sin(t))
                rx = (ca + sa) * s / 2
                ry = (ca + sa) * s / 2
            else:
                rx = s / 2
                ry = s / 2
            c.append(cx - rx)
            c.append(1 - cx - rx)
            c.append(cy - ry)
            c.append(1 - cy - ry)
        return c

    cons = [{'type': 'ineq', 'fun': constraints_bounds}]

    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]

    def pair_constraints(x):
        c = []
        for (i, j) in pairs:
            cxi, cyi, si = x[k * i], x[k * i + 1], x[k * i + 2]
            cxj, cyj, sj = x[k * j], x[k * j + 1], x[k * j + 2]
            if free_angle:
                ti = x[k * i + 3] * 2 * math.pi
                tj = x[k * j + 3] * 2 * math.pi
                norms = [(math.cos(ti), math.sin(ti)), (-math.sin(ti), math.cos(ti)),
                         (math.cos(tj), math.sin(tj)), (-math.sin(tj), math.cos(tj))]
                best = -1e18
                for ux, uy in norms:
                    ri = (abs(math.cos(ti) * ux + math.sin(ti) * uy) +
                          abs(-math.sin(ti) * ux + math.cos(ti) * uy)) * si / 2
                    rj = (abs(math.cos(tj) * ux + math.sin(tj) * uy) +
                          abs(-math.sin(tj) * ux + math.cos(tj) * uy)) * sj / 2
                    proj = abs((cxi - cxj) * ux + (cyi - cyj) * uy)
                    best = max(best, proj - ri - rj)
            else:
                dx_sep = abs(cxi - cxj) - (si + sj) / 2
                dy_sep = abs(cyi - cyj) - (si + sj) / 2
                best = max(dx_sep, dy_sep)
            c.append(best)
        return c

    cons.append({'type': 'ineq', 'fun': pair_constraints})

    try:
        res = minimize(neg_sum, x0, jac=neg_grad, constraints=cons,
                       method='SLSQP', options={'maxiter': maxiter, 'ftol': 1e-11})
        x = res.x
    except Exception:
        return squares

    out = []
    for i in range(n):
        ang = (float(x[k * i + 3]) % 1.0) if free_angle else squares[i][2]
        out.append((float(x[k * i]), float(x[k * i + 1]), ang,
                    float(x[k * i + 2])))
    out = [(min(max(cx, 0.0), 1.0), min(max(cy, 0.0), 1.0),
            ang % 1.0, min(max(s, 0.0), 1.0)) for (cx, cy, ang, s) in out]
    return out


def _greedy_fix(squares):
    n = len(squares)
    out = [list(s) for s in squares]

    def bad(i):
        cx, cy, ang, s = out[i]
        if s < 0:
            return True
        if not _in_unit(cx, cy, ang, s):
            return True
        for j in range(n):
            if j != i and _overlap(out[i], out[j]):
                return True
        return False

    for _ in range(60):
        changed = False
        for i in range(n):
            while bad(i) and out[i][3] > 1e-6:
                out[i][3] *= 0.98
                changed = True
            if bad(i):
                out[i][3] = 0.0
                changed = True
        if not changed:
            break
    return [(float(a), float(b), float(c), float(d)) for a, b, c, d in out]


def _score(layout):
    return sum(s[3] for s in layout)


def _cd_polish(squares, iters=8, step=0.03):
    """Coordinate-descent: try to grow each square and nudge centres/angles
    while keeping the whole layout valid.  Deterministic, exact SAT checks."""
    cur = [list(s) for s in squares]
    n = len(cur)

    def valid():
        layout = [(a, b, c, d) for a, b, c, d in cur]
        return _valid_layout(layout)

    if not valid():
        return squares

    for _ in range(iters):
        improved = False
        for i in range(n):
            # try enlarging
            for ds in (step, step / 2, step / 4):
                trial = cur[i][3] + ds
                if trial > 1:
                    continue
                old = cur[i][3]
                cur[i][3] = trial
                if valid():
                    improved = True
                    break
                cur[i][3] = old
            # try nudging centre and angle
            cx, cy, ang, s = cur[i]
            best = (cx, cy, ang)
            best_ok = False
            # centre nudges
            for ddx in (-step, step, 0.0):
                for ddy in (-step, step, 0.0):
                    if ddx == 0 and ddy == 0:
                        continue
                    ncx = min(max(cx + ddx, 0.0), 1.0)
                    ncy = min(max(cy + ddy, 0.0), 1.0)
                    trial = cur[i][:]
                    trial[0], trial[1] = ncx, ncy
                    save = cur[i][:]
                    cur[i] = trial
                    if valid():
                        best = (ncx, ncy, ang)
                        best_ok = True
                        cur[i] = save
                        break
                    cur[i] = save
                if best_ok:
                    break
            if best_ok:
                cur[i][0], cur[i][1] = best[0], best[1]
                improved = True
            # angle nudges
            ang = cur[i][2]
            for da in (step, -step, step / 2, -step / 2):
                trial = cur[i][:]
                trial[2] = (ang + da) % 1.0
                save = cur[i][:]
                cur[i] = trial
                if valid():
                    cur[i] = save
                    cur[i][2] = (ang + da) % 1.0
                    improved = True
                    break
                cur[i] = save
        if not improved:
            break
    return [(float(a), float(b), float(c), float(d)) for a, b, c, d in cur]


def _shrink_repair(squares, factor=0.9):
    """Shrink all squares slightly and re-grow via CD to escape local optima."""
    out = [(cx, cy, ang, s * factor) for (cx, cy, ang, s) in squares]
    return out


def solve(n):
    if n <= 0:
        return []
    base = _construct(n)
    best = base
    best_val = _score(base)

    candidates = [base]
    candidates.append(_slsqp_polish(base, maxiter=300, free_angle=False))
    for off in (0.0, 0.0625, 0.125):
        candidates.append(_slsqp_polish(base, maxiter=400, free_angle=True,
                                        angle_perturb=off))
    r45 = _rot45(base)
    candidates.append(r45)
    candidates.append(_slsqp_polish(r45, maxiter=300, free_angle=False))

    # Custom coordinate-descent polish on each candidate, plus on a
    # shrink-repaired variant to escape tight local optima.
    extra = []
    for cand in candidates:
        cd = _cd_polish(cand, iters=10, step=0.02)
        extra.append(cd)
        shrunk = _shrink_repair(cd, 0.92)
        cd2 = _cd_polish(shrunk, iters=12, step=0.02)
        extra.append(cd2)
    candidates.extend(extra)

    for cand in candidates:
        cand = [(min(max(cx, 0.0), 1.0), min(max(cy, 0.0), 1.0),
                 a % 1.0, min(max(s, 0.0), 1.0)) for (cx, cy, a, s) in cand]
        if not _valid_layout(cand):
            cand = _greedy_fix(cand)
        if _valid_layout(cand):
            v = _score(cand)
            if v > best_val:
                best_val = v
                best = cand

    if not _valid_layout(best):
        best = base
    while len(best) < n:
        best.append((0.5, 0.5, 0.0, 0.0))
    return best[:n]
