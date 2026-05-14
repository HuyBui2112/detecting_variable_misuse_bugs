"""Cấu hình cho pipeline tiền xử lý GREAT."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PreprocessingConfig:
    """Cấu hình điều khiển việc lọc, cân bằng và ghi dữ liệu đã xử lý."""

    input_root: Path
    output_root: Path
    report_path: Path
    max_tokens: int = 512
    max_edges: int = 4096
    min_repair_candidates: int = 2
    balance_classes: bool = True
    max_samples_per_class: int | None = None
    drop_duplicate_tokens_within_split: bool = False
    keep_control_flow_edges: bool = True
    include_linear_next_token_edges: bool = True
    output_format: str = "compact"
    include_provenance: bool = True
