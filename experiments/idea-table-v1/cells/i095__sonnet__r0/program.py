# EVOLVE-BLOCK-START
"""Slicing-tree search with a compaction LP (free sizes and cut positions)."""
import math
import random
import time

import numpy as np
from scipy.optimize import linprog


def _build(t):
    state = {"nv": 0}
    leaves = []
    rows = []  # (list of (idx, coef), rhs)

    def addb(terms, rhs, bound, coef):
        i, c = bound
        if i >= 0:
            terms.append((i, coef))
            return rhs
        return rhs - coef * c

    def rec(t, x0, x1, y0, y1):
        if t == 0:
            s = state["nv"]
            state["nv"] += 1
            leaves.append((s, x0, x1, y0, y1))
            for (a, b) in ((x0, x1), (y0, y1)):
                terms = [(s, 1.0)]
                rhs = 0.0
                rhs = addb(terms, rhs, b, -1.0)
                rhs = addb(terms, rhs, a, 1.0)
                rows.append((terms, rhs))
            return
        d, L, R = t
        c = state["nv"]
        state["nv"] += 1
        cb = (c, 0.0)
        if d == 0:
            rec(L, x0, cb, y0, y1)
            rec(R, cb, x1, y0, y1)
        else:
            rec(L, x0, x1, y0, cb)
            rec(R, x0, x1, cb, y1)

    rec(t, (-1, 0.0), (-1, 1.0), (-1, 0.0), (-1, 1.0))
    return state["nv"], leaves, rows


def _lp(t, need_sol=False):
    nv, leaves, rows = _build(t)
    A = np.zeros((len(rows), nv))
    b = np.zeros(len(rows))
    for r, (terms, rhs) in enumerate(rows):
        for i, c in terms:
            A[r, i] += c
        b[r] = rhs
    c = np.zeros(nv)
    for s, *_ in leaves:
        c[s] = -1.0
    try:
        res = linprog(c, A_ub=A, b_ub=b, bounds=[(0, 1)] * nv, method="highs")
    except Exception:
        return -1.0, None
    if res.status != 0:
        return -1.0, None
    if need_sol:
        return -res.fun, (res.x, leaves)
    return -res.fun, None


def _paths(t, p=()):
    yield p
    if t != 0:
        yield from _paths(t[1], p + (1,))
        yield from _paths(t[2], p + (2,))


def _get(t, p):
    for i in p:
        t = t[i]
    return t


def _rep(t, p, new):
    if not p:
        return new
    l = list(t)
    l[p[0]] = _rep(t[p[0]], p[1:], new)
    return tuple(l)


def _count(t):
    return 1 if t == 0 else _count(t[1]) + _count(t[2])


def _chain(items, d):
    t = items[0]
    for it in items[1:]:
        t = (d, t, it)
    return t


def _rows_tree(m, g):
    rws = []
    left = m
    while left > 0:
        k = min(g, left)
        rws.append(_chain([0] * k, 0))
        left -= k
    return _chain(rws, 1)


def _remove_leaf(t, rng):
    if t == 0:
        return t
    lp = [p for p in _paths(t) if _get(t, p) == 0]
    p = rng.choice(lp)
    pp = p[:-1]
    sib = _get(t, pp)[3 - p[-1]]
    return _rep(t, pp, sib)


def _graft(t, rng):
    q = rng.choice(list(_paths(t)))
    X = _get(t, q)
    d = rng.randint(0, 1)
    new = (d, X, 0) if rng.random() < 0.5 else (d, 0, X)
    return _rep(t, q, new)


def _mutate(t, n, rng):
    r = rng.random()
    cnt = _count(t)
    if r < 0.3 and t != 0:
        ip = [p for p in _paths(t) if _get(t, p) != 0]
        p = rng.choice(ip)
        x = _get(t, p)
        return _rep(t, p, (1 - x[0], x[1], x[2]))
    if r < 0.7 and cnt > 1:
        return _graft(_remove_leaf(t, rng), rng)
    if r < 0.85 and cnt < n:
        return _graft(t, rng)
    if r < 0.9 and cnt > 1:
        return _remove_leaf(t, rng)
    if t != 0:
        # rotation: ((A,B),C) -> (A,(B,C)) with the same direction
        ip = [p for p in _paths(t) if _get(t, p) != 0 and _get(t, p + (1,)) != 0]
        if ip:
            p = rng.choice(ip)
            d, L, C = _get(t, p)
            d2, A, B = L
            return _rep(t, p, (d2, A, (d, B, C)))
    return _graft(_remove_leaf(t, rng), rng) if cnt > 1 else t


def solve(n):
    t0 = time.time()
    budget = 28.0
    rng = random.Random(12345 + n)
    k = max(1, math.isqrt(n))
    seeds = []
    for m in {n, k * k}:
        if m < 1:
            continue
        for g in range(1, k + 3):
            seeds.append(_rows_tree(m, g))
    cache = {}

    def ev(t):
        if t not in cache:
            cache[t] = _lp(t)[0]
        return cache[t]

    best, bestv = None, -1.0
    for s in seeds:
        v = ev(s)
        if v > bestv:
            best, bestv = s, v
        if time.time() - t0 > budget * 0.3:
            break
    cur, curv = best, bestv
    it = 0
    while time.time() - t0 < budget:
        frac = (time.time() - t0) / budget
        T = 0.03 * (1 - frac) + 1e-4
        cand = cur
        for _ in range(rng.randint(1, 2)):
            cand = _mutate(cand, n, rng)
        if _count(cand) > n:
            continue
        v = ev(cand)
        it += 1
        if v >= curv or rng.random() < math.exp((v - curv) / T):
            cur, curv = cand, v
            if v > bestv + 1e-12:
                best, bestv = cand, v
        if it % 400 == 0 and curv < bestv - 0.1:
            cur, curv = best, bestv

    val, sol = _lp(best, need_sol=True)
    squares = []
    if sol is not None:
        x, leaves = sol

        def bv(b):
            return x[b[0]] if b[0] >= 0 else b[1]

        for s, x0, x1, y0, y1 in leaves:
            a0, a1, b0, b1 = bv(x0), bv(x1), bv(y0), bv(y1)
            side = max(0.0, min(float(x[s]), a1 - a0, b1 - b0) - 1e-9)
            cx = min(1.0, max(0.0, (a0 + a1) / 2))
            cy = min(1.0, max(0.0, (b0 + b1) / 2))
            squares.append((float(cx), float(cy), 0.0, float(side)))
    if not squares:
        side = 1.0 / k
        squares = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side)
                   for i in range(k) for j in range(k)]
    squares = squares[:n]
    squares += [(0.5, 0.5, 0.0, 0.0)] * (n - len(squares))
    return squares
# EVOLVE-BLOCK-END
