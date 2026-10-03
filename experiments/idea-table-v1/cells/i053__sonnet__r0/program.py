# EVOLVE-BLOCK-START
"""Recursive block/shelf packing with exact fractions, memoised DP, iterative deepening."""
import math
import time
from fractions import Fraction


_CAND_FR = None


def _cand_fracs():
    global _CAND_FR
    if _CAND_FR is None:
        st = set()
        for q in range(1, 9):
            st.add(Fraction(1, q))
        for q in range(1, 6):
            for p in range(1, q + 1):
                st.add(Fraction(p, q))
        _CAND_FR = sorted(st, reverse=True)
    return _CAND_FR


def solve(n):
    if n <= 0:
        return []
    start = time.time()
    deadline = start + 45.0
    memo = {}
    cand_cache = {}

    def cands(W, H):
        key = (W, H)
        r = cand_cache.get(key)
        if r is None:
            mn = min(W, H)
            st = set()
            for base in (W, H):
                for f in _cand_fracs():
                    s = base * f
                    if s <= mn and s * 6 >= mn:
                        st.add(s)
            r = sorted(st, reverse=True)
            cand_cache[key] = r
        return r

    def F(W, H, m, d):
        if m <= 0 or W <= 0 or H <= 0:
            return (Fraction(0), None)
        key = (W, H, m, d)
        r = memo.get(key)
        if r is not None:
            return r
        if time.time() > deadline:
            raise TimeoutError
        best = Fraction(0)
        ch = None
        for s in cands(W, H):
            cols = math.floor(W / s)
            rows = math.floor(H / s)
            if cols < 1 or rows < 1:
                continue
            cnt = min(m, cols * rows)
            v = cnt * s
            if v > best:
                best = v
                ch = ('grid', s, cols, cnt)
            if d <= 0:
                continue
            bs_set = {b for b in (1, cols, cols - 1) if 1 <= b <= cols}
            as_set = {a for a in (1, rows, rows - 1) if 1 <= a <= rows}
            for b in bs_set:
                for a in as_set:
                    if a * b > m:
                        continue
                    rest = m - a * b
                    if rest <= 0:
                        continue
                    bw = b * s
                    ah = a * s
                    if bw == W and ah == H:
                        continue
                    base = a * b * s
                    for split in (0, 1):
                        if split == 0:
                            r1 = (W - bw, H, bw, Fraction(0))
                            r2 = (bw, H - ah, Fraction(0), ah)
                        else:
                            r1 = (W, H - ah, Fraction(0), ah)
                            r2 = (W - bw, ah, bw, Fraction(0))
                        for m1 in range(rest + 1):
                            v1 = F(r1[0], r1[1], m1, d - 1)[0] if m1 > 0 else 0
                            v2 = F(r2[0], r2[1], rest - m1, d - 1)[0] if rest - m1 > 0 else 0
                            tot = base + v1 + v2
                            if tot > best:
                                best = tot
                                ch = ('blk', s, b, a, split, m1, rest - m1)
        res = (best, ch)
        memo[key] = res
        return res

    def build(W, H, m, d, ox, oy, out):
        if m <= 0 or W <= 0 or H <= 0:
            return
        val, ch = memo[(W, H, m, d)]
        if ch is None:
            return
        if ch[0] == 'grid':
            _, s, cols, cnt = ch
            for i in range(cnt):
                cx = ox + (i % cols) * s + s / 2
                cy = oy + (i // cols) * s + s / 2
                out.append((float(cx), float(cy), 0.0, float(s)))
            return
        _, s, b, a, split, m1, m2 = ch
        for i in range(a):
            for j in range(b):
                out.append((float(ox + j * s + s / 2), float(oy + i * s + s / 2), 0.0, float(s)))
        bw = b * s
        ah = a * s
        if split == 0:
            r1 = (W - bw, H, bw, Fraction(0))
            r2 = (bw, H - ah, Fraction(0), ah)
        else:
            r1 = (W, H - ah, Fraction(0), ah)
            r2 = (W - bw, ah, bw, Fraction(0))
        build(r1[0], r1[1], m1, d - 1, ox + r1[2], oy + r1[3], out)
        build(r2[0], r2[1], m2, d - 1, ox + r2[2], oy + r2[3], out)

    best_out = None
    best_val = -1
    one = Fraction(1)
    for D in range(1, 7):
        try:
            v, _ = F(one, one, n, D)
        except TimeoutError:
            break
        if v > best_val or best_out is None:
            out = []
            build(one, one, n, D, Fraction(0), Fraction(0), out)
            best_out = out
            best_val = v
        if time.time() > deadline - 5:
            break

    if best_out is None:
        k = math.isqrt(n)
        side = 1.0 / k
        best_out = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side)
                    for i in range(k) for j in range(k)]
    best_out = best_out[:n]
    best_out += [(0.5, 0.5, 0.0, 0.0)] * (n - len(best_out))
    return best_out
# EVOLVE-BLOCK-END
