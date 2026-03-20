#!/usr/bin/env bash
# Intent: run the next leaderboard-informed 1xH100 ablations with consistent logging and ledger updates.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="${REPO_DIR:-$(cd "$SCRIPT_DIR/../.." && pwd)}"
EXPERIMENT_ID="${EXPERIMENT_ID:-${1:-}}"
LOG_ROOT_BASE="${LOG_ROOT_BASE:-$REPO_DIR/logs/experiments/next_1xh100_workstream}"
BASELINE_COMPARE_JSON="${BASELINE_COMPARE_JSON:-$REPO_DIR/experiments/baselines/local_1xh100_baseline_summary.json}"

usage() {
  cat <<'EOF'
Usage:
  bash scripts/experiments/run_1xh100_ablation.sh <experiment_id>

Supported experiment_id values:
  control
  fp16_embed
  lr_warmdown
  compound_ctx1536

This wrapper preserves the documented 1xH100 baseline path and only layers named
env-var ablations on top. It also refreshes experiments/ledger.csv from the
parsed summary JSON and compares each run against the local 1xH100 baseline
anchor when experiments/baselines/local_1xh100_baseline_summary.json exists.
EOF
}

if [[ -z "$EXPERIMENT_ID" || "$EXPERIMENT_ID" == "--help" ]]; then
  usage
  exit 0
fi

find_python() {
  if command -v python3 >/dev/null 2>&1; then
    command -v python3
    return 0
  fi
  if command -v python >/dev/null 2>&1; then
    command -v python
    return 0
  fi
  return 1
}

PYTHON_BIN="$(find_python || true)"
if [[ -z "$PYTHON_BIN" ]]; then
  echo "python3/python not found" >&2
  exit 1
fi

DATASET_VARIANT="${DATASET_VARIANT:-fineweb10B_sp1024}"
TOKENIZER_VARIANT="${TOKENIZER_VARIANT:-fineweb_1024_bpe.model}"
TARGET_GPU_LABEL="${TARGET_GPU_LABEL:-h100}"
TRACK_INTENT="${TRACK_INTENT:-non-record}"
WALLCLOCK_TARGET="${WALLCLOCK_TARGET:-600s}"

common_env=(
  "TARGET_GPU_LABEL=$TARGET_GPU_LABEL"
  "DATA_PATH=${DATA_PATH:-$REPO_DIR/data/datasets/fineweb10B_sp1024}"
  "TOKENIZER_PATH=${TOKENIZER_PATH:-$REPO_DIR/data/tokenizers/fineweb_1024_bpe.model}"
  "VOCAB_SIZE=${VOCAB_SIZE:-1024}"
  "EXPECTED_TRAIN_SHARDS=${EXPECTED_TRAIN_SHARDS:-80}"
  "ALLOW_PARTIAL_DATA=${ALLOW_PARTIAL_DATA:-0}"
  "TRAIN_LOG_EVERY=${TRAIN_LOG_EVERY:-50}"
  "VAL_LOSS_EVERY=${VAL_LOSS_EVERY:-200}"
  "MAX_WALLCLOCK_SECONDS=${MAX_WALLCLOCK_SECONDS:-600}"
)

case "$EXPERIMENT_ID" in
  control)
    RUN_ID="${RUN_ID:-ablate_control_1xh100_1024}"
    CORE_HPARAMS="seq1024 9x512 kv4 mlp_mult2 tied_emb baseline_schedule"
    NOTES="control run near the current local 1xH100 baseline path"
    experiment_env=()
    ;;
  fp16_embed)
    RUN_ID="${RUN_ID:-ablate_fp16_embed_1xh100_1024}"
    CORE_HPARAMS="seq1024 9x512 kv4 mlp_hidden992 keep_float=tok_emb.weight"
    NOTES="leaderboard-informed export ablation: keep tied embedding in fp16 and trim MLP slightly for size headroom"
    experiment_env=(
      "MLP_HIDDEN=992"
      "INT8_KEEP_FLOAT_NAME_PATTERNS=tok_emb.weight"
    )
    ;;
  lr_warmdown)
    RUN_ID="${RUN_ID:-ablate_lr_warmdown_1xh100_1024}"
    CORE_HPARAMS="seq1024 9x512 kv4 mlp_mult2 warmdown3600 matrix_lr0.06"
    NOTES="leaderboard-informed optimization ablation: longer warmdown and higher matrix LR for the under-stepped 1xH100 path"
    experiment_env=(
      "WARMDOWN_ITERS=3600"
      "MATRIX_LR=0.06"
    )
    ;;
  compound_ctx1536)
    RUN_ID="${RUN_ID:-ablate_compound_ctx1536_1xh100}"
    CORE_HPARAMS="seq1536 10x480 kv4 mlp_hidden896 balanced_compound_probe"
    NOTES="balanced scaling probe: slightly deeper, narrower, smaller MLP, and longer context without changing dataset or eval rules"
    experiment_env=(
      "NUM_LAYERS=10"
      "MODEL_DIM=480"
      "MLP_HIDDEN=896"
      "TRAIN_SEQ_LEN=1536"
    )
    ;;
  *)
    echo "unknown experiment_id: $EXPERIMENT_ID" >&2
    usage
    exit 1
    ;;
esac

LOG_ROOT="$LOG_ROOT_BASE/$EXPERIMENT_ID"

"$PYTHON_BIN" "$REPO_DIR/scripts/experiments/new_experiment.py" \
  --run-id "$RUN_ID" \
  --dataset-variant "$DATASET_VARIANT" \
  --tokenizer-variant "$TOKENIZER_VARIANT" \
  --core-hparams "$CORE_HPARAMS" \
  --hardware "1xH100" \
  --track-intent "$TRACK_INTENT" \
  --code-path "train_gpt.py" \
  --wallclock-target "$WALLCLOCK_TARGET" \
  --notes "$NOTES" \
  --force

env_args=("RUN_ID=$RUN_ID" "LOG_ROOT=$LOG_ROOT")
env_args+=("${common_env[@]}")
env_args+=("${experiment_env[@]}")

(
  cd "$REPO_DIR"
  env "${env_args[@]}" bash "$REPO_DIR/scripts/experiments/run_baseline_1gpu.sh"
)

latest_run_dir="$(
  find "$LOG_ROOT" -mindepth 1 -maxdepth 1 -type d -name "*_${RUN_ID}" | sort | tail -n 1
)"
if [[ -z "$latest_run_dir" || ! -d "$latest_run_dir" ]]; then
  echo "unable to locate run directory under $LOG_ROOT for $RUN_ID" >&2
  exit 1
fi

latest_log="$latest_run_dir/run.log"
latest_summary="$latest_run_dir/summary.txt"
latest_json="$latest_run_dir/summary.json"

compare_args=()
if [[ -f "$BASELINE_COMPARE_JSON" ]]; then
  compare_args=(
    "--compare-json" "$BASELINE_COMPARE_JSON"
    "--compare-label" "local_1xh100_baseline"
  )
fi

"$PYTHON_BIN" "$REPO_DIR/scripts/experiments/parse_train_log.py" \
  "$latest_log" \
  --label "$RUN_ID" \
  --summary-out "$latest_summary" \
  --json-out "$latest_json" \
  --require-final-metrics \
  "${compare_args[@]}"

"$PYTHON_BIN" "$REPO_DIR/scripts/experiments/update_ledger.py" \
  --run-id "$RUN_ID" \
  --summary-json "$latest_json"

"$PYTHON_BIN" "$REPO_DIR/scripts/compliance/check_artifact_size.py" "$latest_json"

echo "experiment_id=$EXPERIMENT_ID"
echo "run_id=$RUN_ID"
echo "run_dir=$latest_run_dir"
echo "summary_json=$latest_json"
