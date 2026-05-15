# Layout huấn luyện GGNN cho Variable Misuse

## 1. Vị trí của training layer trong pipeline

Pipeline tổng thể:

```text
1. Data audit
2. Preprocessing
3. Graph construction
4. Shared embedding artifacts
5. Training GGNN/GNN
6. Evaluation
7. Visualization/Demo
```

Tài liệu này mô tả **bước 5: Training GGNN/GNN**.

Phân biệt với embedding layer:

- **Embedding layer** tạo vocabulary và `embedding_init.pt` dùng chung.
- **Training layer** load embedding đó, đọc graph shards, chạy GGNN, tính loss, cập nhật trọng số, lưu checkpoint và metrics.

Như vậy phần code `src/variable_misuse_gnn/training/` đã là tầng huấn luyện, không còn là layout embedding.

## 2. Mục tiêu theo yêu cầu đồ án

Theo `instruction.md`, training phải phục vụ:

- dùng mô hình **Gated Graph Neural Network (GGNN)** hoặc GNN message passing tương đương;
- dự đoán vị trí biến bị dùng sai;
- đề xuất biến thay thế đúng;
- đánh giá bằng:
  - **Localization Accuracy**;
  - **Repair Accuracy**;
- so sánh graph chỉ có AST với graph có thêm Data Flow.

Bảng kết quả cuối cùng cần có dạng:

```text
Model / Graph Variant | Localization Accuracy | Repair Accuracy
```

Graph variants bắt buộc:

```text
ast_only
ast_next_token
ast_next_token_data_flow
```

## 3. Cơ sở lý thuyết từ tài liệu

Theo `gnn_documentation.md`:

- Program graph là **heterogeneous directed graph**.
- GNN/GGNN tính node embedding bằng message passing trên typed edges.
- Với Variable Misuse, model cần:
  - **localize** node buggy;
  - **repair** bằng cách chọn candidate symbol/variable trong scope.
- Localization có thể xem như pointer network trên variable usage nodes cộng thêm no-bug event.
- Repair có thể xem như pointer network trên candidate symbols tại vị trí bug.

Áp dụng vào project hiện tại:

- Node hiện là token node.
- Candidate variables được lưu trong `repair_candidates`.
- No-bug event được thêm trong localization head.
- Repair head chỉ scoring trên candidate set, không softmax toàn bộ vocabulary.

## 4. Input của training layer

### 4.1. Graph shards

Graph shards nằm trên Drive/Colab:

```text
/content/drive/MyDrive/variable_misuse_graph_build/dataset/graphs/great_colab_balanced_300000/
├── ast_only/
│   ├── train/
│   ├── dev/
│   └── eval/
├── ast_next_token/
└── ast_next_token_data_flow/
```

Mỗi graph JSONL có các field chính:

```text
node_tokens
edge_index
edge_types
has_bug
localization_target
repair_candidates
repair_targets
```

### 4.2. Shared embedding artifacts

Embedding artifacts dùng chung:

```text
/content/drive/MyDrive/variable_misuse_graph_build/artifacts/embedding/shared_token_embedding_300000/
├── token_to_id.json
├── id_to_token.json
├── embedding_config.json
├── vocabulary_summary.json
└── embedding_init.pt
```

Quy tắc:

- Cả 3 graph variants dùng cùng `token_to_id`.
- Cả 3 graph variants load cùng `embedding_init.pt`.
- Mỗi training run có checkpoint riêng theo graph variant.

## 5. Output của training layer

Mỗi variant ghi vào:

```text
/content/drive/MyDrive/variable_misuse_graph_build/artifacts/training/ggnn_shared_embedding_300000/<variant>/
├── best_model.pt
├── metrics_history.json
└── training_summary.json
```

Trong đó:

- `best_model.pt`: checkpoint tốt nhất theo dev Repair Accuracy.
- `metrics_history.json`: loss, Localization Accuracy, Repair Accuracy theo epoch.
- `training_summary.json`: config, device, embedding config và lịch sử metric.

## 6. Module source đã triển khai

```text
src/variable_misuse_gnn/models/
├── __init__.py
└── ggnn.py

src/variable_misuse_gnn/training/
├── __init__.py
├── config.py
├── dataset.py
├── embedding_artifacts.py
├── losses.py
└── trainer.py

src/variable_misuse_gnn/evaluation/
├── __init__.py
└── metrics.py

src/variable_misuse_gnn/utils/
├── __init__.py
├── device.py
└── seed.py

scripts/train_gnn.py
```

Vai trò:

| File | Vai trò |
| --- | --- |
| `models/ggnn.py` | GGNN message passing, localization head, repair head |
| `training/dataset.py` | Đọc graph shards, map token sang id, collate sparse batch |
| `training/embedding_artifacts.py` | Load shared vocabulary và embedding init |
| `training/losses.py` | Localization loss và repair loss |
| `training/trainer.py` | Train loop, evaluation loop, checkpoint, metrics |
| `evaluation/metrics.py` | Tích lũy Localization/Repair Accuracy |
| `utils/device.py` | Tự chọn GPU nếu có |
| `utils/seed.py` | Set seed để tái lập |
| `scripts/train_gnn.py` | CLI chạy trên Colab |

## 7. Tensorization và batching

Training loader đọc graph JSONL theo streaming để không tải toàn bộ dataset vào RAM.

Mỗi batch chuyển thành:

```text
node_token_ids: LongTensor[num_total_nodes]
edge_index: LongTensor[2, num_total_edges]
edge_types: LongTensor[num_total_edges]
graph_ptr: LongTensor[batch_size + 1]
candidate_indices: list[LongTensor]
localization_targets: LongTensor[batch_size]
repair_targets: list[LongTensor]
has_bug: BoolTensor[batch_size]
```

Lý do dùng sparse edge list:

- Graph có số node/edge thay đổi.
- `ast_next_token_data_flow` có nhiều edge do NextToken/Data Flow và inverse edges.
- Dense adjacency matrix không phù hợp bộ nhớ Colab.

## 8. Kiến trúc GGNN hiện tại

Pipeline model:

```text
node_token_ids
    ↓
shared nn.Embedding
    ↓
linear projection
    ↓
GGNN message passing theo edge_types
    ↓
node_hidden
    ↓
localization head + repair head
```

Thành phần chính:

- `nn.Embedding`: khởi tạo từ `embedding_init.pt`.
- `edge_transforms`: một linear transform riêng cho từng edge type.
- `GRUCell`: cập nhật hidden state sau mỗi bước message passing.
- `localization_head`: score từng node.
- `no_bug_head`: score no-bug event của từng graph.
- `repair_query` và `repair_candidate`: score candidate repair.

Hyperparameter mặc định:

```text
hidden_dim = 128
message_passing_steps = 4
dropout = 0.1
batch_size = 8
learning_rate = 1e-3
weight_decay = 1e-5
epochs = 5
```

## 9. Localization objective

Input:

- `node_hidden` của từng node;
- graph-level no-bug score.

Logits mỗi graph:

```text
[score(node_0), score(node_1), ..., score(node_n), score(NO_BUG)]
```

Target:

- Bug sample: local index của `localization_target`.
- No-bug sample: index đặc biệt `NO_BUG`.

Loss:

```text
CrossEntropy(localization_logits, localization_target_or_no_bug)
```

Metric:

```text
Localization Accuracy = correct localization predictions / total samples
```

## 10. Repair objective

Repair chỉ tính trên bug samples.

Input:

- hidden state của bug node;
- hidden state của candidate nodes trong `repair_candidates`.

Logits:

```text
score(candidate_0), score(candidate_1), ..., score(candidate_k)
```

Target:

- `repair_targets`.
- Nếu có nhiều target đúng, evaluation tính đúng khi predicted candidate nằm trong target set.
- Training baseline hiện dùng target đầu tiên để tính cross-entropy cho đơn giản.

Metric:

```text
Repair Accuracy = correct repair predictions / bug samples with candidates
```

Ghi chú cần báo cáo:

- Đây là baseline loss đơn giản.
- Có thể cải thiện bằng multi-positive loss ở vòng sau.

## 11. Training loop chuẩn

Mỗi epoch:

```text
1. Train loop trên train split
   - forward
   - localization loss
   - repair loss
   - total loss = localization + repair
   - backward
   - gradient clipping
   - optimizer step

2. Dev loop trên dev split
   - no grad
   - tính loss
   - tính Localization Accuracy
   - tính Repair Accuracy

3. Save checkpoint nếu dev Repair Accuracy tốt hơn
4. Ghi metrics_history.json sau mỗi epoch
```

Optimizer:

```text
AdamW
```

Checkpoint gồm:

```text
model_state_dict
optimizer_state_dict
epoch
dev_metrics
config
```

## 12. Chạy song song 3 Colab account

Chạy song song là hợp lý vì mỗi graph variant train độc lập nhưng dùng cùng embedding artifact.

Thiết lập chung:

```bash
cd /content/detecting_variable_misuse_bugs
export PYTHONPATH=src

GRAPH_ROOT=/content/drive/MyDrive/variable_misuse_graph_build/dataset/graphs/great_colab_balanced_300000
EMBEDDING_ROOT=/content/drive/MyDrive/variable_misuse_graph_build/artifacts/embedding/shared_token_embedding_300000
OUTPUT_ROOT=/content/drive/MyDrive/variable_misuse_graph_build/artifacts/training/ggnn_shared_embedding_300000
```

Account 1:

```bash
python scripts/train_gnn.py \
  --graph-root "$GRAPH_ROOT" \
  --embedding-root "$EMBEDDING_ROOT" \
  --output-root "$OUTPUT_ROOT" \
  --graph-variant ast_only \
  --epochs 5 \
  --batch-size 8 \
  --hidden-dim 128 \
  --message-passing-steps 4
```

Account 2:

```bash
python scripts/train_gnn.py \
  --graph-root "$GRAPH_ROOT" \
  --embedding-root "$EMBEDDING_ROOT" \
  --output-root "$OUTPUT_ROOT" \
  --graph-variant ast_next_token \
  --epochs 5 \
  --batch-size 8 \
  --hidden-dim 128 \
  --message-passing-steps 4
```

Account 3:

```bash
python scripts/train_gnn.py \
  --graph-root "$GRAPH_ROOT" \
  --embedding-root "$EMBEDDING_ROOT" \
  --output-root "$OUTPUT_ROOT" \
  --graph-variant ast_next_token_data_flow \
  --epochs 5 \
  --batch-size 8 \
  --hidden-dim 128 \
  --message-passing-steps 4
```

Nếu các account không chung Drive:

- copy `shared_token_embedding_300000.zip`;
- copy graph shards của variant tương ứng;
- giữ cùng cấu trúc `GRAPH_ROOT` và `EMBEDDING_ROOT` trong từng runtime.

## 13. Smoke test bắt buộc trước khi train dài

Trên mỗi account, chạy smoke test trước:

```bash
python scripts/train_gnn.py \
  --graph-root "$GRAPH_ROOT" \
  --embedding-root "$EMBEDDING_ROOT" \
  --output-root "$OUTPUT_ROOT/smoke_test" \
  --graph-variant ast_next_token_data_flow \
  --epochs 1 \
  --batch-size 4 \
  --hidden-dim 64 \
  --message-passing-steps 2 \
  --max-train-graphs 64 \
  --max-dev-graphs 64 \
  --log-every 10
```

Điều kiện pass:

```text
best_model.pt tồn tại
metrics_history.json tồn tại
training_summary.json tồn tại
loss hữu hạn
localization_total > 0
repair_total > 0
```

## 14. Evaluation và bảng kết quả

Sau training, lấy metric tốt nhất hoặc metric epoch cuối từ:

```text
artifacts/training/ggnn_shared_embedding_300000/<variant>/training_summary.json
```

Bảng báo cáo:

| Model / Graph Variant | Localization Accuracy | Repair Accuracy |
| --- | ---: | ---: |
| GGNN - `ast_only` | TBD | TBD |
| GGNN - `ast_next_token` | TBD | TBD |
| GGNN - `ast_next_token_data_flow` | TBD | TBD |

Cách diễn giải:

- Nếu `ast_next_token_data_flow` tốt hơn `ast_only`, kết luận Data Flow giúp bắt long-range dependencies trên subset.
- Nếu kết quả không cải thiện, phân tích giới hạn: subset, token-level graph, hyperparameter, synthetic bugs, loss đơn giản.

## 15. Các giới hạn hiện tại

- Model hiện là baseline GGNN token-level.
- Chưa dùng syntax node hoặc symbol node riêng vì compact GREAT output không giữ metadata đó.
- Repair loss dùng target đầu tiên nếu có nhiều repair targets.
- Chưa có batching tối ưu theo số node/edge, nên Colab có thể cần giảm batch size.
- Chưa có early stopping nâng cao ngoài checkpoint theo dev Repair Accuracy.

## 16. Điều chỉnh khi Colab thiếu tài nguyên

Nếu gặp OOM:

```text
batch_size: 8 -> 4 -> 2
hidden_dim: 128 -> 64
message_passing_steps: 4 -> 2
```

Nếu train quá lâu:

```text
epochs: 5 -> 3
max_train_graphs: dùng subset nhỏ để kiểm tra nhanh
```

Nếu muốn so sánh graph structure chặt hơn:

```bash
--freeze-embedding
```

nhưng model có thể kém hơn vì embedding không được fine-tune.

## 17. Definition of Done cho training layer

Training layer được xem là đạt khi:

- chạy được smoke test trên Colab;
- train được 3 variants hoặc ít nhất 2 variants `ast_only` và `ast_next_token_data_flow`;
- mỗi variant có `best_model.pt`, `metrics_history.json`, `training_summary.json`;
- báo cáo được Localization Accuracy và Repair Accuracy;
- bảng kết quả so sánh AST-only với Data Flow có số liệu thật;
- không tuyên bố kết quả trên full dataset nếu chỉ train trên balanced subset.

