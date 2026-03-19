# Runpod Checklist

## Local Checks

- Run `powershell -ExecutionPolicy Bypass -File scripts/windows/check_local_tools.ps1`.
- Confirm `git` and `ssh` are available locally.
- Confirm your Runpod SSH key exists on disk.
- Confirm you know your fork URL.
- Optional: confirm `runpodctl` is installed if you plan to use it.
- Optional: confirm Git Bash or WSL is available if you plan to use `rsync`.

## Remote Checks

- SSH reaches the Pod successfully.
- The repo path is `/workspace/parameter-golf`.
- `git`, `python3`, `torchrun`, and `nvidia-smi` are available.
- The expected GPU count matches the Pod shape.
- `bash scripts/runpod/verify_pod_env.sh` passes.

## First Commands After SSH Login

```bash
cd /workspace
git clone https://github.com/<you>/parameter-golf.git parameter-golf
cd /workspace/parameter-golf
FORK_URL=https://github.com/<you>/parameter-golf.git bash scripts/runpod/bootstrap_pod.sh
bash scripts/runpod/verify_pod_env.sh
bash scripts/runpod/download_sp1024.sh
bash scripts/runpod/run_baseline_1gpu.sh
```

## Common Failure Modes

- `runpodctl` is missing locally or remotely: treat it as optional and continue with SSH.
- SSH works in the terminal but not in Windsurf: fix your `~/.ssh/config` host alias and `IdentityFile`.
- `FORK_URL` was not set on first bootstrap: rerun the bootstrap script with your fork URL.
- The dataset or tokenizer path is missing: rerun `bash scripts/runpod/download_sp1024.sh`.
- Fewer GPUs are visible than expected: check the Pod shape in Runpod before launching training.
- The 8xH100 wrapper refuses to run: set `CONFIRM_TRACK_8GPU=YES` and verify all 8 GPUs are present.
- Logs are hard to find: check `logs/runpod/` under `/workspace/parameter-golf`.
