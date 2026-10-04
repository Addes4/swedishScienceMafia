#!/usr/bin/env bash
# Launch the 20 short-horizon-v1 runs, at most 4 at a time (see PROTOCOL.md). Run from the repository root.
set -u
PY=${PY:-python}
OUT=experiments/short-horizon-v1/runs
mkdir -p "$OUT"
jobs_list=()
for seed in 0 1 2 3; do
  for arm in bp_sh_a5000 bp_sh_b200 bp_sh_c80 bp_sh_d_cex bp_sh_e_rand; do
    jobs_list+=("$arm $seed")
  done
done
run_one() {
  local arm=$1 seed=$2 dir="$OUT/$1-s$2"
  [ -f "$dir/report.md" ] && { echo "skip $dir (done)"; return; }
  [ -e "$dir" ] && { echo "skip $dir (exists, unfinished: finish with --report)"; return; }
  "$PY" -m autoresearch.loop "problems/$arm" --provider hf \
      --model deepseek-ai/DeepSeek-V4.1-Flash:deepinfra \
      --max-iters 150 --budget 0.20 --wall 5400 --gate-workers 1 --seed "$seed" \
      --out "$dir" > "$OUT/$arm-s$seed.log" 2>&1
  echo "$(date +%H:%M:%S) finished $dir (exit $?)"
}
export -f run_one; export PY OUT
printf '%s\n' "${jobs_list[@]}" | xargs -P 4 -L 1 bash -c 'run_one $0 $1'
echo "all runs finished $(date +%H:%M:%S)"
