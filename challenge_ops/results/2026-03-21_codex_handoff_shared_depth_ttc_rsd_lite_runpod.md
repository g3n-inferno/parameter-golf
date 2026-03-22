# Codex Handoff

## Task

- Request summary: implement a minimal, reversible training-only recurrent self-distillation experiment on top of the existing shared-depth path, verify the default path stays unchanged, add a named `1xH100` ablation entry, run it on Runpod, and report exact commands, env vars, metrics, and risks.
- Scope: repo-local `train_gpt.py` plus the `run_1xh100_ablation.sh` wrapper, one fresh official-template `1xH100` Runpod pod after two failed reuse attempts, one same-pod shared-depth control, one same-pod TTC run, result capture, and challenge-memory updates.
- Constraint summary: unchanged dataset/tokenizer, env-gated default-off behavior, no export-format or artifact-accounting changes, no `8xH100`, one pod only, tracked Runpod usage, and a written dry-run brief because `controller.py plan-experiment` is currently broken for unseen ideas.

## Outcome

- Status: completed.
- What changed: added default-off TTC env parsing and training logic to [`train_gpt.py`](C:\Users\g3n_i\Desktop\0. Coding\Projects\parameter-golf\train_gpt.py), added the `shared_depth_ttc_rsd_lite` wrapper entry in [`scripts/experiments/run_1xh100_ablation.sh`](C:\Users\g3n_i\Desktop\0. Coding\Projects\parameter-golf\scripts\experiments\run_1xh100_ablation.sh), ran a fresh same-pod shared-depth control and TTC retry on Runpod, generated result packets, updated the local ledgers, and updated [`challenge_ops/CURRENT_FRONTIER.md`](C:\Users\g3n_i\Desktop\0. Coding\Projects\parameter-golf\challenge_ops\CURRENT_FRONTIER.md) plus [`challenge_ops/TRIED_IDEAS_INDEX.md`](C:\Users\g3n_i\Desktop\0. Coding\Projects\parameter-golf\challenge_ops\TRIED_IDEAS_INDEX.md).
- What did not change: dataset export, tokenizer, accepted record folders, submission packaging, or the exported student model path.

## Confirmed Findings

- Default-off TTC behavior is preserved by construction: `TTC_DISTILL_MODE` defaults to `off`, and the train loop only enters the teacher/KL path when that mode is enabled.
- The same-pod shared-depth control `ablate_shared_depth_stable_1xh100_retry1` completed on fresh official-template pod `mf8286d28a4gdi` at `final_int8_zlib_roundtrip_exact val_bpb=1.41961582`, `stop_step=1409`, `step_avg_ms=426.03`, and `total_int8_zlib_bytes=4941086`.
- The first TTC launch `ablate_shared_depth_ttc_rsd_lite_1xh100` failed immediately because the `11`-pass teacher used more decoder skip positions than the `9`-pass student had skip weights for.
- A minimal guard that only applies weighted skips when `i < self.skip_weights.size(0)` fixed that teacher-only crash without changing the student export path.
- The TTC retry `ablate_shared_depth_ttc_rsd_lite_1xh100_retry1` completed on the same pod at `final_int8_zlib_roundtrip_exact val_bpb=1.43462137`, `stop_step=1085`, `step_avg_ms=553.35`, `final_eval_time_ms=11151`, and `total_int8_zlib_bytes=4568999`.
- Relative to the same-pod shared-depth control, the TTC retry regressed by `+0.01500555` `val_bpb`, lost `324` steps, increased logged `step_avg_ms` by `127.32` (`+29.89%`), and reduced counted artifact bytes by `372087`.
- The TTC logs showed `distill_cadence:4`, `distill_lambda` warming to `0.050000`, and `teacher_time_share` stabilizing near `0.143`.
- Runpod reuse-first policy was followed: restart attempts on `v16rndtmqt47dq` and `vhrzxwizzi276z` both failed with host GPU exhaustion before a fresh template pod was created.
- Session `shared_depth_ttc_rsd_lite_runpod_20260321_session3` on pod `mf8286d28a4gdi` ran for `2076` seconds with estimated billed cost `1.55123333` USD; the successful control and TTC retries accounted for `813` seconds (`0.60749167` USD) and `750` seconds (`0.56041667` USD) respectively.

## Inferred Conclusions

- On the current `1xH100-surrogate` path, this TTC-RSD-lite configuration spends meaningful train-time compute but does not recover the resulting throughput loss in validation quality.
- The negative same-pod pair is more trustworthy than earlier cross-pod comparisons because both runs used the same fresh pod, dataset cache, and patched code state.
- The shared-depth family still has ample artifact headroom, but this particular recurrent-logit teacher schedule is not a good next paid repeat in unchanged form.

## Files Changed

- Exact paths changed:
  - `C:\Users\g3n_i\Desktop\0. Coding\Projects\parameter-golf\train_gpt.py`
  - `C:\Users\g3n_i\Desktop\0. Coding\Projects\parameter-golf\scripts\experiments\run_1xh100_ablation.sh`
  - `C:\Users\g3n_i\Desktop\0. Coding\Projects\parameter-golf\challenge_ops\briefs\2026-03-21_shared_depth_ttc_rsd_lite_runpod_20260321.md`
  - `C:\Users\g3n_i\Desktop\0. Coding\Projects\parameter-golf\challenge_ops\CURRENT_FRONTIER.md`
  - `C:\Users\g3n_i\Desktop\0. Coding\Projects\parameter-golf\challenge_ops\TRIED_IDEAS_INDEX.md`
  - `C:\Users\g3n_i\Desktop\0. Coding\Projects\parameter-golf\experiments\ledger.csv`
  - `C:\Users\g3n_i\Desktop\0. Coding\Projects\parameter-golf\experiments\runpod_runs.csv`
  - `C:\Users\g3n_i\Desktop\0. Coding\Projects\parameter-golf\experiments\runpod_sessions.csv`
  - `C:\Users\g3n_i\Desktop\0. Coding\Projects\parameter-golf\challenge_ops\results\2026-03-21_ablate_shared_depth_stable_1xh100_retry1.result.json`
  - `C:\Users\g3n_i\Desktop\0. Coding\Projects\parameter-golf\challenge_ops\results\2026-03-21_ablate_shared_depth_stable_1xh100_retry1.result.md`
  - `C:\Users\g3n_i\Desktop\0. Coding\Projects\parameter-golf\challenge_ops\results\2026-03-21_ablate_shared_depth_ttc_rsd_lite_1xh100_retry1.result.json`
  - `C:\Users\g3n_i\Desktop\0. Coding\Projects\parameter-golf\challenge_ops\results\2026-03-21_ablate_shared_depth_ttc_rsd_lite_1xh100_retry1.result.md`
  - `C:\Users\g3n_i\Desktop\0. Coding\Projects\parameter-golf\challenge_ops\results\2026-03-21_codex_handoff_shared_depth_ttc_rsd_lite_runpod.md`

## Commands Run

- Exact commands run:
  - `python scripts/autonomy/controller.py status`
  - `python scripts/autonomy/controller.py check-remote-approval --approval-id shared_depth_residual_experts_runpod_20260321_approval1 --hardware-target "Runpod 1xH100 pod"`
  - `runpodctl pod start v16rndtmqt47dq`
  - `runpodctl pod start vhrzxwizzi276z`
  - `runpodctl template get y5cejece4j`
  - `runpodctl pod create --template-id y5cejece4j --gpu-id "NVIDIA H100 80GB HBM3" --gpu-count 1 --container-disk-in-gb 20 --volume-in-gb 0 --data-center-ids US-MO-1 --name "parameter-golf-shared-depth-ttc-20260321b"`
  - `python scripts/runpod/track_challenge_usage.py start-session --session-id shared_depth_ttc_rsd_lite_runpod_20260321_session3 --pod-id mf8286d28a4gdi --usage-scope challenge --purpose "1xH100 Parameter Golf TTC-RSD-lite shared-depth ablation" --funding-note "OpenAI Runpod credit allocation ($25, blended balance assumption)" --notes "..."`
  - `python scripts/runpod/track_challenge_usage.py mark-ready --session-id shared_depth_ttc_rsd_lite_runpod_20260321_session3`
  - `ssh -i C:\Users\g3n_i\.runpod\ssh\RunPod-Key-Go root@64.247.201.32 -p 10049 "rm -rf /workspace/parameter-golf && cd /workspace && git clone https://github.com/g3n-inferno/parameter-golf.git && cd parameter-golf && git remote add upstream https://github.com/openai/parameter-golf.git && git fetch origin --prune && git fetch upstream --prune && git checkout main && git rev-parse HEAD"`
  - `scp -P 10049 -i C:\Users\g3n_i\.runpod\ssh\RunPod-Key-Go train_gpt.py root@64.247.201.32:/workspace/parameter-golf/train_gpt.py`
  - `scp -P 10049 -i C:\Users\g3n_i\.runpod\ssh\RunPod-Key-Go scripts\experiments\run_1xh100_ablation.sh root@64.247.201.32:/workspace/parameter-golf/scripts/experiments/run_1xh100_ablation.sh`
  - `ssh -i C:\Users\g3n_i\.runpod\ssh\RunPod-Key-Go root@64.247.201.32 -p 10049 "cd /workspace/parameter-golf && bash scripts/runpod/verify_pod_env.sh && python3 -m py_compile train_gpt.py"`
  - `ssh -i C:\Users\g3n_i\.runpod\ssh\RunPod-Key-Go root@64.247.201.32 -p 10049 "cd /workspace/parameter-golf && python3 data/cached_challenge_fineweb.py --variant sp1024 --train-shards 80"`
  - `python scripts/runpod/track_challenge_usage.py start-run --session-id shared_depth_ttc_rsd_lite_runpod_20260321_session3 --run-id ablate_shared_depth_stable_1xh100_retry1 --experiment-id shared_depth_ttc_rsd_lite_runpod_20260321_control --train-command "RUN_ID=ablate_shared_depth_stable_1xh100_retry1 ... bash scripts/experiments/run_1xh100_ablation.sh shared_depth_stable" --notes "retry after LF normalization on remote wrapper"`
  - `ssh -i C:\Users\g3n_i\.runpod\ssh\RunPod-Key-Go root@64.247.201.32 -p 10049 "cd /workspace/parameter-golf && RUN_ID=ablate_shared_depth_stable_1xh100_retry1 ... bash scripts/experiments/run_1xh100_ablation.sh shared_depth_stable"`
  - `python scripts/runpod/track_challenge_usage.py start-run --session-id shared_depth_ttc_rsd_lite_runpod_20260321_session3 --run-id ablate_shared_depth_ttc_rsd_lite_1xh100_retry1 --experiment-id shared_depth_ttc_rsd_lite_runpod_20260321 --train-command "RUN_ID=ablate_shared_depth_ttc_rsd_lite_1xh100_retry1 ... bash scripts/experiments/run_1xh100_ablation.sh shared_depth_ttc_rsd_lite" --notes "retry after teacher skip-weight overrun fix"`
  - `ssh -i C:\Users\g3n_i\.runpod\ssh\RunPod-Key-Go root@64.247.201.32 -p 10049 "cd /workspace/parameter-golf && RUN_ID=ablate_shared_depth_ttc_rsd_lite_1xh100_retry1 ... bash scripts/experiments/run_1xh100_ablation.sh shared_depth_ttc_rsd_lite"`
  - `scp -r -P 10049 -i C:\Users\g3n_i\.runpod\ssh\RunPod-Key-Go root@64.247.201.32:/workspace/parameter-golf/logs/experiments/next_1xh100_workstream/shared_depth_stable/20260322_010500_ablate_shared_depth_stable_1xh100_retry1 logs/experiments/next_1xh100_workstream/shared_depth_stable/`
  - `scp -r -P 10049 -i C:\Users\g3n_i\.runpod\ssh\RunPod-Key-Go root@64.247.201.32:/workspace/parameter-golf/logs/experiments/next_1xh100_workstream/shared_depth_ttc_rsd_lite/20260322_012046_ablate_shared_depth_ttc_rsd_lite_1xh100_retry1 logs/experiments/next_1xh100_workstream/shared_depth_ttc_rsd_lite/`
  - `runpodctl pod stop mf8286d28a4gdi`
  - `python scripts/runpod/track_challenge_usage.py finish-session --session-id shared_depth_ttc_rsd_lite_runpod_20260321_session3`
  - `python scripts/autonomy/controller.py record-result --log-path logs/experiments/next_1xh100_workstream/shared_depth_stable/20260322_010500_ablate_shared_depth_stable_1xh100_retry1/run.log --run-id ablate_shared_depth_stable_1xh100_retry1 ...`
  - `python scripts/experiments/new_experiment.py --run-id ablate_shared_depth_ttc_rsd_lite_1xh100_retry1 --date 2026-03-21 --dataset-variant fineweb10B_sp1024 --tokenizer-variant fineweb_1024_bpe.model --core-hparams "seq1024 shared_depth cyclic unique3 passes9 resid_scale=inv_sqrt_reuse ttc_rsd teacher11 every4 lambda0.05 warmup100" --hardware "Runpod 1xH100 pod" --track-intent non-record --code-path train_gpt.py --wallclock-target 600s --notes "Fresh same-pod TTC recurrent self-distillation retry after teacher skip-weight overrun fix." --force`
  - `python scripts/experiments/update_ledger.py --run-id ablate_shared_depth_ttc_rsd_lite_1xh100_retry1 --summary-json challenge_ops/results/2026-03-21_ablate_shared_depth_ttc_rsd_lite_1xh100_retry1.result.json --date 2026-03-21 --dataset-variant fineweb10B_sp1024 --tokenizer-variant fineweb_1024_bpe.model --core-hparams "seq1024 shared_depth cyclic unique3 passes9 resid_scale=inv_sqrt_reuse ttc_rsd teacher11 every4 lambda0.05 warmup100" --hardware "Runpod 1xH100 pod" --track-intent non-record --code-path train_gpt.py --wallclock-target 600s --notes "Fresh same-pod TTC recurrent self-distillation retry after teacher skip-weight overrun fix."`

## Metrics Observed

- Exact metrics observed, with scope and source:
  - `ablate_shared_depth_stable_1xh100_retry1` from local copied `summary.json`:
    - `final_val_loss=2.39696185`
    - `final_val_bpb=1.41961582`
    - `stop_step=1409`
    - `last_logged_step_avg_ms=426.03`
    - `final_eval_time_ms=11155`
    - `total_submission_size_int8_zlib_bytes=4941086`
  - `ablate_shared_depth_ttc_rsd_lite_1xh100_retry1` from local copied `summary.json`:
    - `final_val_loss=2.42229808`
    - `final_val_bpb=1.43462137`
    - `stop_step=1085`
    - `last_logged_step_avg_ms=553.35`
    - `final_eval_time_ms=11151`
    - `total_submission_size_int8_zlib_bytes=4568999`
  - Same-pod control vs TTC deltas:
    - `delta_val_bpb=+0.01500555`
    - `delta_stop_step=-324`
    - `delta_step_avg_ms=+127.32`
    - `delta_step_avg_pct=+29.89%`
    - `delta_counted_total_bytes=-372087`
  - Runpod tracker rows:
    - `shared_depth_ttc_rsd_lite_runpod_20260321_session3 session_seconds=2076.000 billed_amount_usd=1.55123333 non_training_seconds=408.000`
    - `ablate_shared_depth_stable_1xh100_retry1 run_seconds=813.000 billed_amount_usd=0.60749167`
    - `ablate_shared_depth_ttc_rsd_lite_1xh100_retry1 run_seconds=750.000 billed_amount_usd=0.56041667`

## challenge_ops Updates

- `CURRENT_FRONTIER.md`: updated with the fresh same-pod shared-depth control/TTC pair and the new negative TTC evidence.
- `TRIED_IDEAS_INDEX.md`: added `Shared-Depth Stable` and `Shared-Depth TTC-RSD-lite` as already-tried negative `1xH100-surrogate` ideas.
- `TERMINOLOGY_CROSSWALK.md`: no change.
- `SUBMISSION_AUDIT.md`: no change.

## Risks And Next Actions

- Remaining risks:
  - `controller.py plan-experiment` still crashes on unseen ideas because it eagerly formats the missing `existing_idea` message; this task used a written brief instead of patching that unrelated bug.
  - The first TTC failure mode was structural, not statistical; other teacher-pass schedules may expose additional shared-depth edge cases.
  - The Runpod tracker rows for these sessions used an estimated-duration billing fallback, and the funding-note string in the CSV lost `$25` because PowerShell interpolated it away in the command literal.
- Recommended next step:
  - Do not repeat this TTC-RSD-lite config unchanged. If shared-depth train-time compute is revisited, reduce cadence or teacher passes first, and only after deciding whether the shared-depth student family itself is worth further paid surrogate time relative to simpler baseline-style families.
