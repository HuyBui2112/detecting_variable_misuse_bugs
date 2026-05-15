"""Cấu hình xây dựng Program Graph từ dữ liệu GREAT compact."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class GraphConstructionConfig:
    """Cấu hình điều khiển bước xây dựng Program Graph."""

    input_root: Path = Path("dataset/processed/great_colab")
    output_root: Path = Path("dataset/graphs/great_colab")
    graph_variant: str = "ast_next_token_data_flow"
    splits: tuple[str, ...] = ("train", "dev", "eval")
    add_inverse_edges: bool = True
    add_self_loops: bool = False
    max_samples_per_split: int | None = None
    shard_size: int = 50000
    output_format: str = "jsonl"
    dry_run: bool = False

