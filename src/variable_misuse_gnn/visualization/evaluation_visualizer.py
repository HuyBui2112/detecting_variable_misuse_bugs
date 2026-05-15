"""Vẽ bảng/biểu đồ và Program Graph cho kết quả evaluation."""

from __future__ import annotations

from collections import defaultdict, deque
from html import escape
from pathlib import Path
from typing import Any

import networkx as nx


def write_accuracy_chart(rows: list[dict[str, Any]], output_path: Path) -> None:
    """Vẽ biểu đồ so sánh Localization Accuracy và Repair Accuracy dạng SVG."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(build_accuracy_chart_svg(rows), encoding="utf-8")


def build_accuracy_chart_svg(rows: list[dict[str, Any]]) -> str:
    """Tạo SVG bar chart từ các dòng evaluation summary."""
    width = 960
    height = 520
    margin_left = 110
    margin_right = 40
    margin_top = 72
    margin_bottom = 110
    plot_width = width - margin_left - margin_right
    plot_height = height - margin_top - margin_bottom
    group_width = plot_width / max(len(rows), 1)
    bar_width = min(72, group_width * 0.28)
    y_axis_x = margin_left
    baseline_y = margin_top + plot_height

    parts = [
        svg_header(width, height),
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        text(width / 2, 34, "So sánh Localization Accuracy và Repair Accuracy", 22, "middle", "#111827"),
        text(width / 2, 58, "Kết quả trên split eval, dùng checkpoint tốt nhất trên dev", 13, "middle", "#4b5563"),
    ]

    for tick in range(0, 101, 20):
        y = baseline_y - (tick / 100) * plot_height
        parts.append(line(y_axis_x, y, width - margin_right, y, "#e5e7eb", 1))
        parts.append(text(y_axis_x - 12, y + 4, f"{tick}%", 12, "end", "#4b5563"))
    parts.append(line(y_axis_x, margin_top, y_axis_x, baseline_y, "#374151", 1.2))
    parts.append(line(y_axis_x, baseline_y, width - margin_right, baseline_y, "#374151", 1.2))

    colors = {
        "localization_accuracy": "#2563eb",
        "repair_accuracy": "#16a34a",
    }
    for index, row in enumerate(rows):
        group_center = margin_left + group_width * index + group_width / 2
        loc_value = float(row["localization_accuracy"])
        repair_value = float(row["repair_accuracy"])
        for offset, metric_name, value in [
            (-bar_width * 0.62, "localization_accuracy", loc_value),
            (bar_width * 0.62, "repair_accuracy", repair_value),
        ]:
            bar_height = value * plot_height
            x = group_center + offset - bar_width / 2
            y = baseline_y - bar_height
            parts.append(
                f'<rect x="{x:.2f}" y="{y:.2f}" width="{bar_width:.2f}" '
                f'height="{bar_height:.2f}" rx="4" fill="{colors[metric_name]}"/>'
            )
            parts.append(text(x + bar_width / 2, y - 8, f"{value:.3f}", 12, "middle", "#111827"))
        label = str(row["graph_variant"]).replace("_", " ")
        parts.append(rotated_text(group_center, baseline_y + 30, label, 12, "#111827"))

    legend_x = width - margin_right - 300
    legend_y = margin_top - 28
    parts.extend(
        [
            legend_item(legend_x, legend_y, "#2563eb", "Localization Accuracy"),
            legend_item(legend_x + 165, legend_y, "#16a34a", "Repair Accuracy"),
        ]
    )
    parts.append("</svg>")
    return "\n".join(parts)


def write_program_graph_svg(
    graph: dict[str, Any],
    prediction: dict[str, Any],
    output_path: Path,
    max_nodes: int = 45,
) -> None:
    """Vẽ Program Graph và đánh dấu node dự đoán lỗi bằng màu đỏ."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(build_program_graph_svg(graph, prediction, max_nodes), encoding="utf-8")


def build_program_graph_svg(
    graph: dict[str, Any],
    prediction: dict[str, Any],
    max_nodes: int,
) -> str:
    """Tạo SVG Program Graph từ một graph JSONL và prediction metadata."""
    selected_nodes = select_display_nodes(graph, prediction, max_nodes)
    display_graph = nx.DiGraph()
    for node_id in selected_nodes:
        display_graph.add_node(node_id)
    for edge, edge_type_name in zip(graph["edge_index"], graph["edge_type_names"], strict=True):
        source, target = int(edge[0]), int(edge[1])
        if source in selected_nodes and target in selected_nodes:
            display_graph.add_edge(source, target, edge_type_name=str(edge_type_name))

    if len(display_graph) == 1:
        only_node = next(iter(display_graph.nodes))
        positions = {only_node: (0.5, 0.5)}
    else:
        positions = nx.spring_layout(display_graph, seed=42, k=1.1, iterations=80)

    width = 1180
    height = 760
    margin = 92
    scaled = scale_positions(positions, width, height, margin)
    predicted_node = prediction.get("predicted_localization")
    target_node = graph.get("localization_target")
    repair_targets = set(int(value) for value in graph.get("repair_targets", []))
    repair_candidates = set(int(value) for value in graph.get("repair_candidates", []))

    title = (
        f"{graph.get('graph_variant', 'program_graph')} | graph_id={graph.get('graph_id')} | "
        f"pred={format_node_ref(predicted_node)} | target={format_node_ref(target_node)}"
    )
    parts = [
        svg_header(width, height),
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        text(width / 2, 34, "Program Graph cho Variable Misuse", 22, "middle", "#111827"),
        text(width / 2, 58, title, 12, "middle", "#4b5563"),
    ]

    edge_groups: dict[str, list[tuple[int, int]]] = defaultdict(list)
    for source, target, data in display_graph.edges(data=True):
        edge_groups[data.get("edge_type_name", "edge")].append((source, target))
    for edge_type_name, edges in edge_groups.items():
        color = edge_color(edge_type_name)
        for source, target in edges:
            x1, y1 = scaled[source]
            x2, y2 = scaled[target]
            parts.append(line(x1, y1, x2, y2, color, 1.4, opacity=0.48))

    for node_id in display_graph.nodes:
        x, y = scaled[node_id]
        fill, stroke, radius = node_style(
            node_id=node_id,
            predicted_node=predicted_node,
            target_node=target_node,
            repair_targets=repair_targets,
            repair_candidates=repair_candidates,
        )
        parts.append(
            f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{radius}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="2"/>'
        )
        label = truncate_token(str(graph["node_tokens"][node_id]), max_length=16)
        parts.append(text(x, y + radius + 14, label, 10, "middle", "#111827"))
        parts.append(text(x, y + 4, str(node_id), 10, "middle", "#111827"))

    parts.extend(build_graph_legend(26, height - 120))
    provenance = graph.get("provenance", {})
    filepath = provenance.get("filepath", "")
    if filepath:
        parts.append(text(24, height - 18, f"source: {filepath}", 11, "start", "#4b5563"))
    if len(selected_nodes) < int(graph["num_nodes"]):
        parts.append(
            text(
                width - 24,
                height - 18,
                f"hiển thị {len(selected_nodes)}/{graph['num_nodes']} node quanh prediction/target",
                11,
                "end",
                "#4b5563",
            )
        )
    parts.append("</svg>")
    return "\n".join(parts)


def select_display_nodes(graph: dict[str, Any], prediction: dict[str, Any], max_nodes: int) -> set[int]:
    """Chọn node quan trọng quanh prediction, ground-truth và repair candidates."""
    num_nodes = int(graph["num_nodes"])
    if num_nodes <= max_nodes:
        return set(range(num_nodes))

    important_nodes = {
        value
        for value in [
            prediction.get("predicted_localization"),
            graph.get("localization_target"),
            prediction.get("predicted_repair"),
        ]
        if value is not None
    }
    important_nodes.update(int(value) for value in graph.get("repair_targets", []))
    important_nodes.update(int(value) for value in graph.get("repair_candidates", [])[:10])

    adjacency: dict[int, set[int]] = defaultdict(set)
    for source, target in graph["edge_index"]:
        source_id = int(source)
        target_id = int(target)
        adjacency[source_id].add(target_id)
        adjacency[target_id].add(source_id)

    selected = set(int(value) for value in important_nodes if 0 <= int(value) < num_nodes)
    queue = deque((node_id, 0) for node_id in selected)
    while queue and len(selected) < max_nodes:
        node_id, depth = queue.popleft()
        if depth >= 2:
            continue
        for neighbor in sorted(adjacency[node_id]):
            if neighbor in selected:
                continue
            selected.add(neighbor)
            queue.append((neighbor, depth + 1))
            if len(selected) >= max_nodes:
                break

    for node_id in range(num_nodes):
        if len(selected) >= max_nodes:
            break
        selected.add(node_id)
    return selected


def scale_positions(
    positions: dict[int, tuple[float, float]],
    width: int,
    height: int,
    margin: int,
) -> dict[int, tuple[float, float]]:
    """Scale tọa độ spring layout sang viewport SVG."""
    xs = [position[0] for position in positions.values()]
    ys = [position[1] for position in positions.values()]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    span_x = max(max_x - min_x, 1e-6)
    span_y = max(max_y - min_y, 1e-6)
    return {
        node_id: (
            margin + ((x - min_x) / span_x) * (width - margin * 2),
            margin + 10 + ((y - min_y) / span_y) * (height - margin * 2 - 40),
        )
        for node_id, (x, y) in positions.items()
    }


def node_style(
    node_id: int,
    predicted_node: int | None,
    target_node: int | None,
    repair_targets: set[int],
    repair_candidates: set[int],
) -> tuple[str, str, int]:
    """Trả về màu node theo vai trò trong prediction."""
    if node_id == predicted_node and node_id == target_node:
        return "#7c3aed", "#4c1d95", 18
    if node_id == predicted_node:
        return "#dc2626", "#7f1d1d", 18
    if node_id == target_node:
        return "#16a34a", "#14532d", 18
    if node_id in repair_targets:
        return "#22c55e", "#15803d", 15
    if node_id in repair_candidates:
        return "#f59e0b", "#92400e", 13
    return "#e5e7eb", "#6b7280", 11


def edge_color(edge_type_name: str) -> str:
    """Chọn màu cạnh theo nhóm edge."""
    lowered = edge_type_name.lower()
    if "data_flow" in lowered:
        return "#2563eb"
    if "next_token" in lowered:
        return "#64748b"
    if "lexical" in lowered:
        return "#9333ea"
    if "syntax" in lowered:
        return "#94a3b8"
    return "#9ca3af"


def build_graph_legend(x: int, y: int) -> list[str]:
    """Tạo chú giải màu node và edge cho SVG graph."""
    items = [
        ("#dc2626", "predicted bug node"),
        ("#16a34a", "ground-truth bug node"),
        ("#f59e0b", "repair candidate"),
        ("#2563eb", "Data Flow edge"),
        ("#64748b", "NextToken edge"),
    ]
    parts = [text(x, y - 12, "Legend", 13, "start", "#111827")]
    for index, (color, label) in enumerate(items):
        item_y = y + index * 20
        parts.append(f'<circle cx="{x + 8}" cy="{item_y}" r="6" fill="{color}"/>')
        parts.append(text(x + 22, item_y + 4, label, 11, "start", "#374151"))
    return parts


def legend_item(x: float, y: float, color: str, label: str) -> str:
    """Tạo một item legend cho bar chart."""
    return (
        f'<rect x="{x:.2f}" y="{y:.2f}" width="14" height="14" rx="3" fill="{color}"/>'
        f'{text(x + 22, y + 12, label, 12, "start", "#374151")}'
    )


def text(x: float, y: float, content: str, size: int, anchor: str, color: str) -> str:
    """Tạo SVG text đã escape nội dung."""
    return (
        f'<text x="{x:.2f}" y="{y:.2f}" font-family="Arial, sans-serif" '
        f'font-size="{size}" text-anchor="{anchor}" fill="{color}">{escape(content)}</text>'
    )


def rotated_text(x: float, y: float, content: str, size: int, color: str) -> str:
    """Tạo label nghiêng cho trục x."""
    return (
        f'<text x="{x:.2f}" y="{y:.2f}" font-family="Arial, sans-serif" '
        f'font-size="{size}" text-anchor="end" fill="{color}" '
        f'transform="rotate(-28 {x:.2f} {y:.2f})">{escape(content)}</text>'
    )


def line(
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    color: str,
    width: float,
    opacity: float = 1.0,
) -> str:
    """Tạo SVG line."""
    return (
        f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" '
        f'stroke="{color}" stroke-width="{width}" opacity="{opacity}"/>'
    )


def svg_header(width: int, height: int) -> str:
    """Tạo header SVG."""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img">'
    )


def truncate_token(token: str, max_length: int) -> str:
    """Rút gọn token dài để label không đè lên graph."""
    token = token.replace("#NEWLINE#", "NL")
    if len(token) <= max_length:
        return token
    return token[: max_length - 3] + "..."


def format_node_ref(node_id: int | None) -> str:
    """Format node id, xử lý trường hợp model dự đoán no-bug."""
    if node_id is None:
        return "no-bug"
    return str(node_id)
