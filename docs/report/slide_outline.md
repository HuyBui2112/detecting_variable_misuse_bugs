# Sườn slide báo cáo theo yêu cầu

Đề tài: **Graph Neural Networks in Program Analysis - Detecting Variable Misuse Bugs**

Thời lượng mục tiêu: **20 phút trình bày + demo ngắn**.

Nguyên tắc:

- Tập trung vào **Variable Misuse**, **Program Graph**, **GNN/GGNN**, **Localization** và **Repair**.
- Không chuyển sang social network analysis, graph mining tổng quát hoặc community detection.
- Số liệu nào đã có thì ghi rõ; kết quả training/evaluation chưa chạy thì để placeholder, không bịa số.

## 1. Giới thiệu bài toán

### Slide 1. Tiêu đề và định hướng

Tiêu đề:

**Detecting Variable Misuse Bugs using Program Graphs and Graph Neural Networks**

Nội dung:

- Bài toán: phát hiện lỗi dùng sai biến trong chương trình.
- Hướng tiếp cận: chuyển mã nguồn thành **Program Graph** và dùng **GNN/GGNN** để học ngữ cảnh.
- Hai nhiệm vụ chính:
  - **Localization**: tìm vị trí biến bị dùng sai.
  - **Repair**: đề xuất biến thay thế đúng.

Gợi ý trình bày:

- Đây là bài toán program analysis bằng machine learning.
- Graph giúp biểu diễn quan hệ cú pháp và luồng dữ liệu trong code.

### Slide 2. 1.1. Dataset

Dataset sử dụng:

- GREAT Variable Misuse dataset.
- Liên quan paper **Global Relational Models of Source Code**.
- Dữ liệu phù hợp vì đã có:
  - token sequence;
  - nhãn `has_bug`;
  - vị trí lỗi `loc`;
  - danh sách biến ứng viên `candidates`;
  - biến sửa đúng `targets`;
  - typed edges cho syntax, NextToken, Data Flow.

Số liệu sau preprocessing:

| Split | Số sample |
| --- | ---: |
| Train | 1,756,340 |
| Dev | 181,478 |
| Eval | 946,505 |
| Tổng | 2,884,323 |

Thống kê nhãn:

| Nhãn | Số sample |
| --- | ---: |
| Bug | 1,434,367 |
| No-bug | 1,449,956 |

Ghi chú:

- Dataset gốc lớn nên project dùng streaming JSONL.
- Dữ liệu preprocessing đã được lưu trên Google Drive để tái sử dụng trên Colab.

### Slide 3. 1.2. Giới thiệu chủ đề Variable Misuse

Định nghĩa:

- **Variable Misuse** xảy ra khi lập trình viên dùng nhầm một biến đang có trong scope thay vì biến đúng về mặt ngữ nghĩa.
- Code vẫn có thể đúng cú pháp, nên compiler/static checker có thể bỏ sót.

Ví dụ:

```python
def truncate(content, min_len, max_len):
    if len(content) > max_len:
        return content[:min_len]  # Bug: nên dùng max_len
    return content
```

Phân tích:

- Bug location: token `min_len`.
- Repair target: `max_len`.
- Model cần hiểu quan hệ giữa biến, điều kiện và biểu thức trả về.

Nguồn lý thuyết:

- **Learning to Represent Programs with Graphs** định nghĩa bài toán Variable Misuse gồm localize và repair.
- `instruction.md` yêu cầu đánh giá bằng **Localization Accuracy** và **Repair Accuracy**.

### Slide 4. 1.3. Các loại graph sử dụng

Ba graph variants chính:

| Variant | Edge group | Vai trò |
| --- | --- | --- |
| `ast_only` | syntax | Baseline chỉ dùng cấu trúc AST/syntax |
| `ast_next_token` | syntax + next_token | Thêm thứ tự token tuyến tính |
| `ast_next_token_data_flow` | syntax + next_token + data_flow + lexical | Graph chính để kiểm tra Data Flow |

Ý nghĩa:

- `ast_only`: kiểm tra graph cú pháp cơ bản.
- `ast_next_token`: thêm luồng đọc code từ trái sang phải.
- `ast_next_token_data_flow`: thêm quan hệ dùng/ghi/tính toán biến để bắt phụ thuộc xa.

Quy ước inverse edges:

| Base edge | Reverse edge |
| --- | --- |
| `syntax` | `syntax_reverse` |
| `next_token` | `next_token_reverse` |
| `data_flow` | `data_flow_reverse` |
| `lexical` | `lexical_reverse` |

Ghi chú:

- Inverse edges giúp message passing truyền thông tin hai chiều.
- `syntax_reverse` tương ứng ý tưởng `Parent` trong `Child/Parent`.

## 2. Lý thuyết

### Slide 5. 2.1. Giới thiệu graph trong program analysis

Theo `gnn_documentation.md`:

- Program có thể biểu diễn thành **heterogeneous directed graph**.
- Node có thể là:
  - **Token Node**: token trong source code.
  - **Syntax Node**: node AST/syntax.
  - **Symbol Node**: biến/hàm/symbol trong scope.
- Edge biểu diễn quan hệ trong chương trình:
  - Syntax relation.
  - Token order.
  - Data Flow.
  - Control/Semantic relations nếu có.

Vì sao dùng graph:

- Sequence model dễ bỏ sót quan hệ xa.
- Graph giữ được quan hệ cú pháp và ngữ nghĩa.
- Data Flow giúp mô hình thấy các lần sử dụng biến cách xa nhau.

### Slide 6. 2.2. Chuyển đổi tập dữ liệu sang graph

Input sau preprocessing là compact JSONL:

```json
{
  "tokens": ["def f(", "x", ",", "y", ")", ":", "return", "x"],
  "has_bug": true,
  "loc": 7,
  "candidates": [1, 3, 7],
  "targets": [1],
  "edges": [[0, 1, 0, 7]]
}
```

Edge compact:

```text
[source, target, edge_group_id, raw_type_id]
```

Mapping edge group:

| ID | Nhóm | Ý nghĩa |
| ---: | --- | --- |
| 0 | `syntax` | AST/Child edge |
| 1 | `next_token` | NextToken |
| 2 | `data_flow` | LastRead, LastWrite, ComputedFrom |
| 3 | `lexical` | LastUse-like |
| 4 | `semantic` | Formal argument name |
| 5 | `control_flow` | CFG, ReturnsTo, Calls |

Quyết định triển khai:

- Không parse lại source bằng `ast`.
- Dùng trực tiếp edges đã chuẩn hóa từ GREAT/preprocessing.
- Graph hiện tại là **token-level program graph with typed edges**.

### Slide 7. 2.3. Áp dụng graph cho bài toán Variable Misuse

Mỗi sample được chuyển thành `ProgramGraph`:

```text
ProgramGraph
├── node_tokens
├── candidate_mask
├── edge_index
├── edge_types
├── has_bug
├── localization_target
├── repair_candidates
└── repair_targets
```

Cách dùng trong bài toán:

- `localization_target = loc` nếu sample có bug.
- `repair_candidates = candidates`.
- `repair_targets = targets`.
- `candidate_mask` đánh dấu node nào là candidate repair.

Hai module dự đoán:

- **Localization head**: chọn vị trí biến bị dùng sai hoặc no-bug.
- **Repair head**: chọn biến thay thế trong candidate set.

Metric:

| Metric | Ý nghĩa |
| --- | --- |
| Localization Accuracy | Tỉ lệ dự đoán đúng vị trí bug/no-bug |
| Repair Accuracy | Tỉ lệ đề xuất đúng biến sửa |

### Slide 8. 2.4. Các đặc trưng được áp dụng trong graph

Node features hiện có:

- Token text.
- Node type: `"token"`.
- Candidate mask.

Edge features:

- `edge_index`: source-target.
- `edge_type`: relation id cho GGNN.
- `edge_type_name`: tên relation.
- `raw_type_id`: metadata để debug/thống kê.

Label features:

- `has_bug`.
- `localization_target`.
- `repair_candidates`.
- `repair_targets`.

Edge type vocabulary:

| Base group | Forward | Reverse |
| --- | ---: | ---: |
| syntax | 0 | 1 |
| next_token | 2 | 3 |
| data_flow | 4 | 5 |
| lexical | 6 | 7 |
| semantic | 8 | 9 |
| control_flow | 10 | 11 |

Ghi chú:

- `raw_type_id` không dùng làm edge type chính để model dễ giải thích hơn.
- `lexical` được dùng cùng Data Flow vì GREAT có `enum_LAST_LEXICAL_USE`.

### Slide 9. Lý thuyết mô hình GGNN/GNN

Nội dung:

- GGNN thực hiện **message passing** trên graph có nhiều loại edge.
- Mỗi edge type có tham số riêng.
- Node hidden state được cập nhật qua nhiều bước lan truyền.
- Sau message passing:
  - embedding node phục vụ localization;
  - embedding bug position + candidate phục vụ repair.

Pipeline mô hình dự kiến:

```text
Program Graph
    ↓
Token Embedding
    ↓
GGNN Message Passing
    ↓
Localization Head + Repair Head
```

Nguồn:

- **Learning to Represent Programs with Graphs**: nền tảng GGNN/Variable Misuse.
- **Global Relational Models of Source Code**: GREAT và relational graph bias.

## 3. Sơ đồ - workflow

### Slide 10. 3.1. Methodology tổng quát

Workflow:

```text
Raw GREAT dataset
      ↓
Data audit
      ↓
Preprocessing
      ↓
Compact JSONL
      ↓
Balanced subset
      ↓
Graph construction
      ↓
Graph variants
      ↓
Training GGNN/GNN
      ↓
Evaluation + Visualization
```

Mục tiêu từng bước:

- Audit: hiểu schema, dung lượng, license, split.
- Preprocessing: validate, filter, normalize edge.
- Balanced subset: giảm chi phí Colab, giữ tỉ lệ split và cân bằng nhãn.
- Graph construction: tạo `ProgramGraph` cho từng variant.
- Training/evaluation: so sánh Localization/Repair Accuracy.

### Slide 11. 3.2. Pipeline tiền xử lý đã hoàn thành

Module đã có:

```text
src/variable_misuse_gnn/data/preprocessing/
├── config.py
├── edge_types.py
├── normalizer.py
├── pipeline.py
├── reader.py
├── schema.py
└── validation.py
```

Script:

```text
scripts/preprocess_great_data.py
```

Đã làm:

- Đọc JSONL theo streaming.
- Validate schema và index.
- Chuẩn hóa edge group.
- Thêm linear NextToken nếu cần.
- Ghi compact JSONL để giảm dung lượng.
- Ghi `preprocessing_summary.json`.

Output hiện có:

```text
dataset/processed/great_colab/
├── train.jsonl
├── dev.jsonl
├── eval.jsonl
└── preprocessing_summary.json
```

### Slide 12. 3.3. Pipeline xây dựng graph đã hoàn thành

Module đã có:

```text
src/variable_misuse_gnn/graph/
├── config.py
├── variants.py
├── schema.py
├── builder.py
├── validator.py
├── reader.py
├── serializer.py
├── statistics.py
├── pipeline.py
└── dataset.py
```

Script:

```text
scripts/build_graphs.py
```

Đã làm:

- Hỗ trợ 3 graph variants bắt buộc.
- Thêm inverse edges.
- Validate compact sample và ProgramGraph.
- Ghi graph shards JSONL.
- Ghi graph construction summary.
- Có lazy dataset để training không cần materialize full graph.

### Slide 13. 3.4. Workflow Colab/Drive

Notebook:

```text
notebooks/build_graphs_colab.ipynb
```

Thiết kế:

- Source code clone từ GitHub vào `/content`.
- Dataset preprocessing lưu trên Google Drive.
- Output graph shard/report lưu trên Google Drive.
- Nếu reset runtime, không mất dữ liệu Drive.

Drive layout:

```text
variable_misuse_graph_build/
├── dataset/processed/great_colab/
├── dataset/processed/great_colab_balanced_300000/
└── dataset/graphs/great_colab_balanced_300000/
```

Lý do:

- Không upload source code thủ công.
- Tránh upload lại 16GB dữ liệu preprocessing.
- Có thể tái chạy training/evaluation trên Colab.

### Slide 14. 3.5. Balanced subset methodology

Vấn đề:

- Full dataset có 2,884,323 sample.
- Build graph full rất lâu và output lớn.

Giải pháp:

- Tạo balanced subset mặc định **300,000 sample**.
- Giữ tỉ lệ `train/dev/eval` theo dataset gốc.
- Trong từng split cân bằng `bug/no_bug`.
- Dùng reservoir sampling với seed cố định.

Ưu điểm:

- Phù hợp giới hạn Colab.
- Có thể tái lập.
- Vẫn đủ để so sánh 3 graph variants.

Ghi chú báo cáo:

- Khi trình bày kết quả trên subset, phải ghi rõ không phải full benchmark.

## 4. Kết quả thực nghiệm

### Slide 15. Kết quả preprocessing

Số liệu đã có:

| Hạng mục | Giá trị |
| --- | ---: |
| Sample đọc | 2,952,990 |
| Sample ghi sau lọc | 2,884,323 |
| Bug sample | 1,434,367 |
| No-bug sample | 1,449,956 |
| Bị loại do quá nhiều token | 53,068 |
| Bị loại do bug sample thiếu repair target | 15,598 |
| Repair target được bổ sung vào candidates | 12,666 |

Edge group:

| Edge group | Số lượng |
| --- | ---: |
| syntax | 79,930,821 |
| next_token | 554,258,762 |
| data_flow | 81,309,475 |
| lexical | 36,833,980 |
| semantic | 130,614 |
| control_flow | 25,268,818 |

### Slide 16. Kết quả kiểm tra graph construction

Dry-run đã chạy trên `ast_next_token_data_flow`, 1,000 sample/split:

| Hạng mục | Giá trị |
| --- | ---: |
| Read | 3,000 |
| Written | 3,000 |
| Bug | 1,360 |
| No-bug | 1,640 |

Edge type counts:

| Edge type | Số lượng |
| --- | ---: |
| syntax | 81,563 |
| syntax_reverse | 81,563 |
| next_token | 567,743 |
| next_token_reverse | 567,743 |
| data_flow | 81,050 |
| data_flow_reverse | 81,050 |
| lexical | 37,252 |
| lexical_reverse | 37,252 |

Ý nghĩa:

- Graph builder đọc được compact JSONL.
- Graph giữ đủ syntax, NextToken, Data Flow, lexical và inverse edges.
- Đây là kết quả kiểm tra pipeline, chưa phải kết quả model.

### Slide 17. Kết quả balanced subset

Điền sau khi chạy notebook:

| Split | Tổng sample | Bug | No-bug |
| --- | ---: | ---: | ---: |
| Train | TBD | TBD | TBD |
| Dev | TBD | TBD | TBD |
| Eval | TBD | TBD | TBD |
| Tổng | 300,000 | ~150,000 | ~150,000 |

Ghi chú:

- Notebook lưu summary tại:

```text
dataset/processed/great_colab_balanced_300000/preprocessing_summary.json
```

- Sau khi chạy xong, cập nhật bảng này bằng số thật.

### Slide 18. Bảng kết quả mô hình

Điền sau khi training/evaluation:

| Model / Graph Variant | Localization Accuracy | Repair Accuracy | Ghi chú |
| --- | ---: | ---: | --- |
| GGNN - `ast_only` | TBD | TBD | Baseline AST-only |
| GGNN - `ast_next_token` | TBD | TBD | Thêm NextToken |
| GGNN - `ast_next_token_data_flow` | TBD | TBD | Thêm Data Flow |

Cách diễn giải mong muốn:

- Nếu `ast_next_token_data_flow` tốt hơn `ast_only`, có thể kết luận Data Flow giúp bắt long-range dependencies trên subset.
- Nếu chưa train xong, trình bày đây là thiết kế đánh giá và không công bố số giả.

### Slide 19. Thảo luận kết quả và giới hạn

Nội dung:

- Preprocessing và graph construction đã chạy được trên dữ liệu lớn.
- Đã tách pipeline để chạy được local và Colab.
- Full dataset rất lớn, nên dùng balanced subset cho thí nghiệm ban đầu.
- Compact GREAT output hiện là token-level graph, không có syntax node metadata đầy đủ.
- Kết quả trên synthetic/random bug không nên tuyên bố đại diện hoàn toàn cho bug thật.

Hướng tiếp theo:

- Training GGNN.
- Evaluation bằng Localization Accuracy và Repair Accuracy.
- Visualization graph nhỏ và prediction.

## 5. Demo

### Slide 20. Demo đề xuất

Demo để sau, nhưng kịch bản nên gồm:

1. Mở `notebooks/build_graphs_colab.ipynb`.
2. Cho thấy Drive đã có preprocessing dataset.
3. Chạy hoặc trình chiếu:
   - kiểm tra preprocessing summary;
   - tạo balanced subset;
   - dry-run graph construction;
   - build 3 graph variants.
4. Mở một `graph_construction_summary.json`.
5. Nếu có visualization/model:
   - hiển thị graph nhỏ;
   - đánh dấu ground-truth bug node;
   - hiển thị predicted bug node và repair candidate.

Ghi chú:

- Demo hiện tại nên tập trung vào pipeline dữ liệu và graph construction.
- Demo model prediction chỉ làm sau khi training/evaluation hoàn tất.

## Tài liệu tham khảo đưa vào slide cuối

- **Learning to Represent Programs with Graphs**.
- **Global Relational Models of Source Code**.
- **Self-Supervised Bug Detection and Repair**.
- **Deep Learning for Source Code Modeling and Generation: Models, Applications and Challenges**.
- `docs/references/instruction.md`.
- `docs/references/gnn_documentation.md`.
- `docs/references/general_paper.md`.

## Checklist cập nhật trước ngày báo cáo

- Cập nhật số thật của balanced subset.
- Cập nhật graph construction summary cho cả 3 variants.
- Nếu train xong, cập nhật Localization Accuracy và Repair Accuracy.
- Chuẩn bị một hình graph nhỏ để minh họa.
- Chuẩn bị demo notebook chạy ổn trên Colab.

