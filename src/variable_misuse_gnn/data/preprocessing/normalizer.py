"""Chuẩn hóa raw GREAT example thành schema nội bộ."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from variable_misuse_gnn.data.preprocessing.config import PreprocessingConfig
from variable_misuse_gnn.data.preprocessing.edge_types import (
    EDGE_GROUP_TO_ID,
    GRAPH_VARIANT_EDGE_GROUPS,
    edge_group_for,
)
from variable_misuse_gnn.data.preprocessing.schema import (
    NormalizedEdge,
    Provenance,
    VariableMisuseExample,
)


def normalize_example(
    example: dict[str, Any],
    split: str,
    source_path: Path,
    line_number: int,
    config: PreprocessingConfig,
) -> VariableMisuseExample:
    """Chuẩn hóa một sample GREAT sau khi đã validate."""
    tokens = list(example["source_tokens"])
    token_hash = hash_tokens(tokens)
    sample_id = build_sample_id(split, source_path, line_number)
    repair_targets = sorted(set(int(index) for index in example["repair_targets"]))
    repair_candidates = normalize_candidate_indices(example["repair_candidates"], repair_targets)
    has_bug = bool(example["has_bug"])
    localization_target = int(example["error_location"]) if has_bug else None
    error_location = int(example["error_location"]) if has_bug else None
    provenance = extract_provenance(example)
    normalized_edges = normalize_edges(example["edges"], token_count=len(tokens), config=config)
    graph_variant_edges = build_graph_variant_edges(normalized_edges)

    return VariableMisuseExample(
        sample_id=sample_id,
        split=split,
        source_path=source_path.as_posix(),
        line_number=line_number,
        source_tokens=tokens,
        token_count=len(tokens),
        has_bug=has_bug,
        bug_kind_name=str(example["bug_kind_name"]),
        error_location=error_location,
        localization_target=localization_target,
        repair_candidates=repair_candidates,
        repair_targets=repair_targets,
        candidate_token_texts=[tokens[index] for index in repair_candidates],
        normalized_edges=normalized_edges,
        graph_variant_edges=graph_variant_edges,
        provenance=provenance,
        token_hash=token_hash,
    )


def normalize_candidate_indices(candidates: list[Any], repair_targets: list[int]) -> list[int]:
    """Giữ candidate dạng index và bổ sung repair target nếu raw candidate bị thiếu."""
    candidate_indices = {int(candidate) for candidate in candidates if isinstance(candidate, int)}
    candidate_indices.update(repair_targets)
    return sorted(candidate_indices)


def normalize_edges(
    raw_edges: list[list[Any]],
    token_count: int,
    config: PreprocessingConfig,
) -> list[NormalizedEdge]:
    """Chuẩn hóa edge và thêm linear NextToken nếu cần."""
    normalized_edges: list[NormalizedEdge] = []
    for edge in raw_edges:
        source = int(edge[0])
        target = int(edge[1])
        raw_type_id = int(edge[2])
        raw_type_name = str(edge[3])
        edge_group = edge_group_for(raw_type_name)
        if edge_group == "unknown":
            continue
        if edge_group == "control_flow" and not config.keep_control_flow_edges:
            continue
        normalized_edges.append(
            NormalizedEdge(
                source=source,
                target=target,
                raw_type_id=raw_type_id,
                raw_type_name=raw_type_name,
                edge_group=edge_group,
                edge_group_id=EDGE_GROUP_TO_ID[edge_group],
            )
        )

    if config.include_linear_next_token_edges:
        normalized_edges.extend(build_linear_next_token_edges(token_count))

    return normalized_edges


def build_linear_next_token_edges(token_count: int) -> list[NormalizedEdge]:
    """Tạo edge tuần tự giữa các token liền kề để đúng yêu cầu NextToken."""
    edges: list[NormalizedEdge] = []
    for source in range(max(0, token_count - 1)):
        edges.append(
            NormalizedEdge(
                source=source,
                target=source + 1,
                raw_type_id=-1,
                raw_type_name="LOCAL_NEXT_TOKEN",
                edge_group="next_token",
                edge_group_id=EDGE_GROUP_TO_ID["next_token"],
            )
        )
    return edges


def build_graph_variant_edges(edges: list[NormalizedEdge]) -> dict[str, list[int]]:
    """Lưu index edge theo từng graph variant để bước graph construction dùng lại."""
    variant_edges: dict[str, list[int]] = {}
    for variant_name, allowed_groups in GRAPH_VARIANT_EDGE_GROUPS.items():
        variant_edges[variant_name] = [
            index for index, edge in enumerate(edges) if edge.edge_group in allowed_groups
        ]
    return variant_edges


def extract_provenance(example: dict[str, Any]) -> Provenance:
    """Trích xuất provenance đầu tiên của GREAT sample."""
    provenances = example.get("provenances") or []
    dataset_provenance = {}
    if provenances and isinstance(provenances[0], dict):
        dataset_provenance = provenances[0].get("datasetProvenance", {})
    return Provenance(
        dataset_name=str(dataset_provenance.get("datasetName", "")),
        filepath=str(dataset_provenance.get("filepath", "")),
        license=str(dataset_provenance.get("license", "")),
        note=str(dataset_provenance.get("note", "")),
    )


def build_sample_id(split: str, source_path: Path, line_number: int) -> str:
    """Tạo sample ID ổn định theo split, file và dòng."""
    key = f"{split}:{source_path.as_posix()}:{line_number}"
    return hashlib.sha1(key.encode("utf-8")).hexdigest()[:16]


def hash_tokens(tokens: list[str]) -> str:
    """Hash token để phát hiện duplicate trong preprocessing."""
    payload = json.dumps(tokens, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha1(payload.encode("utf-8")).hexdigest()
