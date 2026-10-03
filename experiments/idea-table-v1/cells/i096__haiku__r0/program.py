import math
from scipy.optimize import minimize
import numpy as np


def solve(n):
    """Return n squares (centre_x, centre_y, angle, side) inside the unit square,
    with disjoint interiors, maximising the sum of the sides."""
    
    # Start with a k x k grid baseline
    k = math.isqrt(n)
    side = 1.0 / k
    squares = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side) for i in range(k) for j in range(k)]
    squares += [(0.5, 0.5, 0.0, 0.0)] * (n - len(squares))
    squares = squares[:n]
    
    # Convert to state vector: [x0, y0, s0, x1, y1, s1, ..., x(n-1), y(n-1), s(n-1)]
    state = np.array([coord for sq in squares for coord in sq[:3]], dtype=float)
    
    # Determine ordering constraints based on current positions
    orderings = {}  # (i, j) -> 'left', 'right', 'above', 'below'
    for i in range(n):
        for j in range(i + 1, n):
            xi, yi = squares[i][0], squares[i][1]
            xj, yj = squares[j][0], squares[j][1]
            dx = abs(xj - xi)
            dy = abs(yj - yi)
            
            if dx > dy:
                orderings[(i, j)] = 'left' if xi < xj else 'right'
            else:
                orderings[(i, j)] = 'above' if yi < yj else 'below'
    
    def objective(s):
        """Minimize negative sum of sides (so we maximize sum)."""
        return -np.sum(s[2::3])
    
    def make_constraints(orderings_dict):
        """Generate constraint functions from ordering dict."""
        def constraints_func(s):
            constraints_list = []
            
            for (i, j), order in orderings_dict.items():
                xi, yi, si = s[3*i], s[3*i+1], s[3*i+2]
                xj, yj, sj = s[3*j], s[3*j+1], s[3*j+2]
                
                # Box constraints
                constraints_list.append(xi)  # >= 0
                constraints_list.append(1 - xi)  # <= 1
                constraints_list.append(yi)  # >= 0
                constraints_list.append(1 - yi)  # <= 1
                constraints_list.append(si)  # >= 0
                constraints_list.append(1 - si)  # >= 0 (si <= 1)
                
                constraints_list.append(xj)
                constraints_list.append(1 - xj)
                constraints_list.append(yj)
                constraints_list.append(1 - yj)
                constraints_list.append(sj)
                constraints_list.append(1 - sj)
                
                # No-overlap constraints based on ordering
                if order == 'left':
                    # i is to the left of j: xi + si/2 + si/2 <= xj - sj/2
                    constraints_list.append(xj - xi - si/2 - sj/2 - 1e-6)
                elif order == 'right':
                    # i is to the right of j: xj + sj/2 + sj/2 <= xi - si/2
                    constraints_list.append(xi - xj - sj/2 - si/2 - 1e-6)
                elif order == 'above':
                    # i is above j: yi + si/2 + si/2 <= yj - sj/2
                    constraints_list.append(yj - yi - si/2 - sj/2 - 1e-6)
                elif order == 'below':
                    # i is below j: yj + sj/2 + sj/2 <= yi - si/2
                    constraints_list.append(yi - yj - sj/2 - si/2 - 1e-6)
            
            return np.array(constraints_list)
        
        return constraints_func
    
    constraints_func = make_constraints(orderings)
    
    # Create scipy constraints from the constraint function
    cons = {'type': 'ineq', 'fun': constraints_func}
    
    # Initial polish with SLSQP
    result = minimize(objective, state, method='SLSQP', constraints=cons, options={'maxiter': 500})
    best_state = result.x
    best_value = result.fun
    
    # Try flipping orderings of pairs with tied separations (greedy within 20 seconds)
    import time
    start_time = time.time()
    max_time = 20
    
    tied_pairs = []
    for i in range(n):
        for j in range(i + 1, n):
            xi, yi = best_state[3*i], best_state[3*i+1]
            xj, yj = best_state[3*j], best_state[3*j+1]
            dx = abs(xj - xi)
            dy = abs(yj - yi)
            if abs(dx - dy) < 0.01:  # Consider tied if close
                tied_pairs.append((i, j))
    
    for (i, j) in tied_pairs:
        if time.time() - start_time > max_time:
            break
        
        old_order = orderings[(i, j)]
        new_orders = {'left': 'right', 'right': 'left', 'above': 'below', 'below': 'above'}
        orderings[(i, j)] = new_orders[old_order]
        
        constraints_func = make_constraints(orderings)
        cons = {'type': 'ineq', 'fun': constraints_func}
        
        result = minimize(objective, best_state, method='SLSQP', constraints=cons, options={'maxiter': 200})
        
        if result.fun < best_value:
            best_value = result.fun
            best_state = result.x
        else:
            orderings[(i, j)] = old_order
    
    # Convert back to output format
    output = []
    for i in range(n):
        x = best_state[3*i]
        y = best_state[3*i+1]
        s = max(0, best_state[3*i+2])
        output.append((x, y, 0.0, s))
    
    return output
