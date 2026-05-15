"""Schema nội bộ cho Program Graph sau graph construction."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class PreprocessedExample:
    """Sample compact đã tiền xử lý và sẵn sàng chuyển thành graph."""

    sample_id: str
    split: str
    tokens: list[str]
    has_bug: bool
    localization_target: int | None
    repair_candidates: list[int]
    repair_targets: list[int]
    edges: list[list[int]]
    provenance: dict[str, Any]


@dataclass(frozen=True)
class NodeMetadata:
    """Metadata của token node dùng cho debug và visualization."""

    node_id: int
    node_type: str
    token_text: str
    syntax_type: str | None
    symbol_name: str | None
    source_line: int | None
    source_column: int | None
    scope_id: str | None


@dataclass(frozen=True)
class GraphEdge:
    """Edge đã chuẩn hóa cho Program Graph."""

    source: int
    target: int
    edge_type: int
    edge_type_name: str
    edge_group_id: int
    edge_group_name: str
    raw_type_id: int
    is_reverse: bool = False


@dataclass(frozen=True)
class ProgramGraph:
    """Program Graph token-level cho localization và repair."""

    graph_id: str
    split: str
    graph_variant: str
    num_nodes: int
    node_tokens: list[str]
    node_types: list[str]
    candidate_mask: list[bool]
    edge_index: list[list[int]]
    edge_types: list[int]
    edge_type_names: list[str]
    edge_group_ids: list[int]
    raw_edge_types: list[int]
    has_bug: bool
    localization_target: int | None
    repair_candidates: list[int]
    repair_targets: list[int]
    provenance: dict[str, Any]

    def to_json_dict(self) -> dict[str, Any]:
        """Chuyển graph sang dict có thể ghi JSONL."""
        return asdict(self)


def program_graph_from_json(data: dict[str, Any]) -> ProgramGraph:
    """Khôi phục `ProgramGraph` từ dict đọc trong JSONL."""
    return ProgramGraph(
        graph_id=str(data["graph_id"]),
        split=str(data["split"]),
        graph_variant=str(data["graph_variant"]),
        num_nodes=int(data["num_nodes"]),
        node_tokens=list(data["node_tokens"]),
        node_types=list(data["node_types"]),
        candidate_mask=[bool(value) for value in data["candidate_mask"]],
        edge_index=[list(edge) for edge in data["edge_index"]],
        edge_types=[int(value) for value in data["edge_types"]],
        edge_type_names=[str(value) for value in data["edge_type_names"]],
        edge_group_ids=[int(value) for value in data["edge_group_ids"]],
        raw_edge_types=[int(value) for value in data["raw_edge_types"]],
        has_bug=bool(data["has_bug"]),
        localization_target=(
            None if data.get("localization_target") is None else int(data["localization_target"])
        ),
        repair_candidates=[int(value) for value in data["repair_candidates"]],
        repair_targets=[int(value) for value in data["repair_targets"]],
        provenance=dict(data.get("provenance", {})),
    )

