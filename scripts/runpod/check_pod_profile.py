#!/usr/bin/env python3
"""Check a Runpod pod against a declared control-profile policy."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]


def run_runpodctl(*args: str) -> dict[str, Any]:
    cmd = ["runpodctl", *args]
    try:
        output = subprocess.check_output(cmd, cwd=ROOT, text=True)
    except subprocess.CalledProcessError as exc:
        raise SystemExit(exc.output.strip() or str(exc)) from exc
    return json.loads(output)


def normalize(pod: dict[str, Any]) -> dict[str, Any]:
    machine = pod.get("machine") or {}
    return {
        "pod_id": str(pod.get("id", "")),
        "pod_name": str(pod.get("name", "")),
        "gpu_id": str(machine.get("gpuId", "")),
        "gpu_count": int(pod.get("gpuCount", 0) or 0),
        "image_name": str(pod.get("imageName", "")),
        "container_disk_gb": int(pod.get("containerDiskInGb", 0) or 0),
        "volume_gb": int(pod.get("volumeInGb", 0) or 0),
        "memory_gb": int(pod.get("memoryInGb", 0) or 0),
        "vcpu_count": int(pod.get("vcpuCount", 0) or 0),
        "data_center_id": str(machine.get("dataCenterId", "")),
        "location": str(machine.get("location", "")),
        "secure_cloud": bool(machine.get("secureCloud", False)),
        "cost_per_hr_usd": float(pod.get("costPerHr", 0.0) or 0.0),
        "desired_status": str(pod.get("desiredStatus", "")),
    }


def compare(profile: dict[str, Any], actual: dict[str, Any]) -> list[str]:
    mismatches: list[str] = []

    exact_keys = [
        "gpu_id",
        "gpu_count",
        "image_name",
        "container_disk_gb",
        "volume_gb",
        "memory_gb",
        "secure_cloud",
    ]
    for key in exact_keys:
        if key in profile and actual.get(key) != profile.get(key):
            mismatches.append(f"{key}: expected {profile.get(key)!r}, got {actual.get(key)!r}")

    if "min_vcpu_count" in profile and actual.get("vcpu_count", 0) < int(profile["min_vcpu_count"]):
        mismatches.append(
            f"vcpu_count: expected at least {int(profile['min_vcpu_count'])}, got {actual.get('vcpu_count')!r}"
        )

    if "allowed_data_center_ids" in profile:
        allowed = {str(value) for value in profile["allowed_data_center_ids"]}
        if actual.get("data_center_id") not in allowed:
            mismatches.append(
                f"data_center_id: expected one of {sorted(allowed)!r}, got {actual.get('data_center_id')!r}"
            )

    if "allowed_locations" in profile:
        allowed_locations = {str(value) for value in profile["allowed_locations"]}
        if actual.get("location") not in allowed_locations:
            mismatches.append(
                f"location: expected one of {sorted(allowed_locations)!r}, got {actual.get('location')!r}"
            )

    return mismatches


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pod-id", required=True)
    parser.add_argument("--profile-json", type=Path, required=True)
    parser.add_argument("--json-out", type=Path)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    profile = json.loads(args.profile_json.read_text(encoding="utf-8"))
    pod = run_runpodctl("pod", "get", args.pod_id, "--include-machine")
    actual = normalize(pod)
    mismatches = compare(profile, actual)
    result = {
        "profile_label": profile.get("profile_label", ""),
        "profile_path": str(args.profile_json.resolve()),
        "matches": not mismatches,
        "mismatches": mismatches,
        "actual": actual,
    }
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.json_out is not None:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(text, encoding="utf-8")
    sys.stdout.write(text)
    return 0 if not mismatches else 1


if __name__ == "__main__":
    raise SystemExit(main())
