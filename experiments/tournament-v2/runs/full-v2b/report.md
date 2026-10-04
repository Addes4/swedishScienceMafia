# Tournament report: full-v2b

60 runs, 47 budget-matched (used their cap before any API error). Anthropic spend recorded (live runs): $8.04. Scores are normalized so 1.0 matches the reference value; higher is better. A final score of at least 1 - 1e-6 ties with the reference.

## Full budget: budget-matched runs only

AUC gain: area under the incumbent score over budget fraction [0, 1], minus the starting score, divided by the headroom (1 - starting score).

| problem | arm | runs | final public (mean) | min | max | AUC gain | final hidden | $ spent | calls | idea calls (triage rounds) | evals | valid evals | improvements | $/improvement | evals hitting a time limit | wall s | runs at record |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| bin_packing_online | independent | 4 | 0.9797 | 0.9654 | 0.9910 | 0.2672 | 0.9795 | 0.1485 | 276.2 | 0.0 | 276.8 | 268.2 | 2.0 | 0.0743 | 3.0 | 4845.6 | 0 |
| bin_packing_online | lean | 4 | 0.9831 | 0.9640 | 0.9927 | 0.3185 | 0.9818 | 0.1470 | 188.5 | 0.0 | 189.5 | 185.2 | 11.8 | 0.0203 | 1.0 | 1560.7 | 0 |
| bin_packing_online | lean_gate_patience | 4 | 0.9825 | 0.9642 | 0.9927 | 0.4230 | 0.9822 | 0.1474 | 222.0 | 0.0 | 222.8 | 212.8 | 4.5 | 0.0707 | 3.0 | 1678.6 | 0 |
| bin_packing_online | shinka | 4 | 0.9755 | 0.9616 | 0.9920 | 0.3063 | 0.9747 | 0.1467 | 174.2 | 0.0 | 81.5 | 79.0 | 2.2 | 0.0817 | 0.0 | 834.0 | 0 |
| bin_packing_online | triage | 4 | 0.9618 | 0.9616 | 0.9619 | 0.0015 | 0.9607 | 0.1344 | 48.8 | 7.0 | 42.2 | 25.5 | 1.0 | 0.0662 | 5.0 | 1445.9 | 0 |
| erdos_squares | independent | 4 | 0.9717 | 0.9582 | 0.9920 | 0.6653 | 0.8331 | 0.1489 | 76.0 | 0.0 | 76.8 | 59.0 | 3.0 | 0.0571 | 19.0 | 7009.3 | 0 |
| erdos_squares | lean | 2 | 0.9940 | 0.9881 | 1.0000 | 0.8271 | 0.1250 | 0.1469 | 48.0 | 0.0 | 48.0 | 40.5 | 7.0 | 0.0214 | 24.5 | 5126.4 | 1 |
| erdos_squares | lean_gate_patience | 4 | 0.9778 | 0.9570 | 1.0000 | 0.7605 | 0.5480 | 0.1473 | 52.2 | 0.0 | 52.8 | 48.2 | 4.0 | 0.0424 | 16.0 | 5719.8 | 1 |
| erdos_squares | shinka | 4 | 0.9965 | 0.9917 | 1.0000 | 0.8515 | 0.9864 | 0.1403 | 53.8 | 0.0 | 26.0 | 23.8 | 4.0 | 0.0427 | 0.2 | 1024.2 | 2 |
| erdos_squares | triage | 4 | 0.9598 | 0.9393 | 0.9984 | 0.5491 | 0.6524 | 0.1357 | 21.8 | 3.2 | 19.0 | 10.0 | 1.8 | 0.0863 | 3.5 | 1341.6 | 0 |
| sum_difference | lean_gate_patience | 1 | 0.8886 | 0.8886 | 0.8886 | 0.0055 | – | 0.1472 | 85.0 | 0.0 | 86.0 | 75.0 | 2.0 | 0.0736 | 5.0 | 6310.2 | 0 |
| sum_difference | shinka | 4 | 0.8928 | 0.8874 | 0.9090 | 0.0192 | – | 0.1444 | 83.5 | 0.0 | 41.2 | 36.5 | 0.8 | 0.0474 | 1.0 | 2469.3 | 0 |
| sum_difference | triage | 4 | 0.9037 | 0.8874 | 0.9350 | 0.0679 | – | 0.1371 | 38.2 | 5.5 | 33.2 | 20.5 | 1.2 | 0.0832 | 4.5 | 2238.5 | 0 |

### Paired against `shinka`, both runs complete

Sign-flip permutation p-values, Holm-adjusted within each metric across the arms compared.

| metric | arm | n | mean difference | bootstrap 95% CI | P(arm > reference) | 95% CI | wins / ties / losses | p | p (Holm) |
|---|---|---|---|---|---|---|---|---|---|
| auc_gain | independent | 8 | -0.1126 | [-0.3352, 0.1141] | 0.25 | [0.00, 0.62] | 2 / 0 / 6 | 0.414 | 1.000 |
| auc_gain | lean | 6 | -0.0037 | [-0.1817, 0.1827] | 0.50 | [0.17, 0.83] | 3 / 0 / 3 | 0.938 | 1.000 |
| auc_gain | lean_gate_patience | 9 | 0.0121 | [-0.2278, 0.2380] | 0.56 | [0.22, 0.89] | 5 / 0 / 4 | 0.941 | 1.000 |
| auc_gain | triage | 12 | -0.1862 | [-0.3465, -0.0406] | 0.50 | [0.25, 0.75] | 5 / 2 / 5 | 0.062 | 0.250 |
| final_public | independent | 8 | -0.0103 | [-0.0241, 0.0049] | 0.38 | [0.12, 0.75] | 3 / 0 / 5 | 0.281 | 0.562 |
| final_public | lean | 6 | 0.0054 | [0.0000, 0.0116] | 0.83 | [0.50, 1.00] | 5 / 0 / 1 | 0.156 | 0.516 |
| final_public | lean_gate_patience | 9 | -0.0051 | [-0.0183, 0.0083] | 0.50 | [0.17, 0.78] | 4 / 1 / 4 | 0.508 | 0.562 |
| final_public | triage | 12 | -0.0132 | [-0.0281, 0.0029] | 0.25 | [0.04, 0.46] | 2 / 2 / 8 | 0.129 | 0.516 |
| final_hidden | independent | 8 | -0.0743 | [-0.2068, 0.0028] | 0.38 | [0.12, 0.75] | 3 / 0 / 5 | 0.188 | 0.562 |
| final_hidden | lean | 6 | -0.2779 | [-0.6067, 0.0089] | 0.67 | [0.33, 1.00] | 4 / 0 / 2 | 0.500 | 0.625 |
| final_hidden | lean_gate_patience | 8 | -0.2155 | [-0.5024, 0.0069] | 0.44 | [0.12, 0.75] | 3 / 1 / 4 | 0.312 | 0.625 |
| final_hidden | triage | 8 | -0.1740 | [-0.4217, -0.0157] | 0.12 | [0.00, 0.38] | 1 / 0 / 7 | 0.016 | 0.062 |

### Secondary contrasts, both runs complete

| contrast | metric | n | mean difference | bootstrap 95% CI | P(first > second) | 95% CI | wins / ties / losses | p |
|---|---|---|---|---|---|---|---|---|
| lean_gate_patience - lean | auc_gain | 6 | 0.0063 | [-0.2040, 0.2157] | 0.50 | [0.17, 0.83] | 3 / 0 / 3 | 0.969 |
| lean_gate_patience - lean | final_public | 6 | -0.0106 | [-0.0252, 0.0053] | 0.33 | [0.00, 0.67] | 2 / 0 / 4 | 0.219 |
| lean - independent | auc_gain | 6 | 0.0952 | [-0.1445, 0.2698] | 0.83 | [0.50, 1.00] | 5 / 0 / 1 | 0.438 |
| lean - independent | final_public | 6 | 0.0131 | [-0.0048, 0.0294] | 0.83 | [0.50, 1.00] | 5 / 0 / 1 | 0.250 |

## Common spend checkpoint (every run)

Per problem, the checkpoint is the smallest spend any run reached before an API error (or its cap), rounded down to a multiple of $0.05: bin_packing_online $0.10, erdos_squares $0.10. Gain: (score at checkpoint - start) / (1 - start). AUC gain: same for the mean incumbent score over spend [0, checkpoint].

| problem | arm | checkpoint $ | runs | score (mean) | min | max | gain | AUC gain | runs at record |
|---|---|---|---|---|---|---|---|---|---|
| bin_packing_online | independent | 0.10 | 4 | 0.9790 | 0.9628 | 0.9910 | 0.4534 | 0.1698 | 0 |
| bin_packing_online | lean | 0.10 | 4 | 0.9807 | 0.9640 | 0.9900 | 0.4962 | 0.2037 | 0 |
| bin_packing_online | lean_gate_patience | 0.10 | 4 | 0.9809 | 0.9642 | 0.9917 | 0.5010 | 0.3796 | 0 |
| bin_packing_online | shinka | 0.10 | 4 | 0.9748 | 0.9616 | 0.9920 | 0.3442 | 0.2864 | 0 |
| bin_packing_online | triage | 0.10 | 4 | 0.9617 | 0.9616 | 0.9619 | 0.0015 | 0.0009 | 0 |
| erdos_squares | independent | 0.10 | 4 | 0.9670 | 0.9582 | 0.9732 | 0.7709 | 0.6074 | 0 |
| erdos_squares | lean | 0.10 | 4 | 0.9618 | 0.8607 | 1.0000 | 0.7345 | 0.6032 | 1 |
| erdos_squares | lean_gate_patience | 0.10 | 4 | 0.9746 | 0.9441 | 1.0000 | 0.8231 | 0.7213 | 1 |
| erdos_squares | shinka | 0.10 | 4 | 0.9918 | 0.9754 | 1.0000 | 0.9426 | 0.7927 | 2 |
| erdos_squares | triage | 0.10 | 4 | 0.9598 | 0.9393 | 0.9984 | 0.7207 | 0.4633 | 0 |

### Paired against `shinka` at the checkpoint, all problems pooled

Sign-flip permutation p-values, Holm-adjusted within each metric across the arms compared.

| metric | arm | n | mean difference | bootstrap 95% CI | P(arm > reference) | 95% CI | wins / ties / losses | p | p (Holm) |
|---|---|---|---|---|---|---|---|---|---|
| auc_gain | independent | 8 | -0.1509 | [-0.3519, 0.0531] | 0.25 | [0.00, 0.62] | 2 / 0 / 6 | 0.227 | 0.680 |
| auc_gain | lean | 8 | -0.1361 | [-0.3836, 0.0806] | 0.38 | [0.00, 0.75] | 3 / 0 / 5 | 0.359 | 0.719 |
| auc_gain | lean_gate_patience | 8 | 0.0109 | [-0.2574, 0.2564] | 0.50 | [0.12, 0.88] | 4 / 0 / 4 | 0.938 | 0.938 |
| auc_gain | triage | 8 | -0.3075 | [-0.4951, -0.1200] | 0.38 | [0.00, 0.75] | 3 / 0 / 5 | 0.062 | 0.250 |
| gain | independent | 8 | -0.0313 | [-0.3099, 0.2612] | 0.38 | [0.12, 0.75] | 3 / 0 / 5 | 0.797 | 1.000 |
| gain | lean | 8 | -0.0281 | [-0.3381, 0.2170] | 0.50 | [0.12, 0.88] | 4 / 0 / 4 | 0.891 | 1.000 |
| gain | lean_gate_patience | 8 | 0.0186 | [-0.2677, 0.2966] | 0.44 | [0.12, 0.75] | 3 / 1 / 4 | 0.914 | 1.000 |
| gain | triage | 8 | -0.2823 | [-0.4871, -0.0961] | 0.25 | [0.00, 0.62] | 2 / 0 / 6 | 0.031 | 0.125 |

### Secondary contrasts at the checkpoint

| contrast | metric | n | mean difference | bootstrap 95% CI | P(first > second) | 95% CI | wins / ties / losses | p |
|---|---|---|---|---|---|---|---|---|
| lean_gate_patience - lean | auc_gain | 8 | 0.1470 | [-0.0502, 0.3605] | 0.62 | [0.25, 0.88] | 5 / 0 / 3 | 0.250 |
| lean_gate_patience - lean | gain | 8 | 0.0467 | [-0.2489, 0.3482] | 0.62 | [0.25, 0.88] | 5 / 0 / 3 | 0.789 |
| lean - independent | auc_gain | 8 | 0.0149 | [-0.1988, 0.1909] | 0.75 | [0.38, 1.00] | 6 / 0 / 2 | 0.906 |
| lean - independent | gain | 8 | 0.0032 | [-0.3412, 0.3167] | 0.62 | [0.25, 0.88] | 5 / 0 / 3 | 0.992 |

## Scores above the best known value

Re-checked by the strict checker in the gate. Only a margin above n x tolerance is worth a human review; nothing here is a claim until reviewed.

| run | instance | score | reference | margin | n x tolerance | worth review |
|---|---|---|---|---|---|---|
| lean_gate_patience__erdos_squares__s3 | n=8 | 2.66666666667 | 2.66666666667 | 4.55e-12 | 8e-09 | False |
| lean_gate_patience__erdos_squares__s3 | n=15 | 3.75000000001 | 3.75 | 1.29e-11 | 1.5e-08 | False |

## Completion and time limits by arm

| arm | budget | incomplete | evaluations | evaluations with an instance at its time limit |
|---|---|---|---|---|
| independent | 8 | 4 | 1626 | 104 |
| lean | 6 | 6 | 1282 | 145 |
| lean_gate_patience | 9 | 3 | 1403 | 94 |
| shinka | 12 | 0 | 595 | 5 |
| triage | 12 | 0 | 378 | 52 |

## Runs

$ spent includes reservations charged for calls whose billing was unknown. Last public / hidden: the run's last incumbent, which for a truncated run is not a full-budget result. AUC gain over the full budget is shown for complete runs only.

| run | completion | $ spent | valid to $ | cap | calls | failed calls | evals | start | last public | last hidden | AUC gain |
|---|---|---|---|---|---|---|---|---|---|---|---|
| independent__bin_packing_online__s0 | budget | 0.1479 | 0.1479 | 0.15 | 249 | 0 | 250 | 0.9616 | 0.9654 | 0.9651 | 0.0401 |
| independent__bin_packing_online__s1 | budget | 0.1492 | 0.1492 | 0.15 | 300 | 0 | 300 | 0.9616 | 0.9910 | 0.9888 | 0.3972 |
| independent__bin_packing_online__s2 | budget | 0.1492 | 0.1492 | 0.15 | 286 | 0 | 286 | 0.9616 | 0.9713 | 0.9712 | 0.1017 |
| independent__bin_packing_online__s3 | budget | 0.1479 | 0.1479 | 0.15 | 270 | 0 | 271 | 0.9616 | 0.9910 | 0.9930 | 0.5300 |
| lean__bin_packing_online__s0 | budget | 0.1470 | 0.1470 | 0.15 | 207 | 0 | 208 | 0.9616 | 0.9922 | 0.9930 | 0.3912 |
| lean__bin_packing_online__s1 | budget | 0.1462 | 0.1462 | 0.15 | 154 | 0 | 155 | 0.9616 | 0.9927 | 0.9905 | 0.4481 |
| lean__bin_packing_online__s2 | budget | 0.1475 | 0.1475 | 0.15 | 173 | 0 | 174 | 0.9616 | 0.9834 | 0.9815 | 0.3821 |
| lean__bin_packing_online__s3 | budget | 0.1474 | 0.1474 | 0.15 | 220 | 0 | 221 | 0.9616 | 0.9640 | 0.9620 | 0.0525 |
| lean_gate_patience__bin_packing_online__s0 | budget | 0.1472 | 0.1472 | 0.15 | 215 | 0 | 216 | 0.9616 | 0.9642 | 0.9627 | 0.0305 |
| lean_gate_patience__bin_packing_online__s1 | budget | 0.1472 | 0.1472 | 0.15 | 221 | 0 | 222 | 0.9616 | 0.9917 | 0.9923 | 0.6869 |
| lean_gate_patience__bin_packing_online__s2 | budget | 0.1475 | 0.1475 | 0.15 | 228 | 0 | 228 | 0.9616 | 0.9927 | 0.9933 | 0.5644 |
| lean_gate_patience__bin_packing_online__s3 | budget | 0.1477 | 0.1477 | 0.15 | 224 | 0 | 225 | 0.9616 | 0.9812 | 0.9806 | 0.4104 |
| shinka__bin_packing_online__s0 | budget | 0.1475 | 0.1475 | 0.15 | 175 | 0 | 81 | 0.9616 | 0.9920 | 0.9930 | 0.7485 |
| shinka__bin_packing_online__s1 | budget | 0.1464 | 0.1464 | 0.15 | 178 | 0 | 82 | 0.9616 | 0.9843 | 0.9815 | 0.4755 |
| shinka__bin_packing_online__s2 | budget | 0.1470 | 0.1470 | 0.15 | 164 | 0 | 80 | 0.9616 | 0.9640 | 0.9639 | 0.0012 |
| shinka__bin_packing_online__s3 | budget | 0.1461 | 0.1461 | 0.15 | 180 | 0 | 83 | 0.9616 | 0.9616 | 0.9604 | 0.0000 |
| triage__bin_packing_online__s0 | budget | 0.1361 | 0.1361 | 0.15 | 49 | 0 | 42 | 0.9616 | 0.9616 | 0.9604 | 0.0000 |
| triage__bin_packing_online__s1 | budget | 0.1367 | 0.1367 | 0.15 | 56 | 0 | 49 | 0.9616 | 0.9616 | 0.9604 | 0.0000 |
| triage__bin_packing_online__s2 | budget | 0.1308 | 0.1308 | 0.15 | 46 | 0 | 40 | 0.9616 | 0.9619 | 0.9609 | 0.0016 |
| triage__bin_packing_online__s3 | budget | 0.1339 | 0.1339 | 0.15 | 44 | 0 | 38 | 0.9616 | 0.9619 | 0.9611 | 0.0043 |
| independent__erdos_squares__s0 | budget | 0.1484 | 0.1484 | 0.15 | 79 | 0 | 80 | 0.8562 | 0.9920 | 0.9652 | 0.6775 |
| independent__erdos_squares__s1 | budget | 0.1493 | 0.1493 | 0.15 | 80 | 0 | 80 | 0.8562 | 0.9721 | 0.4800 | 0.6955 |
| independent__erdos_squares__s2 | budget | 0.1488 | 0.1488 | 0.15 | 75 | 0 | 76 | 0.8562 | 0.9647 | 0.9602 | 0.6133 |
| independent__erdos_squares__s3 | budget | 0.1489 | 0.1489 | 0.15 | 70 | 0 | 71 | 0.8562 | 0.9582 | 0.9268 | 0.6748 |
| lean__erdos_squares__s0 | incomplete | 0.1324 | 0.1324 | 0.15 | 45 | 0 | 46 | 0.8562 | 0.8607 | 0.0000 | n/a |
| lean__erdos_squares__s1 | incomplete | 0.1253 | 0.1253 | 0.15 | 45 | 0 | 45 | 0.8562 | 1.0000 | 0.5000 | n/a |
| lean__erdos_squares__s2 | budget | 0.1465 | 0.1465 | 0.15 | 46 | 0 | 46 | 0.8562 | 0.9881 | 0.0000 | 0.8125 |
| lean__erdos_squares__s3 | budget | 0.1473 | 0.1473 | 0.15 | 50 | 0 | 50 | 0.8562 | 1.0000 | 0.2500 | 0.8417 |
| lean_gate_patience__erdos_squares__s0 | budget | 0.1478 | 0.1478 | 0.15 | 56 | 0 | 56 | 0.8562 | 0.9842 | 0.0000 | 0.8038 |
| lean_gate_patience__erdos_squares__s1 | budget | 0.1460 | 0.1460 | 0.15 | 47 | 0 | 48 | 0.8562 | 1.0000 | 1.0000 | 0.9647 |
| lean_gate_patience__erdos_squares__s2 | budget | 0.1476 | 0.1476 | 0.15 | 49 | 0 | 49 | 0.8562 | 0.9570 | 0.9555 | 0.6121 |
| lean_gate_patience__erdos_squares__s3 | budget | 0.1478 | 0.1478 | 0.15 | 57 | 0 | 58 | 0.8562 | 0.9700 | 0.2364 | 0.6616 |
| shinka__erdos_squares__s0 | budget | 0.1356 | 0.1356 | 0.15 | 53 | 0 | 28 | 0.8562 | 1.0000 | 1.0000 | 0.8855 |
| shinka__erdos_squares__s1 | budget | 0.1405 | 0.1405 | 0.15 | 49 | 0 | 23 | 0.8562 | 1.0000 | 1.0000 | 0.7955 |
| shinka__erdos_squares__s2 | budget | 0.1424 | 0.1424 | 0.15 | 48 | 0 | 24 | 0.8562 | 0.9917 | 0.9722 | 0.8837 |
| shinka__erdos_squares__s3 | budget | 0.1427 | 0.1427 | 0.15 | 65 | 0 | 29 | 0.8562 | 0.9943 | 0.9734 | 0.8412 |
| triage__erdos_squares__s0 | budget | 0.1384 | 0.1384 | 0.15 | 28 | 0 | 25 | 0.8562 | 0.9441 | 0.9555 | 0.5422 |
| triage__erdos_squares__s1 | budget | 0.1244 | 0.1244 | 0.15 | 21 | 0 | 19 | 0.8562 | 0.9984 | 0.0000 | 0.8227 |
| triage__erdos_squares__s2 | budget | 0.1476 | 0.1476 | 0.15 | 21 | 0 | 18 | 0.8562 | 0.9393 | 0.9555 | 0.4495 |
| triage__erdos_squares__s3 | budget | 0.1326 | 0.1326 | 0.15 | 17 | 0 | 14 | 0.8562 | 0.9576 | 0.6985 | 0.3821 |
| independent__sum_difference__s0 | incomplete | 0.0773 | 0.0773 | 0.15 | 65 | 0 | 65 | 0.8874 | 0.8884 | – | n/a |
| independent__sum_difference__s1 | incomplete | 0.0211 | 0.0211 | 0.15 | 22 | 0 | 23 | 0.8874 | 0.8874 | – | n/a |
| independent__sum_difference__s2 | incomplete | 0.0749 | 0.0749 | 0.15 | 60 | 0 | 61 | 0.8874 | 0.9064 | – | n/a |
| independent__sum_difference__s3 | incomplete | 0.0683 | 0.0683 | 0.15 | 62 | 0 | 63 | 0.8874 | 0.8895 | – | n/a |
| lean__sum_difference__s0 | incomplete | 0.1170 | 0.1170 | 0.15 | 85 | 0 | 84 | 0.8874 | 0.8886 | – | n/a |
| lean__sum_difference__s1 | incomplete | 0.1227 | 0.1227 | 0.15 | 81 | 0 | 82 | 0.8874 | 0.9046 | – | n/a |
| lean__sum_difference__s2 | incomplete | 0.1150 | 0.1150 | 0.15 | 74 | 0 | 74 | 0.8874 | 0.9158 | – | n/a |
| lean__sum_difference__s3 | incomplete | 0.1234 | 0.1234 | 0.15 | 96 | 0 | 97 | 0.8874 | 0.9083 | – | n/a |
| lean_gate_patience__sum_difference__s0 | budget | 0.1472 | 0.1472 | 0.15 | 85 | 0 | 86 | 0.8874 | 0.8886 | – | 0.0055 |
| lean_gate_patience__sum_difference__s1 | incomplete | 0.1189 | 0.1189 | 0.15 | 75 | 0 | 76 | 0.8874 | 0.8889 | – | n/a |
| lean_gate_patience__sum_difference__s2 | incomplete | 0.1232 | 0.1232 | 0.15 | 92 | 0 | 92 | 0.8874 | 0.9158 | – | n/a |
| lean_gate_patience__sum_difference__s3 | incomplete | 0.0686 | 0.0686 | 0.15 | 47 | 0 | 47 | 0.8874 | 0.8886 | – | n/a |
| shinka__sum_difference__s0 | budget | 0.1437 | 0.1437 | 0.15 | 88 | 0 | 42 | 0.8874 | 0.8874 | – | 0.0000 |
| shinka__sum_difference__s1 | budget | 0.1459 | 0.1459 | 0.15 | 85 | 0 | 42 | 0.8874 | 0.8874 | – | 0.0000 |
| shinka__sum_difference__s2 | budget | 0.1421 | 0.1421 | 0.15 | 74 | 0 | 39 | 0.8874 | 0.9090 | – | 0.0768 |
| shinka__sum_difference__s3 | budget | 0.1461 | 0.1461 | 0.15 | 87 | 0 | 42 | 0.8874 | 0.8874 | – | 0.0000 |
| triage__sum_difference__s0 | budget | 0.1244 | 0.1244 | 0.15 | 36 | 0 | 32 | 0.8874 | 0.9350 | – | 0.1299 |
| triage__sum_difference__s1 | budget | 0.1474 | 0.1474 | 0.15 | 42 | 0 | 35 | 0.8874 | 0.8874 | – | 0.0000 |
| triage__sum_difference__s2 | budget | 0.1352 | 0.1352 | 0.15 | 33 | 0 | 29 | 0.8874 | 0.9048 | – | 0.1417 |
| triage__sum_difference__s3 | budget | 0.1412 | 0.1412 | 0.15 | 42 | 0 | 37 | 0.8874 | 0.8874 | – | 0.0000 |
