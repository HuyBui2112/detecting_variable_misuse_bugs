"""Pipeline tiền xử lý dữ liệu GREAT."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from variable_misuse_gnn.data.preprocessing.config import PreprocessingConfig
from variable_misuse_gnn.data.preprocessing.normalizer import normalize_example
from variable_misuse_gnn.data.preprocessing.reader import iter_raw_examples
from variable_misuse_gnn.data.preprocessing.validation import validate_raw_example


SPLITS = ("train", "dev", "eval")


class SplitPreprocessor:
    """Bộ xử lý một split theo cấu hình lọc và cân bằng."""

    def __init__(self, split: str, config: PreprocessingConfig) -> None:
        self.split = split
        self.config = config
        self.seen_token_hashes: set[str] = set()
        self.class_counts: Counter[str] = Counter()
        self.counters: Counter[str] = Counter()
        self.edge_group_counts: Counter[str] = Counter()
        self.license_counts: Counter[str] = Counter()

    def process(self) -> dict[str, Any]:
        """Chạy tiền xử lý cho split và ghi JSONL đã chuẩn hóa."""
        output_path = self.config.output_root / f"{self.split}.jsonl"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with output_path.open("w", encoding="utf-8") as output_file:
            for source_path, line_number, raw_example, decode_error in iter_raw_examples(
                self.config.input_root, self.split
            ):
                self.counters["read"] += 1
                if raw_example is None:
                    self.counters[f"dropped_json_error:{decode_error}"] += 1
                    continue

                is_valid, reason = validate_raw_example(raw_example)
                if not is_valid:
                    self.counters[f"dropped_{reason}"] += 1
                    continue

                normalized = normalize_example(
                    raw_example, self.split, source_path, line_number, self.config
                )
                if self.has_augmented_repair_candidates(raw_example, normalized):
                    self.counters["fixed_repair_target_added_to_candidates"] += 1
                drop_reason = self.drop_reason(normalized)
                if drop_reason is not None:
                    self.counters[f"dropped_{drop_reason}"] += 1
                    continue

                output_file.write(
                    json.dumps(serialize_example(normalized, self.config), ensure_ascii=False) + "\n"
                )
                self.counters["written"] += 1
                class_name = "bug" if normalized.has_bug else "no_bug"
                self.class_counts[class_name] += 1
                self.seen_token_hashes.add(normalized.token_hash)
                self.license_counts[normalized.provenance.license] += 1
                for edge in normalized.normalized_edges:
                    self.edge_group_counts[edge.edge_group] += 1

        return {
            "split": self.split,
            "output_path": output_path.as_posix(),
            "counters": dict(self.counters),
            "class_counts": dict(self.class_counts),
            "edge_group_counts": dict(self.edge_group_counts),
            "license_counts": dict(self.license_counts),
        }

    def drop_reason(self, normalized: Any) -> str | None:
        """Xác định lý do loại sample nếu sample không đạt tiêu chí tiền xử lý."""
        if normalized.token_count > self.config.max_tokens:
            return "too_many_tokens"
        if len(normalized.normalized_edges) > self.config.max_edges:
            return "too_many_edges"
        if len(normalized.repair_candidates) < self.config.min_repair_candidates:
            return "too_few_repair_candidates"
        if (
            self.config.drop_duplicate_tokens_within_split
            and normalized.token_hash in self.seen_token_hashes
        ):
            return "duplicate_tokens_within_split"
        if self.config.balance_classes and self.config.max_samples_per_class is not None:
            class_name = "bug" if normalized.has_bug else "no_bug"
            if self.class_counts[class_name] >= self.config.max_samples_per_class:
                return "class_limit_reached"
        return None

    def has_augmented_repair_candidates(self, raw_example: dict[str, Any], normalized: Any) -> bool:
        """Kiểm tra candidate set có được bổ sung repair target hay không."""
        raw_candidates = {candidate for candidate in raw_example["repair_candidates"] if isinstance(candidate, int)}
        return not set(normalized.repair_targets).issubset(raw_candidates)


def run_preprocessing(config: PreprocessingConfig) -> dict[str, Any]:
    """Chạy toàn bộ pipeline tiền xử lý cho train/dev/eval."""
    split_reports = []
    for split in SPLITS:
        preprocessor = SplitPreprocessor(split, config)
        split_reports.append(preprocessor.process())

    report = {
        "input_root": config.input_root.as_posix(),
        "output_root": config.output_root.as_posix(),
        "max_tokens": config.max_tokens,
        "max_edges": config.max_edges,
        "min_repair_candidates": config.min_repair_candidates,
        "balance_classes": config.balance_classes,
        "max_samples_per_class": config.max_samples_per_class,
        "drop_duplicate_tokens_within_split": config.drop_duplicate_tokens_within_split,
        "output_format": config.output_format,
        "include_provenance": config.include_provenance,
        "splits": split_reports,
        "aggregate": aggregate_reports(split_reports),
    }
    config.report_path.parent.mkdir(parents=True, exist_ok=True)
    config.report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report


def aggregate_reports(split_reports: list[dict[str, Any]]) -> dict[str, Any]:
    """Tổng hợp báo cáo nhiều split."""
    aggregate_counters: dict[str, Counter[str]] = defaultdict(Counter)
    for split_report in split_reports:
        for key in ("counters", "class_counts", "edge_group_counts", "license_counts"):
            aggregate_counters[key].update(split_report.get(key, {}))
    return {key: dict(counter) for key, counter in aggregate_counters.items()}


def serialize_example(normalized: Any, config: PreprocessingConfig) -> dict[str, Any]:
    """Ghi sample theo format compact hoặc full."""
    if config.output_format == "full":
        data = normalized.to_json_dict()
        if not config.include_provenance:
            data.pop("provenance", None)
        return data

    if config.output_format != "compact":
        raise ValueError(f"Unsupported output_format: {config.output_format}")

    data = {
        "id": normalized.sample_id,
        "split": normalized.split,
        "tokens": normalized.source_tokens,
        "has_bug": normalized.has_bug,
        "loc": normalized.localization_target,
        "candidates": normalized.repair_candidates,
        "targets": normalized.repair_targets,
        # Edge compact: source, target, edge_group_id, raw_type_id.
        # Tên edge group có thể tra lại từ edge_types.py để tránh lặp chuỗi dài hàng trăm triệu lần.
        "edges": [
            [edge.source, edge.target, edge.edge_group_id, edge.raw_type_id]
            for edge in normalized.normalized_edges
        ],
    }
    if config.include_provenance:
        data["provenance"] = {
            "license": normalized.provenance.license,
            "filepath": normalized.provenance.filepath,
        }
    return data
