"""Kiểm tra schema và tính hợp lệ của Program Graph."""

from __future__ import annotations

from typing import Any

from variable_misuse_gnn.graph.schema import ProgramGraph


REQUIRED_COMPACT_FIELDS = {
    "id",
    "split",
    "tokens",
    "has_bug",
    "loc",
    "candidates",
    "targets",
    "edges",
}


def validate_preprocessed_example(example: dict[str, Any]) -> tuple[bool, str]:
    """Kiểm tra sample compact trước khi xây dựng graph."""
    missing_fields = sorted(REQUIRED_COMPACT_FIELDS - set(example))
    if missing_fields:
        return False, f"missing_field:{','.join(missing_fields)}"

    tokens = example.get("tokens")
    if not isinstance(tokens, list) or not all(isinstance(token, str) for token in tokens):
        return False, "invalid_tokens"
    if not tokens:
        return False, "empty_tokens"

    num_nodes = len(tokens)
    has_bug = example.get("has_bug")
    if not isinstance(has_bug, bool):
        return False, "invalid_has_bug"

    loc = example.get("loc")
    if has_bug and (not isinstance(loc, int) or not 0 <= loc < num_nodes):
        return False, "invalid_localization_target"
    if not has_bug and loc is not None:
        return False, "unexpected_no_bug_location"

    for field_name in ("candidates", "targets"):
        values = example.get(field_name)
        if not isinstance(values, list):
            return False, f"invalid_{field_name}"
        for value in values:
            if not isinstance(value, int) or not 0 <= value < num_nodes:
                return False, f"invalid_{field_name}_index"

    if has_bug and not example.get("targets"):
        return False, "bug_sample_without_repair_target"
    if not has_bug and example.get("targets"):
        return False, "unexpected_no_bug_repair_target"
    if not set(example.get("targets", [])).issubset(set(example.get("candidates", []))):
        return False, "repair_target_not_in_candidates"

    edges = example.get("edges")
    if not isinstance(edges, list):
        return False, "invalid_edges"
    for edge in edges:
        if not isinstance(edge, list) or len(edge) != 4:
            return False, "invalid_edge_shape"
        source, target, edge_group_id, raw_type_id = edge
        if not all(isinstance(value, int) for value in (source, target, edge_group_id, raw_type_id)):
            return False, "invalid_edge_value_type"
        if not 0 <= source < num_nodes or not 0 <= target < num_nodes:
            return False, "invalid_edge_endpoint_index"
        if edge_group_id not in {0, 1, 2, 3, 4, 5}:
            return False, "invalid_edge_group_id"

    return True, "ok"


def validate_program_graph(graph: ProgramGraph) -> tuple[bool, str]:
    """Kiểm tra Program Graph sau khi build."""
    if graph.num_nodes <= 0:
        return False, "empty_graph"
    if len(graph.node_tokens) != graph.num_nodes:
        return False, "invalid_node_tokens_length"
    if len(graph.node_types) != graph.num_nodes:
        return False, "invalid_node_types_length"
    if len(graph.candidate_mask) != graph.num_nodes:
        return False, "invalid_candidate_mask_length"

    edge_count = len(graph.edge_index)
    if not (
        edge_count
        == len(graph.edge_types)
        == len(graph.edge_type_names)
        == len(graph.edge_group_ids)
        == len(graph.raw_edge_types)
    ):
        return False, "inconsistent_edge_lengths"

    for edge in graph.edge_index:
        if len(edge) != 2:
            return False, "invalid_edge_index_shape"
        source, target = edge
        if not 0 <= source < graph.num_nodes or not 0 <= target < graph.num_nodes:
            return False, "invalid_edge_endpoint_index"

    if graph.has_bug:
        if graph.localization_target is None:
            return False, "missing_localization_target"
        if not 0 <= graph.localization_target < graph.num_nodes:
            return False, "invalid_localization_target"
        if not graph.repair_targets:
            return False, "missing_repair_target"
    elif graph.localization_target is not None or graph.repair_targets:
        return False, "unexpected_no_bug_label"

    for index in graph.repair_candidates:
        if not 0 <= index < graph.num_nodes:
            return False, "invalid_repair_candidate"
        if not graph.candidate_mask[index]:
            return False, "candidate_mask_mismatch"

    candidate_set = set(graph.repair_candidates)
    for index in graph.repair_targets:
        if not 0 <= index < graph.num_nodes:
            return False, "invalid_repair_target"
        if index not in candidate_set:
            return False, "repair_target_not_in_candidates"

    return True, "ok"
