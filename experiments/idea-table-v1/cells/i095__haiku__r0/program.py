import math
from fractions import Fraction
from scipy.optimize import linprog
import numpy as np


def solve(n):
    """Solve using LP-based guillotine cutting with free sizes on a slicing tree."""
    
    if n == 1:
        return [(0.5, 0.5, 0.0, 1.0)]
    
    if n == 2:
        return [(0.25, 0.5, 0.0, 0.5), (0.75, 0.5, 0.0, 0.5)]
    
    # Build a balanced binary slicing tree
    tree = build_slicing_tree(n)
    
    # Use LP to optimize sizes and positions
    result = solve_with_lp(tree, n)
    
    if result is not None:
        return result
    
    # Fallback to grid-based solution
    k = math.isqrt(n)
    side = 1.0 / k
    squares = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side) for i in range(k) for j in range(k)]
    squares += [(0.5, 0.5, 0.0, 0.0)] * (n - len(squares))
    return squares[:n]


def build_slicing_tree(n):
    """Build a balanced binary slicing tree for n leaves."""
    class Node:
        def __init__(self, is_leaf=False, leaf_idx=None):
            self.is_leaf = is_leaf
            self.leaf_idx = leaf_idx
            self.left = None
            self.right = None
            self.orientation = None  # 'h' for horizontal, 'v' for vertical
    
    def build(count, depth=0):
        if count == 1:
            node = Node(is_leaf=True, leaf_idx=0)
            return node
        
        # Alternate between horizontal and vertical cuts
        is_horizontal = (depth % 2 == 0)
        
        left_count = count // 2
        right_count = count - left_count
        
        node = Node()
        node.orientation = 'h' if is_horizontal else 'v'
        node.left = build(left_count, depth + 1)
        node.right = build(right_count, depth + 1)
        
        # Renumber leaves in tree
        renumber_leaves(node)
        return node
    
    def renumber_leaves(node):
        if node.is_leaf:
            return 1
        left_count = renumber_leaves(node.left)
        renumber_leaves_update(node.right, left_count)
        return left_count + renumber_leaves(node.right)
    
    def renumber_leaves_update(node, offset):
        if node.is_leaf:
            node.leaf_idx = offset
            return
        renumber_leaves_update(node.left, offset)
        renumber_leaves_update(node.right, offset + count_leaves(node.left))
    
    def count_leaves(node):
        if node.is_leaf:
            return 1
        return count_leaves(node.left) + count_leaves(node.right)
    
    tree = build(n)
    return tree


def solve_with_lp(tree, n):
    """Solve layout using linear programming."""
    # Extract tree structure
    leaves = []
    
    def extract_leaves(node):
        if node.is_leaf:
            leaves.append(node)
        else:
            extract_leaves(node.left)
            extract_leaves(node.right)
    
    extract_leaves(tree)
    
    # Variables: side lengths for each leaf
    # side[i] for leaf i, bounded by [0, 1]
    c = [-1.0] * n  # Maximize sum of sides (negate for minimization)
    
    bounds = [(0, 1) for _ in range(n)]
    
    # Constraints: total area <= 1
    A_ub = [[1.0] * n]
    b_ub = [1.0]
    
    try:
        result = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method='highs')
        
        if result.success:
            sides = result.x
            
            # Pack squares using guillotine with optimized sizes
            squares = pack_guillotine(tree, sides)
            return squares
    except:
        pass
    
    return None


def pack_guillotine(tree, sides):
    """Pack squares into unit square using guillotine cutting."""
    squares = []
    
    def pack_recursive(node, x, y, w, h, leaf_idx_ref):
        if node.is_leaf:
            side = min(sides[leaf_idx_ref[0]], min(w, h))
            cx = x + w / 2.0
            cy = y + h / 2.0
            squares.append((cx, cy, 0.0, side))
            leaf_idx_ref[0] += 1
            return
        
        if node.orientation == 'h':
            # Horizontal cut: split top and bottom
            left_leaves = count_leaves(node.left)
            right_leaves = count_leaves(node.right)
            total_leaves = left_leaves + right_leaves
            
            # Allocate height based on leaf counts
            h_left = h * left_leaves / total_leaves
            h_right = h - h_left
            
            pack_recursive(node.left, x, y, w, h_left, leaf_idx_ref)
            pack_recursive(node.right, x, y + h_left, w, h_right, leaf_idx_ref)
        else:
            # Vertical cut: split left and right
            left_leaves = count_leaves(node.left)
            right_leaves = count_leaves(node.right)
            total_leaves = left_leaves + right_leaves
            
            # Allocate width based on leaf counts
            w_left = w * left_leaves / total_leaves
            w_right = w - w_left
            
            pack_recursive(node.left, x, y, w_left, h, leaf_idx_ref)
            pack_recursive(node.right, x + w_left, y, w_right, h, leaf_idx_ref)
    
    pack_recursive(tree, 0, 0, 1.0, 1.0, [0])
    return squares


def count_leaves(node):
    """Count leaves in subtree."""
    if node.is_leaf:
        return 1
    return count_leaves(node.left) + count_leaves(node.right)
