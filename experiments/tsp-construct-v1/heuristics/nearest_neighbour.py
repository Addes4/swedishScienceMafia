import numpy as np


def select_next_node(current_node: int, destination_node: int, unvisited_nodes: set, distance_matrix: np.ndarray) -> int:
    """Nearest neighbour: the papers' 'Greedy Construct' baseline."""
    U = np.fromiter(unvisited_nodes, dtype=np.int64)
    return int(U[int(np.argmin(distance_matrix[current_node, U]))])
