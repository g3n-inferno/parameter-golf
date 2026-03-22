# Experiment Brief

- Date: `2026-03-21`
- Owner: `Codex`
- Scope: `smoke-path`
- Idea label: `Shared-depth residual experts`
- Standardized name: `shared_depth_residual_experts_sequence_router_probe`
- Lineage: `novel`
- State: `frontier`
- Objective: validate end-to-end training, eval, export, and int8+zlib roundtrip for late-pass sequence-level residual experts on the existing shared-depth trunk.
- Why now: the user requested a minimal reversible prototype plus local smoke validation before any costlier surrogate run.
- Closest run: `scripts/experiments/run_1xh100_ablation.sh#shared_depth_stable`
- Novelty rationale: `challenge_ops/TRIED_IDEAS_INDEX.md` does not currently represent a shared-trunk late-pass residual-expert family.
- Hardware target: `local RTX 3060 smoke`
- Dataset/tokenizer: synthetic local smoke shards plus a local SentencePiece model only for plumbing validation.
- Planned commands: run `train_gpt.py` three times on the synthetic smoke assets for `shared_depth_stable`, `shared_depth_experts_fixed`, and `shared_depth_experts_router`.
- Success threshold: all three variants finish, `final_int8_zlib_roundtrip` succeeds, expert usage logs appear, and artifact bytes are reported.
- Failure threshold: any variant fails compile, forward, export, or roundtrip, or expert usage logs are absent.
- Inconclusive threshold: runs finish but router usage or collapse cannot be determined from logs plus post-run inspection.
- Constraints: preserve tokenizer/eval structure in code, keep changes minimal and reversible, do not treat smoke `val_bpb` as challenge evidence, and do not use remote compute.
