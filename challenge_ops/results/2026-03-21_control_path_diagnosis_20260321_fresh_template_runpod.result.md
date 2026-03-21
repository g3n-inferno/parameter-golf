# Experiment Result

## Run Identity

- `run_id`: control_path_diagnosis_20260321_fresh_template_runpod
- `experiment_id`: control_path_diagnosis_20260321_fresh_template
- `date`: 2026-03-21
- `branch`: main
- `commit_sha`: 82189d277df1191bdc7211d0783d6b7718548cd4
- `log_path`: C:\Users\g3n_i\Desktop\0. Coding\Projects\parameter-golf\artifacts\runpod\control_path_diagnosis_20260321_fresh_template_runpod\run.log
- `code_path`: train_gpt.py

## Standardized Classification

- `idea_label`: Control 1xH100
- `standardized_name`: runpod_1xh100_control_anchor
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
- `core_hparams`: seq1024 9x512 kv4 mlp_mult2 tied_emb baseline_schedule
- `exact_command`: RUN_ID=control_path_diagnosis_20260321_fresh_template_runpod TARGET_GPU_LABEL=h100_sxm_fresh_template DATA_PATH=/workspace/parameter-golf/data/datasets/fineweb10B_sp1024 TOKENIZER_PATH=/workspace/parameter-golf/data/tokenizers/fineweb_1024_bpe.model VOCAB_SIZE=1024 VAL_LOSS_EVERY=200 bash scripts/experiments/run_baseline_1gpu.sh

## Confirmed Metrics

- `final_val_loss`: 2.28421247
- `final_val_bpb`: 1.35283929
- `final_metric_source`: final_int8_zlib_roundtrip_exact
- `final_eval_time_ms`: 11176
- `stop_reason`: wallclock_cap
- `stop_step`: 1107
- `stop_train_time_ms`: 600221
- `peak_memory_allocated_mib`: 10239
- `peak_memory_reserved_mib`: 10748
- `model_int8_zlib_bytes`: 12747081
- `code_bytes`: 61795
- `total_submission_size_int8_zlib_bytes`: 12808876

## Comparison

- `comparison.label`: runpod_1xh100_control_anchor_summary
- `comparison.delta_val_loss`: 0.05278832
- `comparison.delta_val_bpb`: 0.03126422
- `comparison.delta_bytes_total`: -1195688
- `comparison.delta_stop_step`: -399
- `comparison.delta_eval_time_ms`: 

## Compare Target Provenance

- `compare_target.path`: C:\Users\g3n_i\Desktop\0. Coding\Projects\parameter-golf\experiments\baselines\runpod_1xh100_control_anchor_summary.json
- `compare_target.label`: runpod_1xh100_control_anchor_summary
- `compare_target.source_run_id`: ablate_control_1xh100_1024
- `compare_target.source_commit_sha`: ac7e33ddcb84253c3ed713668785c3b598c8259b
- `compare_target.anchor_status`: provisional_legacy
- `compare_target.provenance_status`: mirrored_from_ledger_only
- `compare_target.raw_log_present`: False
- `compare_target.raw_result_packet_present`: False
- `compare_target.requires_rebuild_before_ablation`: True

## Run Provenance

- `provenance.git.commit_sha`: 82189d277df1191bdc7211d0783d6b7718548cd4
- `provenance.code.sha256`: 15846ddcd260753dbd7023522e1e12a6d0dec0dd5cb5e5a69446b6407a3b7bd5
- `provenance.dataset.manifest_sha256`: c0ebc88d5ac10324c8dc29c9c27041ec0efdc6441f9be747901c4f7f45f59ae9
- `provenance.tokenizer.sha256`: 4f5e8adb109c66b4886963bc75a7befd73bda36d27fd7102df8e9e66503b0e2a

## Confirmed Findings

- Fresh official-template US-MO-1 H100 pod vhrzxwizzi276z matched the declared control profile and recovered a real checkout from a stub template in 3.704 seconds before training.
- The run completed under the 600s wallclock cap at stop_step=1107 with final_int8_zlib_roundtrip_exact val_loss=2.28421247 and val_bpb=1.35283929.
- Counted artifact size was total_int8_zlib=12808876 bytes with code_bytes=61795 and model_int8_zlib_bytes=12747081.

## Inferred Conclusions

- A fresh official-template US-MO-1 1xH100 control path reproduces the ~1.3528 regime, strengthening the case that the better 1.32776835 same-pod rebuild is not the stable fresh-pod control anchor.

## Notes

- Fresh official-template US-MO-1 H100 control diagnosis on new pod vhrzxwizzi276z after bounded checkout recovery from a stub template in 3.704s. final_int8_zlib_roundtrip_exact val_bpb=1.35283929, which is +0.00395778 worse than baseline_sp1024_1xh100_20260320_integrated_main and +0.00003114 from ablate_control_1xh100_20260320_runpod_stable.

## Artifact Cap Check

- `artifact_cap_bytes`: 16000000
- `artifact_cap_ok`: True
- `counted_total_bytes`: 12808876
- `counted_total_bytes_source`: total_submission_size_int8_zlib_bytes
