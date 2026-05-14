"""Tải và audit GREAT Variable-Misuse dataset.

Script chỉ dùng thư viện chuẩn để tránh cài dependency vào môi trường hệ thống.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import platform
import shutil
import statistics
import subprocess
import sys
import time
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any


REPO_API_TREE_URL = (
    "https://api.github.com/repos/google-research-datasets/great/git/trees/master?recursive=1"
)
REPO_HEAD_URL = "https://api.github.com/repos/google-research-datasets/great/commits/master"
RAW_BASE_URL = "https://raw.githubusercontent.com/google-research-datasets/great/master"

DATASET_ROOT = Path("dataset")
RAW_ROOT = DATASET_ROOT / "raw" / "great"
INTERIM_ROOT = DATASET_ROOT / "interim"
AUDIT_ROOT = DATASET_ROOT / "audit"
SUBSET_ROOT = INTERIM_ROOT / "great_sample_subset"

REMOTE_MANIFEST_PATH = INTERIM_ROOT / "great_remote_shard_manifest.csv"
SAMPLE_MANIFEST_PATH = INTERIM_ROOT / "great_sample_manifest.csv"
AUDIT_SUMMARY_PATH = AUDIT_ROOT / "great_dataset_audit_summary.json"

REQUIRED_FIELDS = {
    "bug_kind",
    "bug_kind_name",
    "edges",
    "error_location",
    "has_bug",
    "provenances",
    "repair_candidates",
    "repair_targets",
    "source_tokens",
}

SPLITS = ("train", "dev", "eval")
MAX_TOKENS_FOR_SUBSET = 512


def parse_args() -> argparse.Namespace:
    """Đọc tham số dòng lệnh."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--download",
        choices=["all", "sample", "none"],
        default="all",
        help="Chọn phạm vi tải raw dataset.",
    )
    parser.add_argument(
        "--audit",
        choices=["all", "downloaded", "none"],
        default="all",
        help="Chọn phạm vi audit sample manifest.",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=4,
        help="Số luồng tải song song.",
    )
    parser.add_argument(
        "--subset-per-split",
        type=int,
        default=300,
        help="Số sample subset tối đa cho mỗi split.",
    )
    parser.add_argument(
        "--dataset-root",
        type=Path,
        default=Path("dataset"),
        help="Thư mục gốc để lưu raw/interim/audit dataset.",
    )
    return parser.parse_args()


def configure_dataset_paths(dataset_root: Path) -> None:
    """Cập nhật các đường dẫn output theo thư mục dataset được chọn."""
    global DATASET_ROOT
    global RAW_ROOT
    global INTERIM_ROOT
    global AUDIT_ROOT
    global SUBSET_ROOT
    global REMOTE_MANIFEST_PATH
    global SAMPLE_MANIFEST_PATH
    global AUDIT_SUMMARY_PATH

    DATASET_ROOT = dataset_root
    RAW_ROOT = DATASET_ROOT / "raw" / "great"
    INTERIM_ROOT = DATASET_ROOT / "interim"
    AUDIT_ROOT = DATASET_ROOT / "audit"
    SUBSET_ROOT = INTERIM_ROOT / "great_sample_subset"
    REMOTE_MANIFEST_PATH = INTERIM_ROOT / "great_remote_shard_manifest.csv"
    SAMPLE_MANIFEST_PATH = INTERIM_ROOT / "great_sample_manifest.csv"
    AUDIT_SUMMARY_PATH = AUDIT_ROOT / "great_dataset_audit_summary.json"


def fetch_json(url: str) -> Any:
    """Tải JSON từ URL."""
    request = urllib.request.Request(url, headers={"User-Agent": "variable-misuse-audit"})
    with urllib.request.urlopen(request, timeout=120) as response:
        return json.loads(response.read().decode("utf-8"))


def get_remote_files() -> tuple[str, list[dict[str, Any]]]:
    """Lấy commit và danh sách file remote từ GitHub API."""
    commit_info = fetch_json(REPO_HEAD_URL)
    tree = fetch_json(REPO_API_TREE_URL)
    files = [item for item in tree["tree"] if item.get("type") == "blob"]
    return commit_info["sha"], files


def split_from_path(path: str) -> str:
    """Suy ra split từ đường dẫn remote."""
    first = path.split("/", 1)[0]
    if first in SPLITS:
        return first
    return "metadata"


def write_remote_manifest(files: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Ghi manifest remote cho README, LICENSE và toàn bộ shard."""
    INTERIM_ROOT.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    for item in sorted(files, key=lambda value: value["path"]):
        path = item["path"]
        rows.append(
            {
                "split": split_from_path(path),
                "path": path,
                "name": Path(path).name,
                "size": int(item.get("size", 0) or 0),
                "sha": item.get("sha", ""),
                "download_url": f"{RAW_BASE_URL}/{path}",
            }
        )

    with REMOTE_MANIFEST_PATH.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["split", "path", "name", "size", "sha", "download_url"],
        )
        writer.writeheader()
        writer.writerows(rows)
    return rows


def select_download_rows(rows: list[dict[str, Any]], mode: str) -> list[dict[str, Any]]:
    """Chọn các file cần tải theo chế độ."""
    if mode == "none":
        return []
    if mode == "all":
        return rows

    selected_paths = {"README.md", "LICENSE"}
    for split in SPLITS:
        split_paths = sorted(row["path"] for row in rows if row["split"] == split)
        if split_paths:
            selected_paths.add(split_paths[0])
    return [row for row in rows if row["path"] in selected_paths]


def ensure_free_space(rows: list[dict[str, Any]]) -> dict[str, int]:
    """Kiểm tra dung lượng còn trống trước khi tải."""
    RAW_ROOT.mkdir(parents=True, exist_ok=True)
    needed_bytes = 0
    already_bytes = 0
    for row in rows:
        output_path = RAW_ROOT / row["path"]
        expected_size = int(row["size"])
        if output_path.exists() and output_path.stat().st_size == expected_size:
            already_bytes += expected_size
        else:
            needed_bytes += expected_size

    free_bytes = shutil.disk_usage(DATASET_ROOT).free
    # Chừa khoảng trống cho file tạm, manifest và hệ điều hành.
    safety_margin = 2 * 1024**3
    if needed_bytes + safety_margin > free_bytes:
        raise RuntimeError(
            "Không đủ dung lượng để tải dataset. "
            f"Cần thêm khoảng {needed_bytes / 1024**3:.2f} GiB, "
            f"còn trống {free_bytes / 1024**3:.2f} GiB."
        )
    return {
        "needed_bytes": needed_bytes,
        "already_downloaded_bytes": already_bytes,
        "free_bytes_before_download": free_bytes,
    }


def download_all(rows: list[dict[str, Any]], workers: int) -> dict[str, Any]:
    """Tải các file raw với resume theo kích thước file."""
    if not rows:
        return {"requested_files": 0, "downloaded_files": 0, "skipped_files": 0, "failed_files": []}

    space_info = ensure_free_space(rows)
    counters = Counter()
    failed_files: list[dict[str, str]] = []
    start = time.time()

    print(
        "download plan:",
        f"files={len(rows)}",
        f"need={space_info['needed_bytes'] / 1024**3:.2f} GiB",
        f"free={space_info['free_bytes_before_download'] / 1024**3:.2f} GiB",
    )

    with ThreadPoolExecutor(max_workers=max(1, workers)) as executor:
        future_to_row = {executor.submit(download_one, row): row for row in rows}
        for index, future in enumerate(as_completed(future_to_row), start=1):
            row = future_to_row[future]
            try:
                result = future.result()
            except Exception as error:  # noqa: BLE001
                failed_files.append({"path": row["path"], "error": str(error)})
                counters["failed"] += 1
            else:
                counters[result] += 1

            if index % 25 == 0 or index == len(rows):
                elapsed = max(1.0, time.time() - start)
                print(
                    "download progress:",
                    f"{index}/{len(rows)}",
                    f"downloaded={counters['downloaded']}",
                    f"skipped={counters['skipped']}",
                    f"failed={counters['failed']}",
                    f"elapsed={elapsed:.0f}s",
                )

    if failed_files:
        raise RuntimeError(f"Có {len(failed_files)} file tải lỗi: {failed_files[:5]}")

    return {
        "requested_files": len(rows),
        "downloaded_files": counters["downloaded"],
        "skipped_files": counters["skipped"],
        "failed_files": failed_files,
        **space_info,
    }


def download_one(row: dict[str, Any]) -> str:
    """Tải một file, bỏ qua nếu kích thước đã khớp."""
    output_path = RAW_ROOT / row["path"]
    expected_size = int(row["size"])
    if output_path.exists() and output_path.stat().st_size == expected_size:
        return "skipped"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = output_path.with_name(output_path.name + ".tmp")
    url = row["download_url"]
    last_error: Exception | None = None
    for attempt in range(1, 4):
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "variable-misuse-audit"})
            with urllib.request.urlopen(request, timeout=300) as response, temp_path.open("wb") as file:
                shutil.copyfileobj(response, file)
            actual_size = temp_path.stat().st_size
            if actual_size != expected_size:
                raise IOError(f"size mismatch: expected={expected_size}, actual={actual_size}")
            temp_path.replace(output_path)
            return "downloaded"
        except (urllib.error.URLError, TimeoutError, IOError) as error:
            last_error = error
            if temp_path.exists():
                temp_path.unlink()
            time.sleep(2 * attempt)
    raise RuntimeError(f"{url}: {last_error}")


def iter_shard_paths(scope: str) -> list[Path]:
    """Liệt kê shard local cần audit."""
    paths: list[Path] = []
    for split in SPLITS:
        split_paths = sorted((RAW_ROOT / split).glob(f"{split}__VARIABLE_MISUSE__SStuB.txt-*"))
        if scope == "downloaded":
            split_paths = split_paths[:1]
        paths.extend(split_paths)
    return paths


def validate_example(example: dict[str, Any]) -> tuple[str, str]:
    """Kiểm tra schema và index cơ bản của một sample."""
    missing_fields = sorted(REQUIRED_FIELDS - set(example))
    if missing_fields:
        return "missing_field", ";".join(missing_fields)

    tokens = example.get("source_tokens")
    if not isinstance(tokens, list) or not all(isinstance(token, str) for token in tokens):
        return "invalid_tokens", "source_tokens must be list[str]"
    if not tokens:
        return "empty_tokens", "source_tokens is empty"

    token_count = len(tokens)
    if example.get("has_bug") is True:
        error_location = example.get("error_location")
        if not isinstance(error_location, int) or not 0 <= error_location < token_count:
            return "invalid_error_location", str(error_location)

    for target in example.get("repair_targets", []):
        if not isinstance(target, int) or not 0 <= target < token_count:
            return "invalid_repair_target", str(target)

    for candidate in example.get("repair_candidates", []):
        if isinstance(candidate, int) and not 0 <= candidate < token_count:
            return "invalid_repair_candidate", str(candidate)

    for edge in example.get("edges", []):
        if not isinstance(edge, list) or len(edge) < 4:
            return "invalid_edge", str(edge)
        before_index, after_index = edge[0], edge[1]
        if not isinstance(before_index, int) or not isinstance(after_index, int):
            return "invalid_edge_endpoint", str(edge)
        if not 0 <= before_index < token_count or not 0 <= after_index < token_count:
            return "invalid_edge_endpoint", str(edge)

    return "ok", ""


def get_provenance_field(example: dict[str, Any], field_name: str) -> str:
    """Lấy trường provenance đầu tiên của sample."""
    provenances = example.get("provenances")
    if not isinstance(provenances, list) or not provenances:
        return ""
    first = provenances[0]
    if not isinstance(first, dict):
        return ""
    dataset_provenance = first.get("datasetProvenance", {})
    if not isinstance(dataset_provenance, dict):
        return ""
    return str(dataset_provenance.get(field_name, ""))


def stable_sample_id(split: str, shard_path: Path, line_number: int) -> str:
    """Tạo ID nội bộ ổn định."""
    key = f"{split}:{shard_path.as_posix()}:{line_number}"
    return hashlib.sha1(key.encode("utf-8")).hexdigest()[:16]


def hash_tokens(tokens: list[str]) -> str:
    """Hash chuỗi token để kiểm tra duplicate/leakage."""
    return hashlib.sha1(json.dumps(tokens, ensure_ascii=False).encode("utf-8")).hexdigest()


def audit_samples(scope: str, subset_per_split: int) -> dict[str, Any]:
    """Audit sample local và tạo sample manifest."""
    if scope == "none":
        return {}

    shard_paths = iter_shard_paths(scope)
    if not shard_paths:
        raise RuntimeError("Không tìm thấy shard local để audit.")

    SUBSET_ROOT.mkdir(parents=True, exist_ok=True)
    for subset_file in SUBSET_ROOT.glob("*_sample.jsonl"):
        subset_file.unlink()

    manifest_fields = [
        "sample_id",
        "split",
        "raw_shard",
        "line_number",
        "language",
        "has_bug",
        "bug_kind_name",
        "num_tokens",
        "num_edges",
        "num_repair_candidates",
        "num_repair_targets",
        "license",
        "filepath",
        "status",
        "note",
    ]

    split_counters: dict[str, Counter[str]] = defaultdict(Counter)
    status_counter: Counter[str] = Counter()
    edge_type_counter: Counter[str] = Counter()
    license_counter: Counter[str] = Counter()
    token_lengths: list[int] = []
    edge_lengths: list[int] = []
    filepath_sets: dict[str, set[str]] = defaultdict(set)
    token_hash_sets: dict[str, set[str]] = defaultdict(set)
    duplicate_hash_counter: Counter[str] = Counter()
    subset_counts: dict[str, Counter[str]] = defaultdict(Counter)
    file_error_counter: Counter[str] = Counter()
    total_samples = 0

    start = time.time()
    with SAMPLE_MANIFEST_PATH.open("w", encoding="utf-8", newline="") as manifest_file:
        writer = csv.DictWriter(manifest_file, fieldnames=manifest_fields)
        writer.writeheader()

        for shard_index, shard_path in enumerate(shard_paths, start=1):
            split = shard_path.parent.name
            with shard_path.open("r", encoding="utf-8") as file:
                for line_number, line in enumerate(file, start=1):
                    total_samples += 1
                    raw_line = line.rstrip("\n")
                    sample_id = stable_sample_id(split, shard_path, line_number)
                    try:
                        example = json.loads(raw_line)
                    except json.JSONDecodeError as error:
                        example = {}
                        status, note = "json_error", str(error)
                    else:
                        status, note = validate_example(example)

                    row = build_manifest_row(sample_id, split, shard_path, line_number, example, status, note)
                    writer.writerow(row)

                    status_counter[status] += 1
                    split_counters[split]["samples"] += 1
                    split_counters[split]["bug" if row["has_bug"] == "True" else "no_bug"] += 1
                    if status != "ok":
                        file_error_counter[shard_path.as_posix()] += 1

                    tokens = example.get("source_tokens", []) if isinstance(example, dict) else []
                    edges = example.get("edges", []) if isinstance(example, dict) else []
                    if isinstance(tokens, list):
                        token_lengths.append(len(tokens))
                        token_hash = hash_tokens(tokens)
                        token_hash_sets[split].add(token_hash)
                        duplicate_hash_counter[token_hash] += 1
                    if isinstance(edges, list):
                        edge_lengths.append(len(edges))
                        for edge in edges:
                            if isinstance(edge, list) and len(edge) >= 4:
                                edge_type_counter[str(edge[3])] += 1
                    if row["license"]:
                        license_counter[row["license"]] += 1
                    if row["filepath"]:
                        filepath_sets[split].add(row["filepath"])

                    maybe_write_subset(raw_line, split, row, subset_counts, subset_per_split)

            if shard_index % 25 == 0 or shard_index == len(shard_paths):
                elapsed = max(1.0, time.time() - start)
                print(
                    "audit progress:",
                    f"shards={shard_index}/{len(shard_paths)}",
                    f"samples={total_samples}",
                    f"elapsed={elapsed:.0f}s",
                )

    duplicate_candidates = sum(count - 1 for count in duplicate_hash_counter.values() if count > 1)
    return {
        "audit_scope": scope,
        "audited_shards": len(shard_paths),
        "sample_count": total_samples,
        "split_sample_counts": {split: dict(counter) for split, counter in split_counters.items()},
        "status_counts": dict(status_counter),
        "file_error_counts": dict(file_error_counter),
        "token_length_stats": numeric_stats(token_lengths),
        "edge_count_stats": numeric_stats(edge_lengths),
        "edge_type_counts": dict(edge_type_counter),
        "license_counts": dict(license_counter),
        "duplicate_token_hash_candidates": duplicate_candidates,
        "leakage_check": compute_leakage(filepath_sets, token_hash_sets),
        "subset_counts": {
            split: {
                "bug": counter.get("bug", 0),
                "no_bug": counter.get("no_bug", 0),
                "total": counter.get("bug", 0) + counter.get("no_bug", 0),
            }
            for split, counter in subset_counts.items()
        },
    }


def build_manifest_row(
    sample_id: str,
    split: str,
    shard_path: Path,
    line_number: int,
    example: dict[str, Any],
    status: str,
    note: str,
) -> dict[str, Any]:
    """Tạo một dòng sample manifest."""
    tokens = example.get("source_tokens", []) if isinstance(example, dict) else []
    edges = example.get("edges", []) if isinstance(example, dict) else []
    repair_candidates = example.get("repair_candidates", []) if isinstance(example, dict) else []
    repair_targets = example.get("repair_targets", []) if isinstance(example, dict) else []
    has_bug = example.get("has_bug", "") if isinstance(example, dict) else ""
    return {
        "sample_id": sample_id,
        "split": split,
        "raw_shard": shard_path.as_posix(),
        "line_number": line_number,
        "language": "python",
        "has_bug": str(has_bug),
        "bug_kind_name": example.get("bug_kind_name", "") if isinstance(example, dict) else "",
        "num_tokens": len(tokens) if isinstance(tokens, list) else 0,
        "num_edges": len(edges) if isinstance(edges, list) else 0,
        "num_repair_candidates": len(repair_candidates) if isinstance(repair_candidates, list) else 0,
        "num_repair_targets": len(repair_targets) if isinstance(repair_targets, list) else 0,
        "license": get_provenance_field(example, "license") if isinstance(example, dict) else "",
        "filepath": get_provenance_field(example, "filepath") if isinstance(example, dict) else "",
        "status": status,
        "note": note,
    }


def maybe_write_subset(
    raw_line: str,
    split: str,
    row: dict[str, Any],
    subset_counts: dict[str, Counter[str]],
    subset_per_split: int,
) -> None:
    """Ghi subset nhỏ, cân bằng tương đối bug/no-bug và ưu tiên sample ngắn."""
    if row["status"] != "ok":
        return
    if int(row["num_tokens"]) > MAX_TOKENS_FOR_SUBSET:
        return
    bug_key = "bug" if row["has_bug"] == "True" else "no_bug"
    total = subset_counts[split]["bug"] + subset_counts[split]["no_bug"]
    if total >= subset_per_split:
        return
    per_class_limit = max(1, subset_per_split // 2)
    if subset_counts[split][bug_key] >= per_class_limit:
        other_key = "no_bug" if bug_key == "bug" else "bug"
        if subset_counts[split][other_key] < per_class_limit:
            return

    subset_path = SUBSET_ROOT / f"{split}_sample.jsonl"
    with subset_path.open("a", encoding="utf-8") as file:
        file.write(raw_line + "\n")
    subset_counts[split][bug_key] += 1


def compute_leakage(
    filepath_sets: dict[str, set[str]], token_hash_sets: dict[str, set[str]]
) -> dict[str, int]:
    """Tính overlap filepath/token hash giữa split."""
    result: dict[str, int] = {}
    for left, right in [("train", "dev"), ("train", "eval"), ("dev", "eval")]:
        result[f"{left}_{right}_filepath_overlap"] = len(filepath_sets[left] & filepath_sets[right])
        result[f"{left}_{right}_token_hash_overlap"] = len(
            token_hash_sets[left] & token_hash_sets[right]
        )
    return result


def numeric_stats(values: list[int]) -> dict[str, float | int | None]:
    """Tính thống kê số đơn giản."""
    if not values:
        return {"count": 0, "min": None, "median": None, "p95": None, "max": None}
    sorted_values = sorted(values)
    p95_index = min(len(sorted_values) - 1, int(0.95 * (len(sorted_values) - 1)))
    return {
        "count": len(values),
        "min": min(values),
        "median": statistics.median(values),
        "p95": sorted_values[p95_index],
        "max": max(values),
    }


def summarize_remote(rows: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    """Tổng hợp số file/dung lượng remote."""
    summary: dict[str, dict[str, int]] = defaultdict(lambda: {"files": 0, "size_bytes": 0})
    for row in rows:
        summary[row["split"]]["files"] += 1
        summary[row["split"]]["size_bytes"] += int(row["size"])
    return dict(summary)


def summarize_local_raw() -> dict[str, Any]:
    """Thống kê raw files đã tải."""
    files = [path for path in RAW_ROOT.rglob("*") if path.is_file()]
    split_summary: dict[str, dict[str, int]] = defaultdict(lambda: {"files": 0, "size_bytes": 0})
    file_type_counts: Counter[str] = Counter()
    empty_files: list[str] = []
    largest_file = {"path": "", "size_bytes": 0}
    total_size = 0
    for path in files:
        size = path.stat().st_size
        total_size += size
        relative = path.relative_to(RAW_ROOT).as_posix()
        split = split_from_path(relative)
        split_summary[split]["files"] += 1
        split_summary[split]["size_bytes"] += size
        file_type_counts[path.suffix or "<no_suffix>"] += 1
        if size == 0:
            empty_files.append(path.as_posix())
        if size > largest_file["size_bytes"]:
            largest_file = {"path": path.as_posix(), "size_bytes": size}
    return {
        "total_files": len(files),
        "total_size_bytes": total_size,
        "split_summary": dict(split_summary),
        "file_type_counts": dict(file_type_counts),
        "empty_files": empty_files,
        "largest_file": largest_file,
    }


def environment_info() -> dict[str, Any]:
    """Thu thập thông tin môi trường chạy."""
    return {
        "python_executable": sys.executable,
        "python_version": sys.version.split()[0],
        "pip_version": run_command([sys.executable, "-m", "pip", "--version"]),
        "platform": platform.platform(),
        "nvidia_smi": run_command(
            ["nvidia-smi", "--query-gpu=name,memory.total,driver_version", "--format=csv,noheader"]
        ),
        "torch": torch_info(),
        "disk_usage_dataset_root": disk_usage(DATASET_ROOT),
    }


def run_command(command: list[str]) -> str:
    """Chạy lệnh môi trường và trả về output ngắn."""
    try:
        result = subprocess.run(command, check=False, capture_output=True, text=True, timeout=30)
    except (FileNotFoundError, subprocess.TimeoutExpired) as error:
        return str(error)
    return (result.stdout or result.stderr).strip()[:2000]


def torch_info() -> dict[str, Any]:
    """Kiểm tra PyTorch nếu đã cài."""
    try:
        import torch
    except Exception as error:  # noqa: BLE001
        return {"installed": False, "error": str(error)}
    return {
        "installed": True,
        "version": torch.__version__,
        "cuda_available": bool(torch.cuda.is_available()),
        "cuda_version": torch.version.cuda,
        "device_count": int(torch.cuda.device_count()),
    }


def disk_usage(path: Path) -> dict[str, int]:
    """Lấy dung lượng đĩa cho đường dẫn."""
    usage = shutil.disk_usage(path)
    return {"total_bytes": usage.total, "used_bytes": usage.used, "free_bytes": usage.free}


def write_summary(
    commit_sha: str,
    remote_rows: list[dict[str, Any]],
    download_summary: dict[str, Any],
    sample_audit: dict[str, Any],
    started_at: str,
) -> None:
    """Ghi audit summary JSON."""
    AUDIT_ROOT.mkdir(parents=True, exist_ok=True)
    summary = {
        "dataset_name": "GREAT Variable-Misuse dataset",
        "source": "https://github.com/google-research-datasets/great",
        "paper": "Global Relational Models of Source Code",
        "code_repository": "https://github.com/VHellendoorn/ICLR20-Great",
        "original_dataset": "ETHPy150Open",
        "language": "Python",
        "task": "Variable Misuse Localization and Repair",
        "audit_started_at": started_at,
        "audit_finished_at": time.strftime("%Y-%m-%d %H:%M:%S %z"),
        "remote_commit": commit_sha,
        "raw_root": RAW_ROOT.as_posix(),
        "remote_manifest": REMOTE_MANIFEST_PATH.as_posix(),
        "sample_manifest": SAMPLE_MANIFEST_PATH.as_posix(),
        "sample_subset_dir": SUBSET_ROOT.as_posix(),
        "remote_summary": summarize_remote(remote_rows),
        "download_summary": download_summary,
        "local_raw_summary": summarize_local_raw(),
        "schema_fields": sorted(REQUIRED_FIELDS),
        "sample_audit": sample_audit,
        "environment": environment_info(),
        "known_issues": [
            "Dataset rất lớn nên các bước sau cần xử lý streaming/batch.",
            "License nằm ở từng sample provenance, không nên xem toàn bộ dataset là một license đồng nhất.",
            "Nếu có token-hash overlap giữa split, cần phân tích trước khi kết luận data leakage.",
        ],
        "recommended_next_step": (
            "Đọc audit summary và manifest; sau đó thiết kế preprocessing riêng cho GREAT JSONL "
            "theo các trường source_tokens, edges, error_location, repair_candidates và repair_targets."
        ),
    }
    with AUDIT_SUMMARY_PATH.open("w", encoding="utf-8") as file:
        json.dump(summary, file, ensure_ascii=False, indent=2)


def main() -> None:
    """Chạy download và Data Understanding audit."""
    args = parse_args()
    configure_dataset_paths(args.dataset_root)
    started_at = time.strftime("%Y-%m-%d %H:%M:%S %z")
    RAW_ROOT.mkdir(parents=True, exist_ok=True)
    INTERIM_ROOT.mkdir(parents=True, exist_ok=True)
    AUDIT_ROOT.mkdir(parents=True, exist_ok=True)

    commit_sha, remote_files = get_remote_files()
    remote_rows = write_remote_manifest(remote_files)
    rows_to_download = select_download_rows(remote_rows, args.download)
    download_summary = download_all(rows_to_download, args.workers)
    sample_audit = audit_samples(args.audit, args.subset_per_split)
    write_summary(commit_sha, remote_rows, download_summary, sample_audit, started_at)

    print(f"remote manifest: {REMOTE_MANIFEST_PATH}")
    print(f"sample manifest: {SAMPLE_MANIFEST_PATH}")
    print(f"subset dir: {SUBSET_ROOT}")
    print(f"audit summary: {AUDIT_SUMMARY_PATH}")


if __name__ == "__main__":
    main()
