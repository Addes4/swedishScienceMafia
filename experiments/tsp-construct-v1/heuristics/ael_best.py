# Copied verbatim from ReEvo (github.com/ai4co/reevo, MIT licence), commit 6dce18257da5e11db2d138e417a2fffc5c72d05f,
# problems/tsp_constructive/test/test_synthetic.ipynb, cell 1. Only the function is kept; the
# evaluation loop in eval_interface.py is the same as ReEvo's.
import numpy as np

def select_next_node_AEL(current_node, destination_node, unvisited_nodes, distance_matrix, threshold=0.7):
    """Algorithm Evolution Using Large Language Model"""
    scores = {}
    for node in unvisited_nodes:
        all_distances = [distance_matrix[node][i] for i in unvisited_nodes if i != node]
        average_distance_to_unvisited = np.mean(all_distances)
        std_dev_distance_to_unvisited = np.std(all_distances)
        score = 0.4 * distance_matrix[current_node][node] - 0.3 * average_distance_to_unvisited + 0.2 * std_dev_distance_to_unvisited - 0.1 * distance_matrix[destination_node][node]
        scores[node] = score
    if min(scores.values()) > threshold:
        next_node = min(unvisited_nodes, key=lambda node: distance_matrix[current_node][node])
    else:
        next_node = min(scores, key=scores.get)
    return next_node


select_next_node = select_next_node_AEL
