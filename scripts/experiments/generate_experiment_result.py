#!/usr/bin/env python3
"""Generate a standardized experiment result markdown file and JSON sidecar."""

from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
from datetime import date
from pathlib import Path
from typing import Any


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


def git_output(root: Path, *args: str) -> str:
    try:
        proc = subprocess.run(
            ["git", *args],
            cwd=root,
            capture_output=True,
            text=True,
            check=True,
        )
    except Exception:
        return ""
    return proc.stdout.strip()


def load_metadata(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def choose(parsed: dict[str, Any], int8_key: str, raw_key: str) -> tuple[Any, str | None]:
    if parsed.get(int8_key) is not None:
        return parsed[int8_key], int8_key
    if parsed.get(raw_key) is not None:
        return parsed[raw_key], raw_key
    return None, None


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("log_path", type=Path, help="Path to the training log.")
    parser.add_argument("--metadata-json", type=Path, default=None, help="Optional metadata JSON to merge in first.")
    parser.add_argument("--run-id", default=None, help="Stable run identifier. Default: log filename stem.")
    parser.add_argument("--experiment-id", default=None)
    parser.add_argument("--idea-label", default=None)
    parser.add_argument("--standardized-name", default=None)
    parser.add_argument("--date", default=None, help="Run date. Default: today.")
    parser.add_argument("--branch", default=None, help="Git branch. Default: current branch if available.")
    parser.add_argument("--commit-sha", default=None, help="Git commit SHA. Default: HEAD if available.")
    parser.add_argument("--track-intent", default=None, choices=["non-record", "track-candidate"])
    parser.add_argument(
        "--scope",
        default=None,
        choices=[
            "smoke-path",
            "1xH100-surrogate",
            "8xH100-leaderboard",
            "non-record-unlimited",
            "records-preflight",
        ],
    )
    parser.add_argument("--lineage", default=None, choices=["baseline", "variant", "novel"])
    parser.add_argument("--state", default=None, choices=["frontier", "already-tried"])
    parser.add_argument("--result", default=None, choices=["positive", "negative", "inconclusive"])
    parser.add_argument("--status", default=None, help="Result packet status. Default: completed.")
    parser.add_argument("--code-path", default=None)
    parser.add_argument("--dataset-variant", default=None)
    parser.add_argument("--tokenizer-variant", default=None)
    parser.add_argument("--hardware", default=None)
    parser.add_argument("--wallclock-target", default=None)
    parser.add_argument("--core-hparams", default=None)
    parser.add_argument("--exact-command", default=None)
    parser.add_argument("--notes", default=None)
    parser.add_argument("--compare-json", type=Path, default=None, help="Optional parsed summary JSON to compare against.")
    parser.add_argument("--compare-label", default=None)
    parser.add_argument("--artifact-cap", type=int, default=None, help="Optional counted artifact cap check.")
    parser.add_argument("--confirmed-finding", action="append", default=[], help="Repeat to add confirmed findings.")
    parser.add_argument(
        "--inferred-conclusion",
        action="append",
        default=[],
        help="Repeat to add inferred conclusions.",
    )
    parser.add_argument("--json-out", type=Path, default=None, help="Output JSON path. Default: <log>.result.json")
    parser.add_argument("--md-out", type=Path, default=None, help="Output markdown path. Default: <log>.result.md")
    parser.add_argument(
        "--require-final-metrics",
        action="store_true",
        help="Exit non-zero if no final val metrics are present.",
    )
    return parser


def resolved_output(path: Path | None, default_path: Path) -> Path:
    return default_path if path is None else path


def metadata_value(metadata: dict[str, Any], key: str, fallback: Any = "") -> Any:
    value = metadata.get(key, fallback)
    return fallback if value is None else value


def build_result(
    args: argparse.Namespace,
    parsed: dict[str, Any],
    metadata: dict[str, Any],
    comparison: dict[str, Any] | None,
) -> dict[str, Any]:
    root = repo_root()
    run_id = args.run_id or metadata_value(metadata, "run_id", args.log_path.stem)
    model_counted, model_repr = choose(parsed, "model_int8_zlib_bytes", "model_bytes")
    total_counted, total_repr = choose(parsed, "total_submission_size_int8_zlib_bytes", "total_submission_size_bytes")

    result: dict[str, Any] = {
        "schema_version": 1,
        "run_id": run_id,
        "experiment_id": args.experiment_id or metadata_value(metadata, "experiment_id"),
        "idea_label": args.idea_label or metadata_value(metadata, "idea_label"),
        "standardized_name": args.standardized_name or metadata_value(metadata, "standardized_name"),
        "date": args.date or metadata_value(metadata, "date", date.today().isoformat()),
        "branch": args.branch or metadata_value(metadata, "branch", git_output(root, "branch", "--show-current")),
        "commit_sha": args.commit_sha or metadata_value(metadata, "commit_sha", git_output(root, "rev-parse", "HEAD")),
        "track_intent": args.track_intent or metadata_value(metadata, "track_intent"),
        "scope": args.scope or metadata_value(metadata, "scope"),
        "lineage": args.lineage or metadata_value(metadata, "lineage"),
        "state": args.state or metadata_value(metadata, "state"),
        "result": args.result or metadata_value(metadata, "result"),
        "status": args.status or metadata_value(metadata, "status", "completed"),
        "log_path": str(args.log_path.resolve()),
        "code_path": args.code_path or metadata_value(metadata, "code_path"),
        "dataset_variant": args.dataset_variant or metadata_value(metadata, "dataset_variant"),
        "tokenizer_variant": args.tokenizer_variant or metadata_value(metadata, "tokenizer_variant"),
        "hardware": args.hardware or metadata_value(metadata, "hardware"),
        "wallclock_target": args.wallclock_target or metadata_value(metadata, "wallclock_target"),
        "core_hparams": args.core_hparams or metadata_value(metadata, "core_hparams"),
        "exact_command": args.exact_command or metadata_value(metadata, "exact_command"),
        "notes": args.notes if args.notes is not None else metadata_value(metadata, "notes"),
        "final_val_loss": parsed.get("final_val_loss"),
        "final_val_bpb": parsed.get("final_val_bpb"),
        "final_metric_source": parsed.get("final_metric_source") or "",
        "final_eval_time_ms": parsed.get("final_eval_time_ms"),
        "stop_reason": parsed.get("stop_reason") or "",
        "stop_step": parsed.get("stop_step"),
        "stop_train_time_ms": parsed.get("stop_train_time_ms"),
        "last_step": parsed.get("last_step"),
        "iterations": parsed.get("iterations"),
        "last_logged_train_time_ms": parsed.get("last_logged_train_time_ms"),
        "last_logged_step_avg_ms": parsed.get("last_logged_step_avg_ms"),
        "peak_memory_allocated_mib": parsed.get("peak_memory_allocated_mib"),
        "peak_memory_reserved_mib": parsed.get("peak_memory_reserved_mib"),
        "model_bytes": parsed.get("model_bytes"),
        "model_int8_zlib_bytes": parsed.get("model_int8_zlib_bytes"),
        "code_bytes": parsed.get("code_bytes"),
        "total_submission_size_bytes": parsed.get("total_submission_size_bytes"),
        "total_submission_size_int8_zlib_bytes": parsed.get("total_submission_size_int8_zlib_bytes"),
        "counted_model_bytes": model_counted,
        "counted_model_bytes_source": model_repr or "",
        "counted_total_bytes": total_counted,
        "counted_total_bytes_source": total_repr or "",
        "comparison": comparison
        or metadata.get(
            "comparison",
            {
                "label": "",
                "delta_val_loss": None,
                "delta_val_bpb": None,
                "delta_bytes_total": None,
                "delta_stop_step": None,
                "delta_eval_time_ms": None,
            },
        ),
        "confirmed_findings": metadata.get("confirmed_findings", []) + list(args.confirmed_finding),
        "inferred_conclusions": metadata.get("inferred_conclusions", []) + list(args.inferred_conclusion),
    }
    if args.artifact_cap is not None:
        result["artifact_cap_bytes"] = args.artifact_cap
        result["artifact_cap_ok"] = total_counted is not None and int(total_counted) <= int(args.artifact_cap)
    return result


def format_number(value: Any) -> str:
    if value is None or value == "":
        return ""
    if isinstance(value, float):
        return f"{value:.8f}"
    return str(value)


def render_markdown(result: dict[str, Any]) -> str:
    comparison = result.get("comparison") or {}
    confirmed = result.get("confirmed_findings") or []
    inferred = result.get("inferred_conclusions") or []

    def bullet(label: str, key: str) -> str:
        return f"- `{label}`: {format_number(result.get(key))}"

    lines = [
        "# Experiment Result",
        "",
        "## Run Identity",
        "",
        bullet("run_id", "run_id"),
        bullet("experiment_id", "experiment_id"),
        bullet("date", "date"),
        bullet("branch", "branch"),
        bullet("commit_sha", "commit_sha"),
        bullet("log_path", "log_path"),
        bullet("code_path", "code_path"),
        "",
        "## Standardized Classification",
        "",
        bullet("idea_label", "idea_label"),
        bullet("standardized_name", "standardized_name"),
        bullet("lineage", "lineage"),
        bullet("state", "state"),
        bullet("result", "result"),
        bullet("track_intent", "track_intent"),
        bullet("scope", "scope"),
        "",
        "## Run Context",
        "",
        bullet("dataset_variant", "dataset_variant"),
        bullet("tokenizer_variant", "tokenizer_variant"),
        bullet("hardware", "hardware"),
        bullet("wallclock_target", "wallclock_target"),
        bullet("core_hparams", "core_hparams"),
        bullet("exact_command", "exact_command"),
        "",
        "## Confirmed Metrics",
        "",
        bullet("final_val_loss", "final_val_loss"),
        bullet("final_val_bpb", "final_val_bpb"),
        bullet("final_metric_source", "final_metric_source"),
        bullet("final_eval_time_ms", "final_eval_time_ms"),
        bullet("stop_reason", "stop_reason"),
        bullet("stop_step", "stop_step"),
        bullet("stop_train_time_ms", "stop_train_time_ms"),
        bullet("peak_memory_allocated_mib", "peak_memory_allocated_mib"),
        bullet("peak_memory_reserved_mib", "peak_memory_reserved_mib"),
        bullet("model_int8_zlib_bytes", "model_int8_zlib_bytes"),
        bullet("code_bytes", "code_bytes"),
        bullet("total_submission_size_int8_zlib_bytes", "total_submission_size_int8_zlib_bytes"),
        "",
        "## Comparison",
        "",
        f"- `comparison.label`: {format_number(comparison.get('label'))}",
        f"- `comparison.delta_val_loss`: {format_number(comparison.get('delta_val_loss'))}",
        f"- `comparison.delta_val_bpb`: {format_number(comparison.get('delta_val_bpb'))}",
        f"- `comparison.delta_bytes_total`: {format_number(comparison.get('delta_bytes_total'))}",
        f"- `comparison.delta_stop_step`: {format_number(comparison.get('delta_stop_step'))}",
        f"- `comparison.delta_eval_time_ms`: {format_number(comparison.get('delta_eval_time_ms'))}",
        "",
        "## Confirmed Findings",
        "",
    ]
    if confirmed:
        lines.extend(f"- {item}" for item in confirmed)
    else:
        lines.append("- none recorded")

    lines.extend(["", "## Inferred Conclusions", ""])
    if inferred:
        lines.extend(f"- {item}" for item in inferred)
    else:
        lines.append("- none recorded")

    lines.extend(["", "## Notes", "", f"- {result.get('notes') or 'none recorded'}"])

    if "artifact_cap_bytes" in result:
        lines.extend(
            [
                "",
                "## Artifact Cap Check",
                "",
                f"- `artifact_cap_bytes`: {format_number(result.get('artifact_cap_bytes'))}",
                f"- `artifact_cap_ok`: {format_number(result.get('artifact_cap_ok'))}",
                f"- `counted_total_bytes`: {format_number(result.get('counted_total_bytes'))}",
                f"- `counted_total_bytes_source`: {format_number(result.get('counted_total_bytes_source'))}",
            ]
        )

    return "\n".join(lines) + "\n"


def main() -> int:
    args = build_parser().parse_args()
    root = repo_root()
    parser_module = load_parse_module(root)
    metadata = load_metadata(args.metadata_json)
    parsed = parser_module.parse_log(args.log_path)

    comparison = None
    if args.compare_json is not None:
        other = parser_module.load_parsed_json(args.compare_json)
        compare_label = args.compare_label or args.compare_json.stem
        comparison = parser_module.build_comparison(parsed, other, compare_label)

    result = build_result(args, parsed, metadata, comparison)
    markdown = render_markdown(result)

    json_out = resolved_output(args.json_out, args.log_path.with_suffix(args.log_path.suffix + ".result.json"))
    md_out = resolved_output(args.md_out, args.log_path.with_suffix(args.log_path.suffix + ".result.md"))

    json_out.parent.mkdir(parents=True, exist_ok=True)
    md_out.parent.mkdir(parents=True, exist_ok=True)
    json_out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_out.write_text(markdown, encoding="utf-8")

    print(f"wrote {json_out}")
    print(f"wrote {md_out}")

    if args.require_final_metrics and result["final_val_bpb"] is None:
        print("error: final metrics were not found in the log", file=sys.stderr)
        return 1
    if args.artifact_cap is not None and not result.get("artifact_cap_ok", False):
        print("error: counted artifact size exceeds the supplied cap", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
