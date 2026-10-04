# No-cache variant of lkh_emit.py (fact-check follow-up, RUN_LOG.md): identical plan, recomputed at every call.

import numpy as np
from elkai import _elkai

_MEMO = {}


def _plan(D, destination_node):
    """LKH (via elkai) on the explicit distance matrix, scaled to integers; RUNS = 1."""
    n = D.shape[0]
    W = np.rint(D * 1e6).astype(np.int64)
    rows = "\n".join(" ".join(map(str, r)) for r in W)
    problem = (f"TYPE : TSP\nDIMENSION : {n}\nEDGE_WEIGHT_TYPE : EXPLICIT\n"
               f"EDGE_WEIGHT_FORMAT : FULL_MATRIX\nEDGE_WEIGHT_SECTION\n{rows}\n")
    t = np.array([s - 1 for s in _elkai.solve_problem("RUNS = 1\nSEED = 1\nPROBLEM_FILE = :stdin:\n", problem)])
    k = int(np.flatnonzero(t == destination_node)[0])
    t = np.concatenate([t[k:], t[:k]])
    if t[1] > t[-1]:
        t = np.concatenate([t[:1], t[1:][::-1]])
    return t


def select_next_node(current_node: int, destination_node: int, unvisited_nodes: set, distance_matrix: np.ndarray) -> int:
    """Emit an LKH tour one node at a time (exploratory ceiling; needs the compiled elkai package).

    Same pattern as greedy_ls_emit: the plan depends only on distance_matrix and destination_node;
    _MEMO caches it within an instance. Falls back to nearest neighbour off-plan.
    """
    D = distance_matrix
    n = D.shape[0]
    key = (n, destination_node, hash(D.tobytes()))
    _MEMO.clear()  # no-cache variant: recompute the plan at every call
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
