#!/bin/sh
# Chain C (added 06:39, RUN_LOG.md): chain A's fast steps in reverse order, each skipped if its output
# exists, so they run while chain A waits on the heavy LKH check. The commands are those of
# run_confirmatory.sh; only the order differs.
PY=${PY:-/Users/adriansohrabi/.venvs/ssm-tsp/bin/python}
EI="$PY -W ignore eval_interface.py"
skip() { [ -f "$1" ] && echo "skip $1 (exists)" && return 0; return 1; }
for s in fresh200 fresh100 fresh50 mctsahd/test200 mctsahd/test100 mctsahd/test50; do
  t=$(basename $s)
  case $t in fresh*) n=${t#fresh}; skip results/lkh_fresh$n.npy || $PY lkh_opt.py --dataset data/fresh$n.npy --out results/lkh_fresh$n.npy --workers 2;; esac
  skip results/classical_$t.json || $PY -W ignore run_classical.py --dataset data/$s.npy --tag $t
  for h in nn_rollout fi_replan fetched/clade_released fetched/refineevo_released ael_best reevo_best lkh_emit greedy_ls_emit fi_emit nearest_neighbour; do
    name=$(basename $h)
    skip results/interface_${name}_$t.json || $EI heuristics/$h.py --dataset data/$s.npy --tag $t --workers 2
  done
done
echo "CHAIN C DONE $(date)"
