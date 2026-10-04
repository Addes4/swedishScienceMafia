#!/bin/sh
# Final runner (07:08, RUN_LOG.md). Session cc asked us to cap all TSP worker pools at 4 processes,
# because the machine's load threatens other sessions' timeout-based LLM runs. The earlier chains
# were drained with a HOLD file. This script waits for the steps already running, then runs every
# missing output of run_confirmatory.sh (plus the exploratory TIDE prefixes) one step at a time with
# a single pool of 3 workers. Test sets come first, then the fresh sets, then TIDE at n = 200.
PY=${PY:-/Users/adriansohrabi/.venvs/ssm-tsp/bin/python}
export TSP_IGNORE_HOLD=1
W=3
for pid in "$@"; do while ps -p "$pid" >/dev/null 2>&1; do sleep 20; done; done
rm -f HOLD
skip() { [ -f "$1" ] && echo "skip $1 (exists)" && return 0; return 1; }
ev() {  # ev <heuristic path> <set path> <tag> [limit]
  name=$(basename "$1" .py)
  skip "results/interface_${name}_$3.json" && return
  if [ -n "$4" ]; then $PY -W ignore eval_interface.py "$1" --dataset "$2" --tag "$3" --workers $W --limit "$4"
  else $PY -W ignore eval_interface.py "$1" --dataset "$2" --tag "$3" --workers $W; fi
}
FAST="nearest_neighbour fi_emit greedy_ls_emit lkh_emit reevo_best ael_best fetched/refineevo_released fetched/clade_released fi_replan nn_rollout"
for n in 50 100 200; do
  skip results/classical_test$n.json || $PY -W ignore run_classical.py --dataset data/mctsahd/test$n.npy --tag test$n
  for h in $FAST; do ev heuristics/$h.py data/mctsahd/test$n.npy test$n; done
done
ev heuristics/tide_appendix.py data/mctsahd/test50.npy test50 200
ev heuristics/tide_appendix.py data/mctsahd/test100.npy test100 30
ev heuristics/mctsahd_gpt4omini_best.py data/mctsahd/test100.npy test100
ev heuristics/mctsahd_gpt4omini_best.py data/mctsahd/test200.npy test200 200
ev heuristics/hifo_best.py data/mctsahd/test100.npy test100 200
ev heuristics/hifo_best.py data/mctsahd/test200.npy test200 50
skip results/lkh_heavy_check_test200.json || $PY lkh_heavy_check.py --k 20 --workers $W
for n in 50 100 200; do
  skip results/lkh_fresh$n.npy || $PY lkh_opt.py --dataset data/fresh$n.npy --out results/lkh_fresh$n.npy --workers $W
  skip results/classical_fresh$n.json || $PY -W ignore run_classical.py --dataset data/fresh$n.npy --tag fresh$n
  for h in $FAST; do ev heuristics/$h.py data/fresh$n.npy fresh$n; done
done
ev heuristics/mctsahd_gpt4omini_best.py data/fresh50.npy fresh50 200
ev heuristics/hifo_best.py data/fresh50.npy fresh50 200
ev heuristics/mctsahd_gpt4omini_best.py data/fresh100.npy fresh100 200
ev heuristics/hifo_best.py data/fresh100.npy fresh100 100
ev heuristics/mctsahd_gpt4omini_best.py data/fresh200.npy fresh200 50
ev heuristics/hifo_best.py data/fresh200.npy fresh200 25
ev heuristics/tide_appendix.py data/mctsahd/test200.npy test200 3
echo "FINAL DONE $(date)"
