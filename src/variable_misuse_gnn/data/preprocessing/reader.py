"""Bộ đọc JSONL streaming cho GREAT dataset."""

from __future__ import annotations

import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any


def iter_jsonl_files(input_root: Path, split: str) -> list[Path]:
    """Liệt kê file JSONL của một split hoặc một file subset."""
    split_file = input_root / f"{split}_sample.jsonl"
    if split_file.exists():
        return [split_file]

    split_dir = input_root / split
    if split_dir.exists():
        return sorted(split_dir.glob(f"{split}__VARIABLE_MISUSE__SStuB.txt-*"))

    raise FileNotFoundError(f"Không tìm thấy dữ liệu split {split} trong {input_root}")


def iter_raw_examples(input_root: Path, split: str) -> Iterator[tuple[Path, int, dict[str, Any] | None, str]]:
    """Đọc từng dòng JSONL và trả về sample raw hoặc lỗi decode."""
    for file_path in iter_jsonl_files(input_root, split):
        with file_path.open("r", encoding="utf-8") as file:
            for line_number, line in enumerate(file, start=1):
                raw_line = line.rstrip("\n")
                try:
                    yield file_path, line_number, json.loads(raw_line), ""
                except json.JSONDecodeError as error:
                    yield file_path, line_number, None, str(error)

