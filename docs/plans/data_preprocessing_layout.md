# Layout module tiền xử lý dữ liệu GREAT

## 1. Mục tiêu

Module tiền xử lý dữ liệu chuyển GREAT raw JSONL thành schema nội bộ ổn định để phục vụ bước tiếp theo: **xây dựng graph variants** và huấn luyện mô hình **GGNN/GNN** cho bài toán **Variable Misuse Localization and Repair**.

Đầu vào chính:

```text
dataset/raw/great/
dataset/interim/great_sample_subset/
```

Đầu ra chính:

```text
dataset/processed/great_subset/
dataset/processed/great/
```

## 2. Nguyên tắc thiết kế

- Giữ nguyên raw dataset trong `dataset/raw/great/`.
- Xử lý theo streaming JSONL để phù hợp dataset gần 3 triệu sample.
- Không học statistics từ `dev` hoặc `eval`.
- Mọi sample sau preprocessing phải có label rõ cho localization và repair.
- Edge được chuẩn hóa theo nhóm để tạo được các graph variant:
  - `syntactic_only`;
  - `syntactic_next_token`;
  - `syntactic_next_token_data_flow`;
  - `full_available`.
- Tài liệu, comment và docstring dùng tiếng Việt có dấu.
- Tên biến, hàm, class, file dùng tiếng Anh.

## 3. Cấu trúc module

```text
src/variable_misuse_gnn/data/preprocessing/
├── __init__.py
├── config.py
├── edge_types.py
├── normalizer.py
├── pipeline.py
├── reader.py
├── schema.py
└── validation.py
```

Vai trò:

| File | Vai trò |
| --- | --- |
| `config.py` | Cấu hình lọc, cân bằng, ngưỡng token/edge và output. |
| `edge_types.py` | Mapping edge GREAT sang nhóm `syntax`, `next_token`, `data_flow`, `lexical`, `semantic`, `control_flow`. |
| `reader.py` | Đọc JSONL streaming từ full raw dataset hoặc sample subset. |
| `validation.py` | Kiểm tra schema, index label, edge endpoint và repair target. |
| `normalizer.py` | Chuẩn hóa sample raw thành `VariableMisuseExample`. |
| `schema.py` | Dataclass cho `Provenance`, `NormalizedEdge`, `VariableMisuseExample`. |
| `pipeline.py` | Điều phối validate, clean, filter, balance và ghi JSONL. |

Script chạy:

```text
scripts/preprocess_great_data.py
```

## 4. Công tác tiền xử lý

### 4.1. Làm sạch và kiểm tra lỗi dữ liệu

Các sample bị loại nếu:

- JSON decode lỗi;
- thiếu field bắt buộc;
- `source_tokens` rỗng hoặc sai kiểu;
- `has_bug` sai kiểu;
- `error_location` nằm ngoài token range;
- `repair_targets` nằm ngoài token range;
- `repair_candidates` dạng integer nằm ngoài token range;
- edge endpoint nằm ngoài token range;
- bug sample không có `repair_targets`;
- repair target không thuộc candidate set;
- sample vượt ngưỡng `max_tokens`;
- sample vượt ngưỡng `max_edges`;
- candidate set quá nhỏ.

### 4.2. Xử lý trường dữ liệu

Các trường raw được chuẩn hóa:

| Raw field | Field sau preprocessing |
| --- | --- |
| `source_tokens` | `source_tokens`, `token_count`, `token_hash` |
| `has_bug` | `has_bug` |
| `error_location` | `error_location`, `localization_target` |
| `repair_candidates` | `repair_candidates`, `candidate_token_texts` |
| `repair_targets` | `repair_targets` |
| `edges` | `normalized_edges`, `graph_variant_edges` |
| `provenances` | `provenance` |

Với no-bug sample, `localization_target = null` và `repair_targets = []`.

### 4.3. Chuẩn hóa edge

GREAT edge type được gom nhóm:

| Nhóm | Raw edge types |
| --- | --- |
| `syntax` | `enum_FIELD`, `enum_SYNTAX` |
| `next_token` | `enum_NEXT_SYNTAX`, `LOCAL_NEXT_TOKEN` |
| `data_flow` | `enum_LAST_READ`, `enum_LAST_WRITE`, `enum_COMPUTED_FROM` |
| `lexical` | `enum_LAST_LEXICAL_USE` |
| `semantic` | `enum_FORMAL_ARG_NAME` |
| `control_flow` | `enum_CFG_NEXT`, `enum_RETURNS_TO`, `enum_CALLS` |

Module có thể thêm `LOCAL_NEXT_TOKEN` giữa token liền kề để bảo đảm có luồng tuyến tính NextToken đúng yêu cầu đồ án.

### 4.4. Cân bằng dữ liệu

GREAT đã cân bằng bug/no-bug theo split. Module vẫn hỗ trợ:

- giữ cân bằng hiện có;
- giới hạn `max_samples_per_class` cho demo hoặc thử nghiệm nhỏ;
- tạo subset cân bằng bug/no-bug.

### 4.5. Xử lý duplicate và leakage

Module có tùy chọn `drop_duplicate_tokens_within_split`.

Không mặc định xóa duplicate giữa các split ở bước này vì:

- audit cho thấy không có `filepath overlap`;
- có `token-hash overlap`, nhưng cần phân tích sâu vì có thể là code sinh tự động hoặc hàm wrapper giống nhau từ file khác nhau.

Quy tắc hiện tại: ghi nhận token hash để bước sau phân tích leakage, chưa xóa mặc định.

## 5. Output cho graph construction

Mặc định pipeline ghi **compact output** để tránh phình dung lượng khi xử lý full GREAT dataset. Mỗi dòng output là một JSON object:

```json
{
  "id": "...",
  "split": "train",
  "tokens": ["#NEWLINE#", "def ..."],
  "has_bug": true,
  "loc": 52,
  "candidates": [2, 9, 52],
  "targets": [9],
  "edges": [[0, 1, 1, -1]],
  "provenance": {
    "license": "mit",
    "filepath": "repo/file.py"
  }
}
```

Edge compact có dạng:

```text
[source, target, edge_group_id, raw_type_id]
```

Trong đó `edge_group_id` tra theo:

| ID | Nhóm |
| ---: | --- |
| 0 | `syntax` |
| 1 | `next_token` |
| 2 | `data_flow` |
| 3 | `lexical` |
| 4 | `semantic` |
| 5 | `control_flow` |

Các graph variant được tạo ở bước graph construction bằng cách lọc theo `edge_group_id`, thay vì lưu sẵn danh sách index edge trong JSONL. Cách này giảm mạnh dung lượng output full dataset.

Nếu cần debug chi tiết, có thể chạy:

```bash
--output-format full
```

nhưng không khuyến nghị cho toàn bộ GREAT vì file sẽ rất lớn.

## 6. Cách chạy

Chạy trên subset đã audit:

```bash
PYTHONPATH=src python3 scripts/preprocess_great_data.py \
  --input-root dataset/interim/great_sample_subset \
  --output-root dataset/processed/great_subset \
  --report-path dataset/processed/great_subset/preprocessing_summary.json
```

Chạy trên full raw dataset:

```bash
PYTHONPATH=src python3 scripts/preprocess_great_data.py \
  --input-root dataset/raw/great \
  --output-root dataset/processed/great \
  --report-path dataset/processed/great/preprocessing_summary.json \
  --output-format compact
```

Nếu cần demo nhỏ cân bằng:

```bash
PYTHONPATH=src python3 scripts/preprocess_great_data.py \
  --input-root dataset/raw/great \
  --output-root dataset/processed/great_demo \
  --report-path dataset/processed/great_demo/preprocessing_summary.json \
  --max-samples-per-class 1000 \
  --output-format compact
```
