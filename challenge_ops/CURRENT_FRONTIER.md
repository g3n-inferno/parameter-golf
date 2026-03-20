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
| `baseline_sp1024_h100_local_20260319` | `1xH100-surrogate` | `1.32321114` | Legacy-named baseline summary from a Runpod `1xH100` pod; keep the run ID for compatibility. |
| `ablate_control_1xh100_1024` | `1xH100-surrogate` | `1.32157507` | Direct Runpod `1xH100` control rerun near the current surrogate anchor path. |

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

## Known Mixed Or Inconclusive Ideas

- `control_1xh100`
  - Standardized name: `runpod_1xh100_control_anchor`
  - Verdict: `variant / already-tried / inconclusive / non-record @ 1xH100-surrogate`
  - Evidence: Runpod-surrogate `ablate_control_1xh100_1024` reached `val_bpb=1.32157507`, but fresh single-pod Runpod retry `ablate_control_1xh100_20260320_runpod_retry2` landed at `1.33518228`.
- `lr_warmdown`
  - Standardized name: `longer_warmdown_schedule`
  - Verdict: `variant / already-tried / inconclusive / non-record @ 1xH100-surrogate`
  - Evidence: earlier `1xH100-surrogate` run `ablate_lr_warmdown_1xh100_1024` reached `val_bpb=1.31909196`, but remote Runpod rerun `ablate_lr_warmdown_1xh100_20260320_runpod` regressed to `1.33058722`, and the clean remote control retry was even worse at `1.33518228`.

## Known Weak Or Negative Ideas

- `compound_ctx1536`
  - Standardized name: `compound_longer_context_1536_probe`
  - Verdict: `variant / already-tried / negative / non-record @ 1xH100-surrogate`
  - Evidence: `ablate_compound_ctx1536_1xh100` regressed to `1.32518999`.
- `fp16_embed_1xh100_probe`
  - Standardized name: `fp16_tied_embedding_1xh100_probe`
  - Verdict: `variant / already-tried / negative / non-record @ 1xH100-surrogate`
  - Evidence: `ablate_fp16_embed_1xh100_1024` regressed to `1.32389328`.

## Biggest Bottleneck

- Confirmed: `1xH100-surrogate` reproducibility is now a bottleneck, because the strongest earlier `lr_warmdown` win did not reproduce on a real Runpod H100 SXM rerun.
- Confirmed: the fresh single-pod remote control retry `ablate_control_1xh100_20260320_runpod_retry2` completed at `val_bpb=1.33518228`, which is `+0.01360721` worse than the current Runpod `1xH100` control anchor and `+0.00459506` worse than the earlier remote `lr_warmdown` run.
- Inferred: the dominant issue is workflow variance on the Runpod `1xH100-surrogate` path, not an idea-specific `lr_warmdown` miss, and more paid ablations should pause until that control path is reliable.

## Most Promising Next Experiment

- Candidate: a narrow Runpod control-path stabilization pass for the fresh-boot remote control path before any more paid ablations.
- Standardized name: `runpod_1xh100_control_anchor`
- Why:
  - Confirmed the clean remote control retry completed and still landed materially worse than the existing Runpod `1xH100` surrogate anchors.
  - Confirmed the clean remote control retry was also worse than the earlier remote `lr_warmdown` run, so the workflow itself is now the strongest confounder.
  - The highest-value next move is to make the exact control path reliable, not to spend more money on another ablation variant.
- Guardrails before any expensive run:
  - keep dataset and tokenizer unchanged
  - keep result reporting apples to apples
  - predeclare anchor, scope, and success threshold in an experiment brief
  - use one pod and one operator thread only; do not allow parallel agents to touch Runpod
  - verify the pod still has a real repo checkout after start or resume; if not, reclone before any dataset or training step
  - stop after a grounded infra failure rather than spending more paid ablation time on an unstable pod
  - run submission and artifact checks before claiming record relevance

## Artifact Budget View

Artifact cap: `16000000` bytes

| Run | Scope | Counted total bytes | Headroom |
| --- | --- | ---: | ---: |
| `Naive Baseline` | `8xH100-leaderboard` | `15863489` | `136511` |
| `Long Context Seq2048 v2` | `8xH100-leaderboard` | `15867270` | `132730` |
| `Sliding Window Eval` | `8xH100-leaderboard` | `15874829` | `125171` |
| `local_1xh100_baseline_summary` (legacy alias for `runpod_1xh100_control_anchor`) | `1xH100-surrogate` | `14037860` | `1962140` |
| `ablate_lr_warmdown_1xh100_1024` | `1xH100-surrogate` | `12455545` | `3544455` |
| `ablate_lr_warmdown_1xh100_20260320_runpod` | `1xH100-surrogate` | `12053652` | `3946348` |
| `ablate_control_1xh100_20260320_runpod_retry2` | `1xH100-surrogate` | `13673535` | `2326465` |

## Terminology Reminders

- `frontier` means untested or under-tested idea, not current SOTA.
- `track-candidate` means plausible for `records/track_10min_16mb`, not automatically submission-ready.
- `already-tried` starts at the first meaningful ledger row or `/records` evidence.
- `positive`, `negative`, and `inconclusive` are scope-specific. Do not collapse `1xH100-surrogate` and `8xH100-leaderboard` evidence into one verdict.
- Treat challenge legality, reproducibility, and counted artifact size as first-class constraints on every frontier update.
