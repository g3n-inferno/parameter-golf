# Experiment Result

## Run Identity

- `run_id`: ablate_control_1xh100_20260320_runpod_retry2
- `experiment_id`: control_runpod_1xh100_20260320_retry2
- `date`: 2026-03-20
- `branch`: main
- `commit_sha`: 90effbae28001f2356b5638fbde9812c0d50f700
- `log_path`: C:\Users\g3n_i\Desktop\0. Coding\Projects\parameter-golf\logs\experiments\next_1xh100_workstream\control\20260320_183925_ablate_control_1xh100_20260320_runpod_retry2\run.log
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
- `exact_command`: RUN_ID=ablate_control_1xh100_20260320_runpod_retry2 TARGET_GPU_LABEL=h100_sxm bash scripts/experiments/run_1xh100_ablation.sh control

## Confirmed Metrics

- `final_val_loss`: 2.25439935
- `final_val_bpb`: 1.33518228
- `final_metric_source`: final_int8_zlib_roundtrip_exact
- `final_eval_time_ms`: 11125
- `stop_reason`: wallclock_cap
- `stop_step`: 1282
- `stop_train_time_ms`: 600357
- `peak_memory_allocated_mib`: 10239
- `peak_memory_reserved_mib`: 10748
- `model_int8_zlib_bytes`: 13611740
- `code_bytes`: 61795
- `total_submission_size_int8_zlib_bytes`: 13673535

## Comparison

- `comparison.label`: runpod_1xh100_control_anchor
- `comparison.delta_val_loss`: 0.02021277
- `comparison.delta_val_bpb`: 0.01197114
- `comparison.delta_bytes_total`: -364325
- `comparison.delta_stop_step`: -162
- `comparison.delta_eval_time_ms`: -33

## Confirmed Findings

- Fresh pod xgi77lp1vapny8 was a single NVIDIA H100 80GB HBM3 pod on the official Parameter Golf template and was stopped immediately after log sync.
- The pod passed the repo verify script, the sp1024 export completed, and the remote dataset path had 80 training shards, 1 validation shard, and the expected tokenizer before training.
- The run finished with final_int8_zlib_roundtrip_exact val_loss=2.25439935, val_bpb=1.33518228, total_submission_size_int8_zlib_bytes=13673535, stop_step=1282, and final_eval_time_ms=11125.
- Relative to the legacy compatibility file `experiments/baselines/local_1xh100_baseline_summary.json`, which stores the Runpod `1xH100` control anchor, delta_val_bpb was +0.01197114 and delta_val_loss was +0.02021277.
- Relative to ablate_control_1xh100_1024, delta_val_bpb was +0.01360721; relative to ablate_lr_warmdown_1xh100_20260320_runpod, delta_val_bpb was +0.00459506.

## Inferred Conclusions

- Because the clean remote control rerun is materially worse than both the current Runpod `1xH100` control anchor and the earlier remote lr_warmdown run, the dominant issue is workflow variance rather than an idea-specific lr_warmdown failure.
- LR Warmdown should remain inconclusive at 1xH100-surrogate scope, while the remote control family itself should be treated as mixed or inconclusive until the workflow is stabilized.

## Notes

- Fresh single-pod retry on pod xgi77lp1vapny8 with no subagents touching Runpod. The run completed on main@90effbae28001f2356b5638fbde9812c0d50f700 and establishes a clean same-workflow Runpod `1xH100` control anchor.

## Artifact Cap Check

- `artifact_cap_bytes`: 16000000
- `artifact_cap_ok`: True
- `counted_total_bytes`: 13673535
- `counted_total_bytes_source`: total_submission_size_int8_zlib_bytes
