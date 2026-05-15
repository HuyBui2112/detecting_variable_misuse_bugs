"""Tiện ích chọn thiết bị chạy mô hình."""

from __future__ import annotations

import torch


def get_runtime_device() -> torch.device:
    """Chọn GPU nếu khả dụng, nếu không thì dùng CPU."""
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")

