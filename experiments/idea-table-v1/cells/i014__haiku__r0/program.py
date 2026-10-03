import math
import heapq
from functools import lru_cache

def solve(n):
    """Return n squares maximizing the sum of side lengths using dynamic programming."""
    
    # Start with k x k grids and use best-first search to explore refinements
    best_sum = {}
    best_layout = {}
    
    # Initialize with all k x k grids
    for k in range(1, int(math.sqrt(n)) + 2):
        num_squares = k * k
        if num_squares <= n:
            side = 1.0 / k
            total_side = k * side
            best_sum[num_squares] = total_side
            layout = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side) 
                     for i in range(k) for j in range(k)]
            best_layout[num_squares] = layout
    
    # Best-first search: state = (number of squares, tree structure)
    # Tree structure: dict mapping position to (side_length, children_dict or None)
    # None children means it's a leaf (actual square)
    
    visited = set()
    pq = []
    
    # Initialize with k x k grids as trees
    for k in range(1, int(math.sqrt(n)) + 2):
        num_squares = k * k
        if num_squares <= n:
            # Build tree: root has k x k children at leaves
            tree = {
                'x': 0.5, 'y': 0.5, 'side': 1.0,
                'children': [(i, j) for i in range(k) for j in range(k)]
            }
            state = freeze_tree(tree)
            visited.add(state)
            priority = -best_sum.get(num_squares, 0)
            heapq.heappush(pq, (priority, num_squares, state, tree))
    
    # BFS to explore refinements
    iterations = 0
    max_iterations = 100000
    
    while pq and iterations < max_iterations:
        iterations += 1
        _, num_sq, state, tree = heapq.heappop(pq)
        
        if num_sq > n:
            continue
        
        # Try splitting a square
        splits = get_split_moves(tree)
        for split_idx in splits:
            for j in range(2, 5):  # Split into j x j
                new_tree = apply_split(tree, split_idx, j)
                new_num_sq = num_sq + j*j - 1
                
                if new_num_sq > n:
                    continue
                
                new_sum = tree_to_sum(new_tree)
                new_state = freeze_tree(new_tree)
                
                if new_state not in visited:
                    visited.add(new_state)
                    if new_num_sq not in best_sum or new_sum > best_sum[new_num_sq]:
                        best_sum[new_num_sq] = new_sum
                        best_layout[new_num_sq] = tree_to_layout(new_tree)
                    
                    priority = -new_sum
                    heapq.heappush(pq, (priority, new_num_sq, new_state, new_tree))
    
    # Build result for n squares
    if n in best_layout:
        result = best_layout[n]
    else:
        # Find best k x k that fits and pad with zeros
        k = int(math.sqrt(n))
        side = 1.0 / k
        result = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side) 
                 for i in range(k) for j in range(k)]
        result += [(0.5, 0.5, 0.0, 0.0)] * (n - len(result))
    
    return result[:n]


def freeze_tree(tree):
    """Convert tree to hashable representation."""
    if isinstance(tree, dict):
        children = tree.get('children', [])
        if isinstance(children, list):
            ch = tuple(freeze_tree(c) for c in children)
        else:
            ch = tuple()
        return (tree['side'], ch)
    return tree


def tree_to_sum(tree):
    """Calculate total side length from tree."""
    total = 0.0
    stack = [tree]
    while stack:
        node = stack.pop()
        if isinstance(node, dict):
            children = node.get('children', [])
            if not children or not isinstance(children[0], dict):
                # Leaf node
                total += node['side']
            else:
                stack.extend(children)
    return total


def get_split_moves(tree):
    """Return indices of squares that can be split."""
    return [0]  # Simplified: only consider main tree


def apply_split(tree, idx, j):
    """Apply split operation to tree."""
    import copy
    new_tree = copy.deepcopy(tree)
    side = new_tree['side'] / j
    new_tree['children'] = [
        {'x': new_tree['x'] + (i - j/2 + 0.5) * side,
         'y': new_tree['y'] + (k - j/2 + 0.5) * side,
         'side': side, 'children': []}
        for i in range(j) for k in range(j)
    ]
    return new_tree


def tree_to_layout(tree):
    """Convert tree to layout list."""
    result = []
    stack = [tree]
    while stack:
        node = stack.pop()
        if isinstance(node, dict):
            children = node.get('children', [])
            if not children:
                result.append((node['x'], node['y'], 0.0, node['side']))
            else:
                stack.extend(children)
    return result
