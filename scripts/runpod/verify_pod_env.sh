#!/usr/bin/env bash
# Intent: verify that a Runpod machine is usable for Parameter Golf without mutating training code.

set -euo pipefail

REPO_DIR="${REPO_DIR:-/workspace/parameter-golf}"

usage() {
  cat <<'EOF'
Usage:
  bash scripts/runpod/verify_pod_env.sh

Optional environment variables:
  REPO_DIR    Remote repo path. Default: /workspace/parameter-golf
EOF
}

if [[ "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

status_ok() {
  printf '[ok] %s\n' "$1"
}

status_warn() {
  printf '[warn] %s\n' "$1"
}

status_fail() {
  printf '[fail] %s\n' "$1" >&2
  exit 1
}

check_required_cmd() {
  local cmd="$1"
  if command -v "$cmd" >/dev/null 2>&1; then
    status_ok "found command: $cmd"
  else
    status_fail "missing required command: $cmd"
  fi
}

check_optional_cmd() {
  local cmd="$1"
  if command -v "$cmd" >/dev/null 2>&1; then
    status_ok "found optional command: $cmd"
  else
    status_warn "optional command not found: $cmd"
  fi
}

check_required_cmd git
check_required_cmd python3
check_required_cmd torchrun
check_required_cmd nvidia-smi
check_optional_cmd runpodctl

if [[ ! -d "$REPO_DIR/.git" ]]; then
  status_fail "expected repo at $REPO_DIR"
fi

status_ok "repo present at $REPO_DIR"

gpu_count="$(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null | wc -l | tr -d ' ')"
if [[ -z "$gpu_count" || "$gpu_count" -lt 1 ]]; then
  status_fail "no GPUs detected by nvidia-smi"
fi
status_ok "GPU count detected: $gpu_count"

python3 --version
torchrun --version || true
nvidia-smi -L

if command -v runpodctl >/dev/null 2>&1; then
  auth_hint_found=0
  if [[ -n "${RUNPOD_API_KEY:-}" ]]; then
    auth_hint_found=1
    status_ok "RUNPOD_API_KEY is set"
  fi
  if [[ -f "$HOME/.runpod/config.toml" || -f "$HOME/.runpod/config.yaml" || -f "$HOME/.config/runpod/config.toml" ]]; then
    auth_hint_found=1
    status_ok "runpodctl config file detected"
  fi
  if [[ "$auth_hint_found" -eq 0 ]]; then
    status_warn "runpodctl is installed, but no auth hint was detected. Auth may still be required."
  fi
fi

echo "Environment verification complete."
