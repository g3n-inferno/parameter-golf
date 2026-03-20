#!/usr/bin/env python3
"""Track Runpod challenge pod sessions and experiment runs using runpodctl."""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SESSIONS_LEDGER = ROOT / "experiments" / "runpod_sessions.csv"
DEFAULT_RUNS_LEDGER = ROOT / "experiments" / "runpod_runs.csv"
DEFAULT_USAGE_SCOPE = "challenge"
DEFAULT_FUNDING_NOTE = "OpenAI Runpod credit allocation ($25, blended balance assumption)"
DEFAULT_CHALLENGE_CREDIT_BUDGET_USD = 25.0

SESSION_FIELDS = [
    "session_id",
    "pod_id",
    "pod_name",
    "usage_scope",
    "purpose",
    "funding_note",
    "session_start_utc",
    "pod_ready_utc",
    "session_end_utc",
    "init_seconds",
    "session_seconds",
    "non_training_seconds",
    "billed_amount_usd",
    "billed_time_ms",
    "cost_per_hr_usd",
    "gpu_id",
    "gpu_count",
    "container_disk_gb",
    "volume_gb",
    "memory_gb",
    "vcpu_count",
    "image_name",
    "data_center_id",
    "secure_cloud",
    "created_at_utc",
    "notes",
]

RUN_FIELDS = [
    "session_id",
    "run_id",
    "experiment_id",
    "train_command",
    "run_start_utc",
    "run_end_utc",
    "run_seconds",
    "billed_amount_usd",
    "billed_time_ms",
    "notes",
]


@dataclass
class LedgerPaths:
    sessions: Path
    runs: Path


def utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_time(value: str) -> datetime:
    normalized = value.strip()
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def format_time(dt: datetime) -> str:
    return dt.astimezone(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def get_timestamp(value: str | None) -> str:
    return utc_now_iso() if value is None else format_time(parse_time(value))


def ensure_csv(path: Path, fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()


def read_rows(path: Path, fields: list[str]) -> list[dict[str, str]]:
    ensure_csv(path, fields)
    with path.open("r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_rows(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    ensure_csv(path, fields)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def require_row(rows: list[dict[str, str]], key: str, value: str) -> dict[str, str]:
    row = next((row for row in rows if row.get(key) == value), None)
    if row is None:
        raise SystemExit(f"{key} not found: {value}")
    return row


def run_runpodctl(*args: str) -> Any:
    cmd = ["runpodctl", *args]
    try:
        output = subprocess.check_output(cmd, cwd=ROOT, text=True)
    except subprocess.CalledProcessError as exc:
        raise SystemExit(exc.output.strip() or str(exc)) from exc
    return json.loads(output)


def fetch_pod_config(pod_id: str) -> dict[str, Any]:
    pod = run_runpodctl("pod", "get", pod_id, "--include-machine")
    machine = pod.get("machine") or {}
    return {
        "pod_name": str(pod.get("name", "")),
        "cost_per_hr_usd": str(pod.get("costPerHr", "")),
        "gpu_id": str(machine.get("gpuId", pod.get("imageName", ""))),
        "gpu_count": str(pod.get("gpuCount", "")),
        "container_disk_gb": str(pod.get("containerDiskInGb", "")),
        "volume_gb": str(pod.get("volumeInGb", "")),
        "memory_gb": str(pod.get("memoryInGb", "")),
        "vcpu_count": str(pod.get("vcpuCount", "")),
        "image_name": str(pod.get("imageName", "")),
        "data_center_id": str(machine.get("dataCenterId", "")),
        "secure_cloud": str(machine.get("secureCloud", "")),
        "created_at_utc": str(pod.get("createdAt", "")),
    }


def fetch_billing_window(pod_id: str, start_utc: str, end_utc: str) -> tuple[float, int]:
    amount = 0.0
    billed_ms = 0
    for attempt in range(4):
        rows = run_runpodctl(
            "billing",
            "pods",
            "--bucket-size",
            "hour",
            "--grouping",
            "podId",
            "--pod-id",
            pod_id,
            "--start-time",
            start_utc,
            "--end-time",
            end_utc,
        )
        amount = sum(float(row.get("amount", 0.0)) for row in rows)
        billed_ms = sum(int(float(row.get("timeBilledMs", 0))) for row in rows if row.get("timeBilledMs") is not None)
        if amount > 0.0 or billed_ms > 0:
            break
        if attempt < 3:
            time.sleep(2.0)
    return amount, billed_ms


def estimate_billing(duration_seconds: float, cost_per_hr_usd: str | None) -> tuple[float, int]:
    if duration_seconds <= 0.0 or not cost_per_hr_usd:
        return 0.0, 0
    hourly_rate = float(cost_per_hr_usd)
    return hourly_rate * (duration_seconds / 3600.0), int(round(duration_seconds * 1000.0))


def append_note_bits(existing: str, *note_bits: str) -> str:
    notes = [existing.strip()] if existing.strip() else []
    for bit in note_bits:
        if bit and bit not in existing:
            notes.append(bit)
    return "; ".join(notes)


def seconds_between(start_utc: str, end_utc: str) -> float:
    return (parse_time(end_utc) - parse_time(start_utc)).total_seconds()


def get_session_run_rows(paths: LedgerPaths, session_id: str) -> list[dict[str, str]]:
    return [row for row in read_rows(paths.runs, RUN_FIELDS) if row.get("session_id") == session_id]


def command_init(args: argparse.Namespace, paths: LedgerPaths) -> None:
    ensure_csv(paths.sessions, SESSION_FIELDS)
    ensure_csv(paths.runs, RUN_FIELDS)
    print(f"initialized: {paths.sessions}")
    print(f"initialized: {paths.runs}")


def command_start_session(args: argparse.Namespace, paths: LedgerPaths) -> None:
    rows = read_rows(paths.sessions, SESSION_FIELDS)
    if any(row["session_id"] == args.session_id for row in rows):
        raise SystemExit(f"session_id already exists: {args.session_id}")
    timestamp = get_timestamp(args.started_at)
    config = fetch_pod_config(args.pod_id)
    row = {field: "" for field in SESSION_FIELDS}
    row.update(
        {
            "session_id": args.session_id,
            "pod_id": args.pod_id,
            "usage_scope": args.usage_scope,
            "purpose": args.purpose,
            "funding_note": args.funding_note,
            "session_start_utc": timestamp,
            "notes": args.notes or "",
            **config,
        }
    )
    rows.append(row)
    write_rows(paths.sessions, SESSION_FIELDS, rows)
    print(f"started session: {args.session_id}")


def command_mark_ready(args: argparse.Namespace, paths: LedgerPaths) -> None:
    rows = read_rows(paths.sessions, SESSION_FIELDS)
    row = require_row(rows, "session_id", args.session_id)
    ready_utc = get_timestamp(args.ready_at)
    row["pod_ready_utc"] = ready_utc
    if row.get("session_start_utc"):
        row["init_seconds"] = f"{seconds_between(row['session_start_utc'], ready_utc):.3f}"
    write_rows(paths.sessions, SESSION_FIELDS, rows)
    print(f"marked ready: {args.session_id}")


def command_finish_session(args: argparse.Namespace, paths: LedgerPaths) -> None:
    rows = read_rows(paths.sessions, SESSION_FIELDS)
    row = require_row(rows, "session_id", args.session_id)
    end_utc = get_timestamp(args.ended_at)
    row["session_end_utc"] = end_utc
    if row.get("session_start_utc"):
        duration_seconds = seconds_between(row["session_start_utc"], end_utc)
        row["session_seconds"] = f"{duration_seconds:.3f}"
        amount, billed_ms = fetch_billing_window(row["pod_id"], row["session_start_utc"], end_utc)
        if amount <= 0.0 and billed_ms <= 0:
            amount, billed_ms = estimate_billing(duration_seconds, row.get("cost_per_hr_usd"))
            row["notes"] = append_note_bits(
                row.get("notes", ""),
                "billing_source=estimated_duration_x_hourly_rate",
            )
        row["billed_amount_usd"] = f"{amount:.8f}"
        row["billed_time_ms"] = str(billed_ms)
    session_runs = get_session_run_rows(paths, args.session_id)
    training_seconds = sum(float(run.get("run_seconds") or 0.0) for run in session_runs)
    session_seconds = float(row.get("session_seconds") or 0.0)
    row["non_training_seconds"] = f"{max(session_seconds - training_seconds, 0.0):.3f}"
    write_rows(paths.sessions, SESSION_FIELDS, rows)
    print(f"finished session: {args.session_id}")


def command_start_run(args: argparse.Namespace, paths: LedgerPaths) -> None:
    session_rows = read_rows(paths.sessions, SESSION_FIELDS)
    require_row(session_rows, "session_id", args.session_id)
    run_rows = read_rows(paths.runs, RUN_FIELDS)
    if any(row["run_id"] == args.run_id for row in run_rows):
        raise SystemExit(f"run_id already exists: {args.run_id}")
    row = {field: "" for field in RUN_FIELDS}
    row.update(
        {
            "session_id": args.session_id,
            "run_id": args.run_id,
            "experiment_id": args.experiment_id or "",
            "train_command": args.train_command or "",
            "run_start_utc": get_timestamp(args.started_at),
            "notes": args.notes or "",
        }
    )
    run_rows.append(row)
    write_rows(paths.runs, RUN_FIELDS, run_rows)
    print(f"started run: {args.run_id}")


def command_finish_run(args: argparse.Namespace, paths: LedgerPaths) -> None:
    run_rows = read_rows(paths.runs, RUN_FIELDS)
    run_row = require_row(run_rows, "run_id", args.run_id)
    session_rows = read_rows(paths.sessions, SESSION_FIELDS)
    session_row = require_row(session_rows, "session_id", run_row["session_id"])
    end_utc = get_timestamp(args.ended_at)
    run_row["run_end_utc"] = end_utc
    duration_seconds = seconds_between(run_row["run_start_utc"], end_utc)
    run_row["run_seconds"] = f"{duration_seconds:.3f}"
    amount, billed_ms = fetch_billing_window(session_row["pod_id"], run_row["run_start_utc"], end_utc)
    if amount <= 0.0 and billed_ms <= 0:
        amount, billed_ms = estimate_billing(duration_seconds, session_row.get("cost_per_hr_usd"))
        run_row["notes"] = append_note_bits(
            run_row.get("notes", ""),
            "billing_source=estimated_duration_x_hourly_rate",
        )
    run_row["billed_amount_usd"] = f"{amount:.8f}"
    run_row["billed_time_ms"] = str(billed_ms)
    write_rows(paths.runs, RUN_FIELDS, run_rows)
    print(f"finished run: {args.run_id}")


def command_refresh_billing(args: argparse.Namespace, paths: LedgerPaths) -> None:
    session_rows = read_rows(paths.sessions, SESSION_FIELDS)
    run_rows = read_rows(paths.runs, RUN_FIELDS)

    if args.session_id:
        session_rows = [require_row(session_rows, "session_id", args.session_id)]
    elif args.usage_scope:
        session_rows = [row for row in session_rows if row.get("usage_scope") == args.usage_scope]

    session_ids = {row["session_id"] for row in session_rows}
    if args.run_id:
        target_run = require_row(run_rows, "run_id", args.run_id)
        run_rows = [target_run]
        session_ids.add(target_run["session_id"])
        session_rows = [row for row in read_rows(paths.sessions, SESSION_FIELDS) if row["session_id"] in session_ids]
    else:
        run_rows = [row for row in run_rows if row.get("session_id") in session_ids]

    session_map = {row["session_id"]: row for row in read_rows(paths.sessions, SESSION_FIELDS)}
    updated_runs = 0
    updated_sessions = 0

    for run_row in run_rows:
        session_row = session_map[run_row["session_id"]]
        if not run_row.get("run_start_utc") or not run_row.get("run_end_utc"):
            continue
        duration_seconds = seconds_between(run_row["run_start_utc"], run_row["run_end_utc"])
        amount, billed_ms = fetch_billing_window(session_row["pod_id"], run_row["run_start_utc"], run_row["run_end_utc"])
        if amount <= 0.0 and billed_ms <= 0:
            amount, billed_ms = estimate_billing(duration_seconds, session_row.get("cost_per_hr_usd"))
            run_row["notes"] = append_note_bits(
                run_row.get("notes", ""),
                "billing_source=estimated_duration_x_hourly_rate",
            )
        else:
            run_row["notes"] = append_note_bits(
                run_row.get("notes", ""),
                "billing_source=runpod_api",
            )
        run_row["billed_amount_usd"] = f"{amount:.8f}"
        run_row["billed_time_ms"] = str(billed_ms)
        updated_runs += 1

    for session_row in session_rows:
        if not session_row.get("session_start_utc") or not session_row.get("session_end_utc"):
            continue
        duration_seconds = seconds_between(session_row["session_start_utc"], session_row["session_end_utc"])
        amount, billed_ms = fetch_billing_window(session_row["pod_id"], session_row["session_start_utc"], session_row["session_end_utc"])
        if amount <= 0.0 and billed_ms <= 0:
            amount, billed_ms = estimate_billing(duration_seconds, session_row.get("cost_per_hr_usd"))
            session_row["notes"] = append_note_bits(
                session_row.get("notes", ""),
                "billing_source=estimated_duration_x_hourly_rate",
            )
        else:
            session_row["notes"] = append_note_bits(
                session_row.get("notes", ""),
                "billing_source=runpod_api",
            )
        session_row["billed_amount_usd"] = f"{amount:.8f}"
        session_row["billed_time_ms"] = str(billed_ms)
        updated_sessions += 1

    all_session_rows = read_rows(paths.sessions, SESSION_FIELDS)
    all_run_rows = read_rows(paths.runs, RUN_FIELDS)
    by_session = {row["session_id"]: row for row in session_rows}
    by_run = {row["run_id"]: row for row in run_rows}
    for index, row in enumerate(all_session_rows):
        if row["session_id"] in by_session:
            all_session_rows[index] = by_session[row["session_id"]]
    for index, row in enumerate(all_run_rows):
        if row["run_id"] in by_run:
            all_run_rows[index] = by_run[row["run_id"]]
    write_rows(paths.sessions, SESSION_FIELDS, all_session_rows)
    write_rows(paths.runs, RUN_FIELDS, all_run_rows)
    print(f"refreshed billing: sessions={updated_sessions} runs={updated_runs}")


def command_report(args: argparse.Namespace, paths: LedgerPaths) -> None:
    sessions = read_rows(paths.sessions, SESSION_FIELDS)
    runs = read_rows(paths.runs, RUN_FIELDS)
    if args.usage_scope:
        sessions = [row for row in sessions if row.get("usage_scope") == args.usage_scope]
    session_ids = {row["session_id"] for row in sessions}
    runs = [row for row in runs if row.get("session_id") in session_ids]

    total_session_cost = sum(float(row.get("billed_amount_usd") or 0.0) for row in sessions)
    total_session_billed_ms = sum(int(float(row.get("billed_time_ms") or 0.0)) for row in sessions)
    total_run_cost = sum(float(row.get("billed_amount_usd") or 0.0) for row in runs)
    total_run_seconds = sum(float(row.get("run_seconds") or 0.0) for row in runs)
    total_init_seconds = sum(float(row.get("init_seconds") or 0.0) for row in sessions)
    total_non_training_seconds = sum(float(row.get("non_training_seconds") or 0.0) for row in sessions)
    assumed_budget = float(args.challenge_credit_budget_usd)
    remaining_budget = max(assumed_budget - total_session_cost, 0.0)

    report = {
        "sessions_ledger": str(paths.sessions),
        "runs_ledger": str(paths.runs),
        "usage_scope": args.usage_scope or "all",
        "session_count": len(sessions),
        "run_count": len(runs),
        "total_session_cost_usd": round(total_session_cost, 8),
        "total_session_billed_hours": round(total_session_billed_ms / 3_600_000.0, 6),
        "total_run_cost_usd": round(total_run_cost, 8),
        "total_run_hours": round(total_run_seconds / 3600.0, 6),
        "total_init_hours": round(total_init_seconds / 3600.0, 6),
        "total_non_training_hours": round(total_non_training_seconds / 3600.0, 6),
        "assumed_challenge_credit_budget_usd": round(assumed_budget, 8),
        "assumed_challenge_credit_remaining_usd": round(remaining_budget, 8),
        "credit_source_note": (
            "Runpod surfaces cost and a blended balance, but not which credits were consumed. "
            "This report treats challenge usage as drawing down a fixed $25 OpenAI allocation "
            "via funding_note/usage_scope, independent of the current Runpod balance."
        ),
    }
    print(json.dumps(report, indent=2))


def command_run_command(args: argparse.Namespace, paths: LedgerPaths) -> None:
    command_args = list(args.command_args)
    if command_args[:1] == ["--"]:
        command_args = command_args[1:]
    if not command_args:
        raise SystemExit("run-command requires a command after --")
    command_init(args, paths)
    session_args = argparse.Namespace(
        session_id=args.session_id,
        pod_id=args.pod_id,
        usage_scope=args.usage_scope,
        purpose=args.purpose,
        funding_note=args.funding_note,
        started_at=args.started_at,
        notes=args.notes,
    )
    start_run_args = argparse.Namespace(
        session_id=args.session_id,
        run_id=args.run_id,
        experiment_id=args.experiment_id,
        train_command=" ".join(command_args),
        started_at=args.run_started_at,
        notes=args.run_notes,
    )
    finish_run_args = argparse.Namespace(run_id=args.run_id, ended_at=args.run_ended_at)
    finish_session_args = argparse.Namespace(session_id=args.session_id, ended_at=args.ended_at)
    report_args = argparse.Namespace(
        usage_scope=args.usage_scope,
        challenge_credit_budget_usd=args.challenge_credit_budget_usd,
    )

    command_start_session(session_args, paths)
    ready_args = argparse.Namespace(session_id=args.session_id, ready_at=args.ready_at)
    command_mark_ready(ready_args, paths)
    command_start_run(start_run_args, paths)

    exit_code = 0
    try:
        result = subprocess.run(command_args, cwd=ROOT, check=False)
        exit_code = int(result.returncode)
    finally:
        command_finish_run(finish_run_args, paths)
        command_finish_session(finish_session_args, paths)
        command_report(report_args, paths)
    if exit_code != 0:
        raise SystemExit(exit_code)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sessions-ledger", type=Path, default=DEFAULT_SESSIONS_LEDGER)
    parser.add_argument("--runs-ledger", type=Path, default=DEFAULT_RUNS_LEDGER)
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("init")

    start_session = subparsers.add_parser("start-session")
    start_session.add_argument("--session-id", required=True)
    start_session.add_argument("--pod-id", required=True)
    start_session.add_argument("--usage-scope", default=DEFAULT_USAGE_SCOPE)
    start_session.add_argument("--purpose", required=True)
    start_session.add_argument("--funding-note", default=DEFAULT_FUNDING_NOTE)
    start_session.add_argument("--started-at")
    start_session.add_argument("--notes")

    ready = subparsers.add_parser("mark-ready")
    ready.add_argument("--session-id", required=True)
    ready.add_argument("--ready-at")

    finish_session = subparsers.add_parser("finish-session")
    finish_session.add_argument("--session-id", required=True)
    finish_session.add_argument("--ended-at")

    start_run = subparsers.add_parser("start-run")
    start_run.add_argument("--session-id", required=True)
    start_run.add_argument("--run-id", required=True)
    start_run.add_argument("--experiment-id")
    start_run.add_argument("--train-command")
    start_run.add_argument("--started-at")
    start_run.add_argument("--notes")

    finish_run = subparsers.add_parser("finish-run")
    finish_run.add_argument("--run-id", required=True)
    finish_run.add_argument("--ended-at")

    refresh_billing = subparsers.add_parser("refresh-billing")
    refresh_billing.add_argument("--session-id")
    refresh_billing.add_argument("--run-id")
    refresh_billing.add_argument("--usage-scope")

    report = subparsers.add_parser("report")
    report.add_argument("--usage-scope")
    report.add_argument("--challenge-credit-budget-usd", type=float, default=DEFAULT_CHALLENGE_CREDIT_BUDGET_USD)

    run_command = subparsers.add_parser("run-command")
    run_command.add_argument("--session-id", required=True)
    run_command.add_argument("--pod-id", required=True)
    run_command.add_argument("--run-id", required=True)
    run_command.add_argument("--purpose", required=True)
    run_command.add_argument("--usage-scope", default=DEFAULT_USAGE_SCOPE)
    run_command.add_argument("--funding-note", default=DEFAULT_FUNDING_NOTE)
    run_command.add_argument("--experiment-id")
    run_command.add_argument("--started-at")
    run_command.add_argument("--ready-at")
    run_command.add_argument("--run-started-at")
    run_command.add_argument("--run-ended-at")
    run_command.add_argument("--ended-at")
    run_command.add_argument("--notes")
    run_command.add_argument("--run-notes")
    run_command.add_argument("--challenge-credit-budget-usd", type=float, default=DEFAULT_CHALLENGE_CREDIT_BUDGET_USD)
    run_command.add_argument("command_args", nargs=argparse.REMAINDER)

    return parser


def main() -> None:
    args = build_parser().parse_args()
    paths = LedgerPaths(args.sessions_ledger, args.runs_ledger)
    commands = {
        "init": command_init,
        "start-session": command_start_session,
        "mark-ready": command_mark_ready,
        "finish-session": command_finish_session,
        "start-run": command_start_run,
        "finish-run": command_finish_run,
        "refresh-billing": command_refresh_billing,
        "report": command_report,
        "run-command": command_run_command,
    }
    commands[args.command](args, paths)


if __name__ == "__main__":
    main()
