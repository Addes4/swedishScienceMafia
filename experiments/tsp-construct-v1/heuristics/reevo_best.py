# Copied verbatim from ReEvo (github.com/ai4co/reevo, MIT licence), commit 6dce18257da5e11db2d138e417a2fffc5c72d05f,
# problems/tsp_constructive/test/test_synthetic.ipynb, cell 1. Only the function is kept; the
# evaluation loop in eval_interface.py is the same as ReEvo's.
import numpy as np

def select_next_node_ReEvo(current_node: int, destination_node: int, unvisited_nodes: set, distance_matrix: np.ndarray) -> int:
    """Select the next node to visit from the unvisited nodes."""
    weights = {'distance_to_current': 0.4, 
               'average_distance_to_unvisited': 0.25, 
               'std_dev_distance_to_unvisited': 0.25, 
               'distance_to_destination': 0.1}
    scores = {}
    for node in unvisited_nodes:
        future_distances = [distance_matrix[node, i] for i in unvisited_nodes if i != node]
        if future_distances:
            average_distance_to_unvisited = sum(future_distances) / len(future_distances)
            std_dev_distance_to_unvisited = (sum((x - average_distance_to_unvisited) ** 2 for x in future_distances) / len(future_distances)) ** 0.5
        else:
            average_distance_to_unvisited = std_dev_distance_to_unvisited = 0
        score = (weights['distance_to_current'] * distance_matrix[current_node, node] -
                 weights['average_distance_to_unvisited'] * average_distance_to_unvisited +
                 weights['std_dev_distance_to_unvisited'] * std_dev_distance_to_unvisited -
                 weights['distance_to_destination'] * distance_matrix[destination_node, node])
        scores[node] = score
    next_node = min(scores, key=scores.get)
    return next_node


select_next_node = select_next_node_ReEvo
