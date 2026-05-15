# Layout embedding cho Program Graph Variable Misuse

## 1. Mục tiêu

Tài liệu này phân tích các graph sample đã build và đề xuất layout embedding dùng cho bước training **GGNN/GNN**.

Input phân tích:

```text
dataset/samples_for_embedding_layout-20260515T115156Z-3-001/samples_for_embedding_layout/
├── ast_only_train_samples.jsonl
├── ast_only_dev_samples.jsonl
├── ast_next_token_train_samples.jsonl
├── ast_next_token_dev_samples.jsonl
├── ast_next_token_data_flow_train_samples.jsonl
├── ast_next_token_data_flow_dev_samples.jsonl
├── *_graph_construction_summary.json
```

Mục tiêu thiết kế:

- dùng **shared vocabulary** cho cả 3 graph variants;
- dùng cùng initialization embedding để so sánh công bằng;
- train/evaluate model riêng cho từng graph variant;
- bảo toàn label cho **Localization** và **Repair**;
- phù hợp chạy song song trên nhiều Colab account/runtime.

## 2. Kết quả phân tích mẫu graph

### 2.1. Schema graph thực tế

Mỗi graph sample có đủ các field:

```text
graph_id
split
graph_variant
num_nodes
node_tokens
node_types
candidate_mask
edge_index
edge_types
edge_type_names
edge_group_ids
raw_edge_types
has_bug
localization_target
repair_candidates
repair_targets
provenance
```

Kết luận:

- Schema đã đủ để build tensor input cho GNN.
- `node_tokens`, `candidate_mask`, labels giống nhau giữa các variants cùng sample.
- Khác biệt chính giữa variants nằm ở `edge_index`, `edge_types`, `edge_type_names`.

### 2.2. Summary graph construction trên balanced subset

Balanced subset đã build đủ 300,000 graph mỗi variant:

| Variant | Read | Written | Bug | No-bug |
| --- | ---: | ---: | ---: | ---: |
| `ast_only` | 300,000 | 300,000 | 150,000 | 150,000 |
| `ast_next_token` | 300,000 | 300,000 | 150,000 | 150,000 |
| `ast_next_token_data_flow` | 300,000 | 300,000 | 150,000 | 150,000 |

Edge type counts:

| Variant | Edge types |
| --- | --- |
| `ast_only` | `syntax`, `syntax_reverse` |
| `ast_next_token` | `syntax`, `syntax_reverse`, `next_token`, `next_token_reverse` |
| `ast_next_token_data_flow` | `syntax`, `syntax_reverse`, `next_token`, `next_token_reverse`, `data_flow`, `data_flow_reverse`, `lexical`, `lexical_reverse` |

Số lượng edge trên subset:

| Edge type | Count |
| --- | ---: |
| syntax | 8,315,620 |
| syntax_reverse | 8,315,620 |
| next_token | 57,649,150 |
| next_token_reverse | 57,649,150 |
| data_flow | 8,452,509 |
| data_flow_reverse | 8,452,509 |
| lexical | 3,830,171 |
| lexical_reverse | 3,830,171 |

### 2.3. Kích thước graph trong sample

Từ sample train/dev:

| Split sample | Num nodes | Num edges `ast_only` | Num edges `ast_next_token_data_flow` | Candidate count |
| --- | --- | --- | --- | --- |
| train sample | 21-356, mean 97.3 | mean 48.6 | mean 481.8 | 4-60, mean 16.3 |
| dev sample | 29-473, mean 135.7 | mean 82.8 | mean 712.6 | 7-67, mean 22.0 |

Kết luận:

- Graph có kích thước vừa phải sau preprocessing, nhưng edge count tăng mạnh khi thêm NextToken/Data Flow và inverse edges.
- Batching cần padding hoặc graph batching theo danh sách edge, không nên dùng adjacency dense matrix.
- Candidate set có thể lớn, repair head cần mask candidate thay vì softmax toàn bộ node.

### 2.4. Token pattern quan sát được

Top token thường gặp trong sample:

```text
#NEWLINE#, ), (, ., ,, :, =, #INDENT#, #UNINDENT#, self, return, if
```

Kết luận:

- Vocabulary cần giữ token đặc biệt như `#NEWLINE#`, `#INDENT#`, `#UNINDENT#`.
- Identifier tokens như `longitude`, `latitude`, `response`, `city`, `channel` cần được xử lý tốt.
- Nên hỗ trợ subtokenization để xử lý out-of-vocabulary identifier.

## 3. Quyết định thiết kế embedding

### 3.1. Dùng chung embedding cho cả 3 graph variants

Quyết định:

```text
Shared:
- vocabulary
- token/subtoken tokenizer
- token_to_id.json
- embedding initialization
- embedding config

Separate per graph variant:
- edge_index
- edge_types
- model checkpoint
- metrics
```

Lý do:

- Ba variants khác nhau ở graph structure, không khác ở token node.
- Dùng embedding khác nhau sẽ làm nhiễu so sánh AST-only với Data Flow.
- Shared vocabulary và same initialization giúp kết quả so sánh công bằng hơn.

### 3.2. Không pretrain Word2Vec trong giai đoạn đầu

Khuyến nghị giai đoạn đầu:

- Dùng `nn.Embedding` trainable.
- Build vocabulary từ `train` split của balanced subset.
- Khởi tạo cùng seed.
- Lưu `embedding_init.pt` để 3 Colab account dùng chung.

Lý do:

- Đơn giản, nhanh, dễ tái lập.
- Đủ tốt cho baseline GGNN.
- Tránh thêm dependency mới như gensim.

Nếu còn thời gian:

- Có thể bổ sung pretrained subtoken embedding hoặc Word2Vec, nhưng phải ghi rõ dependency và kiểm tra phiên bản.

## 4. Tokenization và vocabulary

### 4.1. Token normalization

Giữ nguyên các token đặc biệt:

```text
#NEWLINE#
#INDENT#
#UNINDENT#
```

Giữ nguyên Python keywords và punctuation:

```text
if, for, return, (, ), ., ,, :, =
```

Identifier nên được subtokenize để giảm OOV:

```text
max_len      -> max, len
identityPool -> identity, pool
HTTPResponse -> http, response
```

### 4.2. Vocabulary đề xuất

Hai tầng vocabulary:

```text
token_vocab:
  dùng cho token gốc thường gặp

subtoken_vocab:
  dùng fallback cho identifier hiếm/OOV
```

Thiết kế tối giản cho đồ án:

- Dùng một `token_to_id` trực tiếp trên `node_tokens`.
- Thêm special tokens:

```text
<PAD>
<UNK>
<MASK_NO_BUG>
```

Thiết kế tốt hơn:

- Tạo `subtoken_to_id`.
- Mỗi node token chuyển thành list subtoken ids.
- Node embedding = mean/max pooling embedding của subtokens.

Khuyến nghị triển khai:

- Giai đoạn 1: token-level embedding trực tiếp để nhanh có baseline.
- Giai đoạn 2: subtoken pooling nếu OOV cao hoặc model học kém identifier.

### 4.3. Giới hạn vocabulary

Đề xuất mặc định:

```text
max_vocab_size = 50000
min_frequency = 2
embedding_dim = 128
padding_idx = 0
unk_idx = 1
```

Lý do:

- Dataset 300k sample đủ lớn, token vocabulary có thể rất rộng do identifier.
- Giới hạn 50k giúp embedding matrix vừa phải.
- `128` là kích thước hợp lý cho baseline GGNN trên Colab.

## 5. Tensor input cho model

Mỗi batch graph nên chuyển thành:

```text
node_token_ids: LongTensor[num_total_nodes]
edge_index: LongTensor[2, num_total_edges]
edge_types: LongTensor[num_total_edges]
graph_ptr hoặc batch_index
candidate_mask: BoolTensor[num_total_nodes]
localization_target: LongTensor[batch_size]
repair_candidates: list[LongTensor]
repair_targets: list[LongTensor]
has_bug: BoolTensor[batch_size]
```

Không dùng adjacency dense matrix vì:

- số edge lớn;
- graph batch variable-size;
- sparse edge list phù hợp GGNN/PyTorch Geometric style.

## 6. Localization và Repair với embedding

### 6.1. Localization

Mỗi graph cần thêm một class đặc biệt `NO_BUG`.

Thiết kế head:

```text
node_hidden -> localization_score per node
graph_hidden/no_bug_vector -> no_bug_score
softmax([node_scores, no_bug_score])
```

Target:

- bug sample: index node `localization_target`;
- no-bug sample: special index `NO_BUG`.

### 6.2. Repair

Repair chỉ tính trên bug sample.

Thiết kế:

```text
bug_node_hidden + candidate_node_hidden -> repair_score per candidate
softmax(candidate_scores)
```

Target:

- `repair_targets` có thể có nhiều index đúng.
- Baseline có thể chọn target đầu tiên hoặc dùng multi-positive loss.

Khuyến nghị ban đầu:

- Nếu có nhiều repair targets, xem dự đoán đúng khi predicted candidate thuộc `repair_targets`.
- Training loss có thể dùng cross-entropy với target đầu tiên để đơn giản, nhưng evaluation nên dùng set membership.

## 7. Artifact dùng chung cho nhiều Colab account

Để chạy song song 3 variants trên 3 Colab account nhưng vẫn dùng chung embedding:

```text
artifacts/embedding/shared_v1/
├── token_to_id.json
├── id_to_token.json
├── embedding_config.json
├── embedding_init.pt
└── vocabulary_summary.json
```

Mỗi Colab account/runtime cần tải cùng gói:

```text
shared_embedding_artifacts.zip
```

Quy tắc:

- Không build vocabulary riêng trên từng variant.
- Không random init embedding riêng ở từng runtime.
- Luôn load `embedding_init.pt` trước khi train.

Nếu embedding trainable:

- Sau training, embedding weights của 3 model sẽ khác nhau.
- Điều này chấp nhận được vì cùng initialization và cùng vocabulary.

Nếu muốn kiểm soát chặt:

- Freeze embedding trong cả 3 runs.
- So sánh graph structure thuần hơn, nhưng model có thể kém linh hoạt.

## 8. Pipeline embedding đề xuất

```text
1. Read train graphs from one variant, ưu tiên ast_next_token_data_flow hoặc đọc processed subset
2. Count node_tokens
3. Build token_to_id với max_vocab_size/min_frequency
4. Initialize embedding matrix bằng cùng seed
5. Save shared embedding artifacts
6. Train 3 models riêng, mỗi model load cùng artifacts
7. Save checkpoint và metrics theo variant
```

Nên build vocabulary từ `train` split của balanced subset, không dùng `dev/eval`, để tránh leakage.

## 9. Module đề xuất

```text
src/variable_misuse_gnn/embedding/
├── __init__.py
├── config.py
├── tokenizer.py
├── vocabulary.py
├── initializer.py
├── serializer.py
└── tensorizer.py
```

Vai trò:

| File | Vai trò |
| --- | --- |
| `config.py` | Cấu hình vocabulary, embedding dim, seed, special tokens |
| `tokenizer.py` | Token normalization và optional subtokenization |
| `vocabulary.py` | Count token và build token_to_id |
| `initializer.py` | Tạo embedding_init.pt bằng seed cố định |
| `serializer.py` | Lưu/load artifacts JSON/PT |
| `tensorizer.py` | Chuyển ProgramGraph JSON thành tensor input |

Script đề xuất:

```text
scripts/build_embedding_artifacts.py
```

Notebook Colab:

```text
notebooks/build_embedding_colab.ipynb
```

## 10. Cấu hình đề xuất

```python
@dataclass(frozen=True)
class EmbeddingConfig:
    """Cấu hình xây dựng vocabulary và embedding dùng chung."""

    graph_root: Path
    output_root: Path
    source_variant: str = "ast_next_token_data_flow"
    split: str = "train"
    max_vocab_size: int = 50000
    min_frequency: int = 2
    embedding_dim: int = 128
    seed: int = 42
    pad_token: str = "<PAD>"
    unk_token: str = "<UNK>"
    no_bug_token: str = "<MASK_NO_BUG>"
```

## 11. Kiểm thử bắt buộc

Test nên kiểm tra:

- special tokens có id ổn định;
- cùng seed tạo cùng embedding init;
- unknown token map về `<UNK>`;
- graph sample chuyển thành `node_token_ids` đúng số node;
- candidate mask giữ đúng kích thước;
- không dùng dev/eval khi build vocabulary;
- artifacts load lại không đổi vocabulary.

## 12. Kết luận

Layout tốt nhất cho project hiện tại:

- **Shared token vocabulary + shared embedding initialization** cho cả 3 graph variants.
- **Train riêng 3 model** theo `ast_only`, `ast_next_token`, `ast_next_token_data_flow`.
- Chạy song song trên 3 Colab account được, miễn là copy cùng `shared_embedding_artifacts.zip`.
- Bắt đầu bằng token-level trainable embedding để nhanh có baseline.
- Chỉ nâng lên subtoken pooling khi cần cải thiện xử lý identifier/OOV.

