# EVOLVE-BLOCK-START
"""Baseline: best fit. Put the item in the bin it fits most tightly."""
import numpy as np


def priority(item, bins):
    """Return a priority for every bin in `bins`; the item goes to the highest (first on ties).

    item: integer size of the arriving item, 1..100.
    bins: numpy int64 array with the remaining capacity of every bin the item fits in,
          including unused bins (remaining capacity 100), in bin order.
    """
    return -(bins - item)
# EVOLVE-BLOCK-END
