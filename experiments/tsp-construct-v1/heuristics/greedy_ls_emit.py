import numpy as np

_MEMO = {}


def _greedy_edge(D):
    """Greedy edge: add the shortest edges that keep degrees <= 2 and close no early cycle."""
    n = D.shape[0]
    iu, ju = np.triu_indices(n, 1)
    order = np.argsort(D[iu, ju], kind="stable")
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    deg = [0] * n
    adj = [[] for _ in range(n)]
    added = 0
    for e in order:
        i, j = int(iu[e]), int(ju[e])
        if deg[i] == 2 or deg[j] == 2:
            continue
        ri, rj = find(i), find(j)
        if ri == rj:
            continue
        parent[ri] = rj
        adj[i].append(j)
        adj[j].append(i)
        deg[i] += 1
        deg[j] += 1
        added += 1
        if added == n - 1:
            break
    a, b = [v for v in range(n) if deg[v] == 1]
    adj[a].append(b)
    adj[b].append(a)
    tour, prev, cur = [0], -1, 0
    for _ in range(n - 1):
        nx = adj[cur][0] if adj[cur][0] != prev else adj[cur][1]
        tour.append(nx)
        prev, cur = cur, nx
    return np.array(tour)


def _two_opt(t, D):
    n = len(t)
    improved = True
    while improved:
        improved = False
        for i in range(n - 2):
            j = np.arange(i + 2, n if i > 0 else n - 1)
            if j.size == 0:
                continue
            a, b = t[i], t[i + 1]
            c, d = t[j], t[(j + 1) % n]
            delta = D[a, c] + D[b, d] - D[a, b] - D[c, d]
            k = int(np.argmin(delta))
            if delta[k] < -1e-12:
                jj = int(j[k])
                t[i + 1:jj + 1] = t[i + 1:jj + 1][::-1].copy()
                improved = True
    return t


def _or_opt(t, D):
    n = len(t)
    improved = True
    while improved:
        improved = False
        for L in (1, 2, 3):
            for i in range(n):
                r = np.roll(t, -i)
                seg, rest = r[:L], r[L:]
                s0, s1, p, q = seg[0], seg[-1], rest[-1], rest[0]
                gain = D[p, s0] + D[s1, q] - D[p, q]
                u, v = rest[:-1], rest[1:]
                add = D[u, s0] + D[s1, v] - D[u, v]
                addr = D[u, s1] + D[s0, v] - D[u, v]
                k1, k2 = int(np.argmin(add)), int(np.argmin(addr))
                if min(add[k1], addr[k2]) < gain - 1e-12:
                    if add[k1] <= addr[k2]:
                        k, s = k1, seg
                    else:
                        k, s = k2, seg[::-1]
                    t = np.concatenate([rest[:k + 1], s, rest[k + 1:]])
                    improved = True
    return t


def _plan(D, destination_node):
    t = _greedy_edge(D)
    best = np.inf
    while True:
        t = _or_opt(_two_opt(t, D), D)
        L = D[t, np.roll(t, -1)].sum()
        if L > best - 1e-10:
            break
        best = L
    k = int(np.flatnonzero(t == destination_node)[0])
    t = np.concatenate([t[k:], t[:k]])
    if t[1] > t[-1]:
        t = np.concatenate([t[:1], t[1:][::-1]])
    return t


def select_next_node(current_node: int, destination_node: int, unvisited_nodes: set, distance_matrix: np.ndarray) -> int:
    """Emit a greedy-edge tour improved by 2-opt and Or-opt, one node at a time.

    The plan depends only on distance_matrix and destination_node, so the output is a function of
    the four arguments; _MEMO only caches the plan between calls on the same instance (it changes
    speed, not answers). Falls back to nearest neighbour if called from a partial tour that is not a
    prefix of the plan. numpy only.
    """
    D = distance_matrix
    n = D.shape[0]
    key = (n, destination_node, hash(D.tobytes()))
    if key not in _MEMO:
        if len(_MEMO) > 16:
            _MEMO.clear()
        _MEMO[key] = _plan(D, destination_node)
    t = _MEMO[key]
    pos = int(np.flatnonzero(t == current_node)[0])
    visited_ok = len(unvisited_nodes) == n - 1 - pos and not (set(t[: pos + 1].tolist()) & unvisited_nodes)
    if visited_ok and pos + 1 < n and int(t[pos + 1]) in unvisited_nodes:
        return int(t[pos + 1])
    U = np.fromiter(unvisited_nodes, dtype=np.int64)
    return int(U[int(np.argmin(D[current_node, U]))])
