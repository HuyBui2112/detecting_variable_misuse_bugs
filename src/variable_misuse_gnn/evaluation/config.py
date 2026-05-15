"""Cấu hình evaluation GGNN cho Variable Misuse."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class EvaluationConfig:
    """Cấu hình một lần đánh giá checkpoint trên một graph split."""

    graph_root: Path
    embedding_root: Path
    checkpoint_path: Path
    output_root: Path
    graph_variant: str
    split: str = "eval"
    batch_size: int = 8
    max_graphs: int | None = None
    log_every: int = 100
    seed: int = 42
