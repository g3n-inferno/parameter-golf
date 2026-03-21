# Experiment Result

## Run Identity

- `run_id`: ablate_control_1xh100_20260320_runpod_stable
- `experiment_id`: control_runpod_1xh100_20260320_stable_profile
- `date`: 2026-03-20
- `branch`: main
- `commit_sha`: bc75d7b0c350a41af25131232854833340265e86
- `log_path`: C:\Users\g3n_i\Desktop\0. Coding\Projects\parameter-golf\logs\experiments\next_1xh100_workstream\control\20260320_214306_ablate_control_1xh100_20260320_runpod_stable\run.log
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
- `exact_command`: RUN_ID=ablate_control_1xh100_20260320_runpod_stable TARGET_GPU_LABEL=h100_sxm_stable bash scripts/experiments/run_1xh100_ablation.sh control

## Confirmed Metrics

- `final_val_loss`: 2.28415990
- `final_val_bpb`: 1.35280815
- `final_metric_source`: final_int8_zlib_roundtrip_exact
- `final_eval_time_ms`: 11165
- `stop_reason`: wallclock_cap
- `stop_step`: 1145
- `stop_train_time_ms`: 600423
- `peak_memory_allocated_mib`: 10239
- `peak_memory_reserved_mib`: 10748
- `model_int8_zlib_bytes`: 12435489
- `code_bytes`: 61795
- `total_submission_size_int8_zlib_bytes`: 12497284

## Comparison

- `comparison.label`: runpod_1xh100_control_anchor
- `comparison.delta_val_loss`: 0.05273575
- `comparison.delta_val_bpb`: 0.03123308
- `comparison.delta_bytes_total`: -1507280
- `comparison.delta_stop_step`: -361
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

- `provenance.git.commit_sha`: 
- `provenance.code.sha256`: 
- `provenance.dataset.manifest_sha256`: 
- `provenance.tokenizer.sha256`: 

## Confirmed Findings

- Restart attempts on previously stopped matching pods 9p5aq98sa8j6go, xgi77lp1vapny8, and zzp4jchfuh2ky3 all failed with 'There are not enough free GPUs on the host machine to start this pod.', so reuse was unavailable.
- Fresh pod 474jlphqpo5n8x was created with template y5cejece4j in US-MO-1 and passed challenge_ops/runpod_1xh100_control_profile.json: H100, 1 GPU, runpod/parameter-golf:latest, 20GB container disk, 0GB volume, secure cloud, US location, and 26 vCPUs.
- The remote checkout was pinned to bc75d7b0c350a41af25131232854833340265e86, and preflight confirmed /workspace/parameter-golf/data/datasets/fineweb10B_sp1024 with 80 train shards, 1 validation shard, and tokenizer /workspace/parameter-golf/data/tokenizers/fineweb_1024_bpe.model.
- The exact control command was RUN_ID=ablate_control_1xh100_20260320_runpod_stable TARGET_GPU_LABEL=h100_sxm_stable bash scripts/experiments/run_1xh100_ablation.sh control.
- The run finished with final_int8_zlib_roundtrip_exact val_loss=2.28415990, val_bpb=1.35280815, total_submission_size_int8_zlib_bytes=12497284, stop_step=1145, and final_eval_time_ms=11165.
- Relative to the provisional legacy Runpod 1xH100 control anchor ablate_control_1xh100_1024, delta_val_bpb was +0.03123308, delta_val_loss was +0.05273575, and counted total bytes were -1507280.
- No surrogate ablation was run because the declared recovery gate was val_bpb <= 1.32657507 and this control rerun missed it by +0.02623308.

## Inferred Conclusions

- Matching the pod to the stable US/26-vCPU control profile did not recover the Runpod 1xH100 control path, so the earlier regression cannot be explained away by the low-vCPU EUR-NO-2 host alone.
- Because the compare target remains a provisional legacy anchor mirrored from the ledger rather than a frozen raw packet, paid 1xH100-surrogate ablations should remain paused until a new frozen control anchor is rebuilt.

## Notes

- Stable-profile control rerun on fresh pod 474jlphqpo5n8x after failed restart attempts on 9p5aq98sa8j6go, xgi77lp1vapny8, and zzp4jchfuh2ky3. Pod matched challenge_ops/runpod_1xh100_control_profile.json, and no surrogate ablation was run because the control gate failed.

## Artifact Cap Check

- `artifact_cap_bytes`: 16000000
- `artifact_cap_ok`: True
- `counted_total_bytes`: 12497284
- `counted_total_bytes_source`: total_submission_size_int8_zlib_bytes
