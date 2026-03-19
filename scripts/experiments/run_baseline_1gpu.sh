#!/usr/bin/env bash
# Intent: run the documented 1-GPU baseline path with reproducible logging.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="${REPO_DIR:-$(cd "$SCRIPT_DIR/../.." && pwd)}"
LOG_ROOT="${LOG_ROOT:-$REPO_DIR/logs/experiments/baseline_1gpu}"
RUN_ID="${RUN_ID:-baseline_sp1024_1gpu}"
TARGET_GPU_LABEL="${TARGET_GPU_LABEL:-auto}"
DATA_PATH="${DATA_PATH:-$REPO_DIR/data/datasets/fineweb10B_sp1024}"
TOKENIZER_PATH="${TOKENIZER_PATH:-$REPO_DIR/data/tokenizers/fineweb_1024_bpe.model}"
VOCAB_SIZE="${VOCAB_SIZE:-1024}"
EXPECTED_TRAIN_SHARDS="${EXPECTED_TRAIN_SHARDS:-80}"
ALLOW_PARTIAL_DATA="${ALLOW_PARTIAL_DATA:-0}"
TRAIN_LOG_EVERY="${TRAIN_LOG_EVERY:-50}"
VAL_LOSS_EVERY="${VAL_LOSS_EVERY:-}"
MAX_WALLCLOCK_SECONDS="${MAX_WALLCLOCK_SECONDS:-}"

usage() {
  cat <<'EOF'
Usage:
  bash scripts/experiments/run_baseline_1gpu.sh

This script matches the repo's standard 1-GPU baseline-style command structure and
writes logs under logs/experiments/baseline_1gpu/.

Optional environment variables:
  REPO_DIR                Repo root. Default: inferred from this script
  LOG_ROOT                Log root. Default: <repo>/logs/experiments/baseline_1gpu
  RUN_ID                  Run label. Default: baseline_sp1024_1gpu
  TARGET_GPU_LABEL        Free-form GPU label for log context. Default: auto
  DATA_PATH               Dataset path. Default: <repo>/data/datasets/fineweb10B_sp1024
  TOKENIZER_PATH          Tokenizer path. Default: <repo>/data/tokenizers/fineweb_1024_bpe.model
  VOCAB_SIZE              Tokenizer vocab size. Default: 1024
  EXPECTED_TRAIN_SHARDS   Require this many train shards unless ALLOW_PARTIAL_DATA=1. Default: 80
  ALLOW_PARTIAL_DATA      Set to 1 for non-comparable exploratory runs. Default: 0
  TRAIN_LOG_EVERY         Passed through to train_gpt.py. Default: 50
  VAL_LOSS_EVERY          Optional override, for example 200
  MAX_WALLCLOCK_SECONDS   Optional override. If unset, train_gpt.py keeps its default cap.
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

TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
RUN_DIR="$LOG_ROOT/${TIMESTAMP}_${RUN_ID}"
mkdir -p "$RUN_DIR"
LOG_FILE="$RUN_DIR/run.log"
SUMMARY_FILE="$RUN_DIR/summary.txt"
JSON_FILE="$RUN_DIR/summary.json"

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

LAST_CONTEXT="initializing baseline workflow"

on_exit() {
  local exit_code="$1"
  if [[ "$exit_code" -ne 0 && ! -s "$SUMMARY_FILE" ]]; then
    write_status_summary "failed" "$LAST_CONTEXT (exit_code=$exit_code)"
  fi
}

exec > >(tee -a "$LOG_FILE") 2>&1
trap 'on_exit $?' EXIT

echo "[$(date -Iseconds)] baseline start"
echo "repo_dir=$REPO_DIR"
echo "run_dir=$RUN_DIR"
echo "target_gpu_label=$TARGET_GPU_LABEL"
echo "data_path=$DATA_PATH"
echo "tokenizer_path=$TOKENIZER_PATH"

if [[ ! -d "$REPO_DIR/.git" ]]; then
  echo "expected git repo at $REPO_DIR" >&2
  exit 1
fi

if ! command -v torchrun >/dev/null 2>&1; then
  echo "torchrun not found" >&2
  exit 1
fi

if ! command -v nvidia-smi >/dev/null 2>&1; then
  echo "nvidia-smi not found" >&2
  exit 1
fi

gpu_count="$(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null | wc -l | tr -d ' ')"
if [[ -z "$gpu_count" || "$gpu_count" -lt 1 ]]; then
  echo "no GPU detected by nvidia-smi" >&2
  exit 1
fi
echo "verified gpu_count=$gpu_count"

LAST_CONTEXT="verifying dataset, tokenizer, and torch environment"
DATA_PATH="$DATA_PATH" TOKENIZER_PATH="$TOKENIZER_PATH" VOCAB_SIZE="$VOCAB_SIZE" EXPECTED_TRAIN_SHARDS="$EXPECTED_TRAIN_SHARDS" ALLOW_PARTIAL_DATA="$ALLOW_PARTIAL_DATA" "$PYTHON_BIN" - <<'PY'
from __future__ import annotations

import glob
import os
from pathlib import Path

data_path = Path(os.environ["DATA_PATH"])
tokenizer_path = Path(os.environ["TOKENIZER_PATH"])
expected_vocab = int(os.environ["VOCAB_SIZE"])
expected_train_shards = int(os.environ["EXPECTED_TRAIN_SHARDS"])
allow_partial = int(os.environ["ALLOW_PARTIAL_DATA"]) == 1

train_files = sorted(glob.glob(str(data_path / "fineweb_train_*.bin")))
val_files = sorted(glob.glob(str(data_path / "fineweb_val_*.bin")))
if not train_files:
    raise SystemExit(f"no training shards found under {data_path}")
if not val_files:
    raise SystemExit(f"no validation shards found under {data_path}")
if not tokenizer_path.is_file():
    raise SystemExit(f"tokenizer not found: {tokenizer_path}")
if len(train_files) < expected_train_shards and not allow_partial:
    raise SystemExit(
        f"found {len(train_files)} train shards under {data_path}, expected at least {expected_train_shards}; "
        "set ALLOW_PARTIAL_DATA=1 only for non-comparable exploratory runs"
    )

try:
    import sentencepiece as spm
    import torch
except Exception as exc:  # pragma: no cover - environment probe
    raise SystemExit(f"training dependency probe failed: {exc}")

sp = spm.SentencePieceProcessor(model_file=str(tokenizer_path))
actual_vocab = int(sp.vocab_size())
if actual_vocab != expected_vocab:
    raise SystemExit(f"VOCAB_SIZE mismatch: expected {expected_vocab}, tokenizer has {actual_vocab}")
if not torch.cuda.is_available():
    raise SystemExit("torch.cuda.is_available() is false")

print(
    f"verified train_shards_found={len(train_files)} "
    f"val_shards_found={len(val_files)} tokenizer_vocab={actual_vocab} "
    f"torch_version={torch.__version__}"
)
PY

env_args=(
  "RUN_ID=$RUN_ID"
  "DATA_PATH=$DATA_PATH"
  "TOKENIZER_PATH=$TOKENIZER_PATH"
  "VOCAB_SIZE=$VOCAB_SIZE"
  "TRAIN_LOG_EVERY=$TRAIN_LOG_EVERY"
)

if [[ -n "$VAL_LOSS_EVERY" ]]; then
  env_args+=("VAL_LOSS_EVERY=$VAL_LOSS_EVERY")
fi

if [[ -n "$MAX_WALLCLOCK_SECONDS" ]]; then
  env_args+=("MAX_WALLCLOCK_SECONDS=$MAX_WALLCLOCK_SECONDS")
fi

echo "starting baseline training command"
echo "env overrides: ${env_args[*]}"
LAST_CONTEXT="running baseline training"
(
  cd "$REPO_DIR"
  env "${env_args[@]}" torchrun --standalone --nproc_per_node=1 train_gpt.py
)

LAST_CONTEXT="parsing baseline log"
"$PYTHON_BIN" "$REPO_DIR/scripts/experiments/parse_train_log.py" \
  "$LOG_FILE" \
  --label "$RUN_ID" \
  --summary-out "$SUMMARY_FILE" \
  --json-out "$JSON_FILE" \
  --require-final-metrics

echo "summary_path=$SUMMARY_FILE"
echo "json_path=$JSON_FILE"
