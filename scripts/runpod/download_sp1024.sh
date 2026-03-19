#!/usr/bin/env bash
# Intent: download the documented sp1024 FineWeb cache onto the Pod in a reproducible way.

set -euo pipefail

REPO_DIR="${REPO_DIR:-/workspace/parameter-golf}"
LOG_DIR="${LOG_DIR:-$REPO_DIR/logs/runpod}"
DATASET_DIR="${DATASET_DIR:-$REPO_DIR/data/datasets/fineweb10B_sp1024}"
TOKENIZER_PATH="${TOKENIZER_PATH:-$REPO_DIR/data/tokenizers/fineweb_1024_bpe.model}"
FORCE_DOWNLOAD="${FORCE_DOWNLOAD:-0}"
TRAIN_SHARDS="${TRAIN_SHARDS:-}"

usage() {
  cat <<'EOF'
Usage:
  bash scripts/runpod/download_sp1024.sh

Optional environment variables:
  REPO_DIR         Remote repo path. Default: /workspace/parameter-golf
  LOG_DIR          Log directory. Default: /workspace/parameter-golf/logs/runpod
  DATASET_DIR      Expected dataset directory.
  TOKENIZER_PATH   Expected tokenizer path.
  FORCE_DOWNLOAD   Set to 1 to redownload even if the expected files already exist.
  TRAIN_SHARDS     Optional override passed through as --train-shards.
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

mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/download_sp1024_$(date +%Y%m%d_%H%M%S).log"

if [[ "$FORCE_DOWNLOAD" != "1" && -d "$DATASET_DIR" && -f "$TOKENIZER_PATH" ]]; then
  echo "sp1024 dataset and tokenizer already appear to exist."
  echo "Set FORCE_DOWNLOAD=1 to redownload."
  exit 0
fi

cd "$REPO_DIR"

cmd=(python3 data/cached_challenge_fineweb.py --variant sp1024)
if [[ -n "$TRAIN_SHARDS" ]]; then
  cmd+=(--train-shards "$TRAIN_SHARDS")
fi

echo "Logging to $LOG_FILE"
"${cmd[@]}" 2>&1 | tee "$LOG_FILE"
exit "${PIPESTATUS[0]}"
