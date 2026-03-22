# Experiment Result

## Run Identity

- `run_id`: ablate_shared_depth_stable_1xh100_retry1
- `experiment_id`: shared_depth_ttc_rsd_lite_runpod_20260321_control
- `date`: 2026-03-21
- `branch`: main
- `commit_sha`: 6235d57295cf2ef0e4a5289b0c2a621b8948b304
- `log_path`: C:\Users\g3n_i\Desktop\0. Coding\Projects\parameter-golf\logs\experiments\next_1xh100_workstream\shared_depth_stable\20260322_010500_ablate_shared_depth_stable_1xh100_retry1\run.log
- `code_path`: train_gpt.py

## Standardized Classification

- `idea_label`: Shared-Depth Stable
- `standardized_name`: shared_depth_stable_cyclic_inv_sqrt_reuse
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
- `core_hparams`: seq1024 shared_depth cyclic unique3 passes9 resid_scale=inv_sqrt_reuse
- `exact_command`: RUN_ID=ablate_shared_depth_stable_1xh100_retry1 TARGET_GPU_LABEL=h100_sxm_shared_depth_control DATA_PATH=/workspace/parameter-golf/data/datasets/fineweb10B_sp1024 TOKENIZER_PATH=/workspace/parameter-golf/data/tokenizers/fineweb_1024_bpe.model VOCAB_SIZE=1024 VAL_LOSS_EVERY=200 BASELINE_COMPARE_JSON=/workspace/parameter-golf/challenge_ops/results/2026-03-21_control_path_diagnosis_20260321_fresh_template_runpod.result.json bash scripts/experiments/run_1xh100_ablation.sh shared_depth_stable

## Confirmed Metrics

- `final_val_loss`: 2.39696185
- `final_val_bpb`: 1.41961582
- `final_metric_source`: final_int8_zlib_roundtrip_exact
- `final_eval_time_ms`: 11155
- `stop_reason`: wallclock_cap
- `stop_step`: 1409
- `stop_train_time_ms`: 600282
- `peak_memory_allocated_mib`: 10127
- `peak_memory_reserved_mib`: 10290
- `model_int8_zlib_bytes`: 4868507
- `code_bytes`: 72579
- `total_submission_size_int8_zlib_bytes`: 4941086

## Comparison

- `comparison.label`: fresh_template_control_path
- `comparison.delta_val_loss`: 0.11274938
- `comparison.delta_val_bpb`: 0.06677653
- `comparison.delta_bytes_total`: -7867790
- `comparison.delta_stop_step`: 302
- `comparison.delta_eval_time_ms`: -21

## Compare Target Provenance

- `compare_target.path`: C:\Users\g3n_i\Desktop\0. Coding\Projects\parameter-golf\challenge_ops\results\2026-03-21_control_path_diagnosis_20260321_fresh_template_runpod.result.json
- `compare_target.label`: fresh_template_control_path
- `compare_target.source_run_id`: 
- `compare_target.source_commit_sha`: 
- `compare_target.anchor_status`: 
- `compare_target.provenance_status`: 
- `compare_target.raw_log_present`: 
- `compare_target.raw_result_packet_present`: 
- `compare_target.requires_rebuild_before_ablation`: 

## Run Provenance

- `provenance.git.commit_sha`: 6235d57295cf2ef0e4a5289b0c2a621b8948b304
- `provenance.code.sha256`: 168532ac3a0d31ab54d1d6fd878db38a606cbf7122f1bf313aacb982e91c4dae
- `provenance.dataset.manifest_sha256`: c0ebc88d5ac10324c8dc29c9c27041ec0efdc6441f9be747901c4f7f45f59ae9
- `provenance.tokenizer.sha256`: 4f5e8adb109c66b4886963bc75a7befd73bda36d27fd7102df8e9e66503b0e2a

## Confirmed Findings

- The patched shared-depth control path completed on Runpod 1xH100 with final_int8_zlib_roundtrip_exact val_bpb=1.41961582 at stop_step=1409.
- The counted artifact size was 4941086 bytes total_int8_zlib, with code_bytes=72579 and model_int8_zlib_bytes=4868507.
- Relative to the fresh-template control reference at val_bpb=1.35283929, this shared-depth control regressed by +0.06677653 val_bpb while reaching +302 more optimizer steps under the same 600s cap.

## Inferred Conclusions

- The shared-depth stable control is materially worse than the fresh baseline-style control on the current 1xH100 surrogate path, but it leaves large artifact headroom for train-time-compute variants.

## Notes

- Fresh same-pod shared-depth control under patched train_gpt.py for TTC comparison.

## Artifact Cap Check

- `artifact_cap_bytes`: 16000000
- `artifact_cap_ok`: True
- `counted_total_bytes`: 4941086
- `counted_total_bytes_source`: total_submission_size_int8_zlib_bytes
