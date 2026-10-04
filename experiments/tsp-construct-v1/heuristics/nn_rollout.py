import numpy as np


def select_next_node(current_node: int, destination_node: int, unvisited_nodes: set, distance_matrix: np.ndarray) -> int:
    """Rollout of nearest neighbour (Bertsekas, Tsitsiklis and Wu 1997).

    For each candidate v, cost(v) = d(current, v) + length of the nearest-neighbour path that starts
    at v, visits every other unvisited node and ends at destination_node. Pick the cheapest. All
    candidates' completions run in parallel as array operations. Stateless; numpy only.
    """
    U = np.fromiter(unvisited_nodes, dtype=np.int64)
    m = U.size
    if m == 1:
        return int(U[0])
    D = distance_matrix
    S = D[np.ix_(U, U)]                      # distances among unvisited nodes
    visited = np.eye(m, dtype=bool)          # rollout r starts at candidate r
    cur = np.arange(m)
    cost = D[current_node, U].copy()
    rows = np.arange(m)
    for _ in range(m - 1):
        cand = np.where(visited, np.inf, S[cur])
        nxt = np.argmin(cand, axis=1)
        cost += cand[rows, nxt]
        visited[rows, nxt] = True
        cur = nxt
    cost += D[U[cur], destination_node]
    return int(U[int(np.argmin(cost))])
