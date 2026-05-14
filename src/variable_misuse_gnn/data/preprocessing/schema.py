"""Schema nội bộ cho dữ liệu Variable Misuse sau tiền xử lý."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class Provenance:
    """Thông tin nguồn gốc và license của một sample."""

    dataset_name: str
    filepath: str
    license: str
    note: str


@dataclass(frozen=True)
class NormalizedEdge:
    """Edge đã chuẩn hóa để bước graph construction sử dụng trực tiếp."""

    source: int
    target: int
    raw_type_id: int
    raw_type_name: str
    edge_group: str
    edge_group_id: int


@dataclass(frozen=True)
class VariableMisuseExample:
    """Sample chuẩn hóa cho localization và repair."""

    sample_id: str
    split: str
    source_path: str
    line_number: int
    source_tokens: list[str]
    token_count: int
    has_bug: bool
    bug_kind_name: str
    error_location: int | None
    localization_target: int | None
    repair_candidates: list[int]
    repair_targets: list[int]
    candidate_token_texts: list[str]
    normalized_edges: list[NormalizedEdge]
    graph_variant_edges: dict[str, list[int]]
    provenance: Provenance
    token_hash: str

    def to_json_dict(self) -> dict[str, Any]:
        """Chuyển sample sang dict JSON-friendly."""
        data = asdict(self)
        data["normalized_edges"] = [asdict(edge) for edge in self.normalized_edges]
        data["provenance"] = asdict(self.provenance)
        return data

