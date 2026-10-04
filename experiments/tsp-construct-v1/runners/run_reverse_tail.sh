#!/bin/sh
# Second runner (RUN_LOG.md): after session cc's timeout-sensitive runs finished, the remaining steps of
# run_final.sh are also taken from the end, in reverse order, with 5 workers. Each step is skipped if its
# output exists, so the two runners meet in the middle with at most one duplicated step.
PY=${PY:-/Users/adriansohrabi/.venvs/ssm-tsp/bin/python}
export TSP_IGNORE_HOLD=1
W=5
skip() { [ -f "$1" ] && echo "skip $1 (exists)" && return 0; return 1; }
ev() { name=$(basename "$1" .py); skip "results/interface_${name}_$3.json" && return
  if [ -n "$4" ]; then $PY -W ignore eval_interface.py "$1" --dataset "$2" --tag "$3" --workers $W --limit "$4"
  else $PY -W ignore eval_interface.py "$1" --dataset "$2" --tag "$3" --workers $W; fi; }
ev heuristics/tide_appendix.py data/mctsahd/test200.npy test200 3
ev heuristics/hifo_best.py data/fresh200.npy fresh200 25
ev heuristics/mctsahd_gpt4omini_best.py data/fresh200.npy fresh200 50
ev heuristics/hifo_best.py data/fresh100.npy fresh100 100
ev heuristics/mctsahd_gpt4omini_best.py data/fresh100.npy fresh100 200
ev heuristics/hifo_best.py data/fresh50.npy fresh50 200
ev heuristics/mctsahd_gpt4omini_best.py data/fresh50.npy fresh50 200
for n in 200 100 50; do
  skip results/lkh_fresh$n.npy || $PY lkh_opt.py --dataset data/fresh$n.npy --out results/lkh_fresh$n.npy --workers $W
  skip results/classical_fresh$n.json || $PY -W ignore run_classical.py --dataset data/fresh$n.npy --tag fresh$n
  for h in nn_rollout fi_replan fetched/clade_released fetched/refineevo_released ael_best reevo_best lkh_emit greedy_ls_emit fi_emit nearest_neighbour; do
    ev heuristics/$h.py data/fresh$n.npy fresh$n
  done
done
echo "REVERSE TAIL DONE $(date)"
