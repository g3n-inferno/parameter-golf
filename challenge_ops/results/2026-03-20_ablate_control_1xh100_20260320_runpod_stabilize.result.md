# Experiment Result

## Run Identity

- `run_id`: ablate_control_1xh100_20260320_runpod_stabilize
- `experiment_id`: control_runpod_1xh100_20260320_stabilization
- `date`: 2026-03-20
- `branch`: main
- `commit_sha`: bc75d7b0c350a41af25131232854833340265e86
- `log_path`: C:\Users\g3n_i\Desktop\0. Coding\Projects\parameter-golf\logs\experiments\next_1xh100_workstream\control\20260320_200015_ablate_control_1xh100_20260320_runpod_stabilize\run.log
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
- `exact_command`: RUN_ID=ablate_control_1xh100_20260320_runpod_stabilize TARGET_GPU_LABEL=h100_sxm bash scripts/experiments/run_1xh100_ablation.sh control

## Confirmed Metrics

- `final_val_loss`: 2.27686994
- `final_val_bpb`: 1.34849063
- `final_metric_source`: final_int8_zlib_roundtrip_exact
- `final_eval_time_ms`: 11152
- `stop_reason`: wallclock_cap
- `stop_step`: 1152
- `stop_train_time_ms`: 600351
- `peak_memory_allocated_mib`: 10239
- `peak_memory_reserved_mib`: 10748
- `model_int8_zlib_bytes`: 12878462
- `code_bytes`: 61795
- `total_submission_size_int8_zlib_bytes`: 12940257

## Comparison

- `comparison.label`: runpod_1xh100_control_anchor
- `comparison.delta_val_loss`: 0.04544579
- `comparison.delta_val_bpb`: 0.02691556
- `comparison.delta_bytes_total`: -1064307
- `comparison.delta_stop_step`: -354
- `comparison.delta_eval_time_ms`: 

## Confirmed Findings

- Fresh pod vlmy3ngmeqbq96 was a single NVIDIA H100 80GB HBM3 pod on the official Parameter Golf template with volumeInGb=0, and the remote checkout was pinned to bc75d7b0c350a41af25131232854833340265e86 before dataset or training steps.
- The pod passed scripts/runpod/verify_pod_env.sh, the full sp1024 export completed, and preflight confirmed /workspace/parameter-golf/data/datasets/fineweb10B_sp1024 with 80 train shards, 1 validation shard, and tokenizer /workspace/parameter-golf/data/tokenizers/fineweb_1024_bpe.model.
- The exact control command was RUN_ID=ablate_control_1xh100_20260320_runpod_stabilize TARGET_GPU_LABEL=h100_sxm bash scripts/experiments/run_1xh100_ablation.sh control, writing logs under /workspace/parameter-golf/logs/experiments/next_1xh100_workstream/control/20260320_200015_ablate_control_1xh100_20260320_runpod_stabilize/.
- The run finished with final_int8_zlib_roundtrip_exact val_loss=2.27686994, val_bpb=1.34849063, total_submission_size_int8_zlib_bytes=12940257, stop_step=1152, and final_eval_time_ms=11152.
- Relative to the adopted Runpod 1xH100 control anchor ablate_control_1xh100_1024, delta_val_bpb was +0.02691556, delta_val_loss was +0.04544579, and counted total bytes were -1064307.
- Relative to ablate_control_1xh100_20260320_runpod_retry2, delta_val_bpb was +0.01330835; relative to ablate_lr_warmdown_1xh100_20260320_runpod, delta_val_bpb was +0.01790341; relative to the older legacy Runpod baseline summary, delta_val_bpb was +0.02527949.

## Inferred Conclusions

- This rerun does not stabilize the Runpod 1xH100 control path; it regressed materially beyond both the adopted control anchor and the prior clean retry on the same remote family.
- 1xH100-surrogate ablations should remain paused until the control path has an identified variance cause or a repeatable recovery to the adopted Runpod 1xH100 control anchor.

## Notes

- Fresh single-pod Runpod H100 SXM control stabilization rerun on pod vlmy3ngmeqbq96 with direct SSH, detached checkout at main@bc75d7b0c350a41af25131232854833340265e86, and explicit stop after artifact sync.

## Artifact Cap Check

- `artifact_cap_bytes`: 16000000
- `artifact_cap_ok`: True
- `counted_total_bytes`: 12940257
- `counted_total_bytes_source`: total_submission_size_int8_zlib_bytes
