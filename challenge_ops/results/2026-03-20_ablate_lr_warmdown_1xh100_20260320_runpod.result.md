# Experiment Result

## Run Identity

- `run_id`: ablate_lr_warmdown_1xh100_20260320_runpod
- `experiment_id`: lr_warmdown_runpod_1xh100_20260320
- `date`: 2026-03-20
- `branch`: main
- `commit_sha`: c157a6ff2c32395465e39ba6a387364bcf8c2c99
- `log_path`: C:\Users\g3n_i\Desktop\0. Coding\Projects\parameter-golf\logs\experiments\next_1xh100_workstream\lr_warmdown\20260320_165622_ablate_lr_warmdown_1xh100_20260320_runpod\run.log
- `code_path`: train_gpt.py

## Standardized Classification

- `idea_label`: LR Warmdown
- `standardized_name`: longer_warmdown_schedule
- `lineage`: variant
- `state`: already-tried
- `result`: negative
- `track_intent`: non-record
- `scope`: 1xH100-surrogate

## Run Context

- `dataset_variant`: fineweb10B_sp1024
- `tokenizer_variant`: fineweb_1024_bpe.model
- `hardware`: 1xH100 Runpod NVIDIA H100 80GB HBM3
- `wallclock_target`: 600s
- `core_hparams`: seq1024 9x512 kv4 mlp_mult2 warmdown3600 matrix_lr0.06
- `exact_command`: RUN_ID=ablate_lr_warmdown_1xh100_20260320_runpod TARGET_GPU_LABEL=h100_sxm bash scripts/experiments/run_1xh100_ablation.sh lr_warmdown

## Confirmed Metrics

- `final_val_loss`: 2.24664078
- `final_val_bpb`: 1.33058722
- `final_metric_source`: final_int8_zlib_roundtrip_exact
- `final_eval_time_ms`: 11088
- `stop_reason`: wallclock_cap
- `stop_step`: 1343
- `stop_train_time_ms`: 600167
- `peak_memory_allocated_mib`: 10239
- `peak_memory_reserved_mib`: 10748
- `model_int8_zlib_bytes`: 11991857
- `code_bytes`: 61795
- `total_submission_size_int8_zlib_bytes`: 12053652

## Comparison

- `comparison.label`: runpod_1xh100_control_anchor
- `comparison.delta_val_loss`: 0.01245420
- `comparison.delta_val_bpb`: 0.00737608
- `comparison.delta_bytes_total`: -1984208
- `comparison.delta_stop_step`: -101
- `comparison.delta_eval_time_ms`: -70

## Confirmed Findings

- Runpod pod 9p5aq98sa8j6go was a usable 1x NVIDIA H100 80GB HBM3 pod and the remote checkout matched local main at c157a6ff2c32395465e39ba6a387364bcf8c2c99.
- The remote sp1024 dataset path contained 80 training shards, 1 validation shard, and the expected fineweb_1024_bpe.model tokenizer before training.
- The run finished with final_int8_zlib_roundtrip_exact val_loss=2.24664078, val_bpb=1.33058722, total_submission_size_int8_zlib_bytes=12053652, stop_step=1343, and final_eval_time_ms=11088.
- Relative to the legacy compatibility file `experiments/baselines/local_1xh100_baseline_summary.json`, which stores the Runpod `1xH100` control anchor, delta_val_bpb was +0.00737608 and delta_val_loss was +0.01245420.

## Inferred Conclusions

- This remote rerun does not reproduce the earlier Runpod-control-relative `lr_warmdown` signal on the `1xH100-surrogate` path.
- The lr_warmdown idea family should be treated as mixed or inconclusive at 1xH100-surrogate scope until another clean rerun explains the gap.

## Notes

- Remote rerun on Runpod pod 9p5aq98sa8j6go over SSH after verifying the official parameter-golf image, full sp1024 dataset export, and main@c157a6ff2c32395465e39ba6a387364bcf8c2c99.

## Artifact Cap Check

- `artifact_cap_bytes`: 16000000
- `artifact_cap_ok`: True
- `counted_total_bytes`: 12053652
- `counted_total_bytes_source`: total_submission_size_int8_zlib_bytes
