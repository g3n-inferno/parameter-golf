# Codex Handoff

Use this structure for nontrivial Codex tasks.
Keep it concise, factual, and reproducible.

## Task

- Request summary: fix the misleading `local` wording around the active `1xH100` control anchor, run one pinned-commit fresh-pod Runpod `1xH100` control-path stabilization rerun, collect the result packet, update project memory only if warranted, and explicitly stop or terminate the pod afterward.
- Scope: terminology cleanup, one control-only Runpod rerun, result-packet generation, evidence-based memory updates, and explicit pod shutdown.
- Constraint summary: keep diffs minimal and reversible, preserve stable legacy IDs where possible, do not broaden into new ablations or trainer tuning, require strict preflight checks, and do not leave the pod billing after artifacts are synced.

## Outcome

- Status: completed.
- What changed: adopted `Runpod 1xH100 control anchor` as the canonical human-facing term, added a canonical compare JSON for the adopted control anchor, executed `ablate_control_1xh100_20260320_runpod_stabilize` on a fresh Runpod H100 pod at `main@bc75d7b0c350a41af25131232854833340265e86`, generated the markdown and JSON result packet, updated local ledger plus warranted `challenge_ops` memory files, and explicitly stopped the pod.
- What did not change: no trainer logic, tokenizer behavior, dataset behavior, accepted `records/` folders, or submission packaging state.

## Confirmed Findings

- The legacy `_local_` identifiers in `baseline_sp1024_h100_local_20260319` and `experiments/baselines/local_1xh100_baseline_summary.json` refer to Runpod `1xH100` evidence, not a true local-machine GPU run.
- Fresh pod `vlmy3ngmeqbq96` was created from the official template `y5cejece4j` on `NVIDIA H100 80GB HBM3` with `volumeInGb=0`.
- The remote repo at `/workspace/parameter-golf` was pinned to `bc75d7b0c350a41af25131232854833340265e86`.
- Preflight confirmed `fineweb10B_sp1024`, `80` train shards, `1` validation shard, and tokenizer `/workspace/parameter-golf/data/tokenizers/fineweb_1024_bpe.model`.
- The exact control command was `RUN_ID=ablate_control_1xh100_20260320_runpod_stabilize TARGET_GPU_LABEL=h100_sxm bash scripts/experiments/run_1xh100_ablation.sh control`.
- The run finished with `final_int8_zlib_roundtrip_exact val_loss=2.27686994 val_bpb=1.34849063`, `stop_step=1152`, `final_eval_time_ms=11152`, and `total_submission_size_int8_zlib_bytes=12940257`.
- Relative to the adopted control anchor `ablate_control_1xh100_1024`, delta `val_bpb` was `+0.02691556`.
- Pod `vlmy3ngmeqbq96` was explicitly stopped and confirmed `desiredStatus=EXITED` before session closure.

## Inferred Conclusions

- The Runpod `1xH100` control path is not stable enough to resume paid `1xH100-surrogate` ablations.
- The dominant confounder remains workflow variance on the remote control path rather than an idea-specific miss in `lr_warmdown`.

## Files Changed

- Exact paths changed:
- `challenge_ops/CURRENT_FRONTIER.md`
- `challenge_ops/SUBMISSION_AUDIT.md`
- `challenge_ops/TERMINOLOGY_CROSSWALK.md`
- `challenge_ops/TRIED_IDEAS_INDEX.md`
- `challenge_ops/briefs/2026-03-20_control_runpod_1xh100_stabilization.md`
- `challenge_ops/results/2026-03-20_ablate_control_1xh100_20260320_runpod_stabilize.result.json`
- `challenge_ops/results/2026-03-20_ablate_control_1xh100_20260320_runpod_stabilize.result.md`
- `docs/experiments/next_1xh100_ablations.md`
- `experiments/README.md`
- `experiments/baselines/local_1xh100_baseline_summary.json`
- `experiments/baselines/runpod_1xh100_control_anchor_summary.json`
- `experiments/ledger.csv`
- `experiments/runpod_runs.csv`
- `experiments/runpod_sessions.csv`
- `scripts/experiments/run_1xh100_ablation.sh`

## Commands Run

- Exact commands run:
- `git rev-parse HEAD`
- `runpodctl template get y5cejece4j`
- `runpodctl gpu list --include-unavailable`
- `runpodctl pod create --template-id y5cejece4j --gpu-id "NVIDIA H100 80GB HBM3" --name "parameter-golf-control-h100-sxm-stabilize"`
- `python scripts/runpod/track_challenge_usage.py start-session --session-id h100_20260320_control_stabilize_a --pod-id vlmy3ngmeqbq96 --purpose "1xH100 Parameter Golf control-path stabilization rerun"`
- `runpodctl pod get vlmy3ngmeqbq96 --include-machine --include-network-volume`
- `runpodctl ssh info vlmy3ngmeqbq96`
- `ssh -o StrictHostKeyChecking=accept-new -o ConnectTimeout=15 -i C:\Users\g3n_i\.runpod\ssh\RunPod-Key-Go root@87.120.211.211 -p 18746 "echo connected && hostname && pwd"`
- `python scripts/runpod/track_challenge_usage.py mark-ready --session-id h100_20260320_control_stabilize_a`
- remote setup and pin: clone/update `/workspace/parameter-golf`, set origin to `https://github.com/g3n-inferno/parameter-golf.git`, fetch, and `git checkout --detach bc75d7b0c350a41af25131232854833340265e86`
- `ssh -i C:\Users\g3n_i\.runpod\ssh\RunPod-Key-Go root@87.120.211.211 -p 18746 "bash -lc 'cd /workspace/parameter-golf && bash scripts/runpod/verify_pod_env.sh'"`
- `ssh -i C:\Users\g3n_i\.runpod\ssh\RunPod-Key-Go root@87.120.211.211 -p 18746 "bash -lc 'df -h /workspace && du -sh /workspace || true'"`
- `ssh -i C:\Users\g3n_i\.runpod\ssh\RunPod-Key-Go root@87.120.211.211 -p 18746 "bash -lc 'cd /workspace/parameter-golf && bash scripts/runpod/download_sp1024.sh'"`
- `python scripts/runpod/track_challenge_usage.py start-run --session-id h100_20260320_control_stabilize_a --run-id ablate_control_1xh100_20260320_runpod_stabilize --experiment-id control_runpod_1xh100_20260320_stabilization --train-command "RUN_ID=ablate_control_1xh100_20260320_runpod_stabilize TARGET_GPU_LABEL=h100_sxm bash scripts/experiments/run_1xh100_ablation.sh control"`
- `ssh -i C:\Users\g3n_i\.runpod\ssh\RunPod-Key-Go root@87.120.211.211 -p 18746 "bash -lc 'cd /workspace/parameter-golf && RUN_ID=ablate_control_1xh100_20260320_runpod_stabilize TARGET_GPU_LABEL=h100_sxm bash scripts/experiments/run_1xh100_ablation.sh control'"`
- `scp -r -i C:\Users\g3n_i\.runpod\ssh\RunPod-Key-Go -P 18746 root@87.120.211.211:/workspace/parameter-golf/logs/experiments/next_1xh100_workstream/control/20260320_200015_ablate_control_1xh100_20260320_runpod_stabilize .\logs\experiments\next_1xh100_workstream\control\`
- `python scripts/runpod/track_challenge_usage.py finish-run --run-id ablate_control_1xh100_20260320_runpod_stabilize`
- `python scripts/experiments/generate_experiment_result.py ... --compare-json experiments/baselines/runpod_1xh100_control_anchor_summary.json ...`
- `runpodctl pod stop vlmy3ngmeqbq96`
- `runpodctl pod get vlmy3ngmeqbq96 --include-network-volume`
- `python scripts/runpod/track_challenge_usage.py finish-session --session-id h100_20260320_control_stabilize_a`
- `python scripts/runpod/track_challenge_usage.py report --usage-scope challenge`

## Metrics Observed

- Exact metrics observed, with scope and source:
- `ablate_control_1xh100_20260320_runpod_stabilize` on `1xH100-surrogate`: `final_int8_zlib_roundtrip_exact val_loss=2.27686994 val_bpb=1.34849063`, `stop_step=1152`, `final_eval_time_ms=11152`, `total_submission_size_int8_zlib_bytes=12940257`, source `logs/experiments/next_1xh100_workstream/control/20260320_200015_ablate_control_1xh100_20260320_runpod_stabilize/run.log`
- Delta vs adopted `Runpod 1xH100 control anchor` (`ablate_control_1xh100_1024`): `delta_val_loss=+0.04544579`, `delta_val_bpb=+0.02691556`, `delta_bytes_total=-1064307`, `delta_stop_step=-354`
- Delta vs prior clean Runpod control retry `ablate_control_1xh100_20260320_runpod_retry2`: `delta_val_bpb=+0.01330835`
- Delta vs remote `lr_warmdown` rerun `ablate_lr_warmdown_1xh100_20260320_runpod`: `delta_val_bpb=+0.01790341`

## challenge_ops Updates

- `CURRENT_FRONTIER.md`: updated terminology, canonical anchor wording, and the new no-go evidence from `ablate_control_1xh100_20260320_runpod_stabilize`
- `TRIED_IDEAS_INDEX.md`: updated the `Control 1xH100` row to include the new stabilization rerun regression
- `TERMINOLOGY_CROSSWALK.md`: updated to standardize `Runpod 1xH100 control anchor` and separate historical `_local_` aliases from true local runs
- `SUBMISSION_AUDIT.md`: updated latest gating evidence to the new stabilization rerun regression

## Risks And Next Actions

- Remaining risks: the exact root cause of the Runpod control variance is still unknown; the wrapper comparison on remote pinned commit still referenced the older historical summary until local canonical compare files were updated; Runpod billing export still reports `0` in local audit tables.
- Recommended next step: do not resume paid `1xH100-surrogate` ablations; instead run a low-cost root-cause audit of the Runpod control path using the adopted `Runpod 1xH100 control anchor` as the only comparison target.
