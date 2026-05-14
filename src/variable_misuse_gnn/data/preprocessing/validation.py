"""Kiểm tra chất lượng dữ liệu raw trước khi chuẩn hóa."""

from __future__ import annotations

from typing import Any


REQUIRED_FIELDS = {
    "source_tokens",
    "has_bug",
    "error_location",
    "repair_candidates",
    "repair_targets",
    "bug_kind",
    "bug_kind_name",
    "edges",
    "provenances",
}


def validate_raw_example(example: dict[str, Any]) -> tuple[bool, str]:
    """Kiểm tra schema và index cơ bản của sample GREAT."""
    missing_fields = sorted(REQUIRED_FIELDS - set(example))
    if missing_fields:
        return False, f"missing_field:{','.join(missing_fields)}"

    tokens = example.get("source_tokens")
    if not isinstance(tokens, list) or not all(isinstance(token, str) for token in tokens):
        return False, "invalid_source_tokens"
    if not tokens:
        return False, "empty_source_tokens"

    token_count = len(tokens)
    has_bug = example.get("has_bug")
    if not isinstance(has_bug, bool):
        return False, "invalid_has_bug"

    error_location = example.get("error_location")
    if has_bug and (not isinstance(error_location, int) or not 0 <= error_location < token_count):
        return False, "invalid_error_location"

    repair_targets = example.get("repair_targets")
    if not isinstance(repair_targets, list):
        return False, "invalid_repair_targets"
    for target in repair_targets:
        if not isinstance(target, int) or not 0 <= target < token_count:
            return False, "invalid_repair_target_index"

    repair_candidates = example.get("repair_candidates")
    if not isinstance(repair_candidates, list):
        return False, "invalid_repair_candidates"
    for candidate in repair_candidates:
        if isinstance(candidate, int) and not 0 <= candidate < token_count:
            return False, "invalid_repair_candidate_index"

    edges = example.get("edges")
    if not isinstance(edges, list):
        return False, "invalid_edges"
    for edge in edges:
        if not isinstance(edge, list) or len(edge) < 4:
            return False, "invalid_edge_shape"
        source, target = edge[0], edge[1]
        if not isinstance(source, int) or not isinstance(target, int):
            return False, "invalid_edge_endpoint_type"
        if not 0 <= source < token_count or not 0 <= target < token_count:
            return False, "invalid_edge_endpoint_index"

    if has_bug and not repair_targets:
        return False, "bug_sample_without_repair_target"

    return True, "ok"

