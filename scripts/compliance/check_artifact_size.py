#!/usr/bin/env python3
"""Check counted artifact bytes against the challenge cap."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path


DEFAULT_CAP = 16_000_000


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_parse_module(root: Path):
    module_path = root / "scripts" / "experiments" / "parse_train_log.py"
    spec = importlib.util.spec_from_file_location("parse_train_log_module", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load parser module from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", type=Path, help="Candidate folder, submission.json, or train.log path.")
    parser.add_argument("--cap", type=int, default=DEFAULT_CAP, help=f"Artifact cap in bytes. Default: {DEFAULT_CAP}")
    return parser


def resolve_total(root: Path, target: Path) -> tuple[int | None, str]:
    if target.is_dir():
        submission = target / "submission.json"
        train_log = target / "train.log"
    else:
        submission = target if target.name == "submission.json" else None
        train_log = target if target.name.endswith(".log") else None

    if submission is not None and submission.is_file():
        data = json.loads(submission.read_text(encoding="utf-8"))
        value = data.get("bytes_total")
        if isinstance(value, (int, float)):
            return int(value), f"{submission} bytes_total"

    if train_log is not None and train_log.is_file():
        module = load_parse_module(root)
        parsed = module.parse_log(train_log)
        if parsed.get("total_submission_size_int8_zlib_bytes") is not None:
            return int(parsed["total_submission_size_int8_zlib_bytes"]), f"{train_log} total_submission_size_int8_zlib_bytes"
        if parsed.get("total_submission_size_bytes") is not None:
            return int(parsed["total_submission_size_bytes"]), f"{train_log} total_submission_size_bytes"

    if target.is_dir():
        if submission is not None and submission.is_file():
            pass
        if train_log is not None and train_log.is_file():
            pass
    return None, "no artifact byte source found"


def main() -> int:
    args = build_parser().parse_args()
    root = repo_root()
    target = (root / args.target).resolve() if not args.target.is_absolute() else args.target.resolve()
    if not target.exists():
        print(f"FAIL artifact-size target does not exist: {target}")
        return 1
    try:
        total, source = resolve_total(root, target)
    except Exception as exc:
        print(f"FAIL artifact-size check error: {exc}")
        return 1
    if total is None:
        print(f"FAIL artifact-size unavailable: {source}")
        return 1
    if total <= args.cap:
        print(f"PASS artifact-size: {total} <= {args.cap} ({source})")
        return 0
    print(f"FAIL artifact-size: {total} > {args.cap} ({source})")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
