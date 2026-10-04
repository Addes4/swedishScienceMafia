import numpy as np


def select_next_node(current_node: int, destination_node: int, unvisited_nodes: set, distance_matrix: np.ndarray) -> int:
    """Farthest insertion (Rosenkrantz, Stearns and Lewis 1977), replanned at every step.

    Plans a path from current_node to destination_node through all unvisited nodes: repeatedly take
    the unvisited node farthest from the partial path and insert it where it adds least length.
    Returns the first node of that plan. Stateless: uses only the four arguments. numpy only.
    """
    U = np.fromiter(unvisited_nodes, dtype=np.int64)
    if U.size == 1:
        return int(U[0])
    D = distance_matrix
    path = [current_node, destination_node]
    mind = np.minimum(D[U, current_node], D[U, destination_node])
    left = np.ones(U.size, dtype=bool)
    for _ in range(U.size):
        k = int(np.argmax(np.where(left, mind, -1.0)))
        a = int(U[k])
        p = np.asarray(path)
        cost = D[p[:-1], a] + D[a, p[1:]] - D[p[:-1], p[1:]]
        pos = int(np.argmin(cost))
        path.insert(pos + 1, a)
        left[k] = False
        mind = np.minimum(mind, D[U, a])
    return int(path[1])
