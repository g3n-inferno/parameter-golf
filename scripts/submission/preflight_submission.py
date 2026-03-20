#!/usr/bin/env python3
"""Run structural and compliance-oriented preflight checks on a records candidate folder."""

from __future__ import annotations

import argparse
import ast
import importlib.util
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


ARTIFACT_CAP_DEFAULT = 16_000_000
CORE_WARNING_PREFIXES = (
    "README.md",
    "train_gpt.py",
    "train_gpt_mlx.py",
    "data/",
    "requirements.txt",
)


@dataclass
class CheckResult:
    status: str
    label: str
    detail: str


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("candidate_dir", type=Path, help="Path to a candidate folder under records/.")
    parser.add_argument(
        "--artifact-cap",
        type=int,
        default=ARTIFACT_CAP_DEFAULT,
        help=f"Artifact byte cap. Default: {ARTIFACT_CAP_DEFAULT}",
    )
    return parser


def add(results: list[CheckResult], status: str, label: str, detail: str) -> None:
    results.append(CheckResult(status=status, label=label, detail=detail))


def git_output(root: Path, *args: str) -> str | None:
    try:
        proc = subprocess.run(
            ["git", *args],
            cwd=root,
            capture_output=True,
            text=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return proc.stdout.strip()


def core_git_warnings(root: Path) -> list[str]:
    output = git_output(root, "status", "--porcelain")
    if not output:
        return []
    warnings: list[str] = []
    for line in output.splitlines():
        if len(line) < 4:
            continue
        raw_path = line[3:].strip()
        path = raw_path.replace("\\", "/")
        if path.startswith("records/"):
            continue
        if any(path == prefix.rstrip("/") or path.startswith(prefix) for prefix in CORE_WARNING_PREFIXES):
            warnings.append(path)
    return sorted(set(warnings))


def load_parse_module(root: Path):
    module_path = root / "scripts" / "experiments" / "parse_train_log.py"
    spec = importlib.util.spec_from_file_location("parse_train_log_module", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load parser module from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def looks_self_contained(candidate_dir: Path) -> tuple[list[str], list[str]]:
    warnings: list[str] = []
    failures: list[str] = []
    files = list(candidate_dir.rglob("*"))
    suspicious_tokens = (
        "/workspace/parameter-golf",
        "/root/code/parameter-golf",
        "C:\\Users\\",
    )
    for path in files:
        if not path.is_file() or path.suffix.lower() not in {".py", ".md", ".json", ".sh", ".txt"}:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for token in suspicious_tokens:
            if token in text:
                warnings.append(f"{path.relative_to(candidate_dir)} contains absolute repo path reference: {token}")
        if path.suffix.lower() == ".py":
            try:
                tree = ast.parse(text, filename=str(path))
            except SyntaxError as exc:
                failures.append(f"{path.relative_to(candidate_dir)} does not parse as Python: {exc}")
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
                            f"{path.relative_to(candidate_dir)} uses relative import that is not packaged: "
                            f"from {'.' * node.level}{node.module or ''}"
                        )
    return warnings, failures


def line_count(path: Path) -> int:
    return len(path.read_text(encoding="utf-8", errors="replace").splitlines())


def main() -> int:
    args = build_parser().parse_args()
    root = repo_root()
    candidate_dir = (root / args.candidate_dir).resolve() if not args.candidate_dir.is_absolute() else args.candidate_dir.resolve()

    results: list[CheckResult] = []
    failed = False

    if not candidate_dir.exists():
        print(f"error: candidate folder not found: {candidate_dir}", file=sys.stderr)
        return 1
    try:
        candidate_rel = candidate_dir.relative_to(root)
    except ValueError:
        print(f"error: candidate folder must live inside repo root: {candidate_dir}", file=sys.stderr)
        return 1

    if candidate_rel.parts[:1] != ("records",):
        add(results, "FAIL", "records path", f"{candidate_rel} is not under records/")
        failed = True
    else:
        add(results, "PASS", "records path", str(candidate_rel).replace("\\", "/"))

    required = {
        "README.md": candidate_dir / "README.md",
        "submission.json": candidate_dir / "submission.json",
        "train.log": candidate_dir / "train.log",
        "train_gpt.py": candidate_dir / "train_gpt.py",
    }
    for label, path in required.items():
        if path.is_file():
            add(results, "PASS", f"required file: {label}", f"found {path.relative_to(root)}")
        else:
            add(results, "FAIL", f"required file: {label}", f"missing {path.relative_to(root)}")
            failed = True

    manifest_path = candidate_dir / "metadata" / "candidate_manifest.json"
    manifest = None
    if manifest_path.is_file():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            add(results, "PASS", "candidate manifest", f"parsed {manifest_path.relative_to(root)}")
        except json.JSONDecodeError as exc:
            add(results, "FAIL", "candidate manifest", f"invalid JSON: {exc}")
            failed = True
    else:
        add(results, "WARN", "candidate manifest", "missing metadata/candidate_manifest.json")

    submission_data = None
    submission_path = required["submission.json"]
    if submission_path.is_file():
        try:
            submission_data = json.loads(submission_path.read_text(encoding="utf-8"))
            add(results, "PASS", "submission.json parse", "valid JSON")
        except json.JSONDecodeError as exc:
            add(results, "FAIL", "submission.json parse", f"invalid JSON: {exc}")
            failed = True

    if manifest is not None:
        for rel_path in manifest.get("declared_dependencies", []):
            dep_path = candidate_dir / rel_path
            if dep_path.exists():
                add(results, "PASS", "declared dependency", f"found {dep_path.relative_to(root)}")
            else:
                add(results, "FAIL", "declared dependency", f"missing {dep_path.relative_to(root)}")
                failed = True
        for rel_path in manifest.get("extra_logs", []):
            log_path = candidate_dir / rel_path
            if not log_path.exists():
                add(results, "FAIL", "extra log path", f"missing {log_path.relative_to(root)}")
                failed = True
        for rel_path in manifest.get("metadata_files", []):
            item_path = candidate_dir / rel_path
            if not item_path.exists():
                add(results, "FAIL", "metadata path", f"missing {item_path.relative_to(root)}")
                failed = True

    train_log_path = required["train.log"]
    parsed_log = None
    if train_log_path.is_file():
        try:
            module = load_parse_module(root)
            parsed_log = module.parse_log(train_log_path)
            add(results, "PASS", "train.log parse", "parsed via scripts/experiments/parse_train_log.py")
        except Exception as exc:  # pragma: no cover - defensive preflight
            add(results, "FAIL", "train.log parse", f"could not parse training log: {exc}")
            failed = True

    artifact_total = None
    artifact_source = None
    if submission_data is not None and isinstance(submission_data.get("bytes_total"), (int, float)):
        artifact_total = int(submission_data["bytes_total"])
        artifact_source = "submission.json bytes_total"
    elif parsed_log is not None:
        if parsed_log.get("total_submission_size_int8_zlib_bytes") is not None:
            artifact_total = int(parsed_log["total_submission_size_int8_zlib_bytes"])
            artifact_source = "train.log total_submission_size_int8_zlib_bytes"
        elif parsed_log.get("total_submission_size_bytes") is not None:
            artifact_total = int(parsed_log["total_submission_size_bytes"])
            artifact_source = "train.log total_submission_size_bytes"
    if artifact_total is None:
        add(results, "FAIL", "artifact size", "could not determine total artifact bytes from submission.json or train.log")
        failed = True
    elif artifact_total <= args.artifact_cap:
        add(results, "PASS", "artifact size", f"{artifact_total} <= {args.artifact_cap} ({artifact_source})")
    else:
        add(results, "FAIL", "artifact size", f"{artifact_total} > {args.artifact_cap} ({artifact_source})")
        failed = True

    code_bytes = None
    if submission_data is not None and isinstance(submission_data.get("bytes_code"), (int, float)):
        code_bytes = int(submission_data["bytes_code"])
    elif parsed_log is not None and parsed_log.get("code_bytes") is not None:
        code_bytes = int(parsed_log["code_bytes"])
    if code_bytes is not None:
        add(results, "PASS", "code bytes", str(code_bytes))
    else:
        add(results, "WARN", "code bytes", "could not determine bytes_code from submission.json or train.log")

    for filename in ("train_gpt.py", "train_gpt_mlx.py"):
        path = candidate_dir / filename
        if path.exists():
            count = line_count(path)
            if count <= 1500:
                add(results, "PASS", f"line limit: {filename}", f"{count} <= 1500")
            else:
                add(results, "FAIL", f"line limit: {filename}", f"{count} > 1500")
                failed = True

    if submission_data is not None:
        required_nonempty = ("author", "github_id", "name", "blurb", "date")
        for field in required_nonempty:
            value = submission_data.get(field)
            if isinstance(value, str) and value.strip():
                add(results, "PASS", f"metadata: {field}", "present")
            else:
                add(results, "FAIL", f"metadata: {field}", "missing or blank")
                failed = True
        for field in ("val_loss", "val_bpb", "bytes_total", "bytes_code"):
            value = submission_data.get(field)
            if isinstance(value, (int, float)):
                add(results, "PASS", f"metadata: {field}", str(value))
            else:
                add(results, "FAIL", f"metadata: {field}", "missing numeric value")
                failed = True

    self_contained_warnings, self_contained_failures = looks_self_contained(candidate_dir)
    if self_contained_failures:
        for item in self_contained_failures:
            add(results, "FAIL", "self-contained", item)
        failed = True
    else:
        add(results, "PASS", "self-contained", "no missing packaged relative imports detected")
    for item in self_contained_warnings:
        add(results, "WARN", "self-contained", item)

    git_warnings = core_git_warnings(root)
    if git_warnings:
        add(
            results,
            "WARN",
            "core file packaging",
            "modified core files outside /records: " + ", ".join(git_warnings),
        )
    else:
        add(results, "PASS", "core file packaging", "no modified core files detected outside /records")

    for result in results:
        print(f"[{result.status}] {result.label}: {result.detail}")

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
