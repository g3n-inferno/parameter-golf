# Experiment Result

## Run Identity

- `run_id`: ablate_shared_depth_ttc_rsd_lite_1xh100_retry1
- `experiment_id`: shared_depth_ttc_rsd_lite_runpod_20260321
- `date`: 2026-03-21
- `branch`: main
- `commit_sha`: 6235d57295cf2ef0e4a5289b0c2a621b8948b304
- `log_path`: C:\Users\g3n_i\Desktop\0. Coding\Projects\parameter-golf\logs\experiments\next_1xh100_workstream\shared_depth_ttc_rsd_lite\20260322_012046_ablate_shared_depth_ttc_rsd_lite_1xh100_retry1\run.log
- `code_path`: train_gpt.py

## Standardized Classification

- `idea_label`: Shared-Depth TTC-RSD-lite
- `standardized_name`: shared_depth_recurrent_self_distillation_lite
- `lineage`: variant
- `state`: frontier
- `result`: negative
- `track_intent`: non-record
- `scope`: 1xH100-surrogate

## Run Context

- `dataset_variant`: fineweb10B_sp1024
- `tokenizer_variant`: fineweb_1024_bpe.model
- `hardware`: Runpod 1xH100 pod
- `wallclock_target`: 600s
- `core_hparams`: seq1024 shared_depth cyclic unique3 passes9 resid_scale=inv_sqrt_reuse ttc_rsd teacher11 every4 lambda0.05 warmup100
- `exact_command`: RUN_ID=ablate_shared_depth_ttc_rsd_lite_1xh100_retry1 TARGET_GPU_LABEL=h100_sxm_shared_depth_ttc DATA_PATH=/workspace/parameter-golf/data/datasets/fineweb10B_sp1024 TOKENIZER_PATH=/workspace/parameter-golf/data/tokenizers/fineweb_1024_bpe.model VOCAB_SIZE=1024 VAL_LOSS_EVERY=200 BASELINE_COMPARE_JSON=/workspace/parameter-golf/logs/experiments/next_1xh100_workstream/shared_depth_stable/20260322_010500_ablate_shared_depth_stable_1xh100_retry1/summary.json bash scripts/experiments/run_1xh100_ablation.sh shared_depth_ttc_rsd_lite

## Confirmed Metrics

- `final_val_loss`: 2.42229808
- `final_val_bpb`: 1.43462137
- `final_metric_source`: final_int8_zlib_roundtrip_exact
- `final_eval_time_ms`: 11151
- `stop_reason`: wallclock_cap
- `stop_step`: 1085
- `stop_train_time_ms`: 600386
- `peak_memory_allocated_mib`: 11660
- `peak_memory_reserved_mib`: 12566
- `model_int8_zlib_bytes`: 4496338
- `code_bytes`: 72661
- `total_submission_size_int8_zlib_bytes`: 4568999

## Comparison

- `comparison.label`: shared_depth_stable_same_pod_control
- `comparison.delta_val_loss`: 0.02533623
- `comparison.delta_val_bpb`: 0.01500555
- `comparison.delta_bytes_total`: -372087
- `comparison.delta_stop_step`: -324
- `comparison.delta_eval_time_ms`: -4

## Compare Target Provenance

- `compare_target.path`: C:\Users\g3n_i\Desktop\0. Coding\Projects\parameter-golf\logs\experiments\next_1xh100_workstream\shared_depth_stable\20260322_010500_ablate_shared_depth_stable_1xh100_retry1\summary.json
- `compare_target.label`: shared_depth_stable_same_pod_control
- `compare_target.source_run_id`: 
- `compare_target.source_commit_sha`: 
- `compare_target.anchor_status`: 
- `compare_target.provenance_status`: 
- `compare_target.raw_log_present`: 
- `compare_target.raw_result_packet_present`: 
- `compare_target.requires_rebuild_before_ablation`: 

## Run Provenance

- `provenance.git.commit_sha`: 6235d57295cf2ef0e4a5289b0c2a621b8948b304
- `provenance.code.sha256`: f031acbfdc5504d228605105d88f9916b2eec0069f3805d336eddc2374093d33
- `provenance.dataset.manifest_sha256`: c0ebc88d5ac10324c8dc29c9c27041ec0efdc6441f9be747901c4f7f45f59ae9
- `provenance.tokenizer.sha256`: 4f5e8adb109c66b4886963bc75a7befd73bda36d27fd7102df8e9e66503b0e2a

## Confirmed Findings

- The TTC retry completed with final_int8_zlib_roundtrip_exact val_bpb=1.43462137 at stop_step=1085 and total_int8_zlib_bytes=4568999.
- The TTC logs showed distillation enabled every 4 steps with lambda warming to 0.05 and teacher_time_share stabilizing near 0.143 by the later logged steps.
- Relative to the same-pod shared-depth control at val_bpb=1.41961582, the TTC run regressed by +0.01500555 val_bpb and stopped 324 steps earlier under the same 600s cap.
- The first TTC attempt failed immediately because teacher total passes exceeded the student skip-weight count; the retry succeeded after a minimal guard that omits extra weighted skips beyond the student skip-weight budget.

## Inferred Conclusions

- On the current 1xH100 surrogate path, this TTC-RSD-lite configuration spends meaningful train-time compute but does not recover the resulting step-count loss in validation quality.

## Notes

- Fresh same-pod TTC recurrent self-distillation retry after teacher skip-weight overrun fix.

## Artifact Cap Check

- `artifact_cap_bytes`: 16000000
- `artifact_cap_ok`: True
- `counted_total_bytes`: 4568999
- `counted_total_bytes_source`: total_submission_size_int8_zlib_bytes
