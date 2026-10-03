"""FunSearch's published online bin-packing heuristics, verbatim.

Source: github.com/google-deepmind/funsearch, bin_packing/bin_packing.ipynb at commit
cc53f274237d7ab05c19df939edbc1f9616a7c19 (cells "Heursitic discovered for the OR datasets" and
"Heuristic discovered for the Weibull datasets"); the same functions are Figures C.12 and C.14
of the paper's Supplementary Information. Copyright 2023 DeepMind Technologies Limited,
Apache License 2.0. Only the function names differ from the notebook (both are `priority`
there). Copies for the gate are in experiments/bp-ceiling-v1/programs/.
"""
import numpy as np

SOURCE = {'repository': 'https://github.com/google-deepmind/funsearch',
          'path': 'bin_packing/bin_packing.ipynb',
          'commit': 'cc53f274237d7ab05c19df939edbc1f9616a7c19',
          'license': 'Apache-2.0'}


def funsearch_weibull(item: float, bins: np.ndarray) -> np.ndarray:
  """Heuristic discovered for the Weibull datasets."""
  max_bin_cap = max(bins)
  score = (bins - max_bin_cap)**2 / item + bins**2 / (item**2)
  score += bins**2 / item**3
  score[bins > item] = -score[bins > item]
  score[1:] -= score[:-1]
  return score


def funsearch_or(item: float, bins: np.ndarray) -> np.ndarray:
  """Heursitic discovered for the OR datasets."""
  def s(bin, item):
    if bin - item <= 2:
      return 4
    elif (bin - item) <= 3:
      return 3
    elif (bin - item) <= 5:
      return 2
    elif (bin - item) <= 7:
      return 1
    elif (bin - item) <= 9:
      return 0.9
    elif (bin - item) <= 12:
      return 0.95
    elif (bin - item) <= 15:
      return 0.97
    elif (bin - item) <= 18:
      return 0.98
    elif (bin - item) <= 20:
      return 0.98
    elif (bin - item) <= 21:
      return 0.98
    else:
      return 0.99

  return np.array([s(b, item) for b in bins])


def best_fit(item: float, bins: np.ndarray) -> np.ndarray:
  """FunSearch's starting point (the notebook's skeleton priority)."""
  return -(bins - item)


HEURISTICS = {'funsearch_weibull': funsearch_weibull, 'funsearch_or': funsearch_or,
              'best_fit_priority': best_fit}
