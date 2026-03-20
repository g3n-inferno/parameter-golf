# Experiment Brief

Use this template before a meaningful experiment, packaging attempt, or submission-prep task.

## Identity

- `experiment_id`: `control_runpod_1xh100_20260320_retry2`
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

- What is being tested: retry the same-workflow remote `1xH100` control rerun on a single fresh Runpod H100 SXM pod using the standard `control` wrapper path, unchanged `sp1024` dataset, unchanged tokenizer, and unchanged evaluation rules.
- Why now: the prior fallback pod exited during warmup before step metrics, so one clean single-pod retry is the cheapest remaining way to determine whether the earlier remote `lr_warmdown` miss was idea-specific or workflow variance.

## Anchor And Novelty Check

- Closest prior idea or run: `experiments/ledger.csv` row `ablate_control_1xh100_1024`
- Anchor metric and scope: `val_bpb=1.32157507` for `ablate_control_1xh100_1024` on `1xH100-surrogate`; secondary legacy alias `baseline_sp1024_h100_local_20260319` at `1.32321114`; remote failure case `ablate_lr_warmdown_1xh100_20260320_runpod` at `1.33058722`
- Why this is `novel`, `variant`, or `baseline`: `variant`; this is a retry of the same remote control family, not a new mechanism.
- Check against `challenge_ops/TRIED_IDEAS_INDEX.md`: existing `Control 1xH100` row confirmed; do not call this run `novel`.

## Exact Plan

- Code path: `train_gpt.py` through `scripts/experiments/run_1xh100_ablation.sh`
- Dataset/tokenizer variant: `fineweb10B_sp1024` with `fineweb_1024_bpe.model`
- Hardware target: one fresh `Runpod 1xH100 pod` only (H100 SXM path)
- Wallclock target: `600s`
- Exact planned command: `RUN_ID=ablate_control_1xh100_20260320_runpod_retry2 TARGET_GPU_LABEL=h100_sxm bash scripts/experiments/run_1xh100_ablation.sh control`

## Success And Failure Criteria

- Success threshold: final parsed metrics present and the remote control rerun lands close enough to `ablate_control_1xh100_1024` to support a workflow-stable interpretation.
- Failure threshold: the fresh single-pod retry again fails before producing final metrics, or lands materially worse than the Runpod `1xH100` control anchor.
- What would count as inconclusive: any infra failure before final metrics, or a confounded run that does not preserve the same wrapper, dataset, tokenizer, and single-pod workflow.

## Reproducibility And Legality

- Eval restrictions reminder: no eval-time downloads, network calls, or training-data access may be required by any resulting artifact claim.
- Artifact size concern: record counted bytes and keep them under the repo cap if the run completes.
- Tokenizer/dataset correctness concern: tokenizer and dataset behavior must remain unchanged and be verified before training.
- Runpod or cost concern: use one pod and one operator thread only; stop the pod immediately after log sync or failure classification.

## Planned Outputs

- Expected log path: `logs/experiments/next_1xh100_workstream/control/*_ablate_control_1xh100_20260320_runpod_retry2/run.log`
- Expected result markdown path: `challenge_ops/results/2026-03-20_ablate_control_1xh100_20260320_runpod_retry2.result.md`
- Expected result JSON path: `challenge_ops/results/2026-03-20_ablate_control_1xh100_20260320_runpod_retry2.result.json`
- Ledger update plan: only mirror the run into local `experiments/ledger.csv` if final metrics are produced

## Notes

- Extra context: if this fresh single-pod retry also fails before step metrics or final metrics, stop recommending more paid ablations and retain the infra-variance diagnosis.
