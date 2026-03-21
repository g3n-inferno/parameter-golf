---
name: parameter-golf-autonomy
description: Use when the user wants autoresearch-style autonomous or semi-autonomous Parameter Golf work in this repository, including policy-gated experiment planning, compliant result capture, repo-local challenge memory updates, and Codex-run research loops.
---

# Parameter Golf Autonomy

Use this skill for repo-local autonomous research work in `parameter-golf`.

## Start Here

1. Read `scripts/autonomy/program.md`.
2. Read `scripts/autonomy/policy.toml`.
3. Run:

```bash
python scripts/autonomy/controller.py status
```

4. Read the current frontier files:
   - `challenge_ops/CURRENT_FRONTIER.md`
   - `challenge_ops/TRIED_IDEAS_INDEX.md`

If another agent is supervising you, create a visible no-spend plan before any paid action. A dry-run `plan-experiment` invocation is sufficient if it makes the intended run path inspectable.

## Required Workflow

- Before any meaningful experiment, create a brief:

```bash
python scripts/autonomy/controller.py plan-experiment ...
```

- Before any paid `1xH100` run, first render that plan in dry-run mode so a supervising agent or user can inspect it:

```bash
python scripts/autonomy/controller.py plan-experiment ... --dry-run
```

- Before any remote action, require a local approval token and verify it with:

```bash
python scripts/autonomy/controller.py check-remote-approval --run-id ... --hardware-target ...
```

- If that check fails, stop immediately and wait for the supervisor or user to grant approval with:

```bash
python scripts/autonomy/controller.py grant-remote-approval ...
```

- After any meaningful run, generate the result packet and sync the ledger:

```bash
python scripts/autonomy/controller.py record-result ...
```

- Use the existing repo wrappers and compliance scripts instead of inventing parallel workflows.
- Keep competitive logic and packaging decisions aligned with the repo README and `challenge_ops`.
- Before any future `8xH100` run, prepare a shortlist of `2` to `4` promising setups with:

```bash
python scripts/autonomy/controller.py draft-shortlist ...
```

- Present that shortlist to the user before asking for an `8xH100` policy change.

## Runpod

- If remote execution is needed, follow the active policy first.
- Use the existing Runpod tracking workflow in `scripts/runpod/track_challenge_usage.py`.
- Never use more than one pod at a time.
- Never start `8xH100` work unless the user and the policy both allow it.
- When the task is specifically about Runpod setup or operation, also use the `runpodctl` skill.

## Dataset And Tokenizer Changes

- Treat dataset or tokenizer changes as exceptional.
- If the active policy requires a proof plan for `val_bpb` correctness, do not proceed without one.

## Submission Safety

- Do not package or recommend a submission unless the policy allows it.
- Use the existing compliance and preflight scripts before calling anything submission-ready.

## Notes

- This skill is intentionally narrow: it helps Codex act like a disciplined Parameter Golf operator, not a free-running brute-force search loop.
