# Baseline Reproduction Workflow

This note prepares a safe baseline reproduction workflow around the repo's current published baseline path without changing challenge-critical training logic.

## Goal

The first goal is to reproduce functionality and measurement behavior, not to beat SOTA immediately.

As visible in [README.md](/C:/Users/g3n_i/Desktop/0.%20Coding/Projects/parameter-golf/README.md), the currently visible public baseline in this repo snapshot is:

- `Naive Baseline`: `val_bpb = 1.2244`

The same leaderboard snapshot shows the current visible best public score at `1.206`, so the initial comparison target here is baseline reproduction, not leaderboard improvement.

## Paths

### 1. Smallest Safe Smoke Path

Use [smoke_local_or_remote.sh](/C:/Users/g3n_i/Desktop/0.%20Coding/Projects/parameter-golf/scripts/experiments/smoke_local_or_remote.sh) first.

What it does:

- Downloads published `sp1024` data with `--train-shards 1` if the tokenizer or dataset is missing.
- Verifies the expected dataset layout and tokenizer vocab.
- Refuses to fake a train result when `torchrun`, CUDA, or Python deps are missing.
- Runs only a tiny 1-GPU smoke train when the environment is actually ready.
- Writes a wrapper log plus parsed summary files under `logs/experiments/smoke/`.

Recommended intent:

- Use this on the provided cheap 1xA5000 pod first.
- Use it again on a 1xH100 before the full baseline run.
- Treat its result as an environment validation signal, not a score comparison.

### 2. Standard 1xH100 Baseline Path

Use [run_baseline_1gpu.sh](/C:/Users/g3n_i/Desktop/0.%20Coding/Projects/parameter-golf/scripts/experiments/run_baseline_1gpu.sh) after the smoke path is clean and the full published dataset is present.

What it preserves:

- The repo's standard command shape: env vars plus `torchrun --standalone --nproc_per_node=1 train_gpt.py`.
- The default `train_gpt.py` wallclock cap unless you explicitly set `MAX_WALLCLOCK_SECONDS`.
- Optional `VAL_LOSS_EVERY=200` support for baseline-style periodic validation.
- Consistent logs under `logs/experiments/baseline_1gpu/`.

It also checks that you have the full baseline-style dataset prefix by default:

- `EXPECTED_TRAIN_SHARDS=80`
- `ALLOW_PARTIAL_DATA=0`

If you intentionally want a cheaper non-comparable exploratory run on a 1xA5000, you can override that with `ALLOW_PARTIAL_DATA=1`, but do not compare those runs directly to the published public baseline.

## Runpod Setup Notes

Follow the repo README and existing Runpod helpers first:

1. Run the local Windows readiness check:

   ```powershell
   powershell -ExecutionPolicy Bypass -File scripts/windows/check_local_tools.ps1
   ```

2. On a Runpod pod, bootstrap and verify the repo:

   ```bash
   bash scripts/runpod/bootstrap_pod.sh
   bash scripts/runpod/verify_pod_env.sh
   ```

3. For Runpod CLI checks, use `runpodctl` once installed/authenticated:

   ```bash
   runpodctl doctor
   runpodctl gpu list
   runpodctl template get y5cejece4j
   ```

4. If you want to use Runpod Flash tooling locally, keep it to setup validation only for this workflow:

   ```bash
   flash --help
   flash env list
   ```

This workflow does not auto-launch pods and does not start any multi-GPU run.

## Logging

Both experiment scripts produce:

- a wrapper log that includes setup checks and trainer output
- `summary.txt`
- `summary.json`

The parser lives at [parse_train_log.py](/C:/Users/g3n_i/Desktop/0.%20Coding/Projects/parameter-golf/scripts/experiments/parse_train_log.py) and extracts:

- final `val_loss`
- final `val_bpb`
- raw model bytes if present
- compressed int8+zlib model bytes if present
- code bytes if present
- total submission size fields if present
- wallclock and stop behavior if present

## Exact Commands

### Local Windows Setup Check

```powershell
powershell -ExecutionPolicy Bypass -File scripts/windows/check_local_tools.ps1
```

### Cheap 1xA5000 Smoke Validation

```bash
bash scripts/experiments/smoke_local_or_remote.sh
```

Optional explicit label:

```bash
TARGET_GPU_LABEL=a5000 RUN_ID=smoke_sp1024_a5000 bash scripts/experiments/smoke_local_or_remote.sh
```

### Download Full Published Baseline Data

```bash
python3 data/cached_challenge_fineweb.py --variant sp1024 --train-shards 80
```

### Standard 1xH100 Baseline Reproduction

```bash
TARGET_GPU_LABEL=h100 \
RUN_ID=baseline_sp1024_h100 \
VAL_LOSS_EVERY=200 \
bash scripts/experiments/run_baseline_1gpu.sh
```

### Smaller 1xA5000 Exploratory Baseline-Style Run

Use only after the smoke path is already clean:

```bash
TARGET_GPU_LABEL=a5000 \
RUN_ID=baseline_sp1024_a5000 \
ALLOW_PARTIAL_DATA=1 \
VAL_LOSS_EVERY=200 \
bash scripts/experiments/run_baseline_1gpu.sh
```

If you want apples-to-apples comparison against the visible public baseline, do not use partial data and do not change the default wallclock behavior unless the change is part of the experiment you are explicitly documenting.
