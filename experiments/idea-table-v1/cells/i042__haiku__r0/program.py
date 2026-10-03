import math
import random
import numpy as np
from scipy.optimize import minimize


def solve(n):
    """Return n squares using genetic algorithm with skyline decoder."""
    
    # Generate candidate side lengths from {1/d} for small d
    max_d = max(10, n // 2)
    candidate_sides = sorted([1.0 / d for d in range(1, max_d + 1)], reverse=True)
    
    # Seed solutions
    def grid_seed():
        """k x k grid plus zeros."""
        k = math.isqrt(n)
        side = 1.0 / k
        sides = [side] * (k * k) + [0.0] * (n - k * k)
        return sides[:n]
    
    def erdos_soifer_seed():
        """Multisets inspired by Erdős-Soifer packing."""
        sides = []
        remaining = n
        d = 2
        while remaining > 0 and d < 20:
            count = min(d * d, remaining)
            side = 1.0 / d
            sides.extend([side] * count)
            remaining -= count
            d += 1
        sides += [0.0] * max(0, n - len(sides))
        return sides[:n]
    
    def decode(sides):
        """Skyline (bottom-left) decoder: place squares greedily."""
        squares = []
        placed = []  # List of (x, y, size)
        
        for side in sides:
            if side <= 0:
                squares.append((0.5, 0.5, 0.0, 0.0))
                continue
            
            # Try to place at lowest possible y, then leftmost x
            placed_success = False
            
            # Grid search for placement
            for test_y_steps in range(max(1, int(1.0 / side) + 1)):
                test_y = test_y_steps * side / 2
                if test_y + side > 1.0:
                    break
                
                for test_x_steps in range(max(1, int(1.0 / side) + 1)):
                    test_x = test_x_steps * side / 2
                    if test_x + side > 1.0:
                        break
                    
                    # Check collision
                    collision = False
                    for px, py, ps in placed:
                        if (abs(test_x - px) < (side + ps) / 2 and
                            abs(test_y - py) < (side + ps) / 2):
                            collision = True
                            break
                    
                    if not collision:
                        center_x = test_x + side / 2
                        center_y = test_y + side / 2
                        if center_x <= 1.0 and center_y <= 1.0:
                            squares.append((center_x, center_y, 0.0, side))
                            placed.append((center_x, center_y, side))
                            placed_success = True
                            break
                
                if placed_success:
                    break
            
            if not placed_success:
                squares.append((0.5, 0.5, 0.0, 0.0))
        
        return squares
    
    def fitness(sides):
        """Sum of side lengths."""
        return sum(sides)
    
    def crossover(p1, p2):
        """Order crossover."""
        point = random.randint(1, n - 1)
        child = p1[:point] + p2[point:]
        return child
    
    def mutate(sides):
        """Mutation: change random sides."""
        sides = sides.copy()
        for _ in range(max(1, n // 10)):
            idx = random.randint(0, n - 1)
            sides[idx] = random.choice(candidate_sides + [0.0])
        return sides
    
    # Initialize population
    population = [
        grid_seed(),
        erdos_soifer_seed(),
    ]
    
    # Add random solutions
    for _ in range(8):
        sides = [random.choice(candidate_sides + [0.0]) for _ in range(n)]
        population.append(sides)
    
    # Evolve
    best_solution = max(population, key=fitness)
    best_fitness = fitness(best_solution)
    
    generation = 0
    max_generations = 200
    
    while generation < max_generations:
        generation += 1
        
        # Selection and reproduction
        new_population = []
        for _ in range(len(population)):
            p1 = max(random.sample(population, 2), key=fitness)
            p2 = max(random.sample(population, 2), key=fitness)
            child = crossover(p1, p2)
            if random.random() < 0.7:
                child = mutate(child)
            new_population.append(child)
        
        population = new_population
        current_best = max(population, key=fitness)
        current_fitness = fitness(current_best)
        
        if current_fitness > best_fitness:
            best_fitness = current_fitness
            best_solution = current_best
    
    return decode(best_solution)
