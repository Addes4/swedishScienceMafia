# EVOLVE-BLOCK-START
"""Grid with substituted blocks (a x a cells -> b x b squares), plus a
rotated-chain insertion step for regions with slack."""
import math
import time


def _chain_side(W, H, m, th):
    c, s = math.cos(th), math.sin(th)
    return min(W / (m * c + s), H / (m * s + c))


def _best_chain(W, H, m):
    """Best tilt angle for m equal squares in a row (sharing edges) tilted by th
    inside a W x H rectangle. Returns (side, theta)."""
    best_s, best_t = -1.0, 0.0
    N = 400
    for i in range(N + 1):
        th = (math.pi / 4) * i / N
        sd = _chain_side(W, H, m, th)
        if sd > best_s:
            best_s, best_t = sd, th
    # golden-section refinement around best
    lo = max(0.0, best_t - math.pi / (4 * N))
    hi = min(math.pi / 4, best_t + math.pi / (4 * N))
    g = (math.sqrt(5) - 1) / 2
    for _ in range(60):
        x1 = hi - g * (hi - lo)
        x2 = lo + g * (hi - lo)
        if _chain_side(W, H, m, x1) > _chain_side(W, H, m, x2):
            hi = x2
        else:
            lo = x1
    th = 0.5 * (lo + hi)
    sd = _chain_side(W, H, m, th)
    if sd > best_s:
        best_s, best_t = sd, th
    # also try the swapped orientation (chain along the other axis)
    return best_s, best_t


def _chain_squares(x0, y0, W, H, m):
    """Place a chain of m tilted squares in rectangle; tries both orientations."""
    s1, t1 = _best_chain(W, H, m)
    s2, t2 = _best_chain(H, W, m)
    out = []
    if s1 >= s2:
        sd, th = s1 * (1 - 1e-9), t1
        c, sn = math.cos(th), math.sin(th)
        cx = x0 + sd * (c + sn) / 2
        cy = y0 + sd * (c + sn) / 2
        for i in range(m):
            out.append((cx + i * sd * c, cy + i * sd * sn, th, sd))
    else:
        sd, th = s2 * (1 - 1e-9), t2
        c, sn = math.cos(th), math.sin(th)
        # chain along y direction: transpose coordinates
        cx = x0 + sd * (c + sn) / 2
        cy = y0 + sd * (c + sn) / 2
        for i in range(m):
            # transposed geometry: square rotated by -th about its centre
            out.append((cx + i * sd * sn, cy + i * sd * c, -th, sd))
    return out, m * (s1 if s1 >= s2 else s2)


def solve(n):
    if n <= 0:
        return []
    t0 = time.time()
    r = math.isqrt(n)
    best = (-1.0, 1, ())
    for k in range(1, r + 4):
        if time.time() - t0 > 25:
            break
        base = k * k
        bmax_extra = r + 2
        opts = []
        for a in range(1, k + 1):
            for b in range(0, a + bmax_extra + 1):
                if b == a:
                    continue
                if n > 200 and b != 0 and abs(b - a) > 3:
                    continue
                opts.append((a, b, b * b - a * a, a * (b - a) / k))
        rounds = 4 if n <= 60 else (3 if n <= 200 else 2)
        states = {(0, 0): (0.0, ())}
        allstates = dict(states)
        frontier = states
        upper = n + base
        for _ in range(rounds):
            nf = {}
            for (A, dc), (ds, bl) in frontier.items():
                for (a, b, dcn, dsn) in opts:
                    if A + a > k:
                        continue
                    if bl and (a, b) < bl[-1]:
                        continue
                    nc = dc + dcn
                    if base + nc > upper or base + nc < 0:
                        continue
                    key = (A + a, nc)
                    v = ds + dsn
                    cur = nf.get(key)
                    if cur is None or v > cur[0]:
                        nf[key] = (v, bl + ((a, b),))
            for key, val in nf.items():
                cur = allstates.get(key)
                if cur is None or val[0] > cur[0]:
                    allstates[key] = val
            frontier = nf
            if time.time() - t0 > 25:
                break
        for (A, dc), (ds, bl) in allstates.items():
            cnt = base + dc
            if 0 <= cnt <= n:
                tot = k + ds
                if tot > best[0] + 1e-12:
                    best = (tot, k, bl)

    tot, k, blocks = best
    side = 1.0 / k
    squares = []
    blocked = set()
    empty_regions = []
    p = 0
    for (a, b) in blocks:
        for i in range(p, p + a):
            for j in range(p, p + a):
                blocked.add((i, j))
        if b == 0:
            empty_regions.append((p * side, p * side, a * side, a * side))
        else:
            s2 = a * side / b
            for i in range(b):
                for j in range(b):
                    squares.append((p * side + (i + 0.5) * s2, p * side + (j + 0.5) * s2, 0.0, s2))
        p += a
    for i in range(k):
        for j in range(k):
            if (i, j) not in blocked:
                squares.append(((i + 0.5) * side, (j + 0.5) * side, 0.0, side))

    # Rotated-insert perturbation: fill slack regions with tilted chains
    spare = n - len(squares)
    for (x0, y0, W, H) in empty_regions:
        if spare <= 0:
            break
        bestgain, bestsq = 0.0, None
        for m in range(1, spare + 1):
            sq, gain = _chain_squares(x0, y0, W, H, m)
            if gain > bestgain + 1e-12:
                bestgain, bestsq = gain, sq
        if bestsq is not None:
            squares.extend(bestsq)
            spare -= len(bestsq)
    # Try replacing a run of t row squares by t+1 tilted squares (strip of height 1/k)
    if spare >= 1:
        free_rows = [j for j in range(k) if all((i, j) not in blocked for i in range(k))]
        if free_rows:
            j = free_rows[0]
            bestgain, bestt, bestsq = 1e-12, None, None
            for t in range(1, k + 1):
                sq, val = _chain_squares(0.0, j * side, t * side, side, t + 1)
                gain = val - t * side
                if gain > bestgain:
                    bestgain, bestt, bestsq = gain, t, sq
            if bestsq is not None:
                rm = set((i, j) for i in range(bestt))
                newsq = []
                for q in squares:
                    ci = int(q[0] / side)
                    cj = int(q[1] / side)
                    if q[2] == 0.0 and abs(q[3] - side) < 1e-12 and (ci, cj) in rm:
                        continue
                    newsq.append(q)
                squares = newsq + bestsq

    out = []
    for (x, y, th, s) in squares[:n]:
        ang = (th / (2 * math.pi)) % 1.0
        out.append((min(1.0, max(0.0, x)), min(1.0, max(0.0, y)), ang, min(1.0, max(0.0, s))))
    while len(out) < n:
        out.append((0.5, 0.5, 0.0, 0.0))
    return out
# EVOLVE-BLOCK-END
