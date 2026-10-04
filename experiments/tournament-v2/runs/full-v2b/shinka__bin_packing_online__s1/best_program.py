# EVOLVE-BLOCK-START
"""Concave-utility bin packing: best-fit relaxed with distribution-aware residuals."""
import numpy as np


def priority(item, bins):
    """Return a priority for every bin in `bins`; the item goes to the highest (first on ties).

    item: integer size of the arriving item, 1..100.
    bins: numpy int64 array with the remaining capacity of every bin the item fits in,
          including unused bins (remaining capacity 100), in bin order.
    """
    residual = (bins - item).astype(np.float64)

    # Relaxed best-fit base: very small slope so distribution-aware bonuses
    # dominate the ranking and can freely reorder decisions.
    base = -0.15 * residual

    # (1) Bonus for near-perfect fills (residual ~ 0).
    perfect = np.exp(-0.5 * (residual / 2.0) ** 2)

    # (2) Broad bonus for residuals near the distribution mean (~40):
    #     leftover space of this size is likely to be filled by a future item.
    usable = np.exp(-0.5 * ((residual - 40.0) / 18.0) ** 2)

    # (3) Sharp complementary-pair bonus: prefer residuals close to the current
    #     item size, encouraging two items to fill a bin tightly together.
    pair = np.exp(-0.5 * ((residual - float(item)) / max(1.0, 0.35 * item)) ** 2)

    # (3b) Complementary-pair bonus at 100 - item: prefer residuals that would
    #      let a future item of the same size complete this bin exactly.
    comp = np.exp(-0.5 * ((residual - (100.0 - item)) / max(1.0, 0.2 * item)) ** 2)

    # (3c) Third complementary target at 100 - 2*item, gated to small items
    #      (item <= ~35) where this residual is a plausible leftover: it
    #      captures triples of similarly-sized small items that would fill a
    #      bin exactly. Smoothly disabled for larger items to avoid the
    #      dead-zone penalty seen when stacking extra targets indiscriminately.
    comp2 = np.exp(-0.5 * ((residual - (100.0 - 2.0 * item)) / max(1.0, 0.2 * item)) ** 2)
    comp2_gate = np.clip((35.0 - item) / 35.0, 0.0, 1.0)

    # (4) Mild penalty for tiny unusable slivers just above the item.
    sliver = np.exp(-0.5 * ((residual - 0.25 * item) / max(1.0, 0.25 * item)) ** 2)

    return (base + 8.0 * perfect + 3.0 * usable + 6.0 * pair
            + 2.0 * comp + 1.5 * comp2_gate * comp2 - 2.0 * sliver)
# EVOLVE-BLOCK-END