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
summary JSON, and compares against `experiments/baselines/local_1xh100_baseline_summary.json`.

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
