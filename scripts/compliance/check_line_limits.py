#!/usr/bin/env python3
"""Check line-count limits for train_gpt.py and train_gpt_mlx.py."""

from __future__ import annotations

import argparse
from pathlib import Path


LIMIT = 1500


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "base_dir",
        nargs="?",
        default=".",
        help="Base directory containing train_gpt.py and optionally train_gpt_mlx.py. Default: repo root.",
    )
    parser.add_argument("--limit", type=int, default=LIMIT, help=f"Line limit. Default: {LIMIT}")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    root = repo_root()
    base_dir = (root / args.base_dir).resolve() if not Path(args.base_dir).is_absolute() else Path(args.base_dir).resolve()
    failed = False
    checked = False
    for name in ("train_gpt.py", "train_gpt_mlx.py"):
        path = base_dir / name
        if path.exists():
            checked = True
            count = len(path.read_text(encoding="utf-8", errors="replace").splitlines())
            if count <= args.limit:
                print(f"PASS line-limit: {name} {count} <= {args.limit}")
            else:
                print(f"FAIL line-limit: {name} {count} > {args.limit}")
                failed = True
        else:
            print(f"WARN line-limit: {name} not found under {base_dir}")
    if not checked:
        print(f"FAIL line-limit: no target files found under {base_dir}")
        return 1
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
