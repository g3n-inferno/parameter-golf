#!/usr/bin/env python3
"""Write a reproducibility manifest for a baseline-style training run."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import socket
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_output(repo_dir: Path, *args: str) -> str:
    try:
        proc = subprocess.run(
            ["git", *args],
            cwd=repo_dir,
            capture_output=True,
            text=True,
            check=True,
        )
    except Exception:
        return ""
    return proc.stdout.strip()


def command_output(*args: str) -> str:
    try:
        proc = subprocess.run(
            list(args),
            capture_output=True,
            text=True,
            check=True,
        )
    except Exception:
        return ""
    return proc.stdout.strip()


def dataset_entries(data_path: Path, pattern: str) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for shard in sorted(data_path.glob(pattern)):
        entries.append(
            {
                "name": shard.name,
                "size_bytes": int(shard.stat().st_size),
            }
        )
    return entries


def select_dataset_hash_targets(
    train_entries: list[dict[str, Any]],
    val_entries: list[dict[str, Any]],
) -> list[str]:
    selected: list[str] = []
    if train_entries:
        selected.append(train_entries[0]["name"])
        if len(train_entries) > 1:
            selected.append(train_entries[-1]["name"])
    if val_entries:
        selected.append(val_entries[0]["name"])
    return selected


def load_compare_json(path: Path, label: str | None) -> dict[str, Any]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    return {
        "path": str(path.resolve()),
        "sha256": sha256_file(path),
        "label": label or path.stem,
        "baseline_label": obj.get("baseline_label"),
        "source_run_id": obj.get("source_run_id"),
        "source_commit_sha": obj.get("source_commit_sha"),
        "source_commit_sha_inferred": obj.get("source_commit_sha_inferred"),
        "log_path": obj.get("log_path"),
        "final_val_loss": obj.get("final_val_loss"),
        "final_val_bpb": obj.get("final_val_bpb"),
        "total_submission_size_int8_zlib_bytes": obj.get("total_submission_size_int8_zlib_bytes"),
        "anchor_status": obj.get("anchor_status"),
        "provenance_status": obj.get("provenance_status"),
        "raw_log_present": obj.get("raw_log_present"),
        "raw_result_packet_present": obj.get("raw_result_packet_present"),
        "requires_rebuild_before_ablation": obj.get("requires_rebuild_before_ablation"),
        "compatibility_note": obj.get("compatibility_note"),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--repo-dir", type=Path, required=True)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--log-file", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--code-path", type=Path, required=True)
    parser.add_argument("--wrapper-path", action="append", type=Path, default=[])
    parser.add_argument("--exact-command", required=True)
    parser.add_argument("--target-gpu-label", default="")
    parser.add_argument("--hardware", default="")
    parser.add_argument("--dataset-variant", default="")
    parser.add_argument("--dataset-path", type=Path, required=True)
    parser.add_argument("--expected-train-shards", type=int, default=0)
    parser.add_argument("--tokenizer-variant", default="")
    parser.add_argument("--tokenizer-path", type=Path, required=True)
    parser.add_argument("--core-hparams", default="")
    parser.add_argument("--track-intent", default="")
    parser.add_argument("--wallclock-target", default="")
    parser.add_argument("--compare-json", type=Path, default=None)
    parser.add_argument("--compare-label", default=None)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    repo_dir = args.repo_dir.resolve()
    run_dir = args.run_dir.resolve()
    log_file = args.log_file.resolve()
    code_path = args.code_path.resolve()
    data_path = args.dataset_path.resolve()
    tokenizer_path = args.tokenizer_path.resolve()

    train_entries = dataset_entries(data_path, "fineweb_train_*.bin")
    val_entries = dataset_entries(data_path, "fineweb_val_*.bin")
    if args.expected_train_shards and len(train_entries) != args.expected_train_shards:
        raise SystemExit(
            f"expected {args.expected_train_shards} train shards under {data_path}, found {len(train_entries)}"
        )
    if not val_entries:
        raise SystemExit(f"no validation shards found under {data_path}")
    if not tokenizer_path.is_file():
        raise SystemExit(f"tokenizer not found: {tokenizer_path}")
    if not code_path.is_file():
        raise SystemExit(f"code path not found: {code_path}")

    manifest_payload = {
        "train": train_entries,
        "val": val_entries,
    }
    manifest_sha = sha256_bytes(json.dumps(manifest_payload, sort_keys=True).encode("utf-8"))
    hash_target_names = set(select_dataset_hash_targets(train_entries, val_entries))
    hash_entries: list[dict[str, Any]] = []
    for entry in train_entries + val_entries:
        if entry["name"] not in hash_target_names:
            continue
        shard_path = data_path / entry["name"]
        hash_entries.append(
            {
                "name": entry["name"],
                "size_bytes": entry["size_bytes"],
                "sha256": sha256_file(shard_path),
            }
        )

    wrapper_entries = []
    for wrapper_path in args.wrapper_path:
        wrapper = wrapper_path.resolve()
        if not wrapper.is_file():
            raise SystemExit(f"wrapper path not found: {wrapper}")
        wrapper_entries.append(
            {
                "path": str(wrapper),
                "bytes": int(wrapper.stat().st_size),
                "sha256": sha256_file(wrapper),
            }
        )

    compare_json = None
    if args.compare_json is not None:
        compare_json = load_compare_json(args.compare_json.resolve(), args.compare_label)

    git_status = git_output(repo_dir, "status", "--short")
    manifest = {
        "schema_version": 1,
        "created_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "run_id": args.run_id,
        "run_dir": str(run_dir),
        "log_file": str(log_file),
        "repo_dir": str(repo_dir),
        "exact_command": args.exact_command,
        "target_gpu_label": args.target_gpu_label,
        "hardware": args.hardware,
        "dataset_variant": args.dataset_variant,
        "tokenizer_variant": args.tokenizer_variant,
        "core_hparams": args.core_hparams,
        "track_intent": args.track_intent,
        "wallclock_target": args.wallclock_target,
        "git": {
            "branch": git_output(repo_dir, "branch", "--show-current"),
            "commit_sha": git_output(repo_dir, "rev-parse", "HEAD"),
            "dirty": bool(git_status),
            "status_short": git_status.splitlines(),
        },
        "code": {
            "path": str(code_path),
            "bytes": int(code_path.stat().st_size),
            "sha256": sha256_file(code_path),
        },
        "wrappers": wrapper_entries,
        "dataset": {
            "path": str(data_path),
            "expected_train_shards": args.expected_train_shards,
            "train_shards_found": len(train_entries),
            "val_shards_found": len(val_entries),
            "train_total_bytes": sum(entry["size_bytes"] for entry in train_entries),
            "val_total_bytes": sum(entry["size_bytes"] for entry in val_entries),
            "manifest_sha256": manifest_sha,
            "manifest_fields": ["name", "size_bytes"],
            "sentinel_shard_hashes": hash_entries,
        },
        "tokenizer": {
            "path": str(tokenizer_path),
            "size_bytes": int(tokenizer_path.stat().st_size),
            "sha256": sha256_file(tokenizer_path),
        },
        "compare_json": compare_json,
        "host": {
            "hostname": socket.gethostname(),
            "gpu_names": [line for line in command_output("nvidia-smi", "--query-gpu=name", "--format=csv,noheader").splitlines() if line],
            "gpu_count": len([line for line in command_output("nvidia-smi", "--query-gpu=name", "--format=csv,noheader").splitlines() if line]),
            "vcpu_count": os.cpu_count(),
        },
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(f"wrote {args.output}")
    print(f"git_commit_sha={manifest['git']['commit_sha']}")
    print(f"code_sha256={manifest['code']['sha256']}")
    print(f"dataset_manifest_sha256={manifest['dataset']['manifest_sha256']}")
    print(f"tokenizer_sha256={manifest['tokenizer']['sha256']}")
    if compare_json is not None:
        print(f"compare_json_sha256={compare_json['sha256']}")
        print(f"compare_json_anchor_status={compare_json.get('anchor_status') or ''}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
