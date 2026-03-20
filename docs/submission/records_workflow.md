# Records Workflow

This workflow prepares a local candidate submission folder under `/records` without pushing, opening a PR, or fabricating final metadata.

## Goal

Use this flow when a run looks promising and you want a clean local packaging step before deciding whether it belongs in:

- `records/track_10min_16mb/`
- `records/track_non_record_16mb/`

The workflow is intentionally conservative:

- it creates a timestamped candidate folder
- it snapshots the exact training script used
- it copies logs and optional metadata into predictable locations
- it does not invent scores, authorship, or leaderboard metadata
- it leaves the final submit/no-submit decision to you

## Folder Layout

The candidate folder layout is:

```text
records/<track>/<YYYY-MM-DD>_<slug>/
  README.md
  submission.json
  train.log
  train_gpt.py
  logs/
  metadata/
    candidate_manifest.json
```

Notes:

- `README.md`, `submission.json`, `train.log`, and `train_gpt.py` stay at the folder root because that matches the challenge submission shape.
- Extra logs go under `logs/`.
- Snapshot metadata goes under `metadata/`.
- Optional dependencies can be copied into subpaths inside the candidate folder when the training script needs them to run from inside the record folder.

## Create A Candidate Folder

Run from the repo root:

```bash
python scripts/submission/create_candidate_folder.py \
  --track track_non_record_16mb \
  --slug my_candidate \
  --script train_gpt.py \
  --log /absolute/path/to/train.log \
  --metadata-file /absolute/path/to/summary.json
```

Useful flags:

- `--track`: `track_10min_16mb`, `track_non_record_16mb`, `record`, or `non-record`
- `--slug`: human-readable candidate name suffix
- `--script`: exact training script snapshot to package
- `--target-script-name`: defaults to `train_gpt.py`
- `--dependency`: copy an extra dependency into the candidate folder
- `--extra-log`: copy extra logs into `logs/`
- `--metadata-file`: copy summaries or manifests into `metadata/`

What the script does:

1. Creates `records/<track>/<YYYY-MM-DD>_<slug>/`
2. Copies the chosen training script into the candidate folder
3. Copies the primary train log to `train.log` when provided
4. Creates placeholder `README.md` and `submission.json` from templates
5. Writes `metadata/candidate_manifest.json`
6. Warns if git status suggests the work is still centered on core files instead of packaging under `/records`

## Candidate Manifest

`metadata/candidate_manifest.json` records:

- creation time
- target track
- source script path
- copied dependency paths
- copied log paths
- copied metadata paths
- git HEAD if available
- git warnings detected at packaging time

This is local packaging metadata only. It is not a challenge submission file.

## Preflight The Candidate

Run from the repo root:

```bash
python scripts/submission/preflight_submission.py records/track_non_record_16mb/<YYYY-MM-DD>_<slug>
```

The preflight checks:

- required files exist
- `submission.json` parses
- manifest-declared dependency paths resolve
- artifact-size status from `submission.json` or `train.log`
- line-limit status for `train_gpt.py` and `train_gpt_mlx.py` if present
- obvious missing metadata fields
- self-contained packaging heuristics
- warnings about modified core files outside `/records`

Preflight exits non-zero on failure.

## Suggested Safe Order

1. Run and verify the experiment first.
2. Copy the exact script and final log into a candidate folder under `/records`.
3. Fill in the placeholder metadata manually.
4. Run preflight.
5. Only then decide whether the candidate is ready for a real submission branch or PR.

## What Not To Do

- Do not push directly from the packaging step.
- Do not open a PR before preflight passes.
- Do not leave a candidate dependent on repo-root files outside the candidate folder.
- Do not fabricate `submission.json` scores, bytes, dates, or authorship.
- Do not treat a candidate folder as submission-ready until the final checklist passes.
