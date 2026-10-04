# EVOLVE-BLOCK-START
"""Threshold-aware best fit with histogram-guided near-tie break.

Pure best-fit often creates a bin whose small leftover (say 3..18) no
future item can use, wasting capacity.  We keep the tight-fit ordering
by residual and apply a surcharge to residuals in a "waste" band just
above 0.  Additionally, near-ties in residual are broken by preferring
the bin whose leftover residual is a *likely* future item size (so it
can be exactly filled later), using a static histogram of the known
Weibull-shaped item-size distribution.
"""
import numpy as np

# Residuals strictly between 0 and this value are treated as wasted slack.
_WASTE_LIMIT = 20.0
_SURCHARGE = 6.0
_TIE_EPS = 1.0
_TIE_WEIGHT = 0.05

# Static histogram over item sizes 1..100 (mean ~40, Weibull-shaped),
# used only as a relative "fillability" weight for residuals.  Values are
# smooth approximations, not tuned to any single instance.
_SIZE = np.arange(1, 101, dtype=np.float64)
_LAMBDA = 2.0
_SCALE = 45.0
_PDF = (_LAMBDA / _SCALE) * (_SIZE / _SCALE) ** (_LAMBDA - 1.0) * np.exp(
    -(_SIZE / _SCALE) ** _LAMBDA)
_PDF = _PDF / _PDF.mean()
# For a residual r (1..100) we score fillability as the PDF at r.
_FILL = np.concatenate(([0.0], _PDF))  # index by residual 1..100

_state = {"tick": 0}


def priority(item, bins):
    residual = bins - item                     # >= 0 for every bin shown
    score = -residual.astype(np.float64)       # base: tightest fit wins
    # Penalise residuals that are small but non-zero (unusable slack).
    waste = (residual > 0) & (residual < _WASTE_LIMIT)
    score -= _SURCHARGE * waste

    if _TIE_EPS > 0.0:
        # Near-ties: prefer a leftover residual that is likely to be
        # exactly fillable by a future item.
        _state["tick"] += 1
        rc = np.clip(residual, 0, 100).astype(np.int64)
        fill = _FILL[rc]
        is_near = np.abs(score - score.max()) <= _TIE_EPS
        score = score + _TIE_WEIGHT * fill * is_near
    return score
# EVOLVE-BLOCK-END
