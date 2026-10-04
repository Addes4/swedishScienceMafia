#!/bin/sh
# Exploratory (RUN_LOG.md): TIDE's Appendix F.1 heuristic on fixed prefixes of MCTS-AHD's test sets.
PY=${PY:-/Users/adriansohrabi/.venvs/ssm-tsp/bin/python}
$PY -W ignore eval_interface.py heuristics/tide_appendix.py --dataset data/mctsahd/test50.npy --tag test50 --limit 200 --workers 3
$PY -W ignore eval_interface.py heuristics/tide_appendix.py --dataset data/mctsahd/test100.npy --tag test100 --limit 30 --workers 3
$PY -W ignore eval_interface.py heuristics/tide_appendix.py --dataset data/mctsahd/test200.npy --tag test200 --limit 3 --workers 3
echo "TIDE DONE $(date)"
