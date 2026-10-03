# Tournament report: full-v1

60 runs, 17 budget-matched (used their cap before any API error). Anthropic spend recorded (live runs): $40.23. Scores are normalized so 1.0 matches the reference value; higher is better. A final score of at least 1 - 1e-6 ties with the reference.

## Full budget: budget-matched runs only

AUC gain: area under the incumbent score over budget fraction [0, 1], minus the starting score, divided by the headroom (1 - starting score).

| problem | arm | runs | final public (mean) | min | max | AUC gain | final hidden | $ spent | calls | idea calls (triage rounds) | evals | valid evals | improvements | $/improvement | wall s | runs at record |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| circle_packing | triage | 2 | 1.0000 | 1.0000 | 1.0000 | 0.7689 | – | 1.0568 | 14.0 | 2.0 | 12.5 | 11.5 | 3.0 | 0.3927 | 879.8 | 2 |
| erdos_squares | lean | 3 | 1.0000 | 1.0000 | 1.0000 | 0.9426 | 1.0000 | 1.0729 | 31.3 | 0.0 | 32.3 | 32.3 | 1.3 | 0.8950 | 716.8 | 3 |
| erdos_squares | lean_gate_patience | 2 | 1.0000 | 1.0000 | 1.0000 | 0.9192 | 1.0000 | 1.0890 | 24.0 | 0.0 | 24.0 | 24.0 | 1.0 | 1.0890 | 778.7 | 2 |
| erdos_squares | shinka | 4 | 1.0000 | 1.0000 | 1.0000 | 0.9329 | 1.0000 | 1.0638 | 27.0 | 0.0 | 15.2 | 15.2 | 1.8 | 0.6671 | 578.8 | 4 |
| erdos_squares | triage | 1 | 1.0000 | 1.0000 | 1.0000 | 0.9057 | 0.9920 | 1.0800 | 7.0 | 1.0 | 7.0 | 5.0 | 1.0 | 1.0800 | 873.9 | 1 |
| sum_difference | shinka | 1 | 0.9469 | 0.9469 | 0.9469 | 0.5018 | – | 1.0768 | 25.0 | 0.0 | 13.0 | 13.0 | 1.0 | 1.0768 | 785.6 | 0 |
| sum_difference | triage | 4 | 0.9470 | 0.9469 | 0.9471 | 0.4661 | – | 1.0685 | 10.8 | 1.8 | 9.2 | 7.8 | 1.2 | 0.9385 | 679.3 | 0 |

### Paired against `shinka`, both runs complete

Sign-flip permutation p-values, Holm-adjusted within each metric across the arms compared.

| metric | arm | n | mean difference | bootstrap 95% CI | P(arm > reference) | 95% CI | wins / ties / losses | p | p (Holm) |
|---|---|---|---|---|---|---|---|---|---|
| auc_gain | lean | 3 | 0.0034 | [-0.0033, 0.0165] | 0.33 | [0.00, 1.00] | 1 / 0 / 2 | 1.000 | 1.000 |
| auc_gain | lean_gate_patience | 2 | -0.0086 | [-0.0137, -0.0036] | 0.00 | [0.00, 0.00] | 0 / 0 / 2 | 0.500 | 1.000 |
| auc_gain | triage | 2 | -0.0110 | [-0.0137, -0.0084] | 0.00 | [0.00, 0.00] | 0 / 0 / 2 | 0.500 | 1.000 |
| final_public | lean | 3 | -0.0000 | [-0.0000, 0.0000] | 0.50 | [0.50, 0.50] | 0 / 3 / 0 | 1.000 | 1.000 |
| final_public | lean_gate_patience | 2 | 0.0000 | [0.0000, 0.0000] | 0.50 | [0.50, 0.50] | 0 / 2 / 0 | 0.500 | 1.000 |
| final_public | triage | 2 | 0.0000 | [0.0000, 0.0000] | 0.50 | [0.50, 0.50] | 0 / 2 / 0 | 1.000 | 1.000 |
| final_hidden | lean | 3 | -0.0000 | [-0.0000, 0.0000] | 0.50 | [0.50, 0.50] | 0 / 3 / 0 | 1.000 | 1.000 |
| final_hidden | lean_gate_patience | 2 | 0.0000 | [0.0000, 0.0000] | 0.50 | [0.50, 0.50] | 0 / 2 / 0 | 0.500 | 1.000 |
| final_hidden | triage | 1 | -0.0080 | – | 0.00 | – | 0 / 0 / 1 | 1.000 | 1.000 |

### Secondary contrasts, both runs complete

| contrast | metric | n | mean difference | bootstrap 95% CI | P(first > second) | 95% CI | wins / ties / losses | p |
|---|---|---|---|---|---|---|---|---|
| lean_gate_patience - lean | auc_gain | 1 | -0.0006 | – | 0.00 | – | 0 / 0 / 1 | 1.000 |
| lean_gate_patience - lean | final_public | 1 | -0.0000 | – | 0.50 | – | 0 / 1 / 0 | 1.000 |

## Common spend checkpoint (every run)

Per problem, the checkpoint is the smallest spend any run reached before an API error (or its cap), rounded down to a multiple of $0.05: circle_packing $0.10, erdos_squares $0.15, sum_difference $0.30. Gain: (score at checkpoint - start) / (1 - start). AUC gain: same for the mean incumbent score over spend [0, checkpoint].

| problem | arm | checkpoint $ | runs | score (mean) | min | max | gain | AUC gain | runs at record |
|---|---|---|---|---|---|---|---|---|---|
| circle_packing | independent | 0.10 | 4 | 0.9998 | 0.9994 | 1.0000 | 0.9997 | 0.5829 | 3 |
| circle_packing | lean | 0.10 | 4 | 0.9692 | 0.9361 | 0.9994 | 0.9533 | 0.7070 | 0 |
| circle_packing | lean_gate_patience | 0.10 | 4 | 0.9820 | 0.9288 | 1.0000 | 0.9703 | 0.7314 | 2 |
| circle_packing | shinka | 0.10 | 4 | 0.8410 | 0.3661 | 1.0000 | 0.7493 | 0.1379 | 2 |
| circle_packing | triage | 0.10 | 4 | 0.5227 | 0.3432 | 0.9685 | 0.2374 | 0.0803 | 0 |
| erdos_squares | independent | 0.15 | 4 | 0.9980 | 0.9921 | 1.0000 | 0.9863 | 0.6532 | 3 |
| erdos_squares | lean | 0.15 | 4 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.6019 | 4 |
| erdos_squares | lean_gate_patience | 0.15 | 4 | 0.9980 | 0.9921 | 1.0000 | 0.9863 | 0.4573 | 3 |
| erdos_squares | shinka | 0.15 | 4 | 0.9941 | 0.9921 | 1.0000 | 0.9588 | 0.5243 | 1 |
| erdos_squares | triage | 0.15 | 4 | 0.9917 | 0.9762 | 1.0000 | 0.9423 | 0.2494 | 2 |
| sum_difference | independent | 0.30 | 4 | 0.9469 | 0.9469 | 0.9469 | 0.5286 | 0.4868 | 0 |
| sum_difference | lean | 0.30 | 4 | 0.9469 | 0.9469 | 0.9469 | 0.5286 | 0.4862 | 0 |
| sum_difference | lean_gate_patience | 0.30 | 4 | 0.9470 | 0.9469 | 0.9470 | 0.5290 | 0.4911 | 0 |
| sum_difference | shinka | 0.30 | 4 | 0.9469 | 0.9469 | 0.9469 | 0.5286 | 0.4336 | 0 |
| sum_difference | triage | 0.30 | 4 | 0.9469 | 0.9469 | 0.9469 | 0.5286 | 0.2988 | 0 |

### Paired against `shinka` at the checkpoint, all problems pooled

Sign-flip permutation p-values, Holm-adjusted within each metric across the arms compared.

| metric | arm | n | mean difference | bootstrap 95% CI | P(arm > reference) | 95% CI | wins / ties / losses | p | p (Holm) |
|---|---|---|---|---|---|---|---|---|---|
| auc_gain | independent | 12 | 0.2091 | [0.1037, 0.3212] | 0.92 | [0.75, 1.00] | 11 / 0 / 1 | 0.001 | 0.006 |
| auc_gain | lean | 12 | 0.2331 | [0.0963, 0.3864] | 0.83 | [0.58, 1.00] | 10 / 0 / 2 | 0.002 | 0.007 |
| auc_gain | lean_gate_patience | 12 | 0.1947 | [0.0339, 0.3746] | 0.75 | [0.50, 1.00] | 9 / 0 / 3 | 0.070 | 0.070 |
| auc_gain | triage | 12 | -0.1558 | [-0.2543, -0.0456] | 0.08 | [0.00, 0.25] | 1 / 0 / 11 | 0.019 | 0.038 |
| gain | independent | 12 | 0.0926 | [0.0005, 0.2594] | 0.58 | [0.38, 0.79] | 4 / 6 / 2 | 0.109 | 0.438 |
| gain | lean | 12 | 0.0817 | [-0.0219, 0.2588] | 0.54 | [0.33, 0.75] | 4 / 5 / 3 | 0.531 | 1.000 |
| gain | lean_gate_patience | 12 | 0.0830 | [-0.0195, 0.2590] | 0.71 | [0.54, 0.88] | 6 / 5 / 1 | 0.516 | 1.000 |
| gain | triage | 12 | -0.1761 | [-0.4990, 0.1436] | 0.33 | [0.12, 0.54] | 2 / 4 / 6 | 0.211 | 0.633 |

### Secondary contrasts at the checkpoint

| contrast | metric | n | mean difference | bootstrap 95% CI | P(first > second) | 95% CI | wins / ties / losses | p |
|---|---|---|---|---|---|---|---|---|
| lean_gate_patience - lean | auc_gain | 12 | -0.0385 | [-0.1146, 0.0156] | 0.50 | [0.25, 0.75] | 6 / 0 / 6 | 0.379 |
| lean_gate_patience - lean | gain | 12 | 0.0012 | [-0.0290, 0.0310] | 0.54 | [0.29, 0.79] | 5 / 3 / 4 | 0.898 |
| lean - independent | auc_gain | 12 | 0.0240 | [-0.0454, 0.1076] | 0.50 | [0.25, 0.75] | 6 / 0 / 6 | 0.611 |
| lean - independent | gain | 12 | -0.0109 | [-0.0346, 0.0091] | 0.54 | [0.33, 0.75] | 4 / 5 / 3 | 0.375 |

## Runs

$ spent includes reservations charged for calls whose billing was unknown. Last public / hidden: the run's last incumbent, which for a truncated run is not a full-budget result. AUC gain over the full budget is shown for complete runs only.

| run | completion | $ spent | valid to $ | cap | calls | failed calls | evals | start | last public | last hidden | AUC gain |
|---|---|---|---|---|---|---|---|---|---|---|---|
| independent__circle_packing__s0 | truncated_api_error | 0.1363 | 0.1363 | 1.10 | 10 | 6 | 5 | 0.3806 | 1.0000 | – | n/a |
| independent__circle_packing__s1 | truncated_api_error | 0.1264 | 0.1264 | 1.10 | 10 | 6 | 5 | 0.3305 | 1.0000 | – | n/a |
| independent__circle_packing__s2 | truncated_api_error | 0.1333 | 0.1333 | 1.10 | 10 | 6 | 5 | 0.3769 | 1.0000 | – | n/a |
| independent__circle_packing__s3 | truncated_api_error | 0.1277 | 0.1277 | 1.10 | 10 | 6 | 5 | 0.3612 | 0.9994 | – | n/a |
| lean__circle_packing__s0 | truncated_api_error | 0.1345 | 0.1345 | 1.10 | 10 | 6 | 5 | 0.3480 | 0.9570 | – | n/a |
| lean__circle_packing__s1 | truncated_api_error | 0.1255 | 0.1255 | 1.10 | 10 | 6 | 5 | 0.3347 | 0.9421 | – | n/a |
| lean__circle_packing__s2 | truncated_api_error | 0.1423 | 0.1423 | 1.10 | 10 | 6 | 5 | 0.3115 | 0.9994 | – | n/a |
| lean__circle_packing__s3 | truncated_api_error | 0.1510 | 0.1510 | 1.10 | 10 | 6 | 5 | 0.3516 | 0.9994 | – | n/a |
| lean_gate_patience__circle_packing__s0 | truncated_api_error | 0.1279 | 0.1279 | 1.10 | 10 | 6 | 5 | 0.3777 | 1.0000 | – | n/a |
| lean_gate_patience__circle_packing__s1 | truncated_api_error | 0.1198 | 0.1198 | 1.10 | 10 | 6 | 5 | 0.3695 | 1.0000 | – | n/a |
| lean_gate_patience__circle_packing__s2 | truncated_api_error | 0.1529 | 0.1529 | 1.10 | 10 | 6 | 5 | 0.3952 | 0.9444 | – | n/a |
| lean_gate_patience__circle_packing__s3 | truncated_api_error | 0.1050 | 0.1050 | 1.10 | 10 | 6 | 5 | 0.3548 | 0.9994 | – | n/a |
| shinka__circle_packing__s0 | truncated_api_error | 0.3237 | 0.3237 | 1.10 | 1059 | 1049 | 9 | 0.3570 | 1.0000 | – | n/a |
| shinka__circle_packing__s1 | truncated_api_error | 0.3728 | 0.3728 | 1.10 | 1643 | 1634 | 10 | 0.3566 | 1.0000 | – | n/a |
| shinka__circle_packing__s2 | truncated_api_error | 0.6022 | 0.6022 | 1.10 | 1043 | 1019 | 13 | 0.3514 | 1.0000 | – | n/a |
| shinka__circle_packing__s3 | truncated_api_error | 0.4326 | 0.4326 | 1.10 | 1654 | 1645 | 10 | 0.3661 | 1.0000 | – | n/a |
| triage__circle_packing__s0 | truncated_api_error | 0.8967 | 0.8967 | 1.10 | 16 | 1 | 14 | 0.3432 | 1.0000 | – | n/a |
| triage__circle_packing__s1 | truncated_api_error | 0.6818 | 0.6818 | 1.10 | 16 | 1 | 14 | 0.3852 | 1.0000 | – | n/a |
| triage__circle_packing__s2 | budget | 1.0285 | 1.0285 | 1.10 | 14 | 0 | 13 | 0.3938 | 1.0000 | – | 0.6132 |
| triage__circle_packing__s3 | budget | 1.0851 | 1.0851 | 1.10 | 14 | 0 | 12 | 0.3724 | 1.0000 | – | 0.9246 |
| independent__erdos_squares__s0 | truncated_api_error | 1.1000 | 0.9005 | 1.10 | 17 | 1 | 17 | 0.8562 | 1.0000 | 1.0000 | n/a |
| independent__erdos_squares__s1 | truncated_api_error | 0.9849 | 0.6568 | 1.10 | 19 | 6 | 14 | 0.8562 | 1.0000 | 1.0000 | n/a |
| independent__erdos_squares__s2 | truncated_api_error | 0.4079 | 0.4079 | 1.10 | 14 | 6 | 9 | 0.8562 | 1.0000 | 1.0000 | n/a |
| independent__erdos_squares__s3 | truncated_api_error | 1.0574 | 0.7293 | 1.10 | 19 | 6 | 14 | 0.8562 | 1.0000 | 1.0000 | n/a |
| lean__erdos_squares__s0 | budget | 1.0672 | 1.0672 | 1.10 | 28 | 0 | 29 | 0.8562 | 1.0000 | 1.0000 | 0.9389 |
| lean__erdos_squares__s1 | budget | 1.0722 | 1.0722 | 1.10 | 36 | 0 | 37 | 0.8562 | 1.0000 | 1.0000 | 0.9385 |
| lean__erdos_squares__s2 | truncated_api_error | 0.1901 | 0.1901 | 1.10 | 9 | 6 | 4 | 0.8562 | 1.0000 | 1.0000 | n/a |
| lean__erdos_squares__s3 | budget | 1.0793 | 1.0793 | 1.10 | 30 | 0 | 31 | 0.8562 | 1.0000 | 1.0000 | 0.9503 |
| lean_gate_patience__erdos_squares__s0 | truncated_api_error | 0.3943 | 0.3943 | 1.10 | 14 | 6 | 9 | 0.8562 | 1.0000 | 1.0000 | n/a |
| lean_gate_patience__erdos_squares__s1 | budget | 1.0920 | 1.0920 | 1.10 | 25 | 0 | 25 | 0.8562 | 1.0000 | 1.0000 | 0.9379 |
| lean_gate_patience__erdos_squares__s2 | budget | 1.0861 | 1.0861 | 1.10 | 23 | 0 | 23 | 0.8562 | 1.0000 | 1.0000 | 0.9004 |
| lean_gate_patience__erdos_squares__s3 | truncated_api_error | 0.7773 | 0.7773 | 1.10 | 20 | 6 | 15 | 0.8562 | 1.0000 | 0.9980 | n/a |
| shinka__erdos_squares__s0 | budget | 1.0815 | 1.0815 | 1.10 | 24 | 0 | 12 | 0.8562 | 1.0000 | 1.0000 | 0.9422 |
| shinka__erdos_squares__s1 | budget | 1.0533 | 1.0533 | 1.10 | 28 | 0 | 16 | 0.8562 | 1.0000 | 1.0000 | 0.9415 |
| shinka__erdos_squares__s2 | budget | 1.0721 | 1.0721 | 1.10 | 26 | 0 | 14 | 0.8562 | 1.0000 | 1.0000 | 0.9141 |
| shinka__erdos_squares__s3 | budget | 1.0485 | 1.0485 | 1.10 | 30 | 0 | 19 | 0.8562 | 1.0000 | 1.0000 | 0.9338 |
| triage__erdos_squares__s0 | truncated_api_error | 0.8052 | 0.8052 | 1.10 | 8 | 1 | 7 | 0.8562 | 1.0000 | 1.0000 | n/a |
| triage__erdos_squares__s1 | truncated_api_error | 1.1000 | 0.9500 | 1.10 | 14 | 1 | 12 | 0.8562 | 1.0000 | 1.0000 | n/a |
| triage__erdos_squares__s2 | budget | 1.0800 | 1.0800 | 1.10 | 7 | 0 | 7 | 0.8562 | 1.0000 | 0.9920 | 0.9057 |
| triage__erdos_squares__s3 | truncated_api_error | 0.6984 | 0.6984 | 1.10 | 9 | 2 | 7 | 0.8562 | 1.0000 | 1.0000 | n/a |
| independent__sum_difference__s0 | truncated_api_error | 0.4877 | 0.4877 | 1.10 | 27 | 6 | 22 | 0.8874 | 0.9469 | – | n/a |
| independent__sum_difference__s1 | truncated_api_error | 0.6189 | 0.6189 | 1.10 | 35 | 6 | 30 | 0.8874 | 0.9469 | – | n/a |
| independent__sum_difference__s2 | truncated_api_error | 0.5661 | 0.5661 | 1.10 | 30 | 6 | 25 | 0.8874 | 0.9469 | – | n/a |
| independent__sum_difference__s3 | truncated_api_error | 0.8561 | 0.5272 | 1.10 | 29 | 6 | 24 | 0.8874 | 0.9469 | – | n/a |
| lean__sum_difference__s0 | truncated_api_error | 0.3959 | 0.3959 | 1.10 | 13 | 6 | 8 | 0.8874 | 0.9469 | – | n/a |
| lean__sum_difference__s1 | truncated_api_error | 0.4757 | 0.4757 | 1.10 | 13 | 6 | 8 | 0.8874 | 0.9469 | – | n/a |
| lean__sum_difference__s2 | truncated_api_error | 0.4539 | 0.4539 | 1.10 | 14 | 6 | 9 | 0.8874 | 0.9471 | – | n/a |
| lean__sum_difference__s3 | truncated_api_error | 0.8115 | 0.4741 | 1.10 | 14 | 6 | 9 | 0.8874 | 0.9469 | – | n/a |
| lean_gate_patience__sum_difference__s0 | truncated_api_error | 0.6624 | 0.3276 | 1.10 | 14 | 6 | 9 | 0.8874 | 0.9469 | – | n/a |
| lean_gate_patience__sum_difference__s1 | truncated_api_error | 0.3282 | 0.3282 | 1.10 | 14 | 6 | 9 | 0.8874 | 0.9470 | – | n/a |
| lean_gate_patience__sum_difference__s2 | truncated_api_error | 0.7497 | 0.4089 | 1.10 | 14 | 6 | 9 | 0.8874 | 0.9471 | – | n/a |
| lean_gate_patience__sum_difference__s3 | truncated_api_error | 0.5847 | 0.5847 | 1.10 | 15 | 6 | 10 | 0.8874 | 0.9469 | – | n/a |
| shinka__sum_difference__s0 | truncated_api_error | 0.9953 | 0.9953 | 1.10 | 2493 | 2475 | 12 | 0.8874 | 0.9469 | – | n/a |
| shinka__sum_difference__s1 | truncated_api_error | 0.9671 | 0.9671 | 1.10 | 2435 | 2412 | 12 | 0.8874 | 0.9469 | – | n/a |
| shinka__sum_difference__s2 | budget | 1.0768 | 1.0768 | 1.10 | 25 | 0 | 13 | 0.8874 | 0.9469 | – | 0.5018 |
| shinka__sum_difference__s3 | truncated_api_error | 0.6760 | 0.6760 | 1.10 | 2166 | 2144 | 11 | 0.8874 | 0.9469 | – | n/a |
| triage__sum_difference__s0 | budget | 1.0399 | 1.0399 | 1.10 | 14 | 0 | 13 | 0.8874 | 0.9471 | – | 0.4579 |
| triage__sum_difference__s1 | budget | 1.0817 | 1.0817 | 1.10 | 14 | 0 | 12 | 0.8874 | 0.9469 | – | 0.4440 |
| triage__sum_difference__s2 | budget | 1.0672 | 1.0672 | 1.10 | 9 | 0 | 8 | 0.8874 | 0.9469 | – | 0.4881 |
| triage__sum_difference__s3 | budget | 1.0852 | 1.0852 | 1.10 | 6 | 0 | 4 | 0.8874 | 0.9469 | – | 0.4743 |
