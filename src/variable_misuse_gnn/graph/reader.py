"""Bộ đọc streaming cho dữ liệu GREAT compact sau tiền xử lý."""

from __future__ import annotations

import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any


def split_file_path(input_root: Path, split: str) -> Path:
    """Trả về file JSONL compact của một split."""
    path = input_root / f"{split}.jsonl"
    if not path.exists():
        raise FileNotFoundError(f"Không tìm thấy split {split}: {path}")
    return path


def iter_preprocessed_examples(
    input_root: Path,
    split: str,
    max_samples: int | None = None,
) -> Iterator[tuple[int, dict[str, Any] | None, str]]:
    """Đọc từng sample compact, trả về lỗi decode nếu có."""
    path = split_file_path(input_root, split)
    with path.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            if max_samples is not None and line_number > max_samples:
                break
            raw_line = line.rstrip("\n")
            try:
                yield line_number, json.loads(raw_line), ""
            except json.JSONDecodeError as error:
                yield line_number, None, str(error)

