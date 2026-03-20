# Experiment Result

## Run Identity

- `run_id`: ablate_control_1xh100_20260320_runpod
- `experiment_id`: control_runpod_1xh100_20260320
- `date`: 2026-03-20
- `branch`: main
- `commit_sha`: 90effbae28001f2356b5638fbde9812c0d50f700
- `log_path`: C:\Users\g3n_i\Desktop\0. Coding\Projects\parameter-golf\logs\experiments\next_1xh100_workstream\control\20260320_182407_ablate_control_1xh100_20260320_runpod\run.log
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
- `core_hparams`: seq1024 9x512 kv4 mlp_mult2 tied_emb baseline_schedule
- `exact_command`: RUN_ID=ablate_control_1xh100_20260320_runpod TARGET_GPU_LABEL=h100_sxm bash scripts/experiments/run_1xh100_ablation.sh control

## Confirmed Metrics

- `final_val_loss`: 
- `final_val_bpb`: 
- `final_metric_source`: 
- `final_eval_time_ms`: 
- `stop_reason`: 
- `stop_step`: 
- `stop_train_time_ms`: 
- `peak_memory_allocated_mib`: 
- `peak_memory_reserved_mib`: 
- `model_int8_zlib_bytes`: 
- `code_bytes`: 
- `total_submission_size_int8_zlib_bytes`: 

## Comparison

- `comparison.label`: 
- `comparison.delta_val_loss`: 
- `comparison.delta_val_bpb`: 
- `comparison.delta_bytes_total`: 
- `comparison.delta_stop_step`: 
- `comparison.delta_eval_time_ms`: 

## Confirmed Findings

- Current pod 9p5aq98sa8j6go could not be resumed for the control rerun because Runpod returned 'There are not enough free GPUs on the host machine to start this pod.'
- Fallback pod zzp4jchfuh2ky3 was a 1x NVIDIA H100 80GB HBM3 pod on the official Parameter Golf template and passed the repo verify script before training.
- The fallback pod had the expected sp1024 dataset path with 80 training shards, 1 validation shard, and the expected tokenizer before the control command started.
- The control command emitted warmup_step 1/20 through 20/20, then the connection closed before any step or final metric lines were logged.

## Inferred Conclusions

- This attempt does not provide the discriminating control evidence needed to decide whether the earlier remote lr_warmdown regression was idea-specific.
- Remote workflow variance remains unresolved and should block further paid ablations until the control path is stable.

## Notes

- Main-thread failure evidence only. The original pod 9p5aq98sa8j6go could not be resumed because Runpod reported no free GPUs on the host. Fresh fallback pod zzp4jchfuh2ky3 on the official template reached the control command, printed warmup_step 1/20 through 20/20, then the SSH session was closed by the remote host and the pod exited before any train or validation metrics were emitted.
