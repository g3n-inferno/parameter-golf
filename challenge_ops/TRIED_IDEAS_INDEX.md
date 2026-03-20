# Tried Ideas Index

Last updated: `2026-03-20`

Use one row per idea family, not one row per run.
Update this file when an idea becomes `already-tried`, changes verdict, or gets a better representative run.

| idea_label | standardized_name | closest_run | result | verdict | notes |
| --- | --- | --- | --- | --- | --- |
| `Naive Baseline` | `naive_baseline_sp1024_9x512_kv4` | `records/track_10min_16mb/2026-03-17_NaiveBaseline` | `val_bpb=1.22436570` on `8xH100-leaderboard` | `baseline / already-tried / positive / track-candidate @ 8xH100-leaderboard` | Public baseline anchor for current record-track comparisons. |
| `Long Context Seq2048` | `seq2048_long_context` | `records/track_10min_16mb/2026-03-18_LongContextSeq2048` | `val_bpb=1.20576485` on `8xH100-leaderboard` | `variant / already-tried / positive / track-candidate @ 8xH100-leaderboard` | Current confirmed repo-best leaderboard-track result. |
| `FP16 Embed + WD3600` | `fp16_tied_embedding_with_warmdown` | `records/track_10min_16mb/2026-03-18_FP16Embed_WD3600` | leaderboard score improved vs naive baseline | `variant / already-tried / positive / track-candidate @ 8xH100-leaderboard` | Keep separate from the weaker `1xH100-surrogate` fp16-only probe. |
| `Sliding Window Eval` | `sliding_window_evaluation_stride64` | `records/track_10min_16mb/2026-03-19_SlidingWindowEval` | `val_bpb=1.19250007` post-quant on `8xH100-leaderboard` | `novel / already-tried / positive / track-candidate @ 8xH100-leaderboard` | Evaluation-only gain; track eval-time budget explicitly. |
| `4-Hour Baseline` | `extended_compute_baseline_sp1024` | `records/track_non_record_16mb/2026-03-18_Quasi10Bfrom50B_SP1024_9x512_KV4_4h_pgut3` | `val_bpb=1.2074` on unlimited compute | `baseline / already-tried / positive / non-record @ non-record-unlimited` | Useful quality reference, not a 10-minute track anchor. |
| `Control 1xH100` | `runpod_1xh100_control_anchor` | `experiments/ledger.csv#run_id=ablate_control_1xh100_1024` | `mixed 1xH100-surrogate evidence: adopted Runpod 1xH100 control anchor val_bpb=1.32157507 vs clean Runpod reruns at 1.33518228, 1.34849063, and 1.35280815 even after stable-profile gating` | `variant / already-tried / inconclusive / non-record @ 1xH100-surrogate` | Use `Runpod 1xH100 control anchor` as the human-facing family name. Legacy `_local_` run IDs and filenames remain compatibility aliases only, the stable-profile rerun still failed, and no surrogate ablation should run until the control-family root cause is understood. |
| `LR Warmdown` | `longer_warmdown_schedule` | `experiments/ledger.csv#run_id=ablate_lr_warmdown_1xh100_20260320_runpod` | `mixed 1xH100-surrogate evidence: earlier surrogate val_bpb=1.31909196 vs Runpod rerun val_bpb=1.33058722; clean Runpod control retry was even worse at 1.33518228` | `variant / already-tried / inconclusive / non-record @ 1xH100-surrogate` | The clean remote control retry landed worse than the remote `lr_warmdown` run, so keep `LR Warmdown` inconclusive until the Runpod control path is stable. |
| `FP16 Embed 1xH100 Probe` | `fp16_tied_embedding_1xh100_probe` | `experiments/ledger.csv#run_id=ablate_fp16_embed_1xh100_1024` | `delta_val_bpb=+0.00068214` vs Runpod `1xH100` control anchor | `variant / already-tried / negative / non-record @ 1xH100-surrogate` | The `1xH100-surrogate` probe regressed; do not confuse it with the stronger record-track recipe. |
| `Compound Ctx1536` | `compound_longer_context_1536_probe` | `experiments/ledger.csv#run_id=ablate_compound_ctx1536_1xh100` | `delta_val_bpb=+0.00197885` vs Runpod `1xH100` control anchor | `variant / already-tried / negative / non-record @ 1xH100-surrogate` | Includes a rerun after fixing an initial loader bug; still net negative. |

## Update Rules

- Check this file before calling an idea `novel`.
- If an idea already exists here, extend the existing row unless the new run clearly represents a different mechanism.
- Keep scope in the verdict so `1xH100-surrogate` evidence and leaderboard evidence do not overwrite each other.
- When a new result materially changes understanding, update this file and `challenge_ops/CURRENT_FRONTIER.md` together.
