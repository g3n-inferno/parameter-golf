#!/usr/bin/env bash
# Intent: launch the documented 1xH100 baseline safely and capture a wrapper log.

set -euo pipefail

REPO_DIR="${REPO_DIR:-/workspace/parameter-golf}"
LOG_DIR="${LOG_DIR:-$REPO_DIR/logs/runpod}"
RUN_ID="${RUN_ID:-baseline_sp1024_1gpu}"
DATA_PATH="${DATA_PATH:-$REPO_DIR/data/datasets/fineweb10B_sp1024}"
TOKENIZER_PATH="${TOKENIZER_PATH:-$REPO_DIR/data/tokenizers/fineweb_1024_bpe.model}"
VOCAB_SIZE="${VOCAB_SIZE:-1024}"
VAL_LOSS_EVERY="${VAL_LOSS_EVERY:-1000}"
MAX_WALLCLOCK_SECONDS="${MAX_WALLCLOCK_SECONDS:-600}"

usage() {
  cat <<'EOF'
Usage:
  bash scripts/runpod/run_baseline_1gpu.sh

Optional environment variables:
  REPO_DIR               Remote repo path. Default: /workspace/parameter-golf
  LOG_DIR                Log directory. Default: /workspace/parameter-golf/logs/runpod
  RUN_ID                 Run identifier. Default: baseline_sp1024_1gpu
  DATA_PATH              Dataset path for FineWeb sp1024.
  TOKENIZER_PATH         Tokenizer model path for sp1024.
  VOCAB_SIZE             Tokenizer vocab size. Default: 1024
  VAL_LOSS_EVERY         Validation frequency. Default: 1000
  MAX_WALLCLOCK_SECONDS  Explicit wallclock cap. Default: 600
EOF
}

if [[ "${1:-}" == "--help" ]]; then
  usage
  exit 0
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
if [[ "$gpu_count" -lt 1 ]]; then
  echo "At least one GPU is required." >&2
  exit 1
fi

mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/${RUN_ID}_$(date +%Y%m%d_%H%M%S).log"

cd "$REPO_DIR"

echo "Starting 1xH100 baseline. Logging to $LOG_FILE"
RUN_ID="$RUN_ID" \
DATA_PATH="$DATA_PATH" \
TOKENIZER_PATH="$TOKENIZER_PATH" \
VOCAB_SIZE="$VOCAB_SIZE" \
VAL_LOSS_EVERY="$VAL_LOSS_EVERY" \
MAX_WALLCLOCK_SECONDS="$MAX_WALLCLOCK_SECONDS" \
torchrun --standalone --nproc_per_node=1 train_gpt.py 2>&1 | tee "$LOG_FILE"

exit "${PIPESTATUS[0]}"
