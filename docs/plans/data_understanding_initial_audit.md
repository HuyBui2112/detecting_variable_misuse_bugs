# Công việc 1: Data Understanding / Initial Dataset Audit

## 1. Mục tiêu

Công việc này nhằm hiểu dataset GREAT trước khi làm preprocessing riêng cho bài toán **Variable Misuse Localization and Repair**.

Ở bước này chưa xây graph mới, chưa train model và chưa thiết kế chi tiết các bước preprocessing sau. Mục tiêu là trả lời rõ:

- dataset là gì, lấy từ đâu, phiên bản nào;
- dữ liệu gốc được lưu ở đâu và có giữ bất biến không;
- dataset có README, LICENSE, metadata và label description như thế nào;
- cấu trúc thư mục, loại file, split, schema sample ra sao;
- quy mô dataset có phù hợp máy hiện tại không;
- dữ liệu có lỗi ban đầu nào không;
- có nguy cơ data leakage theo split không;
- cần tạo manifest và subset thử nghiệm như thế nào.

## 2. Dataset được audit

Dataset sử dụng ở bước này là **GREAT Variable-Misuse dataset**.

Thông tin chính:

- Nguồn dataset: https://github.com/google-research-datasets/great
- Paper đi kèm: **Global Relational Models of Source Code**
- Code tham khảo: https://github.com/VHellendoorn/ICLR20-Great
- Dataset gốc: **ETHPy150Open**
- Ngôn ngữ: Python
- Task: **Variable Misuse Localization and Repair**
- Định dạng: sharded JSONL text files
- Split chính thức: `train`, `dev`, `eval`

Theo `docs/references/instruction.md`, dataset từ paper `"GreatEL"` hoặc `"Varsity"` được ưu tiên để demo tốt. Dataset GREAT là nguồn công khai chính thức đã xác minh được cho paper GREAT.

## 3. Vị trí lưu dữ liệu

Theo yêu cầu hiện tại, dữ liệu được lưu trong thư mục:

```text
dataset/
```

Quy ước nội bộ:

```text
dataset/
├── raw/
│   └── great/
│       ├── README.md
│       ├── LICENSE
│       ├── train/
│       ├── dev/
│       └── eval/
├── interim/
│   ├── great_remote_shard_manifest.csv
│   ├── great_sample_manifest.csv
│   └── great_sample_subset/
└── audit/
    └── great_dataset_audit_summary.json
```

Quy tắc:

- Không chỉnh sửa file trong `dataset/raw/great/`.
- Không format lại JSONL raw.
- Không đổi token, label hoặc edge trong raw.
- Không ghi đè shard đã tải nếu không có lý do.
- Mọi file audit, manifest và subset ghi sang `dataset/interim/` hoặc `dataset/audit/`.

## 4. Kế hoạch tải dataset trong lần chạy hiện tại

Kết quả kiểm tra môi trường mới cho thấy ổ `E:` hiện còn khoảng 33 GB trống.

Trong khi đó, GREAT dataset remote có dung lượng xấp xỉ:

- `train`: 14.23 GB;
- `dev`: 1.45 GB;
- `eval`: 7.62 GB;
- tổng: 23.31 GB.

Với 33 GB trống, có thể tải toàn bộ raw dataset vào:

```text
dataset/raw/great/
```

Bước audit hiện tại sẽ:

- tải README và LICENSE;
- tạo manifest remote cho toàn bộ shard dataset;
- tải toàn bộ shard của `train`, `dev`, `eval`;
- audit toàn bộ sample trong các shard đã tải;
- tạo manifest sample cho toàn bộ dataset local;
- tạo subset nhỏ để thử pipeline sau này.

Vẫn cần theo dõi dung lượng vì ngoài raw dataset còn có `great_sample_manifest.csv`, subset và audit summary.

## 5. Các bước thực hiện Data Understanding

### Bước 1: Xác định dataset

Ghi lại:

- tên dataset;
- nguồn tải;
- ngày audit;
- commit/version remote;
- ngôn ngữ lập trình;
- license repository và license từng sample;
- paper đi kèm;
- README/dataset description.

### Bước 2: Lưu raw dataset bất biến

Raw dataset được lưu dưới:

```text
dataset/raw/great/
```

Với audit hiện tại, tải toàn bộ:

- `README.md`;
- `LICENSE`;
- 300 shard của `train`;
- 300 shard của `dev`;
- 300 shard của `eval`.

### Bước 3: Đọc README, LICENSE và label description

Cần trích xuất:

- dataset được tạo từ ETHPy150Open;
- mỗi dòng trong shard là một JSON example;
- các trường label: `has_bug`, `error_location`, `repair_candidates`, `repair_targets`, `bug_kind`, `bug_kind_name`;
- các trường graph: `source_tokens`, `edges`;
- metadata/license: `provenances`.

### Bước 4: Kiểm tra cấu trúc thư mục và loại file

Kiểm tra:

- có split `train`, `dev`, `eval`;
- mỗi split có bao nhiêu shard;
- tên shard có đúng pattern không;
- file loại text/JSONL;
- có README/LICENSE không.

### Bước 5: Thống kê dung lượng, số file, số sample

Thống kê ở hai mức:

- remote shard manifest cho toàn bộ dataset;
- sample manifest cho các shard đã tải.

Các số liệu cần có:

- tổng số shard;
- tổng dung lượng theo split;
- số dòng/sample trong toàn bộ shard đã tải;
- số sample bug/no-bug;
- số token và edge theo sample.

### Bước 6: Kiểm tra định dạng dữ liệu

Với mỗi sample đã tải:

- decode JSON từng dòng;
- kiểm tra `source_tokens` là `list[str]`;
- kiểm tra `edges` là list edge;
- kiểm tra label fields tồn tại;
- kiểm tra edge endpoint theo token index.

### Bước 7: Kiểm tra lỗi ban đầu

Các lỗi cần gắn cờ trong manifest:

- JSON decode lỗi;
- thiếu field bắt buộc;
- `source_tokens` rỗng;
- `error_location` vượt phạm vi token;
- `repair_targets` vượt phạm vi token;
- `repair_candidates` integer vượt phạm vi token;
- edge endpoint vượt phạm vi token;
- file rỗng;
- sample quá dài;
- duplicate candidate theo hash.

### Bước 8: Kiểm tra split và nguy cơ data leakage

Giữ nguyên split chính thức.

Audit ban đầu kiểm tra trên toàn bộ dữ liệu local:

- cùng `filepath` có xuất hiện trong nhiều split của subset không;
- hash `source_tokens` có trùng giữa split không;
- không dùng `dev/eval` để học vocab hoặc thống kê dùng cho train.

### Bước 9: Tạo manifest/index

Tạo hai manifest:

```text
dataset/interim/great_remote_shard_manifest.csv
dataset/interim/great_sample_manifest.csv
```

Remote shard manifest ghi toàn bộ shard trên GitHub:

```text
split,path,name,size,sha,download_url
```

Sample manifest ghi từng sample trong shard đã tải:

```text
sample_id,split,raw_shard,line_number,language,has_bug,bug_kind_name,num_tokens,num_edges,num_repair_candidates,num_repair_targets,license,filepath,status,note
```

### Bước 10: Tạo subset nhỏ

Tạo subset để thử các bước sau:

```text
dataset/interim/great_sample_subset/
├── train_sample.jsonl
├── dev_sample.jsonl
└── eval_sample.jsonl
```

Subset cần có cả sample bug và no-bug, ưu tiên function không quá 512 token.

### Bước 11: Kiểm tra môi trường chạy

Ghi lại:

- Python version;
- pip version;
- OS/platform;
- GPU qua `nvidia-smi` nếu có;
- PyTorch version nếu đã cài;
- CUDA availability nếu dùng PyTorch.

### Bước 12: Ghi audit summary

Ghi file:

```text
dataset/audit/great_dataset_audit_summary.json
```

Nội dung chính:

- dataset name;
- source;
- commit/version;
- downloaded date;
- downloaded files;
- remote size;
- local raw size;
- sample count trong shard đã tải;
- split summary;
- schema fields;
- known issues;
- leakage check;
- recommended next step.

## 6. Kết quả thực hiện ngày 2026-05-14

Đã tải đầy đủ GREAT dataset vào:

```text
dataset/raw/great/
```

Các file đầu ra đã tạo:

```text
dataset/interim/great_remote_shard_manifest.csv
dataset/interim/great_sample_manifest.csv
dataset/interim/great_sample_subset/train_sample.jsonl
dataset/interim/great_sample_subset/dev_sample.jsonl
dataset/interim/great_sample_subset/eval_sample.jsonl
dataset/audit/great_dataset_audit_summary.json
```

### 6.1. Thông tin dataset

| Trường        | Giá trị                                           |
| ------------- | ------------------------------------------------- |
| Dataset       | GREAT Variable-Misuse dataset                     |
| Nguồn         | https://github.com/google-research-datasets/great |
| Paper         | **Global Relational Models of Source Code**       |
| Dataset gốc   | ETHPy150Open                                      |
| Ngôn ngữ      | Python                                            |
| Task          | Variable Misuse Localization and Repair           |
| Remote commit | `d53603435aa62e598feef5ac0723ec975852cfcc`        |
| Format        | Sharded JSONL text files                          |
| Split         | `train`, `dev`, `eval`                            |

### 6.2. Dung lượng và số file raw

| Split    | Số file |           Dung lượng |
| -------- | ------: | -------------------: |
| `train`  |     300 | 14,231,657,044 bytes |
| `dev`    |     300 |  1,454,105,727 bytes |
| `eval`   |     300 |  7,624,611,231 bytes |
| metadata |       2 |          5,066 bytes |
| Tổng     |     902 | 23,310,379,068 bytes |

Kết quả tải:

- requested files: 902;
- downloaded files: 902;
- failed files: 0;
- raw local size khớp remote size.

### 6.3. Số sample và nhãn

| Split   | Tổng sample |       Bug |    No-bug |
| ------- | ----------: | --------: | --------: |
| `train` |   1,798,742 |   899,371 |   899,371 |
| `dev`   |     185,656 |    92,828 |    92,828 |
| `eval`  |     968,592 |   484,296 |   484,296 |
| Tổng    |   2,952,990 | 1,476,495 | 1,476,495 |

Tất cả sample đã audit có `status = ok`.

### 6.4. Thống kê độ dài

Token length:

- min: 10;
- median: 75;
- p95: 327;
- max: 20,274.

Edge count:

- min: 9;
- median: 120;
- p95: 573;
- max: 36,797.

Nhận xét: phần lớn sample đủ nhỏ cho thử nghiệm ban đầu, nhưng vẫn có function rất dài. Preprocessing sau này cần có ngưỡng độ dài hoặc batching theo kích thước graph.

### 6.5. Split và leakage check

Kiểm tra overlap trên toàn bộ dataset local:

| Kiểm tra                            | Kết quả |
| ----------------------------------- | ------: |
| `train` - `dev` filepath overlap    |       0 |
| `train` - `eval` filepath overlap   |       0 |
| `dev` - `eval` filepath overlap     |       0 |
| `train` - `dev` token-hash overlap  |   2,594 |
| `train` - `eval` token-hash overlap |  10,529 |
| `dev` - `eval` token-hash overlap   |   1,386 |

Nhận định:

- Không thấy cùng `filepath` xuất hiện ở nhiều split.
- Có token-hash overlap giữa split. Cần phân tích sâu ở bước preprocessing/audit tiếp theo trước khi kết luận đây là leakage nghiêm trọng, vì các function ngắn hoặc code sinh tự động/API wrapper có thể trùng token nhưng đến từ file khác nhau.

### 6.6. Subset thử nghiệm

Đã tạo subset nhỏ:

| File                                                     | Số sample | Bug | No-bug |
| -------------------------------------------------------- | --------: | --: | -----: |
| `dataset/interim/great_sample_subset/train_sample.jsonl` |       300 | 150 |    150 |
| `dataset/interim/great_sample_subset/dev_sample.jsonl`   |       300 | 150 |    150 |
| `dataset/interim/great_sample_subset/eval_sample.jsonl`  |       300 | 150 |    150 |

Subset này dùng để thử loader, validate schema và bước preprocessing riêng trước khi chạy toàn bộ dataset.

### 6.7. Môi trường audit

| Thành phần   | Giá trị                                                       |
| ------------ | ------------------------------------------------------------- |
| Python       | 3.10.12                                                       |
| pip          | 25.3                                                          |
| Platform     | WSL2 Ubuntu 22.04 kernel `5.15.153.1-microsoft-standard-WSL2` |
| GPU          | NVIDIA GeForce RTX 4050 Laptop GPU, 6141 MiB                  |
| PyTorch      | 2.11.0+cpu                                                    |
| PyTorch CUDA | Không khả dụng                                                |

### 6.8. Nhận định sau Data Understanding

Dataset GREAT phù hợp để tiếp tục làm đề tài vì:

- đúng task **Variable Misuse Localization and Repair**;
- có nhãn localization và repair rõ ràng;
- có graph edges sẵn, gồm syntax, lexical, control-flow và data-flow edges;
- split chính thức đã cân bằng bug/no-bug;
- raw dataset đã tải đầy đủ và giữ bất biến trong `dataset/raw/great/`.

Các điểm cần xử lý ở bước tiếp theo:

- thiết kế loader đọc JSONL streaming vì dataset có gần 3 triệu sample;
- định nghĩa schema nội bộ cho `source_tokens`, `edges`, `error_location`, `repair_candidates`, `repair_targets`;
- quyết định cách xử lý sample quá dài;
- phân tích token-hash overlap để đánh giá nguy cơ leakage;
- chỉ học vocabulary/statistics từ `train`, không dùng `dev/eval`.
