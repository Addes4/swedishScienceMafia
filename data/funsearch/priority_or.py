# Copyright 2023 DeepMind Technologies Limited. Apache-2.0.
import numpy as np

def priority(item: float, bins: np.ndarray) -> np.ndarray:
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
