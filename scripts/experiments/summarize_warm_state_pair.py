#!/usr/bin/env python3
"""Summarize a paired same-pod warm-state control test."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def maybe_delta(first: Any, second: Any) -> float | int | None:
    if first is None or second is None:
        return None
    if isinstance(first, int) and isinstance(second, int):
        return int(second) - int(first)
    return float(second) - float(first)


def wrapper_sha(provenance: dict[str, Any]) -> str:
    wrappers = provenance.get("wrappers") or []
    if not wrappers:
        return ""
    return str(wrappers[0].get("sha256", ""))


def extract_run(summary: dict[str, Any], provenance: dict[str, Any]) -> dict[str, Any]:
    host = provenance.get("host") or {}
    git = provenance.get("git") or {}
    dataset = provenance.get("dataset") or {}
    tokenizer = provenance.get("tokenizer") or {}
    code = provenance.get("code") or {}
    host_python = host.get("python") or {}
    return {
        "run_id": provenance.get("run_id", ""),
        "run_dir": provenance.get("run_dir", ""),
        "git_commit_sha": git.get("commit_sha", ""),
        "git_dirty": bool(git.get("dirty", False)),
        "final_val_loss": summary.get("final_val_loss"),
        "final_val_bpb": summary.get("final_val_bpb"),
        "stop_step": summary.get("stop_step"),
        "stop_train_time_ms": summary.get("stop_train_time_ms"),
        "step_avg_ms": summary.get("last_logged_step_avg_ms"),
        "final_eval_time_ms": summary.get("final_eval_time_ms"),
        "total_submission_size_int8_zlib_bytes": summary.get("total_submission_size_int8_zlib_bytes"),
        "code_sha256": code.get("sha256", ""),
        "wrapper_sha256": wrapper_sha(provenance),
        "dataset_manifest_sha256": dataset.get("manifest_sha256", ""),
        "tokenizer_sha256": tokenizer.get("sha256", ""),
        "host_fingerprint_sha256": host.get("fingerprint_sha256", ""),
        "hostname": host.get("hostname", ""),
        "gpu_names": host.get("gpu_names") or [],
        "gpu_query_rows": host.get("gpu_query_rows") or [],
        "vcpu_count": host.get("vcpu_count"),
        "python_version": host_python.get("python_version", ""),
        "torch_version": host_python.get("torch_version", ""),
        "torch_cuda_version": host_python.get("torch_cuda_version", ""),
    }


def build_report(pair_label: str, first: dict[str, Any], second: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "pair_label": pair_label,
        "run_1": first,
        "run_2": second,
        "comparison": {
            "delta_val_loss": maybe_delta(first.get("final_val_loss"), second.get("final_val_loss")),
            "delta_val_bpb": maybe_delta(first.get("final_val_bpb"), second.get("final_val_bpb")),
            "delta_stop_step": maybe_delta(first.get("stop_step"), second.get("stop_step")),
            "delta_stop_train_time_ms": maybe_delta(first.get("stop_train_time_ms"), second.get("stop_train_time_ms")),
            "delta_step_avg_ms": maybe_delta(first.get("step_avg_ms"), second.get("step_avg_ms")),
            "delta_final_eval_time_ms": maybe_delta(first.get("final_eval_time_ms"), second.get("final_eval_time_ms")),
            "delta_total_submission_size_int8_zlib_bytes": maybe_delta(
                first.get("total_submission_size_int8_zlib_bytes"),
                second.get("total_submission_size_int8_zlib_bytes"),
            ),
            "same_git_commit_sha": first.get("git_commit_sha") == second.get("git_commit_sha"),
            "same_code_sha256": first.get("code_sha256") == second.get("code_sha256"),
            "same_wrapper_sha256": first.get("wrapper_sha256") == second.get("wrapper_sha256"),
            "same_dataset_manifest_sha256": first.get("dataset_manifest_sha256") == second.get("dataset_manifest_sha256"),
            "same_tokenizer_sha256": first.get("tokenizer_sha256") == second.get("tokenizer_sha256"),
            "same_host_fingerprint_sha256": first.get("host_fingerprint_sha256") == second.get("host_fingerprint_sha256"),
        },
    }


def fmt_float(value: Any) -> str:
    if value is None:
        return "n/a"
    return f"{float(value):.8f}"


def fmt_delta(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, int):
        return f"{value:+d}"
    return f"{float(value):+.8f}"


def render_markdown(report: dict[str, Any]) -> str:
    run_1 = report["run_1"]
    run_2 = report["run_2"]
    comparison = report["comparison"]
    lines = [
        "# Warm-State Pair Summary",
        "",
        f"- `pair_label`: `{report['pair_label']}`",
        "",
        "## Run 1",
        "",
        f"- `run_id`: `{run_1['run_id']}`",
        f"- `val_bpb`: `{fmt_float(run_1['final_val_bpb'])}`",
        f"- `val_loss`: `{fmt_float(run_1['final_val_loss'])}`",
        f"- `stop_step`: `{run_1['stop_step']}`",
        f"- `step_avg_ms`: `{fmt_float(run_1['step_avg_ms'])}`",
        f"- `bytes_total_int8_zlib`: `{run_1['total_submission_size_int8_zlib_bytes']}`",
        f"- `host_fingerprint_sha256`: `{run_1['host_fingerprint_sha256']}`",
        "",
        "## Run 2",
        "",
        f"- `run_id`: `{run_2['run_id']}`",
        f"- `val_bpb`: `{fmt_float(run_2['final_val_bpb'])}`",
        f"- `val_loss`: `{fmt_float(run_2['final_val_loss'])}`",
        f"- `stop_step`: `{run_2['stop_step']}`",
        f"- `step_avg_ms`: `{fmt_float(run_2['step_avg_ms'])}`",
        f"- `bytes_total_int8_zlib`: `{run_2['total_submission_size_int8_zlib_bytes']}`",
        f"- `host_fingerprint_sha256`: `{run_2['host_fingerprint_sha256']}`",
        "",
        "## Comparison",
        "",
        f"- `delta_val_bpb`: `{fmt_delta(comparison['delta_val_bpb'])}`",
        f"- `delta_val_loss`: `{fmt_delta(comparison['delta_val_loss'])}`",
        f"- `delta_stop_step`: `{fmt_delta(comparison['delta_stop_step'])}`",
        f"- `delta_step_avg_ms`: `{fmt_delta(comparison['delta_step_avg_ms'])}`",
        f"- `delta_bytes_total_int8_zlib`: `{fmt_delta(comparison['delta_total_submission_size_int8_zlib_bytes'])}`",
        f"- `same_code_sha256`: `{comparison['same_code_sha256']}`",
        f"- `same_wrapper_sha256`: `{comparison['same_wrapper_sha256']}`",
        f"- `same_dataset_manifest_sha256`: `{comparison['same_dataset_manifest_sha256']}`",
        f"- `same_tokenizer_sha256`: `{comparison['same_tokenizer_sha256']}`",
        f"- `same_host_fingerprint_sha256`: `{comparison['same_host_fingerprint_sha256']}`",
        "",
    ]
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pair-label", required=True)
    parser.add_argument("--run-1-summary", type=Path, required=True)
    parser.add_argument("--run-1-provenance", type=Path, required=True)
    parser.add_argument("--run-2-summary", type=Path, required=True)
    parser.add_argument("--run-2-provenance", type=Path, required=True)
    parser.add_argument("--json-out", type=Path, required=True)
    parser.add_argument("--md-out", type=Path, required=True)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    run_1 = extract_run(load_json(args.run_1_summary), load_json(args.run_1_provenance))
    run_2 = extract_run(load_json(args.run_2_summary), load_json(args.run_2_provenance))
    report = build_report(args.pair_label, run_1, run_2)
    markdown = render_markdown(report)

    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.md_out.write_text(markdown + "\n", encoding="utf-8")
    print(markdown)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
