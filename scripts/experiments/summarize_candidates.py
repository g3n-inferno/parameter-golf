#!/usr/bin/env python3
"""Summarize experiment candidates from experiments/ledger.csv."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--track-intent",
        choices=["non-record", "track-candidate"],
        default=None,
        help="Optional intent filter.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Maximum number of rows to print. Default: 10.",
    )
    parser.add_argument(
        "--sort-by",
        choices=["date", "val_bpb", "bytes_total"],
        default="date",
        help="Sort key. Default: date.",
    )
    return parser


def load_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def numeric_or_inf(value: str) -> float:
    try:
        return float(value)
    except Exception:
        return float("inf")


def main() -> int:
    args = build_parser().parse_args()
    path = repo_root() / "experiments" / "ledger.csv"
    rows = load_rows(path)
    if args.track_intent is not None:
        rows = [row for row in rows if row.get("track_intent") == args.track_intent]

    if args.sort_by == "date":
        rows.sort(key=lambda row: row.get("date", ""), reverse=True)
    elif args.sort_by == "val_bpb":
        rows.sort(key=lambda row: numeric_or_inf(row.get("val_bpb", "")))
    else:
        rows.sort(key=lambda row: numeric_or_inf(row.get("bytes_total", "")))

    rows = rows[: args.limit]
    if not rows:
        print("no experiment rows matched")
        return 0

    for row in rows:
        print(
            f"{row.get('date','')}  run_id={row.get('run_id','')}  "
            f"intent={row.get('track_intent','')}  hardware={row.get('hardware','')}  "
            f"val_bpb={row.get('val_bpb','')}  bytes_total={row.get('bytes_total','')}  "
            f"notes={row.get('notes','')}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
