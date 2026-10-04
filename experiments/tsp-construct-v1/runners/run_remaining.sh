#!/bin/sh
# Resume the confirmatory run (PROTOCOL.md): the same commands as run_confirmatory.sh, each skipped if
# its output already exists. Written after an incident at 06:31 (RUN_LOG.md) left three pools of the
# first launch waiting forever on lost tasks.
PY=${PY:-/Users/adriansohrabi/.venvs/ssm-tsp/bin/python}
EI="$PY -W ignore eval_interface.py"
skip() { [ -f "$1" ] && echo "skip $1 (exists)" && return 0; return 1; }
ev() {  # ev <heuristic path> <dataset> <tag> <workers> [limit]
  name=$(basename "$1" .py)
  skip "results/interface_${name}_$3.json" && return
  if [ -n "$5" ]; then $EI "$1" --dataset "$2" --tag "$3" --workers "$4" --limit "$5"; else $EI "$1" --dataset "$2" --tag "$3" --workers "$4"; fi
}
chainA() {
  skip results/lkh_heavy_check_test200.json || $PY lkh_heavy_check.py --k 20 --workers 2
  for n in 50 100 200; do skip results/lkh_fresh$n.npy || $PY lkh_opt.py --dataset data/fresh$n.npy --out results/lkh_fresh$n.npy --workers 2; done
  for s in mctsahd/test50 mctsahd/test100 mctsahd/test200 fresh50 fresh100 fresh200; do
    skip results/classical_$(basename $s).json || $PY -W ignore run_classical.py --dataset data/$s.npy --tag $(basename $s)
  done
  for s in mctsahd/test50 mctsahd/test100 mctsahd/test200 fresh50 fresh100 fresh200; do
    for h in nearest_neighbour fi_emit greedy_ls_emit lkh_emit reevo_best ael_best fetched/refineevo_released fetched/clade_released fi_replan nn_rollout; do
      ev heuristics/$h.py data/$s.npy $(basename $s) 2
    done
  done
}
chainB() {
  ev heuristics/mctsahd_gpt4omini_best.py data/mctsahd/test50.npy test50 3
  ev heuristics/hifo_best.py data/mctsahd/test50.npy test50 3
  ev heuristics/mctsahd_gpt4omini_best.py data/mctsahd/test100.npy test100 3
  ev heuristics/hifo_best.py data/mctsahd/test100.npy test100 3 200
  ev heuristics/mctsahd_gpt4omini_best.py data/mctsahd/test200.npy test200 3 200
  ev heuristics/hifo_best.py data/mctsahd/test200.npy test200 3 50
  ev heuristics/mctsahd_gpt4omini_best.py data/fresh50.npy fresh50 3 200
  ev heuristics/hifo_best.py data/fresh50.npy fresh50 3 200
  ev heuristics/mctsahd_gpt4omini_best.py data/fresh100.npy fresh100 3 200
  ev heuristics/hifo_best.py data/fresh100.npy fresh100 3 100
  ev heuristics/mctsahd_gpt4omini_best.py data/fresh200.npy fresh200 3 50
  ev heuristics/hifo_best.py data/fresh200.npy fresh200 3 25
}
chainA > results/resumeA.log 2>&1 &
chainB > results/resumeB.log 2>&1 &
wait
echo "ALL DONE $(date)" >> results/resumeA.log
