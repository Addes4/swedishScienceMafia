# Online bin packing: write the bin-choice rule

Items arrive one at a time and must be placed immediately, without seeing later items, into
bins of capacity 100. Use as few bins as possible.

Write `priority(item, bins)`. It is called once per arriving item:

- `item` is the integer size of the item, 1 to 100.
- `bins` is a numpy int64 array with the remaining capacity of every bin the item fits in.
  There are as many bins as items in the stream; unused bins have remaining capacity 100 and are
  included. Bins appear in a fixed order (bin index), and the array is a copy.
- Return a numpy array (or list) of the same length with one score per bin (no NaN). The
  item goes into the bin with the highest score; ties go to the first such bin.

The harness owns the bins and enforces capacity; your function only ranks the bins it is
shown. It may keep state between calls within a stream (for example statistics of past items),
but it never sees future items. Item sizes are integers drawn independently from one fixed
distribution (Weibull-shaped, mean about 40).

Your rule will be used on long streams of 5,000 items. To keep evaluation fast, candidates are
scored on the evaluation instances listed in the feedback. An instance consists of one or more
independent streams from the same item distribution; the bins and your module's state start
fresh for every stream.

Score per instance: (lower bound on the optimal number of bins) / (bins you used), over the
instance's streams. Higher is better; 1.0 would match the lower bound. The overall score is the
mean over the instances shown. You are also scored on other streams that you never see, so do
not tune to individual instances. Time limit: 60 seconds per instance; numpy is available.
