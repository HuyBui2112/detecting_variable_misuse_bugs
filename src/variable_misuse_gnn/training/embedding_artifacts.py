"""Đọc shared embedding artifacts đã tạo trên Colab."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import torch


def load_token_to_id(embedding_root: Path) -> dict[str, int]:
    """Đọc vocabulary token dùng chung từ JSON."""
    path = embedding_root / "token_to_id.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    return {str(token): int(index) for token, index in data.items()}


def load_embedding_payload(embedding_root: Path) -> dict[str, Any]:
    """Đọc embedding initialization và config đi kèm."""
    path = embedding_root / "embedding_init.pt"
    return torch.load(path, map_location="cpu")


def load_embedding_config(embedding_root: Path) -> dict[str, Any]:
    """Đọc cấu hình embedding đã lưu."""
    path = embedding_root / "embedding_config.json"
    return json.loads(path.read_text(encoding="utf-8"))

