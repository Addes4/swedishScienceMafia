# Transcribed from C. Chen, M. Zhong, Y. Fan, J. Shi and J. Sun, "TIDE: Tuning-Integrated Dynamic
# Evolution for LLM-Based Automated Heuristic Design", arXiv:2601.21239 (CC BY 4.0), Appendix F.1
# "Best-Performing Heuristic for Constructive TSP". Transcribed by hand from the PDF text (the
# extraction drops indentation); identifiers and constants are as printed. TIDE released no code.
# Added after pre-registration as an exploratory comparison (RUN_LOG.md).
import heapq
import math


def select_next_node_v2(current_node, destination_node, unvisited_nodes, distance_matrix):
    if not unvisited_nodes:
        return None
    if len(unvisited_nodes) == 1:
        return next(iter(unvisited_nodes))
    # Tunable parameters
    alpha = 0.8
    beta = 0.1
    gamma = 0.6
    theta = 0.05
    candidate_ratio = 2.5
    max_candidates = 12
    unvisited_list = list(unvisited_nodes)
    n_total = len(unvisited_list)
    k_candidates = min(int(n_total * candidate_ratio), max_candidates, n_total)
    if k_candidates == 0:
        k_candidates = 1
    candidate_set = heapq.nsmallest(k_candidates, unvisited_list, key=lambda x: distance_matrix[current_node][x])

    def calculate_mst_cost(nodes):
        if len(nodes) <= 1:
            return 0
        nodes = list(nodes)
        edges = []
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                u, v = nodes[i], nodes[j]
                edges.append((distance_matrix[u][v], u, v))
        edges.sort()
        parent = {node: node for node in nodes}
        rank = {node: 0 for node in nodes}

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def union(x, y):
            rx, ry = find(x), find(y)
            if rx == ry:
                return False
            if rank[rx] < rank[ry]:
                parent[rx] = ry
            elif rank[rx] > rank[ry]:
                parent[ry] = rx
            else:
                parent[ry] = rx
                rank[rx] += 1
            return True

        mst_cost = 0
        count = 0
        for cost, u, v in edges:
            if union(u, v):
                mst_cost += cost
                count += 1
                if count == len(nodes) - 1:
                    break
        return mst_cost

    def simulate_refined_path(start, remaining_nodes, dest):
        # Construct greedy path: start -> all remaining -> dest
        path = [start]
        current = start
        remaining = set(remaining_nodes)
        if start in remaining:
            remaining.remove(start)
        while remaining:
            next_n = min(remaining, key=lambda x: distance_matrix[current][x])
            path.append(next_n)
            current = next_n
            remaining.remove(current)
        path.append(dest)
        # Apply iterative 2-opt until no improvement
        improved = True
        while improved:
            improved = False
            best_gain = 0
            best_i, best_j = -1, -1
            n = len(path)
            for i in range(1, n - 2):
                for j in range(i + 2, n):
                    old_dist = distance_matrix[path[i - 1]][path[i]] + distance_matrix[path[j - 1]][path[j]]
                    new_dist = distance_matrix[path[i - 1]][path[j - 1]] + distance_matrix[path[i]][path[j]]
                    gain = old_dist - new_dist
                    if gain > best_gain:
                        best_gain = gain
                        best_i, best_j = i, j
            if best_gain > 1e-9:
                path[best_i:best_j] = reversed(path[best_i:best_j])
                improved = True
        total_cost = sum(distance_matrix[path[i]][path[i + 1]] for i in range(len(path) - 1))
        return total_cost

    best_score = float('inf')
    next_node = candidate_set[0]
    for candidate in candidate_set:
        remaining = set(unvisited_nodes)
        remaining.discard(candidate)
        direct_cost = distance_matrix[current_node][candidate]
        mst_cost = calculate_mst_cost(remaining) if remaining else 0
        sim_cost = simulate_refined_path(candidate, remaining, destination_node)
        dest_bias = distance_matrix[candidate][destination_node]
        score = (
            alpha * direct_cost +
            beta * mst_cost +
            gamma * sim_cost +
            theta * dest_bias
        )
        if score < best_score:
            best_score = score
            next_node = candidate
    return next_node
