#!/usr/bin/env bash
# Intent: run the next leaderboard-informed 1xH100 ablations with consistent logging and ledger updates.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="${REPO_DIR:-$(cd "$SCRIPT_DIR/../.." && pwd)}"
EXPERIMENT_ID="${EXPERIMENT_ID:-${1:-}}"
LOG_ROOT_BASE="${LOG_ROOT_BASE:-$REPO_DIR/logs/experiments/next_1xh100_workstream}"
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
SHARD_SCORE_ROOT="${SHARD_SCORE_ROOT:-$REPO_DIR/artifacts/shard_scores}"

usage() {
  cat <<'EOF'
Usage:
  bash scripts/experiments/run_1xh100_ablation.sh <experiment_id>

Supported experiment_id values:
  control
  fp16_embed
  lr_warmdown
  compound_ctx1536
  byte_aware_loss
  easy_to_hard
  quality_top_half
  shared_depth
  shared_depth_stable
  shared_depth_ttc_rsd_lite
  shared_depth_experts_fixed
  shared_depth_experts_router

This wrapper preserves the documented 1xH100 baseline path and only layers named
env-var ablations on top. It also refreshes experiments/ledger.csv from the
parsed summary JSON and compares each run against the Runpod 1xH100 control
anchor. The canonical comparison file is
experiments/baselines/runpod_1xh100_control_anchor_summary.json, while the
legacy compatibility file experiments/baselines/local_1xh100_baseline_summary.json
remains supported as the older historical Runpod baseline summary.
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
EXPERIMENT_HARDWARE="${EXPERIMENT_HARDWARE:-Runpod 1xH100 pod}"
DATA_PATH_VALUE="${DATA_PATH:-$REPO_DIR/data/datasets/fineweb10B_sp1024}"
TOKENIZER_PATH_VALUE="${TOKENIZER_PATH:-$REPO_DIR/data/tokenizers/fineweb_1024_bpe.model}"
VOCAB_SIZE_VALUE="${VOCAB_SIZE:-1024}"
SHARD_SCORE_PATH_VALUE="${SHARD_SCORE_PATH:-$SHARD_SCORE_ROOT/${DATASET_VARIANT}_train_shard_scores.json}"
need_shard_scores=0

common_env=(
  "TARGET_GPU_LABEL=$TARGET_GPU_LABEL"
  "DATA_PATH=$DATA_PATH_VALUE"
  "TOKENIZER_PATH=$TOKENIZER_PATH_VALUE"
  "VOCAB_SIZE=$VOCAB_SIZE_VALUE"
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
    NOTES="control run near the current Runpod 1xH100 control-anchor path"
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
  byte_aware_loss)
    RUN_ID="${RUN_ID:-ablate_byte_aware_loss_1xh100}"
    CORE_HPARAMS="seq1024 9x512 kv4 mlp_mult2 byte_ce"
    NOTES="byte-aware loss ablation: optimize nats-per-byte during training while preserving validation val_bpb computation"
    experiment_env=(
      "TRAIN_LOSS_MODE=byte_ce"
    )
    ;;
  easy_to_hard)
    RUN_ID="${RUN_ID:-ablate_easy_to_hard_1xh100}"
    CORE_HPARAMS="seq1024 9x512 kv4 shard_order=easy_to_hard unigram_surprisal"
    NOTES="easy-to-hard shard curriculum: deterministic shard ordering by ascending unigram surprisal on the provided FineWeb export"
    need_shard_scores=1
    experiment_env=(
      "TRAIN_SHARD_ORDER=easy_to_hard"
      "SHARD_SCORE_PATH=$SHARD_SCORE_PATH_VALUE"
    )
    ;;
  quality_top_half)
    RUN_ID="${RUN_ID:-ablate_quality_top_half_1xh100}"
    CORE_HPARAMS="seq1024 9x512 kv4 quality_top_half shard_filter"
    NOTES="high-quality subset ablation: keep the top half of train shards by deterministic byte-fragmentation and repetition heuristics"
    need_shard_scores=1
    experiment_env=(
      "TRAIN_SHARD_FILTER=quality_top_fraction"
      "TRAIN_SHARD_FILTER_FRACTION=0.5"
      "SHARD_SCORE_PATH=$SHARD_SCORE_PATH_VALUE"
    )
    ;;
  shared_depth)
    RUN_ID="${RUN_ID:-ablate_shared_depth_1xh100}"
    CORE_HPARAMS="seq1024 shared_depth cyclic unique3 passes9"
    NOTES="shared-depth ablation: 3 unique blocks reused across 9 total passes with the current skip pattern"
    experiment_env=(
      "SHARED_DEPTH_MODE=cyclic"
      "SHARED_DEPTH_UNIQUE_BLOCKS=3"
      "SHARED_DEPTH_TOTAL_PASSES=9"
    )
    ;;
  shared_depth_stable)
    RUN_ID="${RUN_ID:-ablate_shared_depth_stable_1xh100}"
    CORE_HPARAMS="seq1024 shared_depth cyclic unique3 passes9 resid_scale=inv_sqrt_reuse"
    NOTES="shared-depth ablation with conservative residual scaling based on inverse sqrt reuse factor"
    experiment_env=(
      "SHARED_DEPTH_MODE=cyclic"
      "SHARED_DEPTH_UNIQUE_BLOCKS=3"
      "SHARED_DEPTH_TOTAL_PASSES=9"
      "SHARED_DEPTH_RESIDUAL_SCALE_MODE=inv_sqrt_reuse"
    )
    ;;
  shared_depth_ttc_rsd_lite)
    RUN_ID="${RUN_ID:-ablate_shared_depth_ttc_rsd_lite_1xh100}"
    CORE_HPARAMS="seq1024 shared_depth cyclic unique3 passes9 resid_scale=inv_sqrt_reuse ttc_rsd teacher11 every4 lambda0.05 warmup100"
    NOTES="training-only recurrent self-distillation on the shared-depth student path with an 11-pass detached teacher every 4 steps"
    experiment_env=(
      "SHARED_DEPTH_MODE=cyclic"
      "SHARED_DEPTH_UNIQUE_BLOCKS=3"
      "SHARED_DEPTH_TOTAL_PASSES=9"
      "SHARED_DEPTH_RESIDUAL_SCALE_MODE=inv_sqrt_reuse"
      "TTC_DISTILL_MODE=recurrent_logits"
      "TTC_STUDENT_TOTAL_PASSES=9"
      "TTC_TEACHER_TOTAL_PASSES=11"
      "TTC_DISTILL_EVERY=4"
      "TTC_DISTILL_LAMBDA=0.05"
      "TTC_DISTILL_WARMUP_STEPS=100"
    )
    ;;
  shared_depth_experts_fixed)
    RUN_ID="${RUN_ID:-ablate_shared_depth_experts_fixed_1xh100}"
    CORE_HPARAMS="seq1024 shared_depth cyclic unique3 passes9 resid_scale=inv_sqrt_reuse experts=2 upper3 mlp_hidden64 fixed_mix"
    NOTES="shared-depth plus two small sequence-level residual experts on the later passes with learned fixed mixture scalars"
    experiment_env=(
      "SHARED_DEPTH_MODE=cyclic" "SHARED_DEPTH_UNIQUE_BLOCKS=3" "SHARED_DEPTH_TOTAL_PASSES=9" "SHARED_DEPTH_RESIDUAL_SCALE_MODE=inv_sqrt_reuse"
      "SHARED_DEPTH_EXPERT_MODE=fixed" "SHARED_DEPTH_EXPERT_HIDDEN=64" "SHARED_DEPTH_EXPERT_UPPER_PASSES=3"
    )
    ;;
  shared_depth_experts_router)
    RUN_ID="${RUN_ID:-ablate_shared_depth_experts_router_1xh100}"
    CORE_HPARAMS="seq1024 shared_depth cyclic unique3 passes9 resid_scale=inv_sqrt_reuse experts=2 upper3 mlp_hidden64 seq_router"
    NOTES="shared-depth plus two small sequence-level residual experts on the later passes with a pooled-state router"
    experiment_env=(
      "SHARED_DEPTH_MODE=cyclic" "SHARED_DEPTH_UNIQUE_BLOCKS=3" "SHARED_DEPTH_TOTAL_PASSES=9" "SHARED_DEPTH_RESIDUAL_SCALE_MODE=inv_sqrt_reuse"
      "SHARED_DEPTH_EXPERT_MODE=router" "SHARED_DEPTH_EXPERT_HIDDEN=64" "SHARED_DEPTH_EXPERT_UPPER_PASSES=3"
    )
    ;;
  *)
    echo "unknown experiment_id: $EXPERIMENT_ID" >&2
    usage
    exit 1
    ;;
esac

LOG_ROOT="$LOG_ROOT_BASE/$EXPERIMENT_ID"

if [[ -f "$BASELINE_COMPARE_JSON" ]]; then
  if ! "$PYTHON_BIN" - "$BASELINE_COMPARE_JSON" "$EXPERIMENT_ID" <<'PY'
import json
import sys
from pathlib import Path

compare_path = Path(sys.argv[1])
experiment_id = sys.argv[2]
obj = json.loads(compare_path.read_text(encoding="utf-8"))
anchor_status = obj.get("anchor_status") or ""
requires_rebuild = bool(obj.get("requires_rebuild_before_ablation"))
if experiment_id != "control" and requires_rebuild:
    print(
        f"refusing {experiment_id}: compare target {compare_path} is marked "
        f"{anchor_status or 'provisional'} and requires a rebuilt frozen control anchor before surrogate ablations",
        file=sys.stderr,
    )
    raise SystemExit(2)
print(f"compare_json_anchor_status={anchor_status or 'unmarked'}")
PY
  then
    exit 1
  fi
fi

if [[ "$need_shard_scores" -eq 1 && ! -f "$SHARD_SCORE_PATH_VALUE" ]]; then
  mkdir -p "$SHARD_SCORE_ROOT"
  "$PYTHON_BIN" "$REPO_DIR/scripts/experiments/score_train_shards.py" \
    --data-path "$DATA_PATH_VALUE" \
    --tokenizer-path "$TOKENIZER_PATH_VALUE" \
    --vocab-size "$VOCAB_SIZE_VALUE" \
    --output "$SHARD_SCORE_PATH_VALUE"
fi

"$PYTHON_BIN" "$REPO_DIR/scripts/experiments/new_experiment.py" \
  --run-id "$RUN_ID" \
  --dataset-variant "$DATASET_VARIANT" \
  --tokenizer-variant "$TOKENIZER_VARIANT" \
  --core-hparams "$CORE_HPARAMS" \
  --hardware "$EXPERIMENT_HARDWARE" \
  --track-intent "$TRACK_INTENT" \
  --code-path "train_gpt.py" \
  --wallclock-target "$WALLCLOCK_TARGET" \
  --notes "$NOTES" \
  --force

env_args=("RUN_ID=$RUN_ID" "LOG_ROOT=$LOG_ROOT")
env_args+=("${common_env[@]}")
env_args+=("${experiment_env[@]}")
env_args+=(
  "EXPERIMENT_HARDWARE=$EXPERIMENT_HARDWARE"
  "DATASET_VARIANT=$DATASET_VARIANT"
  "TOKENIZER_VARIANT=$TOKENIZER_VARIANT"
  "CORE_HPARAMS=$CORE_HPARAMS"
  "TRACK_INTENT=$TRACK_INTENT"
  "WALLCLOCK_TARGET=$WALLCLOCK_TARGET"
  "WORKFLOW_WRAPPER_PATH=$REPO_DIR/scripts/experiments/run_1xh100_ablation.sh"
  "COMPARE_JSON_PATH=$BASELINE_COMPARE_JSON"
  "COMPARE_JSON_LABEL=$BASELINE_COMPARE_LABEL"
)

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
    "--compare-label" "$BASELINE_COMPARE_LABEL"
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
