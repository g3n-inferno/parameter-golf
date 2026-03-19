#!/usr/bin/env bash
# Intent: prepare a conservative Parameter Golf repo layout on a Runpod machine.
# This script never creates or destroys Pods. It only manages the repo path safely.

set -euo pipefail

REPO_DIR="${REPO_DIR:-/workspace/parameter-golf}"
FORK_URL="${FORK_URL:-}"
UPSTREAM_URL="${UPSTREAM_URL:-https://github.com/openai/parameter-golf.git}"
LOG_DIR="${LOG_DIR:-$REPO_DIR/logs/runpod}"
ARTIFACT_DIR="${ARTIFACT_DIR:-$REPO_DIR/artifacts/runpod}"

usage() {
  cat <<'EOF'
Usage:
  FORK_URL=https://github.com/<you>/parameter-golf.git bash scripts/runpod/bootstrap_pod.sh

Optional environment variables:
  REPO_DIR        Remote repo path. Default: /workspace/parameter-golf
  FORK_URL        Your fork URL. Required on first clone if REPO_DIR does not exist.
  UPSTREAM_URL    Upstream repo URL. Default: https://github.com/openai/parameter-golf.git
  LOG_DIR         Log directory. Default: /workspace/parameter-golf/logs/runpod
  ARTIFACT_DIR    Artifact directory. Default: /workspace/parameter-golf/artifacts/runpod
EOF
}

if [[ "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

need_cmd() {
  local cmd="$1"
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "Missing required command: $cmd" >&2
    exit 1
  fi
}

need_cmd git
need_cmd python3

if [[ ! -d "$REPO_DIR/.git" ]]; then
  if [[ -z "$FORK_URL" ]]; then
    echo "REPO_DIR does not exist and FORK_URL was not provided." >&2
    echo "Set FORK_URL to your fork and rerun." >&2
    exit 1
  fi
  mkdir -p "$(dirname "$REPO_DIR")"
  echo "Cloning fork into $REPO_DIR"
  git clone "$FORK_URL" "$REPO_DIR"
fi

cd "$REPO_DIR"

if ! git remote get-url origin >/dev/null 2>&1; then
  if [[ -z "$FORK_URL" ]]; then
    echo "Repo exists but origin is missing and FORK_URL was not provided." >&2
    exit 1
  fi
  git remote add origin "$FORK_URL"
fi

if [[ -n "$FORK_URL" ]]; then
  current_origin="$(git remote get-url origin)"
  if [[ "$current_origin" != "$FORK_URL" ]]; then
    echo "Updating origin to $FORK_URL"
    git remote set-url origin "$FORK_URL"
  fi
fi

if git remote get-url upstream >/dev/null 2>&1; then
  current_upstream="$(git remote get-url upstream)"
  if [[ "$current_upstream" != "$UPSTREAM_URL" ]]; then
    echo "Updating upstream to $UPSTREAM_URL"
    git remote set-url upstream "$UPSTREAM_URL"
  fi
else
  git remote add upstream "$UPSTREAM_URL"
fi

mkdir -p "$LOG_DIR" "$ARTIFACT_DIR"

echo "Fetching origin and upstream safely"
git fetch origin --prune
git fetch upstream --prune

echo
echo "Bootstrap complete."
echo "Repo path: $REPO_DIR"
echo "Current branch: $(git branch --show-current || true)"
echo "Origin: $(git remote get-url origin)"
echo "Upstream: $(git remote get-url upstream)"
echo "Logs: $LOG_DIR"
echo "Artifacts: $ARTIFACT_DIR"
echo
echo "Next steps:"
echo "  1. bash scripts/runpod/verify_pod_env.sh"
echo "  2. bash scripts/runpod/download_sp1024.sh"
echo "  3. bash scripts/runpod/run_baseline_1gpu.sh"
