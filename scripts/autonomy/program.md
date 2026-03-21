# Parameter Golf Autonomy Program

Use this prompt when Codex is operating in an autoresearch-style loop for this repo.

## Mission

Advance Parameter Golf progress without violating challenge rules, repo guardrails, or the active autonomy policy in `scripts/autonomy/policy.toml`.

## First Step Every Time

1. Read `README.md`.
2. Read `scripts/autonomy/policy.toml`.
3. Run `python scripts/autonomy/controller.py status`.
4. Read `challenge_ops/CURRENT_FRONTIER.md` and `challenge_ops/TRIED_IDEAS_INDEX.md`.

Do not skip the policy check. The policy is the live authority for what Codex may do autonomously.

When a parent agent is supervising a bounded trial, produce a visible no-spend plan before any paid action. The minimum acceptable form is either:

- a dry-run experiment brief via `python scripts/autonomy/controller.py plan-experiment ... --dry-run`, or
- a written brief under `challenge_ops/briefs/`

The supervising agent must be able to inspect that plan from the repo or from your progress message before you spend a paid run.

## Core Operating Rules

- Treat challenge legality, reproducibility, artifact size, and measurement correctness as first-class constraints.
- Do not call an idea `novel` until `challenge_ops/TRIED_IDEAS_INDEX.md` has been checked.
- Do not run a meaningful experiment without first creating a brief through `python scripts/autonomy/controller.py plan-experiment ...`, unless the task is explicitly limited to read-only investigation.
- Before any paid `1xH100` run, emit a visible dry-run `plan-experiment` summary first so the supervising agent can inspect your intended action.
- Before any remote action, verify that a local approval token exists with `python scripts/autonomy/controller.py check-remote-approval --run-id ... --hardware-target ...`.
- If the approval check fails, stop. Do not touch Runpod, do not start the tracker, and do not resume a pod.
- Do not start or resume paid Runpod work unless the policy allows it.
- Never use more than one Runpod pod at a time.
- Never start `8xH100` work unless both the user and the policy explicitly allow it.
- Before any future `8xH100` request, prepare a shortlist of `2` to `4` promising setups and present it to the user first.
- Do not package or recommend a submission unless the policy allows it and the submission preflight passes.
- Do not run blind sweeps or seed fishing.

## Preferred Workflow

1. Read current repo state and frontier memory.
2. Pick one bounded next action.
3. Write an experiment brief with `controller.py plan-experiment`.
4. Run the experiment only if the policy allows it.
5. Immediately record the result with `controller.py record-result`.
6. When enough evidence accumulates for leaderboard-scale consideration, create a shortlist with `controller.py draft-shortlist`.
7. If the result materially changes understanding, update `challenge_ops/CURRENT_FRONTIER.md` and `challenge_ops/TRIED_IDEAS_INDEX.md`.
8. End nontrivial tasks with the standard Codex handoff summary from `challenge_ops/templates/codex_handoff.md`.

## Remote Runs

When remote work is in scope:

- Use the repo's Runpod scripts and tracking workflow.
- Run `controller.py check-remote-approval` successfully before any remote action.
- Prefer the repo-local `scripts/runpod/track_challenge_usage.py` wrapper over ad hoc commands.
- Prefer `1xH100` or cheaper validation paths before anything leaderboard-scale.
- If a pod is created, confirm the repo is a real checkout before running anything expensive.

## Result Capture

For each meaningful run:

- keep or create the ledger row in `experiments/ledger.csv`
- generate the markdown and JSON result packet under `challenge_ops/results/`
- preserve exact command, dataset/tokenizer variant, hardware, wallclock target, and observed metrics

The helper command is:

```bash
python scripts/autonomy/controller.py record-result ...
```

For leaderboard handoff preparation, use:

```bash
python scripts/autonomy/controller.py draft-shortlist ...
```

## Boundaries

This autonomy program is meant to make Codex disciplined and persistent, not unsupervised in ways that violate your discretion. If the policy says no, stop and report the blocked gate clearly.
