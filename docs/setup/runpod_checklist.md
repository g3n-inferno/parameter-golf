# Runpod Checklist

## Local Checks

- Run `powershell -ExecutionPolicy Bypass -File scripts/windows/check_local_tools.ps1`.
- Confirm `git` and `ssh` are available locally.
- Confirm your Runpod SSH key exists on disk.
- Confirm you know your fork URL.
- Optional: confirm `runpodctl` is installed if you plan to use it.
- Optional: confirm `flash` is installed if you plan to use the Flash workflow.
- Optional: confirm Git Bash or WSL has an installed distro if you plan to use `rsync`.

## Remote Checks

- SSH reaches the Pod successfully.
- If SSH is not ready but Jupyter is live, use Jupyter as the fallback control plane.
- The repo path is `/workspace/parameter-golf`.
- `/workspace/parameter-golf/.git` exists. If not, replace the template stub directory with a real clone of your fork.
- `git`, `python3`, `torchrun`, and `nvidia-smi` are available.
- The expected GPU count matches the Pod shape.
- `bash scripts/runpod/verify_pod_env.sh` passes.

## First Commands After SSH Login

```bash
cd /workspace
rm -rf /workspace/parameter-golf
git clone https://github.com/<you>/parameter-golf.git parameter-golf
cd /workspace/parameter-golf
FORK_URL=https://github.com/<you>/parameter-golf.git bash scripts/runpod/bootstrap_pod.sh
bash scripts/runpod/verify_pod_env.sh
python3 data/cached_challenge_fineweb.py --variant sp1024 --train-shards 80
TARGET_GPU_LABEL=h100 RUN_ID=baseline_sp1024_h100 VAL_LOSS_EVERY=200 bash scripts/experiments/run_baseline_1gpu.sh
```

## Common Failure Modes

- `runpodctl` is missing locally or remotely: treat it as optional and continue with SSH.
- SSH works in the terminal but not in Windsurf: fix your `~/.ssh/config` host alias and `IdentityFile`.
- The template already created `/workspace/parameter-golf`, but it is only a stub directory: remove it and do a real clone before running anything.
- `FORK_URL` was not set on first bootstrap: rerun the bootstrap script with your fork URL.
- The dataset or tokenizer path is missing: rerun `python3 data/cached_challenge_fineweb.py --variant sp1024 --train-shards 80`.
- Fewer GPUs are visible than expected: check the Pod shape in Runpod before launching training.
- The 8xH100 wrapper refuses to run: set `CONFIRM_TRACK_8GPU=YES` and verify all 8 GPUs are present.
- Logs are hard to find: check `logs/experiments/` under `/workspace/parameter-golf`.
