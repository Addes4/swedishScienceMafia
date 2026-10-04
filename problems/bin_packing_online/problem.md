# Online bin packing: write the bin-choice rule

Items arrive one at a time and must be placed immediately, without seeing later items, into
bins of capacity 100. Use as few bins as possible.

Write `priority(item, bins)`. It is called once per arriving item:

- `item` is the integer size of the item, 1 to 100.
- `bins` is a numpy int64 array with the remaining capacity of every bin the item fits in.
  There are as many bins as items; unused bins have remaining capacity 100 and are included.
  Bins appear in a fixed order (bin index), and the array is a copy.
- Return a numpy array (or list) of the same length with one score per bin (no NaN). The
  item goes into the bin with the highest score; ties go to the first such bin.

The harness owns the bins and enforces capacity; your function only ranks the bins it is
shown. It may keep state between calls (for example statistics of past items), but it never
sees future items. Each instance has 5,000 items with integer sizes drawn independently
from one fixed distribution (Weibull-shaped, mean about 40).

Score per instance: (lower bound on the optimal number of bins) / (bins you used). Higher is
better; 1.0 would match the lower bound. The overall score is the mean over the instances
shown. You are also scored on other instances from the same distribution that you never see,
so do not tune to individual instances. Time limit: 30 seconds per instance (5,000 calls);
numpy is available.
