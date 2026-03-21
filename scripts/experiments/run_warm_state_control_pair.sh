#!/usr/bin/env bash
# Intent: run the documented 1xH100 control path twice back to back on one unchanged pod/container.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="${REPO_DIR:-$(cd "$SCRIPT_DIR/../.." && pwd)}"
PAIR_ID="${PAIR_ID:-warm_state_control_pair_1xh100}"
RUN1_ID="${RUN1_ID:-${PAIR_ID}_run1}"
RUN2_ID="${RUN2_ID:-${PAIR_ID}_run2}"
LOG_ROOT_BASE="${LOG_ROOT_BASE:-$REPO_DIR/logs/experiments/warm_state_control_pair}"
LOG_ROOT="$LOG_ROOT_BASE/$PAIR_ID"
CANONICAL_BASELINE_COMPARE_JSON="${CANONICAL_BASELINE_COMPARE_JSON:-$REPO_DIR/experiments/baselines/runpod_1xh100_control_anchor_summary.json}"
LEGACY_BASELINE_COMPARE_JSON="$REPO_DIR/experiments/baselines/local_1xh100_baseline_summary.json"
BASELINE_COMPARE_JSON="${BASELINE_COMPARE_JSON:-}"
if [[ -z "$BASELINE_COMPARE_JSON" ]]; then
  if [[ -f "$CANONICAL_BASELINE_COMPARE_JSON" ]]; then
    BASELINE_COMPARE_JSON="$CANONICAL_BASELINE_COMPARE_JSON"
  else
    BASELINE_COMPARE_JSON="$LEGACY_BASELINE_COMPARE_JSON"
  fi
fi
BASELINE_COMPARE_LABEL="${BASELINE_COMPARE_LABEL:-runpod_1xh100_control_anchor}"

usage() {
  cat <<'EOF'
Usage:
  bash scripts/experiments/run_warm_state_control_pair.sh

This wrapper runs the standard 1xH100 control path twice in sequence on one
unchanged pod/container so the second run can test for warm-state effects.

Optional environment variables:
  PAIR_ID                  Pair label. Default: warm_state_control_pair_1xh100
  RUN1_ID                  First run ID. Default: <PAIR_ID>_run1
  RUN2_ID                  Second run ID. Default: <PAIR_ID>_run2
  LOG_ROOT_BASE            Log root. Default: <repo>/logs/experiments/warm_state_control_pair
  TARGET_GPU_LABEL         Free-form GPU label. Default: h100
  DATA_PATH                Dataset path. Default: <repo>/data/datasets/fineweb10B_sp1024
  TOKENIZER_PATH           Tokenizer path. Default: <repo>/data/tokenizers/fineweb_1024_bpe.model
  VAL_LOSS_EVERY           Validation cadence. Default: 200
  MAX_WALLCLOCK_SECONDS    Wallclock cap. Default: 600
EOF
}

if [[ "${1:-}" == "--help" ]]; then
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
EXPERIMENT_HARDWARE="${EXPERIMENT_HARDWARE:-Runpod 1xH100 pod}"
DATA_PATH_VALUE="${DATA_PATH:-$REPO_DIR/data/datasets/fineweb10B_sp1024}"
TOKENIZER_PATH_VALUE="${TOKENIZER_PATH:-$REPO_DIR/data/tokenizers/fineweb_1024_bpe.model}"
VOCAB_SIZE_VALUE="${VOCAB_SIZE:-1024}"
CORE_HPARAMS="${CORE_HPARAMS:-seq1024 9x512 kv4 mlp_mult2 tied_emb baseline_schedule}"
NOTES_PREFIX="${NOTES_PREFIX:-paired warm-state control test on one unchanged pod/container}"

common_env=(
  "LOG_ROOT=$LOG_ROOT"
  "TARGET_GPU_LABEL=$TARGET_GPU_LABEL"
  "DATA_PATH=$DATA_PATH_VALUE"
  "TOKENIZER_PATH=$TOKENIZER_PATH_VALUE"
  "VOCAB_SIZE=$VOCAB_SIZE_VALUE"
  "EXPECTED_TRAIN_SHARDS=${EXPECTED_TRAIN_SHARDS:-80}"
  "ALLOW_PARTIAL_DATA=${ALLOW_PARTIAL_DATA:-0}"
  "TRAIN_LOG_EVERY=${TRAIN_LOG_EVERY:-50}"
  "VAL_LOSS_EVERY=${VAL_LOSS_EVERY:-200}"
  "MAX_WALLCLOCK_SECONDS=${MAX_WALLCLOCK_SECONDS:-600}"
  "EXPERIMENT_HARDWARE=$EXPERIMENT_HARDWARE"
  "DATASET_VARIANT=$DATASET_VARIANT"
  "TOKENIZER_VARIANT=$TOKENIZER_VARIANT"
  "CORE_HPARAMS=$CORE_HPARAMS"
  "TRACK_INTENT=$TRACK_INTENT"
  "WALLCLOCK_TARGET=$WALLCLOCK_TARGET"
  "WORKFLOW_WRAPPER_PATH=$REPO_DIR/scripts/experiments/run_warm_state_control_pair.sh"
  "COMPARE_JSON_PATH=$BASELINE_COMPARE_JSON"
  "COMPARE_JSON_LABEL=$BASELINE_COMPARE_LABEL"
)

mkdir -p "$LOG_ROOT"

create_ledger_row() {
  local run_id="$1"
  local note="$2"
  "$PYTHON_BIN" "$REPO_DIR/scripts/experiments/new_experiment.py" \
    --run-id "$run_id" \
    --dataset-variant "$DATASET_VARIANT" \
    --tokenizer-variant "$TOKENIZER_VARIANT" \
    --core-hparams "$CORE_HPARAMS" \
    --hardware "$EXPERIMENT_HARDWARE" \
    --track-intent "$TRACK_INTENT" \
    --code-path "train_gpt.py" \
    --wallclock-target "$WALLCLOCK_TARGET" \
    --notes "$note" \
    --force
}

latest_run_dir_for() {
  local run_id="$1"
  find "$LOG_ROOT" -mindepth 1 -maxdepth 1 -type d -name "*_${run_id}" | sort | tail -n 1
}

run_one() {
  local run_id="$1"
  local note="$2"
  local result_var_name="$3"

  create_ledger_row "$run_id" "$note"

  (
    cd "$REPO_DIR"
    env "RUN_ID=$run_id" "${common_env[@]}" bash "$REPO_DIR/scripts/experiments/run_baseline_1gpu.sh"
  )

  local run_dir
  run_dir="$(latest_run_dir_for "$run_id")"
  if [[ -z "$run_dir" || ! -d "$run_dir" ]]; then
    echo "unable to locate run directory under $LOG_ROOT for $run_id" >&2
    exit 1
  fi

  local log_path="$run_dir/run.log"
  local summary_path="$run_dir/summary.txt"
  local json_path="$run_dir/summary.json"

  local compare_args=()
  if [[ -f "$BASELINE_COMPARE_JSON" ]]; then
    compare_args=(
      "--compare-json" "$BASELINE_COMPARE_JSON"
      "--compare-label" "$BASELINE_COMPARE_LABEL"
    )
  fi

  "$PYTHON_BIN" "$REPO_DIR/scripts/experiments/parse_train_log.py" \
    "$log_path" \
    --label "$run_id" \
    --summary-out "$summary_path" \
    --json-out "$json_path" \
    --require-final-metrics \
    "${compare_args[@]}"

  "$PYTHON_BIN" "$REPO_DIR/scripts/experiments/update_ledger.py" \
    --run-id "$run_id" \
    --summary-json "$json_path"

  "$PYTHON_BIN" "$REPO_DIR/scripts/compliance/check_artifact_size.py" "$json_path"

  printf -v "$result_var_name" '%s' "$run_dir"
}

run1_note="$NOTES_PREFIX; role=run1_of_2; pair_id=$PAIR_ID"
run2_note="$NOTES_PREFIX; role=run2_of_2; pair_id=$PAIR_ID"

RUN1_DIR=""
RUN2_DIR=""
run_one "$RUN1_ID" "$run1_note" RUN1_DIR
run_one "$RUN2_ID" "$run2_note" RUN2_DIR

PAIR_TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
PAIR_DIR="$LOG_ROOT/pairs/${PAIR_TIMESTAMP}_${PAIR_ID}"
mkdir -p "$PAIR_DIR"

"$PYTHON_BIN" "$REPO_DIR/scripts/experiments/summarize_warm_state_pair.py" \
  --pair-label "$PAIR_ID" \
  --run-1-summary "$RUN1_DIR/summary.json" \
  --run-1-provenance "$RUN1_DIR/provenance.json" \
  --run-2-summary "$RUN2_DIR/summary.json" \
  --run-2-provenance "$RUN2_DIR/provenance.json" \
  --json-out "$PAIR_DIR/pair_summary.json" \
  --md-out "$PAIR_DIR/pair_summary.md"

echo "pair_id=$PAIR_ID"
echo "run1_id=$RUN1_ID"
echo "run1_dir=$RUN1_DIR"
echo "run2_id=$RUN2_ID"
echo "run2_dir=$RUN2_DIR"
echo "pair_summary_json=$PAIR_DIR/pair_summary.json"
echo "pair_summary_md=$PAIR_DIR/pair_summary.md"
