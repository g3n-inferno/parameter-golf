# Next 1xH100 Workstream

This note chooses the next 1xH100-only workstream from the current repo state and the public leaderboard snapshot as of 2026-03-19.

## Why This Workstream

- The current Runpod `1xH100` surrogate anchor is `val_bpb=1.32321114` with `14,037,860` total int8+zlib bytes and a `wallclock_cap` stop at step `1444`.
- The public `8xH100` naive baseline is `1.2244`, so the Runpod surrogate anchor is behind by about `+0.0988` BPB and should be treated as a cheap iteration surrogate, not a leaderboard-comparable result.
- The public `4-hour` non-record baseline reached `1.2074`, which says extra compute on the same 9x512 layout is useful but not the first lever to test.
- The cleanest public low-risk gains came from:
  - fp16 tied-embedding export plus modest size compensation and LR/warmdown tuning
  - longer context
- The strongest repo-compatible next step is therefore a compact ablation program centered on:
  - fp16 tied-embedding export
  - schedule tuning
  - one balanced scaling probe

## Chosen Primary Workstream

Use a hand-picked four-run matrix on `1xH100`, not a reusable mini-search framework:

1. `control`
2. `fp16_embed`
3. `lr_warmdown`
4. `compound_ctx1536`

Rationale:

- It preserves the baseline launcher path and keeps diffs narrow.
- It tests the highest-leverage public ideas before new architecture churn.
- It still includes one original balanced-scaling point instead of only scalar hyperparameter tuning.

## Commands

Run from repo root on the `1xH100` pod:

```bash
bash scripts/experiments/run_1xh100_ablation.sh control
```

```bash
bash scripts/experiments/run_1xh100_ablation.sh fp16_embed
```

```bash
bash scripts/experiments/run_1xh100_ablation.sh lr_warmdown
```

```bash
bash scripts/experiments/run_1xh100_ablation.sh compound_ctx1536
```

The wrapper:

- uses the existing `scripts/experiments/run_baseline_1gpu.sh` path
- writes timestamped logs under `logs/experiments/next_1xh100_workstream/`
- refreshes `experiments/ledger.csv`
- compares each run against the legacy compatibility file `experiments/baselines/local_1xh100_baseline_summary.json`, which stores the Runpod `1xH100` control anchor
- checks the artifact cap from the parsed summary JSON

## Matrix Summary

### `control`

- Goal: refresh the Runpod `1xH100` control anchor under the same baseline-family command shape
- Expected win: `val_bpb < 1.3232`
- Risk: low artifact and compliance risk

### `fp16_embed`

- Change: keep `tok_emb.weight` in fp16 during export and set `MLP_HIDDEN=992`
- Goal: reduce post-quant degradation without changing training rules
- Expected win: any clear `val_bpb` gain at similar steps while staying under `16,000,000` bytes

### `lr_warmdown`

- Change: `WARMDOWN_ITERS=3600`, `MATRIX_LR=0.06`
- Goal: adapt the schedule to the very low step count seen on `1xH100`
- Expected win: `>= 0.01` BPB improvement versus the Runpod `1xH100` control anchor

### `compound_ctx1536`

- Change: `NUM_LAYERS=10`, `MODEL_DIM=480`, `MLP_HIDDEN=896`, `TRAIN_SEQ_LEN=1536`
- Goal: test a balanced multi-axis tradeoff instead of a single-axis tweak
- Expected win: beat both the refreshed control and at least one low-risk ablation

## Stop / Continue Rule

- Continue this workstream if either `fp16_embed` or `lr_warmdown` improves the Runpod `1xH100` control anchor by about `0.01` BPB or more.
- Escalate to a dedicated `2048` context follow-up only if at least one of those low-risk runs wins cleanly and remains comfortable on artifact size.
- Do not move to `8xH100` candidate work yet unless a `1xH100` run lands near the public naive baseline proxy zone and the same change remains packaging-safe.
