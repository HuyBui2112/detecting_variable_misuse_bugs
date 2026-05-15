"""Lazy dataset đọc sample compact và build graph khi cần."""

from __future__ import annotations

from collections.abc import Iterator

from variable_misuse_gnn.graph.builder import build_program_graph
from variable_misuse_gnn.graph.config import GraphConstructionConfig
from variable_misuse_gnn.graph.reader import iter_preprocessed_examples
from variable_misuse_gnn.graph.schema import ProgramGraph
from variable_misuse_gnn.graph.validator import validate_preprocessed_example, validate_program_graph


class LazyProgramGraphDataset:
    """Dataset streaming không materialize graph full ra đĩa."""

    def __init__(self, split: str, config: GraphConstructionConfig) -> None:
        self.split = split
        self.config = config

    def __iter__(self) -> Iterator[ProgramGraph]:
        """Sinh từng graph hợp lệ theo cấu hình hiện tại."""
        for _, example, _ in iter_preprocessed_examples(
            self.config.input_root,
            self.split,
            max_samples=self.config.max_samples_per_split,
        ):
            if example is None:
                continue
            is_valid, _ = validate_preprocessed_example(example)
            if not is_valid:
                continue
            graph = build_program_graph(example, self.config)
            is_graph_valid, _ = validate_program_graph(graph)
            if is_graph_valid:
                yield graph

