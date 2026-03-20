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

## Proven 1xH100 Runpod Workflow

This is the exact workflow that successfully produced a full 10-minute `1xH100` baseline run on the official Parameter Golf image.

### 1. Create the Right Pod

Use the official Parameter Golf template:

- template id: `y5cejece4j`
- preferred GPU for baseline reproduction: `NVIDIA H100 80GB HBM3` / H100 SXM
- keep `gpuCount=1`
- keep the default image and environment, including `JUPYTER_PASSWORD=parameter-golf`

Practical notes:

- If one H100 SKU is out of capacity, try another H100 SKU, but prefer SXM for closer alignment with the published baseline environment.
- If you create multiple fallback pods while probing capacity, stop the extras immediately once one working H100 is live.

### 2. Prefer SSH, Fall Back to Jupyter

The working control-path order is:

1. `runpodctl pod get <pod-id> --include-machine`
2. `runpodctl ssh info <pod-id>`
3. Direct SSH if the port is actually reachable
4. Jupyter on `https://<pod-id>-8888.proxy.runpod.net` if SSH is not ready but the pod is otherwise alive

Useful checks:

```powershell
$runpodctl = "$env:TEMP\runpodctl-install\runpodctl.exe"
& $runpodctl pod get <pod-id> --include-machine
& $runpodctl ssh info <pod-id>
Test-NetConnection <ip> -Port <port>
ssh -o StrictHostKeyChecking=accept-new -i C:\Users\g3n_i\.runpod\ssh\RunPod-Key-Go root@<ip> -p <port> "echo SSH_OK && nvidia-smi --query-gpu=name --format=csv,noheader"
```

Operational lesson:

- Do not assume the existence of SSH metadata means the pod is actually reachable.
- If SSH is down but Jupyter works, use Jupyter rather than waiting indefinitely on port 22.

### 3. Fix the Repo Checkout First

On the working pods so far, the template created `/workspace/parameter-golf`, but it was only a stub directory and not a real git checkout.

Always verify this before running anything:

```bash
if [ -d /workspace/parameter-golf/.git ]; then
  echo REPO_OK
else
  echo REPO_MISSING
fi
```

If it is missing, replace it with a real clone:

```bash
cd /workspace
rm -rf /workspace/parameter-golf
git clone https://github.com/g3n-inferno/parameter-golf.git /workspace/parameter-golf
cd /workspace/parameter-golf
git remote add upstream https://github.com/openai/parameter-golf.git || true
git fetch origin --prune
git checkout main
git pull --ff-only origin main
```

### 4. Verify the Pod Before Data Download

Run:

```bash
cd /workspace/parameter-golf
bash scripts/runpod/verify_pod_env.sh
```

This confirms:

- repo path is real
- `python3`, `torchrun`, and `nvidia-smi` exist
- at least one GPU is visible

### 5. Check Disk Before Pulling the Full Dataset

The official pod template used here had a `20G` container disk. The full published `sp1024` baseline dataset consumed about `16G`, so disk headroom matters.

Check first:

```bash
df -h /workspace
du -sh /workspace 2>/dev/null || true
```

Then pull the full published baseline dataset:

```bash
cd /workspace/parameter-golf
python3 data/cached_challenge_fineweb.py --variant sp1024 --train-shards 80
```

Afterward, verify the expected layout:

```bash
find data/datasets/fineweb10B_sp1024 -maxdepth 1 -name 'fineweb_train_*.bin' | wc -l
find data/datasets/fineweb10B_sp1024 -maxdepth 1 -name 'fineweb_val_*.bin' | wc -l
du -sh data/datasets/fineweb10B_sp1024
```

Expected result:

- `80` train shards
- `1` val shard

### 6. Run the Standard 10-Minute 1xH100 Baseline

Use the wrapper, not an ad hoc hand-edited command:

```bash
cd /workspace/parameter-golf
TARGET_GPU_LABEL=h100-sxm \
RUN_ID=baseline_sp1024_h100 \
VAL_LOSS_EVERY=200 \
bash scripts/experiments/run_baseline_1gpu.sh
```

This keeps:

- the repo's standard `torchrun --standalone --nproc_per_node=1 train_gpt.py` structure
- the default `MAX_WALLCLOCK_SECONDS`
- the published `sp1024` tokenizer and dataset assumptions

### 7. What a Healthy Run Looks Like

Expected early signals:

- warmup steps print first
- first periodic train logs arrive quickly
- step time is roughly in the few-hundred-millisecond range on `1xH100`
- `VAL_LOSS_EVERY=200` produces validation checkpoints during the run
- the run stops because of `wallclock_cap`, not a crash

The successful reference run in this repo used:

- hardware: `1x NVIDIA H100 80GB HBM3`
- dataset: `fineweb10B_sp1024`
- tokenizer: `fineweb_1024_bpe.model`
- stop reason: `wallclock_cap`
- stop train time: about `600.5s`
- stop step: `1444`
- final exact metric: `val_bpb=1.32321114`
- total compressed submission size: `14,037,860` bytes

This is a valid functional baseline reproduction on `1xH100`, but it is not directly comparable to the public `8xH100` naive baseline score of `1.2244`.

### 8. Clean Shutdown

Stop the H100 pod as soon as the summary files are written:

```powershell
$runpodctl = "$env:TEMP\runpodctl-install\runpodctl.exe"
& $runpodctl pod stop <pod-id>
& $runpodctl pod get <pod-id> --include-machine
```

Wait until `desiredStatus` is `EXITED`.

## Known Failure Modes

- SSH metadata exists, but the SSH port is still closed.
- Jupyter is live, but `/workspace/parameter-golf` is only a stub directory.
- The full `sp1024` dataset fills most of a `20G` disk, so extra junk on the pod can cause disk pressure.
- Unauthenticated Hugging Face downloads still work for this path, but they warn and may be slower.
- `1xH100` results are for reproducibility and iteration. Do not report them as apples-to-apples equivalents of the published `8xH100` public baseline.

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
