# Experiment Brief

## Identity

- `experiment_id`: `control_path_warm_state_pair_20260321`
- `run_id`: `control_path_warm_state_pair_20260321_runpod_pair`
- `idea_label`: `Control 1xH100`
- `standardized_name`: `runpod_1xh100_control_anchor`
- `owner`: `Codex`
- `date`: `2026-03-21`

## Standardized Classification

- `lineage`: `variant`
- `state`: `already-tried`
- `intent`: `non-record`
- `scope`: `1xH100-surrogate`

## Objective

- What is being tested: Run the unchanged sp1024 1xH100 control command twice back to back on one fresh official-template H100 pod to test whether warm reused-container state explains the gap between the fresh-pod ~1.3528 regime and the reused same-pod 1.3278-1.3347 regime.
- Why now: The forensic audit ruled out the recorded code, dataset, tokenizer, wrapper, and declared pod profile surfaces as the main explanation. The strongest remaining concrete confounder is warm reused-container state.

## Anchor And Novelty Check

- Closest prior idea or run: `control_path_diagnosis_20260321_fresh_template_runpod`
- Anchor metric and scope: Fresh official-template controls landed at val_bpb=1.34888151 and 1.35283929, while reused same-pod rebuilds on pod 474jlphqpo5n8x landed at 1.32963305, 1.32776835, and 1.33473550.
- Why this is `novel`, `variant`, or `baseline`: This is not a model-change idea. It is a controlled reproducibility and ops experiment that isolates same-pod warm-state effects under the existing 1xH100 control path.
- Check against `challenge_ops/TRIED_IDEAS_INDEX.md`: existing row found for `runpod_1xh100_control_anchor`; treat this as already represented in repo memory.

## Exact Plan

- Code path: `train_gpt.py`
- Dataset/tokenizer variant: `fineweb10B_sp1024` with `fineweb_1024_bpe.model`
- Hardware target: `Runpod 1xH100 pod`
- Wallclock target: `600s`
- Exact planned command: `PAIR_ID=control_path_warm_state_pair_20260321 RUN1_ID=control_path_warm_state_pair_20260321_run1 RUN2_ID=control_path_warm_state_pair_20260321_run2 VAL_LOSS_EVERY=200 MAX_WALLCLOCK_SECONDS=600 bash scripts/experiments/run_warm_state_control_pair.sh`

## Success And Failure Criteria

- Success threshold: The second run reproduces a materially better result or throughput regime than the first run under matching recorded provenance, supporting warm-state contamination as a real confounder.
- Failure threshold: Both runs remain in the same fresh-pod regime within normal noise, or the pod fails the bounded checkout and environment checks before training starts.
- What would count as inconclusive: infra failure, missing final metrics, or a confounded setup change

## Reproducibility And Legality

- Eval restrictions reminder: No eval-time downloads, network calls, or training-data access may be required by any resulting artifact claim.
- Artifact size concern: Keep counted artifact bytes under the 16,000,000-byte cap. Current cap: 16000000 bytes.
- Tokenizer/dataset correctness concern: Keep the documented dataset and tokenizer unchanged; no val_bpb proof plan is needed for this run.
- Runpod or cost concern: Use exactly one fresh official-template 1xH100 pod, one approval token, and one paired run only. If checkout recovery or environment verification exceeds the bound, abort before training and stop the pod.

## Planned Outputs

- Expected log path: `logs/experiments/**/*_control_path_warm_state_pair_20260321_runpod_pair/run.log`
- Expected result markdown path: `C:\Users\g3n_i\Desktop\0. Coding\Projects\parameter-golf\challenge_ops\results\2026-03-21_control_path_warm_state_pair_20260321_runpod_pair.result.md`
- Expected result JSON path: `C:\Users\g3n_i\Desktop\0. Coding\Projects\parameter-golf\challenge_ops\results\2026-03-21_control_path_warm_state_pair_20260321_runpod_pair.result.json`
- Ledger update plan: use `scripts/autonomy/controller.py record-result ...` after the run to generate the result packet and sync `experiments/ledger.csv`.

## Notes

- Extra context: Before any remote action, render this same brief with --dry-run, grant one approval token, verify /workspace/parameter-golf/.git, verify shell-safe SSH control commands, and collect the pair summary artifact from scripts/experiments/run_warm_state_control_pair.sh.
