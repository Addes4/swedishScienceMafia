# Tournament report: mock-v1

16 runs. Anthropic spend (live runs only): $0.00. Scores are normalized so 1.0 matches the best known result; higher is better. AUC gain is the area under the best-score-versus-budget-fraction curve, minus the starting score, divided by the headroom (1 - starting score). A run is at the record when its final score is at least 1 - 1e-6; such runs tie with the record, they do not beat it.

| problem | arm | runs | final public (mean) | min | max | AUC gain | final hidden | $ spent | improvements | $/improvement | tokens/improvement | calls | valid evals | evals | wall s | runs at record | within cap |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| circle_packing | lean | 2 | 0.4644 | 0.4125 | 0.5164 | 0.0893 | – | 0.4856 | 3.0 | 0.1619 | 20375.0 | 15.0 | 15.5 | 15.5 | 5.0 | 0 | True |
| circle_packing | lean_gate_patience | 2 | 0.4575 | 0.3911 | 0.5239 | 0.1099 | – | 0.4856 | 3.0 | 0.1619 | 20338.0 | 15.0 | 15.5 | 15.5 | 3.7 | 0 | True |
| circle_packing | shinka | 2 | 0.4743 | 0.4060 | 0.5425 | 0.1296 | – | 0.4920 | 2.5 | 0.2050 | 28887.5 | 15.5 | 11.0 | 11.0 | 20.0 | 0 | True |
| circle_packing | triage | 2 | 0.4529 | 0.3821 | 0.5237 | 0.0523 | – | 0.4819 | 1.5 | 0.1630 | 14784.0 | 12.0 | 10.5 | 10.5 | 2.5 | 0 | True |
| erdos_squares | lean | 2 | 0.8562 | 0.8562 | 0.8562 | 0.0000 | 0.9128 | 0.4911 | 0.0 | – | – | 15.5 | 11.0 | 15.5 | 33.5 | 0 | True |
| erdos_squares | lean_gate_patience | 2 | 0.8562 | 0.8562 | 0.8562 | 0.0000 | 0.9128 | 0.4911 | 0.0 | – | – | 15.5 | 11.0 | 15.5 | 37.3 | 0 | True |
| erdos_squares | shinka | 2 | 0.8562 | 0.8562 | 0.8562 | 0.0000 | 0.9128 | 0.4925 | 0.0 | – | – | 15.5 | 7.5 | 11.0 | 29.4 | 0 | True |
| erdos_squares | triage | 2 | 0.8562 | 0.8562 | 0.8562 | 0.0000 | 0.9128 | 0.4789 | 0.0 | – | – | 11.0 | 7.0 | 10.0 | 8.4 | 0 | True |

## Paired differences against `shinka` (matched problem and seed)

Sign-flip permutation p-values, Holm-adjusted within each metric across the arms compared.

| metric | arm | n | mean difference | bootstrap 95% CI | P(arm > reference) | 95% CI | wins / ties / losses | p | p (Holm) |
|---|---|---|---|---|---|---|---|---|---|
| auc_gain | lean | 4 | -0.0201 | [-0.0403, 0.0000] | 0.25 | [0.00, 0.50] | 0 / 2 / 2 | 0.500 | 1.000 |
| auc_gain | lean_gate_patience | 4 | -0.0098 | [-0.0287, 0.0000] | 0.25 | [0.00, 0.50] | 0 / 2 / 2 | 0.500 | 1.000 |
| auc_gain | triage | 4 | -0.0386 | [-0.0773, 0.0000] | 0.25 | [0.00, 0.50] | 0 / 2 / 2 | 0.500 | 1.000 |
| final_public | lean | 4 | -0.0049 | [-0.0196, 0.0049] | 0.50 | [0.12, 0.88] | 1 / 2 / 1 | 1.000 | 1.000 |
| final_public | lean_gate_patience | 4 | -0.0084 | [-0.0167, 0.0000] | 0.25 | [0.00, 0.50] | 0 / 2 / 2 | 0.500 | 1.000 |
| final_public | triage | 4 | -0.0107 | [-0.0214, 0.0000] | 0.25 | [0.00, 0.50] | 0 / 2 / 2 | 0.500 | 1.000 |
| final_hidden | lean | 2 | 0.0000 | [0.0000, 0.0000] | 0.50 | [0.50, 0.50] | 0 / 2 / 0 | 1.000 | 1.000 |
| final_hidden | lean_gate_patience | 2 | 0.0000 | [0.0000, 0.0000] | 0.50 | [0.50, 0.50] | 0 / 2 / 0 | 1.000 | 1.000 |
| final_hidden | triage | 2 | 0.0000 | [0.0000, 0.0000] | 0.50 | [0.50, 0.50] | 0 / 2 / 0 | 1.000 | 1.000 |

## Secondary contrasts (matched problem and seed)

| contrast | metric | n | mean difference | bootstrap 95% CI | P(first > second) | 95% CI | wins / ties / losses | p |
|---|---|---|---|---|---|---|---|---|
| lean_gate_patience - lean | auc_gain | 4 | 0.0103 | [0.0000, 0.0232] | 0.75 | [0.50, 1.00] | 2 / 2 / 0 | 0.500 |
| lean_gate_patience - lean | final_public | 4 | -0.0035 | [-0.0160, 0.0057] | 0.50 | [0.12, 0.88] | 1 / 2 / 1 | 1.000 |

## Runs

| run | status | $ spent | cap | calls | evals | start | final public | final hidden | AUC gain |
|---|---|---|---|---|---|---|---|---|---|
| lean__circle_packing__s0 | ok | 0.4905 | 0.50 | 16 | 16 | 0.3718 | 0.4125 | – | 0.0271 |
| lean__circle_packing__s1 | ok | 0.4808 | 0.50 | 14 | 15 | 0.3846 | 0.5164 | – | 0.1515 |
| lean_gate_patience__circle_packing__s0 | ok | 0.4905 | 0.50 | 16 | 16 | 0.3432 | 0.3911 | – | 0.0580 |
| lean_gate_patience__circle_packing__s1 | ok | 0.4808 | 0.50 | 14 | 15 | 0.3749 | 0.5239 | – | 0.1619 |
| shinka__circle_packing__s0 | ok | 0.4920 | 0.50 | 16 | 11 | 0.3539 | 0.4060 | – | 0.0591 |
| shinka__circle_packing__s1 | ok | 0.4920 | 0.50 | 15 | 11 | 0.3702 | 0.5425 | – | 0.2001 |
| triage__circle_packing__s0 | ok | 0.4747 | 0.50 | 13 | 12 | 0.3821 | 0.3821 | – | 0.0000 |
| triage__circle_packing__s1 | ok | 0.4891 | 0.50 | 11 | 9 | 0.3393 | 0.5237 | – | 0.1046 |
| lean__erdos_squares__s0 | ok | 0.4910 | 0.50 | 16 | 16 | 0.8562 | 0.8562 | 0.9128 | 0.0000 |
| lean__erdos_squares__s1 | ok | 0.4911 | 0.50 | 15 | 15 | 0.8562 | 0.8562 | 0.9128 | 0.0000 |
| lean_gate_patience__erdos_squares__s0 | ok | 0.4910 | 0.50 | 16 | 16 | 0.8562 | 0.8562 | 0.9128 | 0.0000 |
| lean_gate_patience__erdos_squares__s1 | ok | 0.4911 | 0.50 | 15 | 15 | 0.8562 | 0.8562 | 0.9128 | 0.0000 |
| shinka__erdos_squares__s0 | ok | 0.4925 | 0.50 | 16 | 11 | 0.8562 | 0.8562 | 0.9128 | 0.0000 |
| shinka__erdos_squares__s1 | ok | 0.4925 | 0.50 | 15 | 11 | 0.8562 | 0.8562 | 0.9128 | 0.0000 |
| triage__erdos_squares__s0 | ok | 0.4711 | 0.50 | 11 | 10 | 0.8562 | 0.8562 | 0.9128 | 0.0000 |
| triage__erdos_squares__s1 | ok | 0.4867 | 0.50 | 11 | 10 | 0.8562 | 0.8562 | 0.9128 | 0.0000 |
