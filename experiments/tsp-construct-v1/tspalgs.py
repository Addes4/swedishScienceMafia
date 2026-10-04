"""Classical TSP tour constructions and local search, compiled with numba.

Everything takes a dense Euclidean distance matrix ``D`` (float64, n x n) and returns a tour as an
int64 array holding each node once. ``tour_length`` closes the cycle.

Constructions (textbook versions; see RESULTS.md for references):
- ``nearest_neighbour(D, start)``: always go to the closest unvisited node.
- ``insertion(D, rule)``: grow a cycle, choosing the next node by ``rule`` and inserting it where
  it adds least length. rule 0 = farthest (Rosenkrantz, Stearns and Lewis 1977), 1 = nearest,
  2 = random order (node index order; the instances are i.i.d., so index order is random),
  3 = cheapest (the node and position with the smallest added length).
- ``greedy_edge(D)``: add the shortest edges that keep every degree at most 2 and close no early
  cycle (the "greedy" or "greedy matching" heuristic).
- ``savings(D, hub)``: Clarke and Wright savings for the TSP.

Local search:
- ``two_opt(D, tour)``: first-improvement 2-opt to a local optimum.
- ``or_opt(D, tour)``: move segments of 1-3 nodes, either orientation, to a better position.
- ``two_opt_or_opt(D, tour)``: alternate the two until neither improves.

Distances are compared with a 1e-12 tolerance so floating-point noise cannot cause cycling.
"""
import numpy as np
from numba import njit

EPS = 1e-12


@njit(cache=True)
def tour_length(D, tour):
    n = tour.shape[0]
    s = 0.0
    for i in range(n):
        s += D[tour[i], tour[(i + 1) % n]]
    return s


@njit(cache=True)
def nearest_neighbour(D, start):
    n = D.shape[0]
    visited = np.zeros(n, dtype=np.bool_)
    tour = np.empty(n, dtype=np.int64)
    tour[0] = start
    visited[start] = True
    cur = start
    for k in range(1, n):
        best = -1
        bd = np.inf
        for j in range(n):
            if not visited[j] and D[cur, j] < bd:
                bd = D[cur, j]
                best = j
        tour[k] = best
        visited[best] = True
        cur = best
    return tour


@njit(cache=True)
def _insert_best(D, nxt, a, head):
    """Insert node a into the cycle stored as a successor array nxt at the cheapest edge."""
    best_u = head
    best_c = np.inf
    u = head
    while True:
        v = nxt[u]
        c = D[u, a] + D[a, v] - D[u, v]
        if c < best_c - EPS:
            best_c = c
            best_u = u
        u = v
        if u == head:
            break
    nxt[a] = nxt[best_u]
    nxt[best_u] = a
    return best_c


@njit(cache=True)
def insertion(D, rule):
    """rule: 0 farthest, 1 nearest, 2 index order (random), 3 cheapest."""
    n = D.shape[0]
    in_tour = np.zeros(n, dtype=np.bool_)
    nxt = -np.ones(n, dtype=np.int64)
    # start: farthest/nearest/cheapest begin from the two endpoints of the longest edge for
    # farthest, and from node 0 and its nearest neighbour otherwise.
    if rule == 0:
        bi, bj, bd = 0, 1, -1.0
        for i in range(n):
            for j in range(i + 1, n):
                if D[i, j] > bd:
                    bd = D[i, j]
                    bi = i
                    bj = j
    else:
        bi = 0
        bj = -1
        bd = np.inf
        for j in range(1, n):
            if D[0, j] < bd:
                bd = D[0, j]
                bj = j
        if rule == 2:
            bj = 1
    in_tour[bi] = True
    in_tour[bj] = True
    nxt[bi] = bj
    nxt[bj] = bi
    head = bi
    # mind[j] = distance from j to the nearest tour node
    mind = np.empty(n)
    for j in range(n):
        mind[j] = min(D[j, bi], D[j, bj])
    for step in range(n - 2):
        a = -1
        if rule == 0:
            bv = -1.0
            for j in range(n):
                if not in_tour[j] and mind[j] > bv:
                    bv = mind[j]
                    a = j
        elif rule == 1:
            bv = np.inf
            for j in range(n):
                if not in_tour[j] and mind[j] < bv:
                    bv = mind[j]
                    a = j
        elif rule == 2:
            for j in range(n):
                if not in_tour[j]:
                    a = j
                    break
        else:
            # cheapest insertion over all (node, edge) pairs
            bv = np.inf
            u = head
            while True:
                v = nxt[u]
                for j in range(n):
                    if not in_tour[j]:
                        c = D[u, j] + D[j, v] - D[u, v]
                        if c < bv - EPS:
                            bv = c
                            a = j
                u = v
                if u == head:
                    break
        _insert_best(D, nxt, a, head)
        in_tour[a] = True
        for j in range(n):
            if D[j, a] < mind[j]:
                mind[j] = D[j, a]
    tour = np.empty(n, dtype=np.int64)
    u = head
    for k in range(n):
        tour[k] = u
        u = nxt[u]
    return tour


@njit(cache=True)
def _find(parent, x):
    while parent[x] != x:
        parent[x] = parent[parent[x]]
        x = parent[x]
    return x


@njit(cache=True)
def _edges_to_tour(n, adj0, adj1):
    tour = np.empty(n, dtype=np.int64)
    tour[0] = 0
    prev = -1
    cur = 0
    for k in range(1, n):
        nx = adj0[cur] if adj0[cur] != prev else adj1[cur]
        tour[k] = nx
        prev = cur
        cur = nx
    return tour


@njit(cache=True)
def _greedy_join(n, order_i, order_j, skip):
    """Add candidate edges in the given order while degrees stay <= 2 and no early cycle forms.

    Nodes with skip[i] True are left out (used by savings for the hub). Returns adjacency arrays
    describing one Hamiltonian path over the non-skipped nodes (path ends have one -1 slot).
    """
    deg = np.zeros(n, dtype=np.int64)
    adj0 = -np.ones(n, dtype=np.int64)
    adj1 = -np.ones(n, dtype=np.int64)
    parent = np.arange(n)
    m = 0
    for i in range(n):
        if not skip[i]:
            m += 1
    added = 0
    for e in range(order_i.shape[0]):
        if added == m - 1:
            break
        i = order_i[e]
        j = order_j[e]
        if skip[i] or skip[j] or deg[i] >= 2 or deg[j] >= 2:
            continue
        ri = _find(parent, i)
        rj = _find(parent, j)
        if ri == rj:
            continue
        parent[ri] = rj
        if adj0[i] == -1:
            adj0[i] = j
        else:
            adj1[i] = j
        if adj0[j] == -1:
            adj0[j] = i
        else:
            adj1[j] = i
        deg[i] += 1
        deg[j] += 1
        added += 1
    return adj0, adj1, deg


def greedy_edge(D):
    n = D.shape[0]
    iu, ju = np.triu_indices(n, 1)
    order = np.argsort(D[iu, ju], kind="stable")
    adj0, adj1, deg = _greedy_join(n, iu[order], ju[order], np.zeros(n, dtype=np.bool_))
    ends = np.flatnonzero(deg == 1)
    a, b = ends[0], ends[1]
    adj1[a] = b
    adj1[b] = a
    return _edges_to_tour(n, adj0, adj1)


def savings(D, hub=None):
    """Clarke-Wright savings. The hub defaults to the node closest to the centroid of the points'
    distance profile (the node minimising its total distance), a common choice."""
    n = D.shape[0]
    if hub is None:
        hub = int(np.argmin(D.sum(1)))
    iu, ju = np.triu_indices(n, 1)
    s = D[hub, iu] + D[hub, ju] - D[iu, ju]
    order = np.argsort(-s, kind="stable")
    skip = np.zeros(n, dtype=np.bool_)
    skip[hub] = True
    adj0, adj1, deg = _greedy_join(n, iu[order], ju[order], skip)
    ends = np.flatnonzero((deg == 1) & ~skip)
    a, b = ends[0], ends[1]
    adj1[a] = hub
    adj1[b] = hub
    adj0[hub] = a
    adj1[hub] = b
    return _edges_to_tour(n, adj0, adj1)


@njit(cache=True)
def two_opt(D, tour):
    t = tour.copy()
    n = t.shape[0]
    improved = True
    while improved:
        improved = False
        for i in range(n - 1):
            a = t[i]
            b = t[i + 1]
            dab = D[a, b]
            for j in range(i + 2, n if i > 0 else n - 1):
                c = t[j]
                d = t[(j + 1) % n]
                delta = D[a, c] + D[b, d] - dab - D[c, d]
                if delta < -EPS:
                    # reverse t[i+1..j]
                    lo = i + 1
                    hi = j
                    while lo < hi:
                        tmp = t[lo]
                        t[lo] = t[hi]
                        t[hi] = tmp
                        lo += 1
                        hi -= 1
                    improved = True
                    a = t[i]
                    b = t[i + 1]
                    dab = D[a, b]
    return t


@njit(cache=True)
def or_opt(D, tour):
    """Move a segment of length 1..3 (optionally reversed) between two other consecutive nodes."""
    t = tour.copy()
    n = t.shape[0]
    improved = True
    while improved:
        improved = False
        for seglen in range(1, 4):
            if seglen >= n - 2:
                break
            i = 0
            while i < n:
                # segment t[i..i+seglen-1] (cyclic), prev p, next q
                p = t[(i - 1) % n]
                s0 = t[i % n]
                s1 = t[(i + seglen - 1) % n]
                q = t[(i + seglen) % n]
                remove_gain = D[p, s0] + D[s1, q] - D[p, q]
                best = -EPS
                bk = -1
                brev = False
                # candidate edges (u, v) not touching the segment: positions after the segment
                for k in range(n - seglen - 1):
                    u = t[(i + seglen + k) % n]
                    v = t[(i + seglen + k + 1) % n]
                    add = D[u, s0] + D[s1, v] - D[u, v]
                    addr = D[u, s1] + D[s0, v] - D[u, v]
                    if remove_gain - add > best + EPS:
                        best = remove_gain - add
                        bk = k
                        brev = False
                    if remove_gain - addr > best + EPS:
                        best = remove_gain - addr
                        bk = k
                        brev = True
                if bk >= 0:
                    # rebuild: rest of tour starting at q, insert segment after position bk
                    seg = np.empty(seglen, dtype=np.int64)
                    for m in range(seglen):
                        seg[m] = t[(i + m) % n]
                    if brev:
                        seg = seg[::-1].copy()
                    rest = np.empty(n - seglen, dtype=np.int64)
                    for m in range(n - seglen):
                        rest[m] = t[(i + seglen + m) % n]
                    nt = np.empty(n, dtype=np.int64)
                    pos = 0
                    for m in range(bk + 1):
                        nt[pos] = rest[m]
                        pos += 1
                    for m in range(seglen):
                        nt[pos] = seg[m]
                        pos += 1
                    for m in range(bk + 1, n - seglen):
                        nt[pos] = rest[m]
                        pos += 1
                    t = nt
                    improved = True
                i += 1
    return t


@njit(cache=True)
def two_opt_or_opt(D, tour):
    t = tour.copy()
    best = tour_length(D, t)
    while True:
        t = two_opt(D, t)
        t = or_opt(D, t)
        L = tour_length(D, t)
        if L > best - 1e-10:
            break
        best = L
    return t


def rotate_to(tour, start):
    k = int(np.flatnonzero(tour == start)[0])
    return np.concatenate([tour[k:], tour[:k]])
