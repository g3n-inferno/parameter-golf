# Submission Preflight Checklist

Use this checklist before deciding whether a candidate under `/records` is ready for a real submission branch or PR.

## Track Choice

- Confirm the candidate belongs in the correct track:
  - `records/track_10min_16mb/` for leaderboard-relevant runs
  - `records/track_non_record_16mb/` for non-record or unlimited-compute style runs
- Do not package a non-record result as if it were a SOTA candidate.

## SOTA Vs Non-Record

- If the candidate claims a new SOTA, verify it beats the current SOTA by at least `0.005` nats.
- If the candidate is not intended to beat SOTA, package it as a non-record submission and say so clearly in the README.
- Make sure the README states whether the run is leaderboard-comparable or not.

## Statistical Evidence

- New SOTA claims require enough evidence to justify `p < 0.01`, unless the change is purely a systems-only speed optimization.
- Do not rely on one lucky run when statistical evidence is required.
- Do not brute-force seeds or run blind search sweeps in place of principled evidence.

## Tokenizer And Dataset Warning

- If the tokenizer changed, expect much stronger scrutiny.
- If the dataset changed, verify the reported `val_bpb` is still correct.
- Do not submit tokenizer or dataset modifications without a clear correctness argument.

## Evaluation Restrictions

- No network calls during evaluation.
- No training-data access during evaluation unless those bits are included in the artifact budget.
- No eval-time downloads.
- The candidate folder should look runnable from inside the record folder itself.

## Structural Readiness

- `README.md` exists and explains the run clearly.
- `submission.json` exists and parses.
- `train.log` is present.
- `train_gpt.py` is present.
- Any extra dependencies needed to run from inside the record folder are included.
- The candidate is packaged under `/records`, not left as loose root-level code edits.

## Artifact And Line Limits

- Total counted artifact bytes pass the `16,000,000` byte cap.
- `train_gpt.py` is at or below `1500` lines.
- `train_gpt_mlx.py` is at or below `1500` lines if included.

## Broken Script Rule

- Do not submit broken scripts.
- The packaged script should compile and run from inside the candidate folder.
- A preflight pass is necessary, but it does not replace actually verifying the packaged script works.

## Final Decision

- If preflight fails, fix the candidate locally before doing anything else.
- If preflight passes, you still need to decide whether the candidate is worth submitting.
- Do not push, commit, or open a PR from this checklist step alone.
