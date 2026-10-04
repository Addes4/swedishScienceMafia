#!/usr/bin/env bash
# Launch the four llm-long-search-v1 runs in parallel (see PROTOCOL.md). Run from the repository root.
set -u
PY=${PY:-python}
OUT=experiments/llm-long-search-v1/runs
mkdir -p "$OUT"
for seed in 0 1 2 3; do
  "$PY" -m autoresearch.loop problems/bin_packing_online --provider hf \
      --model deepseek-ai/DeepSeek-V4.1-Flash:deepinfra \
      --max-iters 300 --budget 0.75 --wall 5400 --gate-workers 2 --seed "$seed" \
      --out "$OUT/s$seed" > "$OUT/s$seed.log" 2>&1 &
done
wait
echo "all runs finished"
