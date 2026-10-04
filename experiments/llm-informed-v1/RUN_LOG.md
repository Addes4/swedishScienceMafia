# llm-informed-v1: run log

Times are BST, from `date`.

| Time | Event |
|---|---|
| 05:43:37 | PROTOCOL.md committed (e2e4b81), before any run. |
| 05:43:48 | Launched `run.sh` (4 runs, seeds 0–3, in parallel) at commit e2e4b81, the pre-registration. |
| 05:56 | Coordination: session 2d asked which lanes are taken and then claimed TSP step-by-step construction (exp/tsp-construct, experiments/tsp-construct-v1). It will not touch bin packing, PFSP or MKP. |
| 06:16 | Coordination: session 43, cleaning up the repo with the user's approval, asked to delete origin/exp/online-beyond-ss. I checked that it is fully merged into origin/main (PR #6) and agreed. The local commits 6191b66 and e2e4b81 are unaffected and will be rebased onto main before a PR. |
| 07:17 | All 4 runs finished. s1, s2 and s3 completed 300 steps. s0 stopped at 236 steps at the pre-registered 5,400 s wall limit; the machine was shared and loaded (load average 15–35). Audit started. |
| 07:17–07:27 | `audit.py --workers 6`: 12 programs × 100 instances, all valid. Positive control passed: best fit, FunSearch and the 4 uninformed programs give bins identical to llm-long-search-v1's audit.json. Q1–Q3: 0 of 4 informed runs. Q4: informed mean 1.361% vs uninformed 1.109%, permutation p = 0.46. |
| 07:25 | Code reading (`classification.md`), `runs_table.json`, `summary.json`, RESULTS.md. Post-hoc, not pre-registered: the informed runs' gap between fresh and public excess is larger (+0.23 vs +0.05 pp, permutation p = 0.029). Spend recomputed from usage.jsonl: $1.0719, 1,136 calls, 0 errors. |
| 07:30 | Rebased the branch onto main (after PR #8's docs move). The pre-registration commit e2e4b81 became c1de65d: same author date 05:43:37, identical PROTOCOL.md and problem folder (`git diff e2e4b81 c1de65d` on those paths is empty). The original is kept as tag `prereg/llm-informed-v1`. Tests: 182 passed after the rebase. |
