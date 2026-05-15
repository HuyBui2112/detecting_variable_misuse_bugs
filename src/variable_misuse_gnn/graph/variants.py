"""Định nghĩa graph variant và relation type cho GGNN."""

from __future__ import annotations

from dataclasses import dataclass

from variable_misuse_gnn.data.preprocessing.edge_types import EDGE_GROUP_TO_ID


@dataclass(frozen=True)
class GraphVariant:
    """Một biến thể Program Graph dùng cho so sánh thí nghiệm."""

    name: str
    edge_groups: frozenset[str]
    description: str


EDGE_ID_TO_GROUP = {edge_id: group for group, edge_id in EDGE_GROUP_TO_ID.items()}

GRAPH_VARIANTS: dict[str, GraphVariant] = {
    "ast_only": GraphVariant(
        name="ast_only",
        edge_groups=frozenset({"syntax"}),
        description="Baseline chỉ dùng AST/syntax edge.",
    ),
    "ast_next_token": GraphVariant(
        name="ast_next_token",
        edge_groups=frozenset({"syntax", "next_token"}),
        description="Baseline dùng AST/syntax và NextToken.",
    ),
    "ast_next_token_data_flow": GraphVariant(
        name="ast_next_token_data_flow",
        edge_groups=frozenset({"syntax", "next_token", "data_flow", "lexical"}),
        description="Graph chính dùng AST, NextToken, Data Flow và LastUse-like lexical edge.",
    ),
    "full_available": GraphVariant(
        name="full_available",
        edge_groups=frozenset(
            {"syntax", "next_token", "data_flow", "lexical", "semantic", "control_flow"}
        ),
        description="Graph mở rộng dùng toàn bộ edge group đã tiền xử lý.",
    ),
}

BASE_EDGE_TYPE_ORDER = (
    "syntax",
    "next_token",
    "data_flow",
    "lexical",
    "semantic",
    "control_flow",
)

FORWARD_EDGE_TYPE_TO_ID = {
    edge_group: index * 2 for index, edge_group in enumerate(BASE_EDGE_TYPE_ORDER)
}
REVERSE_EDGE_TYPE_TO_ID = {
    edge_group: index * 2 + 1 for index, edge_group in enumerate(BASE_EDGE_TYPE_ORDER)
}

EDGE_TYPE_ID_TO_NAME = {
    edge_type_id: edge_group
    for edge_group, edge_type_id in FORWARD_EDGE_TYPE_TO_ID.items()
} | {
    edge_type_id: f"{edge_group}_reverse"
    for edge_group, edge_type_id in REVERSE_EDGE_TYPE_TO_ID.items()
}

SELF_LOOP_EDGE_TYPE = len(BASE_EDGE_TYPE_ORDER) * 2
EDGE_TYPE_ID_TO_NAME[SELF_LOOP_EDGE_TYPE] = "self_loop"


def get_graph_variant(name: str) -> GraphVariant:
    """Trả về graph variant theo tên public của bước graph construction."""
    try:
        return GRAPH_VARIANTS[name]
    except KeyError as error:
        supported = ", ".join(sorted(GRAPH_VARIANTS))
        raise ValueError(f"Graph variant không hỗ trợ: {name}. Hỗ trợ: {supported}") from error


def edge_group_name(edge_group_id: int) -> str:
    """Chuyển edge group id compact về tên nhóm edge."""
    try:
        return EDGE_ID_TO_GROUP[edge_group_id]
    except KeyError as error:
        raise ValueError(f"Edge group id không hỗ trợ: {edge_group_id}") from error


def relation_type_id(edge_group: str, is_reverse: bool = False) -> int:
    """Ánh xạ edge group sang relation type id dùng cho GGNN."""
    mapping = REVERSE_EDGE_TYPE_TO_ID if is_reverse else FORWARD_EDGE_TYPE_TO_ID
    try:
        return mapping[edge_group]
    except KeyError as error:
        raise ValueError(f"Edge group không hỗ trợ: {edge_group}") from error

