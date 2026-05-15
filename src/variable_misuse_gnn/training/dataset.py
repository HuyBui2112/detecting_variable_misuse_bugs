"""Dataset và collate graph shards cho GGNN."""

from __future__ import annotations

import json
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import torch
from torch.utils.data import IterableDataset


@dataclass(frozen=True)
class GraphBatch:
    """Batch graph đã nối node/edge để đưa vào GGNN."""

    node_token_ids: torch.Tensor
    edge_index: torch.Tensor
    edge_types: torch.Tensor
    graph_ptr: torch.Tensor
    candidate_indices: list[torch.Tensor]
    localization_targets: torch.Tensor
    repair_targets: list[torch.Tensor]
    has_bug: torch.Tensor
    graph_ids: list[str]

    def to(self, device: torch.device) -> "GraphBatch":
        """Chuyển các tensor chính sang device runtime."""
        return GraphBatch(
            node_token_ids=self.node_token_ids.to(device),
            edge_index=self.edge_index.to(device),
            edge_types=self.edge_types.to(device),
            graph_ptr=self.graph_ptr.to(device),
            candidate_indices=[tensor.to(device) for tensor in self.candidate_indices],
            localization_targets=self.localization_targets.to(device),
            repair_targets=[tensor.to(device) for tensor in self.repair_targets],
            has_bug=self.has_bug.to(device),
            graph_ids=self.graph_ids,
        )


class GraphShardDataset(IterableDataset):
    """Đọc graph JSONL shard theo streaming để không tải hết dữ liệu vào RAM."""

    def __init__(
        self,
        graph_root: Path,
        graph_variant: str,
        split: str,
        token_to_id: dict[str, int],
        unk_idx: int,
        max_graphs: int | None = None,
    ) -> None:
        self.graph_dir = graph_root / graph_variant / split
        self.token_to_id = token_to_id
        self.unk_idx = unk_idx
        self.max_graphs = max_graphs

    def __iter__(self) -> Iterator[dict[str, Any]]:
        """Sinh từng graph đã map token sang id."""
        emitted = 0
        for shard_path in sorted(self.graph_dir.glob("shard_*.jsonl")):
            with shard_path.open("r", encoding="utf-8") as file:
                for line in file:
                    graph = json.loads(line)
                    graph["node_token_ids"] = [
                        self.token_to_id.get(token, self.unk_idx)
                        for token in graph["node_tokens"]
                    ]
                    yield graph
                    emitted += 1
                    if self.max_graphs is not None and emitted >= self.max_graphs:
                        return


def collate_graphs(graphs: list[dict[str, Any]]) -> GraphBatch:
    """Nối nhiều graph variable-size thành một batch sparse edge list."""
    node_token_ids: list[int] = []
    edge_indices: list[list[int]] = []
    edge_types: list[int] = []
    graph_ptr = [0]
    candidate_indices: list[torch.Tensor] = []
    localization_targets: list[int] = []
    repair_targets: list[torch.Tensor] = []
    has_bug: list[bool] = []
    graph_ids: list[str] = []
    node_offset = 0

    for graph in graphs:
        num_nodes = int(graph["num_nodes"])
        node_token_ids.extend(int(index) for index in graph["node_token_ids"])
        for edge, edge_type in zip(graph["edge_index"], graph["edge_types"], strict=True):
            edge_indices.append([int(edge[0]) + node_offset, int(edge[1]) + node_offset])
            edge_types.append(int(edge_type))

        local_candidates = torch.tensor(
            [int(index) + node_offset for index in graph["repair_candidates"]],
            dtype=torch.long,
        )
        candidate_indices.append(local_candidates)

        if graph["localization_target"] is None:
            localization_targets.append(-1)
        else:
            localization_targets.append(int(graph["localization_target"]) + node_offset)

        repair_targets.append(
            torch.tensor(
                [int(index) + node_offset for index in graph["repair_targets"]],
                dtype=torch.long,
            )
        )
        has_bug.append(bool(graph["has_bug"]))
        graph_ids.append(str(graph["graph_id"]))

        node_offset += num_nodes
        graph_ptr.append(node_offset)

    if edge_indices:
        edge_index_tensor = torch.tensor(edge_indices, dtype=torch.long).t().contiguous()
        edge_type_tensor = torch.tensor(edge_types, dtype=torch.long)
    else:
        edge_index_tensor = torch.empty((2, 0), dtype=torch.long)
        edge_type_tensor = torch.empty((0,), dtype=torch.long)

    return GraphBatch(
        node_token_ids=torch.tensor(node_token_ids, dtype=torch.long),
        edge_index=edge_index_tensor,
        edge_types=edge_type_tensor,
        graph_ptr=torch.tensor(graph_ptr, dtype=torch.long),
        candidate_indices=candidate_indices,
        localization_targets=torch.tensor(localization_targets, dtype=torch.long),
        repair_targets=repair_targets,
        has_bug=torch.tensor(has_bug, dtype=torch.bool),
        graph_ids=graph_ids,
    )

