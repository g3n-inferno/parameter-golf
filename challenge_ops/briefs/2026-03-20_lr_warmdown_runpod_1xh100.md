# Experiment Brief

Use this template before a meaningful experiment, packaging attempt, or submission-prep task.

## Identity

- `experiment_id`: `lr_warmdown_runpod_1xh100_20260320`
- `idea_label`: `LR Warmdown`
- `standardized_name`: `longer_warmdown_schedule`
- `owner`: `Codex`
- `date`: `2026-03-20`

## Standardized Classification

- `lineage`: `variant`
- `state`: `already-tried`
- `intent`: `non-record`
- `scope`: `1xH100-surrogate`

## Objective

- What is being tested: run one real remote `1xH100` reproduction of the repo-supported `lr_warmdown` ablation using the standard wrapper, unchanged tokenizer, and unchanged `sp1024` dataset path.
- Why now: this is the strongest positive local schedule-style signal in current repo memory and it exercises the new `challenge_ops` coordination workflow end to end on a cheap apples-to-apples surrogate path.

## Anchor And Novelty Check

- Closest prior idea or run: `experiments/ledger.csv` row `ablate_lr_warmdown_1xh100_1024`
- Anchor metric and scope: `val_bpb=1.32157507` for `ablate_control_1xh100_1024` on `1xH100-surrogate`; prior positive reference `val_bpb=1.31909196` for `ablate_lr_warmdown_1xh100_1024`
- Why this is `novel`, `variant`, or `baseline`: `variant`; this is a remote reproducibility rerun of an already-tried schedule family, not a new mechanism.
- Check against `challenge_ops/TRIED_IDEAS_INDEX.md`: existing `LR Warmdown` row confirmed; do not call this run `novel`.

## Exact Plan

- Code path: `train_gpt.py` through `scripts/experiments/run_1xh100_ablation.sh`
- Dataset/tokenizer variant: `fineweb10B_sp1024` with `fineweb_1024_bpe.model`
- Hardware target: `1xH100`
- Wallclock target: `600s`
- Exact planned command: `RUN_ID=ablate_lr_warmdown_1xh100_20260320_runpod TARGET_GPU_LABEL=h100_sxm bash scripts/experiments/run_1xh100_ablation.sh lr_warmdown`

## Success And Failure Criteria

- Success threshold: final parsed metrics present and `val_bpb <= 1.32157507` so the remote rerun at least preserves the current local positive signal against the control anchor.
- Failure threshold: final parsed metrics present and `val_bpb > 1.32157507`, or the run violates the documented apples-to-apples dataset/tokenizer path.
- What would count as inconclusive: infra failure, incomplete dataset, missing final metrics, or a run that finishes with confounded setup differences from the standard wrapper path.

## Reproducibility And Legality

- Eval restrictions reminder: no eval-time downloads, network calls, or training-data access may be required by any resulting artifact claim.
- Artifact size concern: record counted bytes and keep them under the repo cap, even though this task does not package a submission.
- Tokenizer/dataset correctness concern: tokenizer and dataset behavior must remain unchanged; use the documented `sp1024` dataset export command with `--train-shards 80`.
- Runpod or cost concern: use the existing `1xH100` pod if it is usable; do not create anything larger than `1xH100`, and track challenge usage from pod start.

## Planned Outputs

- Expected log path: `logs/experiments/next_1xh100_workstream/lr_warmdown/*_ablate_lr_warmdown_1xh100_20260320_runpod/run.log`
- Expected result markdown path: `challenge_ops/results/2026-03-20_ablate_lr_warmdown_1xh100_20260320_runpod.result.md`
- Expected result JSON path: `challenge_ops/results/2026-03-20_ablate_lr_warmdown_1xh100_20260320_runpod.result.json`
- Ledger update plan: use `scripts/experiments/update_ledger.py` via the wrapper, then preserve the new row in `experiments/ledger.csv`

## Notes

- Extra context: if the current pod does not come up cleanly via SSH, use Jupyter as the control plane rather than waiting indefinitely.
