# Parameter Golf Codex Guardrails

This file is the authoritative operating contract for Codex work in this repository.
When repo-specific guidance conflicts with generic guidance, follow this file.

## Mission

Optimize for compliant, reproducible Parameter Golf progress without breaking challenge rules.

Priority order:
1. Challenge-rule compliance.
2. Reproducibility and measurement correctness.
3. Cheap iteration before expensive track runs.
4. Model quality and submission readiness.

## Repository Map

- `README.md`: challenge rules, baseline workflow, Runpod setup, and submission policy.
- `data/`: dataset and tokenizer helper scripts plus data-specific docs.
- `experiments/`: lightweight local experiment ledger and workflow notes.
- `docs/submission/`: local candidate packaging workflow and final preflight checklist.
- `records/`: accepted-style submission folders and prior run examples.
- `templates/`: conservative packaging templates for draft `README.md` and `submission.json`.
- `scripts/compliance/`: artifact-size, records-shape, and line-limit checks.
- `train_gpt.py`: CUDA baseline launcher and a starting point, not the preferred home for competitive records.
- `train_gpt_mlx.py`: MLX baseline launcher and a starting point for local iteration.

## Non-Negotiable Challenge Rules

1. The leaderboard artifact cap is 16,000,000 total bytes.
2. The main track training target is under 10 minutes on 8xH100.
3. Evaluation must also stay within the repo-stated 10-minute limit on 8xH100.
4. Scoring is tokenizer-agnostic `val_bpb` on the FineWeb validation split.
5. No external downloads, network calls, or training-data access are allowed during evaluation.
6. If the tokenizer or dataset changes, `val_bpb` correctness must be proved.
7. New SOTA submissions must beat the current SOTA by at least 0.005 nats and provide enough logs to justify `p < 0.01`, unless the change is a systems-only speed optimization.
8. Accepted challenge submissions should add only a new folder under `/records`.
9. `train_gpt.py` and `train_gpt_mlx.py` are launching-off points, but competitive runs should live in `/records`.
10. `train_gpt.py` and `train_gpt_mlx.py` must never exceed 1500 lines.
11. No blind large-scale search or brute-force seed fishing is allowed.
12. Prefer 1xH100 and cheaper SKUs for iteration before 8xH100 track runs.

## Required Workflow

Follow this order unless the task is tightly scoped and already localized:
1. Repo mapping.
2. Runpod setup.
3. Baseline reproduction.
4. Experiment tracking.
5. Submission safety checks.

### Repo Mapping

- Read the challenge rules in `README.md` before changing workflows or packaging anything.
- Inspect `records/` examples before proposing a new competitive run layout.
- Treat `train_gpt.py` and `train_gpt_mlx.py` as baselines to learn from, not the default destination for competitive logic.

### Runpod Setup

- Prefer cheap SKUs and 1xH100 for setup validation, smoke tests, and iteration.
- Use the repo's documented Runpod flow and template before inventing new bootstrap steps.
- Do not start expensive remote runs automatically. Ask first when the action incurs meaningful cost.
- For H100 baseline reproduction, prefer the official Parameter Golf template `y5cejece4j`.
- Prefer direct SSH when it is genuinely reachable. If the pod exposes Jupyter first and SSH is still closed, use Jupyter as the control plane instead of waiting indefinitely.
- Always verify whether `/workspace/parameter-golf` is a real git checkout. On the official template it may exist only as a stub directory and must be replaced with a real clone before any run.
- Stop extra fallback pods immediately once one working pod is confirmed.
- For any Runpod GPU compute used for this OpenAI challenge, initialize and maintain the local usage audit trail with `scripts/runpod/track_challenge_usage.py`.
- Default to `python scripts/runpod/track_challenge_usage.py run-command ... -- <command>` for tracked one-shot runs on already-reachable pods.
- If pod initialization time matters, use the explicit tracker lifecycle: `start-session` when pod start is requested, `mark-ready` when SSH/Jupyter is actually usable, then `start-run` / `finish-run` / `finish-session`.
- Always set `usage_scope=challenge` for challenge compute unless the user explicitly says otherwise.
- Default the Runpod challenge `funding_note` to `OpenAI Runpod credit allocation ($25, blended balance assumption)`.
- Treat the local challenge credit budget as a fixed `$25` for audit/reporting purposes, even if the live Runpod account balance is higher because credits are blended together.
- Treat the tracker as the required local audit layer for challenge-only compute. Runpod billing does not expose which credit source was consumed, so that attribution must be recorded locally.

### Baseline Reproduction

- Reproduce the documented baseline path before claiming improvements.
- Record the exact command, dataset variant, tokenizer path, GPU shape, and wallclock behavior.
- Preserve apples-to-apples evaluation assumptions when comparing runs.
- Before a true `1xH100` baseline run, verify the pod with `bash scripts/runpod/verify_pod_env.sh`.
- For the published `sp1024` baseline path, require the full dataset prefix: `python3 data/cached_challenge_fineweb.py --variant sp1024 --train-shards 80`.
- Check disk headroom before downloading the full dataset. The `sp1024` baseline dataset can consume about `16G`, which is significant on a `20G` pod disk.
- Use `scripts/experiments/run_baseline_1gpu.sh` for the standard `1xH100` path, with `VAL_LOSS_EVERY=200` when periodic validation is needed. Do not override the default wallclock cap unless the experiment explicitly calls for it.
- Treat `1xH100` runs as reproducibility and iteration checks. The visible public naive baseline score is an `8xH100` reference point, not an apples-to-apples `1xH100` target.

### Experiment Tracking

- Every meaningful experiment must capture at least: run ID, date, code path, dataset/tokenizer variant, hardware, wallclock target, `val_bpb`, and artifact size.
- Compare against the current baseline or current SOTA explicitly; do not report floating numbers without context.
- Keep experiment summaries concise and reproducible.
- Use `experiments/ledger.csv` as the lightweight local source of truth for meaningful runs.
- Use `scripts/experiments/new_experiment.py`, `scripts/experiments/update_ledger.py`, and `scripts/experiments/summarize_candidates.py` instead of ad hoc notes when possible.
- For any Runpod challenge run, also maintain `experiments/runpod_sessions.csv` and `experiments/runpod_runs.csv` via `scripts/runpod/track_challenge_usage.py` so pod config, init time, run time, billed time, and billed cost are auditable.

### Submission Safety Checks

- Verify artifact byte budget, required files, and evaluation restrictions before proposing a submission.
- Confirm the submission adds only a new folder under the appropriate `/records` track.
- Refuse packaging that depends on eval-time downloads, network access, or training-data access.
- Use `scripts/compliance/check_artifact_size.py`, `scripts/compliance/check_records_submission.py`, and `scripts/compliance/check_line_limits.py` for focused checks.
- Use `scripts/submission/create_candidate_folder.py` to package a local draft candidate under `/records`.
- Use `scripts/submission/preflight_submission.py` before any submission branch, PR prep, or submission recommendation.
- Treat `templates/submission_README_template.md` and `templates/submission_json_template.json` as placeholders only. Do not fabricate final metadata.

## Execution Guardrails

- Do not auto-launch paid 8xH100 runs or long sweeps without explicit user approval.
- Do not auto-package or finalize submissions without an explicit pre-submission check.
- Do not push, commit, or open a submission PR as part of the local packaging/preflight workflow unless the user explicitly asks.
- Do not edit existing accepted record folders unless the user explicitly asks for that maintenance work.
- Do not touch core training logic for this guardrail setup task.
- Do not treat tokenizer or dataset changes as routine. They require an explicit proof plan for `val_bpb` correctness.
- Do not run blind brute-force searches over seeds or large unprincipled sweeps.

## Known Good Remote Workflow

For future Codex-run remote experiments, the fastest safe path is:

1. Confirm the official template and chosen GPU SKU with `runpodctl`.
2. Create a cheap validation pod first when possible, then a `1xH100` pod for the real baseline path.
3. Start the local Runpod challenge tracker session as soon as pod start is requested when init-time accounting matters.
4. Verify actual access, in this order: `runpodctl pod get`, `runpodctl ssh info`, direct SSH reachability, then Jupyter fallback.
5. Mark the tracker session ready once SSH or Jupyter is genuinely usable.
6. Confirm `/workspace/parameter-golf/.git` exists. If not, reclone the repo and pull `origin/main`.
7. Run `bash scripts/runpod/verify_pod_env.sh`.
8. Download the exact dataset needed for the intended comparison.
9. Run the experiment through the tracker wrapper or the explicit tracker lifecycle, not as an untracked hand-edited trainer command.
10. Monitor file-backed logs until the wrapper exits and summary files are present.
11. Finish the tracker run/session, record costs, then stop the pod once the logs and summaries are secured.

When reporting results, always distinguish:

- smoke-path validation
- `1xH100` baseline-style reproduction
- `8xH100` leaderboard-comparable runs
- local `/records` packaging and preflight status

## Current Launcher Baseline

- `train_gpt.py` is currently 1001 lines.
- `train_gpt_mlx.py` is currently 978 lines.

## Delegation Policy

Use the narrow agent profiles in `.codex/agents/` when delegation is useful:
- `repo_mapper`: read-only repo understanding.
- `runpod_operator`: setup, Runpod bootstrap, SSH, and remote scripts.
- `training_operator`: training commands, reproducibility, and experiment execution plans.
- `eval_submission_guard`: artifact size, required files, and compliance checks.
- `experiment_historian`: experiment ledger structure and run summaries.

Keep scopes narrow and hand work off to the next role once the current role's job is done.
