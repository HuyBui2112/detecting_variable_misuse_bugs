"""Ghi và đọc Program Graph ở định dạng JSONL shard."""

from __future__ import annotations

import json
from collections.abc import Iterator
from pathlib import Path

from variable_misuse_gnn.graph.schema import ProgramGraph, program_graph_from_json


class GraphShardWriter:
    """Ghi Program Graph thành nhiều shard JSONL để tránh file quá lớn."""

    def __init__(self, output_root: Path, graph_variant: str, split: str, shard_size: int) -> None:
        self.output_dir = output_root / graph_variant / split
        self.shard_size = shard_size
        self.current_shard_index = 0
        self.current_count = 0
        self.file = None
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def __enter__(self) -> "GraphShardWriter":
        """Trả về writer và chỉ mở file khi có graph đầu tiên."""
        return self

    def __exit__(self, exc_type: object, exc_value: object, traceback: object) -> None:
        """Đóng file shard đang mở."""
        self.close()

    def write(self, graph: ProgramGraph) -> None:
        """Ghi một graph và tự chuyển shard khi đạt giới hạn."""
        if self.file is None:
            self.open_next_shard()
        if self.current_count >= self.shard_size:
            self.open_next_shard()
        assert self.file is not None
        self.file.write(json.dumps(graph.to_json_dict(), ensure_ascii=False) + "\n")
        self.current_count += 1

    def open_next_shard(self) -> None:
        """Mở shard kế tiếp."""
        self.close()
        shard_path = self.output_dir / f"shard_{self.current_shard_index:05d}.jsonl"
        self.file = shard_path.open("w", encoding="utf-8")
        self.current_shard_index += 1
        self.current_count = 0

    def close(self) -> None:
        """Đóng shard hiện tại nếu đang mở."""
        if self.file is not None:
            self.file.close()
            self.file = None


def iter_serialized_graphs(graph_dir: Path) -> Iterator[ProgramGraph]:
    """Đọc lại toàn bộ graph JSONL trong một thư mục shard."""
    for shard_path in sorted(graph_dir.glob("shard_*.jsonl")):
        with shard_path.open("r", encoding="utf-8") as file:
            for line in file:
                yield program_graph_from_json(json.loads(line))
