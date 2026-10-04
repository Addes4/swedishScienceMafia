# EVOLVE-BLOCK-START
"""Guillotine-cut layout optimised by simulated annealing + local polish."""
import math
import random


# ----------------------------------------------------------------------
# Fallback: greedy grid + recursive subdivision heuristic.
# ----------------------------------------------------------------------
def _grid_subdivision(n):
    if n <= 0:
        return [], 0.0
    best_cells = None
    best_sum = -1.0
    max_k = math.isqrt(n)
    for k in range(1, max_k + 1):
        s = 1.0 / k
        cells = [(i * s, j * s, s) for i in range(k) for j in range(k)]
        guard = 0
        while len(cells) < n and guard < 100000:
            guard += 1
            idx = 0
            for i in range(1, len(cells)):
                if cells[i][2] > cells[idx][2]:
                    idx = i
            x, y, ss = cells[idx]
            h = ss * 0.5
            cells[idx] = (x, y, h)
            cells.append((x + h, y, h))
            cells.append((x, y + h, h))
            cells.append((x + h, y + h, h))
        if len(cells) > n:
            cells.sort(key=lambda t: -t[2])
            cells = cells[:n]
        total = sum(c[2] for c in cells)
        if total > best_sum:
            best_sum = total
            best_cells = cells
    return best_cells, best_sum


# ----------------------------------------------------------------------
# Guillotine tree representation.
#   Leaf  = ('L', x0, y0, x1, y1)
#   Node  = ('V'|'H', pos, left, right)
# ----------------------------------------------------------------------
def _build_balanced(n, x0, y0, x1, y1, rng):
    if n == 1:
        return ('L', x0, y0, x1, y1)
    if n == 2:
        a = 1
    else:
        a = rng.randint(1, n - 1)
        if rng.random() < 0.5:
            a = n // 2
    b = n - a
    w = x1 - x0
    h = y1 - y0
    if w >= h:
        vertical = rng.random() < 0.85
    else:
        vertical = rng.random() < 0.15
    if vertical:
        frac = a / float(n)
        frac = min(0.95, max(0.05, frac + rng.uniform(-0.15, 0.15)))
        pos = x0 + frac * w
        left = _build_balanced(a, x0, y0, pos, y1, rng)
        right = _build_balanced(b, pos, y0, x1, y1, rng)
        return ('V', pos, left, right)
    else:
        frac = a / float(n)
        frac = min(0.95, max(0.05, frac + rng.uniform(-0.15, 0.15)))
        pos = y0 + frac * h
        left = _build_balanced(a, x0, y0, x1, pos, rng)
        right = _build_balanced(b, x0, pos, x1, y1, rng)
        return ('H', pos, left, right)


def _collect_leaves(node, out):
    t = node[0]
    if t == 'L':
        out.append((node[1], node[2], node[3], node[4]))
        return
    _collect_leaves(node[2], out)
    _collect_leaves(node[3], out)


def _score_tree(node):
    t = node[0]
    if t == 'L':
        w = node[3] - node[1]
        h = node[4] - node[2]
        return min(w, h)
    return _score_tree(node[2]) + _score_tree(node[3])


def _recompute_rects(node, x0, y0, x1, y1):
    t = node[0]
    if t == 'L':
        return ('L', x0, y0, x1, y1)
    if t == 'V':
        _, pos, l, r = node
        pos = min(x1 - 1e-9, max(x0 + 1e-9, pos))
        if pos <= x0:
            pos = x0 + (x1 - x0) * 0.5
        if pos >= x1:
            pos = x0 + (x1 - x0) * 0.5
        nl = _recompute_rects(l, x0, y0, pos, y1)
        nr = _recompute_rects(r, pos, y0, x1, y1)
        return ('V', pos, nl, nr)
    else:
        _, pos, l, r = node
        pos = min(y1 - 1e-9, max(y0 + 1e-9, pos))
        if pos <= y0:
            pos = y0 + (y1 - y0) * 0.5
        if pos >= y1:
            pos = y0 + (y1 - y0) * 0.5
        nl = _recompute_rects(l, x0, y0, x1, pos)
        nr = _recompute_rects(r, x0, pos, x1, y1)
        return ('H', pos, nl, nr)


def _list_cuts(node, acc):
    t = node[0]
    if t == 'L':
        return
    acc.append((id(node), t, node[1]))
    _list_cuts(node[2], acc)
    _list_cuts(node[3], acc)


def _set_cut(node, target_id, new_pos):
    t = node[0]
    if t == 'L':
        return node
    _, pos, l, r = node
    if id(node) == target_id:
        pos = new_pos
    l = _set_cut(l, target_id, new_pos)
    r = _set_cut(r, target_id, new_pos)
    return (t, pos, l, r)


def _optimize_tree(tree, n, rng, iters):
    tree = _recompute_rects(tree, 0.0, 0.0, 1.0, 1.0)
    cur = _score_tree(tree)
    best_tree = tree
    best = cur
    cuts = []
    _list_cuts(tree, cuts)
    if not cuts:
        return tree, cur
    temp0 = 0.15
    temp1 = 0.001
    for it in range(iters):
        T = temp0 * (temp1 / temp0) ** (it / max(1, iters - 1))
        cid, kind, pos = cuts[rng.randrange(len(cuts))]
        step = 0.02 + 0.25 * T
        new_pos = pos + rng.gauss(0.0, step)
        new_pos = min(0.999999, max(0.000001, new_pos))
        trial = _set_cut(tree, cid, new_pos)
        trial = _recompute_rects(trial, 0.0, 0.0, 1.0, 1.0)
        sc = _score_tree(trial)
        if sc >= cur or rng.random() < math.exp((sc - cur) / max(1e-9, T)):
            tree = trial
            cur = sc
            if sc > best:
                best = sc
                best_tree = trial
            cuts = []
            _list_cuts(tree, cuts)
    return best_tree, best


def _polish(tree, n, rng, rounds=2):
    tree = _recompute_rects(tree, 0.0, 0.0, 1.0, 1.0)
    cur = _score_tree(tree)
    for _ in range(rounds):
        cuts = []
        _list_cuts(tree, cuts)
        improved = False
        for (cid, kind, pos) in cuts:
            for delta in (0.01, -0.01, 0.03, -0.03, 0.005, -0.005):
                np_ = min(0.999999, max(0.000001, pos + delta))
                trial = _set_cut(tree, cid, np_)
                trial = _recompute_rects(trial, 0.0, 0.0, 1.0, 1.0)
                sc = _score_tree(trial)
                if sc > cur + 1e-12:
                    tree = trial
                    cur = sc
                    improved = True
                    break
        if not improved:
            break
    return tree, cur


def solve(n):
    if n <= 0:
        return []
    if n == 1:
        return [(0.5, 0.5, 0.0, 1.0)]

    base_cells, base_sum = _grid_subdivision(n)
    best_cells = base_cells
    best_sum = base_sum

    rng = random.Random(12345 + n)

    n_restarts = 6
    iters = max(400, 250 * n)

    for r in range(n_restarts):
        tree = _build_balanced(n, 0.0, 0.0, 1.0, 1.0, rng)
        tree, sc = _optimize_tree(tree, n, rng, iters)
        tree, sc = _polish(tree, n, rng, rounds=3)
        if sc > best_sum:
            leaves = []
            _collect_leaves(tree, leaves)
            cells = []
            for (x0, y0, x1, y1) in leaves:
                w = x1 - x0
                h = y1 - y0
                s = min(w, h)
                cx = 0.5 * (x0 + x1)
                cy = 0.5 * (y0 + y1)
                cells.append((cx - s * 0.5, cy - s * 0.5, s))
            best_sum = sc
            best_cells = cells

    result = []
    for (x, y, s) in best_cells:
        result.append((x + s * 0.5, y + s * 0.5, 0.0, s))
    while len(result) < n:
        result.append((0.5, 0.5, 0.0, 0.0))
    return result[:n]
# EVOLVE-BLOCK-END