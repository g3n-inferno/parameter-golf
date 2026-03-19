# Rsync Examples

These examples are for Git Bash or WSL on Windows, where `rsync` is typically available.
PowerShell does not ship with `rsync` natively.

Assumptions:
- SSH host alias: `parameter-golf-runpod`
- Remote repo path: `/workspace/parameter-golf`

## Sync Local Working Tree To The Pod

Use this when you have local changes that are not pushed yet:

```bash
rsync -avz \
  --exclude '.git/' \
  --exclude 'data/datasets/' \
  --exclude 'logs/' \
  --exclude 'artifacts/' \
  ./ parameter-golf-runpod:/workspace/parameter-golf/
```

## Pull Wrapper Logs Back To Windows

```bash
rsync -avz \
  parameter-golf-runpod:/workspace/parameter-golf/logs/runpod/ \
  ./logs/runpod/
```

## Pull Temporary Artifacts Back To Windows

```bash
rsync -avz \
  parameter-golf-runpod:/workspace/parameter-golf/artifacts/runpod/ \
  ./artifacts/runpod/
```

## Sync A Specific Records Folder Back Locally

```bash
rsync -avz \
  parameter-golf-runpod:/workspace/parameter-golf/records/track_10min_16mb/<run-folder>/ \
  ./records/track_10min_16mb/<run-folder>/
```

Prefer Git for durable source control changes.
Use `rsync` mainly for uncommitted working-tree sync or pulling logs and artifacts back from the Pod.
