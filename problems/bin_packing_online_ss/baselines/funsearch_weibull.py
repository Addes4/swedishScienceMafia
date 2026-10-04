# FunSearch's published heuristic for the Weibull datasets, verbatim from
# github.com/google-deepmind/funsearch, bin_packing/bin_packing.ipynb (commit
# cc53f274237d7ab05c19df939edbc1f9616a7c19), cell "Heuristic discovered for the Weibull datasets".
# Copyright 2023 DeepMind Technologies Limited, Apache License 2.0.
# Same function as Figure C.14 of the paper's Supplementary Information.
import numpy as np


def priority(item: float, bins: np.ndarray) -> np.ndarray:
  """Heuristic discovered for the Weibull datasets."""
  max_bin_cap = max(bins)
  score = (bins - max_bin_cap)**2 / item + bins**2 / (item**2)
  score += bins**2 / item**3
  score[bins > item] = -score[bins > item]
  score[1:] -= score[:-1]
  return score
