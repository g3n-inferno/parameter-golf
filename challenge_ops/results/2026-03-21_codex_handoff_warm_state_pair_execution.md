# Codex Handoff

## Task

- Request summary: execute the prepared paired same-pod warm-state `1xH100` control test using the stored training command.
- Scope: one bounded paid `1xH100` Runpod run on a fresh official-template pod, with local approval-token gating, result capture, and repo-memory updates.
- Constraint summary: one pod only, unchanged dataset/tokenizer, no `8xH100`, no submission packaging, and stop the pod plus revoke the token at the end.

## Outcome

- Status: completed.
- What changed: the paired warm-state test ran to completion, both run result packets were recorded locally, the paired summary was preserved, and `challenge_ops` memory was updated.
- What did not change: no model architecture or dataset/tokenizer change, no submission candidate packaging, and no second approval token or second pod.

## Confirmed Findings

- Fresh official-template pod `v16rndtmqt47dq` matched the declared `US-MO-1` / `26`-vCPU `1xH100` control profile and used template `y5cejece4j`.
- The official template again came up with a stubbed `/workspace/parameter-golf` directory and no `.git`, so the checkout had to be rebuilt before training.
- `control_path_warm_state_pair_20260321_run1` finished at `val_bpb=1.33964300`, `val_loss=2.26193109`, `stop_step=1258`, `step_avg_ms=477.20`, and `total_submission_size_int8_zlib_bytes=13344164`.
- `control_path_warm_state_pair_20260321_run2` finished at `val_bpb=1.33753867`, `val_loss=2.25837801`, `stop_step=1283`, `step_avg_ms=467.83`, and `total_submission_size_int8_zlib_bytes=13302509`.
- The paired summary showed `delta_val_bpb=-0.00210433`, `delta_stop_step=+25`, `delta_step_avg_ms=-9.37`, and matching recorded code/dataset/tokenizer/host fingerprints across the two runs.
- The pod was stopped, the local runpod session was finished, and the approval token was revoked successfully.

## Inferred Conclusions

- Warm-state effects are real on the current `1xH100-surrogate` path, because the second run improved the first on the same pod under the same recorded surface.
- Warm state is not the full explanation for the earlier `1.3278-1.3347` rebuilt same-pod range, because the warmed second run still stopped at `1.33753867`.
- Future `1xH100-surrogate` model experiments should use the warmed same-pod second-run protocol and preserve host fingerprints explicitly.

## Files Changed

- Exact paths changed:
- `challenge_ops/CURRENT_FRONTIER.md`
- `challenge_ops/TRIED_IDEAS_INDEX.md`
- `challenge_ops/approvals/control_path_warm_state_pair_20260321_approval1.json`
- `experiments/ledger.csv`
- `experiments/runpod_runs.csv`
- `experiments/runpod_sessions.csv`
- `artifacts/runpod/control_path_warm_state_pair_20260321/`
- `challenge_ops/results/2026-03-21_control_path_warm_state_pair_20260321_run1.result.json`
- `challenge_ops/results/2026-03-21_control_path_warm_state_pair_20260321_run1.result.md`
- `challenge_ops/results/2026-03-21_control_path_warm_state_pair_20260321_run2.result.json`
- `challenge_ops/results/2026-03-21_control_path_warm_state_pair_20260321_run2.result.md`
- `challenge_ops/results/2026-03-21_control_path_warm_state_pair_20260321_pair_summary.json`
- `challenge_ops/results/2026-03-21_control_path_warm_state_pair_20260321_pair_summary.md`
- `challenge_ops/results/2026-03-21_codex_handoff_warm_state_pair_execution.md`

## Commands Run

- Exact commands run:
- `python scripts/autonomy/controller.py plan-experiment ... --dry-run`
- `python scripts/autonomy/controller.py grant-remote-approval --approval-id control_path_warm_state_pair_20260321_approval1 ...`
- `python scripts/autonomy/controller.py check-remote-approval --run-id control_path_warm_state_pair_20260321_runpod_pair --hardware-target 'Runpod 1xH100 pod'`
- `git bundle create artifacts/runpod/control_path_warm_state_pair_20260321.bundle HEAD`
- `runpodctl pod create --template-id y5cejece4j --gpu-id 'NVIDIA H100 80GB HBM3' --name 'parameter-golf-control-h100-warmpair-20260321a' --container-disk-in-gb 20 --volume-in-gb 0 --data-center-ids US-MO-1 --cloud-type SECURE`
- `python scripts/runpod/track_challenge_usage.py start-session --session-id h100_20260321_warm_state_pair_a --pod-id v16rndtmqt47dq ...`
- `python scripts/runpod/check_pod_profile.py --pod-id v16rndtmqt47dq --profile-json challenge_ops/runpod_1xh100_control_profile.json`
- `runpodctl ssh info v16rndtmqt47dq`
- `python scripts/runpod/track_challenge_usage.py mark-ready --session-id h100_20260321_warm_state_pair_a`
- `scp ... artifacts/runpod/control_path_warm_state_pair_20260321.bundle root@64.247.201.48:/workspace/control_path_warm_state_pair_20260321.bundle`
- `ssh ... 'rm -rf /workspace/parameter-golf && git clone /workspace/control_path_warm_state_pair_20260321.bundle /workspace/parameter-golf && git checkout -B main ...'`
- `ssh ... 'cd /workspace/parameter-golf && python3 data/cached_challenge_fineweb.py --variant sp1024 --train-shards 80'`
- `python scripts/runpod/track_challenge_usage.py start-run --session-id h100_20260321_warm_state_pair_a --run-id control_path_warm_state_pair_20260321_runpod_pair ...`
- `ssh ... 'cd /workspace/parameter-golf && PAIR_ID=control_path_warm_state_pair_20260321 RUN1_ID=control_path_warm_state_pair_20260321_run1 RUN2_ID=control_path_warm_state_pair_20260321_run2 VAL_LOSS_EVERY=200 MAX_WALLCLOCK_SECONDS=600 bash scripts/experiments/run_warm_state_control_pair.sh'`
- `python scripts/runpod/track_challenge_usage.py finish-run --run-id control_path_warm_state_pair_20260321_runpod_pair`
- `runpodctl pod stop v16rndtmqt47dq`
- `python scripts/runpod/track_challenge_usage.py finish-session --session-id h100_20260321_warm_state_pair_a`
- `python scripts/autonomy/controller.py revoke-remote-approval --approval-id control_path_warm_state_pair_20260321_approval1 ...`
- `python scripts/autonomy/controller.py record-result ... --run-id control_path_warm_state_pair_20260321_run1`
- `python scripts/autonomy/controller.py record-result ... --run-id control_path_warm_state_pair_20260321_run2`

## Metrics Observed

- Exact metrics observed, with scope and source:
- `control_path_warm_state_pair_20260321_run1`: `val_bpb=1.33964300`, `val_loss=2.26193109`, `stop_step=1258`, `step_avg_ms=477.20`, `total_submission_size_int8_zlib_bytes=13344164`
- `control_path_warm_state_pair_20260321_run2`: `val_bpb=1.33753867`, `val_loss=2.25837801`, `stop_step=1283`, `step_avg_ms=467.83`, `total_submission_size_int8_zlib_bytes=13302509`
- Pair deltas: `delta_val_bpb=-0.00210433`, `delta_stop_step=+25`, `delta_step_avg_ms=-9.37`
- Runpod session `h100_20260321_warm_state_pair_a`: `init_seconds=43.000`, `session_seconds=2300.000`, `non_training_seconds=730.000`, `billed_amount_usd=1.71861111`, `billed_time_ms=2300000`
- Runpod run `control_path_warm_state_pair_20260321_runpod_pair`: `run_seconds=1570.000`, `billed_amount_usd=1.17313889`, `billed_time_ms=1570000`

## challenge_ops Updates

- `CURRENT_FRONTIER.md`: updated to record the paired same-host warm-state evidence and to shift future surrogate work to a warmed second-run protocol.
- `TRIED_IDEAS_INDEX.md`: updated the `Control 1xH100` row with the paired-run evidence and the revised control-path interpretation.
- `TERMINOLOGY_CROSSWALK.md`: no change.
- `SUBMISSION_AUDIT.md`: no change.

## Risks And Next Actions

- Remaining risks: the official zero-volume template lost the remote run directory after a post-run restart, so the local `run.log` files were reconstructed from captured SSH stdout before result-packet generation.
- Recommended next step: move to one bounded warmed-second-run surrogate model probe rather than another pure control rerun, and preserve the same-pod ordering explicitly in that next brief.

