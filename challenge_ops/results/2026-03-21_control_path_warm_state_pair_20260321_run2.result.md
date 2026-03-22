# Experiment Result

## Run Identity

- `run_id`: control_path_warm_state_pair_20260321_run2
- `experiment_id`: control_path_warm_state_pair_20260321
- `date`: 2026-03-21
- `branch`: main
- `commit_sha`: d1200c7c450a3da03dff0cdcf392b6340e645aaf
- `log_path`: C:\Users\g3n_i\Desktop\0. Coding\Projects\parameter-golf\artifacts\runpod\control_path_warm_state_pair_20260321\20260321_213405_control_path_warm_state_pair_20260321_run2\run.log
- `code_path`: train_gpt.py

## Standardized Classification

- `idea_label`: Control 1xH100
- `standardized_name`: runpod_1xh100_control_anchor
- `lineage`: variant
- `state`: already-tried
- `result`: inconclusive
- `track_intent`: non-record
- `scope`: 1xH100-surrogate

## Run Context

- `dataset_variant`: fineweb10B_sp1024
- `tokenizer_variant`: fineweb_1024_bpe.model
- `hardware`: 1xH100 Runpod NVIDIA H100 80GB HBM3
- `wallclock_target`: 600s
- `core_hparams`: seq1024 9x512 kv4 mlp_mult2 tied_emb baseline_schedule warm_state_pair_run2
- `exact_command`: env RUN_ID=control_path_warm_state_pair_20260321_run2 DATA_PATH=/workspace/parameter-golf/data/datasets/fineweb10B_sp1024 TOKENIZER_PATH=/workspace/parameter-golf/data/tokenizers/fineweb_1024_bpe.model VOCAB_SIZE=1024 TRAIN_LOG_EVERY=50 VAL_LOSS_EVERY=200 MAX_WALLCLOCK_SECONDS=600 torchrun --standalone --nproc_per_node=1 train_gpt.py

## Confirmed Metrics

- `final_val_loss`: 2.25837801
- `final_val_bpb`: 1.33753867
- `final_metric_source`: final_int8_zlib_roundtrip_exact
- `final_eval_time_ms`: 11156
- `stop_reason`: wallclock_cap
- `stop_step`: 1283
- `stop_train_time_ms`: 600222
- `peak_memory_allocated_mib`: 10239
- `peak_memory_reserved_mib`: 10554
- `model_int8_zlib_bytes`: 13240714
- `code_bytes`: 61795
- `total_submission_size_int8_zlib_bytes`: 13302509

## Comparison

- `comparison.label`: runpod_1xh100_control_anchor
- `comparison.delta_val_loss`: 0.02695386
- `comparison.delta_val_bpb`: 0.01596360
- `comparison.delta_bytes_total`: -702055
- `comparison.delta_stop_step`: -223
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

- `provenance.git.commit_sha`: d1200c7c450a3da03dff0cdcf392b6340e645aaf
- `provenance.code.sha256`: 15846ddcd260753dbd7023522e1e12a6d0dec0dd5cb5e5a69446b6407a3b7bd5
- `provenance.dataset.manifest_sha256`: c0ebc88d5ac10324c8dc29c9c27041ec0efdc6441f9be747901c4f7f45f59ae9
- `provenance.tokenizer.sha256`: 4f5e8adb109c66b4886963bc75a7befd73bda36d27fd7102df8e9e66503b0e2a

## Confirmed Findings

- Second run on the same unchanged pod/container landed at val_bpb=1.33753867 with stop_step=1283 and total_submission_size_int8_zlib_bytes=13302509.
- Compared with run 1, the second run improved val_bpb by 0.00210433, ran 9.37 ms per step faster, and reached 25 additional steps under the same 600s cap.

## Inferred Conclusions

- The second run materially supports a warm-state effect on the same pod, but it still does not fully recover the earlier 1.3278-1.3347 reused-pod range, so the control-family bottleneck is reduced rather than resolved.

## Notes

- Fresh official-template 1xH100 warm-state pair run 2 of 2. Local run.log reconstructed verbatim from captured SSH stdout after the zero-volume pod lost its remote log directory on post-run restart.

## Artifact Cap Check

- `artifact_cap_bytes`: 16000000
- `artifact_cap_ok`: True
- `counted_total_bytes`: 13302509
- `counted_total_bytes_source`: total_submission_size_int8_zlib_bytes
