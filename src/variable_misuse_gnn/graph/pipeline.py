"""Pipeline xây dựng Program Graph từ dữ liệu compact."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from variable_misuse_gnn.graph.builder import build_program_graph
from variable_misuse_gnn.graph.config import GraphConstructionConfig
from variable_misuse_gnn.graph.reader import iter_preprocessed_examples
from variable_misuse_gnn.graph.serializer import GraphShardWriter
from variable_misuse_gnn.graph.statistics import GraphConstructionStatistics
from variable_misuse_gnn.graph.validator import validate_preprocessed_example, validate_program_graph
from variable_misuse_gnn.graph.variants import get_graph_variant


def run_graph_construction(config: GraphConstructionConfig) -> dict[str, Any]:
    """Chạy graph construction cho các split trong cấu hình."""
    get_graph_variant(config.graph_variant)
    split_reports = [process_split(split, config) for split in config.splits]
    report = {
        "input_root": config.input_root.as_posix(),
        "output_root": config.output_root.as_posix(),
        "graph_variant": config.graph_variant,
        "splits": list(config.splits),
        "add_inverse_edges": config.add_inverse_edges,
        "add_self_loops": config.add_self_loops,
        "max_samples_per_split": config.max_samples_per_split,
        "shard_size": config.shard_size,
        "output_format": config.output_format,
        "dry_run": config.dry_run,
        "split_reports": split_reports,
        "aggregate": aggregate_split_reports(split_reports),
    }
    report_path = graph_report_path(config)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report


def process_split(split: str, config: GraphConstructionConfig) -> dict[str, Any]:
    """Xây dựng graph cho một split và trả về report."""
    stats = GraphConstructionStatistics()
    writer_context = NullWriter()
    if not config.dry_run:
        writer_context = GraphShardWriter(
            output_root=config.output_root,
            graph_variant=config.graph_variant,
            split=split,
            shard_size=config.shard_size,
        )

    with writer_context as writer:
        for line_number, example, decode_error in iter_preprocessed_examples(
            config.input_root,
            split,
            max_samples=config.max_samples_per_split,
        ):
            stats.counters["read"] += 1
            if example is None:
                stats.counters[f"dropped_json_error:{decode_error}"] += 1
                continue
            is_valid, reason = validate_preprocessed_example(example)
            if not is_valid:
                stats.counters[f"dropped_{reason}"] += 1
                continue

            try:
                graph = build_program_graph(example, config)
            except ValueError as error:
                stats.counters[f"dropped_build_error:{error}"] += 1
                continue

            is_graph_valid, graph_reason = validate_program_graph(graph)
            if not is_graph_valid:
                stats.counters[f"dropped_{graph_reason}"] += 1
                continue

            stats.update_graph(graph)
            if writer is not None:
                writer.write(graph)

    report = stats.to_json_dict()
    report["split"] = split
    report["max_samples_per_split"] = config.max_samples_per_split
    return report


class NullWriter:
    """Context manager rỗng cho chế độ dry-run."""

    def __enter__(self) -> None:
        """Không mở file khi dry-run."""
        return None

    def __exit__(self, exc_type: object, exc_value: object, traceback: object) -> None:
        """Không cần đóng file khi dry-run."""
        return None


def graph_report_path(config: GraphConstructionConfig) -> Path:
    """Trả về đường dẫn report của graph construction."""
    return config.output_root / config.graph_variant / "graph_construction_summary.json"


def aggregate_split_reports(split_reports: list[dict[str, Any]]) -> dict[str, Any]:
    """Tổng hợp counter chính từ các split report."""
    aggregate: dict[str, Any] = {
        "counters": {},
        "class_counts": {},
        "edge_type_counts": {},
    }
    for report in split_reports:
        for key in ("counters", "class_counts", "edge_type_counts"):
            for name, value in report.get(key, {}).items():
                aggregate[key][name] = aggregate[key].get(name, 0) + value
    return aggregate
