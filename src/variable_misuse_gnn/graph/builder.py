"""Xây dựng Program Graph từ sample compact đã tiền xử lý."""

from __future__ import annotations

from typing import Any

from variable_misuse_gnn.graph.config import GraphConstructionConfig
from variable_misuse_gnn.graph.schema import GraphEdge, ProgramGraph
from variable_misuse_gnn.graph.variants import (
    EDGE_TYPE_ID_TO_NAME,
    SELF_LOOP_EDGE_TYPE,
    edge_group_name,
    get_graph_variant,
    relation_type_id,
)


def build_program_graph(
    raw_example: dict[str, Any],
    config: GraphConstructionConfig,
) -> ProgramGraph:
    """Chuyển một sample GREAT compact thành Program Graph theo variant được chọn."""
    tokens = [str(token) for token in raw_example["tokens"]]
    num_nodes = len(tokens)
    variant = get_graph_variant(config.graph_variant)
    candidate_indices = sorted({int(index) for index in raw_example.get("candidates", [])})
    graph_edges: list[GraphEdge] = []

    for compact_edge in raw_example.get("edges", []):
        source, target, edge_group_id, raw_type_id = parse_compact_edge(compact_edge)
        group_name = edge_group_name(edge_group_id)
        if group_name not in variant.edge_groups:
            continue
        graph_edges.append(
            make_graph_edge(
                source=source,
                target=target,
                edge_group_id=edge_group_id,
                edge_group=group_name,
                raw_type_id=raw_type_id,
                is_reverse=False,
            )
        )
        if config.add_inverse_edges:
            graph_edges.append(
                make_graph_edge(
                    source=target,
                    target=source,
                    edge_group_id=edge_group_id,
                    edge_group=group_name,
                    raw_type_id=raw_type_id,
                    is_reverse=True,
                )
            )

    if config.add_self_loops:
        graph_edges.extend(build_self_loop_edges(num_nodes))

    return ProgramGraph(
        graph_id=str(raw_example["id"]),
        split=str(raw_example["split"]),
        graph_variant=variant.name,
        num_nodes=num_nodes,
        node_tokens=tokens,
        node_types=["token"] * num_nodes,
        candidate_mask=build_candidate_mask(num_nodes, candidate_indices),
        edge_index=[[edge.source, edge.target] for edge in graph_edges],
        edge_types=[edge.edge_type for edge in graph_edges],
        edge_type_names=[edge.edge_type_name for edge in graph_edges],
        edge_group_ids=[edge.edge_group_id for edge in graph_edges],
        raw_edge_types=[edge.raw_type_id for edge in graph_edges],
        has_bug=bool(raw_example["has_bug"]),
        localization_target=normalize_optional_index(raw_example.get("loc")),
        repair_candidates=candidate_indices,
        repair_targets=sorted({int(index) for index in raw_example.get("targets", [])}),
        provenance=dict(raw_example.get("provenance", {})),
    )


def parse_compact_edge(edge: list[Any]) -> tuple[int, int, int, int]:
    """Đọc compact edge `[source, target, edge_group_id, raw_type_id]`."""
    if not isinstance(edge, list) or len(edge) != 4:
        raise ValueError(f"Compact edge không hợp lệ: {edge}")
    return int(edge[0]), int(edge[1]), int(edge[2]), int(edge[3])


def make_graph_edge(
    source: int,
    target: int,
    edge_group_id: int,
    edge_group: str,
    raw_type_id: int,
    is_reverse: bool,
) -> GraphEdge:
    """Tạo edge forward hoặc reverse với relation type ổn định."""
    edge_type = relation_type_id(edge_group, is_reverse=is_reverse)
    return GraphEdge(
        source=source,
        target=target,
        edge_type=edge_type,
        edge_type_name=EDGE_TYPE_ID_TO_NAME[edge_type],
        edge_group_id=edge_group_id,
        edge_group_name=edge_group,
        raw_type_id=raw_type_id,
        is_reverse=is_reverse,
    )


def build_self_loop_edges(num_nodes: int) -> list[GraphEdge]:
    """Tạo self-loop tùy chọn cho mỗi node."""
    return [
        GraphEdge(
            source=node_id,
            target=node_id,
            edge_type=SELF_LOOP_EDGE_TYPE,
            edge_type_name=EDGE_TYPE_ID_TO_NAME[SELF_LOOP_EDGE_TYPE],
            edge_group_id=-1,
            edge_group_name="self_loop",
            raw_type_id=-1,
            is_reverse=False,
        )
        for node_id in range(num_nodes)
    ]


def build_candidate_mask(num_nodes: int, candidate_indices: list[int]) -> list[bool]:
    """Tạo mask node ứng viên repair từ candidate index đã tiền xử lý."""
    candidate_set = set(candidate_indices)
    return [node_id in candidate_set for node_id in range(num_nodes)]


def normalize_optional_index(value: Any) -> int | None:
    """Chuẩn hóa index có thể rỗng trong compact JSONL."""
    if value is None:
        return None
    return int(value)

