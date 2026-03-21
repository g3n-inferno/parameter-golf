#!/usr/bin/env python3
"""Policy-aware controller for Parameter Golf autonomous workflows."""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
import tomllib
from dataclasses import dataclass
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_POLICY_PATH = ROOT / "scripts" / "autonomy" / "policy.toml"


def repo_path(relative_path: str) -> Path:
    return (ROOT / relative_path).resolve()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_toml(path: Path) -> dict[str, Any]:
    return tomllib.loads(read_text(path))


def run_python_script(script_path: Path, args: list[str], dry_run: bool) -> None:
    cmd = [sys.executable, str(script_path), *args]
    if dry_run:
        print("dry_run_command=" + " ".join(cmd))
        return
    subprocess.run(cmd, cwd=ROOT, check=True)


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_tried_ideas(path: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    lines = read_text(path).splitlines()
    for line in lines:
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        if "---" in stripped or "idea_label" in stripped:
            continue
        parts = [part.strip() for part in stripped.strip("|").split("|")]
        if len(parts) < 6:
            continue
        rows.append(
            {
                "idea_label": parts[0].strip("`"),
                "standardized_name": parts[1].strip("`"),
                "closest_run": parts[2].strip("`"),
                "result": parts[3].strip("`"),
                "verdict": parts[4].strip("`"),
                "notes": parts[5].strip("`"),
            }
        )
    return rows


def parse_frontier_summary(path: Path) -> dict[str, str]:
    summary = {
        "best_result_label": "",
        "best_result_metric": "",
        "biggest_bottleneck": "",
        "next_experiment": "",
    }
    lines = read_text(path).splitlines()
    section = ""
    for idx, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("## "):
            section = stripped[3:]
            continue
        if section == "Best Known Result" and stripped.startswith("- Confirmed repo-best leaderboard-track result:"):
            summary["best_result_label"] = stripped.split(":", 1)[1].strip()
        elif section == "Best Known Result" and stripped.startswith("- Exact reported metric:"):
            summary["best_result_metric"] = stripped.split(":", 1)[1].strip()
        elif section == "Biggest Bottleneck" and stripped.startswith("- Confirmed:") and not summary["biggest_bottleneck"]:
            summary["biggest_bottleneck"] = stripped[2:].strip()
        elif section == "Most Promising Next Experiment" and stripped.startswith("- Candidate:"):
            summary["next_experiment"] = stripped.split(":", 1)[1].strip()
        elif idx > 400:
            break
    return summary


@dataclass
class Policy:
    path: Path
    raw: dict[str, Any]

    @property
    def defaults(self) -> dict[str, Any]:
        return self.raw.get("defaults", {})

    @property
    def permissions(self) -> dict[str, Any]:
        return self.raw.get("permissions", {})

    @property
    def guards(self) -> dict[str, Any]:
        return self.raw.get("guards", {})

    @property
    def paths(self) -> dict[str, Any]:
        return self.raw.get("paths", {})

    def path_value(self, key: str) -> Path:
        value = self.paths.get(key)
        if not value:
            raise KeyError(f"policy paths.{key} is not set")
        return repo_path(value)


def load_policy(path: Path) -> Policy:
    return Policy(path=path.resolve(), raw=load_toml(path))


def approval_dir(policy: Policy) -> Path:
    return policy.path_value("approvals_dir")


def active_remote_approvals(policy: Policy) -> list[dict[str, Any]]:
    directory = approval_dir(policy)
    if not directory.exists():
        return []
    approvals: list[dict[str, Any]] = []
    for path in sorted(directory.glob("*.json")):
        try:
            payload = read_json(path)
        except Exception:
            continue
        if payload.get("kind") != "remote_runpod":
            continue
        if not bool(payload.get("active", False)):
            continue
        payload["_path"] = str(path.resolve())
        approvals.append(payload)
    return approvals


def find_existing_idea(rows: list[dict[str, str]], idea_label: str, standardized_name: str) -> dict[str, str] | None:
    for row in rows:
        if row["standardized_name"] == standardized_name or row["idea_label"] == idea_label:
            return row
    return None


def mentions_runpod(text: str) -> bool:
    return "runpod" in text.lower()


def mentions_8xh100(text: str) -> bool:
    normalized = text.lower().replace(" ", "")
    return "8xh100" in normalized


def ledger_has_run_id(path: Path, run_id: str) -> bool:
    return any(row.get("run_id") == run_id for row in read_csv_rows(path))


def policy_default(policy: Policy, key: str, fallback: str = "") -> str:
    value = policy.defaults.get(key, fallback)
    return fallback if value is None else str(value)


def require_policy_gate(checks: list[str], allowed: bool, message: str) -> None:
    if not allowed:
        checks.append(message)


def build_status_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser("status", help="Summarize repo autonomy state and policy.")
    parser.add_argument("--policy", type=Path, default=DEFAULT_POLICY_PATH)
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    parser.set_defaults(func=command_status)


def build_plan_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser("plan-experiment", help="Check policy gates and write an experiment brief.")
    parser.add_argument("--policy", type=Path, default=DEFAULT_POLICY_PATH)
    parser.add_argument("--experiment-id", required=True)
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--idea-label", required=True)
    parser.add_argument("--standardized-name", required=True)
    parser.add_argument("--owner", default=None)
    parser.add_argument("--date", default=date.today().isoformat())
    parser.add_argument("--lineage", required=True, choices=["baseline", "variant", "novel"])
    parser.add_argument("--state", required=True, choices=["frontier", "already-tried"])
    parser.add_argument("--intent", default=None, choices=["non-record", "track-candidate"])
    parser.add_argument(
        "--scope",
        default=None,
        choices=[
            "smoke-path",
            "1xH100-surrogate",
            "8xH100-leaderboard",
            "non-record-unlimited",
            "records-preflight",
        ],
    )
    parser.add_argument("--objective", required=True)
    parser.add_argument("--why-now", required=True)
    parser.add_argument("--closest-run", required=True)
    parser.add_argument("--anchor-metric", required=True)
    parser.add_argument("--novelty-rationale", required=True)
    parser.add_argument("--code-path", default=None)
    parser.add_argument("--dataset-variant", default=None)
    parser.add_argument("--tokenizer-variant", default=None)
    parser.add_argument("--hardware-target", default=None)
    parser.add_argument("--wallclock-target", default=None)
    parser.add_argument("--planned-command", required=True)
    parser.add_argument("--success-threshold", required=True)
    parser.add_argument("--failure-threshold", required=True)
    parser.add_argument("--inconclusive-threshold", default="infra failure, missing final metrics, or a confounded setup change")
    parser.add_argument("--paid-run", action="store_true")
    parser.add_argument("--pod-count", type=int, default=0)
    parser.add_argument("--proof-plan", default="")
    parser.add_argument("--artifact-size-concern", default="Keep counted artifact bytes under the 16,000,000-byte cap.")
    parser.add_argument(
        "--eval-restrictions-reminder",
        default="No eval-time downloads, network calls, or training-data access may be required by any resulting artifact claim.",
    )
    parser.add_argument("--runpod-cost-concern", default="")
    parser.add_argument("--extra-notes", default="")
    parser.add_argument("--brief-path", type=Path, default=None)
    parser.add_argument("--dry-run", action="store_true")
    parser.set_defaults(func=command_plan_experiment)


def build_record_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser("record-result", help="Generate result packets and sync experiments/ledger.csv.")
    parser.add_argument("--policy", type=Path, default=DEFAULT_POLICY_PATH)
    parser.add_argument("--log-path", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--experiment-id", required=True)
    parser.add_argument("--idea-label", required=True)
    parser.add_argument("--standardized-name", required=True)
    parser.add_argument("--lineage", required=True, choices=["baseline", "variant", "novel"])
    parser.add_argument("--state", required=True, choices=["frontier", "already-tried"])
    parser.add_argument("--result", required=True, choices=["positive", "negative", "inconclusive"])
    parser.add_argument("--track-intent", default=None, choices=["non-record", "track-candidate"])
    parser.add_argument(
        "--scope",
        required=True,
        choices=[
            "smoke-path",
            "1xH100-surrogate",
            "8xH100-leaderboard",
            "non-record-unlimited",
            "records-preflight",
        ],
    )
    parser.add_argument("--date", default=date.today().isoformat())
    parser.add_argument("--code-path", default=None)
    parser.add_argument("--dataset-variant", default=None)
    parser.add_argument("--tokenizer-variant", default=None)
    parser.add_argument("--hardware", default=None)
    parser.add_argument("--wallclock-target", default=None)
    parser.add_argument("--core-hparams", required=True)
    parser.add_argument("--exact-command", default="")
    parser.add_argument("--notes", default="")
    parser.add_argument("--compare-json", type=Path, default=None)
    parser.add_argument("--compare-label", default=None)
    parser.add_argument("--confirmed-finding", action="append", default=[])
    parser.add_argument("--inferred-conclusion", action="append", default=[])
    parser.add_argument("--artifact-cap", type=int, default=None)
    parser.add_argument("--dry-run", action="store_true")
    parser.set_defaults(func=command_record_result)


def build_shortlist_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser("draft-shortlist", help="Draft a user review shortlist of promising setups.")
    parser.add_argument("--policy", type=Path, default=DEFAULT_POLICY_PATH)
    parser.add_argument("--shortlist-id", required=True)
    parser.add_argument("--date", default=date.today().isoformat())
    parser.add_argument("--title", default="Promising Setups For 8xH100 Review")
    parser.add_argument("--overview", required=True)
    parser.add_argument(
        "--candidate",
        action="append",
        default=[],
        help="Format: run_id|label|why_promising|recommended_next_step",
    )
    parser.add_argument("--notes", default="")
    parser.add_argument("--dry-run", action="store_true")
    parser.set_defaults(func=command_draft_shortlist)


def build_remote_approval_parsers(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    grant = subparsers.add_parser("grant-remote-approval", help="Grant a local approval token for remote Runpod actions.")
    grant.add_argument("--policy", type=Path, default=DEFAULT_POLICY_PATH)
    grant.add_argument("--approval-id", required=True)
    grant.add_argument("--run-id", default="")
    grant.add_argument("--hardware-target", default="")
    grant.add_argument("--max-paid-runs", type=int, default=1)
    grant.add_argument("--approved-by", default="supervisor")
    grant.add_argument("--notes", default="")
    grant.add_argument("--dry-run", action="store_true")
    grant.set_defaults(func=command_grant_remote_approval)

    check = subparsers.add_parser("check-remote-approval", help="Check for an active local approval token for remote Runpod actions.")
    check.add_argument("--policy", type=Path, default=DEFAULT_POLICY_PATH)
    check.add_argument("--run-id", default="")
    check.add_argument("--hardware-target", default="")
    check.add_argument("--approval-id", default="")
    check.set_defaults(func=command_check_remote_approval)

    revoke = subparsers.add_parser("revoke-remote-approval", help="Revoke a local approval token for remote Runpod actions.")
    revoke.add_argument("--policy", type=Path, default=DEFAULT_POLICY_PATH)
    revoke.add_argument("--approval-id", required=True)
    revoke.add_argument("--revoked-by", default="supervisor")
    revoke.add_argument("--notes", default="")
    revoke.add_argument("--dry-run", action="store_true")
    revoke.set_defaults(func=command_revoke_remote_approval)


def command_status(args: argparse.Namespace) -> int:
    policy = load_policy(args.policy)
    frontier_path = policy.path_value("current_frontier")
    tried_path = policy.path_value("tried_ideas")
    ledger_path = policy.path_value("ledger")

    tried_rows = parse_tried_ideas(tried_path)
    frontier = parse_frontier_summary(frontier_path)
    ledger_rows = read_csv_rows(ledger_path)
    latest_run = ledger_rows[-1] if ledger_rows else {}
    approvals = active_remote_approvals(policy)

    payload = {
        "policy_path": str(policy.path),
        "defaults": policy.defaults,
        "permissions": policy.permissions,
        "guards": policy.guards,
        "active_remote_approvals": approvals,
        "frontier": frontier,
        "tried_idea_count": len(tried_rows),
        "ledger_run_count": len(ledger_rows),
        "latest_ledger_run": latest_run,
    }

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0

    print(f"policy_path={policy.path}")
    print(f"default_scope={policy_default(policy, 'scope')}")
    print(f"default_dataset_variant={policy_default(policy, 'dataset_variant')}")
    print(f"default_tokenizer_variant={policy_default(policy, 'tokenizer_variant')}")
    print(f"allow_remote_runpod={policy.permissions.get('allow_remote_runpod', False)}")
    print(f"allow_paid_runpod={policy.permissions.get('allow_paid_runpod', False)}")
    print(f"allow_8xh100={policy.permissions.get('allow_8xh100', False)}")
    print(f"max_concurrent_pods={policy.permissions.get('max_concurrent_pods', 0)}")
    print(f"require_remote_approval_token={policy.guards.get('require_remote_approval_token', False)}")
    print(f"active_remote_approval_count={len(approvals)}")
    if approvals:
        print(f"active_remote_approval_ids={','.join(str(item.get('approval_id', '')) for item in approvals)}")
    print(f"shortlist_min_candidates={policy.raw.get('promotion', {}).get('min_shortlist_candidates', '')}")
    print(f"shortlist_max_candidates={policy.raw.get('promotion', {}).get('max_shortlist_candidates', '')}")
    print(f"best_result_label={frontier.get('best_result_label', '')}")
    print(f"best_result_metric={frontier.get('best_result_metric', '')}")
    print(f"biggest_bottleneck={frontier.get('biggest_bottleneck', '')}")
    print(f"next_experiment={frontier.get('next_experiment', '')}")
    print(f"tried_idea_count={len(tried_rows)}")
    print(f"ledger_run_count={len(ledger_rows)}")
    if latest_run:
        print(f"latest_run_id={latest_run.get('run_id', '')}")
        print(f"latest_val_bpb={latest_run.get('val_bpb', '')}")
        print(f"latest_hardware={latest_run.get('hardware', '')}")
    return 0


def render_brief(
    *,
    experiment_id: str,
    run_id: str,
    idea_label: str,
    standardized_name: str,
    owner: str,
    run_date: str,
    lineage: str,
    state: str,
    intent: str,
    scope: str,
    objective: str,
    why_now: str,
    closest_run: str,
    anchor_metric: str,
    novelty_rationale: str,
    novelty_check_note: str,
    code_path: str,
    dataset_variant: str,
    tokenizer_variant: str,
    hardware_target: str,
    wallclock_target: str,
    planned_command: str,
    success_threshold: str,
    failure_threshold: str,
    inconclusive_threshold: str,
    eval_restrictions_reminder: str,
    artifact_size_concern: str,
    tokenizer_dataset_concern: str,
    runpod_cost_concern: str,
    expected_log_path: str,
    expected_result_md_path: str,
    expected_result_json_path: str,
    extra_notes: str,
) -> str:
    return "\n".join(
        [
            "# Experiment Brief",
            "",
            "## Identity",
            "",
            f"- `experiment_id`: `{experiment_id}`",
            f"- `run_id`: `{run_id}`",
            f"- `idea_label`: `{idea_label}`",
            f"- `standardized_name`: `{standardized_name}`",
            f"- `owner`: `{owner}`",
            f"- `date`: `{run_date}`",
            "",
            "## Standardized Classification",
            "",
            f"- `lineage`: `{lineage}`",
            f"- `state`: `{state}`",
            f"- `intent`: `{intent}`",
            f"- `scope`: `{scope}`",
            "",
            "## Objective",
            "",
            f"- What is being tested: {objective}",
            f"- Why now: {why_now}",
            "",
            "## Anchor And Novelty Check",
            "",
            f"- Closest prior idea or run: `{closest_run}`",
            f"- Anchor metric and scope: {anchor_metric}",
            f"- Why this is `novel`, `variant`, or `baseline`: {novelty_rationale}",
            f"- Check against `challenge_ops/TRIED_IDEAS_INDEX.md`: {novelty_check_note}",
            "",
            "## Exact Plan",
            "",
            f"- Code path: `{code_path}`",
            f"- Dataset/tokenizer variant: `{dataset_variant}` with `{tokenizer_variant}`",
            f"- Hardware target: `{hardware_target}`",
            f"- Wallclock target: `{wallclock_target}`",
            f"- Exact planned command: `{planned_command}`",
            "",
            "## Success And Failure Criteria",
            "",
            f"- Success threshold: {success_threshold}",
            f"- Failure threshold: {failure_threshold}",
            f"- What would count as inconclusive: {inconclusive_threshold}",
            "",
            "## Reproducibility And Legality",
            "",
            f"- Eval restrictions reminder: {eval_restrictions_reminder}",
            f"- Artifact size concern: {artifact_size_concern}",
            f"- Tokenizer/dataset correctness concern: {tokenizer_dataset_concern}",
            f"- Runpod or cost concern: {runpod_cost_concern}",
            "",
            "## Planned Outputs",
            "",
            f"- Expected log path: `{expected_log_path}`",
            f"- Expected result markdown path: `{expected_result_md_path}`",
            f"- Expected result JSON path: `{expected_result_json_path}`",
            "- Ledger update plan: use `scripts/autonomy/controller.py record-result ...` after the run to generate the result packet and sync `experiments/ledger.csv`.",
            "",
            "## Notes",
            "",
            f"- Extra context: {extra_notes or 'none'}",
            "",
        ]
    )


def command_plan_experiment(args: argparse.Namespace) -> int:
    policy = load_policy(args.policy)
    tried_rows = parse_tried_ideas(policy.path_value("tried_ideas"))

    run_id = args.run_id or args.experiment_id
    owner = args.owner or policy_default(policy, "owner", "Codex")
    intent = args.intent or policy_default(policy, "intent", "non-record")
    scope = args.scope or policy_default(policy, "scope")
    code_path = args.code_path or policy_default(policy, "code_path", "train_gpt.py")
    dataset_variant = args.dataset_variant or policy_default(policy, "dataset_variant")
    tokenizer_variant = args.tokenizer_variant or policy_default(policy, "tokenizer_variant")
    hardware_target = args.hardware_target or policy_default(policy, "hardware", "Runpod 1xH100 pod")
    wallclock_target = args.wallclock_target or policy_default(policy, "wallclock_target", "600s")
    artifact_cap = int(policy.defaults.get("artifact_cap_bytes", 16_000_000))

    checks: list[str] = []
    existing_idea = find_existing_idea(tried_rows, args.idea_label, args.standardized_name)
    require_policy_gate(
        checks,
        not (args.lineage == "novel" and existing_idea is not None),
        (
            "lineage=novel conflicts with TRIED_IDEAS_INDEX.md entry "
            f"({existing_idea['standardized_name']})"
        ),
    )
    require_policy_gate(
        checks,
        not (mentions_runpod(hardware_target) and not policy.permissions.get("allow_remote_runpod", False)),
        "policy blocks remote Runpod work until permissions.allow_remote_runpod=true",
    )
    require_policy_gate(
        checks,
        not (args.paid_run and not policy.permissions.get("allow_paid_runpod", False)),
        "policy blocks paid Runpod runs until permissions.allow_paid_runpod=true",
    )
    require_policy_gate(
        checks,
        not ((scope == "8xH100-leaderboard" or mentions_8xh100(hardware_target)) and not policy.permissions.get("allow_8xh100", False)),
        "policy blocks 8xH100 work until permissions.allow_8xh100=true",
    )
    require_policy_gate(
        checks,
        args.pod_count <= int(policy.permissions.get("max_concurrent_pods", 1)),
        (
            f"requested pod_count={args.pod_count} exceeds "
            f"permissions.max_concurrent_pods={policy.permissions.get('max_concurrent_pods', 1)}"
        ),
    )

    defaults_dataset = policy_default(policy, "dataset_variant")
    defaults_tokenizer = policy_default(policy, "tokenizer_variant")
    changed_data_or_tokenizer = (
        (defaults_dataset and dataset_variant != defaults_dataset)
        or (defaults_tokenizer and tokenizer_variant != defaults_tokenizer)
    )
    if changed_data_or_tokenizer and policy.guards.get("require_val_bpb_proof_for_dataset_or_tokenizer_change", False):
        require_policy_gate(
            checks,
            bool(args.proof_plan.strip()),
            "dataset/tokenizer change requires --proof-plan under the active policy",
        )

    if checks:
        print("policy_check=blocked")
        for issue in checks:
            print(f"blocker={issue}")
        return 1

    novelty_check_note = (
        f"existing row found for `{existing_idea['standardized_name']}`; treat this as already represented in repo memory."
        if existing_idea is not None
        else "no matching idea row found."
    )
    tokenizer_dataset_concern = (
        args.proof_plan.strip()
        if changed_data_or_tokenizer
        else "Keep the documented dataset and tokenizer unchanged; no val_bpb proof plan is needed for this run."
    )
    runpod_cost_concern = args.runpod_cost_concern.strip()
    if not runpod_cost_concern:
        if mentions_runpod(hardware_target):
            runpod_cost_concern = (
                "Use one pod only, maintain the Runpod usage tracker, and stop after an infra failure instead of spending paid time on an uncontrolled retry."
            )
        else:
            runpod_cost_concern = "No Runpod action planned."

    brief_path = args.brief_path.resolve() if args.brief_path else policy.path_value("briefs_dir") / f"{args.date}_{args.experiment_id}.md"
    results_dir = policy.path_value("results_dir")
    expected_log_path = f"logs/experiments/**/*_{run_id}/run.log"
    expected_result_md_path = str((results_dir / f"{args.date}_{run_id}.result.md").resolve())
    expected_result_json_path = str((results_dir / f"{args.date}_{run_id}.result.json").resolve())

    brief_body = render_brief(
        experiment_id=args.experiment_id,
        run_id=run_id,
        idea_label=args.idea_label,
        standardized_name=args.standardized_name,
        owner=owner,
        run_date=args.date,
        lineage=args.lineage,
        state=args.state,
        intent=intent,
        scope=scope,
        objective=args.objective,
        why_now=args.why_now,
        closest_run=args.closest_run,
        anchor_metric=args.anchor_metric,
        novelty_rationale=args.novelty_rationale,
        novelty_check_note=novelty_check_note,
        code_path=code_path,
        dataset_variant=dataset_variant,
        tokenizer_variant=tokenizer_variant,
        hardware_target=hardware_target,
        wallclock_target=wallclock_target,
        planned_command=args.planned_command,
        success_threshold=args.success_threshold,
        failure_threshold=args.failure_threshold,
        inconclusive_threshold=args.inconclusive_threshold,
        eval_restrictions_reminder=args.eval_restrictions_reminder,
        artifact_size_concern=f"{args.artifact_size_concern} Current cap: {artifact_cap} bytes.",
        tokenizer_dataset_concern=tokenizer_dataset_concern,
        runpod_cost_concern=runpod_cost_concern,
        expected_log_path=expected_log_path,
        expected_result_md_path=expected_result_md_path,
        expected_result_json_path=expected_result_json_path,
        extra_notes=args.extra_notes,
    )

    if args.dry_run:
        print(f"dry_run_brief_path={brief_path}")
        print(brief_body)
        return 0

    brief_path.parent.mkdir(parents=True, exist_ok=True)
    brief_path.write_text(brief_body, encoding="utf-8")
    print(f"wrote_brief={brief_path}")
    print(f"run_id={run_id}")
    print(f"scope={scope}")
    print("policy_check=ok")
    return 0


def command_record_result(args: argparse.Namespace) -> int:
    policy = load_policy(args.policy)
    log_path = args.log_path.resolve()
    if not log_path.exists():
        print(f"error: log file not found: {log_path}", file=sys.stderr)
        return 1

    results_dir = policy.path_value("results_dir")
    results_dir.mkdir(parents=True, exist_ok=True)
    result_json_path = results_dir / f"{args.date}_{args.run_id}.result.json"
    result_md_path = results_dir / f"{args.date}_{args.run_id}.result.md"

    dataset_variant = args.dataset_variant or policy_default(policy, "dataset_variant")
    tokenizer_variant = args.tokenizer_variant or policy_default(policy, "tokenizer_variant")
    hardware = args.hardware or policy_default(policy, "hardware", "")
    wallclock_target = args.wallclock_target or policy_default(policy, "wallclock_target", "")
    track_intent = args.track_intent or policy_default(policy, "intent", "non-record")
    code_path = args.code_path or policy_default(policy, "code_path", "train_gpt.py")
    artifact_cap = args.artifact_cap or int(policy.defaults.get("artifact_cap_bytes", 16_000_000))
    compare_json = args.compare_json.resolve() if args.compare_json else None

    ledger_path = policy.path_value("ledger")
    if not ledger_has_run_id(ledger_path, args.run_id):
        create_args = [
            "--run-id",
            args.run_id,
            "--date",
            args.date,
            "--dataset-variant",
            dataset_variant,
            "--tokenizer-variant",
            tokenizer_variant,
            "--core-hparams",
            args.core_hparams,
            "--hardware",
            hardware,
            "--track-intent",
            track_intent,
            "--code-path",
            code_path,
            "--wallclock-target",
            wallclock_target,
            "--notes",
            args.notes,
        ]
        run_python_script(ROOT / "scripts" / "experiments" / "new_experiment.py", create_args, args.dry_run)

    result_args = [
        str(log_path),
        "--run-id",
        args.run_id,
        "--experiment-id",
        args.experiment_id,
        "--idea-label",
        args.idea_label,
        "--standardized-name",
        args.standardized_name,
        "--date",
        args.date,
        "--track-intent",
        track_intent,
        "--scope",
        args.scope,
        "--lineage",
        args.lineage,
        "--state",
        args.state,
        "--result",
        args.result,
        "--code-path",
        code_path,
        "--dataset-variant",
        dataset_variant,
        "--tokenizer-variant",
        tokenizer_variant,
        "--hardware",
        hardware,
        "--wallclock-target",
        wallclock_target,
        "--core-hparams",
        args.core_hparams,
        "--artifact-cap",
        str(artifact_cap),
        "--json-out",
        str(result_json_path),
        "--md-out",
        str(result_md_path),
        "--require-final-metrics",
    ]
    if args.exact_command:
        result_args.extend(["--exact-command", args.exact_command])
    if args.notes:
        result_args.extend(["--notes", args.notes])
    if compare_json is not None:
        result_args.extend(["--compare-json", str(compare_json)])
        if args.compare_label:
            result_args.extend(["--compare-label", args.compare_label])
    for finding in args.confirmed_finding:
        result_args.extend(["--confirmed-finding", finding])
    for conclusion in args.inferred_conclusion:
        result_args.extend(["--inferred-conclusion", conclusion])

    run_python_script(ROOT / "scripts" / "experiments" / "generate_experiment_result.py", result_args, args.dry_run)

    update_args = [
        "--run-id",
        args.run_id,
        "--summary-json",
        str(result_json_path),
        "--date",
        args.date,
        "--dataset-variant",
        dataset_variant,
        "--tokenizer-variant",
        tokenizer_variant,
        "--core-hparams",
        args.core_hparams,
        "--hardware",
        hardware,
        "--track-intent",
        track_intent,
        "--code-path",
        code_path,
        "--wallclock-target",
        wallclock_target,
    ]
    run_python_script(ROOT / "scripts" / "experiments" / "update_ledger.py", update_args, args.dry_run)

    if args.dry_run:
        print(f"dry_run_result_json={result_json_path}")
        print(f"dry_run_result_md={result_md_path}")
        return 0

    print(f"result_json={result_json_path}")
    print(f"result_md={result_md_path}")
    print("next_action=update challenge_ops/CURRENT_FRONTIER.md and challenge_ops/TRIED_IDEAS_INDEX.md if this run materially changes repo understanding")
    return 0


def parse_candidate_spec(raw: str) -> dict[str, str]:
    parts = [part.strip() for part in raw.split("|", 3)]
    if len(parts) != 4 or any(not part for part in parts):
        raise ValueError(
            "candidate must use format run_id|label|why_promising|recommended_next_step"
        )
    return {
        "run_id": parts[0],
        "label": parts[1],
        "why_promising": parts[2],
        "recommended_next_step": parts[3],
    }


def command_draft_shortlist(args: argparse.Namespace) -> int:
    policy = load_policy(args.policy)
    promotion = policy.raw.get("promotion", {})
    min_candidates = int(promotion.get("min_shortlist_candidates", 2))
    max_candidates = int(promotion.get("max_shortlist_candidates", 4))
    candidates = [parse_candidate_spec(raw) for raw in args.candidate]
    candidate_count = len(candidates)
    if candidate_count < min_candidates or candidate_count > max_candidates:
        print(
            f"error: candidate count {candidate_count} is outside the policy range "
            f"[{min_candidates}, {max_candidates}]",
            file=sys.stderr,
        )
        return 1

    shortlist_dir = policy.path_value("shortlists_dir")
    shortlist_path = shortlist_dir / f"{args.date}_{args.shortlist_id}.md"
    lines = [
        f"# {args.title}",
        "",
        f"- `shortlist_id`: `{args.shortlist_id}`",
        f"- `date`: `{args.date}`",
        f"- `policy_path`: `{policy.path}`",
        "",
        "## Overview",
        "",
        f"- {args.overview}",
        "",
        "## Candidate Setups",
        "",
    ]
    for index, candidate in enumerate(candidates, start=1):
        lines.extend(
            [
                f"### Candidate {index}",
                "",
                f"- `run_id`: `{candidate['run_id']}`",
                f"- `label`: {candidate['label']}",
                f"- Why promising: {candidate['why_promising']}",
                f"- Recommended next step: {candidate['recommended_next_step']}",
                "",
            ]
        )
    lines.extend(
        [
            "## Gate",
            "",
            "- `8xH100` work remains blocked until the user explicitly approves a follow-up policy change.",
            "- This shortlist is intended for user review before any leaderboard-scale run is planned.",
            "",
            "## Notes",
            "",
            f"- {args.notes or 'none'}",
            "",
        ]
    )
    body = "\n".join(lines)

    if args.dry_run:
        print(f"dry_run_shortlist_path={shortlist_path}")
        print(body)
        return 0

    shortlist_dir.mkdir(parents=True, exist_ok=True)
    shortlist_path.write_text(body, encoding="utf-8")
    print(f"shortlist_path={shortlist_path}")
    print("next_action=present this shortlist to the user before any 8xH100 policy change")
    return 0


def remote_approval_matches(
    approval: dict[str, Any],
    *,
    approval_id: str,
    run_id: str,
    hardware_target: str,
) -> bool:
    if approval_id and approval.get("approval_id") != approval_id:
        return False
    if run_id and approval.get("run_id") not in ("", run_id):
        return False
    if hardware_target and approval.get("hardware_target") not in ("", hardware_target):
        return False
    return True


def command_grant_remote_approval(args: argparse.Namespace) -> int:
    policy = load_policy(args.policy)
    payload = {
        "schema_version": 1,
        "approval_id": args.approval_id,
        "kind": "remote_runpod",
        "active": True,
        "created_at_utc": utc_now_iso(),
        "approved_by": args.approved_by,
        "run_id": args.run_id,
        "hardware_target": args.hardware_target,
        "max_paid_runs": args.max_paid_runs,
        "notes": args.notes,
    }
    path = approval_dir(policy) / f"{args.approval_id}.json"
    if args.dry_run:
        print(f"dry_run_remote_approval_path={path}")
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0
    write_json(path, payload)
    print(f"remote_approval_path={path}")
    return 0


def command_check_remote_approval(args: argparse.Namespace) -> int:
    policy = load_policy(args.policy)
    approvals = active_remote_approvals(policy)
    for approval in approvals:
        if remote_approval_matches(
            approval,
            approval_id=args.approval_id,
            run_id=args.run_id,
            hardware_target=args.hardware_target,
        ):
            print(f"remote_approval_ok=true")
            print(f"approval_id={approval.get('approval_id', '')}")
            print(f"approval_path={approval.get('_path', '')}")
            print(f"approved_by={approval.get('approved_by', '')}")
            print(f"run_id={approval.get('run_id', '')}")
            print(f"hardware_target={approval.get('hardware_target', '')}")
            return 0
    print("remote_approval_ok=false")
    print("error=no active remote approval token matched the requested run_id/hardware_target", file=sys.stderr)
    return 1


def command_revoke_remote_approval(args: argparse.Namespace) -> int:
    policy = load_policy(args.policy)
    path = approval_dir(policy) / f"{args.approval_id}.json"
    if not path.exists():
        print(f"error: approval token not found: {path}", file=sys.stderr)
        return 1
    payload = read_json(path)
    payload["active"] = False
    payload["revoked_at_utc"] = utc_now_iso()
    payload["revoked_by"] = args.revoked_by
    if args.notes:
        payload["revocation_notes"] = args.notes
    if args.dry_run:
        print(f"dry_run_remote_approval_path={path}")
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0
    write_json(path, payload)
    print(f"revoked_remote_approval_path={path}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    build_status_parser(subparsers)
    build_plan_parser(subparsers)
    build_record_parser(subparsers)
    build_shortlist_parser(subparsers)
    build_remote_approval_parsers(subparsers)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
