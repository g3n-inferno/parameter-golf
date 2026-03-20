# Submission Audit

Last updated: `2026-03-20`

Use this file before any submission recommendation, candidate folder PR prep, or claim that a run is record-ready.
This file is an audit template and checklist, not a replacement for the compliance scripts.

## Current Status

- Active candidate: `none recorded yet`
- Submission intent: `not started`
- Last completed preflight: `none recorded yet`
- Latest gating evidence: clean remote control stabilization rerun `ablate_control_1xh100_20260320_runpod_stabilize` completed at `val_bpb=1.34849063`, materially worse than the adopted Runpod `1xH100` control anchor, the prior clean Runpod control retry, and the earlier remote `lr_warmdown` run, so workflow variance remains unresolved and no submission candidate was promoted.

## Mandatory Checks

- Candidate lives under the correct `/records` track.
- Submission adds only a new folder under `/records`.
- Required files exist: `README.md`, `submission.json`, `train.log`, `train_gpt.py`, plus packaged dependencies if needed.
- Packaged code is self-contained and does not depend on repo-root imports, local absolute paths, eval-time downloads, network calls, or training-data access.
- Counted artifact size is `<= 16000000` bytes.
- Packaged `train_gpt.py` and `train_gpt_mlx.py` remain within the `1500` line cap if present.
- Exact command, dataset/tokenizer variant, hardware shape, wallclock target, stop behavior, and final metrics are recorded.
- If claiming a new record, the run beats the current SOTA by at least `0.005` nats and includes enough rerun evidence for `p < 0.01`, unless it is systems-only speed work.
- If tokenizer or dataset behavior changed, a `val_bpb` correctness proof is attached.
- Meaningful run evidence is present in `experiments/ledger.csv`, and Runpod challenge runs also have usage audit rows.

## Required Commands

```bash
python scripts/compliance/check_records_submission.py <candidate_dir>
python scripts/compliance/check_artifact_size.py <candidate_dir>
python scripts/compliance/check_line_limits.py <candidate_dir>
python scripts/submission/preflight_submission.py <candidate_dir>
```

## Audit Template

### Candidate Identity

- `candidate_dir`:
- `track`:
- `submission_intent`:
- `submission_status`:
- `run_id`:
- `branch`:
- `git_head`:

### Metadata

- `author`:
- `github_id`:
- `name`:
- `blurb`:
- `date`:

### Reproducibility

- `source_script`:
- `packaged_script`:
- `declared_dependencies`:
- `candidate_manifest_path`:
- `dataset_variant`:
- `dataset_path`:
- `tokenizer_variant`:
- `tokenizer_path`:
- `exact_command`:
- `hardware`:
- `gpu_shape`:
- `topology`:
- `framework_version`:
- `wallclock_target_seconds`:
- `wallclock_seconds`:
- `stop_reason`:
- `step_stop`:

### Metrics And Artifact Size

- `val_loss`:
- `val_bpb`:
- `pre_quant_val_loss`:
- `pre_quant_val_bpb`:
- `eval_time_seconds`:
- `bytes_model_int8_zlib`:
- `bytes_code`:
- `bytes_total`:

### Evidence

- `train_log_path`:
- `extra_log_paths`:
- `summary_json_path`:
- `ledger_row_ref`:
- `runpod_session_id`:
- `runpod_run_id`:
- `usage_scope`:
- `funding_note`:

### Challenge Compliance

- `eval_restrictions_asserted`:
- `tokenizer_changed`:
- `dataset_changed`:
- `val_bpb_correctness_proof`:
- `sota_anchor_val_bpb`:
- `delta_vs_sota`:
- `stat_test`:
- `p_value`:
- `rerun_log_count`:

### Command Results

- `records_shape_status`:
- `artifact_size_status`:
- `line_limit_status`:
- `preflight_status`:

### Reviewer Notes

- Confirmed findings:
- Inferred conclusions:
- Blockers:
- Recommendation:
