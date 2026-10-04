#!/bin/sh
# Fact-check follow-up (RUN_LOG.md): uncached variants of the two cached interface methods.
PY=${PY:-/Users/adriansohrabi/.venvs/ssm-tsp/bin/python}
export TSP_IGNORE_HOLD=1
for h in greedy_ls_emit_nocache lkh_emit_nocache; do
  $PY -W ignore eval_interface.py heuristics/$h.py --dataset data/mctsahd/test50.npy --tag test50 --workers 6
  $PY -W ignore eval_interface.py heuristics/$h.py --dataset data/mctsahd/test100.npy --tag test100 --limit 200 --workers 6
  $PY -W ignore eval_interface.py heuristics/$h.py --dataset data/mctsahd/test200.npy --tag test200 --limit 50 --workers 6
done
echo "NOCACHE DONE $(date)"
