# Structured Sequence Research Note

## Realistic Medium-Term Ideas In This Repo

The most realistic original directions after the low-risk ablations are:

- tied-block recurrence
- lightweight local 1D shared-kernel mixing ahead of attention
- chunk-summary side paths that preserve the current validation and tokenizer assumptions

These ideas stay close to token-sequence structure and can improve quality-per-byte through reuse instead of brute-force width.

## Best Medium-Term Branch

The best original branch after the current ablation matrix is:

- recurrent shared-block depth with a small number of untied stages

Why:

- parameter sharing is directly aligned with the `16,000,000` byte cap
- it can increase effective depth without paying for fully unique layers
- it is easier to package later than a full multiresolution token pyramid

## Ideas Worth Researching But Not Implementing Yet

- a local convolutional or Toeplitz-like pre-mixer for short-range structure
- chunked recurrent summaries between groups of tokens

These are interesting, but they should follow only after the current matrix identifies whether the repo is limited more by export quality, schedule, or balanced layout.

## Ideas Too Risky Or Too Expensive Right Now

- full hierarchical token pyramids
- large evaluation-only rule changes
- broad structured-matrix replacements across all dense projections
- graph, manifold, or gauge-inspired methods without a direct token-sequence transfer argument

Those paths are too invasive for the next narrow 1xH100 step and would make attribution and future `/records` packaging harder.
