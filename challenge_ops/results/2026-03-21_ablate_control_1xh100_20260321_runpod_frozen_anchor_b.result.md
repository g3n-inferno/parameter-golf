# Experiment Result

## Run Identity

- `run_id`: ablate_control_1xh100_20260321_runpod_frozen_anchor_b
- `experiment_id`: control_runpod_1xh100_20260321_frozen_anchor_confirm
- `date`: 2026-03-21
- `branch`: detached
- `commit_sha`: c59338a1920870c1648faf90c29416f15ebf63bf
- `log_path`: C:\Users\g3n_i\Desktop\0. Coding\Projects\parameter-golf\logs\experiments\next_1xh100_workstream\control\20260321_003337_ablate_control_1xh100_20260321_runpod_frozen_anchor_b\run.log
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
- `exact_command`: RUN_ID=ablate_control_1xh100_20260321_runpod_frozen_anchor_b TARGET_GPU_LABEL=h100_sxm_reuse474_frozen bash scripts/experiments/run_1xh100_ablation.sh control

## Confirmed Metrics

- `final_val_loss`: 2.24188124
- `final_val_bpb`: 1.32776835
- `final_metric_source`: final_int8_zlib_roundtrip_exact
- `final_eval_time_ms`: 11073
- `stop_reason`: wallclock_cap
- `stop_step`: 1387
- `stop_train_time_ms`: 600289
- `peak_memory_allocated_mib`: 10239
- `peak_memory_reserved_mib`: 10554
- `model_int8_zlib_bytes`: 13625409
- `code_bytes`: 61795
- `total_submission_size_int8_zlib_bytes`: 13687204

## Comparison

- `comparison.label`: runpod_1xh100_control_anchor
- `comparison.delta_val_loss`: 0.01045709
- `comparison.delta_val_bpb`: 0.00619328
- `comparison.delta_bytes_total`: -317360
- `comparison.delta_stop_step`: -119
- `comparison.delta_eval_time_ms`: 

## Compare Target Provenance

- `compare_target.path`: C:\Users\g3n_i\Desktop\0. Coding\Projects\parameter-golf\experiments\baselines\runpod_1xh100_control_anchor_summary.json
- `compare_target.label`: runpod_1xh100_control_anchor
- `compare_target.source_run_id`: ablate_control_1xh100_1024
- `compare_target.source_commit_sha`: ac7e33ddcb84253c3ed713668785c3b598c8259b
- `compare_target.anchor_status`: provisional_legacy
- `compare_target.provenance_status`: mirrored_from_ledger_only
- `compare_target.raw_log_present`: False
- `compare_target.raw_result_packet_present`: False
- `compare_target.requires_rebuild_before_ablation`: True

## Run Provenance

- `provenance.git.commit_sha`: c59338a1920870c1648faf90c29416f15ebf63bf
- `provenance.code.sha256`: 15846ddcd260753dbd7023522e1e12a6d0dec0dd5cb5e5a69446b6407a3b7bd5
- `provenance.dataset.manifest_sha256`: c0ebc88d5ac10324c8dc29c9c27041ec0efdc6441f9be747901c4f7f45f59ae9
- `provenance.tokenizer.sha256`: 4f5e8adb109c66b4886963bc75a7befd73bda36d27fd7102df8e9e66503b0e2a

## Confirmed Findings

- none recorded

## Inferred Conclusions

- none recorded

## Notes

- Second provenance-hardened same-pod control rerun on reused stable-profile pod 474jlphqpo5n8x; best rebuilt-control metric of the session.

## Artifact Cap Check

- `artifact_cap_bytes`: 16000000
- `artifact_cap_ok`: True
- `counted_total_bytes`: 13687204
- `counted_total_bytes_source`: total_submission_size_int8_zlib_bytes
