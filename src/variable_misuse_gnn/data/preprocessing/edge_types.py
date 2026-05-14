"""Định nghĩa và chuẩn hóa edge type của GREAT dataset."""

from __future__ import annotations


RAW_EDGE_TYPE_TO_GROUP = {
    "enum_CFG_NEXT": "control_flow",
    "enum_LAST_READ": "data_flow",
    "enum_LAST_WRITE": "data_flow",
    "enum_COMPUTED_FROM": "data_flow",
    "enum_RETURNS_TO": "control_flow",
    "enum_FORMAL_ARG_NAME": "semantic",
    "enum_FIELD": "syntax",
    "enum_SYNTAX": "syntax",
    "enum_NEXT_SYNTAX": "next_token",
    "enum_LAST_LEXICAL_USE": "lexical",
    "enum_CALLS": "control_flow",
}

GRAPH_VARIANT_EDGE_GROUPS = {
    "syntactic_only": {"syntax"},
    "syntactic_next_token": {"syntax", "next_token"},
    "syntactic_next_token_data_flow": {"syntax", "next_token", "data_flow", "lexical"},
    "full_available": {"syntax", "next_token", "data_flow", "lexical", "semantic", "control_flow"},
}

EDGE_GROUP_TO_ID = {
    "syntax": 0,
    "next_token": 1,
    "data_flow": 2,
    "lexical": 3,
    "semantic": 4,
    "control_flow": 5,
}


def edge_group_for(edge_name: str) -> str:
    """Trả về nhóm edge chuẩn hóa từ tên edge trong GREAT."""
    return RAW_EDGE_TYPE_TO_GROUP.get(edge_name, "unknown")

