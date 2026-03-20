# Experiment Brief

Use this template before a meaningful experiment, packaging attempt, or submission-prep task.

## Identity

- `experiment_id`: `control_runpod_1xh100_20260320_stable_profile`
- `idea_label`: `Control 1xH100`
- `standardized_name`: `runpod_1xh100_control_anchor`
- `owner`: `Codex`
- `date`: `2026-03-20`

## Standardized Classification

- `lineage`: `variant`
- `state`: `already-tried`
- `intent`: `non-record`
- `scope`: `1xH100-surrogate`

## Objective

- What is being tested: rerun the remote control path on either the same stopped pod if restartable or a fresh pod that exactly matches the declared stable `Runpod 1xH100 control anchor` hardware/workflow profile.
- Why now: the previous stabilization rerun used an `EUR-NO-2` / `8 vCPU` host that fell outside the intended control family, so the control path must be rechecked on a profile-matching pod before any surrogate ablation resumes.

## Anchor And Novelty Check

- Closest prior idea or run: `experiments/ledger.csv` row `ablate_control_1xh100_1024`
- Anchor metric and scope: adopted `Runpod 1xH100 control anchor` is `ablate_control_1xh100_1024` at `val_bpb=1.32157507` on `1xH100-surrogate`
- Why this is `novel`, `variant`, or `baseline`: `variant`; this is a same-family control rerun under stricter hardware/workflow gating.
- Check against `challenge_ops/TRIED_IDEAS_INDEX.md`: existing `Control 1xH100` row confirmed; do not call this `novel`.

## Exact Plan

- Code path: `train_gpt.py` through `scripts/experiments/run_1xh100_ablation.sh`
- Frozen commit: `bc75d7b0c350a41af25131232854833340265e86`
- Declared control profile: `challenge_ops/runpod_1xh100_control_profile.json`
- Pod reuse rule: first try restarting a prior matching stopped pod; if that fails, create a fresh H100 SXM pod in an allowed US datacenter and require a passing profile check before SSH or training
- Dataset/tokenizer variant: `fineweb10B_sp1024` with `fineweb_1024_bpe.model`
- Wallclock target: `600s`
- Exact planned command: `RUN_ID=ablate_control_1xh100_20260320_runpod_stable TARGET_GPU_LABEL=h100_sxm_stable bash scripts/experiments/run_1xh100_ablation.sh control`

## Success And Failure Criteria

- Success threshold: final parsed metrics present and `val_bpb <= 1.32657507`, which is within `+0.00500000` of `ablate_control_1xh100_1024`
- Failure threshold: profile mismatch, grounded infra failure, or control rerun landing worse than the success threshold
- What would count as inconclusive: missing final metrics or any drift in commit, dataset, tokenizer, or declared pod profile

## Reproducibility And Legality

- Eval restrictions reminder: no eval-time downloads, network calls, or training-data access may be required by any resulting artifact claim.
- Artifact size concern: still record counted bytes for the control rerun and any follow-up surrogate ablation.
- Tokenizer/dataset correctness concern: tokenizer and dataset behavior must remain unchanged and be verified before training.
- Runpod or cost concern: if control does not recover near the adopted anchor, stop immediately and do not spend GPU time on a surrogate ablation.

## Planned Outputs

- Expected log path: `logs/experiments/next_1xh100_workstream/control/*_ablate_control_1xh100_20260320_runpod_stable/run.log`
- Expected result markdown path: `challenge_ops/results/2026-03-20_ablate_control_1xh100_20260320_runpod_stable.result.md`
- Expected result JSON path: `challenge_ops/results/2026-03-20_ablate_control_1xh100_20260320_runpod_stable.result.json`
- Conditional follow-up: run at most one surrogate ablation only if the control success threshold is met

## Notes

- The stable control family now explicitly excludes low-vCPU non-US H100 hosts such as `vlmy3ngmeqbq96`.
