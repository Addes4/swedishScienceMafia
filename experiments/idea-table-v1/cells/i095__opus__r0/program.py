# EVOLVE-BLOCK-START
"""Grid DP over guillotine layouts + LP compaction of the slicing tree + local search."""
import math
import time
import random
import copy
from fractions import Fraction

import numpy as np
from scipy.optimize import linprog


# ---------------------------------------------------------------- grid DP
def dp_grid(q, n):
    N = n + 1
    f = np.zeros((q + 1, q + 1, N))
    store = {}
    ii, jj = np.meshgrid(np.arange(N), np.arange(N), indexing='ij')
    ii = ii.ravel()
    jj = jj.ravel()
    cols = ii + jj
    T = np.full((N, 2 * N - 1), -np.inf)
    for a in range(1, q + 1):
        for b in range(1, q + 1):
            best = np.full(N, float(min(a, b)))
            best[0] = 0.0
            typ = np.zeros(N, dtype=int)
            pos = np.zeros(N, dtype=int)
            spl = np.zeros(N, dtype=int)
            for c in range(1, a // 2 + 1):
                A = f[c, b]
                B = f[a - c, b]
                T[ii, cols] = A[ii] + B[jj]
                v = T.max(0)[:N]
                ar = T.argmax(0)[:N]
                m = v > best + 1e-9
                if m.any():
                    best[m] = v[m]
                    typ[m] = 1
                    pos[m] = c
                    spl[m] = ar[m]
            for c in range(1, b // 2 + 1):
                A = f[a, c]
                B = f[a, b - c]
                T[ii, cols] = A[ii] + B[jj]
                v = T.max(0)[:N]
                ar = T.argmax(0)[:N]
                m = v > best + 1e-9
                if m.any():
                    best[m] = v[m]
                    typ[m] = 2
                    pos[m] = c
                    spl[m] = ar[m]
            f[a, b] = best
            store[(a, b)] = (typ, pos, spl)

    def rec(a, b, m):
        if m <= 0:
            return None
        typ, pos, spl = store[(a, b)]
        t = typ[m]
        if t == 0:
            return ['L']
        c = int(pos[m])
        m1 = int(spl[m])
        if t == 1:
            kids = [rec(c, b, m1), rec(a - c, b, m - m1)]
            o = 'V'
        else:
            kids = [rec(a, c, m1), rec(a, b - c, m - m1)]
            o = 'H'
        kids = [k for k in kids if k is not None]
        if not kids:
            return None
        if len(kids) == 1:
            return kids[0]
        return [o, kids]

    return f[q, q, n] / q, rec(q, q, n)


# ---------------------------------------------------------------- tree utils
def norm(node):
    if node is None:
        return None
    if node[0] == 'L':
        return node
    kids = []
    for c in node[1]:
        c2 = norm(c)
        if c2 is None:
            continue
        if c2[0] == node[0]:
            kids.extend(c2[1])
        else:
            kids.append(c2)
    if not kids:
        return None
    if len(kids) == 1:
        return kids[0]
    return [node[0], kids]


def count_leaves(node):
    if node[0] == 'L':
        return 1
    return sum(count_leaves(c) for c in node[1])


def collect(lst, i, leaves, internals):
    node = lst[i]
    if node[0] == 'L':
        leaves.append((lst, i))
    else:
        internals.append((lst, i))
        for j in range(len(node[1])):
            collect(node[1], j, leaves, internals)


# ---------------------------------------------------------------- LP
def lp_eval(tree):
    rows = []
    leaves = []
    nv = [0]

    def build(node):
        if node[0] == 'L':
            idx = nv[0]
            nv[0] += 1
            leaves.append(idx)
            return idx, idx
        w = nv[0]
        h = nv[0] + 1
        nv[0] += 2
        ch = [build(c) for c in node[1]]
        if node[0] == 'V':
            r = {w: -1.0}
            for cw, chh in ch:
                r[cw] = r.get(cw, 0.0) + 1.0
                rows.append({chh: 1.0, h: -1.0})
            rows.append(r)
        else:
            r = {h: -1.0}
            for cw, chh in ch:
                r[chh] = r.get(chh, 0.0) + 1.0
                rows.append({cw: 1.0, w: -1.0})
            rows.append(r)
        return w, h

    build(tree)
    n_var = nv[0]
    c = np.zeros(n_var)
    c[leaves] = -1.0
    if rows:
        A = np.zeros((len(rows), n_var))
        for k, r in enumerate(rows):
            for j, v in r.items():
                A[k, j] += v
        b = np.zeros(len(rows))
        res = linprog(c, A_ub=A, b_ub=b, bounds=[(0, 1)] * n_var, method='highs')
    else:
        res = linprog(c, bounds=[(0, 1)] * n_var, method='highs')
    if res.status != 0:
        return -1.0, None
    return -res.fun, [max(0.0, float(res.x[i])) for i in leaves]


# ---------------------------------------------------------------- placement
def place(tree, sides):
    it = iter(sides)

    def dims(node):
        if node[0] == 'L':
            s = next(it)
            return ('L', s, s, s)
        ch = [dims(c) for c in node[1]]
        if node[0] == 'V':
            W = sum(x[1] for x in ch)
            H = max(x[2] for x in ch)
        else:
            W = max(x[1] for x in ch)
            H = sum(x[2] for x in ch)
        return (node[0], W, H, ch)

    d = dims(tree)
    out = []

    def put(dn, x, y):
        if dn[0] == 'L':
            out.append((x, y, dn[3]))
            return
        cx, cy = x, y
        for c in dn[3]:
            put(c, cx, cy)
            if dn[0] == 'V':
                cx = cx + c[1]
            else:
                cy = cy + c[2]

    put(d, 0 * d[1], 0 * d[1])
    return d[1], d[2], out


def to_squares(tree, sides, n):
    result = None
    for den in (1000, 100000, 10 ** 7):
        fs = [Fraction(s).limit_denominator(den) for s in sides]
        W, H, out = place(tree, fs)
        if W <= 1 and H <= 1 and all(s >= 0 for s in fs):
            if abs(float(sum(fs)) - sum(sides)) < 1e-7:
                result = [(float(x + s / 2), float(y + s / 2), 0.0, float(s)) for x, y, s in out]
                break
    if result is None:
        W, H, out = place(tree, sides)
        sc = (1.0 - 1e-10) / max(1.0, W, H)
        result = [(min(1.0, (x + s / 2) * sc), min(1.0, (y + s / 2) * sc), 0.0, s * sc)
                  for x, y, s in out]
    result = result[:n]
    result += [(0.0, 0.0, 0.0, 0.0)] * (n - len(result))
    return result


# ---------------------------------------------------------------- mutation
def mutate(tree, n, rng):
    box = [copy.deepcopy(tree)]
    leaves, internals = [], []
    collect(box, 0, leaves, internals)
    op = rng.random()
    if op < 0.35 or not internals:
        lst, i = rng.choice(leaves)
        k = rng.choice([2, 2, 2, 3])
        lst[i] = [rng.choice('VH'), [['L'] for _ in range(k)]]
    elif op < 0.5:
        lst, i = rng.choice(leaves)
        o = rng.choice('VH')
        p = 'H' if o == 'V' else 'V'
        lst[i] = [o, [[p, [['L'], ['L']]], [p, [['L'], ['L']]]]]
    elif op < 0.65:
        lst, i = rng.choice(internals)
        lst[i][0] = 'H' if lst[i][0] == 'V' else 'V'
    elif op < 0.8:
        lst, i = rng.choice(internals)
        lst[i] = ['L']
    elif op < 0.9:
        lst, i = rng.choice(leaves)
        lst.pop(i)
    else:
        # move a subtree: swap two random nodes' contents
        allp = leaves + internals
        (l1, i1), (l2, i2) = rng.choice(allp), rng.choice(allp)
        a, b = l1[i1], l2[i2]
        l1[i1], l2[i2] = copy.deepcopy(b), copy.deepcopy(a)
    t = norm(box[0])
    if t is None:
        return None
    while count_leaves(t) > n:
        box = [t]
        leaves, internals = [], []
        collect(box, 0, leaves, internals)
        lst, i = rng.choice(leaves)
        lst.pop(i)
        t = norm(box[0])
        if t is None:
            return None
    return t


# ---------------------------------------------------------------- main
def solve(n):
    t0 = time.time()
    if n <= 0:
        return []
    if n == 1:
        return [(0.5, 0.5, 0.0, 1.0)]
    rng = random.Random(12345)
    cands = []
    seen = set()
    q = 1
    while q <= 48 and time.time() - t0 < 12.0:
        val, tree = dp_grid(q, n)
        if tree is not None:
            key = repr(tree)
            if key not in seen:
                seen.add(key)
                cands.append((val, tree))
        q += 1
    cands.sort(key=lambda x: -x[0])
    evaluated = []
    for val, tree in cands[:12]:
        v, s = lp_eval(tree)
        if s is not None:
            evaluated.append((v, tree, s))
    evaluated.sort(key=lambda x: -x[0])
    best_v, best_t, best_s = evaluated[0]
    pool = evaluated[:5]

    cur_v, cur_t = best_v, best_t
    deadline = t0 + 38.0
    it = 0
    while time.time() < deadline:
        it += 1
        if rng.random() < 0.01:
            cur_v, cur_t, _ = rng.choice(pool)
            if rng.random() < 0.5:
                cur_v, cur_t = best_v, best_t
        nt = mutate(cur_t, n, rng)
        if nt is None:
            continue
        v, s = lp_eval(nt)
        if s is None:
            continue
        if v >= cur_v - 1e-9:
            cur_v, cur_t = v, nt
            if v > best_v + 1e-9:
                best_v, best_t, best_s = v, nt, s

    return to_squares(best_t, best_s, n)
# EVOLVE-BLOCK-END
