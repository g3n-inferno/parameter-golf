# Experiment Workflow

This directory holds lightweight local experiment bookkeeping for Parameter Golf work.

## Policy

- Cheap iteration first.
- No blind brute-force seed abuse or unprincipled large sweeps.
- Tokenizer or dataset edits require stronger correctness checks before trusting `val_bpb`.
- Competitive entries belong under `/records`, not only in this ledger.

## Files

- `ledger.csv`: flat experiment ledger for meaningful runs and candidates.

## Scripts

Run from the repo root:

```bash
python scripts/experiments/new_experiment.py --run-id my_run --hardware 1xH100 --track-intent non-record
python scripts/experiments/update_ledger.py --run-id my_run --val-bpb 1.32 --bytes-total 14037860
python scripts/experiments/summarize_candidates.py
```

For the current compact 1xH100 workstream, use:

```bash
bash scripts/experiments/run_1xh100_ablation.sh control
```

That wrapper keeps the baseline command path, refreshes the ledger from the parsed
summary JSON, and compares against
`experiments/baselines/runpod_1xh100_control_anchor_summary.json` by default.
The legacy compatibility file `experiments/baselines/local_1xh100_baseline_summary.json`
is still supported, but it stores the older historical Runpod baseline summary rather than the adopted control-anchor metrics. New wrapper-created ledger rows default to
hardware `Runpod 1xH100 pod`; override `EXPERIMENT_HARDWARE` only for true
local-machine or other remote-host runs.

Each wrapper-created run directory now also records `provenance.json`, which captures:

- pinned git branch and commit
- exact wrapper and `train_gpt.py` hashes
- compare-JSON path and lineage metadata
- dataset shard-count plus manifest hash
- tokenizer hash

If the compare JSON is marked `requires_rebuild_before_ablation=true`, the wrapper
permits `control` rebuilds but refuses non-control surrogate ablations until a new
frozen control anchor exists.

Before a paid `1xH100-surrogate` Runpod run, validate the pod against the
declared stable control profile:

```bash
python scripts/runpod/check_pod_profile.py \
  --pod-id <pod_id> \
  --profile-json challenge_ops/runpod_1xh100_control_profile.json
```

Available named ablations in the current wrapper include:

- `control`
- `fp16_embed`
- `lr_warmdown`
- `compound_ctx1536`
- `byte_aware_loss`
- `easy_to_hard`
- `quality_top_half`
- `shared_depth`
- `shared_depth_stable`

## Runpod Usage Tracking

Use the local Runpod usage tracker when you want an audit trail for challenge-only pod
sessions, initialization time, per-run timing, and billed cost.

Initialize the ledgers once:

```bash
python scripts/runpod/track_challenge_usage.py init
```

Start a challenge session after creating or starting a pod:

```bash
python scripts/runpod/track_challenge_usage.py start-session \
  --session-id h100_20260320_a \
  --pod-id 9p5aq98sa8j6go \
  --purpose "1xH100 parameter-golf ablations"
```

Mark the pod ready once SSH or Jupyter is actually usable:

```bash
python scripts/runpod/track_challenge_usage.py mark-ready --session-id h100_20260320_a
```

Mark individual experiment runs inside that pod session:

```bash
python scripts/runpod/track_challenge_usage.py start-run \
  --session-id h100_20260320_a \
  --run-id byte_aware_loss_1 \
  --experiment-id byte_aware_loss \
  --train-command "bash scripts/experiments/run_1xh100_ablation.sh byte_aware_loss"
```

```bash
python scripts/runpod/track_challenge_usage.py finish-run --run-id byte_aware_loss_1
python scripts/runpod/track_challenge_usage.py finish-session --session-id h100_20260320_a
```

Summarize the current challenge-only totals:

```bash
python scripts/runpod/track_challenge_usage.py report --usage-scope challenge
```

If billing rows are still zero immediately after a run or stop, refresh them once
the Runpod billing API has caught up:

```bash
python scripts/runpod/track_challenge_usage.py refresh-billing --usage-scope challenge
```

For the common one-shot case where the pod is already reachable and you want to track
the whole compute run automatically, use:

```bash
python scripts/runpod/track_challenge_usage.py run-command \
  --session-id h100_20260320_b \
  --pod-id 9p5aq98sa8j6go \
  --run-id byte_aware_loss_2 \
  --experiment-id byte_aware_loss \
  --purpose "1xH100 tracked ablation" \
  -- python scripts/experiments/parse_train_log.py --help
```

That one command:

- starts the session ledger row
- marks the pod ready immediately
- starts the run row
- executes the command
- finishes the run and session
- prints the updated challenge totals

If you need accurate pod initialization time, start the session when the pod start is
requested, then call `mark-ready` only after SSH or Jupyter becomes usable.

Important limitation: Runpod exposes pod billing and account balance, but not which
credit source was consumed. The tracker therefore defaults to:

- `usage_scope=challenge`
- `funding_note="OpenAI Runpod credit allocation ($25, blended balance assumption)"`
- a fixed challenge credit budget of `$25` for local audit reports, independent of the
  current blended Runpod balance

Use `usage_scope` and `funding_note` as your challenge audit layer for OpenAI-credit
compliance.

## Ledger Conventions

Each meaningful run should track at least:

- `run_id`
- `branch`
- `date`
- dataset/tokenizer variant
- core hyperparameters
- hardware
- `val_loss`
- `val_bpb`
- `bytes_model`
- `bytes_code`
- `bytes_total`
- notes
- whether it is intended as `non-record` or `track-candidate`

Keep entries concise and reproducible. The ledger is local workflow support, not a submission artifact.
