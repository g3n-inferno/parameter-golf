# Experiment Result

## Run Identity

- `run_id`: smeargate_bigramhash_mlp3x_warmprobe_20260321_run2_model
- `experiment_id`: smeargate_bigramhash_mlp3x_warmprobe_20260321
- `date`: 2026-03-21
- `branch`: main
- `commit_sha`: d1200c7c450a3da03dff0cdcf392b6340e645aaf
- `log_path`: C:\Users\g3n_i\Desktop\0. Coding\Projects\parameter-golf\artifacts\runpod\smeargate_bigramhash_mlp3x_warmprobe_20260321\run2\run.log
- `code_path`: records/track_10min_16mb/2026-03-20_Int6_MLP3x_SmearGate_BigramHash_MuonWD_SWA/train_gpt.py

## Standardized Classification

- `idea_label`: Int6 MLP3x + SmearGate + BigramHash + OrthoInit + Muon WD + SWA
- `standardized_name`: smeargate_bigramhash_mlp3x_muonwd_swa
- `lineage`: novel
- `state`: already-tried
- `result`: negative
- `track_intent`: non-record
- `scope`: 1xH100-surrogate

## Run Context

- `dataset_variant`: fineweb10B_sp1024
- `tokenizer_variant`: fineweb_1024_bpe.model
- `hardware`: 1xH100 Runpod NVIDIA H100 80GB HBM3
- `wallclock_target`: 600s
- `core_hparams`: seq2048 9x512 kv4 mlp_mult3 int6 smeargate bigramhash4096 dim128 tied_emb muon_wd swa stride64
- `exact_command`: RUN_ID=smeargate_bigramhash_mlp3x_warmprobe_20260321_run2_model TARGET_GPU_LABEL=h100_sxm_warm_model DATA_PATH=/workspace/parameter-golf/data/datasets/fineweb10B_sp1024 TOKENIZER_PATH=/workspace/parameter-golf/data/tokenizers/fineweb_1024_bpe.model VOCAB_SIZE=1024 NUM_LAYERS=9 MODEL_DIM=512 NUM_HEADS=8 NUM_KV_HEADS=4 MLP_MULT=3 TRAIN_SEQ_LEN=2048 TRAIN_BATCH_TOKENS=786432 MATRIX_LR=0.02 SCALAR_LR=0.02 TIED_EMBED_LR=0.03 MUON_MOMENTUM=0.99 MUON_MOMENTUM_WARMUP_START=0.92 MUON_MOMENTUM_WARMUP_STEPS=1500 WARMDOWN_ITERS=3000 GRAD_CLIP_NORM=0.3 BIGRAM_VOCAB_SIZE=4096 BIGRAM_DIM=128 EVAL_STRIDE=64 SWA_ENABLED=1 SWA_START_FRAC=0.5 SWA_EVERY=50 VAL_LOSS_EVERY=200 MAX_WALLCLOCK_SECONDS=600 bash scripts/experiments/run_baseline_1gpu.sh

## Confirmed Metrics

- `final_val_loss`: 2.52864608
- `final_val_bpb`: 1.49761060
- `final_metric_source`: final_int8_zlib_roundtrip_exact
- `final_eval_time_ms`: 1220523
- `stop_reason`: wallclock_cap
- `stop_step`: 968
- `stop_train_time_ms`: 600202
- `peak_memory_allocated_mib`: 17113
- `peak_memory_reserved_mib`: 17212
- `model_int8_zlib_bytes`: 
- `code_bytes`: 52243
- `total_submission_size_int8_zlib_bytes`: 16290010

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
- `provenance.code.sha256`: 138aeff57aeaf9e50b5077e0fd8388b038f8e09e5c7af3154109ea5815c11e2b
- `provenance.dataset.manifest_sha256`: c0ebc88d5ac10324c8dc29c9c27041ec0efdc6441f9be747901c4f7f45f59ae9
- `provenance.tokenizer.sha256`: 4f5e8adb109c66b4886963bc75a7befd73bda36d27fd7102df8e9e66503b0e2a

## Confirmed Findings

- final_int8_zlib_roundtrip_exact val_bpb=1.49761060 with stop_step=968, step_avg_ms=620.04, and final_eval_time_ms=1220523.
- The counted int8+zlib artifact total was 16290010 bytes, which exceeds the 16000000-byte challenge cap by 290010 bytes.
- Relative to the immediate warm-up control on the same pod, the model probe regressed val_bpb by 0.14804342 while also taking 163 fewer optimizer steps under the same 600s cap.

## Inferred Conclusions

- This direct 1xH100 warmed surrogate of the leaderboard SmearGate/BigramHash/MLP3x family is not competitive as configured and should not be repeated unchanged.

## Notes

- Warmed second-run surrogate probe on the same fresh official-template pod aagwbrm1z1rrej after a baseline warm-up control. The remote shell-script copy initially failed because of CRLF line endings; the copied shell and Python helper files were normalized to LF before the successful run. Counted int8+zlib size exceeded the 16000000-byte challenge cap by 290010 bytes, so this is strictly a negative surrogate record, not a candidate packaging path.

## Artifact Cap Check

- `artifact_cap_bytes`: 16000000
- `artifact_cap_ok`: False
- `counted_total_bytes`: 16290010
- `counted_total_bytes_source`: total_submission_size_int8_zlib_bytes
