# Codex Handoff

## Task

- Request summary: use Runpod to execute the next control-path steps, verify the results, iterate until the control answer is clear, and shut the pod down at the end.
- Scope: Runpod `1xH100` control-only rebuilds on the same pod if possible, with strict preflight and provenance capture; no new model ablations unless control recovered near the provisional legacy anchor.
- Constraint summary: same pod if restartable, pinned repo state, strict dataset/tokenizer invariance checks, result packets, local audit updates, and explicit pod shutdown.

## Outcome

- Status: completed.
- What changed: restarted reused stable-profile pod `474jlphqpo5n8x`, rebuilt the repo checkout, overlaid the provenance-hardened control scripts, ran three control-only provenance-hardened reruns (`a`, `b`, `c`), synced artifacts locally, generated result packets, updated local ledgers and active memory, and stopped the pod.
- What did not change: no surrogate ablation was run, no training code was modified, and the provisional legacy compare target was not promoted to a replacement anchor.

## Confirmed Findings

- Pod reuse worked on `474jlphqpo5n8x`; the pod matched `challenge_ops/runpod_1xh100_control_profile.json` again (`US-MO-1`, `26` vCPUs, `1x NVIDIA H100 80GB HBM3`, `20 GB` container disk, `0 GB` volume).
- `/workspace/parameter-golf` was only a template stub on resume, so the repo had to be recloned before any dataset or training step.
- The remote base checkout was pinned to `c59338a1920870c1648faf90c29416f15ebf63bf`, then overlaid only with:
  - `scripts/experiments/run_baseline_1gpu.sh`
  - `scripts/experiments/run_1xh100_ablation.sh`
  - `scripts/experiments/write_run_provenance.py`
  - `scripts/experiments/generate_experiment_result.py`
  - `experiments/baselines/runpod_1xh100_control_anchor_summary.json`
- All three rebuilt control runs recorded the same provenance-critical hashes:
  - `train_gpt.py sha256=15846ddcd260753dbd7023522e1e12a6d0dec0dd5cb5e5a69446b6407a3b7bd5`
  - `dataset manifest sha256=c0ebc88d5ac10324c8dc29c9c27041ec0efdc6441f9be747901c4f7f45f59ae9`
  - `tokenizer sha256=4f5e8adb109c66b4886963bc75a7befd73bda36d27fd7102df8e9e66503b0e2a`
  - `compare_json sha256=aa400747841436b3190d0cd239957f7ad8fd14a93232639f7f9a55a786959d99`
  - wrapper hashes from `provenance.json`: `run_baseline_1gpu.sh=8f502448...`, `run_1xh100_ablation.sh=e9f8f0a6...`
- Control metrics on the same reused pod were:
  - `ablate_control_1xh100_20260321_runpod_frozen_anchor_a`: `val_bpb=1.32963305`, `val_loss=2.24502970`, `stop_step=1365`, `bytes_total=13549048`
  - `ablate_control_1xh100_20260321_runpod_frozen_anchor_b`: `val_bpb=1.32776835`, `val_loss=2.24188124`, `stop_step=1387`, `bytes_total=13687204`
  - `ablate_control_1xh100_20260321_runpod_frozen_anchor_c`: `val_bpb=1.33473550`, `val_loss=2.25364497`, `stop_step=1293`, `bytes_total=13772166`
- The best rebuilt rerun `b` still missed the provisional legacy anchor `ablate_control_1xh100_1024` by `+0.00619328 val_bpb`; the legacy recovery gate was `+0.00500000`.
- No surrogate ablation was run.
- Pod cleanup action was `stopped`; `runpodctl pod get 474jlphqpo5n8x --include-network-volume` confirmed `desiredStatus=EXITED`.

## Inferred Conclusions

- The provenance surface is now much stronger than before, but the control path is still not stable enough for surrogate ablations because same-pod same-overlay reruns still drifted across `1.32776835` to `1.33473550`.
- The best rebuilt rerun is useful as the strongest provenance-hardened control datapoint so far, but it is not yet strong enough to replace the provisional legacy anchor as a promotion decision.
- More paid GPU time should stay focused on control-path diagnosis, not architecture or parameter ablations.

## Files Changed

- Exact paths changed:
- `challenge_ops/CURRENT_FRONTIER.md`
- `challenge_ops/SUBMISSION_AUDIT.md`
- `challenge_ops/TRIED_IDEAS_INDEX.md`
- `challenge_ops/results/2026-03-21_ablate_control_1xh100_20260321_runpod_frozen_anchor_a.result.json`
- `challenge_ops/results/2026-03-21_ablate_control_1xh100_20260321_runpod_frozen_anchor_a.result.md`
- `challenge_ops/results/2026-03-21_ablate_control_1xh100_20260321_runpod_frozen_anchor_b.result.json`
- `challenge_ops/results/2026-03-21_ablate_control_1xh100_20260321_runpod_frozen_anchor_b.result.md`
- `challenge_ops/results/2026-03-21_ablate_control_1xh100_20260321_runpod_frozen_anchor_c.result.json`
- `challenge_ops/results/2026-03-21_ablate_control_1xh100_20260321_runpod_frozen_anchor_c.result.md`
- `experiments/ledger.csv`
- `experiments/runpod_runs.csv`
- `experiments/runpod_sessions.csv`

## Commands Run

- Exact commands run:
- `runpodctl pod list --all`
- `runpodctl template get y5cejece4j`
- `runpodctl user`
- `python scripts/runpod/track_challenge_usage.py start-session --session-id h100_20260320_control_rebuild_reuse_474_a --pod-id 474jlphqpo5n8x --purpose "1xH100 Parameter Golf frozen-control rebuild reuse attempt on stable-profile pod"`
- `runpodctl pod start 474jlphqpo5n8x`
- `runpodctl pod get 474jlphqpo5n8x --include-machine --include-network-volume`
- `runpodctl ssh info 474jlphqpo5n8x`
- `python scripts/runpod/track_challenge_usage.py mark-ready --session-id h100_20260320_control_rebuild_reuse_474_a`
- `ssh ... root@64.247.201.40 -p 19869 "echo connected && hostname && pwd && ls /workspace"`
- `ssh ... root@64.247.201.40 -p 19869 "rm -rf /workspace/parameter-golf && git clone https://github.com/g3n-inferno/parameter-golf.git /workspace/parameter-golf && cd /workspace/parameter-golf && git checkout --detach c59338a1920870c1648faf90c29416f15ebf63bf && git rev-parse HEAD"`
- `scp ... run_baseline_1gpu.sh run_1xh100_ablation.sh write_run_provenance.py generate_experiment_result.py ...`
- `scp ... experiments/baselines/runpod_1xh100_control_anchor_summary.json ...`
- `python scripts/runpod/check_pod_profile.py --pod-id 474jlphqpo5n8x --profile-json challenge_ops/runpod_1xh100_control_profile.json --json-out logs/runpod/474jlphqpo5n8x_control_rebuild_profile_check.json`
- `ssh ... root@64.247.201.40 -p 19869 "cd /workspace/parameter-golf && bash scripts/runpod/verify_pod_env.sh && git rev-parse HEAD && git status --short && df -h /workspace"`
- `ssh ... root@64.247.201.40 -p 19869 "cd /workspace/parameter-golf && bash scripts/runpod/download_sp1024.sh"`
- `python scripts/runpod/track_challenge_usage.py start-run --session-id h100_20260320_control_rebuild_reuse_474_a --run-id ablate_control_1xh100_20260321_runpod_frozen_anchor_a --experiment-id control_runpod_1xh100_20260321_frozen_anchor_rebuild --train-command "RUN_ID=ablate_control_1xh100_20260321_runpod_frozen_anchor_a TARGET_GPU_LABEL=h100_sxm_reuse474_frozen bash scripts/experiments/run_1xh100_ablation.sh control"`
- `ssh ... root@64.247.201.40 -p 19869 "cd /workspace/parameter-golf && RUN_ID=ablate_control_1xh100_20260321_runpod_frozen_anchor_a TARGET_GPU_LABEL=h100_sxm_reuse474_frozen bash scripts/experiments/run_1xh100_ablation.sh control"`
- `python scripts/runpod/track_challenge_usage.py start-run --session-id h100_20260320_control_rebuild_reuse_474_a --run-id ablate_control_1xh100_20260321_runpod_frozen_anchor_b --experiment-id control_runpod_1xh100_20260321_frozen_anchor_confirm --train-command "RUN_ID=ablate_control_1xh100_20260321_runpod_frozen_anchor_b TARGET_GPU_LABEL=h100_sxm_reuse474_frozen bash scripts/experiments/run_1xh100_ablation.sh control"`
- `ssh ... root@64.247.201.40 -p 19869 "cd /workspace/parameter-golf && RUN_ID=ablate_control_1xh100_20260321_runpod_frozen_anchor_b TARGET_GPU_LABEL=h100_sxm_reuse474_frozen bash scripts/experiments/run_1xh100_ablation.sh control"`
- `python scripts/runpod/track_challenge_usage.py start-run --session-id h100_20260320_control_rebuild_reuse_474_a --run-id ablate_control_1xh100_20260321_runpod_frozen_anchor_c --experiment-id control_runpod_1xh100_20260321_frozen_anchor_confirm2 --train-command "RUN_ID=ablate_control_1xh100_20260321_runpod_frozen_anchor_c TARGET_GPU_LABEL=h100_sxm_reuse474_frozen bash scripts/experiments/run_1xh100_ablation.sh control"`
- `ssh ... root@64.247.201.40 -p 19869 "cd /workspace/parameter-golf && RUN_ID=ablate_control_1xh100_20260321_runpod_frozen_anchor_c TARGET_GPU_LABEL=h100_sxm_reuse474_frozen bash scripts/experiments/run_1xh100_ablation.sh control"`
- `scp -r ... /workspace/parameter-golf/logs/experiments/next_1xh100_workstream/control/20260321_001938_ablate_control_1xh100_20260321_runpod_frozen_anchor_a ...`
- `scp -r ... /workspace/parameter-golf/logs/experiments/next_1xh100_workstream/control/20260321_003337_ablate_control_1xh100_20260321_runpod_frozen_anchor_b ...`
- `scp -r ... /workspace/parameter-golf/logs/experiments/next_1xh100_workstream/control/20260321_004653_ablate_control_1xh100_20260321_runpod_frozen_anchor_c ...`
- `python scripts/runpod/track_challenge_usage.py finish-run --run-id ablate_control_1xh100_20260321_runpod_frozen_anchor_a`
- `python scripts/runpod/track_challenge_usage.py finish-run --run-id ablate_control_1xh100_20260321_runpod_frozen_anchor_b`
- `python scripts/runpod/track_challenge_usage.py finish-run --run-id ablate_control_1xh100_20260321_runpod_frozen_anchor_c`
- `python scripts/experiments/generate_experiment_result.py ... --metadata-json .../provenance.json ... --json-out challenge_ops/results/2026-03-21_ablate_control_1xh100_20260321_runpod_frozen_anchor_*.result.json --md-out ...`
- `python scripts/experiments/new_experiment.py ... --run-id ablate_control_1xh100_20260321_runpod_frozen_anchor_* ... --force`
- `python scripts/experiments/update_ledger.py --run-id ablate_control_1xh100_20260321_runpod_frozen_anchor_* --summary-json challenge_ops/results/...`
- `runpodctl pod stop 474jlphqpo5n8x`
- `runpodctl pod get 474jlphqpo5n8x --include-network-volume`
- `python scripts/runpod/track_challenge_usage.py finish-session --session-id h100_20260320_control_rebuild_reuse_474_a`
- `python scripts/runpod/track_challenge_usage.py refresh-billing --usage-scope challenge`
- `python scripts/runpod/track_challenge_usage.py report --usage-scope challenge`

## Metrics Observed

- Exact metrics observed, with scope and source:
- `ablate_control_1xh100_20260321_runpod_frozen_anchor_a` on `1xH100-surrogate`: `val_loss=2.24502970`, `val_bpb=1.32963305`, `stop_step=1365`, `bytes_total=13549048`, `delta_val_bpb_vs_legacy=+0.00805798`.
- `ablate_control_1xh100_20260321_runpod_frozen_anchor_b` on `1xH100-surrogate`: `val_loss=2.24188124`, `val_bpb=1.32776835`, `stop_step=1387`, `bytes_total=13687204`, `delta_val_bpb_vs_legacy=+0.00619328`.
- `ablate_control_1xh100_20260321_runpod_frozen_anchor_c` on `1xH100-surrogate`: `val_loss=2.25364497`, `val_bpb=1.33473550`, `stop_step=1293`, `bytes_total=13772166`, `delta_val_bpb_vs_legacy=+0.01316043`.
- Runpod challenge usage report after refresh: `total_session_cost_usd=6.34962322`, `total_run_cost_usd=6.28603811`, `assumed_challenge_credit_remaining_usd=18.65037678`.

## challenge_ops Updates

- `CURRENT_FRONTIER.md`: updated with the three provenance-hardened same-pod control rebuilds and the no-go ablation recommendation.
- `TRIED_IDEAS_INDEX.md`: updated the `Control 1xH100` row so the best rebuilt rerun is the representative run, but not a promoted replacement anchor.
- `TERMINOLOGY_CROSSWALK.md`: no terminology change required in this turn.
- `SUBMISSION_AUDIT.md`: updated latest gating evidence to the A/B/C rebuilt-control family and the continued no-go decision.

## Risks And Next Actions

- Remaining risks: same-pod same-overlay control variance still spans about `0.00697 val_bpb`; the provisional legacy anchor remains provenance-weak; the rebuilt control family is closer but still not repeatedly within the provisional-legacy `+0.005` gate.
- Recommended next step: do not run a surrogate ablation yet. If more GPU time is spent, use it only for another control-path diagnosis step, ideally one that isolates why the same reused pod still drifts despite identical recorded hashes.
