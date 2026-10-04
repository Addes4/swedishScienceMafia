# EVOLVE-BLOCK-START
"""Recursive guillotine partition + tree-based annealing, with non-guillotine
corner constructions as extra candidates.

Idea
----
A guillotine partition is naturally represented as a binary tree: each internal
node splits its rectangle either horizontally or vertically at some ratio, and
each leaf is a rectangle in which we inscribe the largest axis-aligned square.

The previous program used a weak local-improve move set (only re-splitting two
adjacent rectangles into a 1x2 or 2x1 grid).  Here I:

1. Encode the partition as an explicit tree with (orient, ratio) at internal
   nodes and leaf rectangles at the leaves.
2. Warm-start from many cheap candidate families: direct grids, subdivided
   grids, strip partitions, and a greedy guillotine builder.
3. Also try non-guillotine "corner + central grid" constructions, since the
   best-known values exceed what pure guillotine layouts achieve for some n.
4. Run simulated annealing with three mutation types:
     - ratio nudge (perturb a random internal split ratio),
     - orientation flip (swap H/V at a random internal node),
     - topology swap (move a leaf from one child subtree to the other).
   Topology moves are heavily weighted for small n where the binding constraint
   is structure rather than ratio.
5. Convert the best tree to rectangles and inscribe the largest square in each.

This keeps the same inputs/outputs as the original program.
"""
import math
import random


# ---------------------------------------------------------------------------
# Tree representation
# ---------------------------------------------------------------------------

class Node:
    __slots__ = ("orient", "ratio", "left", "right", "rect")

    def __init__(self, orient=None, ratio=0.5, left=None, right=None, rect=None):
        self.orient = orient      # 'H' or 'V' for internal, None for leaf
        self.ratio = ratio        # split fraction for internal nodes
        self.left = left
        self.right = right
        self.rect = rect          # (x, y, w, h) for leaves


def _leaf_count(node):
    if node.orient is None:
        return 1
    return _leaf_count(node.left) + _leaf_count(node.right)


def _assign_rects(node, x, y, w, h):
    """Recursively assign rectangles to leaves given the node's split ratios."""
    if node.orient is None:
        node.rect = (x, y, w, h)
        return
    r = node.ratio
    if node.orient == 'V':
        wl = w * r
        _assign_rects(node.left, x, y, wl, h)
        _assign_rects(node.right, x + wl, y, w - wl, h)
    else:
        hl = h * r
        _assign_rects(node.left, x, y, w, hl)
        _assign_rects(node.right, x, y + hl, w, h - hl)


def _collect_leaves(node, out):
    if node.orient is None:
        out.append(node)
        return
    _collect_leaves(node.left, out)
    _collect_leaves(node.right, out)


def _tree_score(node):
    _assign_rects(node, 0.0, 0.0, 1.0, 1.0)
    leaves = []
    _collect_leaves(node, leaves)
    return sum(min(l.rect[2], l.rect[3]) for l in leaves)


def _tree_leaves_rects(node):
    _assign_rects(node, 0.0, 0.0, 1.0, 1.0)
    leaves = []
    _collect_leaves(node, leaves)
    return [l.rect for l in leaves]


def _build_tree_from_rects(rects):
    """Build a balanced guillotine tree that reproduces the given rectangles.

    We use a simple sweep: recursively partition the set of rectangles by the
    median x or y, choosing the axis that best separates them.  This is only
    used to warm-start the annealer from an existing rectangle list; the
    resulting tree may not exactly reproduce the rectangles, but it captures
    the topology (which is what matters for the annealer).
    """
    if len(rects) == 1:
        return Node(rect=rects[0])

    # Compute bounding box
    xs = [r[0] for r in rects]
    ys = [r[1] for r in rects]
    xe = [r[0] + r[2] for r in rects]
    ye = [r[1] + r[3] for r in rects]
    minx, maxx = min(xs), max(xe)
    miny, maxy = min(ys), max(ye)
    W = maxx - minx
    H = maxy - miny

    # Try vertical split: sort by center x, split at median
    best_axis = 'V'
    best_ratio = 0.5
    best_cost = float('inf')
    for axis in ('V', 'H'):
        if axis == 'V':
            key = lambda r: r[0] + r[2] / 2
            span = W
            lo = minx
        else:
            key = lambda r: r[1] + r[3] / 2
            span = H
            lo = miny
        if span <= 1e-12:
            continue
        srt = sorted(rects, key=key)
        mid = len(srt) // 2
        # Ratio to split at the boundary between the two halves
        if axis == 'V':
            boundary = (srt[mid - 1][0] + srt[mid - 1][2] + srt[mid][0]) / 2.0
        else:
            boundary = (srt[mid - 1][1] + srt[mid - 1][3] + srt[mid][1]) / 2.0
        ratio = (boundary - lo) / span
        ratio = max(0.05, min(0.95, ratio))
        # Cost: how badly the split cuts rectangles
        cost = 0.0
        for r in rects:
            if axis == 'V':
                cx = r[0] + r[2] / 2
            else:
                cy = r[1] + r[3] / 2
            # Distance of center from the split line
            split_pos = lo + ratio * span
            cost += abs((cx if axis == 'V' else cy) - split_pos)
        if cost < best_cost:
            best_cost = cost
            best_axis = axis
            best_ratio = ratio

    if best_axis == 'V':
        key = lambda r: r[0] + r[2] / 2
        lo = minx
    else:
        key = lambda r: r[1] + r[3] / 2
        lo = miny
    srt = sorted(rects, key=key)
    mid = len(srt) // 2
    left_rects = srt[:mid]
    right_rects = srt[mid:]
    if not left_rects or not right_rects:
        left_rects = srt[:1]
        right_rects = srt[1:]

    left = _build_tree_from_rects(left_rects)
    right = _build_tree_from_rects(right_rects)
    return Node(orient=best_axis, ratio=best_ratio, left=left, right=right)


def _clone_tree(node):
    if node.orient is None:
        return Node(rect=node.rect)
    return Node(orient=node.orient, ratio=node.ratio,
                left=_clone_tree(node.left), right=_clone_tree(node.right))


# ---------------------------------------------------------------------------
# Cheap candidate families (kept from previous program, extended)
# ---------------------------------------------------------------------------

def _square_sum(rects):
    return sum(min(r[2], r[3]) for r in rects)


def _split_rect(rect, a, b):
    x, y, w, h = rect
    sw = w / a
    sh = h / b
    out = []
    for i in range(a):
        for j in range(b):
            out.append((x + i * sw, y + j * sh, sw, sh))
    return out


def _greedy_partition(n):
    rects = [(0.0, 0.0, 1.0, 1.0)]
    need = n - 1
    while need > 0:
        best = None
        best_gain_per = -1.0
        for idx, r in enumerate(rects):
            w, h = r[2], r[3]
            base = min(w, h)
            for a in range(1, 6):
                for b in range(1, 6):
                    if a * b < 2:
                        continue
                    added = a * b - 1
                    if added > need:
                        continue
                    sub = _split_rect(r, a, b)
                    gain = _square_sum(sub) - base
                    if gain <= 0:
                        continue
                    gp = gain / added
                    if gp > best_gain_per + 1e-12:
                        best_gain_per = gp
                        best = (idx, a, b)
        if best is None:
            idx = max(range(len(rects)), key=lambda i: rects[i][2] * rects[i][3])
            best = (idx, 2, 2)
        idx, a, b = best
        r = rects.pop(idx)
        rects.extend(_split_rect(r, a, b))
        need -= (a * b - 1)
    return rects


def _direct_grid_candidates(n):
    results = []
    for k in range(1, int(math.isqrt(n)) + 4):
        if k * k < n:
            continue
        side = 1.0 / k
        rects = []
        count = 0
        for i in range(k):
            for j in range(k):
                if count >= n:
                    break
                rects.append((i * side, j * side, side, side))
                count += 1
            if count >= n:
                break
        if len(rects) == n:
            results.append(rects)
    return results


def _subdivide_candidates(n):
    results = []
    for k in range(1, int(math.isqrt(n)) + 3):
        if k * k > n:
            continue
        base = 1.0 / k
        cells = [(i * base, j * base, base, base) for i in range(k) for j in range(k)]
        for a in (2, 3, 4):
            x0, y0, w0, h0 = cells[0]
            sub_w = w0 / a
            sub_h = h0 / a
            new_cells = list(cells[1:])
            for i in range(a):
                for j in range(a):
                    new_cells.append((x0 + i * sub_w, y0 + j * sub_h, sub_w, sub_h))
            while len(new_cells) > n:
                idx = min(range(len(new_cells)),
                          key=lambda t: min(new_cells[t][2], new_cells[t][3]))
                new_cells.pop(idx)
            if len(new_cells) == n:
                results.append(new_cells)
        for a in (2, 3):
            for b in (2, 3):
                if a == b:
                    continue
                x0, y0, w0, h0 = cells[0]
                sub_w = w0 / a
                sub_h = h0 / b
                new_cells = list(cells[1:])
                for i in range(a):
                    for j in range(b):
                        new_cells.append((x0 + i * sub_w, y0 + j * sub_h, sub_w, sub_h))
                while len(new_cells) > n:
                    idx = min(range(len(new_cells)),
                              key=lambda t: min(new_cells[t][2], new_cells[t][3]))
                    new_cells.pop(idx)
                if len(new_cells) == n:
                    results.append(new_cells)
    return results


def _strip_candidates(n):
    results = []
    for m in range(1, n + 1):
        base = n // m
        rem = n % m
        counts = [base + (1 if i < rem else 0) for i in range(m)]
        if any(c == 0 for c in counts):
            continue
        h = 1.0 / m
        rects = []
        y = 0.0
        for i, c in enumerate(counts):
            w = 1.0 / c
            for j in range(c):
                rects.append((j * w, y, w, h))
            y += h
        if len(rects) == n:
            results.append(rects)
    for m in range(1, n + 1):
        base = n // m
        rem = n % m
        counts = [base + (1 if i < rem else 0) for i in range(m)]
        if any(c == 0 for c in counts):
            continue
        w = 1.0 / m
        rects = []
        x = 0.0
        for i, c in enumerate(counts):
            h = 1.0 / c
            for j in range(c):
                rects.append((x, j * h, w, h))
            x += w
        if len(rects) == n:
            results.append(rects)
    return results


def _corner_candidates(n):
    """Non-guillotine layouts: place squares in corners plus a central grid.

    For small n, the best-known configurations often place a few large squares
    in the corners and fill the middle with a fine grid.  We try a few variants.
    """
    results = []
    if n < 2:
        return results
    # Try k corner squares plus (n-k) tiny squares in a central grid
    for k in (1, 2, 3, 4):
        if k >= n:
            continue
        rem = n - k
        # central grid: r x c with r*c >= rem, drop extras
        for r in range(1, rem + 1):
            c = max(1, (rem + r - 1) // r)
            if r * c < rem:
                continue
            # Corner squares occupy a corner of size s; central grid fills rest
            # Choose s to maximise sum: k*s + rem*min(cell_w, cell_h)
            # cell_w = (1 - 2s)/c, cell_h = (1 - 2s)/r  (if 2 corners)
            # For simplicity, try a few s values.
            for s in (0.15, 0.2, 0.25, 0.3, 0.333, 0.4):
                if 2 * s >= 1.0:
                    continue
                inner = 1.0 - 2 * s
                cell_w = inner / c
                cell_h = inner / r
                cell = min(cell_w, cell_h)
                if cell <= 0:
                    continue
                # Score estimate: k corner squares of side s + rem cells of side cell
                # (this is just to filter; the actual rects are built below)
                if k * s + rem * cell <= 0:
                    continue
                rects = []
                # Corner squares: bottom-left, bottom-right, top-left, top-right
                corners = [(0.0, 0.0), (1.0 - s, 0.0), (0.0, 1.0 - s), (1.0 - s, 1.0 - s)]
                for i in range(k):
                    cx, cy = corners[i]
                    rects.append((cx, cy, s, s))
                # Central grid
                count = 0
                for i in range(r):
                    for j in range(c):
                        if count >= rem:
                            break
                        rects.append((s + j * cell_w, s + i * cell_h, cell_w, cell_h))
                        count += 1
                    if count >= rem:
                        break
                if len(rects) == n:
                    results.append(rects)
    return results


# ---------------------------------------------------------------------------
# Annealing over trees
# ---------------------------------------------------------------------------

def _collect_internal_nodes(node, out):
    if node.orient is None:
        return
    out.append(node)
    _collect_internal_nodes(node.left, out)
    _collect_internal_nodes(node.right, out)


def _collect_leaves_nodes(node, out):
    if node.orient is None:
        out.append(node)
        return
    _collect_leaves_nodes(node.left, out)
    _collect_leaves_nodes(node.right, out)


def _mutate(node, rng, n, topology_weight):
    """Mutate the tree in place.  Returns True if a structural change occurred."""
    internals = []
    _collect_internal_nodes(node, internals)
    if not internals:
        return False
    r = rng.random()
    if r < topology_weight and n > 2:
        # Topology swap: pick a random internal node, swap one leaf from its
        # left subtree with one leaf from its right subtree.
        # To do this we find the parent of a leaf in each subtree and swap
        # the leaf nodes themselves.
        target = rng.choice(internals)
        if target.left is None or target.right is None:
            return False
        left_leaves = []
        _collect_leaves_nodes(target.left, left_leaves)
        right_leaves = []
        _collect_leaves_nodes(target.right, right_leaves)
        if not left_leaves or not right_leaves:
            return False
        # Swap the leaf nodes' subtrees by swapping their 'rect' identity:
        # easier: swap the leaf nodes in the tree structure.  We do this by
        # finding parents.
        def find_parent(root, child):
            if root.orient is None:
                return None
            if root.left is child or root.right is child:
                return root
            p = find_parent(root.left, child)
            if p is not None:
                return p
            return find_parent(root.right, child)
        la = rng.choice(left_leaves)
        lb = rng.choice(right_leaves)
        pa = find_parent(node, la)
        pb = find_parent(node, lb)
        if pa is None or pb is None:
            return False
        # Swap la and lb in their parents
        if pa.left is la:
            pa.left = lb
        else:
            pa.right = lb
        if pb.left is lb:
            pb.left = la
        else:
            pb.right = la
        return True
    elif r < topology_weight + 0.15:
        # Orientation flip
        nd = rng.choice(internals)
        nd.orient = 'H' if nd.orient == 'V' else 'V'
        return True
    else:
        # Ratio nudge
        nd = rng.choice(internals)
        delta = rng.gauss(0.0, 0.08)
        nd.ratio = max(0.02, min(0.98, nd.ratio + delta))
        return True


def _anneal(start_tree, n, iters, seed, topology_weight):
    rng = random.Random(seed)
    best = _clone_tree(start_tree)
    best_score = _tree_score(best)
    cur = _clone_tree(start_tree)
    cur_score = best_score
    T0 = 0.05
    T1 = 0.0005
    for it in range(iters):
        T = T0 * (T1 / T0) ** (it / max(1, iters - 1))
        cand = _clone_tree(cur)
        if not _mutate(cand, rng, n, topology_weight):
            continue
        cs = _tree_score(cand)
        if cs > cur_score or rng.random() < math.exp((cs - cur_score) / max(T, 1e-9)):
            cur = cand
            cur_score = cs
            if cs > best_score:
                best = _clone_tree(cand)
                best_score = cs
    return best, best_score


# ---------------------------------------------------------------------------
# Main solver
# ---------------------------------------------------------------------------

def solve(n):
    if n <= 0:
        return []
    if n == 1:
        return [(0.5, 0.5, 0.0, 1.0)]

    # Gather candidate rectangle lists from all cheap families
    candidates = []
    for rects in _direct_grid_candidates(n):
        candidates.append(rects)
    for rects in _subdivide_candidates(n):
        candidates.append(rects)
    for rects in _strip_candidates(n):
        candidates.append(rects)
    for rects in _corner_candidates(n):
        candidates.append(rects)
    candidates.append(_greedy_partition(n))

    # Score all candidates, keep the best few
    scored = [( _square_sum(r), r) for r in candidates if len(r) == n]
    scored.sort(key=lambda t: -t[0])

    if not scored:
        # Fallback: grid
        k = math.isqrt(n)
        side = 1.0 / k
        rects = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side)
                 for i in range(k) for j in range(k)]
        rects += [(0.5, 0.5, 0.0, 0.0)] * (n - len(rects))
        return rects[:n]

    best_score = scored[0][0]
    best_rects = scored[0][1]

    # Anneal from the top few candidates
    top_k = min(4, len(scored))
    for i in range(top_k):
        base_rects = scored[i][1]
        tree = _build_tree_from_rects(base_rects)
        # Verify tree leaf count matches n; if not, skip
        if _leaf_count(tree) != n:
            continue
        # Weight topology moves more for small n (structure-bound)
        if n <= 12:
            tw = 0.45
        elif n <= 15:
            tw = 0.30
        else:
            tw = 0.20
        # More iterations for the best candidate
        iters = 2500 if i == 0 else 1200
        t, ts = _anneal(tree, n, iters=iters, seed=1000 + i * 37, topology_weight=tw)
        # Score the actual rectangles (tree score should match, but be safe)
        rects = _tree_leaves_rects(t)
        if len(rects) != n:
            continue
        sc = _square_sum(rects)
        if sc > best_score + 1e-12:
            best_score = sc
            best_rects = rects

    # Convert rectangles to squares
    result = []
    for x, y, w, h in best_rects:
        s = min(w, h)
        cx = x + w / 2.0
        cy = y + h / 2.0
        result.append((cx, cy, 0.0, s))

    while len(result) < n:
        result.append((0.5, 0.5, 0.0, 0.0))
    return result[:n]
# EVOLVE-BLOCK-END