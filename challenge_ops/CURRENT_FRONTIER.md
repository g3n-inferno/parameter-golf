# Current Frontier

Last updated: `2026-03-21`

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
| `Runpod 1xH100 provisional legacy control anchor` | `1xH100-surrogate` | `1.32157507` | Best historical single-GPU control-family metric so far, represented by `ablate_control_1xh100_1024`, but only preserved via ledger-mirrored compare JSON and inferred git lineage; treat it as a provisional legacy anchor until a new frozen anchor is rebuilt. |
| `Runpod 1xH100 rebuilt-control best rerun` | `1xH100-surrogate` | `1.32776835` | Best provenance-hardened same-pod control rerun so far, represented by `ablate_control_1xh100_20260321_runpod_frozen_anchor_b` on reused pod `474jlphqpo5n8x` with pinned base commit `c59338a...` and recorded wrapper/data/tokenizer/compare hashes. |
| `Runpod 1xH100 stable-profile control rerun` | `1xH100-surrogate` | `1.35280815` | Latest clean Runpod `1xH100` control rerun on a profile-matching US `26`-vCPU pod; still materially worse than the provisional legacy anchor and now the strongest non-reproducibility warning signal. |

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
  - Evidence: the provisional legacy `Runpod 1xH100 control anchor` is `ablate_control_1xh100_1024` at `val_bpb=1.32157507`, but its raw log and result packet are not preserved locally and its compare JSON is mirrored from the ledger with inferred commit lineage; provenance-hardened same-pod rebuilds on reused stable-profile pod `474jlphqpo5n8x` then landed at `1.32963305`, `1.32776835`, and `1.33473550` with identical recorded code/dataset/tokenizer/compare hashes, so the control family is better constrained but still not stable enough to resume ablations.
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
- Confirmed: the stable-profile rerun `ablate_control_1xh100_20260320_runpod_stable` completed at `val_bpb=1.35280815`, which is `+0.03123308` worse than the provisional legacy `Runpod 1xH100 control anchor`, `+0.00431752` worse than the earlier non-US low-vCPU rerun, and `+0.02222093` worse than the earlier remote `lr_warmdown` run.
- Confirmed: the stable-profile rerun used a fresh `US-MO-1` H100 pod with `26` vCPUs and passed the declared `challenge_ops/runpod_1xh100_control_profile.json` policy, so the earlier control miss cannot be explained away by the `EUR-NO-2` / `8`-vCPU host alone.
- Confirmed: the provisional legacy anchor `ablate_control_1xh100_1024` is not recoverable as a fully frozen anchor today because its raw log/result packet are absent and its canonical compare JSON is mirrored from `experiments/ledger.csv` with only inferred commit/export lineage.
- Confirmed: the byte drift is not just code drift. The export family changed from `code_bytes=48294` on the provisional legacy anchor to `61795` on later reruns, but the larger same-family change is in `model_int8_zlib_bytes` (`13611740` -> `12878462` -> `12435489`) as the worse reruns stop earlier and compress much smaller.
- Confirmed: three provenance-hardened same-pod control rebuilds on reused pod `474jlphqpo5n8x` shared pinned base commit `c59338a...`, `train_gpt.py` hash `15846ddc...`, dataset manifest hash `c0ebc88d...`, tokenizer hash `4f5e8adb...`, and compare JSON hash `aa400747...`, yet still spread across `val_bpb=1.32776835` to `1.33473550`.
- Inferred: the dominant issue is deeper non-reproducibility in the Runpod `1xH100-surrogate` control path rather than a simple bad-host mismatch, and more paid `1xH100-surrogate` ablations should stay paused because even the provenance-hardened same-pod rebuild did not clear the provisional-legacy `+0.005` recovery gate.

## Most Promising Next Experiment

- Candidate: no paid surrogate ablation yet; if more GPU time is spent, use it only for another control-path diagnosis, not a model change.
- Standardized name: `runpod_1xh100_control_anchor`
- Why:
  - Confirmed the rebuilt control family is now provenance-correct but still not stable enough: same pod, same overlay hashes, and same dataset/tokenizer hashes still produced `1.32963305`, `1.32776835`, and `1.33473550`.
  - Confirmed the best rebuilt rerun missed the provisional-legacy `+0.005` recovery gate by `+0.00119328`, and the third rerun widened again instead of tightening.
  - The highest-value next move is therefore still control-path diagnosis, not a paid model ablation.
- Guardrails before any expensive run:
  - keep dataset and tokenizer unchanged
  - keep result reporting apples to apples
  - predeclare anchor, scope, and success threshold in an experiment brief
  - use one pod and one operator thread only; do not allow parallel agents to touch Runpod
  - verify the pod still has a real repo checkout after start or resume; if not, reclone before any dataset or training step
  - stop after a grounded infra failure rather than spending more paid ablation time on an unstable pod
  - do not resume paid `1xH100-surrogate` ablations until a control family with the new provenance surface repeatedly recovers near the provisional legacy `ablate_control_1xh100_1024`
  - prefer restarting a prior matching pod first, but treat repeated host-placement failures as an ops fact rather than a reason to lower the control-profile bar
  - run submission and artifact checks before claiming record relevance

## Artifact Budget View

Artifact cap: `16000000` bytes

| Run | Scope | Counted total bytes | Headroom |
| --- | --- | ---: | ---: |
| `Naive Baseline` | `8xH100-leaderboard` | `15863489` | `136511` |
| `Long Context Seq2048 v2` | `8xH100-leaderboard` | `15867270` | `132730` |
| `Sliding Window Eval` | `8xH100-leaderboard` | `15874829` | `125171` |
| `runpod_1xh100_control_anchor_summary` | `1xH100-surrogate` | `14004564` | `1995436` |
| `ablate_control_1xh100_20260321_runpod_frozen_anchor_a` | `1xH100-surrogate` | `13549048` | `2450952` |
| `ablate_control_1xh100_20260321_runpod_frozen_anchor_b` | `1xH100-surrogate` | `13687204` | `2312796` |
| `ablate_control_1xh100_20260321_runpod_frozen_anchor_c` | `1xH100-surrogate` | `13772166` | `2227834` |
| `ablate_lr_warmdown_1xh100_1024` | `1xH100-surrogate` | `12455545` | `3544455` |
| `ablate_lr_warmdown_1xh100_20260320_runpod` | `1xH100-surrogate` | `12053652` | `3946348` |
| `ablate_control_1xh100_20260320_runpod_retry2` | `1xH100-surrogate` | `13673535` | `2326465` |
| `ablate_control_1xh100_20260320_runpod_stabilize` | `1xH100-surrogate` | `12940257` | `3059743` |
| `ablate_control_1xh100_20260320_runpod_stable` | `1xH100-surrogate` | `12497284` | `3502716` |

## Terminology Reminders

- `frontier` means untested or under-tested idea, not current SOTA.
- `track-candidate` means plausible for `records/track_10min_16mb`, not automatically submission-ready.
- `already-tried` starts at the first meaningful ledger row or `/records` evidence.
- `positive`, `negative`, and `inconclusive` are scope-specific. Do not collapse `1xH100-surrogate` and `8xH100-leaderboard` evidence into one verdict.
- Treat challenge legality, reproducibility, and counted artifact size as first-class constraints on every frontier update.
- Use `Runpod 1xH100 provisional legacy control anchor` for `ablate_control_1xh100_1024` until a new frozen single-GPU remote control family is rebuilt. Keep legacy `_local_` filenames and run IDs only as compatibility aliases.
