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
- `records/`: accepted-style submission folders and prior run examples.
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

### Baseline Reproduction

- Reproduce the documented baseline path before claiming improvements.
- Record the exact command, dataset variant, tokenizer path, GPU shape, and wallclock behavior.
- Preserve apples-to-apples evaluation assumptions when comparing runs.

### Experiment Tracking

- Every meaningful experiment must capture at least: run ID, date, code path, dataset/tokenizer variant, hardware, wallclock target, `val_bpb`, and artifact size.
- Compare against the current baseline or current SOTA explicitly; do not report floating numbers without context.
- Keep experiment summaries concise and reproducible.

### Submission Safety Checks

- Verify artifact byte budget, required files, and evaluation restrictions before proposing a submission.
- Confirm the submission adds only a new folder under the appropriate `/records` track.
- Refuse packaging that depends on eval-time downloads, network access, or training-data access.

## Execution Guardrails

- Do not auto-launch paid 8xH100 runs or long sweeps without explicit user approval.
- Do not auto-package or finalize submissions without an explicit pre-submission check.
- Do not edit existing accepted record folders unless the user explicitly asks for that maintenance work.
- Do not touch core training logic for this guardrail setup task.
- Do not treat tokenizer or dataset changes as routine. They require an explicit proof plan for `val_bpb` correctness.
- Do not run blind brute-force searches over seeds or large unprincipled sweeps.

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
