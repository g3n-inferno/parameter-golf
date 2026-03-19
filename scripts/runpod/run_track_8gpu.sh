#!/usr/bin/env bash
# Intent: launch a later 8xH100 track run with an explicit confirmation gate.

set -euo pipefail

REPO_DIR="${REPO_DIR:-/workspace/parameter-golf}"
LOG_DIR="${LOG_DIR:-$REPO_DIR/logs/runpod}"
RUN_ID="${RUN_ID:-track_sp1024_8gpu}"
DATA_PATH="${DATA_PATH:-$REPO_DIR/data/datasets/fineweb10B_sp1024}"
TOKENIZER_PATH="${TOKENIZER_PATH:-$REPO_DIR/data/tokenizers/fineweb_1024_bpe.model}"
VOCAB_SIZE="${VOCAB_SIZE:-1024}"
VAL_LOSS_EVERY="${VAL_LOSS_EVERY:-1000}"
MAX_WALLCLOCK_SECONDS="${MAX_WALLCLOCK_SECONDS:-600}"
CONFIRM_TRACK_8GPU="${CONFIRM_TRACK_8GPU:-NO}"

usage() {
  cat <<'EOF'
Usage:
  CONFIRM_TRACK_8GPU=YES bash scripts/runpod/run_track_8gpu.sh

Optional environment variables:
  REPO_DIR               Remote repo path. Default: /workspace/parameter-golf
  LOG_DIR                Log directory. Default: /workspace/parameter-golf/logs/runpod
  RUN_ID                 Run identifier. Default: track_sp1024_8gpu
  DATA_PATH              Dataset path for FineWeb sp1024.
  TOKENIZER_PATH         Tokenizer model path for sp1024.
  VOCAB_SIZE             Tokenizer vocab size. Default: 1024
  VAL_LOSS_EVERY         Validation frequency. Default: 1000
  MAX_WALLCLOCK_SECONDS  Explicit wallclock cap. Default: 600
  CONFIRM_TRACK_8GPU     Must be YES to run.
EOF
}

if [[ "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

if [[ "$CONFIRM_TRACK_8GPU" != "YES" ]]; then
  echo "Refusing to start 8xH100 run without CONFIRM_TRACK_8GPU=YES" >&2
  exit 1
fi

if [[ ! -d "$REPO_DIR/.git" ]]; then
  echo "Expected repo at $REPO_DIR" >&2
  exit 1
fi

if [[ ! -d "$DATA_PATH" || ! -f "$TOKENIZER_PATH" ]]; then
  echo "Dataset or tokenizer missing." >&2
  echo "Run: bash scripts/runpod/download_sp1024.sh" >&2
  exit 1
fi

gpu_count="$(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null | wc -l | tr -d ' ')"
if [[ "$gpu_count" -lt 8 ]]; then
  echo "Expected 8 GPUs, but detected $gpu_count." >&2
  exit 1
fi

mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/${RUN_ID}_$(date +%Y%m%d_%H%M%S).log"

cd "$REPO_DIR"

echo "Starting 8xH100 track run. Logging to $LOG_FILE"
RUN_ID="$RUN_ID" \
DATA_PATH="$DATA_PATH" \
TOKENIZER_PATH="$TOKENIZER_PATH" \
VOCAB_SIZE="$VOCAB_SIZE" \
VAL_LOSS_EVERY="$VAL_LOSS_EVERY" \
MAX_WALLCLOCK_SECONDS="$MAX_WALLCLOCK_SECONDS" \
torchrun --standalone --nproc_per_node=8 train_gpt.py 2>&1 | tee "$LOG_FILE"

exit "${PIPESTATUS[0]}"
