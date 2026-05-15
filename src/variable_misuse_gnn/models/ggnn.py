"""GGNN baseline cho bài toán Variable Misuse Localization và Repair."""

from __future__ import annotations

import torch
from torch import nn

from variable_misuse_gnn.training.dataset import GraphBatch


class GGNNVariableMisuseModel(nn.Module):
    """GGNN token-level với localization head và repair head."""

    def __init__(
        self,
        embedding_weight: torch.Tensor,
        hidden_dim: int,
        num_edge_types: int,
        message_passing_steps: int,
        dropout: float,
        freeze_embedding: bool = False,
    ) -> None:
        super().__init__()
        vocab_size, embedding_dim = embedding_weight.shape
        self.embedding = nn.Embedding(vocab_size, embedding_dim, padding_idx=0)
        self.embedding.weight.data.copy_(embedding_weight)
        self.embedding.weight.requires_grad = not freeze_embedding

        self.input_projection = nn.Linear(embedding_dim, hidden_dim)
        self.edge_transforms = nn.ModuleList(
            nn.Linear(hidden_dim, hidden_dim, bias=False) for _ in range(num_edge_types)
        )
        self.gru = nn.GRUCell(hidden_dim, hidden_dim)
        self.dropout = nn.Dropout(dropout)
        self.message_passing_steps = message_passing_steps

        self.localization_head = nn.Linear(hidden_dim, 1)
        self.no_bug_head = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 1),
        )
        self.repair_query = nn.Linear(hidden_dim, hidden_dim)
        self.repair_candidate = nn.Linear(hidden_dim, hidden_dim)

    def forward(self, batch: GraphBatch) -> dict[str, torch.Tensor | list[torch.Tensor]]:
        """Tính node hidden state và logits cho localization/repair."""
        hidden = self.input_projection(self.embedding(batch.node_token_ids))
        hidden = torch.relu(hidden)
        hidden = self.dropout(hidden)

        for _ in range(self.message_passing_steps):
            messages = torch.zeros_like(hidden)
            if batch.edge_index.numel() > 0:
                source_nodes = batch.edge_index[0]
                target_nodes = batch.edge_index[1]
                for edge_type, transform in enumerate(self.edge_transforms):
                    mask = batch.edge_types == edge_type
                    if not torch.any(mask):
                        continue
                    transformed = transform(hidden[source_nodes[mask]])
                    messages.index_add_(0, target_nodes[mask], transformed)
            hidden = self.gru(messages, hidden)
            hidden = self.dropout(hidden)

        localization_logits = self.localization_head(hidden).squeeze(-1)
        graph_embeddings = pool_graph_embeddings(hidden, batch.graph_ptr)
        no_bug_logits = self.no_bug_head(graph_embeddings).squeeze(-1)
        repair_logits = self.compute_repair_logits(hidden, batch)

        return {
            "node_hidden": hidden,
            "localization_logits": localization_logits,
            "no_bug_logits": no_bug_logits,
            "repair_logits": repair_logits,
        }

    def compute_repair_logits(self, hidden: torch.Tensor, batch: GraphBatch) -> list[torch.Tensor]:
        """Tính score repair trên candidate set của từng graph."""
        repair_logits: list[torch.Tensor] = []
        for graph_index, candidates in enumerate(batch.candidate_indices):
            if len(candidates) == 0:
                repair_logits.append(torch.empty((0,), device=hidden.device))
                continue
            bug_node = batch.localization_targets[graph_index]
            if bug_node < 0:
                # No-bug sample không dùng repair loss, vẫn trả logits để giữ API nhất quán.
                repair_logits.append(torch.empty((0,), device=hidden.device))
                continue
            query = self.repair_query(hidden[bug_node]).unsqueeze(0)
            candidate_states = self.repair_candidate(hidden[candidates])
            scores = (query * candidate_states).sum(dim=-1)
            repair_logits.append(scores)
        return repair_logits


def pool_graph_embeddings(hidden: torch.Tensor, graph_ptr: torch.Tensor) -> torch.Tensor:
    """Mean pooling node hidden state theo từng graph."""
    pooled = []
    for start, end in zip(graph_ptr[:-1], graph_ptr[1:], strict=True):
        pooled.append(hidden[start:end].mean(dim=0))
    return torch.stack(pooled, dim=0)

