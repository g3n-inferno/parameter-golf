# Experiment Brief

## Identity

- `experiment_id`: `control_path_diagnosis_20260321_fresh_template`
- `run_id`: `control_path_diagnosis_20260321_fresh_template_runpod`
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

- What is being tested: Run one fresh official-template 1xH100 control-path diagnosis on unchanged sp1024 data/tokenizer, using shell-safe SSH checks and aborting early if repo checkout recovery is stubbed or exceeds the bounded setup window.
- Why now: The current frontier still identifies 1xH100 control-path reproducibility as the blocker. The previous supervised attempt burned setup time on a reused stub pod without reaching training, so the highest-value next step is a fresh official-template control diagnosis with tighter setup gates.

## Anchor And Novelty Check

- Closest prior idea or run: `baseline_sp1024_1xh100_20260320_integrated_main`
- Anchor metric and scope: fresh official-template integrated-main baseline reproduction: val_bpb=1.34888151 on 1xH100 Runpod NVIDIA H100 80GB HBM3; provisional legacy control anchor: val_bpb=1.32157507
- Why this is `novel`, `variant`, or `baseline`: This is not novel; it is a controlled fresh-pod rerun of the already-tried 1xH100 control family, focused on isolating setup-path instability rather than testing a new model idea.
- Check against `challenge_ops/TRIED_IDEAS_INDEX.md`: existing row found for `runpod_1xh100_control_anchor`; treat this as already represented in repo memory.

## Exact Plan

- Code path: `train_gpt.py`
- Dataset/tokenizer variant: `fineweb10B_sp1024` with `fineweb_1024_bpe.model`
- Hardware target: `Runpod 1xH100 pod`
- Wallclock target: `600s`
- Exact planned command: `RUN_ID=control_path_diagnosis_20260321_fresh_template_runpod TARGET_GPU_LABEL=h100_sxm_fresh_template DATA_PATH=/workspace/parameter-golf/data/datasets/fineweb10B_sp1024 TOKENIZER_PATH=/workspace/parameter-golf/data/tokenizers/fineweb_1024_bpe.model VOCAB_SIZE=1024 VAL_LOSS_EVERY=200 bash scripts/experiments/run_baseline_1gpu.sh`

## Success And Failure Criteria

- Success threshold: Fresh official-template pod passes profile and repo checks, setup completes within the bounded recovery window, and the run records final metrics with val_bpb within 0.005 nats of the best rebuilt-control rerun or better.
- Failure threshold: Repo checkout is stubbed and not safely recoverable within the bounded setup window, pod profile mismatches the declared control profile, or the run again lands materially above the current fresh-pod anchor without a confounder fix.
- What would count as inconclusive: infra failure, dataset download failure, SSH/Jupyter control-path instability, or missing final metrics after a bounded setup attempt

## Reproducibility And Legality

- Eval restrictions reminder: No eval-time downloads, network calls, or training-data access may be required by any resulting artifact claim.
- Artifact size concern: Keep the resulting artifact under 16,000,000 counted bytes; this is a control-path diagnosis only, not a submission attempt. Current cap: 16000000 bytes.
- Tokenizer/dataset correctness concern: Keep the documented dataset and tokenizer unchanged; no val_bpb proof plan is needed for this run.
- Runpod or cost concern: Create exactly one fresh official-template 1xH100 pod, never reuse an old pod for this trial, and stop immediately on profile mismatch or setup overrun instead of spending the run on model training.

## Planned Outputs

- Expected log path: `logs/experiments/**/*_control_path_diagnosis_20260321_fresh_template_runpod/run.log`
- Expected result markdown path: `C:\Users\g3n_i\Desktop\0. Coding\Projects\parameter-golf\challenge_ops\results\2026-03-21_control_path_diagnosis_20260321_fresh_template_runpod.result.md`
- Expected result JSON path: `C:\Users\g3n_i\Desktop\0. Coding\Projects\parameter-golf\challenge_ops\results\2026-03-21_control_path_diagnosis_20260321_fresh_template_runpod.result.json`
- Ledger update plan: use `scripts/autonomy/controller.py record-result ...` after the run to generate the result packet and sync `experiments/ledger.csv`.

## Notes

- Extra context: Use template y5cejece4j on one fresh H100 SXM pod in the declared US control profile. Use only shell-safe SSH probes before any dataset download.
