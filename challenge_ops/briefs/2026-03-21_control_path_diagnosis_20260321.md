# Experiment Brief

## Identity

- `experiment_id`: `control_path_diagnosis_20260321`
- `run_id`: `control_path_diagnosis_20260321_runpod`
- `idea_label`: `Control 1xH100`
- `standardized_name`: `runpod_1xh100_control_anchor`
- `owner`: `Codex`
- `date`: `2026-03-21`

## Standardized Classification

- `lineage`: `variant`
- `state`: `already-tried`
- `intent`: `non-record`
- `scope`: `1xH100-surrogate`

## Objective

- What is being tested: Reconfirm the control-family 1xH100 path on unchanged sp1024 dataset/tokenizer and capture whether the stable-profile regression persists under the standard baseline command.
- Why now: The frontier shows the control path is still the bottleneck, and the repo memory says no surrogate ablation should resume until a control family with the new provenance surface repeatedly recovers near the provisional legacy anchor.

## Anchor And Novelty Check

- Closest prior idea or run: `ablate_control_1xh100_20260321_runpod_frozen_anchor_b`
- Anchor metric and scope: best rebuilt-control rerun: val_bpb=1.32776835 on 1xH100 Runpod NVIDIA H100 80GB HBM3; provisional legacy control anchor: val_bpb=1.32157507
- Why this is `novel`, `variant`, or `baseline`: This is not novel; it is a controlled repeat of the already-tried 1xH100 control family to diagnose reproducibility, not to chase a new architecture.
- Check against `challenge_ops/TRIED_IDEAS_INDEX.md`: existing row found for `runpod_1xh100_control_anchor`; treat this as already represented in repo memory.

## Exact Plan

- Code path: `train_gpt.py`
- Dataset/tokenizer variant: `fineweb10B_sp1024` with `fineweb_1024_bpe.model`
- Hardware target: `Runpod 1xH100 pod`
- Wallclock target: `600s`
- Exact planned command: `VAL_LOSS_EVERY=200 bash scripts/experiments/run_baseline_1gpu.sh`

## Success And Failure Criteria

- Success threshold: Observed val_bpb returns to within 0.005 nats of the provisional legacy control anchor and the run records clean provenance plus final metrics.
- Failure threshold: val_bpb remains materially above 1.32157507 or the run again stops early / fails to produce final metrics.
- What would count as inconclusive: infra failure, missing final metrics, or a confounded setup change

## Reproducibility And Legality

- Eval restrictions reminder: No eval-time downloads, network calls, or training-data access may be required by any resulting artifact claim.
- Artifact size concern: Keep the resulting artifact within the 16,000,000-byte cap and do not change dataset/tokenizer. This is a control-path diagnosis, not a submission attempt. Current cap: 16000000 bytes.
- Tokenizer/dataset correctness concern: Keep the documented dataset and tokenizer unchanged; no val_bpb proof plan is needed for this run.
- Runpod or cost concern: Do not start or resume Runpod until a remote approval token exists; if approved later, use only one 1xH100 pod and the tracked usage wrapper.

## Planned Outputs

- Expected log path: `logs/experiments/**/*_control_path_diagnosis_20260321_runpod/run.log`
- Expected result markdown path: `C:\Users\g3n_i\Desktop\0. Coding\Projects\parameter-golf\challenge_ops\results\2026-03-21_control_path_diagnosis_20260321_runpod.result.md`
- Expected result JSON path: `C:\Users\g3n_i\Desktop\0. Coding\Projects\parameter-golf\challenge_ops\results\2026-03-21_control_path_diagnosis_20260321_runpod.result.json`
- Ledger update plan: use `scripts/autonomy/controller.py record-result ...` after the run to generate the result packet and sync `experiments/ledger.csv`.

## Notes

- Extra context: No remote action is authorized yet. This dry-run brief is only for supervisor inspection before any approved paid run.
