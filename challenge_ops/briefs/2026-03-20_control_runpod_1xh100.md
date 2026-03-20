# Experiment Brief

Use this template before a meaningful experiment, packaging attempt, or submission-prep task.

## Identity

- `experiment_id`: `control_runpod_1xh100_20260320`
- `idea_label`: `Control 1xH100`
- `standardized_name`: `local_control_baseline_rerun`
- `owner`: `Codex`
- `date`: `2026-03-20`

## Standardized Classification

- `lineage`: `variant`
- `state`: `already-tried`
- `intent`: `non-record`
- `scope`: `1xH100-surrogate`

## Objective

- What is being tested: run one same-workflow remote `1xH100` control rerun on Runpod H100 SXM using the standard `control` wrapper path, unchanged `sp1024` dataset, and unchanged tokenizer.
- Why now: the latest remote `lr_warmdown` rerun regressed on the same nominal scope, so the cheapest discriminating next step is to measure whether the remote workflow itself drifts away from the local control anchor.

## Anchor And Novelty Check

- Closest prior idea or run: `experiments/ledger.csv` row `ablate_control_1xh100_1024`
- Anchor metric and scope: local baseline `baseline_sp1024_h100_local_20260319 = 1.32321114` and local control `ablate_control_1xh100_1024 = 1.32157507`, both on `1xH100-surrogate`
- Why this is `novel`, `variant`, or `baseline`: `variant`; this is a remote reproducibility rerun of an already-tried control path.
- Check against `challenge_ops/TRIED_IDEAS_INDEX.md`: existing `Control 1xH100` row confirmed; do not call this `novel`.

## Exact Plan

- Code path: `train_gpt.py` through `scripts/experiments/run_1xh100_ablation.sh`
- Dataset/tokenizer variant: `fineweb10B_sp1024` with `fineweb_1024_bpe.model`
- Hardware target: `1xH100` Runpod H100 SXM
- Wallclock target: `600s`
- Exact planned command: `RUN_ID=ablate_control_1xh100_20260320_runpod TARGET_GPU_LABEL=h100_sxm bash scripts/experiments/run_1xh100_ablation.sh control`

## Success And Failure Criteria

- Success threshold: final parsed metrics present and remote `val_bpb` lands close to the local control anchor, making the recent `lr_warmdown` regression look idea-specific rather than infrastructure-driven.
- Failure threshold: grounded infra failure, or a materially worse remote control rerun that suggests workflow variance dominates the recent difference.
- What would count as inconclusive: final metrics are missing, dataset/tokenizer path changed, or the remote workflow differs from the prior H100 SXM path in a way that breaks apples-to-apples comparison.

## Reproducibility And Legality

- Eval restrictions reminder: no eval-time downloads, network calls, or training-data access may be required by any resulting artifact claim.
- Artifact size concern: keep recording counted bytes even though this run is not submission packaging work.
- Tokenizer/dataset correctness concern: tokenizer and dataset behavior must remain unchanged; confirm the existing full `sp1024` path before training.
- Runpod or cost concern: reuse the same stopped H100 SXM pod if it is still healthy, track challenge usage, and stop the pod immediately after artifacts are secured.

## Planned Outputs

- Expected log path: `logs/experiments/next_1xh100_workstream/control/*_ablate_control_1xh100_20260320_runpod/run.log`
- Expected result markdown path: `challenge_ops/results/2026-03-20_ablate_control_1xh100_20260320_runpod.result.md`
- Expected result JSON path: `challenge_ops/results/2026-03-20_ablate_control_1xh100_20260320_runpod.result.json`
- Ledger update plan: let the wrapper refresh the remote ledger, then mirror the new row into local `experiments/ledger.csv`

## Notes

- Extra context: if the remote control rerun also drifts materially worse than the local control anchor, stop recommending more paid ablations and write an infra-variance diagnosis instead.
