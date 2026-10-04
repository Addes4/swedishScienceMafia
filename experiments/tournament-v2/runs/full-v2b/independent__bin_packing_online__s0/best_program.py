"""Online bin packing: adaptive best-fit priority rule."""
import numpy as np

# Mutable state shared across calls for this instance.
_STATE = {"count": 0, "sum": 0.0}


def priority(item, bins):
    """Rank bins so the item is placed as tightly as possible.

    Strategy:
    - Strongly prefer the bin with the smallest remaining capacity that still
      fits the item (best fit), which minimizes fragmentation.
    - Do not use a brand-new empty bin when an existing non-empty bin can take
      the item, unless the item clearly cannot combine well.
    - Track the running mean of arriving items; bins whose leftover after
      placement is near a multiple of that mean are mildly favored.
    """
    _STATE["count"] += 1
    _STATE["sum"] += float(item)
    mean_item = _STATE["sum"] / _STATE["count"]
    if mean_item < 1.0:
        mean_item = 1.0

    caps = bins.astype(np.float64)
    remaining_after = caps - float(item)

    # Base: best fit -> larger score for smaller leftover after placement.
    score = -remaining_after

    # Penalize opening a fresh empty bin (cap == 100) when other choices exist.
    is_empty = caps >= 100.0
    has_nonempty = np.any(~is_empty)

    if has_nonempty:
        score = np.where(is_empty, score - 1000.0, score)

    # Mild preference for leaving a residue that is a "usable" fraction of the
    # typical item size: avoid residues just below one mean item when possible.
    t = mean_item
    residue = remaining_after
    # Favor residues near or above one typical item, penalize awkward small
    # leftovers that would be hard to fill later, but keep this secondary.
    awkward = np.where(
        (residue > 0.0) & (residue < 0.5 * t),
        -residue * 2.0,
        0.0,
    )
    # Bonus for near-perfect residue around 0 (exact fill), scaled lightly.
    perfect = np.where(residue <= 0.0, 5.0, 0.0)

    score = score + awkward + perfect
    return score
