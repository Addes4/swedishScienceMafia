#!/bin/sh
# Confirmatory run of tsp-construct-v1 (see PROTOCOL.md). Two chains run in parallel:
#   A: reference checks, LKH on fresh sets, classical constructions, fast interface heuristics
#   B: the slow released heuristics (MCTS-AHD, HiFo-Prompt) on the prefixes fixed in PROTOCOL.md
PY=${PY:-/Users/adriansohrabi/.venvs/ssm-tsp/bin/python}
EI="$PY -W ignore eval_interface.py"
chainA() {
  $PY lkh_heavy_check.py --k 20 --workers 2
  for n in 50 100 200; do $PY lkh_opt.py --dataset data/fresh$n.npy --out results/lkh_fresh$n.npy --workers 2; done
  for s in mctsahd/test50 mctsahd/test100 mctsahd/test200 fresh50 fresh100 fresh200; do
    $PY -W ignore run_classical.py --dataset data/$s.npy --tag $(basename $s)
  done
  for s in mctsahd/test50 mctsahd/test100 mctsahd/test200 fresh50 fresh100 fresh200; do
    for h in nearest_neighbour fi_emit greedy_ls_emit lkh_emit reevo_best ael_best fetched/refineevo_released fetched/clade_released fi_replan nn_rollout; do
      $EI heuristics/$h.py --dataset data/$s.npy --tag $(basename $s) --workers 2
    done
  done
}
chainB() {
  $EI heuristics/mctsahd_gpt4omini_best.py --dataset data/mctsahd/test50.npy --tag test50 --workers 3
  $EI heuristics/hifo_best.py --dataset data/mctsahd/test50.npy --tag test50 --workers 3
  $EI heuristics/mctsahd_gpt4omini_best.py --dataset data/mctsahd/test100.npy --tag test100 --workers 3
  $EI heuristics/hifo_best.py --dataset data/mctsahd/test100.npy --tag test100 --limit 200 --workers 3
  $EI heuristics/mctsahd_gpt4omini_best.py --dataset data/mctsahd/test200.npy --tag test200 --limit 200 --workers 3
  $EI heuristics/hifo_best.py --dataset data/mctsahd/test200.npy --tag test200 --limit 50 --workers 3
  $EI heuristics/mctsahd_gpt4omini_best.py --dataset data/fresh50.npy --tag fresh50 --limit 200 --workers 3
  $EI heuristics/hifo_best.py --dataset data/fresh50.npy --tag fresh50 --limit 200 --workers 3
  $EI heuristics/mctsahd_gpt4omini_best.py --dataset data/fresh100.npy --tag fresh100 --limit 200 --workers 3
  $EI heuristics/hifo_best.py --dataset data/fresh100.npy --tag fresh100 --limit 100 --workers 3
  $EI heuristics/mctsahd_gpt4omini_best.py --dataset data/fresh200.npy --tag fresh200 --limit 50 --workers 3
  $EI heuristics/hifo_best.py --dataset data/fresh200.npy --tag fresh200 --limit 25 --workers 3
}
chainA > results/chainA.log 2>&1 &
chainB > results/chainB.log 2>&1 &
wait
echo "ALL DONE $(date)" >> results/chainA.log
