# Runpod Setup From Windows

This repo includes a conservative Runpod workflow for Windows, Windsurf, and Codex.
It prepares the repo side only. You still create or destroy Pods manually in the Runpod UI.

## Goals

- Verify local tools on Windows.
- Connect to a Pod over SSH.
- Keep the remote repo rooted at `/workspace/parameter-golf`.
- Sync from your fork while still fetching upstream.
- Reproduce the documented 1xH100 baseline safely.
- Keep a clear path to a later 8xH100 track run.

## Files Added For This Workflow

- `scripts/windows/check_local_tools.ps1`
- `scripts/runpod/bootstrap_pod.sh`
- `scripts/runpod/verify_pod_env.sh`
- `scripts/runpod/download_sp1024.sh`
- `scripts/runpod/run_baseline_1gpu.sh`
- `scripts/runpod/run_track_8gpu.sh`
- `scripts/runpod/rsync_examples.md`
- `docs/setup/runpod_checklist.md`

## Local Prerequisites

- A Runpod account.
- An SSH key already added to Runpod.
- Git for Windows.
- OpenSSH client on Windows.
- Optional: `runpodctl` for pod inspection or file-transfer workflows.
- Optional: Git Bash or WSL if you want to use `rsync`.

Run the local preflight check:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/windows/check_local_tools.ps1
```

## Recommended Remote Layout

Use this layout on the Pod:

```text
/workspace/parameter-golf
/workspace/parameter-golf/data
/workspace/parameter-golf/logs/runpod
/workspace/parameter-golf/artifacts/runpod
```

Notes:
- The repo itself stays in `/workspace/parameter-golf`.
- Helper scripts log to `logs/runpod/`.
- Temporary experiment artifacts can go under `artifacts/runpod/`.
- Formal challenge submissions still belong under `records/`.

## Pod Creation Policy

Create Pods manually in the Runpod UI.

- For iteration: start with the official Parameter Golf template on 1xH100.
- For track runs later: use the official template on 8xH100 SXM.
- The repo scripts do not create or destroy Pods automatically.

## SSH And Windsurf Workflow

After the Pod is up, get the SSH endpoint from Runpod and add a host alias in `~/.ssh/config`.
The username is usually `root`, but confirm it in the Runpod UI for your Pod.

Example:

```sshconfig
Host parameter-golf-runpod
    HostName <runpod-hostname>
    User <runpod-user>
    Port <runpod-port>
    IdentityFile C:/Users/<you>/.ssh/<your_runpod_key>
    ServerAliveInterval 30
    ServerAliveCountMax 10
```

Connect from PowerShell:

```powershell
ssh parameter-golf-runpod
```

Reconnect from Windsurf:
1. Open the remote SSH target using the same host alias.
2. Open the folder `/workspace/parameter-golf`.
3. Use the same terminal commands documented below so Codex and Windsurf stay on one layout.

## Bootstrap The Pod

On a brand new Pod, do a first clone manually because the helper scripts live inside the repo:

```bash
cd /workspace
git clone https://github.com/<you>/parameter-golf.git parameter-golf
cd /workspace/parameter-golf
```

After that, use the bootstrap wrapper:

```bash
FORK_URL=https://github.com/<you>/parameter-golf.git \
bash scripts/runpod/bootstrap_pod.sh
```

Common env vars for bootstrap:

```bash
FORK_URL=https://github.com/<you>/parameter-golf.git \
UPSTREAM_URL=https://github.com/openai/parameter-golf.git \
bash scripts/runpod/bootstrap_pod.sh
```

Behavior after the repo already exists locally on the Pod:
- Clones your fork into `/workspace/parameter-golf` if the repo is missing.
- Ensures `origin` points at your fork when `FORK_URL` is provided.
- Ensures `upstream` exists and defaults to the official OpenAI repo.
- Fetches both remotes without force-pushing, rebasing, or resetting.

## Verify The Pod Environment

Run:

```bash
cd /workspace/parameter-golf
bash scripts/runpod/verify_pod_env.sh
```

This checks:
- `git`, `python3`, `torchrun`, and `nvidia-smi`
- GPU visibility
- repo path correctness
- optional `runpodctl` availability
- optional `runpodctl` auth hints without assuming auth is already configured

## Download The `sp1024` Dataset

Run:

```bash
cd /workspace/parameter-golf
bash scripts/runpod/download_sp1024.sh
```

Optional smaller smoke download:

```bash
TRAIN_SHARDS=1 bash scripts/runpod/download_sp1024.sh
```

The script logs to `logs/runpod/download_sp1024*.log`.

## Start The 1xH100 Baseline

Run:

```bash
cd /workspace/parameter-golf
bash scripts/runpod/run_baseline_1gpu.sh
```

This wraps the documented baseline:
- `DATA_PATH=./data/datasets/fineweb10B_sp1024/`
- `TOKENIZER_PATH=./data/tokenizers/fineweb_1024_bpe.model`
- `VOCAB_SIZE=1024`
- `torchrun --standalone --nproc_per_node=1 train_gpt.py`

Logs are written to `logs/runpod/`.

## Start A Later 8xH100 Track Run

Run only after you intentionally land on an 8xH100 Pod:

```bash
cd /workspace/parameter-golf
CONFIRM_TRACK_8GPU=YES bash scripts/runpod/run_track_8gpu.sh
```

The confirmation env var is required on purpose.
The script refuses to run unless 8 GPUs are visible.

## Keeping Your Fork And Upstream In Sync

Preferred workflow:
1. Make durable changes locally and push them to your fork.
2. On the Pod, fetch `origin` and `upstream`.
3. Check out the branch you want to test.
4. Pull or fast-forward deliberately, not automatically.

Useful examples:

```bash
cd /workspace/parameter-golf
git fetch origin --prune
git fetch upstream --prune
git branch -vv
git status --short
```

For file sync examples, see [`scripts/runpod/rsync_examples.md`](/C:/Users/g3n_i/Desktop/0.%20Coding/Projects/parameter-golf/scripts/runpod/rsync_examples.md).

## `runpodctl` Notes

`runpodctl` is optional in this repo workflow.
Use it for discovery or file-transfer tasks if you prefer, but do not rely on it for auth being preconfigured.

Recommended checks:

```powershell
runpodctl --help
```

```bash
runpodctl --help
```

If you need auth, follow the current Runpod prompts on your machine rather than hardcoding secrets in repo scripts.

## Logs And Artifacts

- Wrapper logs: `logs/runpod/`
- Temporary experiment outputs: `artifacts/runpod/`
- Formal submission-ready outputs: a new folder under `records/`

Do not commit transient logs or temporary remote artifacts.
