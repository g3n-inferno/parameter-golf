# Experiment Brief

## Identity

- `experiment_id`: `smeargate_bigramhash_mlp3x_warmprobe_20260321`
- `run_id`: `smeargate_bigramhash_mlp3x_warmprobe_20260321_runpod_pair`
- `idea_label`: `Int6 MLP3x + SmearGate + BigramHash + Muon WD + SWA`
- `standardized_name`: `smeargate_bigramhash_mlp3x_muonwd_swa`
- `owner`: `Codex`
- `date`: `2026-03-21`

## Standardized Classification

- `lineage`: `variant`
- `state`: `already-tried`
- `intent`: `non-record`
- `scope`: `1xH100-surrogate`

## Objective

- What is being tested: Run one warmed-second-run 1xH100 surrogate probe of the leaderboard SmearGate/BigramHash/MLP3x family by using a baseline control warm-up first run and the actual model-family probe as the second run on the same fresh official-template pod.
- Why now: The current frontier says warm-state effects are real and future surrogate comparisons should use the warmed second-run protocol rather than mixing fresh-first-run and warmed-second-run results.

## Anchor And Novelty Check

- Closest prior idea or run: `control_path_warm_state_pair_20260321_run2`
- Anchor metric and scope: Current warmed same-pod control anchor on fresh official-template hardware is val_bpb=1.33753867 on control_path_warm_state_pair_20260321_run2; leaderboard 8xH100 family reference is mean val_bpb=1.14582 for the 9L Int6 MLP3x + SmearGate + BigramHash + Muon WD + SWA record.
- Why this is `novel`, `variant`, or `baseline`: This is an already-tried leaderboard family, but it is a new repo-local 1xH100 warmed-second-run surrogate probe of that family under the current reproducibility protocol.
- Check against `challenge_ops/TRIED_IDEAS_INDEX.md`: existing row found for `smeargate_bigramhash_mlp3x_muonwd_swa`; treat this as already represented in repo memory.

## Exact Plan

- Code path: `train_gpt.py`
- Dataset/tokenizer variant: `fineweb10B_sp1024` with `fineweb_1024_bpe.model`
- Hardware target: `Runpod 1xH100 pod`
- Wallclock target: `600s`
- Exact planned command: `run1: baseline control warm-up via bash scripts/experiments/run_baseline_1gpu.sh on repo baseline trainer; run2: overwrite root train_gpt.py with records/track_10min_16mb/2026-03-20_Int6_MLP3x_SmearGate_BigramHash_MuonWD_SWA/train_gpt.py and run bash scripts/experiments/run_baseline_1gpu.sh with NUM_LAYERS=9 MODEL_DIM=512 NUM_HEADS=8 NUM_KV_HEADS=4 MLP_MULT=3 TRAIN_SEQ_LEN=2048 TRAIN_BATCH_TOKENS=786432 MATRIX_LR=0.02 SCALAR_LR=0.02 TIED_EMBED_LR=0.03 MUON_MOMENTUM=0.99 MUON_MOMENTUM_WARMUP_START=0.92 MUON_MOMENTUM_WARMUP_STEPS=1500 WARMDOWN_ITERS=3000 GRAD_CLIP_NORM=0.3 BIGRAM_VOCAB_SIZE=4096 BIGRAM_DIM=128 EVAL_STRIDE=64 SWA_ENABLED=1 SWA_START_FRAC=0.5 SWA_EVERY=50 VAL_LOSS_EVERY=200 MAX_WALLCLOCK_SECONDS=600.`

## Success And Failure Criteria

- Success threshold: The warmed second run completes cleanly with final metrics and lands in a regime competitive enough to compare against the warmed control anchor and other candidate families without obvious infra confounding.
- Failure threshold: The model probe OOMs, fails to finish, or lands in a clearly broken regime that cannot be compared apples to apples.
- What would count as inconclusive: infra failure, missing final metrics, or a confounded setup change

## Reproducibility And Legality

- Eval restrictions reminder: No eval-time downloads, network calls, or training-data access may be required by any resulting artifact claim.
- Artifact size concern: Keep counted artifact bytes under the 16,000,000-byte cap. Current cap: 16000000 bytes.
- Tokenizer/dataset correctness concern: Keep the documented dataset and tokenizer unchanged; no val_bpb proof plan is needed for this run.
- Runpod or cost concern: Use exactly one fresh official-template 1xH100 pod and stop after one warmed pair unless a local bug forces a bounded rerun on the same pod.

## Planned Outputs

- Expected log path: `logs/experiments/**/*_smeargate_bigramhash_mlp3x_warmprobe_20260321_runpod_pair/run.log`
- Expected result markdown path: `C:\Users\g3n_i\Desktop\0. Coding\Projects\parameter-golf\challenge_ops\results\2026-03-21_smeargate_bigramhash_mlp3x_warmprobe_20260321_runpod_pair.result.md`
- Expected result JSON path: `C:\Users\g3n_i\Desktop\0. Coding\Projects\parameter-golf\challenge_ops\results\2026-03-21_smeargate_bigramhash_mlp3x_warmprobe_20260321_runpod_pair.result.json`
- Ledger update plan: use `scripts/autonomy/controller.py record-result ...` after the run to generate the result packet and sync `experiments/ledger.csv`.

## Notes

- Extra context: Collect run1 and run2 logs before stopping the zero-volume pod; do not restart the pod after training until the artifacts are already copied locally.
