"""Loss functions cho localization và repair."""

from __future__ import annotations

import torch
import torch.nn.functional as F

from variable_misuse_gnn.training.dataset import GraphBatch


def compute_variable_misuse_loss(
    outputs: dict[str, torch.Tensor | list[torch.Tensor]],
    batch: GraphBatch,
) -> tuple[torch.Tensor, dict[str, float]]:
    """Tính tổng loss localization và repair theo batch."""
    localization_loss = compute_localization_loss(
        outputs["localization_logits"],
        outputs["no_bug_logits"],
        batch,
    )
    repair_loss = compute_repair_loss(outputs["repair_logits"], batch)
    total_loss = localization_loss + repair_loss
    return total_loss, {
        "localization_loss": float(localization_loss.detach().cpu().item()),
        "repair_loss": float(repair_loss.detach().cpu().item()),
    }


def compute_localization_loss(
    node_logits: torch.Tensor | list[torch.Tensor],
    no_bug_logits: torch.Tensor | list[torch.Tensor],
    batch: GraphBatch,
) -> torch.Tensor:
    """Cross-entropy trên node trong từng graph cộng thêm class no-bug."""
    assert isinstance(node_logits, torch.Tensor)
    assert isinstance(no_bug_logits, torch.Tensor)
    losses = []
    for graph_index, (start, end) in enumerate(zip(batch.graph_ptr[:-1], batch.graph_ptr[1:], strict=True)):
        logits = torch.cat([node_logits[start:end], no_bug_logits[graph_index].view(1)], dim=0)
        if batch.has_bug[graph_index]:
            target = batch.localization_targets[graph_index] - start
        else:
            target = (end - start).long().to(logits.device)
        losses.append(F.cross_entropy(logits.view(1, -1), target.view(1)))
    return torch.stack(losses).mean()


def compute_repair_loss(
    repair_logits: torch.Tensor | list[torch.Tensor],
    batch: GraphBatch,
) -> torch.Tensor:
    """Cross-entropy repair trên candidate set của bug samples."""
    assert isinstance(repair_logits, list)
    losses = []
    for graph_index, logits in enumerate(repair_logits):
        if not batch.has_bug[graph_index] or logits.numel() == 0:
            continue
        targets = batch.repair_targets[graph_index]
        candidates = batch.candidate_indices[graph_index]
        if targets.numel() == 0 or candidates.numel() == 0:
            continue
        target_positions = (candidates == targets[0]).nonzero(as_tuple=False)
        if target_positions.numel() == 0:
            continue
        target = target_positions[0, 0].view(1)
        losses.append(F.cross_entropy(logits.view(1, -1), target))
    if not losses:
        device = batch.node_token_ids.device
        return torch.tensor(0.0, device=device)
    return torch.stack(losses).mean()
