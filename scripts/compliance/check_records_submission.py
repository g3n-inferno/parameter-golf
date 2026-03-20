#!/usr/bin/env python3
"""Check that a records candidate folder has the minimum required submission shape."""

from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("candidate_dir", type=Path, help="Candidate folder under records/.")
    return parser


def missing_relative_imports(candidate_dir: Path) -> list[str]:
    failures: list[str] = []
    for path in candidate_dir.rglob("*.py"):
        text = path.read_text(encoding="utf-8", errors="replace")
        try:
            tree = ast.parse(text, filename=str(path))
        except SyntaxError as exc:
            failures.append(f"{path.relative_to(candidate_dir)} does not parse: {exc}")
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.level > 0:
                module_parts = [] if node.module is None else node.module.split(".")
                rel_root = path.parent
                for _ in range(node.level - 1):
                    rel_root = rel_root.parent
                target = rel_root.joinpath(*module_parts) if module_parts else rel_root
                exists = target.with_suffix(".py").exists() or (target / "__init__.py").exists()
                if not exists:
                    failures.append(
                        f"{path.relative_to(candidate_dir)} references unpackaged relative import "
                        f"from {'.' * node.level}{node.module or ''}"
                    )
    return failures


def main() -> int:
    args = build_parser().parse_args()
    root = repo_root()
    candidate_dir = (root / args.candidate_dir).resolve() if not args.candidate_dir.is_absolute() else args.candidate_dir.resolve()
    if not candidate_dir.is_dir():
        print(f"FAIL records-submission: candidate directory not found: {candidate_dir}")
        return 1

    failed = False
    required = ["README.md", "submission.json", "train.log", "train_gpt.py"]
    for name in required:
        path = candidate_dir / name
        if path.is_file():
            print(f"PASS required-file: {name}")
        else:
            print(f"FAIL required-file: missing {name}")
            failed = True

    submission_path = candidate_dir / "submission.json"
    if submission_path.is_file():
        try:
            json.loads(submission_path.read_text(encoding="utf-8"))
            print("PASS submission.json parse")
        except json.JSONDecodeError as exc:
            print(f"FAIL submission.json parse: {exc}")
            failed = True

    manifest_path = candidate_dir / "metadata" / "candidate_manifest.json"
    if manifest_path.is_file():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            print("PASS candidate manifest parse")
            for rel_path in manifest.get("declared_dependencies", []):
                dep = candidate_dir / rel_path
                if dep.exists():
                    print(f"PASS declared dependency: {rel_path}")
                else:
                    print(f"FAIL declared dependency: missing {rel_path}")
                    failed = True
        except json.JSONDecodeError as exc:
            print(f"FAIL candidate manifest parse: {exc}")
            failed = True
    else:
        print("WARN candidate manifest: metadata/candidate_manifest.json not present")

    import_failures = missing_relative_imports(candidate_dir)
    if import_failures:
        for item in import_failures:
            print(f"FAIL self-contained: {item}")
        failed = True
    else:
        print("PASS self-contained: no missing packaged relative imports detected")

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
