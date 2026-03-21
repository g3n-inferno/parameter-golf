# Codex Handoff

## Task

- Request summary: audit the Runpod `1xH100` control anchor with priority on commit pinning, wrapper-path pinning, compare-JSON provenance, dataset/tokenizer invariance, and same-family byte drift; fix issues along the way and verify the fixes locally.
- Scope: provenance and workflow hardening only; no new paid Runpod run and no surrogate ablation.
- Constraint summary: keep diffs minimal and reversible, preserve historical IDs, distinguish confirmed findings from inference, and do not resume `1xH100-surrogate` ablations unless control provenance is frozen again.

## Outcome

- Status: completed.
- What changed: demoted `ablate_control_1xh100_1024` to a provisional legacy control anchor in active memory and compare JSON; added `scripts/experiments/write_run_provenance.py`; updated the baseline/ablation wrappers to emit provenance manifests and to block non-control ablations when the compare target requires a rebuilt anchor; extended `generate_experiment_result.py` to carry compare-target provenance and auto-load sibling `provenance.json`; refreshed the latest stable result packet and wrote a dedicated provenance audit note.
- What did not change: no new remote control rerun, no new surrogate ablation, no core training logic change in `train_gpt.py`, and no historical run IDs were renamed.

## Confirmed Findings

- `ablate_control_1xh100_1024` is only preserved locally through `experiments/ledger.csv` and the canonical compare file `experiments/baselines/runpod_1xh100_control_anchor_summary.json`; no raw local log or result packet for that run exists under `logs/` or `challenge_ops/results/`.
- The anchor first appears in git history at `ac7e33ddcb84253c3ed713668785c3b598c8259b` with `code_bytes=48294`; later clean Runpod reruns used larger export families with `code_bytes=61795`.
- The later reruns preserved the same declared dataset path, tokenizer path, shard count, hyperparameter family, and `RUN_ID ... bash scripts/experiments/run_1xh100_ablation.sh control` wrapper path in their logs.
- Same-family byte drift is dominated by `model_int8_zlib_bytes`, not code alone: `13956270` on `ablate_control_1xh100_1024`, then `13611740`, `12878462`, and `12435489` across later clean reruns.
- The new provenance manifest path records git commit, wrapper hashes, code hash, dataset manifest hash, tokenizer hash, and compare-JSON lineage in `provenance.json`.
- The non-control ablation guard now blocks when the compare JSON has `requires_rebuild_before_ablation=true`.

## Inferred Conclusions

- The current canonical compare target is too weak to serve as a frozen control anchor because its provenance is ledger-mirrored and partially inferred.
- Host variability mattered, but it is not sufficient to explain the control failure; commit/export drift and missing anchor provenance are also material.
- The next valid step is to rebuild one new frozen Runpod `1xH100` control anchor under the hardened provenance workflow before any more `1xH100-surrogate` ablations.

## Files Changed

- Exact paths changed:
- `challenge_ops/CURRENT_FRONTIER.md`
- `challenge_ops/SUBMISSION_AUDIT.md`
- `challenge_ops/TERMINOLOGY_CROSSWALK.md`
- `challenge_ops/TRIED_IDEAS_INDEX.md`
- `challenge_ops/results/2026-03-20_ablate_control_1xh100_20260320_runpod_stable.result.json`
- `challenge_ops/results/2026-03-20_ablate_control_1xh100_20260320_runpod_stable.result.md`
- `challenge_ops/results/2026-03-20_runpod_1xh100_control_anchor_provenance_audit.md`
- `experiments/README.md`
- `experiments/baselines/local_1xh100_baseline_summary.json`
- `experiments/baselines/runpod_1xh100_control_anchor_summary.json`
- `experiments/ledger.csv`
- `scripts/experiments/generate_experiment_result.py`
- `scripts/experiments/run_1xh100_ablation.sh`
- `scripts/experiments/run_baseline_1gpu.sh`
- `scripts/experiments/write_run_provenance.py`

## Commands Run

- Exact commands run:
- `Get-Content challenge_ops\\CURRENT_FRONTIER.md`
- `Get-Content challenge_ops\\SUBMISSION_AUDIT.md`
- `Get-Content challenge_ops\\TRIED_IDEAS_INDEX.md`
- `Get-Content experiments\\ledger.csv`
- `Get-Content experiments\\baselines\\runpod_1xh100_control_anchor_summary.json`
- `Get-Content experiments\\baselines\\local_1xh100_baseline_summary.json`
- `Get-Content challenge_ops\\results\\2026-03-20_ablate_control_1xh100_20260320_runpod_stable.result.json`
- `Get-Content challenge_ops\\results\\2026-03-20_ablate_control_1xh100_20260320_runpod_stabilize.result.json`
- `Get-Content scripts\\experiments\\run_1xh100_ablation.sh`
- `Get-Content scripts\\experiments\\run_baseline_1gpu.sh`
- `Get-Content scripts\\experiments\\generate_experiment_result.py`
- `Get-Content scripts\\experiments\\parse_train_log.py`
- `Get-Content scripts\\experiments\\update_ledger.py`
- `Get-Content scripts\\experiments\\new_experiment.py`
- `Get-Content scripts\\runpod\\verify_pod_env.sh`
- `git log --oneline --decorate -n 20`
- `git log --since="2026-03-19" --until="2026-03-20 23:59" --stat -- train_gpt.py scripts/experiments/run_baseline_1gpu.sh scripts/experiments/run_1xh100_ablation.sh scripts/experiments/parse_train_log.py scripts/experiments/generate_experiment_result.py experiments/baselines challenge_ops`
- `git show ac7e33d:experiments/ledger.csv`
- `git show e26784b:experiments/ledger.csv`
- `git show ac7e33d:experiments/baselines/local_1xh100_baseline_summary.json`
- `git diff ac7e33d..bc75d7b -- train_gpt.py`
- `Get-Content logs\\experiments\\next_1xh100_workstream\\control\\20260320_183925_ablate_control_1xh100_20260320_runpod_retry2\\run.log -TotalCount 120`
- `Get-Content logs\\experiments\\next_1xh100_workstream\\control\\20260320_200015_ablate_control_1xh100_20260320_runpod_stabilize\\run.log -TotalCount 120`
- `Get-Content logs\\experiments\\next_1xh100_workstream\\control\\20260320_214306_ablate_control_1xh100_20260320_runpod_stable\\run.log -TotalCount 120`
- `python -m py_compile scripts\\experiments\\write_run_provenance.py scripts\\experiments\\generate_experiment_result.py scripts\\experiments\\update_ledger.py scripts\\experiments\\parse_train_log.py scripts\\runpod\\track_challenge_usage.py`
- `python scripts\\experiments\\write_run_provenance.py --output logs\\tmp\\provenance_smoke\\provenance.json --repo-dir . --run-dir logs\\tmp\\provenance_smoke --log-file logs\\tmp\\provenance_smoke\\run.log --run-id provenance_smoke --code-path train_gpt.py --wrapper-path scripts\\experiments\\run_baseline_1gpu.sh --wrapper-path scripts\\experiments\\run_1xh100_ablation.sh --exact-command "env RUN_ID=provenance_smoke torchrun --standalone --nproc_per_node=1 train_gpt.py" --target-gpu-label smoke --hardware "Runpod 1xH100 pod" --dataset-variant fineweb10B_sp1024 --dataset-path logs\\tmp\\provenance_smoke\\dataset --expected-train-shards 2 --tokenizer-variant fineweb_1024_bpe.model --tokenizer-path README.md --core-hparams "seq1024 smoke" --track-intent non-record --wallclock-target 600s --compare-json experiments\\baselines\\runpod_1xh100_control_anchor_summary.json --compare-label runpod_1xh100_control_anchor`
- `python scripts\\experiments\\generate_experiment_result.py logs\\tmp\\provenance_smoke\\run.log --run-id provenance_smoke --compare-json experiments\\baselines\\runpod_1xh100_control_anchor_summary.json --compare-label runpod_1xh100_control_anchor --json-out logs\\tmp\\provenance_smoke\\result.json --md-out logs\\tmp\\provenance_smoke\\result.md --require-final-metrics`
- `python scripts\\experiments\\generate_experiment_result.py logs\\experiments\\next_1xh100_workstream\\control\\20260320_214306_ablate_control_1xh100_20260320_runpod_stable\\run.log --run-id ablate_control_1xh100_20260320_runpod_stable --experiment-id control_runpod_1xh100_20260320_stable_profile --idea-label "Control 1xH100" --standardized-name runpod_1xh100_control_anchor --date 2026-03-20 --branch main --commit-sha bc75d7b0c350a41af25131232854833340265e86 --track-intent non-record --scope 1xH100-surrogate --lineage variant --state already-tried --result negative --status completed --code-path train_gpt.py --dataset-variant fineweb10B_sp1024 --tokenizer-variant fineweb_1024_bpe.model --hardware "1xH100 Runpod NVIDIA H100 80GB HBM3" --wallclock-target 600s --core-hparams "seq1024 9x512 kv4 mlp_mult2 tied_emb baseline_schedule" --exact-command "RUN_ID=ablate_control_1xh100_20260320_runpod_stable TARGET_GPU_LABEL=h100_sxm_stable bash scripts/experiments/run_1xh100_ablation.sh control" --notes "Stable-profile control rerun on fresh pod 474jlphqpo5n8x after failed restart attempts on 9p5aq98sa8j6go, xgi77lp1vapny8, and zzp4jchfuh2ky3. Pod matched challenge_ops/runpod_1xh100_control_profile.json, and no surrogate ablation was run because the control gate failed." --compare-json experiments\\baselines\\runpod_1xh100_control_anchor_summary.json --compare-label runpod_1xh100_control_anchor --artifact-cap 16000000 --confirmed-finding "Restart attempts on previously stopped matching pods 9p5aq98sa8j6go, xgi77lp1vapny8, and zzp4jchfuh2ky3 all failed with 'There are not enough free GPUs on the host machine to start this pod.', so reuse was unavailable." --confirmed-finding "Fresh pod 474jlphqpo5n8x was created with template y5cejece4j in US-MO-1 and passed challenge_ops/runpod_1xh100_control_profile.json: H100, 1 GPU, runpod/parameter-golf:latest, 20GB container disk, 0GB volume, secure cloud, US location, and 26 vCPUs." --confirmed-finding "The remote checkout was pinned to bc75d7b0c350a41af25131232854833340265e86, and preflight confirmed /workspace/parameter-golf/data/datasets/fineweb10B_sp1024 with 80 train shards, 1 validation shard, and tokenizer /workspace/parameter-golf/data/tokenizers/fineweb_1024_bpe.model." --confirmed-finding "The exact control command was RUN_ID=ablate_control_1xh100_20260320_runpod_stable TARGET_GPU_LABEL=h100_sxm_stable bash scripts/experiments/run_1xh100_ablation.sh control." --confirmed-finding "The run finished with final_int8_zlib_roundtrip_exact val_loss=2.28415990, val_bpb=1.35280815, total_submission_size_int8_zlib_bytes=12497284, stop_step=1145, and final_eval_time_ms=11165." --confirmed-finding "Relative to the provisional legacy Runpod 1xH100 control anchor ablate_control_1xh100_1024, delta_val_bpb was +0.03123308, delta_val_loss was +0.05273575, and counted total bytes were -1507280." --confirmed-finding "No surrogate ablation was run because the declared recovery gate was val_bpb <= 1.32657507 and this control rerun missed it by +0.02623308." --inferred-conclusion "Matching the pod to the stable US/26-vCPU control profile did not recover the Runpod 1xH100 control path, so the earlier regression cannot be explained away by the low-vCPU EUR-NO-2 host alone." --inferred-conclusion "Because the compare target remains a provisional legacy anchor mirrored from the ledger rather than a frozen raw packet, paid 1xH100-surrogate ablations should remain paused until a new frozen control anchor is rebuilt." --json-out challenge_ops\\results\\2026-03-20_ablate_control_1xh100_20260320_runpod_stable.result.json --md-out challenge_ops\\results\\2026-03-20_ablate_control_1xh100_20260320_runpod_stable.result.md --require-final-metrics`
- `git status --short`

## Metrics Observed

- Exact metrics observed, with scope and source:
- Provisional legacy anchor `ablate_control_1xh100_1024` on `1xH100-surrogate` from `experiments/ledger.csv`: `val_bpb=1.32157507`, `val_loss=2.23142415`, `bytes_total=14004564`, `code_bytes=48294`, `stop_step=1506`.
- Stable-profile rerun `ablate_control_1xh100_20260320_runpod_stable` from `challenge_ops/results/2026-03-20_ablate_control_1xh100_20260320_runpod_stable.result.json`: `val_bpb=1.35280815`, `val_loss=2.28415990`, `total_submission_size_int8_zlib_bytes=12497284`, `model_int8_zlib_bytes=12435489`, `code_bytes=61795`, `stop_step=1145`, `delta_val_bpb=+0.03123308`.
- Same-family model byte series from logs/result packets: `13956270`, `13611740`, `12878462`, `12435489`.

## challenge_ops Updates

- `CURRENT_FRONTIER.md`: updated to demote `ablate_control_1xh100_1024` to a provisional legacy anchor and to recommend rebuilding a new frozen control anchor before more paid surrogate ablations.
- `TRIED_IDEAS_INDEX.md`: updated the `Control 1xH100` row to reflect missing raw anchor provenance and the rebuild requirement.
- `TERMINOLOGY_CROSSWALK.md`: added `Runpod 1xH100 provisional legacy control anchor` and a rule to demote unrecoverable anchors.
- `SUBMISSION_AUDIT.md`: updated the gating evidence to note the provenance weakness plus the stable-profile rerun failure.

## Risks And Next Actions

- Remaining risks: no frozen raw packet/log exists yet for the control anchor; the latest stable result packet still has no sibling provenance manifest because that run predates the new manifest path; local `bash` execution could not be tested directly on this Windows host because WSL is not installed.
- Recommended next step: run one new control-only rebuild on Runpod with the hardened path, preserve `provenance.json` plus raw log and result packet, and only consider resuming a single surrogate ablation if that new frozen control anchor lands near the provisional legacy `ablate_control_1xh100_1024`.
