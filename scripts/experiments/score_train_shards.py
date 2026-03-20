#!/usr/bin/env python3
"""Deterministically score FineWeb training shards for ordering and filtering ablations."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
import sentencepiece as spm


SHARD_MAGIC = 20240520
SHARD_VERSION = 1


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data-path",
        type=Path,
        required=True,
        help="Directory containing fineweb_train_*.bin shards.",
    )
    parser.add_argument(
        "--tokenizer-path",
        type=Path,
        required=True,
        help="SentencePiece tokenizer model path used for the shard export.",
    )
    parser.add_argument(
        "--vocab-size",
        type=int,
        required=True,
        help="Expected tokenizer vocabulary size.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="JSON output path.",
    )
    return parser.parse_args()


def build_sentencepiece_luts(
    sp: spm.SentencePieceProcessor,
    vocab_size: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    sp_vocab_size = int(sp.vocab_size())
    table_size = max(sp_vocab_size, vocab_size)
    base_bytes = np.zeros((table_size,), dtype=np.int16)
    has_leading_space = np.zeros((table_size,), dtype=np.bool_)
    is_boundary_token = np.ones((table_size,), dtype=np.bool_)
    is_byte_token = np.zeros((table_size,), dtype=np.bool_)
    for token_id in range(sp_vocab_size):
        if sp.is_control(token_id) or sp.is_unknown(token_id) or sp.is_unused(token_id):
            continue
        is_boundary_token[token_id] = False
        if sp.is_byte(token_id):
            base_bytes[token_id] = 1
            is_byte_token[token_id] = True
            continue
        piece = sp.id_to_piece(token_id)
        if piece.startswith("▁"):
            has_leading_space[token_id] = True
            piece = piece[1:]
        base_bytes[token_id] = len(piece.encode("utf-8"))
    return base_bytes, has_leading_space, is_boundary_token, is_byte_token


def load_data_shard(file: Path) -> np.ndarray:
    header_bytes = 256 * np.dtype("<i4").itemsize
    token_bytes = np.dtype("<u2").itemsize
    header = np.fromfile(file, dtype="<i4", count=256)
    if header.size != 256 or int(header[0]) != SHARD_MAGIC or int(header[1]) != SHARD_VERSION:
        raise ValueError(f"Unexpected shard header for {file}")
    num_tokens = int(header[2])
    expected_size = header_bytes + num_tokens * token_bytes
    if file.stat().st_size != expected_size:
        raise ValueError(f"Shard size mismatch for {file}: expected {expected_size} bytes")
    tokens = np.fromfile(file, dtype="<u2", count=num_tokens, offset=header_bytes)
    if tokens.size != num_tokens:
        raise ValueError(f"Short read for {file}")
    return tokens.astype(np.int32, copy=False)


def compute_token_bytes(
    tokens: np.ndarray,
    base_bytes: np.ndarray,
    has_leading_space: np.ndarray,
    is_boundary_token: np.ndarray,
) -> np.ndarray:
    token_bytes = base_bytes[tokens].astype(np.float64, copy=True)
    if tokens.size > 1:
        token_bytes[1:] += (
            has_leading_space[tokens[1:]] & ~is_boundary_token[tokens[:-1]]
        ).astype(np.float64)
    return token_bytes


def main() -> None:
    args = parse_args()
    if not args.data_path.is_dir():
        raise FileNotFoundError(f"Data directory not found: {args.data_path}")
    if not args.tokenizer_path.is_file():
        raise FileNotFoundError(f"Tokenizer not found: {args.tokenizer_path}")

    shard_files = sorted(args.data_path.glob("fineweb_train_*.bin"))
    if not shard_files:
        raise FileNotFoundError(f"No fineweb_train_*.bin shards found under {args.data_path}")

    sp = spm.SentencePieceProcessor(model_file=str(args.tokenizer_path))
    actual_vocab_size = int(sp.vocab_size())
    if actual_vocab_size != args.vocab_size:
        raise ValueError(
            f"VOCAB_SIZE mismatch: expected {args.vocab_size}, tokenizer has {actual_vocab_size}"
        )

    base_bytes, has_leading_space, is_boundary_token, is_byte_token = build_sentencepiece_luts(
        sp,
        args.vocab_size,
    )

    total_counts = np.zeros((args.vocab_size,), dtype=np.int64)
    shard_tokens: list[tuple[Path, np.ndarray]] = []
    for shard_file in shard_files:
        tokens = load_data_shard(shard_file)
        if tokens.size == 0:
            raise ValueError(f"Empty shard: {shard_file}")
        if int(tokens.max()) >= args.vocab_size:
            raise ValueError(
                f"Token id {int(tokens.max())} in {shard_file} exceeds VOCAB_SIZE={args.vocab_size}"
            )
        total_counts += np.bincount(tokens, minlength=args.vocab_size)
        shard_tokens.append((shard_file, tokens))

    total_token_count = int(total_counts.sum())
    if total_token_count <= 0:
        raise ValueError("No tokens were counted across training shards")
    token_probs = total_counts.astype(np.float64) / float(total_token_count)
    token_surprisal = np.zeros_like(token_probs, dtype=np.float64)
    nonzero = token_probs > 0
    token_surprisal[nonzero] = -np.log(token_probs[nonzero])

    shard_records: list[dict[str, object]] = []
    for shard_file, tokens in shard_tokens:
        token_count = int(tokens.size)
        repeat_rate = (
            float(np.mean(tokens[1:] == tokens[:-1], dtype=np.float64))
            if token_count > 1
            else 0.0
        )
        byte_token_rate = float(np.mean(is_byte_token[tokens], dtype=np.float64))
        avg_token_bytes = float(np.mean(compute_token_bytes(tokens, base_bytes, has_leading_space, is_boundary_token)))
        mean_unigram_surprisal_nats = float(np.mean(token_surprisal[tokens], dtype=np.float64))
        shard_records.append(
            {
                "filename": shard_file.name,
                "token_count": token_count,
                "mean_unigram_surprisal_nats": mean_unigram_surprisal_nats,
                "repeat_rate": repeat_rate,
                "byte_token_rate": byte_token_rate,
                "avg_token_bytes": avg_token_bytes,
            }
        )

    easy_to_hard = sorted(
        shard_records,
        key=lambda record: (
            float(record["mean_unigram_surprisal_nats"]),
            str(record["filename"]),
        ),
    )
    quality = sorted(
        shard_records,
        key=lambda record: (
            float(record["byte_token_rate"]),
            float(record["repeat_rate"]),
            -float(record["avg_token_bytes"]),
            str(record["filename"]),
        ),
    )
    difficulty_rank = {str(record["filename"]): idx for idx, record in enumerate(easy_to_hard)}
    quality_rank = {str(record["filename"]): idx for idx, record in enumerate(quality)}
    for record in shard_records:
        record["difficulty_rank"] = difficulty_rank[str(record["filename"])]
        record["quality_rank"] = quality_rank[str(record["filename"])]

    output = {
        "format_version": 1,
        "data_path": str(args.data_path.resolve()),
        "tokenizer_path": str(args.tokenizer_path.resolve()),
        "vocab_size": args.vocab_size,
        "train_shards": len(shard_records),
        "total_tokens": total_token_count,
        "heuristics": {
            "difficulty": "ascending mean_unigram_surprisal_nats",
            "quality": "ascending byte_token_rate, ascending repeat_rate, descending avg_token_bytes, ascending filename",
        },
        "orderings": {
            "easy_to_hard": [str(record["filename"]) for record in easy_to_hard],
            "hard_to_easy": [str(record["filename"]) for record in reversed(easy_to_hard)],
            "quality": [str(record["filename"]) for record in quality],
        },
        "shards": sorted(shard_records, key=lambda record: str(record["filename"])),
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(f"wrote shard scores: {args.output}")
    print(f"train_shards={len(shard_records)} total_tokens={total_token_count}")


if __name__ == "__main__":
    main()
