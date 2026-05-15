# Layout module xây dựng đồ thị GREAT

## 1. Mục tiêu

Module xây dựng đồ thị chuyển dữ liệu đã tiền xử lý trong:

```text
dataset/processed/great_colab/
├── train.jsonl
├── dev.jsonl
├── eval.jsonl
└── preprocessing_summary.json
```

thành các **Program Graph** phục vụ mô hình **GGNN/GNN** cho bài toán **Variable Misuse Localization and Repair**.

Mục tiêu trực tiếp theo `instruction.md`:

- xây dựng graph từ biểu diễn AST/syntax, NextToken và Data Flow;
- tạo được các graph variant để so sánh;
- bảo toàn nhãn localization và repair;
- chuẩn bị format thuận tiện cho training, evaluation và visualization;
- không biến bài toán thành graph mining tổng quát.

Nguyên tắc bắt buộc của layout này:

- `instruction.md` quyết định phạm vi và tiêu chí đánh giá;
- `gnn_documentation.md` quyết định cách giải thích Program Graph, directed heterogeneous graph, inverse edge, localization và repair;
- `general_paper.md` chỉ dùng để đặt bối cảnh paper và Related Work;
- module này không được tạo số liệu đánh giá giả và không tuyên bố hiệu quả model khi chưa train/evaluate;
- mọi graph variant phải phục vụ so sánh AST-only với graph có Data Flow.

## 2. Cơ sở thiết kế từ tài liệu

### 2.1. Theo `instruction.md`

Phần Graph Construction yêu cầu các loại cạnh quan trọng:

- `Child` / `Parent`: cạnh trong AST;
- `NextToken`: luồng tuyến tính của code;
- `LastRead` / `LastWrite`: luồng dữ liệu của biến;
- `ComputedFrom`: quan hệ giá trị được tính từ biến khác.

Phần đánh giá yêu cầu so sánh graph AST-only với graph có thêm Data Flow, và báo cáo:

- `Localization Accuracy`;
- `Repair Accuracy`.

### 2.2. Theo `gnn_documentation.md`

Program graph nên được xem là **heterogeneous directed graph**. Với GNN/GGNN, mỗi edge có relation type riêng và có thể thêm inverse edge để message passing truyền thông tin hai chiều.

Tài liệu cũng nhấn mạnh:

- `Token Node` biểu diễn chuỗi token của source code;
- `NextToken` nối token node theo thứ tự tuyến tính;
- syntax edge cung cấp ngữ cảnh AST;
- data-flow edge giúp mô hình bắt **long-range dependencies**;
- localization là pointer trên các variable usage token;
- repair là pointer trên candidate variable/symbol trong scope.

### 2.3. Theo `general_paper.md`

Khi viết báo cáo hoặc giải thích kết quả, dùng đúng tên paper:

- **Learning to Represent Programs with Graphs** cho nền tảng GGNN và Variable Misuse;
- **Global Relational Models of Source Code** cho GREAT;
- **Self-Supervised Bug Detection and Repair** cho BugLab.

Không dùng layout này để gọi GREAT là "Graph-based Representation Attentional Network" như tên chính thức. Nếu cần nhắc, chỉ giải thích đây là cách ghi trong đề bài, còn paper chính thức là **Global Relational Models of Source Code**.

## 3. Đặc điểm dữ liệu hiện tại

Output preprocessing hiện là compact JSONL. Mỗi dòng có dạng:

```json
{
  "id": "...",
  "split": "train",
  "tokens": ["#NEWLINE#", "def __init__(", "self", "..."],
  "has_bug": true,
  "loc": 33,
  "candidates": [2, 4, 6, 8],
  "targets": [8],
  "edges": [[1, 3, 0, 7]],
  "provenance": {
    "license": "mit",
    "filepath": "repo/file.py"
  }
}
```

Trong đó:

```text
edge = [source, target, edge_group_id, raw_type_id]
```

Mapping `edge_group_id` đã được chuẩn hóa ở preprocessing:

| ID | Nhóm edge | Ý nghĩa trong layout graph |
| ---: | --- | --- |
| 0 | `syntax` | AST/syntax relation, dùng cho `ast_only` |
| 1 | `next_token` | NextToken tuyến tính hoặc GREAT next syntax |
| 2 | `data_flow` | LastRead, LastWrite, ComputedFrom |
| 3 | `lexical` | Last lexical use, dùng như LastUse khi so sánh Data Flow |
| 4 | `semantic` | Formal argument name, dùng cho variant mở rộng |
| 5 | `control_flow` | CFG, ReturnsTo, Calls, dùng cho variant mở rộng |

Mapping từ dữ liệu hiện tại sang thuật ngữ trong đề:

| Thuật ngữ trong đề | Dữ liệu hiện tại | Cách dùng trong graph construction |
| --- | --- | --- |
| `Child` | `syntax` forward edge | Giữ edge gốc có `edge_group_id = 0`. |
| `Parent` | inverse của `syntax` | Tạo khi `add_inverse_edges = true`. |
| `NextToken` | `next_token` | Giữ edge có `edge_group_id = 1`. |
| `LastRead` | `data_flow` | Giữ trong variant có Data Flow. |
| `LastWrite` | `data_flow` | Giữ trong variant có Data Flow. |
| `ComputedFrom` | `data_flow` | Giữ trong variant có Data Flow. |
| `LastUse` | `lexical` | Giữ kèm Data Flow vì GREAT có `enum_LAST_LEXICAL_USE`. |

Vì compact output chỉ giữ `edge_group_id` và `raw_type_id`, tên raw edge cụ thể không còn nằm trong từng dòng graph. Do đó bước graph construction dùng `edge_group_id` làm relation chính cho GGNN baseline, còn `raw_type_id` chỉ là metadata để thống kê hoặc debug.

Dataset đã giải nén:

| Split | Số sample |
| --- | ---: |
| `train` | 1,756,340 |
| `dev` | 181,478 |
| `eval` | 946,505 |
| Tổng | 2,884,323 |

Vì dữ liệu đã có edge compact, module này **không parse lại source code bằng `ast`**. Việc parse AST lại từ token là không ổn định và không cần thiết cho dữ liệu GREAT hiện tại. Graph construction sẽ dùng trực tiếp syntax edge do GREAT/preprocessing cung cấp.

## 4. Graph variant bắt buộc

Module phải hỗ trợ tối thiểu ba biến thể theo yêu cầu đồ án:

| Variant | Edge group dùng | Mục đích |
| --- | --- | --- |
| `ast_only` | `{syntax}` | Baseline chỉ dùng cấu trúc AST/syntax. |
| `ast_next_token` | `{syntax, next_token}` | Baseline có thêm luồng token tuyến tính. |
| `ast_next_token_data_flow` | `{syntax, next_token, data_flow, lexical}` | Model chính để kiểm tra tác dụng của Data Flow và LastUse-like edge. |

Variant mở rộng:

| Variant | Edge group dùng | Mục đích |
| --- | --- | --- |
| `full_available` | `{syntax, next_token, data_flow, lexical, semantic, control_flow}` | Thí nghiệm phụ nếu còn thời gian |

Ghi chú: `lexical` được đưa vào `ast_next_token_data_flow` vì GREAT có `enum_LAST_LEXICAL_USE`, gần với LastUse trong yêu cầu đồ án. Khi báo cáo, cần nói rõ Data Flow chính gồm `LastRead`, `LastWrite`, `ComputedFrom`, và phần lexical là quan hệ LastUse-like có sẵn trong GREAT.

Không dùng tên variant `syntactic_only` trong module mới, dù preprocessing từng dùng tên này trong nội bộ. Tên public của bước graph construction phải bám đề và dễ đưa vào bảng kết quả:

```text
Model / Graph Variant | Localization Accuracy | Repair Accuracy
```

## 5. Schema graph nội bộ

Mỗi sample được chuyển thành một `ProgramGraph` có cấu trúc logic:

```text
ProgramGraph
├── graph_id: str
├── split: train | dev | eval
├── graph_variant: str
├── num_nodes: int
├── node_tokens: list[str]
├── node_types: list[str]
├── candidate_mask: list[bool]
├── edge_index: list[list[int]]
├── edge_types: list[int]
├── edge_type_names: list[str]
├── raw_edge_types: list[int]
├── has_bug: bool
├── localization_target: int | None
├── repair_candidates: list[int]
├── repair_targets: list[int]
└── provenance: dict
```

### 5.1. Node

Với dữ liệu hiện tại, node mặc định là token node:

| Field | Cách lấy |
| --- | --- |
| `node_id` | index trong `tokens` |
| `node_type` | `"token"` |
| `token_text` | `tokens[node_id]` |
| `syntax_type` | `null` vì compact GREAT không lưu syntax node type riêng |
| `symbol_name` | token text nếu node nằm trong `candidates`, ngược lại `null` |
| `source_line` | chưa có trong compact output |
| `source_column` | chưa có trong compact output |
| `scope_id` | chưa có trong compact output |

Không tự tạo `Syntax Node` hoặc `Symbol Node` giả nếu dữ liệu không có metadata. Làm vậy có thể tạo diễn giải sai trong báo cáo. Thay vào đó, báo cáo rõ phiên bản hiện tại là **token-level program graph with typed edges**.

Để vẫn bám yêu cầu node metadata của project, module nên cung cấp hàm tạo metadata lazy:

```text
NodeMetadata
├── node_id: int
├── node_type: "token"
├── token_text: str
├── syntax_type: None
├── symbol_name: str | None
├── source_line: None
├── source_column: None
└── scope_id: None
```

Metadata này dùng cho debug, visualization và report. Khi training full dataset, không bắt buộc serialize metadata đầy đủ để tránh phình dung lượng.

### 5.2. Edge

Mỗi edge được lọc theo variant, sau đó chuẩn hóa thành:

```text
GraphEdge
├── source: int
├── target: int
├── edge_type: int
├── edge_type_name: str
├── edge_group_id: int
└── raw_type_id: int
```

Mặc định nên thêm inverse edge:

```text
syntax -> syntax_reverse
next_token -> next_token_reverse
data_flow -> data_flow_reverse
lexical -> lexical_reverse
```

Lý do: `gnn_documentation.md` mô tả program graph là directed graph và GNN có thể dùng `E ∪ E_inv` để message passing truyền thông tin theo cả hai chiều. Đây cũng tương ứng với yêu cầu `Child/Parent` trong `instruction.md`.

Self-loop là tùy chọn cho model layer. Không nên thêm self-loop vào file graph serialized nếu model implementation có thể tự thêm.

### 5.3. Label

Localization:

- nếu `has_bug = true`, `localization_target = loc`;
- nếu `has_bug = false`, dùng `localization_target = null`;
- khi training pointer network, thêm một class đặc biệt `NO_BUG`.

Repair:

- `repair_candidates` lấy từ `candidates`;
- `repair_targets` lấy từ `targets`;
- với no-bug sample, `repair_targets = []`;
- repair accuracy chỉ tính trên bug sample, hoặc báo cáo rõ nếu dùng quy ước khác.

Candidate mask:

- `candidate_mask[node_id] = true` nếu `node_id` nằm trong `candidates`;
- với bug sample, `loc` không nhất thiết phải nằm trong `candidates`, nên localization target phải lưu riêng;
- repair head chỉ chọn trong `repair_candidates`;
- localization head nên dùng mask riêng ở module training nếu muốn giới hạn vào variable usage token. Graph construction không tự suy luận scope mới ngoài dữ liệu đã có.

## 6. Cấu trúc module đề xuất

```text
src/variable_misuse_gnn/graph/
├── __init__.py
├── config.py
├── schema.py
├── variants.py
├── reader.py
├── builder.py
├── validator.py
├── serializer.py
├── statistics.py
└── dataset.py
```

Vai trò:

| File | Vai trò |
| --- | --- |
| `config.py` | Cấu hình input/output, variant, inverse edge, giới hạn sample và shard size. |
| `schema.py` | Dataclass `PreprocessedExample`, `GraphEdge`, `ProgramGraph`, `GraphConstructionReport`. |
| `variants.py` | Định nghĩa `GraphVariant`, mapping edge group, mapping edge type forward/reverse. |
| `reader.py` | Đọc streaming JSONL từ `dataset/processed/great_colab`. |
| `builder.py` | Chuyển một sample compact thành `ProgramGraph`. |
| `validator.py` | Kiểm tra endpoint, candidate, target, duplicate edge và label hợp lệ. |
| `serializer.py` | Ghi/đọc graph shards JSONL hoặc JSONL.GZ. |
| `statistics.py` | Thống kê số node, edge, class balance, edge type theo variant. |
| `dataset.py` | Lazy dataset để training có thể build graph on-the-fly mà không nhân bản dữ liệu lớn. |

Script CLI:

```text
scripts/build_graphs.py
```

Output report của script:

```text
dataset/graphs/great_colab/<variant>/graph_construction_summary.json
```

Test:

```text
tests/test_graph_variants.py
tests/test_graph_builder.py
tests/test_graph_validator.py
tests/test_graph_serializer.py
```

## 7. Cấu hình đề xuất

Dataclass chính:

```python
@dataclass(frozen=True)
class GraphConstructionConfig:
    """Cấu hình xây dựng Program Graph từ dữ liệu GREAT compact."""

    input_root: Path = Path("dataset/processed/great_colab")
    output_root: Path = Path("dataset/graphs/great_colab")
    graph_variant: str = "ast_next_token_data_flow"
    splits: tuple[str, ...] = ("train", "dev", "eval")
    add_inverse_edges: bool = True
    add_self_loops: bool = False
    max_samples_per_split: int | None = None
    shard_size: int = 50000
    output_format: str = "jsonl"
    dry_run: bool = False
```

Không hard-code variant trong code chính. CLI phải cho phép chọn:

```bash
--graph-variant ast_only
--graph-variant ast_next_token
--graph-variant ast_next_token_data_flow
```

Không thêm dependency mới trong layout này. Khi triển khai adapter cho PyTorch Geometric hoặc DGL, phải kiểm tra phiên bản Python, pip, PyTorch và thư viện graph trước khi thêm vào dependency.

## 8. Output layout

Do dữ liệu gốc đã 16 GB, không nên mặc định ghi đủ cả 3 graph variant full dataset trên máy local. Layout nên có hai chế độ.

### 8.1. Chế độ lazy, khuyến nghị cho training

Không ghi graph full ra đĩa. Dataset đọc từng dòng JSONL rồi gọi `build_program_graph(...)` theo variant khi training.

Ưu điểm:

- không nhân bản dữ liệu 16 GB thành nhiều bản;
- đổi variant nhanh;
- phù hợp Colab và laptop.

### 8.2. Chế độ materialized, dùng cho demo hoặc Colab

Ghi graph đã lọc theo variant ra:

```text
dataset/graphs/great_colab/
├── ast_only/
│   ├── train/
│   │   ├── shard_00000.jsonl
│   │   └── ...
│   ├── dev/
│   └── eval/
├── ast_next_token/
└── ast_next_token_data_flow/
```

Mỗi dòng graph JSONL:

```json
{
  "graph_id": "...",
  "split": "train",
  "graph_variant": "ast_next_token_data_flow",
  "num_nodes": 34,
  "node_tokens": ["#NEWLINE#", "def __init__(", "..."],
  "node_types": ["token", "token", "..."],
  "candidate_mask": [false, false, true],
  "edge_index": [[1, 3], [3, 1]],
  "edge_types": [0, 1],
  "edge_type_names": ["syntax", "syntax_reverse"],
  "raw_edge_types": [7, 7],
  "has_bug": true,
  "localization_target": 33,
  "repair_candidates": [2, 4, 6, 8],
  "repair_targets": [8],
  "provenance": {"license": "mit", "filepath": "..."}
}
```

Với full dataset, chỉ materialize khi thật sự cần benchmark hoặc khi chạy trên Colab/ổ đủ dung lượng.

## 9. Edge type vocabulary cho GGNN

Nếu `add_inverse_edges = true`, edge type nên được tách riêng forward và reverse:

| Base group | Forward | Reverse |
| --- | ---: | ---: |
| `syntax` | 0 | 1 |
| `next_token` | 2 | 3 |
| `data_flow` | 4 | 5 |
| `lexical` | 6 | 7 |
| `semantic` | 8 | 9 |
| `control_flow` | 10 | 11 |

Với từng variant, chỉ dùng subset tương ứng. Ví dụ:

- `ast_only`: `{0, 1}`;
- `ast_next_token`: `{0, 1, 2, 3}`;
- `ast_next_token_data_flow`: `{0, 1, 2, 3, 4, 5, 6, 7}`.

Không dùng `raw_type_id` làm edge type chính cho GGNN baseline, vì số raw type có thể làm mô hình và report khó giải thích. `raw_type_id` nên được giữ làm metadata để debug và thống kê.

## 10. Pipeline đề xuất

```text
1. read_preprocessed_examples
2. validate_preprocessed_example
3. select_graph_variant_edges
4. map_edge_group_to_relation_type
5. add_inverse_edges
6. build_candidate_mask
7. build_program_graph
8. validate_program_graph
9. update_graph_statistics
10. write_graph_shard hoặc yield lazy graph
11. write_graph_construction_report
```

Report nên lưu ở:

```text
dataset/graphs/great_colab/<variant>/graph_construction_summary.json
```

Report tối thiểu:

- input root;
- graph variant;
- split counts;
- graph count;
- node count min/mean/max;
- edge count min/mean/max trước và sau inverse edge;
- số sample bug/no-bug;
- số sample bị drop và lý do;
- edge group counts;
- relation type counts sau khi thêm inverse edge;
- số lượng candidate trung bình;
- số sample có bug và no-bug;
- config đã dùng.

Luồng này phải chạy được độc lập với training. Nếu chỉ cần kiểm tra layout, dùng `--dry-run` để thống kê mà không ghi graph lớn ra đĩa.

## 11. CLI đề xuất

Build demo nhỏ:

```bash
PYTHONPATH=src python3 scripts/build_graphs.py \
  --input-root dataset/processed/great_colab \
  --output-root dataset/graphs/great_colab_demo \
  --graph-variant ast_next_token_data_flow \
  --max-samples-per-split 1000
```

Build full một variant:

```bash
PYTHONPATH=src python3 scripts/build_graphs.py \
  --input-root dataset/processed/great_colab \
  --output-root dataset/graphs/great_colab \
  --graph-variant ast_next_token_data_flow
```

Chỉ thống kê, không ghi graph:

```bash
PYTHONPATH=src python3 scripts/build_graphs.py \
  --input-root dataset/processed/great_colab \
  --graph-variant ast_only \
  --dry-run
```

## 12. Kiểm thử bắt buộc

Test nên dùng sample nhỏ tự tạo, không phụ thuộc full dataset.

Tối thiểu kiểm tra:

- `ast_only` chỉ giữ edge group `syntax`;
- `ast_next_token` giữ `syntax` và `next_token`;
- `ast_next_token_data_flow` giữ `syntax`, `next_token`, `data_flow`, `lexical`;
- inverse edge được thêm đúng số lượng và đúng chiều;
- relation type forward/reverse ổn định theo bảng edge vocabulary;
- endpoint edge luôn nằm trong `[0, num_nodes)`;
- `loc` của bug sample nằm trong node range;
- `targets` là subset hợp lệ của node range;
- `candidate_mask` đúng với `candidates`;
- no-bug sample có `localization_target = None` và `repair_targets = []`;
- serializer đọc lại graph không mất label và edge type.

Chạy test:

```bash
pytest tests/test_graph_variants.py tests/test_graph_builder.py
```

Nếu chưa có `pytest` trong môi trường, cần kiểm tra dependency và cập nhật file dependency trước khi dùng.

## 13. Quyết định không làm ở module này

Module này không phụ trách:

- training GGNN;
- tạo vocabulary/token embedding cuối cùng;
- tính `Localization Accuracy` hoặc `Repair Accuracy`;
- visualization graph;
- parse lại raw source code;
- tải lại GREAT dataset.

Không dùng module này để:

- tạo bug synthetic mới;
- cân bằng lại bug/no-bug;
- xóa duplicate;
- suy luận scope hoặc symbol table mới;
- convert sang PyTorch Geometric/DGL nếu chưa kiểm tra dependency.

Các phần đó nên nằm ở module riêng:

```text
src/variable_misuse_gnn/models/
src/variable_misuse_gnn/training/
src/variable_misuse_gnn/evaluation/
src/variable_misuse_gnn/visualization/
```

## 14. Hướng triển khai tiếp theo

Thứ tự triển khai hợp lý:

1. tạo `variants.py` và test mapping variant;
2. tạo `schema.py` cho `ProgramGraph`;
3. tạo `builder.py` build graph từ một dict compact;
4. tạo `validator.py` để chặn graph lỗi;
5. tạo `serializer.py` và test round-trip;
6. tạo `scripts/build_graphs.py` cho demo subset;
7. chạy demo 1000 sample/split để kiểm tra statistics;
8. sau đó mới quyết định materialize full variant hay dùng lazy dataset cho training.

## 15. Definition of Done cho layout graph construction

Một implementation theo layout này được xem là đạt khi:

- đọc được `dataset/processed/great_colab/train.jsonl`, `dev.jsonl`, `eval.jsonl`;
- tạo được đủ ba variant `ast_only`, `ast_next_token`, `ast_next_token_data_flow`;
- thêm inverse edge đúng quy ước để có Child/Parent và message passing hai chiều;
- bảo toàn `has_bug`, `loc`, `candidates`, `targets` cho localization và repair;
- có validation chặn edge endpoint, label và candidate index lỗi;
- có report thống kê riêng cho từng variant;
- có test cho variant filtering, inverse edge, label và serializer;
- không ghi đè dữ liệu gốc trong `dataset/processed/great_colab`;
- không yêu cầu GPU và không phụ thuộc training để chạy graph construction;
- output có thể dùng tiếp cho bảng so sánh `Localization Accuracy` và `Repair Accuracy`.
