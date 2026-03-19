#!/usr/bin/env python3
"""Parse Parameter Golf training logs into a short summary and JSON payload."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


STEP_VAL_RE = re.compile(
    r"step:(?P<step>\d+)/(?P<iterations>\d+)\s+"
    r"val_loss:(?P<val_loss>[0-9.]+)\s+val_bpb:(?P<val_bpb>[0-9.]+)\s+"
    r"train_time:(?P<train_time_ms>[0-9.]+)ms\s+step_avg:(?P<step_avg_ms>[0-9.]+)ms"
)
STEP_TRAIN_RE = re.compile(
    r"step:(?P<step>\d+)/(?P<iterations>\d+)\s+train_loss:(?P<train_loss>[0-9.]+)\s+"
    r"train_time:(?P<train_time_ms>[0-9.]+)ms\s+step_avg:(?P<step_avg_ms>[0-9.]+)ms"
)
FINAL_EXACT_RE = re.compile(
    r"final_int8_zlib_roundtrip_exact\s+val_loss:(?P<val_loss>[0-9.]+)\s+val_bpb:(?P<val_bpb>[0-9.]+)"
)
FINAL_RE = re.compile(
    r"final_int8_zlib_roundtrip\s+val_loss:(?P<val_loss>[0-9.]+)\s+val_bpb:(?P<val_bpb>[0-9.]+)\s+"
    r"eval_time:(?P<eval_time_ms>[0-9.]+)ms"
)
STOP_RE = re.compile(
    r"stopping_early:\s+(?P<reason>\S+)\s+train_time:(?P<train_time_ms>[0-9.]+)ms\s+"
    r"step:(?P<step>\d+)/(?P<iterations>\d+)"
)
PEAK_MEM_RE = re.compile(
    r"peak memory allocated:\s+(?P<allocated_mib>\d+)\s+MiB\s+reserved:\s+(?P<reserved_mib>\d+)\s+MiB"
)
MODEL_BYTES_RE = re.compile(r"Serialized model:\s+(?P<bytes>\d+)\s+bytes")
MODEL_INT8_RE = re.compile(r"Serialized model int8\+zlib:\s+(?P<bytes>\d+)\s+bytes")
CODE_BYTES_RE = re.compile(r"Code size:\s+(?P<bytes>\d+)\s+bytes")
TOTAL_BYTES_RE = re.compile(r"Total submission size:\s+(?P<bytes>\d+)\s+bytes")
TOTAL_INT8_RE = re.compile(r"Total submission size int8\+zlib:\s+(?P<bytes>\d+)\s+bytes")


def _maybe_float(value: str | None) -> float | None:
    return None if value is None else float(value)


def _maybe_int(value: str | None) -> int | None:
    return None if value is None else int(float(value))


def parse_log(path: Path) -> dict:
    result: dict[str, object] = {
        "log_path": str(path.resolve()),
        "final_val_loss": None,
        "final_val_bpb": None,
        "final_metric_source": None,
        "final_eval_time_ms": None,
        "last_step": None,
        "iterations": None,
        "last_logged_train_time_ms": None,
        "last_logged_step_avg_ms": None,
        "stop_reason": None,
        "stop_step": None,
        "stop_train_time_ms": None,
        "peak_memory_allocated_mib": None,
        "peak_memory_reserved_mib": None,
        "model_bytes": None,
        "model_int8_zlib_bytes": None,
        "code_bytes": None,
        "total_submission_size_bytes": None,
        "total_submission_size_int8_zlib_bytes": None,
    }

    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if match := STEP_VAL_RE.search(line):
            result["last_step"] = _maybe_int(match.group("step"))
            result["iterations"] = _maybe_int(match.group("iterations"))
            result["last_logged_train_time_ms"] = _maybe_int(match.group("train_time_ms"))
            result["last_logged_step_avg_ms"] = _maybe_float(match.group("step_avg_ms"))
            if result["final_metric_source"] in {None, "last_step_val"}:
                result["final_val_loss"] = _maybe_float(match.group("val_loss"))
                result["final_val_bpb"] = _maybe_float(match.group("val_bpb"))
                result["final_metric_source"] = "last_step_val"
            continue

        if match := STEP_TRAIN_RE.search(line):
            result["last_step"] = _maybe_int(match.group("step"))
            result["iterations"] = _maybe_int(match.group("iterations"))
            result["last_logged_train_time_ms"] = _maybe_int(match.group("train_time_ms"))
            result["last_logged_step_avg_ms"] = _maybe_float(match.group("step_avg_ms"))
            continue

        if match := FINAL_EXACT_RE.search(line):
            result["final_val_loss"] = _maybe_float(match.group("val_loss"))
            result["final_val_bpb"] = _maybe_float(match.group("val_bpb"))
            result["final_metric_source"] = "final_int8_zlib_roundtrip_exact"
            continue

        if match := FINAL_RE.search(line):
            if result["final_metric_source"] != "final_int8_zlib_roundtrip_exact":
                result["final_val_loss"] = _maybe_float(match.group("val_loss"))
                result["final_val_bpb"] = _maybe_float(match.group("val_bpb"))
                result["final_metric_source"] = "final_int8_zlib_roundtrip"
            result["final_eval_time_ms"] = _maybe_int(match.group("eval_time_ms"))
            continue

        if match := STOP_RE.search(line):
            result["stop_reason"] = match.group("reason")
            result["stop_step"] = _maybe_int(match.group("step"))
            result["iterations"] = _maybe_int(match.group("iterations"))
            result["stop_train_time_ms"] = _maybe_int(match.group("train_time_ms"))
            continue

        if match := PEAK_MEM_RE.search(line):
            result["peak_memory_allocated_mib"] = _maybe_int(match.group("allocated_mib"))
            result["peak_memory_reserved_mib"] = _maybe_int(match.group("reserved_mib"))
            continue

        if match := MODEL_BYTES_RE.search(line):
            result["model_bytes"] = _maybe_int(match.group("bytes"))
            continue

        if match := MODEL_INT8_RE.search(line):
            result["model_int8_zlib_bytes"] = _maybe_int(match.group("bytes"))
            continue

        if match := CODE_BYTES_RE.search(line):
            result["code_bytes"] = _maybe_int(match.group("bytes"))
            continue

        if match := TOTAL_BYTES_RE.search(line):
            result["total_submission_size_bytes"] = _maybe_int(match.group("bytes"))
            continue

        if match := TOTAL_INT8_RE.search(line):
            result["total_submission_size_int8_zlib_bytes"] = _maybe_int(match.group("bytes"))
            continue

    return result


def format_summary(parsed: dict, label: str | None = None) -> str:
    title = label or Path(parsed["log_path"]).name
    lines = [f"log: {title}"]

    if parsed["final_val_loss"] is not None:
        lines.append(
            "final metrics: "
            f"val_loss={parsed['final_val_loss']:.8f} "
            f"val_bpb={parsed['final_val_bpb']:.8f} "
            f"source={parsed['final_metric_source']}"
        )
    else:
        lines.append("final metrics: unavailable")

    if parsed["model_bytes"] is not None or parsed["model_int8_zlib_bytes"] is not None:
        lines.append(
            "artifact bytes: "
            f"model_raw={parsed['model_bytes'] if parsed['model_bytes'] is not None else 'n/a'} "
            f"model_int8_zlib={parsed['model_int8_zlib_bytes'] if parsed['model_int8_zlib_bytes'] is not None else 'n/a'} "
            f"code={parsed['code_bytes'] if parsed['code_bytes'] is not None else 'n/a'} "
            f"total_raw={parsed['total_submission_size_bytes'] if parsed['total_submission_size_bytes'] is not None else 'n/a'} "
            f"total_int8_zlib={parsed['total_submission_size_int8_zlib_bytes'] if parsed['total_submission_size_int8_zlib_bytes'] is not None else 'n/a'}"
        )
    else:
        lines.append("artifact bytes: unavailable")

    wallclock_bits: list[str] = []
    if parsed["stop_reason"] is not None:
        wallclock_bits.append(f"stop_reason={parsed['stop_reason']}")
    if parsed["stop_train_time_ms"] is not None:
        wallclock_bits.append(f"stop_train_time_ms={parsed['stop_train_time_ms']}")
    elif parsed["last_logged_train_time_ms"] is not None:
        wallclock_bits.append(f"last_logged_train_time_ms={parsed['last_logged_train_time_ms']}")
    if parsed["stop_step"] is not None:
        wallclock_bits.append(f"stop_step={parsed['stop_step']}")
    elif parsed["last_step"] is not None:
        wallclock_bits.append(f"last_step={parsed['last_step']}")
    if parsed["iterations"] is not None:
        wallclock_bits.append(f"iterations={parsed['iterations']}")
    if parsed["last_logged_step_avg_ms"] is not None:
        wallclock_bits.append(f"step_avg_ms={parsed['last_logged_step_avg_ms']:.2f}")
    if parsed["final_eval_time_ms"] is not None:
        wallclock_bits.append(f"final_eval_time_ms={parsed['final_eval_time_ms']}")
    lines.append("wallclock: " + (" ".join(wallclock_bits) if wallclock_bits else "unavailable"))

    if parsed["peak_memory_allocated_mib"] is not None or parsed["peak_memory_reserved_mib"] is not None:
        lines.append(
            "peak memory: "
            f"allocated_mib={parsed['peak_memory_allocated_mib'] if parsed['peak_memory_allocated_mib'] is not None else 'n/a'} "
            f"reserved_mib={parsed['peak_memory_reserved_mib'] if parsed['peak_memory_reserved_mib'] is not None else 'n/a'}"
        )
    else:
        lines.append("peak memory: unavailable")

    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("log_path", type=Path, help="Path to a training log or wrapper log.")
    parser.add_argument("--json-out", type=Path, default=None, help="Write parsed fields as JSON.")
    parser.add_argument("--summary-out", type=Path, default=None, help="Write the human summary to a file.")
    parser.add_argument("--label", default=None, help="Optional label to use in the summary header.")
    parser.add_argument(
        "--require-final-metrics",
        action="store_true",
        help="Exit non-zero if no final val metrics were found.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    parsed = parse_log(args.log_path)
    summary = format_summary(parsed, label=args.label)

    if args.json_out is not None:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(parsed, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    if args.summary_out is not None:
        args.summary_out.parent.mkdir(parents=True, exist_ok=True)
        args.summary_out.write_text(summary + "\n", encoding="utf-8")

    print(summary)

    if args.require_final_metrics and parsed["final_val_bpb"] is None:
        print("error: final metrics were not found in the log", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
