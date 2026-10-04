import numpy as np


def _farthest_insertion_cycle(D):
    """Farthest insertion (Rosenkrantz, Stearns and Lewis 1977) over all nodes of D."""
    n = D.shape[0]
    i, j = np.unravel_index(int(np.argmax(D)), D.shape)
    cyc = [int(i), int(j)]
    mind = np.minimum(D[:, i], D[:, j])
    left = np.ones(n, dtype=bool)
    left[[i, j]] = False
    for _ in range(n - 2):
        a = int(np.argmax(np.where(left, mind, -1.0)))
        c = np.asarray(cyc)
        nx = np.roll(c, -1)
        cost = D[c, a] + D[a, nx] - D[c, nx]
        cyc.insert(int(np.argmin(cost)) + 1, a)
        left[a] = False
        mind = np.minimum(mind, D[:, a])
    return np.asarray(cyc)


def _plan(D, destination_node):
    cyc = _farthest_insertion_cycle(D)
    k = int(np.flatnonzero(cyc == destination_node)[0])
    t = np.concatenate([cyc[k:], cyc[:k]])
    # fixed orientation, decided by the instance alone
    if t[1] > t[-1]:
        t = np.concatenate([t[:1], t[1:][::-1]])
    return t


def select_next_node(current_node: int, destination_node: int, unvisited_nodes: set, distance_matrix: np.ndarray) -> int:
    """Emit the farthest-insertion tour one node at a time.

    The whole instance is in distance_matrix, so the function rebuilds the farthest-insertion tour
    of all nodes (deterministic, starting from destination_node in a fixed orientation) and returns
    the node after current_node. If the visited nodes are not a prefix of that tour (the function was
    called from some other partial tour), it falls back to nearest neighbour. Stateless: the output
    depends only on the four arguments. numpy only.
    """
    D = distance_matrix
    n = D.shape[0]
    t = _plan(D, destination_node)
    pos = int(np.flatnonzero(t == current_node)[0])
    visited_ok = len(unvisited_nodes) == n - 1 - pos and not (set(t[: pos + 1].tolist()) & unvisited_nodes)
    if visited_ok and pos + 1 < n and int(t[pos + 1]) in unvisited_nodes:
        return int(t[pos + 1])
    U = np.fromiter(unvisited_nodes, dtype=np.int64)
    return int(U[int(np.argmin(D[current_node, U]))])
