"""Thống kê chất lượng và kích thước Program Graph."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import Any

from variable_misuse_gnn.graph.schema import ProgramGraph


@dataclass
class RunningStats:
    """Thống kê min/mean/max cho một đại lượng số."""

    count: int = 0
    total: int = 0
    minimum: int | None = None
    maximum: int | None = None

    def update(self, value: int) -> None:
        """Cập nhật thống kê với một giá trị mới."""
        self.count += 1
        self.total += value
        self.minimum = value if self.minimum is None else min(self.minimum, value)
        self.maximum = value if self.maximum is None else max(self.maximum, value)

    def to_json_dict(self) -> dict[str, float | int | None]:
        """Chuyển thống kê sang dict JSON-friendly."""
        mean = 0.0 if self.count == 0 else self.total / self.count
        return {
            "count": self.count,
            "min": self.minimum,
            "max": self.maximum,
            "mean": mean,
        }


@dataclass
class GraphConstructionStatistics:
    """Tổng hợp thống kê cho một lần graph construction."""

    counters: Counter[str] = field(default_factory=Counter)
    class_counts: Counter[str] = field(default_factory=Counter)
    edge_type_counts: Counter[str] = field(default_factory=Counter)
    node_stats: RunningStats = field(default_factory=RunningStats)
    edge_stats: RunningStats = field(default_factory=RunningStats)
    candidate_stats: RunningStats = field(default_factory=RunningStats)

    def update_graph(self, graph: ProgramGraph) -> None:
        """Cập nhật thống kê từ một Program Graph hợp lệ."""
        self.counters["written"] += 1
        self.class_counts["bug" if graph.has_bug else "no_bug"] += 1
        self.node_stats.update(graph.num_nodes)
        self.edge_stats.update(len(graph.edge_index))
        self.candidate_stats.update(len(graph.repair_candidates))
        self.edge_type_counts.update(graph.edge_type_names)

    def to_json_dict(self) -> dict[str, Any]:
        """Chuyển thống kê sang dict để ghi report."""
        return {
            "counters": dict(self.counters),
            "class_counts": dict(self.class_counts),
            "edge_type_counts": dict(self.edge_type_counts),
            "node_stats": self.node_stats.to_json_dict(),
            "edge_stats": self.edge_stats.to_json_dict(),
            "candidate_stats": self.candidate_stats.to_json_dict(),
        }

