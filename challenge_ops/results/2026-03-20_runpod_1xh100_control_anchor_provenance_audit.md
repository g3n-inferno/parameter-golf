# Runpod 1xH100 Control Anchor Provenance Audit

## Scope

- Focus: `ablate_control_1xh100_1024` and the current canonical compare file `experiments/baselines/runpod_1xh100_control_anchor_summary.json`
- Goal: determine whether the current `Runpod 1xH100 control anchor` is a recoverable frozen anchor or only a provisional legacy anchor

## Confirmed Findings

- `ablate_control_1xh100_1024` first appears in git history at commit `ac7e33ddcb84253c3ed713668785c3b598c8259b`, where `experiments/ledger.csv` records `val_bpb=1.32157507`, `code_bytes=48294`, and `stop_step=1506`.
- The canonical compare file `experiments/baselines/runpod_1xh100_control_anchor_summary.json` does not point to a raw local log; its `log_path` states `metrics mirrored from experiments/ledger.csv run_id=ablate_control_1xh100_1024`.
- No local raw run log or result packet for `ablate_control_1xh100_1024` was found under `logs/` or `challenge_ops/results/`.
- Later clean Runpod reruns used larger export families: `code_bytes=61795` at commits `c157a6ff2c32395465e39ba6a387364bcf8c2c99`, `90effbae28001f2356b5638fbde9812c0d50f700`, and `bc75d7b0c350a41af25131232854833340265e86`.
- The later reruns preserved the same declared dataset path, tokenizer path, shard count, and control hyperparameters in their logs.
- The same-family byte drift is dominated by `model_int8_zlib_bytes`, not by code alone:
  - `ablate_control_1xh100_1024`: `13956270`
  - `ablate_control_1xh100_20260320_runpod_retry2`: `13611740`
  - `ablate_control_1xh100_20260320_runpod_stabilize`: `12878462`
  - `ablate_control_1xh100_20260320_runpod_stable`: `12435489`

## Inferred Conclusions

- `ablate_control_1xh100_1024` is not recoverable today as a frozen control anchor because its raw packet/log provenance is missing and its source commit is only inferred from git history.
- Host variability was a real confounder, but it is not the sole explanation. Commit/export drift and missing compare-target provenance are also material risks.
- The repo should treat `ablate_control_1xh100_1024` as a provisional legacy anchor in memory and rebuild a new frozen control anchor before more `1xH100-surrogate` ablations.

## Recommended Next Step

- Rebuild one new frozen `Runpod 1xH100 control anchor` under the provenance-hardened workflow: pinned commit, pinned wrapper path, compare-JSON lineage capture, dataset manifest capture, tokenizer hash capture, and preserved raw log plus result packet.
