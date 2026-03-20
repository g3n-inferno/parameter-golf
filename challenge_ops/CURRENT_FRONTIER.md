# Current Frontier

Last updated: `2026-03-20`

This file is the Project GPT and Codex quick-read memory for the current repo frontier.
Use it with `experiments/ledger.csv`, `/records`, and `challenge_ops/TRIED_IDEAS_INDEX.md`.

## Best Known Result

- Confirmed repo-best leaderboard-track result: `Long Context Seq2048 v2`
  - Source: `records/track_10min_16mb/2026-03-18_LongContextSeq2048/README.md`
  - Exact printed metric: `final_int8_zlib_roundtrip_exact val_bpb=1.20576485`
  - Artifact size: `15867270` total bytes
  - Scope: `8xH100-leaderboard`
- Confirmed public repo baseline anchor: `Naive Baseline`
  - Source: `records/track_10min_16mb/2026-03-17_NaiveBaseline/submission.json`
  - Exact `val_bpb`: `1.22436570`
  - Artifact size: `15863489` total bytes
  - Scope: `8xH100-leaderboard`
- Confirmed strongest non-record unlimited-compute reference in repo: `4-Hour Baseline`
  - Source: `records/track_non_record_16mb/2026-03-18_Quasi10Bfrom50B_SP1024_9x512_KV4_4h_pgut3/README.md`
  - Reported `val_bpb`: `1.2074`
  - Scope: `non-record-unlimited`

## Strongest Baselines

| Anchor | Scope | Exact `val_bpb` | Notes |
| --- | --- | ---: | --- |
| `Naive Baseline` | `8xH100-leaderboard` | `1.22436570` | Public leaderboard baseline and record-track comparison anchor. |
| `baseline_sp1024_h100_local_20260319` | `1xH100-surrogate` | `1.32321114` | Local baseline summary used for current ablations. |
| `ablate_control_1xh100_1024` | `1xH100-surrogate` | `1.32157507` | Most direct local control rerun near current baseline path. |

## Known Good Ideas

- `long_context_seq2048`
  - Standardized name: `seq2048_long_context`
  - Verdict: `variant / already-tried / positive / track-candidate @ 8xH100-leaderboard`
  - Evidence: best confirmed repo result.
- `fp16_embed_warmdown`
  - Standardized name: `fp16_tied_embedding_with_warmdown`
  - Verdict: `variant / already-tried / positive / track-candidate @ 8xH100-leaderboard`
  - Evidence: `records/track_10min_16mb/2026-03-18_FP16Embed_WD3600`.
- `sliding_window_eval`
  - Standardized name: `sliding_window_evaluation_stride64`
  - Verdict: `novel / already-tried / positive / track-candidate @ 8xH100-leaderboard`
  - Evidence: `records/track_10min_16mb/2026-03-19_SlidingWindowEval`.
- `lr_warmdown`
  - Standardized name: `longer_warmdown_schedule`
  - Verdict: `variant / already-tried / positive / non-record @ 1xH100-surrogate`
  - Evidence: `experiments/ledger.csv` entry `ablate_lr_warmdown_1xh100_1024` with `delta_val_bpb=-0.00411918` vs local baseline.

## Known Weak Or Negative Ideas

- `compound_ctx1536`
  - Standardized name: `compound_longer_context_1536_probe`
  - Verdict: `variant / already-tried / negative / non-record @ 1xH100-surrogate`
  - Evidence: `ablate_compound_ctx1536_1xh100` regressed to `1.32518999`.
- `fp16_embed_local_probe`
  - Standardized name: `fp16_tied_embedding_local_probe`
  - Verdict: `variant / already-tried / negative / non-record @ 1xH100-surrogate`
  - Evidence: `ablate_fp16_embed_1xh100_1024` regressed to `1.32389328`.

## Biggest Bottleneck

- Confirmed: the repo now has stronger local `1xH100-surrogate` evidence than direct `8xH100-leaderboard` reruns.
- Inferred: the main decision bottleneck is converting promising local variants into apples-to-apples leaderboard evidence without wasting paid runs or violating challenge constraints.

## Most Promising Next Experiment

- Candidate: promote the strongest local schedule win into a leaderboard-comparable rerun.
- Standardized name: `longer_warmdown_schedule`
- Why:
  - Confirmed local evidence beats the current local baseline.
  - Artifact headroom is still comfortable on the local run.
  - It is a variant of an already legal, already packaged family rather than a new tokenizer or dataset path.
- Guardrails before any expensive run:
  - keep dataset and tokenizer unchanged
  - keep result reporting apples to apples
  - predeclare anchor, scope, and success threshold in an experiment brief
  - run submission and artifact checks before claiming record relevance

## Artifact Budget View

Artifact cap: `16000000` bytes

| Run | Scope | Counted total bytes | Headroom |
| --- | --- | ---: | ---: |
| `Naive Baseline` | `8xH100-leaderboard` | `15863489` | `136511` |
| `Long Context Seq2048 v2` | `8xH100-leaderboard` | `15867270` | `132730` |
| `Sliding Window Eval` | `8xH100-leaderboard` | `15874829` | `125171` |
| `local_1xh100_baseline_summary` | `1xH100-surrogate` | `14037860` | `1962140` |
| `ablate_lr_warmdown_1xh100_1024` | `1xH100-surrogate` | `12455545` | `3544455` |

## Terminology Reminders

- `frontier` means untested or under-tested idea, not current SOTA.
- `track-candidate` means plausible for `records/track_10min_16mb`, not automatically submission-ready.
- `already-tried` starts at the first meaningful ledger row or `/records` evidence.
- `positive`, `negative`, and `inconclusive` are scope-specific. Do not collapse `1xH100-surrogate` and `8xH100-leaderboard` evidence into one verdict.
- Treat challenge legality, reproducibility, and counted artifact size as first-class constraints on every frontier update.
