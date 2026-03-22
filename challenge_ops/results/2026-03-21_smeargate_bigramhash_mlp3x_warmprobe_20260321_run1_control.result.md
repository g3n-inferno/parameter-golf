# Experiment Result

## Run Identity

- `run_id`: smeargate_bigramhash_mlp3x_warmprobe_20260321_run1_control
- `experiment_id`: smeargate_bigramhash_mlp3x_warmprobe_20260321
- `date`: 2026-03-21
- `branch`: main
- `commit_sha`: d1200c7c450a3da03dff0cdcf392b6340e645aaf
- `log_path`: C:\Users\g3n_i\Desktop\0. Coding\Projects\parameter-golf\artifacts\runpod\smeargate_bigramhash_mlp3x_warmprobe_20260321\run1\run.log
- `code_path`: train_gpt.py

## Standardized Classification

- `idea_label`: Control 1xH100 warm-up
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
- `core_hparams`: seq1024 9x512 kv4 mlp_mult2 tied_emb baseline_schedule warmup_before_smeargate_probe
- `exact_command`: RUN_ID=smeargate_bigramhash_mlp3x_warmprobe_20260321_run1_control TARGET_GPU_LABEL=h100_sxm_warmup_control DATA_PATH=/workspace/parameter-golf/data/datasets/fineweb10B_sp1024 TOKENIZER_PATH=/workspace/parameter-golf/data/tokenizers/fineweb_1024_bpe.model VOCAB_SIZE=1024 VAL_LOSS_EVERY=200 MAX_WALLCLOCK_SECONDS=600 bash scripts/experiments/run_baseline_1gpu.sh

## Confirmed Metrics

- `final_val_loss`: 2.27868765
- `final_val_bpb`: 1.34956718
- `final_metric_source`: final_int8_zlib_roundtrip_exact
- `final_eval_time_ms`: 11118
- `stop_reason`: wallclock_cap
- `stop_step`: 1131
- `stop_train_time_ms`: 600014
- `peak_memory_allocated_mib`: 10239
- `peak_memory_reserved_mib`: 10748
- `model_int8_zlib_bytes`: 12781623
- `code_bytes`: 61795
- `total_submission_size_int8_zlib_bytes`: 12843418

## Comparison

- `comparison.label`: 
- `comparison.delta_val_loss`: 
- `comparison.delta_val_bpb`: 
- `comparison.delta_bytes_total`: 
- `comparison.delta_stop_step`: 
- `comparison.delta_eval_time_ms`: 

## Compare Target Provenance

- `compare_target.path`: 
- `compare_target.label`: 
- `compare_target.source_run_id`: 
- `compare_target.source_commit_sha`: 
- `compare_target.anchor_status`: 
- `compare_target.provenance_status`: 
- `compare_target.raw_log_present`: 
- `compare_target.raw_result_packet_present`: 
- `compare_target.requires_rebuild_before_ablation`: 

## Run Provenance

- `provenance.git.commit_sha`: d1200c7c450a3da03dff0cdcf392b6340e645aaf
- `provenance.code.sha256`: 15846ddcd260753dbd7023522e1e12a6d0dec0dd5cb5e5a69446b6407a3b7bd5
- `provenance.dataset.manifest_sha256`: c0ebc88d5ac10324c8dc29c9c27041ec0efdc6441f9be747901c4f7f45f59ae9
- `provenance.tokenizer.sha256`: 4f5e8adb109c66b4886963bc75a7befd73bda36d27fd7102df8e9e66503b0e2a

## Confirmed Findings

- final_int8_zlib_roundtrip_exact val_bpb=1.34956718 with total_int8_zlib_bytes=12843418 and stop_step=1131 under the 600s cap.
- The warm-up control stayed near the fresh-first-run control regime rather than the warmer same-pod second-run regime.

## Inferred Conclusions

- This run is usable only as the immediate pod-local warm-up anchor for the paired surrogate probe, not as a new promoted control frontier.

## Notes

- Fresh official-template 1xH100 warm-up control on pod aagwbrm1z1rrej before the SmearGate/BigramHash/MLP3x probe; local log copied off the zero-volume pod before shutdown.

## Artifact Cap Check

- `artifact_cap_bytes`: 16000000
- `artifact_cap_ok`: True
- `counted_total_bytes`: 12843418
- `counted_total_bytes_source`: total_submission_size_int8_zlib_bytes
