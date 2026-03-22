# Experiment Brief

## Identity

- `experiment_id`: `shared_depth_ttc_rsd_lite_runpod_20260321`
- `run_id`: `ablate_shared_depth_ttc_rsd_lite_1xh100`
- `idea_label`: `Shared-Depth TTC-RSD-lite`
- `standardized_name`: `shared_depth_recurrent_self_distillation_lite`
- `owner`: `Codex`
- `date`: `2026-03-21`

## Standardized Classification

- `lineage`: `variant`
- `state`: `frontier`
- `intent`: `non-record`
- `scope`: `1xH100-surrogate`

## Objective

- What is being tested: whether a training-only 11-pass detached teacher improves an exported 9-pass shared-depth student under the standard 600-second `1xH100-surrogate` path.
- Why now: the repo already has an isolated shared-depth implementation, so recurrent self-distillation can be tested with minimal reversible changes and no artifact-format changes.

## Anchor And Novelty Check

- Closest prior idea or run: local shared-depth smoke validation plus the existing `shared_depth` / `shared_depth_stable` ablation wrapper entries.
- Anchor metric and scope: compare against a fresh provenance-backed `1xH100-surrogate` control summary rather than the provisional legacy mirrored anchor that is still marked `requires_rebuild_before_ablation=true`.
- Why this is `novel`, `variant`, or `baseline`: this is a `variant` of the shared-depth family because it keeps the same student export path and only adds train-time recurrent teacher logits.
- Check against `challenge_ops/TRIED_IDEAS_INDEX.md`: no row currently represents recurrent self-distillation or a train-time detached teacher on the shared-depth path.

## Exact Plan

- Code path: `train_gpt.py`
- Dataset/tokenizer variant: `fineweb10B_sp1024` with `fineweb_1024_bpe.model`
- Hardware target: `Runpod 1xH100 pod`
- Wallclock target: `600s`
- Exact planned command: `RUN_ID=ablate_shared_depth_ttc_rsd_lite_1xh100 TARGET_GPU_LABEL=h100_sxm_shared_depth_ttc DATA_PATH=/workspace/parameter-golf/data/datasets/fineweb10B_sp1024 TOKENIZER_PATH=/workspace/parameter-golf/data/tokenizers/fineweb_1024_bpe.model VOCAB_SIZE=1024 VAL_LOSS_EVERY=200 BASELINE_COMPARE_JSON=/workspace/parameter-golf/challenge_ops/results/2026-03-21_control_path_diagnosis_20260321_fresh_template_runpod.result.json bash scripts/experiments/run_1xh100_ablation.sh shared_depth_ttc_rsd_lite`

## Success And Failure Criteria

- Success threshold: the TTC path compiles and runs, logs the distillation fields cleanly, preserves student-only export behavior, and avoids a clear regression in `stop_step` or `val_bpb` relative to the chosen fresh control summary.
- Failure threshold: the TTC path fails to compile or run, breaks parseable logs, changes export behavior, or regresses step count / `val_bpb` enough to make the extra train-time compute clearly unhelpful.
- What would count as inconclusive: infra failure, pod instability, missing final metrics, or an invalid comparison caused by a mismatched or unavailable control summary.

## Reproducibility And Legality

- Eval restrictions reminder: no eval-time downloads, network calls, or training-data access may be required by any resulting artifact claim.
- Artifact size concern: teacher weights are not serialized separately; expected artifact impact is code-only and should stay well under the `16,000,000`-byte cap.
- Tokenizer/dataset correctness concern: keep the documented dataset and tokenizer unchanged; no `val_bpb` proof plan is needed for this run.
- Runpod or cost concern: reuse one existing preferred H100 pod if it restarts cleanly; otherwise create a single fresh official-template H100 pod, track the full session, and stop after one bounded TTC ablation.

## Planned Outputs

- Expected log path: `logs/experiments/next_1xh100_workstream/shared_depth_ttc_rsd_lite/*_ablate_shared_depth_ttc_rsd_lite_1xh100/run.log`
- Expected result markdown path: `challenge_ops/results/2026-03-21_ablate_shared_depth_ttc_rsd_lite_1xh100.result.md`
- Expected result JSON path: `challenge_ops/results/2026-03-21_ablate_shared_depth_ttc_rsd_lite_1xh100.result.json`
- Ledger update plan: generate the result packet and sync `experiments/ledger.csv` immediately after the remote run.

## Notes

- Extra context: the exported student path remains `SHARED_DEPTH_TOTAL_PASSES=9`; the teacher path is detached and train-time only at `11` total passes every `4` steps with a linear warmup to `lambda=0.05`.
