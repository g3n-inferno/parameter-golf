# Codex Handoff

## Task

- Request summary: do a no-new-model-change forensic control-path audit comparing the fresh official-template runs (`1.34888151`, `1.35283929`) against the reused same-pod rebuild family (`1.32963305`, `1.32776835`, `1.33473550`) using stored provenance, Runpod session data, remote environment fingerprints, and wrapper/code hashes.
- Scope: local forensic comparison only; no new paid Runpod work unless one concrete confounder emerges from stored evidence.
- Constraint summary: stay local by default, distinguish confirmed findings from inference, and only propose another paid `1xH100` run if it tests one concrete confounder rather than repeating a generic fresh control rerun.

## Outcome

- Status: completed.
- What changed: updated `challenge_ops/CURRENT_FRONTIER.md` and `challenge_ops/TRIED_IDEAS_INDEX.md` to reflect the audit result and the narrowed follow-up recommendation.
- What did not change: no paid Runpod action, no training-code change, no new experiment row, and no submission packaging work.

## Confirmed Findings

- The reused same-pod rebuild family (`ablate_control_1xh100_20260321_runpod_frozen_anchor_a/b/c`) and the fresh-template rerun `control_path_diagnosis_20260321_fresh_template_runpod` share the same recorded `train_gpt.py` hash `15846ddcd260753dbd7023522e1e12a6d0dec0dd5cb5e5a69446b6407a3b7bd5`, dataset manifest hash `c0ebc88d5ac10324c8dc29c27041ec0efdc6441f9be747901c4f7f45f59ae9`, tokenizer hash `4f5e8adb109c66b4886963bc75a7befd73bda36d27fd7102df8e9e66503b0e2a`, and baseline-wrapper hash `8f5024481bedafdf7519290c72634822b66b79bc333afe65c9a7574f99c88311`.
- The fresh official-template rerun `control_path_diagnosis_20260321_fresh_template_runpod` and the earlier fresh official-template run `baseline_sp1024_1xh100_20260320_integrated_main` did not use identical training commands: the earlier run omitted `VAL_LOSS_EVERY=200`, while the later fresh rerun and the reused same-pod rebuild family all included it.
- The later fresh rerun `control_path_diagnosis_20260321_fresh_template_runpod` landed at `val_bpb=1.35283929`, only `+0.00003114` from the earlier clean stable-profile rerun `ablate_control_1xh100_20260320_runpod_stable` at `1.35280815`.
- The reused same-pod rebuild family on pod `474jlphqpo5n8x` landed at `1.32963305`, `1.32776835`, and `1.33473550`, materially better than the later fresh-template rerun despite the shared recorded code/data/tokenizer/wrapper hashes.
- The reused rebuild family ran in a dirty detached checkout on pod `474jlphqpo5n8x`, with `status_short` showing modified wrapper/result-tracking files and later runs carrying untracked `final_model.pt` / `final_model.int8.ptz`; `train_gpt.py` overwrites and reloads those filenames inside each run.

## Inferred Conclusions

- After accounting for the `VAL_LOSS_EVERY` mismatch between the two fresh official-template runs, the strongest remaining concrete confounder in stored evidence is warm reused-container state on pod `474jlphqpo5n8x`.
- The dirty detached checkout and leftover `final_model.*` files are weaker candidates because the reused family and the later fresh-template rerun still share the same recorded training-code hash, dataset/tokenizer hashes, and baseline-wrapper hash, and the saved `final_model.*` filenames are overwritten during each run.
- A justified next paid run would therefore be one paired warm-state test, not another generic fresh official-template rerun.

## Files Changed

- Exact paths changed:
- `challenge_ops/CURRENT_FRONTIER.md`
- `challenge_ops/TRIED_IDEAS_INDEX.md`
- `challenge_ops/results/2026-03-21_codex_handoff_control_path_forensic_audit.md`

## Commands Run

- Exact commands run:
- `Get-Content -Raw .codex/skills/parameter-golf-autonomy/SKILL.md`
- `Get-Content -Raw challenge_ops/templates/codex_handoff.md`
- `Get-Content -Raw experiments/runpod_sessions.csv`
- `Get-Content -Raw experiments/runpod_runs.csv`
- `Get-Content -Raw experiments/ledger.csv`
- `Get-Content -Raw challenge_ops/results/2026-03-20_ablate_control_1xh100_20260320_runpod_stable.result.json`
- `Get-Content -Raw challenge_ops/results/2026-03-21_ablate_control_1xh100_20260321_runpod_frozen_anchor_b.result.json`
- `Get-Content -Raw challenge_ops/results/2026-03-21_control_path_diagnosis_20260321_fresh_template_runpod.result.json`
- `Get-Content -Raw logs/experiments/baseline_1gpu/20260321_024153_baseline_sp1024_1xh100_20260320_integrated_main/provenance.json`
- `Get-Content -Tail 30 logs/experiments/baseline_1gpu/20260321_024153_baseline_sp1024_1xh100_20260320_integrated_main/run.log`
- `Select-String -Path train_gpt.py,scripts/experiments/run_1xh100_ablation.sh,scripts/experiments/run_baseline_1gpu.sh -Pattern 'final_model|ptz|torch.load|load_state_dict|resume|checkpoint' -Context 1,1`
- `Get-Content -Raw scripts/experiments/run_1xh100_ablation.sh`
- `Get-Content -Raw scripts/experiments/run_baseline_1gpu.sh`
- `python -` scripts that normalized and compared the result/provenance surfaces for the fresh and reused control families

## Metrics Observed

- Exact metrics observed, with scope and source:
- `baseline_sp1024_1xh100_20260320_integrated_main`: `val_bpb=1.34888151`, `stop_step=1136`, `total_submission_size_int8_zlib_bytes=12841006`
- `control_path_diagnosis_20260321_fresh_template_runpod`: `val_bpb=1.35283929`, `stop_step=1107`, `total_submission_size_int8_zlib_bytes=12808876`
- `ablate_control_1xh100_20260321_runpod_frozen_anchor_a/b/c`: `val_bpb=1.32963305`, `1.32776835`, `1.33473550`
- `delta_val_bpb` between `control_path_diagnosis_20260321_fresh_template_runpod` and `ablate_control_1xh100_20260320_runpod_stable`: `+0.00003114`

## challenge_ops Updates

- `CURRENT_FRONTIER.md`: updated to record the `VAL_LOSS_EVERY` mismatch and to narrow the next paid-control recommendation to a paired warm-state test.
- `TRIED_IDEAS_INDEX.md`: updated the `Control 1xH100` row with the same forensic conclusion.
- `TERMINOLOGY_CROSSWALK.md`: no change.
- `SUBMISSION_AUDIT.md`: no change.

## Risks And Next Actions

- Remaining risks: older fresh/stable result packets still lack full provenance blocks, so some environment details remain unrecorded; warm reused-container state is a concrete hypothesis but not yet directly isolated by an explicit paired run.
- Recommended next step: only if more GPU time is approved, run one fresh official-template `1xH100` control test that executes the exact `VAL_LOSS_EVERY=200` command twice back to back on the same untouched pod, comparing first-run vs second-run throughput, `stop_step`, and `val_bpb`.
