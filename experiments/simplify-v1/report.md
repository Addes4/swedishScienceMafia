# Discover, simplify, explain

Winner on the selection suite: **counterexample_replay-4** (experiments/local-v1/audit.json), 11 non-zero terms.

Original: `-1*[gap/100] -0.0309017*[(gap/100)^2] +0.160423*[1/(gap+1)] +0.00808476*[0<gap<10] +0.0608273*[0<gap<item] +0.0395306*[gap>=item] -0.0185077*[abs(gap/100-.25)] +0.151592*[abs(gap/100-.5)] +0.83927*[abs(gap/100-.75)] +0.180921*[0<gap<33] -0.630912*[0<gap<50]`

Simplified (11 -> 1 terms, 12000 packing executions): `-1*[gap/100]`

**Rule:** Put each item in the feasible bin that leaves the smallest gap: [-1*[gap/100]] is exactly best-fit.

## Simplification trace (simplification suite)

| step | mean bins |
|---|---|
| start | 41.2450 |
| keep only gap/100 | 41.2450 |

## Confirmation suite (fresh, includes shifted families)

| comparison | mean A | mean B | A-B | 95% CI | W/T/L | identical packings | placement agreement |
|---|---|---|---|---|---|---|---|
| simplified vs original | 40.2850 | 40.2850 | +0.0000 | [+0.0000, +0.0000] | 0/800/0 | 0.999 | 1.0000 |
| simplified vs best-fit | 40.2850 | 40.2850 | +0.0000 | [+0.0000, +0.0000] | 0/800/0 | 1.000 | 1.0000 |
| original vs best-fit | 40.2850 | 40.2850 | +0.0000 | [+0.0000, +0.0000] | 0/800/0 | 0.999 | 1.0000 |

## Ablations of the simplified rule (confirmation suite)

| removed term | weight | mean bin change | 95% CI | instances changed | identical packings |
|---|---|---|---|---|---|
| gap/100 | -1 | +0.3262 | [+0.2925, +0.3625] | 254 | 0.075 |

## Ablations of the original winner (confirmation suite)

| removed term | weight | mean bin change | 95% CI | instances changed | identical packings |
|---|---|---|---|---|---|
| gap/100 | -1 | +0.0037 | [+0.0000, +0.0088] | 3 | 0.927 |
| (gap/100)^2 | -0.0309 | +0.0000 | [+0.0000, +0.0000] | 0 | 1.000 |
| 1/(gap+1) | +0.16 | +0.0000 | [+0.0000, +0.0000] | 0 | 1.000 |
| 0<gap<10 | +0.00808 | +0.0000 | [+0.0000, +0.0000] | 0 | 1.000 |
| 0<gap<item | +0.0608 | +0.0000 | [+0.0000, +0.0000] | 0 | 0.949 |
| gap>=item | +0.0395 | +0.0000 | [+0.0000, +0.0000] | 0 | 1.000 |
| abs(gap/100-.25) | -0.0185 | +0.0000 | [+0.0000, +0.0000] | 0 | 1.000 |
| abs(gap/100-.5) | +0.152 | +0.0000 | [+0.0000, +0.0000] | 0 | 1.000 |
| abs(gap/100-.75) | +0.839 | +0.0037 | [+0.0000, +0.0088] | 3 | 0.966 |
| 0<gap<33 | +0.181 | +0.0000 | [+0.0000, +0.0000] | 0 | 0.998 |
| 0<gap<50 | -0.631 | +0.5238 | [+0.4575, +0.5913] | 250 | 0.043 |

## Witness

No confirmation instance where the simplified rule and best-fit differ in bin count.

## Simplification map (all distinct candidates)

43 candidates, mean 6.74 -> 1.05 terms; 35 reduce to exactly best-fit, 0 to first-fit.

| surviving term | candidates |
|---|---|
| gap/100 | 20 |
| 1/(gap+1) | 15 |
| abs(gap/100-.75) | 4 |
| abs(gap/100-.5) | 2 |
| (gap/100)^2 | 2 |
| gap>=item | 1 |
| 0<gap<33 | 1 |
