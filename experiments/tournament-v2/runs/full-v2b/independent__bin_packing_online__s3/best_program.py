import numpy as np


def priority(item, bins):
    """
    Online bin packing priority rule.

    Strategy: hybrid of Best Fit and Worst Fit logic with state-
    aware adaptation.  We prefer:
      - Exact fits (waste == 0) with highest priority.
      - Bins where leftover capacity is small (tight fits), but
        penalize leaving small unusable residues.
      - We keep track of recent average item size to decide whether
        a bin is "too full to waste" or can still accommodate future
        medium items.
    """
    # --- State: running estimate of mean item size ---
    # Stored on function attribute for persistence across calls.
    if not hasattr(priority, "_sum"):
        priority._sum = 0.0
        priority._count = 0

    priority._sum += item
    priority._count += 1

    # Running mean of observed items (used to estimate typical item)
    mean_item = priority._sum / priority._count

    # --- Scoring ---
    # leftover after placing item:
    residual = bins - item          # >= 0 for fitting bins

    # Penalize leaving a residual that is smaller than typical item
    # (that space is likely wasted), but reward exact fits strongly.
    # Base score: prefer tight fits (small residual).
    base = -residual.astype(np.float64)

    # Bonus for exact fit
    exact = (residual == 0).astype(np.float64) * 200.0

    # Penalty if residual is non-zero but smaller than mean item
    # (fragmentation risk): scale down such bins.
    small_resid = ((residual > 0) & (residual < mean_item)).astype(np.float64)
    frag_penalty = small_resid * (mean_item - residual) * 1.5

    # Reward bins that can still accept a typical future item after
    # this placement (residual >= mean_item) -- keeps flexibility.
    flexible = (residual >= mean_item).astype(np.float64) * (mean_item * 0.4)

    score = base + exact - frag_penalty + flexible

    return score
