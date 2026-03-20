#!/usr/bin/env python3
"""Create a timestamped local candidate folder under /records."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


TRACK_ALIASES = {
    "record": "track_10min_16mb",
    "non-record": "track_non_record_16mb",
    "non_record": "track_non_record_16mb",
}
CORE_WARNING_PREFIXES = (
    "README.md",
    "train_gpt.py",
    "train_gpt_mlx.py",
    "data/",
    "requirements.txt",
)


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def default_templates(root: Path) -> tuple[Path, Path]:
    return (
        root / "templates" / "submission_README_template.md",
        root / "templates" / "submission_json_template.json",
    )


def normalize_track(value: str) -> str:
    resolved = TRACK_ALIASES.get(value, value)
    if resolved not in {"track_10min_16mb", "track_non_record_16mb"}:
        raise argparse.ArgumentTypeError(
            "track must be one of: track_10min_16mb, track_non_record_16mb, record, non-record"
        )
    return resolved


def slugify(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", value.strip())
    cleaned = cleaned.strip("._-")
    if not cleaned:
        raise argparse.ArgumentTypeError("slug must contain at least one letter or number")
    return cleaned


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


def copy_file(src: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)


def candidate_relative_copy_target(src: Path, root: Path, candidate_dir: Path) -> Path:
    try:
        rel = src.resolve().relative_to(root.resolve())
    except ValueError:
        rel = Path(src.name)
    if rel.parts and rel.parts[0] == "records":
        rel = Path(src.name)
    return candidate_dir / rel


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--track",
        required=True,
        type=normalize_track,
        help="Target records track: track_10min_16mb, track_non_record_16mb, record, or non-record.",
    )
    parser.add_argument(
        "--slug",
        required=True,
        type=slugify,
        help="Short candidate suffix used after YYYY-MM-DD in the folder name.",
    )
    parser.add_argument(
        "--script",
        required=True,
        type=Path,
        help="Path to the exact training script snapshot to package.",
    )
    parser.add_argument(
        "--target-script-name",
        default="train_gpt.py",
        help="Filename to use inside the candidate folder. Default: train_gpt.py",
    )
    parser.add_argument(
        "--log",
        type=Path,
        default=None,
        help="Primary training log to copy into the candidate folder as train.log.",
    )
    parser.add_argument(
        "--dependency",
        action="append",
        type=Path,
        default=[],
        help="Extra dependency to copy into the candidate folder. Can be passed multiple times.",
    )
    parser.add_argument(
        "--extra-log",
        action="append",
        type=Path,
        default=[],
        help="Extra log to copy into the candidate folder's logs/ directory. Can be passed multiple times.",
    )
    parser.add_argument(
        "--metadata-file",
        action="append",
        type=Path,
        default=[],
        help="Extra metadata file to copy into metadata/. Can be passed multiple times.",
    )
    parser.add_argument(
        "--readme-template",
        type=Path,
        default=None,
        help="Override the README template path.",
    )
    parser.add_argument(
        "--submission-template",
        type=Path,
        default=None,
        help="Override the submission.json template path.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    root = repo_root()
    readme_template, submission_template = default_templates(root)
    if args.readme_template is not None:
        readme_template = args.readme_template
    if args.submission_template is not None:
        submission_template = args.submission_template

    source_script = (root / args.script).resolve() if not args.script.is_absolute() else args.script.resolve()
    if not source_script.is_file():
        print(f"error: script not found: {source_script}", file=sys.stderr)
        return 1
    if not readme_template.is_file():
        print(f"error: README template not found: {readme_template}", file=sys.stderr)
        return 1
    if not submission_template.is_file():
        print(f"error: submission template not found: {submission_template}", file=sys.stderr)
        return 1

    date_prefix = datetime.now().strftime("%Y-%m-%d")
    candidate_name = f"{date_prefix}_{args.slug}"
    candidate_dir = root / "records" / args.track / candidate_name
    if candidate_dir.exists():
        print(f"error: candidate folder already exists: {candidate_dir}", file=sys.stderr)
        return 1

    candidate_dir.mkdir(parents=True)
    (candidate_dir / "logs").mkdir()
    (candidate_dir / "metadata").mkdir()

    target_script = candidate_dir / args.target_script_name
    copy_file(source_script, target_script)

    copied_dependencies: list[str] = []
    for dep in args.dependency:
        dep_path = (root / dep).resolve() if not dep.is_absolute() else dep.resolve()
        if not dep_path.is_file():
            print(f"error: dependency not found: {dep_path}", file=sys.stderr)
            return 1
        dest = candidate_relative_copy_target(dep_path, root, candidate_dir)
        copy_file(dep_path, dest)
        copied_dependencies.append(str(dest.relative_to(candidate_dir)).replace("\\", "/"))

    if args.log is not None:
        source_log = (root / args.log).resolve() if not args.log.is_absolute() else args.log.resolve()
        if not source_log.is_file():
            print(f"error: log not found: {source_log}", file=sys.stderr)
            return 1
        copy_file(source_log, candidate_dir / "train.log")
        source_log_str = str(source_log)
    else:
        source_log_str = None

    copied_extra_logs: list[str] = []
    for log in args.extra_log:
        log_path = (root / log).resolve() if not log.is_absolute() else log.resolve()
        if not log_path.is_file():
            print(f"error: extra log not found: {log_path}", file=sys.stderr)
            return 1
        dest = candidate_dir / "logs" / log_path.name
        copy_file(log_path, dest)
        copied_extra_logs.append(str(dest.relative_to(candidate_dir)).replace("\\", "/"))

    copied_metadata: list[str] = []
    for item in args.metadata_file:
        item_path = (root / item).resolve() if not item.is_absolute() else item.resolve()
        if not item_path.is_file():
            print(f"error: metadata file not found: {item_path}", file=sys.stderr)
            return 1
        dest = candidate_dir / "metadata" / item_path.name
        copy_file(item_path, dest)
        copied_metadata.append(str(dest.relative_to(candidate_dir)).replace("\\", "/"))

    readme_text = readme_template.read_text(encoding="utf-8")
    (candidate_dir / "README.md").write_text(readme_text, encoding="utf-8")

    submission_text = submission_template.read_text(encoding="utf-8")
    (candidate_dir / "submission.json").write_text(submission_text + ("\n" if not submission_text.endswith("\n") else ""), encoding="utf-8")

    git_head = git_output(root, "rev-parse", "HEAD")
    git_warnings = core_git_warnings(root)
    manifest = {
        "candidate_dir": str(candidate_dir.relative_to(root)).replace("\\", "/"),
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "track": args.track,
        "source_script": str(source_script),
        "target_script": args.target_script_name,
        "source_log": source_log_str,
        "declared_dependencies": copied_dependencies,
        "extra_logs": copied_extra_logs,
        "metadata_files": copied_metadata,
        "git_head": git_head,
        "git_core_warnings": git_warnings,
    }
    (candidate_dir / "metadata" / "candidate_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print(f"created: {candidate_dir}")
    print(f"script snapshot: {target_script.relative_to(root)}")
    if source_log_str is None:
        print("warning: no primary train log was copied; preflight will fail until train.log exists")
    if git_warnings:
        print("warning: modified core files detected outside /records:")
        for item in git_warnings:
            print(f"  - {item}")
    print(f"next: python scripts/submission/preflight_submission.py {candidate_dir.relative_to(root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
