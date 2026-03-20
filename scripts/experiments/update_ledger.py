#!/usr/bin/env python3
"""Update selected fields for an existing experiment ledger entry."""

from __future__ import annotations

import argparse
import csv
import json
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
    parser.add_argument(
        "--summary-json",
        type=Path,
        default=None,
        help="Optional parsed summary JSON to import val/byte fields from.",
    )
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

    summary_updates: dict[str, str | None] = {}
    note_bits: list[str] = []
    if args.summary_json is not None:
        summary_path = (root / args.summary_json).resolve() if not args.summary_json.is_absolute() else args.summary_json.resolve()
        if not summary_path.exists():
            print(f"error: summary JSON does not exist: {summary_path}", file=sys.stderr)
            return 1
        parsed = json.loads(summary_path.read_text(encoding="utf-8"))
        summary_updates = {
            "val_loss": str(parsed["final_val_loss"]) if parsed.get("final_val_loss") is not None else None,
            "val_bpb": str(parsed["final_val_bpb"]) if parsed.get("final_val_bpb") is not None else None,
            "bytes_model": (
                str(parsed["model_int8_zlib_bytes"])
                if parsed.get("model_int8_zlib_bytes") is not None
                else (str(parsed["model_bytes"]) if parsed.get("model_bytes") is not None else None)
            ),
            "bytes_code": str(parsed["code_bytes"]) if parsed.get("code_bytes") is not None else None,
            "bytes_total": (
                str(parsed["total_submission_size_int8_zlib_bytes"])
                if parsed.get("total_submission_size_int8_zlib_bytes") is not None
                else (
                    str(parsed["total_submission_size_bytes"])
                    if parsed.get("total_submission_size_bytes") is not None
                    else None
                )
            ),
        }
        if parsed.get("stop_reason"):
            note_bits.append(f"stop_reason={parsed['stop_reason']}")
        if parsed.get("stop_step") is not None:
            note_bits.append(f"stop_step={parsed['stop_step']}")
        if parsed.get("comparison", {}).get("label") and parsed["comparison"].get("delta_val_bpb") is not None:
            note_bits.append(
                f"delta_val_bpb_vs_{parsed['comparison']['label']}={parsed['comparison']['delta_val_bpb']:+.8f}"
            )

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
    updates.update(summary_updates)
    if args.notes is not None:
        updates["notes"] = args.notes
    elif note_bits:
        existing_notes = target.get("notes", "").strip()
        filtered_bits = [bit for bit in note_bits if bit not in existing_notes]
        auto_notes = "; ".join(filtered_bits)
        updates["notes"] = f"{existing_notes}; {auto_notes}".strip("; ") if existing_notes else auto_notes
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
