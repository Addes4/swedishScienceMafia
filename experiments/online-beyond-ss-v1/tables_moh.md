# Amendment 1: FWSS against the MoH/HMACE online bin-packing leaderboard

Excess over L1 (%), lower is better.

- Published columns: MoH Table 2 (arXiv 2505.20881) and HMACE Table 2 (arXiv 2605.07214), each on their own 100 instances per setting.
- Our columns: 100 new instances per setting from the same generator (EoH's), so the two sides are different draws from one distribution.
- Our best fit (BF) is the calibration row against their Best Fit.
- ± is a bootstrap standard error over instances.
- FWSS knows the item count; FWSS-no-finish does not.

| C | n | their BF | our BF | best published (method) | FWSS ± se | FWSS-no-finish | SS | FS-W | calibrated | FWSS < best published | by > 2 se |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 100 | 1000 | 4.621 | 4.623 | 2.543 (MCTS-AHD) | **0.535** ± 0.020 | 3.262 | 2.616 | 3.533 | yes | yes | yes |
| 100 | 5000 | 4.149 | 4.135 | 0.585 (HMACE*) | **0.105** ± 0.004 | 0.648 | 0.566 | 0.710 | yes | yes | yes |
| 100 | 10000 | 4.030 | 4.002 | 0.404 (HMACE*) | **0.052** ± 0.002 | 0.318 | 0.284 | 0.352 | yes | yes | yes |
| 200 | 1000 | 1.825 | 1.840 | 0.819 (HMACE*) | **0.337** ± 0.024 | 2.962 | 0.933 | 7.650 | yes | yes | yes |
| 200 | 5000 | 1.555 | 1.585 | 0.223 (HMACE*) | **0.086** ± 0.004 | 0.602 | 0.190 | 1.746 | yes | yes | yes |
| 200 | 10000 | 1.489 | 1.500 | 0.101 (HMACE*) | **0.041** ± 0.002 | 0.293 | 0.097 | 0.916 | yes | yes | yes |
| 300 | 1000 | 1.131 | 1.078 | 0.581 (MoH) | **0.230** ± 0.034 | 2.014 | 0.595 | 22.036 | yes | yes | yes |
| 300 | 5000 | 0.919 | 0.922 | 0.138 (HMACE*) | **0.051** ± 0.007 | 0.436 | 0.149 | 5.632 | yes | yes | yes |
| 300 | 10000 | 0.882 | 0.877 | 0.055 (HMACE*) | **0.028** ± 0.004 | 0.219 | 0.064 | 3.139 | yes | yes | yes |
| 400 | 1000 | 0.815 | 0.813 | 0.488 (HMACE*) | **0.208** ± 0.040 | 1.726 | 0.555 | 41.561 | yes | yes | yes |
| 400 | 5000 | 0.624 | 0.629 | 0.088 (HMACE*) | **0.032** ± 0.007 | 0.340 | 0.090 | 11.395 | yes | yes | yes |
| 400 | 10000 | 0.603 | 0.591 | 0.038 (HMACE*) | **0.024** ± 0.004 | 0.173 | 0.048 | 6.406 | yes | yes | yes |
| 500 | 1000 | 0.546 | 0.482 | 0.324 (FunSearch) | **0.111** ± 0.036 | 1.446 | 0.358 | 68.199 | yes | yes | yes |
| 500 | 5000 | 0.472 | 0.475 | 0.079 (HMACE*) | **0.030** ± 0.008 | 0.276 | 0.072 | 18.828 | yes | yes | yes |
| 500 | 10000 | 0.448 | 0.451 | 0.020 (HMACE*) | **0.017** ± 0.004 | 0.144 | 0.041 | 11.142 | yes | yes | no |

**FWSS is below the best published number in 15 of 15 calibrated settings** (15 settings run). By more than 2 standard errors of our mean (a stricter view added after the protocol; it ignores the published numbers' own sampling error): 14 of 15.

Average over the 15 settings (the leaderboard's 'Average' row):

| Method | average excess (%) |
|---|---|
| FWSS (ours) | 0.126 |
| SS+finish (ours) | 0.282 |
| HMACE* | 0.441 |
| SS (ours) | 0.444 |
| MoH | 0.453 |
| EoH* | 0.664 |
| EoH | 0.680 |
| CORAL* | 0.755 |
| FunSearch | 0.825 |
| FWSS-no-finish (ours) | 0.990 |
| MCTS-AHD | 1.005 |
| HSEvo | 1.125 |
| ReEvo | 1.240 |
| FS-OR (ours) | 1.423 |
| BF (ours) | 1.600 |
| Best Fit | 1.607 |
| First Fit | 1.729 |
| FS-W (ours) | 13.550 |
