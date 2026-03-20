#!/usr/bin/env python3
"""Create a new lightweight experiment ledger entry."""

from __future__ import annotations

import argparse
import csv
import subprocess
import sys
from datetime import date
from pathlib import Path


FIELDS = [
    "run_id",
    "branch",
    "date",
    "dataset_variant",
    "tokenizer_variant",
    "core_hparams",
    "hardware",
    "val_loss",
    "val_bpb",
    "bytes_model",
    "bytes_code",
    "bytes_total",
    "notes",
    "track_intent",
    "code_path",
    "wallclock_target",
]


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def ledger_path(root: Path) -> Path:
    return root / "experiments" / "ledger.csv"


def git_output(root: Path, *args: str) -> str:
    try:
        proc = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, check=True)
    except Exception:
        return ""
    return proc.stdout.strip()


def read_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_rows(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True, help="Stable run identifier.")
    parser.add_argument("--branch", default=None, help="Git branch. Default: current branch if available.")
    parser.add_argument("--date", default=date.today().isoformat(), help="Run date. Default: today.")
    parser.add_argument("--dataset-variant", default="", help="Dataset variant, for example fineweb10B_sp1024.")
    parser.add_argument("--tokenizer-variant", default="", help="Tokenizer variant or path label.")
    parser.add_argument("--core-hparams", default="", help="Short hyperparameter summary.")
    parser.add_argument("--hardware", default="", help="Hardware label, for example 1xH100.")
    parser.add_argument(
        "--track-intent",
        default="non-record",
        choices=["non-record", "track-candidate"],
        help="Whether this run is exploratory or intended as a track candidate.",
    )
    parser.add_argument("--code-path", default="", help="Code path or script used for the run.")
    parser.add_argument("--wallclock-target", default="", help="Wallclock target summary, for example 600s.")
    parser.add_argument("--notes", default="", help="Short notes.")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite an existing run_id entry instead of failing.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    root = repo_root()
    path = ledger_path(root)
    rows = read_rows(path)
    branch = args.branch if args.branch is not None else git_output(root, "branch", "--show-current")

    existing_index = next((idx for idx, row in enumerate(rows) if row["run_id"] == args.run_id), None)
    if existing_index is not None and not args.force:
        print(f"error: run_id already exists in ledger: {args.run_id}", file=sys.stderr)
        print("rerun with --force to replace it", file=sys.stderr)
        return 1

    row = {
        "run_id": args.run_id,
        "branch": branch,
        "date": args.date,
        "dataset_variant": args.dataset_variant,
        "tokenizer_variant": args.tokenizer_variant,
        "core_hparams": args.core_hparams,
        "hardware": args.hardware,
        "val_loss": "",
        "val_bpb": "",
        "bytes_model": "",
        "bytes_code": "",
        "bytes_total": "",
        "notes": args.notes,
        "track_intent": args.track_intent,
        "code_path": args.code_path,
        "wallclock_target": args.wallclock_target,
    }

    if existing_index is None:
        rows.append(row)
    else:
        rows[existing_index] = row
    write_rows(path, rows)
    print(f"updated ledger: {path}")
    print(f"run_id: {args.run_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
