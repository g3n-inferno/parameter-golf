#!/usr/bin/env python3
"""Update selected fields for an existing experiment ledger entry."""

from __future__ import annotations

import argparse
import csv
import sys
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


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_rows(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True, help="Run identifier to update.")
    parser.add_argument("--branch")
    parser.add_argument("--date")
    parser.add_argument("--dataset-variant")
    parser.add_argument("--tokenizer-variant")
    parser.add_argument("--core-hparams")
    parser.add_argument("--hardware")
    parser.add_argument("--val-loss")
    parser.add_argument("--val-bpb")
    parser.add_argument("--bytes-model")
    parser.add_argument("--bytes-code")
    parser.add_argument("--bytes-total")
    parser.add_argument("--notes")
    parser.add_argument("--track-intent", choices=["non-record", "track-candidate"])
    parser.add_argument("--code-path")
    parser.add_argument("--wallclock-target")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    root = repo_root()
    path = ledger_path(root)
    if not path.exists():
        print(f"error: ledger does not exist: {path}", file=sys.stderr)
        return 1
    rows = read_rows(path)
    target = next((row for row in rows if row["run_id"] == args.run_id), None)
    if target is None:
        print(f"error: run_id not found in ledger: {args.run_id}", file=sys.stderr)
        return 1

    updates = {
        "branch": args.branch,
        "date": args.date,
        "dataset_variant": args.dataset_variant,
        "tokenizer_variant": args.tokenizer_variant,
        "core_hparams": args.core_hparams,
        "hardware": args.hardware,
        "val_loss": args.val_loss,
        "val_bpb": args.val_bpb,
        "bytes_model": args.bytes_model,
        "bytes_code": args.bytes_code,
        "bytes_total": args.bytes_total,
        "notes": args.notes,
        "track_intent": args.track_intent,
        "code_path": args.code_path,
        "wallclock_target": args.wallclock_target,
    }
    changed = False
    for key, value in updates.items():
        if value is not None:
            target[key] = value
            changed = True

    if not changed:
        print("error: no updates were provided", file=sys.stderr)
        return 1

    write_rows(path, rows)
    print(f"updated ledger entry: {args.run_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
