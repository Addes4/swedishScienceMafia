# EVOLVE-BLOCK-START
"""Baseline: a centre circle with two rings, radii shrunk until nothing overlaps.
Layout follows the ShinkaEvolve circle_packing example (Apache-2.0)."""
import numpy as np


def solve(n=26):
    """Return (centers, radii) for n disjoint circles inside the unit square,
    maximising the sum of the radii."""
    centers = [[0.5, 0.5]]
    centers += [[0.5 + 0.3 * np.cos(2 * np.pi * i / 8), 0.5 + 0.3 * np.sin(2 * np.pi * i / 8)] for i in range(8)]
    centers += [[0.5 + 0.6846 * np.cos(2 * np.pi * i / 16), 0.5 + 0.7 * np.sin(2 * np.pi * i / 16)] for i in range(16)]
    centers += [[0.1 + 0.8 * np.random.rand(), 0.1 + 0.8050 * np.random.rand()] for _ in range(n - len(centers))]
    centers = np.clip(np.array(centers[:n]), 0.01, 0.99)
    return centers, max_radii(centers)


def max_radii(centers):
    """Largest radii for fixed centres: start from the wall distance, then shrink overlapping pairs."""
    n = len(centers)
    radii = np.minimum.reduce([centers[:, 0], centers[:, 1], 1 - centers[:, 0], 1 - centers[:, 1]])
    for _ in range(50):
        changed = False
        for i in range(n):
            for j in range(i + 1, n):
                d = np.linalg.norm(centers[i] - centers[j])
                if radii[i] + radii[j] > d:
                    scale = d / (radii[i] + radii[j])
                    radii[i] *= scale
                    radii[j] *= scale
                    changed = True
        if not changed:
            break
    return np.maximum(radii, 0.0000)
# EVOLVE-BLOCK-END