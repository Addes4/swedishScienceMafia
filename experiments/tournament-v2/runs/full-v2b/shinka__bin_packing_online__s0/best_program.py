# EVOLVE-BLOCK-START
"""Adaptive residual-band best-fit.

Structural pipeline:
  state.update(item)  ->  derive (mu, sigma, min_item)  ->  score(bins)

The score prefers bins whose post-placement residual lands inside a
variance-adaptive band around the running mean item size, strongly
rewards exact fits, and penalizes dead-end residuals that are positive
but too small for any observed item to fill.
"""
import numpy as np


# ---------------------------------------------------------------------------
# State module: running statistics of arriving items (persist across calls).
# ---------------------------------------------------------------------------
_state = {
    "n": 0,
    "sum": 0.0,
    "sum_sq": 0.0,
    "min_item": 100,
    "ema": 40.0,          # exponential moving average of item size
    "ema_alpha": 0.02,    # smoothing factor
}


def _update_state(item):
    """Incorporate a new item and return (mu, sigma, min_item)."""
    x = float(item)
    s = _state
    s["n"] += 1
    s["sum"] += x
    s["sum_sq"] += x * x
    s["min_item"] = min(s["min_item"], int(item))
    s["ema"] = (1.0 - s["ema_alpha"]) * s["ema"] + s["ema_alpha"] * x

    n = s["n"]
    mu_raw = s["sum"] / n
    var = s["sum_sq"] / n - mu_raw * mu_raw
    if var < 0.0:
        var = 0.0
    sigma = var ** 0.5

    # Blend raw mean with EMA early on to damp startup noise.
    # After ~200 items the raw mean is trusted.
    if n < 200:
        w = n / 200.0
        mu_raw = w * mu_raw + (1.0 - w) * s["ema"]

    # Clamp target to a sensible prior range (Weibull mean ~40).
    mu = min(max(mu_raw, 20.0), 60.0)
    return mu, sigma, s["min_item"]


# ---------------------------------------------------------------------------
# Target module: variance-adaptive band around the target residual.
# ---------------------------------------------------------------------------
def _target_band(mu, sigma):
    """Return (mu_t, half_band) for the ideal post-placement residual."""
    # Band widens with observed spread but stays bounded.
    half = max(4.0, min(1.0 * sigma, 20.0))
    return mu, half


# ---------------------------------------------------------------------------
# Scoring module: additive terms over the residual vector.
# ---------------------------------------------------------------------------
def _score(residual, mu_t, half, min_item):
    """Combine primary + refinement terms into a single score per bin."""
    # Primary: closeness of residual to the adaptive target.
    score = -np.abs(residual - mu_t)

    # Exact fit: strictly best, dominant bonus.
    score += 50.0 * (residual == 0)

    # Dead-end penalty: positive residuals too small for any observed item.
    # Scale by how far below min_item the residual falls.
    dead = (residual > 0) & (residual < min_item)
    if dead.any():
        denom = float(min_item) if min_item > 0 else 1.0
        score -= 0.5 * np.where(dead, (min_item - residual) / denom, 0.0)

    # Refined tiebreak: prefer tighter fits, but only mildly, and further
    # prefer residuals that are actually fillable (>= min_item) over
    # dead-end near-zero residuals. This is inert whenever the primary
    # term already separates candidates.
    fillable = residual >= min_item
    tie = np.where(fillable, residual, residual + 100.0)
    score -= 0.01 * tie

    # Small bonus for residuals inside the fillable band [min_item, mu_t+half].
    in_band = (residual >= min_item) & (residual <= mu_t + half)
    score += 0.05 * in_band

    return score


# ---------------------------------------------------------------------------
# Public entry point.
# ---------------------------------------------------------------------------
def priority(item, bins):
    """Return a priority for every bin; highest score wins (first on ties).

    item: integer size of the arriving item, 1..100.
    bins: numpy int64 array of remaining capacities of bins the item fits in.
    """
    mu, sigma, min_item = _update_state(item)
    mu_t, half = _target_band(mu, sigma)

    residual = (bins - item).astype(np.float64)
    return _score(residual, mu_t, half, min_item)
# EVOLVE-BLOCK-END