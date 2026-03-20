# Codex Handoff

Use this structure for nontrivial Codex tasks.
Keep it concise, factual, and reproducible.

## Task

- Request summary: stabilize the Runpod `1xH100` control-anchor workflow, prefer reuse of the same stopped pod when possible, fix the local Runpod credit tracker, rerun control on a profile-matched pod, run at most one surrogate ablation only if control recovered near `ablate_control_1xh100_1024`, and shut the pod down at the end.
- Scope: Runpod workflow hardening, tracker repair, one stable-profile control rerun, conditional ablation gate, artifact sync, memory updates, and explicit pod shutdown.
- Constraint summary: use Runpod tooling, preserve legality and provenance, keep the control family naming stable, and do not spend GPU time on an ablation if the control gate fails.

## Outcome

- Status: completed.
- What changed: added a declared stable Runpod control-profile policy plus a local profile checker, repaired the Runpod tracker with billing refresh/fallback support, attempted stopped-pod reuse first, ran one stable-profile control rerun on a fresh US `26`-vCPU H100 pod when reuse was unavailable, skipped the surrogate ablation because control failed the recovery gate, and explicitly stopped the pod.
- What did not change: no trainer logic, tokenizer behavior, dataset behavior, or accepted `records/` folders changed; no surrogate ablation was run.

## Confirmed Findings

- Stopped-pod reuse attempts on `9p5aq98sa8j6go`, `xgi77lp1vapny8`, and `zzp4jchfuh2ky3` all failed with Runpod host-placement errors.
- Fresh pod `474jlphqpo5n8x` matched the declared stable profile in [runpod_1xh100_control_profile.json](C:/Users/g3n_i/Desktop/0.%20Coding/Projects/parameter-golf/challenge_ops/runpod_1xh100_control_profile.json): `US-MO-1`, `26` vCPUs, `NVIDIA H100 80GB HBM3`, `runpod/parameter-golf:latest`, `20GB` container disk, and `0GB` volume.
- The remote repo was pinned to `bc75d7b0c350a41af25131232854833340265e86`.
- Preflight confirmed `80` train shards, `1` validation shard, and tokenizer `fineweb_1024_bpe.model`.
- The exact control command was `RUN_ID=ablate_control_1xh100_20260320_runpod_stable TARGET_GPU_LABEL=h100_sxm_stable bash scripts/experiments/run_1xh100_ablation.sh control`.
- `ablate_control_1xh100_20260320_runpod_stable` finished at `final_int8_zlib_roundtrip_exact val_loss=2.28415990 val_bpb=1.35280815`, `stop_step=1145`, `final_eval_time_ms=11165`, `total_submission_size_int8_zlib_bytes=12497284`.
- Relative to `ablate_control_1xh100_1024`, delta `val_bpb` was `+0.03123308`.
- The declared recovery gate was `val_bpb <= 1.32657507`, so no surrogate ablation was run.
- Pod `474jlphqpo5n8x` was explicitly stopped and confirmed `desiredStatus=EXITED`.
- The tracker refresh populated nonzero billing totals; current challenge report shows `total_session_cost_usd=4.29192029`, `total_run_cost_usd=2.62691077`, and `assumed_challenge_credit_remaining_usd=20.70807971`.

## Inferred Conclusions

- Matching the pod to the stable US `26`-vCPU control profile did not recover the `Runpod 1xH100 control anchor`, so the earlier control miss is not explained solely by the `EUR-NO-2` / `8`-vCPU host.
- Paid `1xH100-surrogate` ablations should remain paused until the adopted control anchor itself has a grounded reproducibility explanation.

## Files Changed

- Exact paths changed:
- `challenge_ops/CURRENT_FRONTIER.md`
- `challenge_ops/SUBMISSION_AUDIT.md`
- `challenge_ops/TRIED_IDEAS_INDEX.md`
- `challenge_ops/briefs/2026-03-20_control_runpod_1xh100_stable_profile.md`
- `challenge_ops/results/2026-03-20_ablate_control_1xh100_20260320_runpod_stable.result.json`
- `challenge_ops/results/2026-03-20_ablate_control_1xh100_20260320_runpod_stable.result.md`
- `challenge_ops/runpod_1xh100_control_profile.json`
- `experiments/README.md`
- `experiments/ledger.csv`
- `experiments/runpod_runs.csv`
- `experiments/runpod_sessions.csv`
- `scripts/experiments/run_baseline_1gpu.sh`
- `scripts/runpod/check_pod_profile.py`
- `scripts/runpod/track_challenge_usage.py`

## Commands Run

- Exact commands run:
- `python scripts/runpod/check_pod_profile.py --pod-id 9p5aq98sa8j6go --profile-json challenge_ops/runpod_1xh100_control_profile.json`
- `python scripts/runpod/check_pod_profile.py --pod-id vlmy3ngmeqbq96 --profile-json challenge_ops/runpod_1xh100_control_profile.json`
- `python scripts/runpod/track_challenge_usage.py refresh-billing --usage-scope challenge`
- `python scripts/runpod/track_challenge_usage.py start-session --session-id h100_20260320_control_reuse_9p5_a --pod-id 9p5aq98sa8j6go --purpose "1xH100 Parameter Golf control-path reuse attempt on stable control-profile pod"`
- `runpodctl pod start 9p5aq98sa8j6go`
- `python scripts/runpod/track_challenge_usage.py finish-session --session-id h100_20260320_control_reuse_9p5_a`
- `python scripts/runpod/track_challenge_usage.py start-session --session-id h100_20260320_control_reuse_xgi_a --pod-id xgi77lp1vapny8 --purpose "1xH100 Parameter Golf control-path reuse attempt on stable control-profile pod"`
- `runpodctl pod start xgi77lp1vapny8`
- `python scripts/runpod/track_challenge_usage.py finish-session --session-id h100_20260320_control_reuse_xgi_a`
- `python scripts/runpod/track_challenge_usage.py start-session --session-id h100_20260320_control_reuse_zzp4_a --pod-id zzp4jchfuh2ky3 --purpose "1xH100 Parameter Golf control-path reuse attempt on stable control-profile pod"`
- `runpodctl pod start zzp4jchfuh2ky3`
- `python scripts/runpod/track_challenge_usage.py finish-session --session-id h100_20260320_control_reuse_zzp4_a`
- `runpodctl pod create --template-id y5cejece4j --gpu-id "NVIDIA H100 80GB HBM3" --data-center-ids US-MO-1 --name "parameter-golf-control-h100-sxm-stable-usmo"`
- `python scripts/runpod/track_challenge_usage.py start-session --session-id h100_20260320_control_stable_a --pod-id 474jlphqpo5n8x --purpose "1xH100 Parameter Golf stable-profile control rerun"`
- `python scripts/runpod/check_pod_profile.py --pod-id 474jlphqpo5n8x --profile-json challenge_ops/runpod_1xh100_control_profile.json --json-out logs/runpod/474jlphqpo5n8x_control_profile_check.json`
- `runpodctl ssh info 474jlphqpo5n8x`
- `python scripts/runpod/track_challenge_usage.py mark-ready --session-id h100_20260320_control_stable_a`
- remote repo setup via SSH: clone/update fork, set remotes, fetch, `git checkout --detach bc75d7b0c350a41af25131232854833340265e86`
- remote verify and dataset export via SSH: `bash scripts/runpod/verify_pod_env.sh`, `bash scripts/runpod/download_sp1024.sh`
- `python scripts/runpod/track_challenge_usage.py start-run --session-id h100_20260320_control_stable_a --run-id ablate_control_1xh100_20260320_runpod_stable --experiment-id control_runpod_1xh100_20260320_stable_profile --train-command "RUN_ID=ablate_control_1xh100_20260320_runpod_stable TARGET_GPU_LABEL=h100_sxm_stable bash scripts/experiments/run_1xh100_ablation.sh control"`
- remote control run via SSH: `RUN_ID=ablate_control_1xh100_20260320_runpod_stable TARGET_GPU_LABEL=h100_sxm_stable bash scripts/experiments/run_1xh100_ablation.sh control`
- `scp -r ...:/workspace/parameter-golf/logs/experiments/next_1xh100_workstream/control/20260320_214306_ablate_control_1xh100_20260320_runpod_stable .\logs\experiments\next_1xh100_workstream\control\`
- `python scripts/runpod/track_challenge_usage.py finish-run --run-id ablate_control_1xh100_20260320_runpod_stable`
- `runpodctl pod stop 474jlphqpo5n8x`
- `runpodctl pod get 474jlphqpo5n8x --include-network-volume`
- `python scripts/runpod/track_challenge_usage.py finish-session --session-id h100_20260320_control_stable_a`
- `python scripts/runpod/track_challenge_usage.py refresh-billing --session-id h100_20260320_control_stable_a`
- `python scripts/runpod/track_challenge_usage.py report --usage-scope challenge`
- `python scripts/experiments/generate_experiment_result.py ... --compare-json experiments/baselines/runpod_1xh100_control_anchor_summary.json ...`

## Metrics Observed

- Exact metrics observed, with scope and source:
- `ablate_control_1xh100_20260320_runpod_stable` on `1xH100-surrogate`: `val_loss=2.28415990`, `val_bpb=1.35280815`, `stop_step=1145`, `eval_time_ms=11165`, `total_submission_size_int8_zlib_bytes=12497284`
- Delta vs adopted control anchor `ablate_control_1xh100_1024`: `delta_val_loss=+0.05273575`, `delta_val_bpb=+0.03123308`, `delta_bytes_total=-1507280`
- Delta vs previous stable-profile-excluded rerun `ablate_control_1xh100_20260320_runpod_stabilize`: `delta_val_bpb=+0.00431752`
- Billing report after refresh: `total_session_cost_usd=4.29192029`, `total_run_cost_usd=2.62691077`, `assumed_challenge_credit_remaining_usd=20.70807971`

## challenge_ops Updates

- `CURRENT_FRONTIER.md`: updated with the stable-profile rerun and the stronger conclusion that host-profile matching alone did not recover the anchor
- `TRIED_IDEAS_INDEX.md`: updated the control-family row to include the stable-profile rerun miss
- `TERMINOLOGY_CROSSWALK.md`: unchanged in this pass; phase-1 terminology cleanup already held
- `SUBMISSION_AUDIT.md`: updated latest gating evidence to the stable-profile rerun miss

## Risks And Next Actions

- Remaining risks: the adopted control anchor `ablate_control_1xh100_1024` still lacks a preserved raw result packet/log in repo-local memory; some very short failed reuse-attempt sessions still use estimated billing rather than API billing; no root cause has been isolated yet.
- Recommended next step: do not run another paid surrogate ablation. Audit provenance for `ablate_control_1xh100_1024` and compare environment/run differences against the repeated failed control reruns before spending more H100 time.
