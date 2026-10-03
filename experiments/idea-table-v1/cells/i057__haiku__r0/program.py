import math
import numpy as np
from scipy.optimize import minimize
import multiprocessing as mp
from multiprocessing import Queue, Process
import time
import signal


def solve(n):
    """Return n squares with maximum sum of side lengths using parallel portfolio."""
    
    # For very small n, use direct solutions
    if n == 1:
        return [(0.5, 0.5, 0.0, 1.0)]
    if n == 2:
        return [(0.25, 0.5, 0.0, 0.5), (0.75, 0.5, 0.0, 0.5)]
    if n == 3:
        return [(0.5, 0.5, 0.0, 2/3), (0.5, 1/6, 0.0, 1/3), (0.5, 5/6, 0.0, 1/3)]
    if n == 4:
        return [(0.25, 0.25, 0.0, 0.5), (0.75, 0.25, 0.0, 0.5), 
                (0.25, 0.75, 0.0, 0.5), (0.75, 0.75, 0.0, 0.5)]
    
    start_time = time.time()
    timeout = 50.0
    
    result_queue = Queue()
    
    def run_method(method_name, method_func):
        try:
            result = method_func(n)
            if result:
                total_side = sum(s[3] for s in result)
                result_queue.put((total_side, result, method_name))
        except Exception:
            pass
    
    # Method 1: Grid-based baseline
    def grid_baseline(n):
        k = math.isqrt(n)
        side = 1.0 / k
        squares = [((i + 0.5) * side, (j + 0.5) * side, 0.0, side) 
                   for i in range(k) for j in range(k)]
        squares += [(0.5, 0.5, 0.0, 0.0)] * (n - len(squares))
        return squares[:n]
    
    # Method 2: Guillotine packing heuristic
    def guillotine_packing(n):
        squares = []
        remaining = list(range(n))
        regions = [(0.0, 0.0, 1.0, 1.0)]
        sizes = [1.0 / math.sqrt(n + i) for i in range(n)]
        
        for idx in remaining:
            if not regions:
                break
            reg = regions.pop(0)
            x0, y0, w, h = reg
            s = min(w, h, sizes[idx])
            
            cx, cy = x0 + s/2, y0 + s/2
            squares.append((cx, cy, 0.0, s))
            
            if w - s > 0.001:
                regions.append((x0 + s, y0, w - s, h))
            if h - s > 0.001:
                regions.append((x0, y0 + s, w, h - s))
        
        while len(squares) < n:
            squares.append((0.5, 0.5, 0.0, 0.0))
        return squares[:n]
    
    # Method 3: Rotated continuous optimization
    def rotated_optimization(n):
        def pack_score(params):
            squares_list = []
            for i in range(n):
                cx = params[i * 4]
                cy = params[i * 4 + 1]
                angle = params[i * 4 + 2]
                side = max(0, params[i * 4 + 3])
                squares_list.append((cx, cy, angle, side))
            
            side_sum = sum(s[3] for s in squares_list)
            penalty = 0
            
            for i, (cx, cy, ang, s) in enumerate(squares_list):
                if cx - s/2 < 0 or cx + s/2 > 1 or cy - s/2 < 0 or cy + s/2 > 1:
                    penalty += 100
                
                for j in range(i + 1, len(squares_list)):
                    cx2, cy2, ang2, s2 = squares_list[j]
                    dist = math.sqrt((cx - cx2)**2 + (cy - cy2)**2)
                    min_dist = (s + s2) / 2 * 0.707 + 0.01
                    if dist < min_dist:
                        penalty += 50 * (min_dist - dist)
            
            return -side_sum + penalty
        
        x0 = []
        k = max(1, math.isqrt(n))
        side_init = 1.0 / k
        for i in range(n):
            x0.extend([
                (i % k + 0.5) / k,
                (i // k + 0.5) / k,
                0.0,
                side_init
            ])
        
        bounds = [(0.01, 0.99), (0.01, 0.99), (0, 1), (0, 1)] * n
        
        res = minimize(pack_score, x0, method='L-BFGS-B', bounds=bounds,
                      options={'maxiter': 500, 'ftol': 1e-6})
        
        squares_list = []
        for i in range(n):
            cx = res.x[i * 4]
            cy = res.x[i * 4 + 1]
            angle = res.x[i * 4 + 2] % 1.0
            side = max(0, res.x[i * 4 + 3])
            squares_list.append((cx, cy, angle, side))
        return squares_list
    
    # Method 4: Efficient strip packing
    def strip_packing(n):
        squares = []
        y_pos = 0
        x_pos = 0
        row_height = 0
        side = 1.0 / math.sqrt(n)
        
        for i in range(n):
            if x_pos + side > 1.0:
                x_pos = 0
                y_pos += row_height
                row_height = 0
            
            if y_pos + side > 1.0:
                break
            
            squares.append((x_pos + side/2, y_pos + side/2, 0.0, side))
            x_pos += side
            row_height = max(row_height, side)
        
        while len(squares) < n:
            squares.append((0.5, 0.5, 0.0, 0.0))
        
        return squares[:n]
    
    # Run methods in parallel with timeout
    methods = [
        ("grid", grid_baseline),
        ("guillotine", guillotine_packing),
        ("rotated", rotated_optimization),
        ("strip", strip_packing),
    ]
    
    processes = []
    for name, func in methods:
        p = Process(target=run_method, args=(name, func))
        p.start()
        processes.append((p, name))
    
    best_score = 0
    best_result = None
    best_method = None
    
    deadline = start_time + timeout
    while time.time() < deadline:
        try:
            score, result, method = result_queue.get(timeout=1.0)
            if score > best_score:
                best_score = score
                best_result = result
                best_method = method
        except:
            pass
        
        alive_count = sum(1 for p, _ in processes if p.is_alive())
        if alive_count == 0:
            break
    
    for p, _ in processes:
        if p.is_alive():
            p.terminate()
            p.join(timeout=0.1)
    
    if best_result is None:
        best_result = grid_baseline(n)
    
    return best_result
