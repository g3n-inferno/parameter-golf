# Balanced Scaling Heuristics For This Repo

## Highest-Leverage Axes To Scale Jointly

The most practical joint axes in the current `train_gpt.py` are:

- `NUM_LAYERS`
- `MODEL_DIM`
- absolute MLP size via `MLP_HIDDEN`
- `TRAIN_SEQ_LEN`

These already exist or are now env-driven without changing dataset or evaluation rules.

## Lower-Priority Axes For The Next 1xH100 Phase

- `NUM_HEADS`
- `NUM_KV_HEADS`
- precision choices beyond the tied-embedding fp16 export path

Those are still possible, but they add more confounding than value for the next 3 to 4 runs.

## Realistic 1xH100 Compound Variants

The realistic family for cheap iteration is:

- `10x480`, `MLP_HIDDEN=896`, `TRAIN_SEQ_LEN=1536`
- later only if the first point is healthy: `11x448`, `MLP_HIDDEN=832`, `TRAIN_SEQ_LEN=1536`

Why this family:

- slightly more effective depth
- modestly narrower hidden width to protect artifact size
- smaller MLP to offset deeper blocks
- longer context without jumping straight to the more throughput-sensitive `2048` or `4096` path

## Tradeoffs Likely Bad Under The Artifact Budget

- wider-only scaling at `512+` with a larger MLP
- deeper-only scaling without shrinking width or MLP
- jumping straight to `4096` context on the current `1xH100` surrogate path
- stacking fp16 passthrough on many large tensors instead of a very small targeted keep-float set

## Recommended Family After The Low-Risk Ablations

If either `fp16_embed` or `lr_warmdown` wins cleanly, the next balanced family to expand is:

- base point: `10x480`, `MLP_HIDDEN=896`, `TRAIN_SEQ_LEN=1536`
- follow-up point: same family plus a dedicated schedule retune

That keeps future `/records` packaging straightforward because the code path remains the same and the knobs are explicit env vars.
