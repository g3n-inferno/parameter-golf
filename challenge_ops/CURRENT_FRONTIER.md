# Current Frontier

Last updated: `2026-03-21`

This file is the Project GPT and Codex quick-read memory for the current repo frontier.
Use it with `experiments/ledger.csv`, `/records`, and `challenge_ops/TRIED_IDEAS_INDEX.md`.

## Best Known Result

- Confirmed repo-best leaderboard-track result: `10L Int5-MLP + BigramHash(10240) + SWA(frac=0.4) + WD=0.04`
  - Source: `records/track_10min_16mb/2026-03-20_10L_Int5MLP_MuonWD04_SWA50/README.md`
  - Exact reported metric: `mean val_bpb=1.14276` across `3` seeds
  - Artifact size: `15900000` total bytes from `submission.json`
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
| `10L Int5-MLP + BigramHash(10240) + SWA(frac=0.4) + WD=0.04` | `8xH100-leaderboard` | `1.14276` | Current upstream repo-best leaderboard anchor; sliding-window eval plus mixed int5/int6 quantization, bigram-hash context, and SWA. |
| `Naive Baseline` | `8xH100-leaderboard` | `1.22436570` | Public leaderboard baseline and record-track comparison anchor. |
| `Runpod 1xH100 provisional legacy control anchor` | `1xH100-surrogate` | `1.32157507` | Best historical single-GPU control-family metric so far, represented by `ablate_control_1xh100_1024`, but only preserved via ledger-mirrored compare JSON and inferred git lineage; treat it as a provisional legacy anchor until a new frozen anchor is rebuilt. |
| `Runpod 1xH100 rebuilt-control best rerun` | `1xH100-surrogate` | `1.32776835` | Best provenance-hardened same-pod control rerun so far, represented by `ablate_control_1xh100_20260321_runpod_frozen_anchor_b` on reused pod `474jlphqpo5n8x` with pinned base commit `c59338a...` and recorded wrapper/data/tokenizer/compare hashes. |
| `Runpod 1xH100 fresh same-host warm-state pair best` | `1xH100-surrogate` | `1.33753867` | Second run of the paired warm-state control test on fresh official-template pod `v16rndtmqt47dq`; same host fingerprint as run 1, `+25` steps and `-9.37ms` `step_avg_ms` relative to the first run, but still not down to the rebuilt same-pod `1.3278-1.3347` range. |
| `Runpod 1xH100 fresh official-template control rerun` | `1xH100-surrogate` | `1.35283929` | Fresh official-template `US-MO-1` H100 rerun on new pod `vhrzxwizzi276z`; after bounded checkout recovery from the stub template, it matched the earlier clean stable-profile control regime within `0.00003114` `val_bpb`. |

## Known Good Ideas

- `long_context_seq2048`
  - Standardized name: `seq2048_long_context`
  - Verdict: `variant / already-tried / positive / track-candidate @ 8xH100-leaderboard`
  - Evidence: still a positive leaderboard-track direction, but no longer the repo-best result after the upstream record additions.
- `fp16_embed_warmdown`
  - Standardized name: `fp16_tied_embedding_with_warmdown`
  - Verdict: `variant / already-tried / positive / track-candidate @ 8xH100-leaderboard`
  - Evidence: `records/track_10min_16mb/2026-03-18_FP16Embed_WD3600`.
- `sliding_window_eval`
  - Standardized name: `sliding_window_evaluation_stride64`
  - Verdict: `novel / already-tried / positive / track-candidate @ 8xH100-leaderboard`
  - Evidence: `records/track_10min_16mb/2026-03-19_SlidingWindowEval`.
- `mixed_int5_int6_quantization`
  - Standardized name: `mixed_int5_int6_quantization_with_bigramhash_swa`
  - Verdict: `variant / already-tried / positive / track-candidate @ 8xH100-leaderboard`
  - Evidence: current repo-best `records/track_10min_16mb/2026-03-20_10L_Int5MLP_MuonWD04_SWA50`.
- `smeargate_bigramhash_mlp3x`
  - Standardized name: `smeargate_bigramhash_mlp3x_muonwd_swa`
  - Verdict: `novel / already-tried / positive / track-candidate @ 8xH100-leaderboard`
  - Evidence: `records/track_10min_16mb/2026-03-20_Int6_MLP3x_SmearGate_BigramHash_MuonWD_SWA`.
- `int6_qat_sliding_window_eval`
  - Standardized name: `int6_qat_mlp3x_sliding_window_eval`
  - Verdict: `variant / already-tried / positive / track-candidate @ 8xH100-leaderboard`
  - Evidence: `records/track_10min_16mb/2026-03-19_MLP3x_QAT_Int6_SlidingWindow`.

## Known Mixed Or Inconclusive Ideas

- `control_1xh100`
  - Standardized name: `runpod_1xh100_control_anchor`
  - Verdict: `variant / already-tried / inconclusive / non-record @ 1xH100-surrogate`
  - Evidence: the provisional legacy `Runpod 1xH100 control anchor` is `ablate_control_1xh100_1024` at `val_bpb=1.32157507`, but its raw log and result packet are not preserved locally and its compare JSON is mirrored from the ledger with inferred commit lineage; provenance-hardened same-pod rebuilds on reused stable-profile pod `474jlphqpo5n8x` then landed at `1.32963305`, `1.32776835`, and `1.33473550` with identical recorded code/dataset/tokenizer/compare hashes, while two clean fresh official-template US `26`-vCPU runs on new pods landed at `1.34888151` and `1.35283929`, reinforcing a stable fresh-pod regime near `1.3528` rather than a recovery toward the rebuilt same-pod best.
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
- `smeargate_bigramhash_mlp3x_1xh100_probe`
  - Standardized name: `smeargate_bigramhash_mlp3x_muonwd_swa`
  - Verdict: `novel / already-tried / negative / non-record @ 1xH100-surrogate`
  - Evidence: warmed second-run surrogate `smeargate_bigramhash_mlp3x_warmprobe_20260321_run2_model` on fresh official-template pod `aagwbrm1z1rrej` finished at `val_bpb=1.49761060`, exceeded the artifact cap at `16290010` bytes, and spent `1220523ms` in final sliding-window eval after a same-pod warm-up control at `1.34956718`.

## Biggest Bottleneck

- Confirmed: `1xH100-surrogate` reproducibility is now a bottleneck, because the strongest earlier `lr_warmdown` win did not reproduce on a real Runpod H100 SXM rerun.
- Confirmed: the stable-profile rerun `ablate_control_1xh100_20260320_runpod_stable` completed at `val_bpb=1.35280815`, which is `+0.03123308` worse than the provisional legacy `Runpod 1xH100 control anchor`, `+0.00431752` worse than the earlier non-US low-vCPU rerun, and `+0.02222093` worse than the earlier remote `lr_warmdown` run.
- Confirmed: the stable-profile rerun used a fresh `US-MO-1` H100 pod with `26` vCPUs and passed the declared `challenge_ops/runpod_1xh100_control_profile.json` policy, so the earlier control miss cannot be explained away by the `EUR-NO-2` / `8`-vCPU host alone.
- Confirmed: the fresh official-template control rerun `control_path_diagnosis_20260321_fresh_template_runpod` on new pod `vhrzxwizzi276z` also passed the declared `US-MO-1` `26`-vCPU profile, recovered the stub template checkout to exact local `main` commit `82189d277df1191bdc7211d0783d6b7718548cd4` in `3.704s`, and finished at `val_bpb=1.35283929`, `bytes_total=12808876`, and `stop_step=1107`.
- Confirmed: the fresh official-template control rerun differs from `ablate_control_1xh100_20260320_runpod_stable` by only `+0.00003114` `val_bpb`, which is strong evidence that the clean fresh-pod control path is reproducibly in the `~1.3528` regime.
- Confirmed: the earlier fresh official-template run `baseline_sp1024_1xh100_20260320_integrated_main` at `val_bpb=1.34888151` is not perfectly apples to apples with the later control reruns, because its exact training command did not set `VAL_LOSS_EVERY=200`, while the reused same-pod rebuild family and `control_path_diagnosis_20260321_fresh_template_runpod` all did.
- Confirmed: the paired warm-state control test on fresh official-template pod `v16rndtmqt47dq` produced `control_path_warm_state_pair_20260321_run1` at `val_bpb=1.33964300`, `stop_step=1258`, and `control_path_warm_state_pair_20260321_run2` at `val_bpb=1.33753867`, `stop_step=1283`, with identical recorded code/dataset/tokenizer hashes and identical `host_fingerprint_sha256=c8d9064377e5b6e6e15e7fb44a2946b754c2e26ad0c2e5aec5f9e5dcbb42592e`.
- Confirmed: on that same unchanged pod/container, run 2 improved run 1 by `0.00210433` `val_bpb`, reached `25` additional steps under the same `600s` cap, and reduced `step_avg_ms` by `9.37`, which is direct evidence that warm-state effects matter on the current `1xH100-surrogate` path.
- Confirmed: the direct warmed second-run `1xH100-surrogate` of the leaderboard `Int6 MLP3x + SmearGate + BigramHash + OrthoInit + Muon WD + SWA` family (`smeargate_bigramhash_mlp3x_warmprobe_20260321_run2_model`) was decisively poor on the current control path: `val_bpb=1.49761060`, `stop_step=968`, `step_avg_ms=620.04`, `final_eval_time_ms=1220523`, and counted `total_int8_zlib_bytes=16290010`, which is `290010` bytes over the challenge cap.
- Confirmed: relative to the immediate warm-up control on the same pod (`smeargate_bigramhash_mlp3x_warmprobe_20260321_run1_control` at `1.34956718`), that warmed SmearGate probe regressed by `+0.14804342` `val_bpb` while also taking `163` fewer optimizer steps under the same `600s` cap.
- Confirmed: the provisional legacy anchor `ablate_control_1xh100_1024` is not recoverable as a fully frozen anchor today because its raw log/result packet are absent and its canonical compare JSON is mirrored from `experiments/ledger.csv` with only inferred commit/export lineage.
- Confirmed: the byte drift is not just code drift. The export family changed from `code_bytes=48294` on the provisional legacy anchor to `61795` on later reruns, but the larger same-family change is in `model_int8_zlib_bytes` (`13611740` -> `12878462` -> `12435489`) as the worse reruns stop earlier and compress much smaller.
- Confirmed: three provenance-hardened same-pod control rebuilds on reused pod `474jlphqpo5n8x` shared pinned base commit `c59338a...`, `train_gpt.py` hash `15846ddc...`, dataset manifest hash `c0ebc88d...`, tokenizer hash `4f5e8adb...`, and compare JSON hash `aa400747...`, yet still spread across `val_bpb=1.32776835` to `1.33473550`.
- Confirmed: a fresh official-template H100 baseline reproduction on pod `lgprpetuw79pk9` using the exact local integrated `main` commit `ea0df59713d6288526ab88ee1f316692da188356` via a transferred git bundle completed under the default `600s` cap at `val_bpb=1.34888151`, `bytes_total=12841006`, and `stop_step=1136`.
- Confirmed: upstream moved the leaderboard frontier substantially through new record folders, but those additions are mostly new record recipes and README updates, not a proven fix to the fork-local `1xH100-surrogate` instability path.
- Inferred: after accounting for the `VAL_LOSS_EVERY` mismatch between the two fresh official-template runs, the strongest remaining concrete confounder in stored evidence is warm reused-container state on pod `474jlphqpo5n8x`, because the reused rebuild family and the fresh-template rerun otherwise share the same recorded code hash, dataset manifest hash, tokenizer hash, wrapper hash, GPU class, and pod control profile.
- Inferred: warm-state effects are now confirmed as one real contributor to the control-family spread, but they are not the whole story, because the best same-host second run on fresh pod `v16rndtmqt47dq` only reached `1.33753867`, still above the rebuilt same-pod best `1.32776835`.
- Inferred: the older assumption of a single clean fresh-pod regime near `~1.3528` is too narrow; fresh official-template first-run behavior now spans at least `1.33964300` to `1.35283929` under the currently recorded surfaces, so future surrogate experiments should preserve host fingerprints and same-pod ordering explicitly.

## Most Promising Next Experiment

- Candidate: the next paid model probe should be a simpler warmed-second-run surrogate with legal artifact headroom, starting with the leaderboard-informed `FP16 Embed + WD3600` family rather than repeating the direct SmearGate/BigramHash/MLP3x port unchanged.
- Standardized name: `fp16_tied_embedding_with_warmdown`
- Why:
  - Confirmed the paired same-pod control test moved the second run from `1.33964300` to `1.33753867` under identical recorded surfaces, so future `1xH100-surrogate` comparisons should preserve warmed same-pod ordering explicitly.
  - Confirmed the direct warmed port of the SmearGate/BigramHash/MLP3x leaderboard family was far off-regime on `1xH100-surrogate`, both in quality (`1.49761060`) and legality (`16290010` counted bytes).
  - The highest-value next move is therefore not another repeat of that family unchanged. If GPU time is spent again, it should be on a warmed same-pod surrogate with lower artifact risk and lower eval-time burden.
- Guardrails before any expensive run:
  - keep dataset and tokenizer unchanged
  - keep result reporting apples to apples
  - predeclare anchor, scope, and success threshold in an experiment brief
  - preserve the paired same-pod ordering explicitly whenever a warmed second-run result is compared to another warmed second-run result
  - use one pod and one operator thread only; do not allow parallel agents to touch Runpod
  - verify the pod still has a real repo checkout after start or resume; if not, reclone before any dataset or training step
  - stop after a grounded infra failure rather than spending more paid ablation time on an unstable pod
  - do not compare a warmed same-pod second run directly against an earlier fresh-first-run result without calling out the ordering difference
  - treat further pure control reruns without new instrumentation as low-value confirmation, not frontier progress
  - do not rerun the direct SmearGate/BigramHash/MLP3x port unchanged on `1xH100` unless a concrete size or eval-cost confounder is removed first
  - run submission and artifact checks before claiming record relevance

## Artifact Budget View

Artifact cap: `16000000` bytes

| Run | Scope | Counted total bytes | Headroom |
| --- | --- | ---: | ---: |
| `10L Int5-MLP + BigramHash(10240) + SWA(frac=0.4) + WD=0.04` | `8xH100-leaderboard` | `15900000` | `100000` |
| `Int6 MLP3x + SmearGate + BigramHash + OrthoInit + Muon WD + SWA` | `8xH100-leaderboard` | `15862650` | `137350` |
| `11L MLP3x + WD=0.04 + Int6 QAT + zstd-22 + Sliding Window Eval` | `8xH100-leaderboard` | `15427455` | `572545` |
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
| `control_path_warm_state_pair_20260321_run1` | `1xH100-surrogate` | `13344164` | `2655836` |
| `control_path_warm_state_pair_20260321_run2` | `1xH100-surrogate` | `13302509` | `2697491` |
| `control_path_diagnosis_20260321_fresh_template_runpod` | `1xH100-surrogate` | `12808876` | `3191124` |
| `smeargate_bigramhash_mlp3x_warmprobe_20260321_run1_control` | `1xH100-surrogate` | `12843418` | `3156582` |
| `smeargate_bigramhash_mlp3x_warmprobe_20260321_run2_model` | `1xH100-surrogate` | `16290010` | `-290010` |

## Terminology Reminders

- `frontier` means untested or under-tested idea, not current SOTA.
- `track-candidate` means plausible for `records/track_10min_16mb`, not automatically submission-ready.
- `already-tried` starts at the first meaningful ledger row or `/records` evidence.
- `positive`, `negative`, and `inconclusive` are scope-specific. Do not collapse `1xH100-surrogate` and `8xH100-leaderboard` evidence into one verdict.
- Treat challenge legality, reproducibility, and counted artifact size as first-class constraints on every frontier update.
- Use `Runpod 1xH100 provisional legacy control anchor` for `ablate_control_1xh100_1024` until a new frozen single-GPU remote control family is rebuilt. Keep legacy `_local_` filenames and run IDs only as compatibility aliases.
