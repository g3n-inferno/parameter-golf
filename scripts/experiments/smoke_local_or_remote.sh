#!/usr/bin/env bash
# Intent: cheapest safe validation path for the published sp1024 baseline layout.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="${REPO_DIR:-$(cd "$SCRIPT_DIR/../.." && pwd)}"
LOG_ROOT="${LOG_ROOT:-$REPO_DIR/logs/experiments/smoke}"
RUN_ID="${RUN_ID:-smoke_sp1024_1gpu}"
TARGET_GPU_LABEL="${TARGET_GPU_LABEL:-auto}"
VARIANT="${VARIANT:-sp1024}"
TRAIN_SHARDS="${TRAIN_SHARDS:-1}"
DATA_PATH="${DATA_PATH:-$REPO_DIR/data/datasets/fineweb10B_sp1024}"
TOKENIZER_PATH="${TOKENIZER_PATH:-$REPO_DIR/data/tokenizers/fineweb_1024_bpe.model}"
VOCAB_SIZE="${VOCAB_SIZE:-1024}"
ITERATIONS="${ITERATIONS:-2}"
TRAIN_BATCH_TOKENS="${TRAIN_BATCH_TOKENS:-131072}"
VAL_BATCH_SIZE="${VAL_BATCH_SIZE:-131072}"
TRAIN_LOG_EVERY="${TRAIN_LOG_EVERY:-1}"
VAL_LOSS_EVERY="${VAL_LOSS_EVERY:-0}"
MAX_WALLCLOCK_SECONDS="${MAX_WALLCLOCK_SECONDS:-180}"

usage() {
  cat <<'EOF'
Usage:
  bash scripts/experiments/smoke_local_or_remote.sh

This script:
  - downloads sp1024 with --train-shards 1 if the published data is missing
  - verifies dataset and tokenizer path assumptions
  - runs a tiny 1-GPU smoke train only if the environment is actually ready
  - writes a wrapper log plus summary files under logs/experiments/smoke/

Optional environment variables:
  REPO_DIR                Repo root. Default: inferred from this script
  LOG_ROOT                Log root. Default: <repo>/logs/experiments/smoke
  RUN_ID                  Log/run label. Default: smoke_sp1024_1gpu
  TARGET_GPU_LABEL        Free-form GPU label for log context. Default: auto
  VARIANT                 Data variant. Default: sp1024
  TRAIN_SHARDS            Training shards to fetch if missing. Default: 1
  DATA_PATH               Dataset path. Default: <repo>/data/datasets/fineweb10B_sp1024
  TOKENIZER_PATH          Tokenizer model path. Default: <repo>/data/tokenizers/fineweb_1024_bpe.model
  VOCAB_SIZE              Tokenizer vocab size. Default: 1024
  ITERATIONS              Smoke train iterations. Default: 2
  TRAIN_BATCH_TOKENS      Smoke train batch tokens. Default: 131072
  VAL_BATCH_SIZE          Validation batch size. Default: 131072
  TRAIN_LOG_EVERY         Train log cadence. Default: 1
  VAL_LOSS_EVERY          Periodic validation cadence. Default: 0
  MAX_WALLCLOCK_SECONDS   Hard cap for smoke run. Default: 180
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

write_status_summary() {
  local status="$1"
  local detail="$2"
  cat >"$SUMMARY_FILE" <<EOF
log: $RUN_ID
status: $status
detail: $detail
log_path: $LOG_FILE
EOF
  cat >"$JSON_FILE" <<EOF
{
  "log": "$RUN_ID",
  "status": "$status",
  "detail": "$detail",
  "log_path": "$LOG_FILE"
}
EOF
  cat "$SUMMARY_FILE"
}

LAST_CONTEXT="initializing smoke workflow"

on_exit() {
  local exit_code="$1"
  if [[ "$exit_code" -ne 0 && ! -s "$SUMMARY_FILE" ]]; then
    write_status_summary "failed" "$LAST_CONTEXT (exit_code=$exit_code)"
  fi
}

PYTHON_BIN="$(find_python || true)"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
RUN_DIR="$LOG_ROOT/${TIMESTAMP}_${RUN_ID}"
mkdir -p "$RUN_DIR"
LOG_FILE="$RUN_DIR/run.log"
SUMMARY_FILE="$RUN_DIR/summary.txt"
JSON_FILE="$RUN_DIR/summary.json"

exec > >(tee -a "$LOG_FILE") 2>&1
trap 'on_exit $?' EXIT

echo "[$(date -Iseconds)] smoke start"
echo "repo_dir=$REPO_DIR"
echo "run_dir=$RUN_DIR"
echo "target_gpu_label=$TARGET_GPU_LABEL"
echo "variant=$VARIANT train_shards=$TRAIN_SHARDS"
echo "data_path=$DATA_PATH"
echo "tokenizer_path=$TOKENIZER_PATH"

if [[ ! -d "$REPO_DIR" ]]; then
  write_status_summary "failed" "repo directory not found: $REPO_DIR"
  exit 1
fi

if [[ -z "$PYTHON_BIN" ]]; then
  write_status_summary "failed" "python3/python not found"
  exit 1
fi

need_download=0
if [[ ! -f "$TOKENIZER_PATH" ]]; then
  need_download=1
fi
if [[ ! -d "$DATA_PATH" ]]; then
  need_download=1
fi
if [[ -d "$DATA_PATH" ]]; then
  shopt -s nullglob
  train_bins=("$DATA_PATH"/fineweb_train_*.bin)
  val_bins=("$DATA_PATH"/fineweb_val_*.bin)
  shopt -u nullglob
  if [[ "${#train_bins[@]}" -lt 1 || "${#val_bins[@]}" -lt 1 ]]; then
    need_download=1
  fi
fi

if [[ "$need_download" -eq 1 ]]; then
  LAST_CONTEXT="downloading published $VARIANT data"
  echo "published data missing; downloading $VARIANT with --train-shards $TRAIN_SHARDS"
  (
    cd "$REPO_DIR"
    "$PYTHON_BIN" data/cached_challenge_fineweb.py --variant "$VARIANT" --train-shards "$TRAIN_SHARDS"
  )
fi

if [[ ! -d "$DATA_PATH" || ! -f "$TOKENIZER_PATH" ]]; then
  write_status_summary "failed" "dataset/tokenizer missing after download attempt"
  exit 1
fi

echo "verifying dataset and tokenizer layout"
LAST_CONTEXT="verifying dataset and tokenizer layout"
DATA_PATH="$DATA_PATH" TOKENIZER_PATH="$TOKENIZER_PATH" VOCAB_SIZE="$VOCAB_SIZE" "$PYTHON_BIN" - <<'PY'
from __future__ import annotations

import glob
import os
import sys
from pathlib import Path

data_path = Path(os.environ["DATA_PATH"])
tokenizer_path = Path(os.environ["TOKENIZER_PATH"])
expected_vocab = int(os.environ["VOCAB_SIZE"])

train_files = sorted(glob.glob(str(data_path / "fineweb_train_*.bin")))
val_files = sorted(glob.glob(str(data_path / "fineweb_val_*.bin")))

if not train_files:
    raise SystemExit(f"expected at least one fineweb_train_*.bin under {data_path}")
if not val_files:
    raise SystemExit(f"expected at least one fineweb_val_*.bin under {data_path}")
if not tokenizer_path.is_file():
    raise SystemExit(f"tokenizer not found: {tokenizer_path}")

print(f"verified train_shards_found={len(train_files)} val_shards_found={len(val_files)}")

try:
    import sentencepiece as spm
except Exception as exc:  # pragma: no cover - environment probe
    raise SystemExit(f"sentencepiece import failed: {exc}")

sp = spm.SentencePieceProcessor(model_file=str(tokenizer_path))
actual_vocab = int(sp.vocab_size())
if actual_vocab != expected_vocab:
    raise SystemExit(
        f"VOCAB_SIZE mismatch: expected {expected_vocab}, tokenizer has {actual_vocab}"
    )
print(f"verified tokenizer_vocab={actual_vocab}")
PY

if ! command -v torchrun >/dev/null 2>&1; then
  write_status_summary "blocked" "torchrun not found; smoke training not executed"
  exit 1
fi

if ! command -v nvidia-smi >/dev/null 2>&1; then
  write_status_summary "blocked" "nvidia-smi not found; smoke training not executed"
  exit 1
fi

gpu_count="$(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null | wc -l | tr -d ' ')"
if [[ -z "$gpu_count" || "$gpu_count" -lt 1 ]]; then
  write_status_summary "blocked" "no GPU detected by nvidia-smi"
  exit 1
fi
echo "verified gpu_count=$gpu_count"

LAST_CONTEXT="probing torch/cuda dependencies"
DATA_PATH="$DATA_PATH" TOKENIZER_PATH="$TOKENIZER_PATH" "$PYTHON_BIN" - <<'PY'
from __future__ import annotations

import os
import sys

try:
    import sentencepiece  # noqa: F401
    import torch
except Exception as exc:  # pragma: no cover - environment probe
    raise SystemExit(f"training dependency probe failed: {exc}")

if not torch.cuda.is_available():
    raise SystemExit("torch.cuda.is_available() is false")

print(f"verified torch_version={torch.__version__} cuda_available={torch.cuda.is_available()}")
PY

echo "starting smoke training command"
LAST_CONTEXT="running smoke training"
(
  cd "$REPO_DIR"
  env \
    RUN_ID="$RUN_ID" \
    DATA_PATH="$DATA_PATH" \
    TOKENIZER_PATH="$TOKENIZER_PATH" \
    VOCAB_SIZE="$VOCAB_SIZE" \
    ITERATIONS="$ITERATIONS" \
    TRAIN_BATCH_TOKENS="$TRAIN_BATCH_TOKENS" \
    VAL_BATCH_SIZE="$VAL_BATCH_SIZE" \
    TRAIN_LOG_EVERY="$TRAIN_LOG_EVERY" \
    VAL_LOSS_EVERY="$VAL_LOSS_EVERY" \
    MAX_WALLCLOCK_SECONDS="$MAX_WALLCLOCK_SECONDS" \
    torchrun --standalone --nproc_per_node=1 train_gpt.py
)

LAST_CONTEXT="parsing smoke log"
"$PYTHON_BIN" "$REPO_DIR/scripts/experiments/parse_train_log.py" \
  "$LOG_FILE" \
  --label "$RUN_ID" \
  --summary-out "$SUMMARY_FILE" \
  --json-out "$JSON_FILE"

echo "summary_path=$SUMMARY_FILE"
echo "json_path=$JSON_FILE"
