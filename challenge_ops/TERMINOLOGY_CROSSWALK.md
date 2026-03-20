# Terminology Crosswalk

Last updated: `2026-03-20`

Use this file to normalize informal phrasing into the standard terms used in `challenge_ops/`.

## Standard Labels

- `lineage`: `baseline` | `variant` | `novel`
- `state`: `frontier` | `already-tried`
- `result`: `positive` | `negative` | `inconclusive`
- `intent`: `non-record` | `track-candidate`
- `scope`: `smoke-path` | `1xH100-surrogate` | `8xH100-leaderboard` | `non-record-unlimited` | `records-preflight`

## Crosswalk

| Informal wording | Standard term | Meaning in this repo | Nearest repo example |
| --- | --- | --- | --- |
| `naive baseline`, `simple baseline`, `baseline anchor` | `baseline` | Canonical comparison anchor for a scope. | `records/track_10min_16mb/2026-03-17_NaiveBaseline` |
| `control` | `variant` | Same-family rerun, not automatically the adopted anchor. | `ablate_control_1xh100_1024` |
| `leaderboard-informed` | `variant` | Derivative of an already known record-track idea. | `ablate_fp16_embed_1xh100_1024` |
| `balanced scaling probe` | `variant` | Architectural retune inside an existing family unless it adds a new mechanism. | `ablate_compound_ctx1536_1xh100` |
| `weird`, `creative`, `out-of-the-box` | `novel` | New mechanism, eval method, or architecture family. | `Sliding Window Eval` |
| `already tried`, `we ran this`, `logged before` | `already-tried` | At least one meaningful ledger row or `/records` run exists. | `LR Warmdown` |
| `frontier`, `untested`, `needs first real run` | `frontier` | Idea has not yet produced a meaningful logged run in this repo. | Use only before the first ledger or record entry exists. |
| `promising`, `needs rerun`, `bug-fixed rerun`, `not apples-to-apples yet` | `inconclusive` | Evidence is incomplete, confounded, or not yet leaderboard-comparable. | Use when local evidence exists but comparison is not clean. |
| `net negative`, `hurt convergence`, `compresses worse` | `negative` | Worse than the declared anchor for the declared scope. | `compound_ctx1536` local probe |
| `leaderboard relevant`, `record-track`, `SOTA candidate` | `track-candidate` | Plausible for `records/track_10min_16mb`, subject to compliance and rerun checks. | `Long Context Seq2048` |
| `local`, `cheap surrogate`, `1xH100 check` | `1xH100-surrogate` | Local or cheap remote evidence used for iteration, not direct leaderboard proof. | `baseline_sp1024_h100_local_20260319` |
| `full leaderboard rerun`, `8xH100 SXM run` | `8xH100-leaderboard` | Apples-to-apples leaderboard-comparable evidence. | `Long Context Seq2048` |
| `unlimited compute`, `4-hour run` | `non-record-unlimited` | Useful quality signal outside the 10-minute main track. | `4-Hour Baseline` |
| `submission preflight`, `candidate folder check` | `records-preflight` | Packaging and compliance phase rather than a training experiment. | `scripts/submission/preflight_submission.py` |

## Normalization Rules

- Do not use bare `frontier` to mean current best score. In this repo, `frontier` means under-tested idea space.
- Do not call a run `novel` if it is only a scalar retune of a known family.
- Do not call a local `control` run a `baseline` unless the project explicitly adopts it as the anchor.
- Keep `scope` attached to verdicts. A result can be positive on `1xH100-surrogate` and still be unproven on `8xH100-leaderboard`.
- `track-candidate` is not the same as `submission-ready`. Submission readiness belongs in `challenge_ops/SUBMISSION_AUDIT.md`.
