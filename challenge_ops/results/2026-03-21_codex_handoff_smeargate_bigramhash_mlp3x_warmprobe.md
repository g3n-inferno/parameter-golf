# Codex Handoff

## Task

- Request summary: Run config `#1` from the leaderboard shortlist, using the prepared warmed same-pod `1xH100` surrogate protocol, and iterate until the result is comparable enough to the other candidate families.
- Scope: one fresh official-template `1xH100` Runpod pod, one warm-up control run, one warmed second-run SmearGate/BigramHash/MLP3x probe, then result capture and frontier-memory updates.
- Constraint summary: unchanged `fineweb10B_sp1024` dataset and `fineweb_1024_bpe.model`, no `8xH100`, one pod only, dry-run brief plus approval token before remote action, tracked Runpod usage, no submission packaging.

## Outcome

- Status: completed.
- What changed: ran the paired warm-up/probe experiment on pod `aagwbrm1z1rrej`, copied the canonical logs locally before shutdown, finished the tracked run/session, revoked the approval token, recorded both result packets, updated `experiments/ledger.csv`, and updated `challenge_ops/CURRENT_FRONTIER.md` plus `challenge_ops/TRIED_IDEAS_INDEX.md`.
- What did not change: dataset, tokenizer, accepted record folders, submission packaging, or any core training logic in the main repo.

## Confirmed Findings

- Fresh official-template pod `aagwbrm1z1rrej` was created from template `y5cejece4j`, matched the declared `US-MO-1` / `26`-vCPU H100 control profile, and used exactly one pod for the entire run.
- Warm-up control `smeargate_bigramhash_mlp3x_warmprobe_20260321_run1_control` finished at `final_int8_zlib_roundtrip_exact val_bpb=1.34956718`, `val_loss=2.27868765`, `stop_step=1131`, `step_avg_ms=530.52`, `final_eval_time_ms=11118`, `counted_total_bytes=12843418`.
- Warmed probe `smeargate_bigramhash_mlp3x_warmprobe_20260321_run2_model` finished at `final_int8_zlib_roundtrip_exact val_bpb=1.49761060`, `val_loss=2.52864608`, `stop_step=968`, `step_avg_ms=620.04`, `final_eval_time_ms=1220523`, `counted_total_bytes=16290010`.
- The warmed probe exceeded the challenge artifact cap by `290010` bytes and regressed the immediate same-pod warm-up control by `+0.14804342` `val_bpb`.
- Both runs recorded the same dataset manifest hash `c0ebc88d5ac10324c8dc29c9c27041ec0efdc6441f9be747901c4f7f45f59ae9`, tokenizer hash `4f5e8adb109c66b4886963bc75a7befd73bda36d27fd7102df8e9e66503b0e2a`, wrapper hash `8f5024481bedafdf7519290c72634822b66b79bc333afe65c9a7574f99c88311`, and host fingerprint `784aeb51ab5c4e52a12811d677b1ff4b8caf82706d5883facca1fe5dcc8de201`.
- The approval token was revoked after cleanup, and `python scripts/autonomy/controller.py check-remote-approval --run-id smeargate_bigramhash_mlp3x_warmprobe_20260321_runpod_pair --hardware-target "Runpod 1xH100 pod"` returned `remote_approval_ok=false`.

## Inferred Conclusions

- This direct warmed `1xH100` surrogate of the leaderboard SmearGate/BigramHash/MLP3x family is already comparable enough to reject in unchanged form.
- The dominant local failure mode is not just control-path drift; this recipe also carries too much artifact and final-eval cost for a clean `1xH100` surrogate comparison.
- Further paid iteration on this exact config is low value until a concrete confounder is removed.

## Files Changed

- Exact paths changed:
  - `C:\Users\g3n_i\Desktop\0. Coding\Projects\parameter-golf\challenge_ops\CURRENT_FRONTIER.md`
  - `C:\Users\g3n_i\Desktop\0. Coding\Projects\parameter-golf\challenge_ops\TRIED_IDEAS_INDEX.md`
  - `C:\Users\g3n_i\Desktop\0. Coding\Projects\parameter-golf\experiments\ledger.csv`
  - `C:\Users\g3n_i\Desktop\0. Coding\Projects\parameter-golf\experiments\runpod_runs.csv`
  - `C:\Users\g3n_i\Desktop\0. Coding\Projects\parameter-golf\experiments\runpod_sessions.csv`
  - `C:\Users\g3n_i\Desktop\0. Coding\Projects\parameter-golf\challenge_ops\results\2026-03-21_smeargate_bigramhash_mlp3x_warmprobe_20260321_run1_control.result.json`
  - `C:\Users\g3n_i\Desktop\0. Coding\Projects\parameter-golf\challenge_ops\results\2026-03-21_smeargate_bigramhash_mlp3x_warmprobe_20260321_run1_control.result.md`
  - `C:\Users\g3n_i\Desktop\0. Coding\Projects\parameter-golf\challenge_ops\results\2026-03-21_smeargate_bigramhash_mlp3x_warmprobe_20260321_run2_model.result.json`
  - `C:\Users\g3n_i\Desktop\0. Coding\Projects\parameter-golf\challenge_ops\results\2026-03-21_smeargate_bigramhash_mlp3x_warmprobe_20260321_run2_model.result.md`
  - `C:\Users\g3n_i\Desktop\0. Coding\Projects\parameter-golf\challenge_ops\results\2026-03-21_codex_handoff_smeargate_bigramhash_mlp3x_warmprobe.md`
  - `C:\Users\g3n_i\Desktop\0. Coding\Projects\parameter-golf\challenge_ops\approvals\smeargate_bigramhash_mlp3x_warmprobe_20260321_approval1.json`
  - `C:\Users\g3n_i\Desktop\0. Coding\Projects\parameter-golf\artifacts\runpod\smeargate_bigramhash_mlp3x_warmprobe_20260321.bundle`
  - `C:\Users\g3n_i\Desktop\0. Coding\Projects\parameter-golf\artifacts\runpod\smeargate_bigramhash_mlp3x_warmprobe_20260321\run1\run.log`
  - `C:\Users\g3n_i\Desktop\0. Coding\Projects\parameter-golf\artifacts\runpod\smeargate_bigramhash_mlp3x_warmprobe_20260321\run1\summary.json`
  - `C:\Users\g3n_i\Desktop\0. Coding\Projects\parameter-golf\artifacts\runpod\smeargate_bigramhash_mlp3x_warmprobe_20260321\run1\summary.txt`
  - `C:\Users\g3n_i\Desktop\0. Coding\Projects\parameter-golf\artifacts\runpod\smeargate_bigramhash_mlp3x_warmprobe_20260321\run1\provenance.json`
  - `C:\Users\g3n_i\Desktop\0. Coding\Projects\parameter-golf\artifacts\runpod\smeargate_bigramhash_mlp3x_warmprobe_20260321\run2\run.log`
  - `C:\Users\g3n_i\Desktop\0. Coding\Projects\parameter-golf\artifacts\runpod\smeargate_bigramhash_mlp3x_warmprobe_20260321\run2\summary.json`
  - `C:\Users\g3n_i\Desktop\0. Coding\Projects\parameter-golf\artifacts\runpod\smeargate_bigramhash_mlp3x_warmprobe_20260321\run2\summary.txt`
  - `C:\Users\g3n_i\Desktop\0. Coding\Projects\parameter-golf\artifacts\runpod\smeargate_bigramhash_mlp3x_warmprobe_20260321\run2\provenance.json`

## Commands Run

- Exact commands run:
  - `python scripts/autonomy/controller.py status`
  - `python scripts/autonomy/controller.py plan-experiment --experiment-id smeargate_bigramhash_mlp3x_warmprobe_20260321 --run-id smeargate_bigramhash_mlp3x_warmprobe_20260321_runpod_pair ... --dry-run`
  - `python scripts/autonomy/controller.py plan-experiment --experiment-id smeargate_bigramhash_mlp3x_warmprobe_20260321 --run-id smeargate_bigramhash_mlp3x_warmprobe_20260321_runpod_pair ...`
  - `python scripts/autonomy/controller.py grant-remote-approval --approval-id smeargate_bigramhash_mlp3x_warmprobe_20260321_approval1 --run-id smeargate_bigramhash_mlp3x_warmprobe_20260321_runpod_pair --hardware-target "Runpod 1xH100 pod" --max-paid-runs 1 --approved-by "Codex" --notes "One fresh official-template 1xH100 warmed surrogate probe for the SmearGate/BigramHash/MLP3x family."`
  - `python scripts/autonomy/controller.py check-remote-approval --run-id smeargate_bigramhash_mlp3x_warmprobe_20260321_runpod_pair --hardware-target "Runpod 1xH100 pod"`
  - `git bundle create artifacts/runpod/smeargate_bigramhash_mlp3x_warmprobe_20260321.bundle HEAD`
  - `runpodctl pod create --template-id y5cejece4j --gpu-id "NVIDIA H100 80GB HBM3" --name "parameter-golf-smeargate-warmprobe-20260321a" --container-disk-in-gb 20 --volume-in-gb 0 --data-center-ids US-MO-1 --cloud-type SECURE`
  - `python scripts/runpod/track_challenge_usage.py start-session --session-id h100_20260321_smeargate_probe_a --pod-id aagwbrm1z1rrej --usage-scope challenge --purpose "1xH100 Parameter Golf warmed surrogate probe for SmearGate BigramHash MLP3x" --funding-note "OpenAI Runpod credit allocation ($25, blended balance assumption)" --notes "approval_id=smeargate_bigramhash_mlp3x_warmprobe_20260321_approval1; run_id=smeargate_bigramhash_mlp3x_warmprobe_20260321_runpod_pair; idea=smeargate_bigramhash_mlp3x_muonwd_swa"`
  - `python scripts/runpod/check_pod_profile.py --pod-id aagwbrm1z1rrej --profile-json challenge_ops/runpod_1xh100_control_profile.json`
  - `runpodctl ssh info aagwbrm1z1rrej`
  - `python scripts/runpod/track_challenge_usage.py mark-ready --session-id h100_20260321_smeargate_probe_a`
  - `scp -P 18360 -i "C:\Users\g3n_i\.runpod\ssh\RunPod-Key-Go" "C:\Users\g3n_i\Desktop\0. Coding\Projects\parameter-golf\artifacts\runpod\smeargate_bigramhash_mlp3x_warmprobe_20260321.bundle" root@64.247.201.36:/workspace/smeargate_bigramhash_mlp3x_warmprobe_20260321.bundle`
  - `ssh -o StrictHostKeyChecking=no -o ConnectTimeout=15 -i "C:\Users\g3n_i\.runpod\ssh\RunPod-Key-Go" root@64.247.201.36 -p 18360 "bash -lc 'rm -rf /workspace/parameter-golf && git clone /workspace/smeargate_bigramhash_mlp3x_warmprobe_20260321.bundle /workspace/parameter-golf && cd /workspace/parameter-golf && git checkout -B main d1200c7c450a3da03dff0cdcf392b6340e645aaf'"`
  - `scp -P 18360 -i "C:\Users\g3n_i\.runpod\ssh\RunPod-Key-Go" train_gpt.py root@64.247.201.36:/workspace/baseline_train_gpt.py`
  - `scp -P 18360 -i "C:\Users\g3n_i\.runpod\ssh\RunPod-Key-Go" records/track_10min_16mb/2026-03-20_Int6_MLP3x_SmearGate_BigramHash_MuonWD_SWA/train_gpt.py root@64.247.201.36:/workspace/smear_train_gpt.py`
  - `scp -P 18360 -i "C:\Users\g3n_i\.runpod\ssh\RunPod-Key-Go" scripts/experiments/run_baseline_1gpu.sh scripts/experiments/parse_train_log.py scripts/experiments/write_run_provenance.py root@64.247.201.36:/workspace/parameter-golf/scripts/experiments/`
  - `ssh -o StrictHostKeyChecking=no -o ConnectTimeout=15 -i "C:\Users\g3n_i\.runpod\ssh\RunPod-Key-Go" root@64.247.201.36 -p 18360 "python3 - <<'PY'\nfrom pathlib import Path\nfor rel in [Path('/workspace/parameter-golf/scripts/experiments/run_baseline_1gpu.sh'), Path('/workspace/parameter-golf/scripts/experiments/parse_train_log.py'), Path('/workspace/parameter-golf/scripts/experiments/write_run_provenance.py'), Path('/workspace/baseline_train_gpt.py'), Path('/workspace/smear_train_gpt.py')]:\n    data = rel.read_bytes().replace(b'\\r\\n', b'\\n')\n    rel.write_bytes(data)\nPY\nchmod +x /workspace/parameter-golf/scripts/experiments/run_baseline_1gpu.sh && python3 -m py_compile /workspace/parameter-golf/scripts/experiments/parse_train_log.py /workspace/parameter-golf/scripts/experiments/write_run_provenance.py /workspace/baseline_train_gpt.py /workspace/smear_train_gpt.py"`
  - `python scripts/runpod/track_challenge_usage.py start-run --session-id h100_20260321_smeargate_probe_a --run-id smeargate_bigramhash_mlp3x_warmprobe_20260321_runpod_pair --experiment-id smeargate_bigramhash_mlp3x_warmprobe_20260321 --train-command "run1: baseline warm-up control via bash scripts/experiments/run_baseline_1gpu.sh; run2: record SmearGate/BigramHash/MLP3x probe via bash scripts/experiments/run_baseline_1gpu.sh after swapping in record train_gpt.py" --notes "fresh official-template H100 warmed surrogate probe of smeargate_bigramhash_mlp3x_muonwd_swa"`
  - `ssh -o StrictHostKeyChecking=no -o ConnectTimeout=15 -i "C:\Users\g3n_i\.runpod\ssh\RunPod-Key-Go" root@64.247.201.36 -p 18360 "cd /workspace/parameter-golf && python3 data/cached_challenge_fineweb.py --variant sp1024 --train-shards 80"`
  - `ssh -o StrictHostKeyChecking=no -o ConnectTimeout=15 -i "C:\Users\g3n_i\.runpod\ssh\RunPod-Key-Go" root@64.247.201.36 -p 18360 "bash -lc 'cp /workspace/baseline_train_gpt.py /workspace/parameter-golf/train_gpt.py && cd /workspace/parameter-golf && RUN_ID=smeargate_bigramhash_mlp3x_warmprobe_20260321_run1_control TARGET_GPU_LABEL=h100_sxm_warmup_control DATA_PATH=/workspace/parameter-golf/data/datasets/fineweb10B_sp1024 TOKENIZER_PATH=/workspace/parameter-golf/data/tokenizers/fineweb_1024_bpe.model VOCAB_SIZE=1024 VAL_LOSS_EVERY=200 MAX_WALLCLOCK_SECONDS=600 bash scripts/experiments/run_baseline_1gpu.sh'"`
  - `ssh -o StrictHostKeyChecking=no -o ConnectTimeout=15 -i "C:\Users\g3n_i\.runpod\ssh\RunPod-Key-Go" root@64.247.201.36 -p 18360 "bash -lc 'cp /workspace/smear_train_gpt.py /workspace/parameter-golf/train_gpt.py && cd /workspace/parameter-golf && RUN_ID=smeargate_bigramhash_mlp3x_warmprobe_20260321_run2_model TARGET_GPU_LABEL=h100_sxm_warm_model DATA_PATH=/workspace/parameter-golf/data/datasets/fineweb10B_sp1024 TOKENIZER_PATH=/workspace/parameter-golf/data/tokenizers/fineweb_1024_bpe.model VOCAB_SIZE=1024 NUM_LAYERS=9 MODEL_DIM=512 NUM_HEADS=8 NUM_KV_HEADS=4 MLP_MULT=3 TRAIN_SEQ_LEN=2048 TRAIN_BATCH_TOKENS=786432 MATRIX_LR=0.02 SCALAR_LR=0.02 TIED_EMBED_LR=0.03 MUON_MOMENTUM=0.99 MUON_MOMENTUM_WARMUP_START=0.92 MUON_MOMENTUM_WARMUP_STEPS=1500 WARMDOWN_ITERS=3000 GRAD_CLIP_NORM=0.3 BIGRAM_VOCAB_SIZE=4096 BIGRAM_DIM=128 EVAL_STRIDE=64 SWA_ENABLED=1 SWA_START_FRAC=0.5 SWA_EVERY=50 VAL_LOSS_EVERY=200 MAX_WALLCLOCK_SECONDS=600 bash scripts/experiments/run_baseline_1gpu.sh'"`
  - `scp -P 18360 -i "C:\Users\g3n_i\.runpod\ssh\RunPod-Key-Go" root@64.247.201.36:/workspace/parameter-golf/logs/experiments/baseline_1gpu/20260321_224611_smeargate_bigramhash_mlp3x_warmprobe_20260321_run1_control/run.log artifacts/runpod/smeargate_bigramhash_mlp3x_warmprobe_20260321/run1/`
  - `scp -P 18360 -i "C:\Users\g3n_i\.runpod\ssh\RunPod-Key-Go" root@64.247.201.36:/workspace/parameter-golf/logs/experiments/baseline_1gpu/20260321_225937_smeargate_bigramhash_mlp3x_warmprobe_20260321_run2_model/run.log artifacts/runpod/smeargate_bigramhash_mlp3x_warmprobe_20260321/run2/`
  - `python scripts/runpod/track_challenge_usage.py finish-run --run-id smeargate_bigramhash_mlp3x_warmprobe_20260321_runpod_pair`
  - `runpodctl pod stop aagwbrm1z1rrej`
  - `python scripts/runpod/track_challenge_usage.py finish-session --session-id h100_20260321_smeargate_probe_a`
  - `python scripts/autonomy/controller.py revoke-remote-approval --approval-id smeargate_bigramhash_mlp3x_warmprobe_20260321_approval1 --revoked-by "Codex" --notes "Warmed SmearGate BigramHash MLP3x surrogate probe completed; pod stopped."`
  - `python scripts/autonomy/controller.py record-result --log-path "C:\Users\g3n_i\Desktop\0. Coding\Projects\parameter-golf\artifacts\runpod\smeargate_bigramhash_mlp3x_warmprobe_20260321\run1\run.log" --run-id smeargate_bigramhash_mlp3x_warmprobe_20260321_run1_control ...`
  - `python scripts/autonomy/controller.py record-result --log-path "C:\Users\g3n_i\Desktop\0. Coding\Projects\parameter-golf\artifacts\runpod\smeargate_bigramhash_mlp3x_warmprobe_20260321\run2\run.log" --run-id smeargate_bigramhash_mlp3x_warmprobe_20260321_run2_model ...`
  - `python scripts/experiments/update_ledger.py --run-id smeargate_bigramhash_mlp3x_warmprobe_20260321_run2_model --summary-json "C:\Users\g3n_i\Desktop\0. Coding\Projects\parameter-golf\artifacts\runpod\smeargate_bigramhash_mlp3x_warmprobe_20260321\run2\summary.json" --notes "..."`

## Metrics Observed

- Exact metrics observed, with scope and source:
  - `smeargate_bigramhash_mlp3x_warmprobe_20260321_run1_control` from local copied `summary.json`:
    - `final_val_loss=2.27868765`
    - `final_val_bpb=1.34956718`
    - `stop_step=1131`
    - `last_logged_step_avg_ms=530.52`
    - `final_eval_time_ms=11118`
    - `total_submission_size_int8_zlib_bytes=12843418`
  - `smeargate_bigramhash_mlp3x_warmprobe_20260321_run2_model` from local copied `summary.json`:
    - `final_val_loss=2.52864608`
    - `final_val_bpb=1.49761060`
    - `stop_step=968`
    - `last_logged_step_avg_ms=620.04`
    - `final_eval_time_ms=1220523`
    - `total_submission_size_int8_zlib_bytes=16290010`
  - Same-pod deltas:
    - `delta_val_bpb=+0.14804342`
    - `delta_stop_step=-163`
    - `delta_final_eval_time_ms=+1209405`
    - `delta_counted_total_bytes=+3446592`
  - Runpod tracker rows:
    - `run_seconds=3180.000`
    - `billed_amount_usd=2.37616667`
    - `billed_time_ms=3180000`
    - `session_seconds=3406.000`
    - `non_training_seconds=226.000`
    - `session_billed_amount_usd=2.54503889`
    - `session_billed_time_ms=3406000`

## challenge_ops Updates

- `CURRENT_FRONTIER.md`: updated to mark the direct warmed `1xH100` SmearGate/BigramHash/MLP3x probe as a confirmed negative surrogate and to remove it as the default next paid repeat in unchanged form.
- `TRIED_IDEAS_INDEX.md`: updated the SmearGate/BigramHash/MLP3x family row with the negative warmed `1xH100-surrogate` result and over-cap artifact note while preserving the positive `8xH100-leaderboard` verdict.
- `TERMINOLOGY_CROSSWALK.md`: no change.
- `SUBMISSION_AUDIT.md`: no change.

## Risks And Next Actions

- Remaining risks:
  - `1xH100-surrogate` control drift still exists, even though warm-state ordering is now enforced.
  - The direct SmearGate/BigramHash/MLP3x port is not a trustworthy cheap proxy for leaderboard potential on `1xH100`.
  - `controller.py record-result` currently exits nonzero on over-cap runs even when the intent is to preserve a negative surrogate result; the result files still wrote successfully, but the ledger needed a follow-up repair via `update_ledger.py`.
- Recommended next step:
  - Do not rerun this exact config unchanged. Move to a simpler warmed-second-run surrogate with lower eval-time and artifact-risk, starting with the `FP16 Embed + WD3600` family or another lower-friction leaderboard-informed variant.
