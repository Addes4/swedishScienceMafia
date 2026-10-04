# llm-informed-v1: what the final programs do (code reading)

Each final `best_program.py` was read in full by the analysing session after the audit. The rules were
fixed in PROTOCOL.md before any run:
- (a) **uses the item count:** it reads `len(bins)` on the first call, or equivalent, and the number of
  remaining items changes its decisions;
- (b) **tracks every open bin**, including those the item does not fit in;
- (c) **SS-like objective:** a convex penalty on the number of open bins per gap;
- (d) **end-game rule:** the decision rule changes as the end approaches.

## Informed runs (this study)

| Run | Lines | (a) item count | (b) tracks open bins | (c) SS-like | (d) end game | What it does |
|---|---|---|---|---|---|---|
| s0 | 137 | **yes**: `_N_ITEMS = len(bins)` on the first call; a best-fit weight grows with the fraction of items seen | no | no | partial: a linear schedule over the whole sequence, not an end-game switch | Scores each bin by the distance of the residual to "attractive" residuals: frequent sizes and their complements. Adds single-item and two-item closability bonuses from the size histogram |
| s1 | 130 | attempted, **broken**: it re-initialises all state whenever `len(bins)` changes, which is most calls | no: allocates a per-bin array but never updates it | no | no | Best fit, plus penalties for residuals below the median size and bonuses for residuals with high histogram mass. Its histogram keeps resetting |
| s2 | 123 | no | no | no | no | Best fit, plus a bonus when the residual matches a frequent size, a sliver penalty and a band kernel; tables rebuilt every 200 items |
| s3 | 96 | attempted, **wrong**: it takes `len(bins)` at every call as the item count, but after the first call that is the number of fitting bins | no | no | intended ("shrink near the end"), but driven by the wrong count | Best fit scaled by how many small residuals there are, a huge exact-fill bonus, expected future exact fills and two-item fill probabilities |

## Uninformed runs (llm-long-search-v1), for comparison (grep plus a skim)

| Run | Lines | (a) | (b) | (c) | (d) |
|---|---|---|---|---|---|
| s0 | 61 | no | no | no | no |
| s1 | 60 | no | no | no | no |
| s2 | 40 | no | no | no | no |
| s3 | 76 | no | no | no | no |

Every uninformed program is best fit plus terms built from a running histogram of item sizes.

## Reading

- **The paragraph changed what the model tried, not what worked.** Three of 4 informed runs reached for
  the item count; none of the uninformed runs did. But only s0 used it correctly, and as a gentle
  weight schedule. s1 and s3 misread `len(bins)` despite the paragraph saying it equals the item count
  only on the first call.
- **No run tracked the open bins** (b), although the paragraph spells out how. So no run could compute
  an SS- or FWSS-style objective, which needs the counts of open bins per gap, including bins the item
  does not fit in.
- **The informed programs are about twice as long** (96–137 lines vs 40–76) and stack many tuned terms.
  That fits their larger gap between public and fresh scores (RESULTS.md).
- **Decision agreement** on the first 10 audit instances is low everywhere (`audit.json`):
  - with SS: 2.1–2.2% (informed) vs 2.2–3.4% (uninformed);
  - with FWSS: 1.4–2.5% vs 1.1–3.4%.

  No program is a near-copy of either.
