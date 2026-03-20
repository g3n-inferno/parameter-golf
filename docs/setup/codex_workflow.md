# Codex Workflow

Use this guide with `AGENTS.md` when working in the Parameter Golf repo.

## When To Use Each Agent

- `repo_mapper`: start here for unfamiliar tasks, repo orientation, or baseline discovery.
- `runpod_operator`: use for Runpod account setup, pod bootstrap, SSH, and remote command scaffolding.
- `training_operator`: use for baseline reproduction, training commands, reproducibility, and experiment execution plans.
- `experiment_historian`: use after meaningful runs to record the comparison, metrics, and context.
- `eval_submission_guard`: use before any packaging, PR prep, or leaderboard submission claim.

## Recommended Sequence

`repo_mapper -> runpod_operator -> training_operator -> experiment_historian -> eval_submission_guard`

Typical flow:
1. Map the repo and confirm the relevant constraints in `README.md`.
2. Set up or validate the remote environment, usually on 1xH100 first.
3. Reproduce the baseline before claiming improvements.
4. Record each meaningful run with command, hardware, wallclock target, `val_bpb`, and artifact size in `experiments/ledger.csv`.
5. Package draft candidates under `/records` with `scripts/submission/create_candidate_folder.py`.
6. Run `scripts/compliance/check_artifact_size.py`, `scripts/compliance/check_records_submission.py`, and `scripts/compliance/check_line_limits.py` as needed.
7. Run `scripts/submission/preflight_submission.py` before proposing anything under `records/`.

Reference docs:

- `docs/experiments/baseline_repro.md`
- `experiments/README.md`
- `docs/submission/records_workflow.md`
- `docs/submission/preflight_checklist.md`

## Baseline Reproduction Entry Point

Use the README's documented baseline path first:
- clone the repo,
- fetch the cached FineWeb variant,
- run `train_gpt.py` or `train_gpt_mlx.py` with the documented baseline settings,
- compare future runs against that reproduced baseline rather than memory.

## What Codex Must Not Do Automatically

- Launch 8xH100 track runs or long paid sweeps without explicit approval.
- Allow eval-time downloads, network calls, or training-data access.
- Treat tokenizer or dataset changes as routine without a proof plan for `val_bpb` correctness.
- Perform blind seed fishing or brute-force large-scale search.
- Package or place submissions outside a new folder under `records/`.
- Treat packaging templates as final metadata or invent missing submission fields.
- Push, commit, or open a PR from the packaging step alone.
- Modify accepted record folders unless explicitly asked.
- Treat `train_gpt.py` or `train_gpt_mlx.py` as the default home for competitive submissions.
