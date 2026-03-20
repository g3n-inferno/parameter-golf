# Experiment Brief

Use this template before a meaningful experiment, packaging attempt, or submission-prep task.

## Identity

- `experiment_id`: `control_runpod_1xh100_20260320_stabilization`
- `idea_label`: `Control 1xH100`
- `standardized_name`: `runpod_1xh100_control_anchor`
- `owner`: `Codex`
- `date`: `2026-03-20`

## Standardized Classification

- `lineage`: `variant`
- `state`: `already-tried`
- `intent`: `non-record`
- `scope`: `1xH100-surrogate`

## Objective

- What is being tested: one tightly controlled remote rerun of the adopted `Runpod 1xH100 control anchor` on a fresh Runpod `1xH100` pod with the same wrapper path, same `sp1024` dataset/tokenizer path, and a pinned repo commit.
- Why now: the latest clean Runpod control retry regressed materially, so the highest-value next move is to determine whether the Runpod single-GPU control path is stable enough to resume ablations.

## Anchor And Novelty Check

- Closest prior idea or run: `experiments/ledger.csv` row `ablate_control_1xh100_1024`
- Anchor metric and scope: adopted `Runpod 1xH100 control anchor` is `ablate_control_1xh100_1024` at `val_bpb=1.32157507` on `1xH100-surrogate`; compatibility alias `baseline_sp1024_h100_local_20260319` stores `val_bpb=1.32321114`; latest clean Runpod retry `ablate_control_1xh100_20260320_runpod_retry2` regressed to `1.33518228`
- Why this is `novel`, `variant`, or `baseline`: `variant`; this is a control-path stabilization rerun of an already-tried Runpod control family.
- Check against `challenge_ops/TRIED_IDEAS_INDEX.md`: existing `Control 1xH100` row confirmed; do not call this `novel`.

## Exact Plan

- Code path: `train_gpt.py` through `scripts/experiments/run_1xh100_ablation.sh`
- Frozen commit: `bc75d7b0c350a41af25131232854833340265e86`
- Dataset/tokenizer variant: `fineweb10B_sp1024` with `fineweb_1024_bpe.model`
- Hardware target: one fresh `Runpod 1xH100 pod` only (`NVIDIA H100 80GB HBM3`, no network volume)
- Wallclock target: `600s`
- Exact planned command: `RUN_ID=ablate_control_1xh100_20260320_runpod_stabilize TARGET_GPU_LABEL=h100_sxm bash scripts/experiments/run_1xh100_ablation.sh control`

## Success And Failure Criteria

- Success threshold: final parsed metrics present and the remote rerun lands close enough to the adopted `Runpod 1xH100 control anchor` that the control path no longer looks dominated by workflow variance.
- Failure threshold: grounded infra failure at preflight or runtime, or a materially worse remote control rerun on the same declared path.
- What would count as inconclusive: missing final metrics, any mismatch in commit/dataset/tokenizer/wrapper identity, or a pod-side anomaly that breaks apples-to-apples comparison.

## Reproducibility And Legality

- Eval restrictions reminder: no eval-time downloads, network calls, or training-data access may be required by any resulting artifact claim.
- Artifact size concern: record counted bytes even though this run is not a submission package.
- Tokenizer/dataset correctness concern: tokenizer and dataset behavior must remain unchanged and be verified before training.
- Runpod or cost concern: use one pod and one operator thread only; if a concrete infra failure occurs, classify it and stop rather than broadening into another run.

## Planned Outputs

- Expected log path: `logs/experiments/next_1xh100_workstream/control/*_ablate_control_1xh100_20260320_runpod_stabilize/run.log`
- Expected result markdown path: `challenge_ops/results/2026-03-20_ablate_control_1xh100_20260320_runpod_stabilize.result.md`
- Expected result JSON path: `challenge_ops/results/2026-03-20_ablate_control_1xh100_20260320_runpod_stabilize.result.json`
- Ledger update plan: let the wrapper refresh the remote ledger, then mirror the new row into local `experiments/ledger.csv` if final metrics are produced

## Notes

- Extra context: use `Runpod 1xH100 control anchor` in human-facing notes. Keep the `_local_` filename and run ID only as compatibility aliases.
