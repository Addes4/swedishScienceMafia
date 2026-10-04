#!/usr/bin/env bash
# Launch the four llm-from-ss-v1 runs, at most 3 at a time (see PROTOCOL.md). Run from the repository root.
set -u
PY=${PY:-python}
OUT=experiments/llm-from-ss-v1/runs
mkdir -p "$OUT"
for seed in 0 1 2 3; do
  while [ "$(jobs -rp | wc -l)" -ge 3 ]; do sleep 5; done
  echo "$(date '+%H:%M:%S') start s$seed"
  "$PY" -m autoresearch.loop problems/bin_packing_online_ss --provider hf \
      --model deepseek-ai/DeepSeek-V4.1-Flash:deepinfra \
      --max-iters 300 --budget 0.60 --wall 5400 --gate-workers 1 --seed "$seed" \
      --out "$OUT/s$seed" > "$OUT/s$seed.log" 2>&1 &
done
wait
echo "$(date '+%H:%M:%S') all runs finished"
