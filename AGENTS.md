# AGENTS.md

## 1. Mục tiêu dự án

Dự án này tập trung vào đề tài:

**Graph Neural Networks in Program Analysis - Detecting Variable Misuse Bugs**

Mục tiêu chính là nghiên cứu, hiện thực và trình bày pipeline phát hiện lỗi **Variable Misuse**, tức lỗi dùng nhầm một biến đang nằm trong scope thay vì biến đúng về mặt ngữ nghĩa.

Khi làm việc trong repository này, agent phải luôn giữ trọng tâm vào:

- biểu diễn mã nguồn thành program graph;
- phát hiện lỗi sử dụng sai biến;
- mô hình GNN/GGNN cho program analysis;
- localization: xác định vị trí biến bị dùng sai;
- repair: đề xuất biến thay thế đúng;
- đánh giá bằng Localization Accuracy và Repair Accuracy;
- so sánh AST-only graph với graph có thêm NextToken và Data Flow edges.

Không biến dự án này thành bài toán social network analysis, graph mining tổng quát hoặc community detection.

---

## 2. Thứ tự ưu tiên sử dụng tài liệu

Khi cần viết báo cáo, giải thích lý thuyết, tạo slide, viết code hoặc thiết kế thí nghiệm, sử dụng tài liệu theo thứ tự ưu tiên sau:

### 2.1. `instruction.md`

Đây là tài liệu yêu cầu đồ án và tiêu chí chấm điểm.

Luôn ưu tiên tài liệu này khi quyết định:

- cấu trúc báo cáo;
- phạm vi đề tài;
- loại dữ liệu nên dùng;
- model nên hiện thực;
- các bước tiền xử lý;
- cách xây dựng graph;
- cách đánh giá;
- phần trực quan hóa kết quả.

Nếu tài liệu khác mâu thuẫn với `instruction.md`, ưu tiên `instruction.md`.

### 2.2. `gnn_documentation.md`

Đây là nguồn lý thuyết chính cho GNN trong program analysis.

Ưu tiên tài liệu này khi giải thích:

- Program Graph;
- Token Node;
- Syntax Node;
- Symbol Node;
- heterogeneous directed graph;
- AST edge;
- Child / Parent edge;
- NextToken edge;
- Data Flow edge;
- LastRead / LastWrite / LastUse;
- ComputedFrom;
- message passing;
- GGNN;
- localization module;
- repair module;
- long-range dependencies;
- interpretability của node, edge và feature.

### 2.3. `general_paper.md`

Đây là nguồn tổng hợp paper.

Ưu tiên tài liệu này khi viết:

- Related Work;
- Literature Review;
- phần so sánh mô hình;
- phần nói về GREAT;
- phần nói về BugLab;
- phần nói về Self-Supervised Bug Detection and Repair;
- phần nói về Learning to Represent Programs with Graphs;
- phần nói về kết quả hoặc giới hạn của các nghiên cứu trước.

Khi dùng claim từ paper, phải nhắc tên paper tương ứng.

### 2.4. `general_knowledge.md`

Chỉ dùng tài liệu này cho kiến thức đồ thị cơ bản.

Có thể dùng để giải thích:

- node;
- edge;
- directed graph;
- undirected graph;
- adjacency matrix;
- adjacency list;
- path;
- degree;
- centrality nếu thật sự cần cho phần nền.

Không dùng tài liệu này làm nguồn chính cho Variable Misuse, Program Analysis hoặc GNN for Code.

---

## 3. Quy tắc ngôn ngữ

### 3.1. Comment code và tài liệu

Luôn sử dụng **tiếng Việt có dấu** cho:

- comment trong code;
- docstring mô tả logic nghiệp vụ;
- README;
- báo cáo;
- slide;
- tài liệu hướng dẫn chạy;
- ghi chú thí nghiệm;
- mô tả kết quả.

Ví dụ comment đúng:

```python
# Kiểm tra thiết bị khả dụng để ưu tiên chạy trên GPU nếu có.
device = get_runtime_device()
```

Không viết comment tiếng Việt không dấu.

Ví dụ không nên dùng:

```python
# Kiem tra thiet bi kha dung
```

### 3.2. Tên biến, hàm, class, file và folder

Luôn sử dụng **tiếng Anh** cho tên trong code và cấu trúc project.

Quy tắc đặt tên:

- biến: `snake_case`;
- hàm: `snake_case`;
- file Python: `snake_case.py`;
- folder: `snake_case`;
- class: `PascalCase`;
- hằng số: `UPPER_SNAKE_CASE`;
- module/package: `snake_case`;
- test file: `test_<module_name>.py`.

Ví dụ đúng:

```python
class ProgramGraphBuilder:
    pass

def build_program_graph(source_code: str) -> ProgramGraph:
    pass

MAX_SEQUENCE_LENGTH = 512
```

Ví dụ không nên dùng:

```python
def xay_dung_do_thi(ma_nguon):
    pass
```

### 3.3. Thuật ngữ chuyên môn

Giữ nguyên thuật ngữ tiếng Anh chuẩn khi cần độ chính xác học thuật:

- Variable Misuse;
- Program Graph;
- Abstract Syntax Tree / AST;
- Token Node;
- Syntax Node;
- Symbol Node;
- Data Flow;
- Control Flow;
- GGNN;
- Message Passing;
- Localization Accuracy;
- Repair Accuracy;
- Long-range Dependencies;
- Heterogeneous Directed Graph.

Có thể giải thích bằng tiếng Việt, nhưng không tự ý đổi tên thuật ngữ.

---

## 4. Quy tắc kiểm tra phiên bản ngôn ngữ và thư viện

Trước khi cài đặt, import hoặc sử dụng bất kỳ thư viện nào, agent phải kiểm tra phiên bản môi trường hiện tại.

### 4.1. Kiểm tra Python

Luôn kiểm tra:

```bash
python --version
python -m pip --version
```

Nếu có nhiều bản Python, kiểm tra thêm:

```bash
which python
which pip
```

Trên Windows có thể dùng:

```bash
where python
where pip
```

### 4.2. Không cài thư viện vào system Python

Không cài dependency trực tiếp vào Python hệ thống nếu chưa có yêu cầu rõ ràng.

Ưu tiên tạo virtual environment:

```bash
python -m venv .venv
```

Kích hoạt trên macOS/Linux:

```bash
source .venv/bin/activate
```

Kích hoạt trên Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 4.3. Quản lý dependency

Ưu tiên quản lý dependency bằng một trong các cách sau:

1. `pyproject.toml` cho project chính;
2. `requirements.txt` cho môi trường đơn giản;
3. `requirements-dev.txt` cho công cụ phát triển;
4. `environment.yml` nếu dùng Conda;
5. notebook Colab riêng nếu chạy GPU trên Google Colab.

Không thêm dependency mới nếu chưa xác định:

- dependency đó dùng để làm gì;
- có tương thích với Python hiện tại không;
- có tương thích với PyTorch/CUDA hiện tại không;
- có cần GPU hay không;
- có dependency phụ nào dễ xung đột không.

### 4.4. Tra cứu tài liệu thư viện trước khi dùng

Trước khi dùng thư viện mới hoặc API chưa chắc chắn, phải tra cứu tài liệu chính thức hoặc tài liệu đáng tin cậy.

Đặc biệt cần kiểm tra tài liệu trước khi dùng:

- PyTorch;
- PyTorch Geometric;
- DGL;
- NetworkX;
- javalang;
- ast;
- transformers;
- datasets;
- numpy;
- pandas;
- scikit-learn;
- matplotlib.

Không đoán tên hàm, tham số hoặc cú pháp API.

Nếu không chắc API có tồn tại trong phiên bản hiện tại, phải kiểm tra bằng một trong các cách:

```bash
python -c "import package_name; print(package_name.__version__)"
```

hoặc trong Python:

```python
import inspect

print(inspect.signature(target_function))
```

### 4.5. Ghi lại quyết định phiên bản

Nếu thêm hoặc thay đổi dependency, cập nhật ít nhất một trong các file sau:

- `pyproject.toml`;
- `requirements.txt`;
- `requirements-dev.txt`;
- `environment.yml`;
- `docs/environment.md`.

Trong `docs/environment.md`, ghi rõ:

- phiên bản Python;
- hệ điều hành;
- phiên bản PyTorch;
- phiên bản CUDA nếu có;
- phiên bản PyTorch Geometric hoặc DGL nếu có;
- cách cài đặt;
- lệnh kiểm tra môi trường.

---

## 5. Quy tắc GPU, CPU và tách pipeline

Dự án này có thể chạy trên laptop cá nhân hoặc Google Colab. Vì vậy, pipeline phải được thiết kế để chạy được cả CPU và GPU.

### 5.1. Luôn kiểm tra system info trước khi training

Trước khi chạy training, benchmark hoặc tác vụ nặng, agent phải kiểm tra:

```bash
python --version
python -m pip --version
python -c "import platform; print(platform.platform())"
```

Nếu có NVIDIA GPU, kiểm tra:

```bash
nvidia-smi
```

Nếu dùng PyTorch, kiểm tra:

```bash
python -c "import torch; print(torch.__version__); print(torch.cuda.is_available()); print(torch.version.cuda)"
```

### 5.2. Luôn chọn device tự động

Code training phải có logic chọn thiết bị như sau:

```python
import torch


def get_runtime_device() -> torch.device:
    """Chọn GPU nếu khả dụng, nếu không thì dùng CPU."""
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")
```

Không hard-code `cuda` nếu chưa kiểm tra `torch.cuda.is_available()`.

Không hard-code `cpu` nếu model có thể chạy GPU.

### 5.3. Tách pipeline để tránh phụ thuộc phần cứng

Pipeline phải được tách thành các bước độc lập:

1. data download;
2. preprocessing;
3. graph construction;
4. dataset serialization;
5. training;
6. evaluation;
7. visualization;
8. report generation.

Các bước nhẹ nên chạy được trên laptop cá nhân:

- preprocessing nhỏ;
- tạo demo graph;
- unit test;
- kiểm tra AST;
- kiểm tra edge construction;
- visualization nhỏ.

Các bước nặng có thể đưa lên Google Colab:

- training GNN;
- training GREAT-like model;
- hyperparameter search;
- training trên dataset lớn;
- evaluation toàn bộ benchmark.

### 5.4. Thiết kế output trung gian

Mỗi bước pipeline nên ghi output trung gian ra file để có thể chuyển môi trường.

Ví dụ:

```text
data/raw/
data/processed/
data/graphs/
artifacts/checkpoints/
artifacts/metrics/
artifacts/figures/
```

Không để training phụ thuộc trực tiếp vào việc parse lại toàn bộ source code nếu graph đã được tạo sẵn.

### 5.5. Quy tắc Google Colab

Nếu cần chạy trên Google Colab, tạo notebook hoặc script riêng trong:

```text
notebooks/
```

Notebook Colab phải có:

- cell kiểm tra GPU;
- cell cài đúng phiên bản dependency;
- cell mount Google Drive nếu cần;
- cell tải hoặc đọc dataset đã xử lý;
- cell training;
- cell lưu checkpoint;
- cell tải metrics về local.

Không để notebook là nơi duy nhất chứa logic chính. Logic chính phải nằm trong `src/`, notebook chỉ gọi lại code trong project.

---

## 6. Cấu trúc thư mục chuẩn

Ưu tiên cấu trúc project như sau:

```text
.
├── AGENTS.md
├── README.md
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
├── .gitignore
├── docs/
│   ├── environment.md
│   ├── references/
│   │   ├── instruction.md
│   │   ├── gnn_documentation.md
│   │   ├── general_paper.md
│   │   └── general_knowledge.md
│   ├── report/
│   └── slides/
├── data/
│   ├── raw/
│   ├── interim/
│   ├── processed/
│   └── graphs/
├── notebooks/
│   ├── exploratory_analysis.ipynb
│   └── colab_training.ipynb
├── scripts/
│   ├── check_system.py
│   ├── prepare_data.py
│   ├── build_graphs.py
│   ├── train_model.py
│   ├── evaluate_model.py
│   └── visualize_graph.py
├── src/
│   └── variable_misuse_gnn/
│       ├── __init__.py
│       ├── config/
│       │   ├── __init__.py
│       │   └── settings.py
│       ├── data/
│       │   ├── __init__.py
│       │   ├── dataset_loader.py
│       │   └── preprocessing.py
│       ├── graph/
│       │   ├── __init__.py
│       │   ├── ast_parser.py
│       │   ├── graph_builder.py
│       │   ├── edge_types.py
│       │   └── graph_serializer.py
│       ├── models/
│       │   ├── __init__.py
│       │   ├── ggnn.py
│       │   └── baseline.py
│       ├── training/
│       │   ├── __init__.py
│       │   ├── trainer.py
│       │   └── losses.py
│       ├── evaluation/
│       │   ├── __init__.py
│       │   ├── metrics.py
│       │   └── evaluator.py
│       ├── visualization/
│       │   ├── __init__.py
│       │   └── graph_visualizer.py
│       └── utils/
│           ├── __init__.py
│           ├── device.py
│           ├── logging_utils.py
│           └── seed.py
├── tests/
│   ├── test_ast_parser.py
│   ├── test_graph_builder.py
│   ├── test_edge_types.py
│   ├── test_metrics.py
│   └── test_device.py
└── artifacts/
    ├── checkpoints/
    ├── metrics/
    ├── figures/
    └── logs/
```

Nếu project nhỏ, có thể rút gọn, nhưng không được trộn lẫn toàn bộ logic vào một file duy nhất.

---

## 7. Quy tắc quản lý file và dữ liệu

### 7.1. Không commit file nặng

Không commit các file sau nếu không cần thiết:

- dataset lớn;
- checkpoint model;
- file `.pt`, `.pth`, `.ckpt`;
- file graph đã serialize quá lớn;
- log training dài;
- cache;
- virtual environment;
- output tạm.

Các file này nên được đưa vào `.gitignore`.

### 7.2. Đặt tên file rõ nghĩa

Tên file phải dùng tiếng Anh, `snake_case`, mô tả đúng chức năng.

Ví dụ đúng:

```text
graph_builder.py
edge_types.py
train_model.py
evaluate_model.py
localization_metrics.py
```

Ví dụ không nên dùng:

```text
code1.py
test2.py
lam_do_thi.py
final_final.py
```

### 7.3. Không ghi đè dữ liệu gốc

Không sửa trực tiếp file trong `data/raw/`.

Nếu cần xử lý dữ liệu, ghi ra:

```text
data/interim/
data/processed/
data/graphs/
```

---

## 8. Quy tắc viết code

### 8.1. Code phải dễ đọc và dễ kiểm thử

Mỗi hàm chỉ nên làm một nhiệm vụ rõ ràng.

Ưu tiên viết hàm nhỏ cho các bước:

- parse source code;
- tạo node;
- tạo edge;
- build graph;
- serialize graph;
- load dataset;
- compute localization accuracy;
- compute repair accuracy;
- chọn device;
- lưu checkpoint.

### 8.2. Type hints

Ưu tiên dùng type hints cho hàm public.

Ví dụ:

```python
from pathlib import Path


def load_source_file(file_path: Path) -> str:
    """Đọc nội dung mã nguồn từ một file."""
    return file_path.read_text(encoding="utf-8")
```

### 8.3. Docstring

Hàm public nên có docstring tiếng Việt có dấu.

Ví dụ:

```python
def compute_repair_accuracy(total_correct: int, total_samples: int) -> float:
    """Tính Repair Accuracy từ số dự đoán đúng và tổng số mẫu."""
    if total_samples == 0:
        return 0.0
    return total_correct / total_samples
```

### 8.4. Logging thay vì print

Với pipeline chính, ưu tiên dùng logging thay vì `print`.

Cho phép dùng `print` trong notebook hoặc script kiểm tra nhanh.

### 8.5. Random seed

Nếu có training hoặc sampling, luôn đặt seed.

```python
import random
import numpy as np
import torch


def set_random_seed(seed: int) -> None:
    """Thiết lập seed để kết quả thí nghiệm dễ tái lập hơn."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
```

---

## 9. Quy tắc hiện thực graph cho Variable Misuse

### 9.1. Node metadata bắt buộc

Mỗi node trong program graph nên lưu các trường sau nếu có thể:

- `node_id`;
- `node_type`;
- `token_text`;
- `syntax_type`;
- `symbol_name`;
- `source_line`;
- `source_column`;
- `scope_id`.

### 9.2. Edge type bắt buộc

Tối thiểu hỗ trợ:

- `CHILD`;
- `PARENT`;
- `NEXT_TOKEN`;
- `LAST_READ`;
- `LAST_WRITE`;
- `LAST_USE`;
- `COMPUTED_FROM`.

Có thể mở rộng:

- `RETURNS_TO`;
- `GUARDED_BY`;
- `OCCURRENCE_OF`;
- `CALLS`.

### 9.3. Baseline graph variants

Luôn thiết kế để có thể tạo ít nhất ba biến thể graph:

1. `ast_only`;
2. `ast_next_token`;
3. `ast_next_token_data_flow`.

Không viết code graph construction theo kiểu chỉ tạo duy nhất một biến thể không thể so sánh.

---

## 10. Quy tắc model và training

### 10.1. Baseline bắt buộc

Luôn có baseline đơn giản trước khi train model phức tạp.

Tối thiểu nên có:

- AST-only baseline;
- AST + NextToken baseline;
- AST + NextToken + Data Flow model.

### 10.2. Model chính

Model chính theo yêu cầu đồ án là GGNN hoặc GNN message passing tương đương.

Khi viết model, cần tách rõ:

- input node features;
- edge index;
- edge type;
- message passing layers;
- localization head;
- repair head.

### 10.3. Training config

Không hard-code hyperparameter trong code chính.

Đưa config vào file hoặc object riêng:

```text
src/variable_misuse_gnn/config/settings.py
```

Các tham số nên cấu hình được:

- seed;
- batch size;
- learning rate;
- number of epochs;
- hidden dimension;
- number of GNN layers;
- dropout;
- graph variant;
- device;
- checkpoint path.

### 10.4. Checkpoint

Khi training model, lưu checkpoint vào:

```text
artifacts/checkpoints/
```

Checkpoint nên chứa:

- model state dict;
- optimizer state dict;
- epoch;
- best validation metric;
- config đang dùng.

---

## 11. Quy tắc đánh giá

Luôn báo cáo:

- Localization Accuracy;
- Repair Accuracy.

Nếu có thể, báo cáo thêm:

- loss;
- top-k repair accuracy;
- false positive examples;
- ví dụ model dự đoán đúng;
- ví dụ model dự đoán sai.

Khi so sánh mô hình, tối thiểu có bảng:

```text
Model / Graph Variant | Localization Accuracy | Repair Accuracy
```

Bắt buộc so sánh AST-only với graph có Data Flow nếu dữ liệu và thời gian cho phép.

---

## 12. Quy tắc trực quan hóa

Khi trực quan hóa graph:

- đánh dấu node bị dự đoán lỗi;
- đánh dấu node ground-truth nếu có;
- thể hiện khác biệt giữa các loại edge nếu có thể;
- không vẽ graph quá lớn trong báo cáo;
- ưu tiên ví dụ nhỏ, dễ hiểu.

Output hình ảnh lưu vào:

```text
artifacts/figures/
```

---

## 13. Quy tắc viết báo cáo

Khi viết báo cáo, dùng cấu trúc đề xuất:

1. Giới thiệu bài toán;
2. Cơ sở lý thuyết;
3. Biểu diễn mã nguồn thành graph;
4. Mô hình GGNN/GNN;
5. Localization và Repair;
6. Dữ liệu và tiền xử lý;
7. Thí nghiệm và đánh giá;
8. Trực quan hóa kết quả;
9. Thảo luận giới hạn;
10. Kết luận;
11. Tài liệu tham khảo.

Luôn giải thích rõ:

- vì sao compiler có thể bỏ sót Variable Misuse;
- vì sao graph phù hợp với program analysis;
- vì sao Data Flow giúp bắt long-range dependencies;
- vì sao cần Localization Accuracy và Repair Accuracy;
- sự khác nhau giữa bug ngẫu nhiên và bug thật.

---

## 14. Quy tắc citation và paper

Khi nhắc paper, dùng đúng tên chính thức.

Dùng:

- **Global Relational Models of Source Code** cho paper GREAT;
- **Learning to Represent Programs with Graphs** cho paper nền tảng GGNN/Variable Misuse;
- **Self-Supervised Bug Detection and Repair** cho BugLab;
- **Deep Learning for Source Code Modeling and Generation: Models, Applications and Challenges** cho survey source code modeling.

Không gọi GREAT là "Graph-based Representation Attentional Network" trừ khi đang giải thích rằng đây là tên ghi chưa chính xác trong đề bài.

Không bịa thêm paper, dataset, metric hoặc số liệu nếu chưa có nguồn.

---

## 15. Quy tắc kiểm thử

Khi thêm code mới, ưu tiên thêm test tương ứng trong `tests/`.

Tối thiểu nên test:

- parser có đọc được code mẫu không;
- graph builder có tạo đúng node không;
- graph builder có tạo đúng edge type không;
- metric có tính đúng không;
- device selection có fallback CPU không;
- serialization/deserialization có giữ metadata không.

Chạy test bằng:

```bash
pytest
```

Nếu chưa có `pytest`, phải kiểm tra dependency và cập nhật file dependency trước khi dùng.

---

## 16. Quy tắc trước khi hoàn thành task

Trước khi kết thúc một task, agent phải tự kiểm tra:

- Có bám đúng `instruction.md` không?
- Có dùng `gnn_documentation.md` cho phần lý thuyết không?
- Có dùng `general_paper.md` cho phần paper không?
- Có tránh lệch sang graph/social network chung chung không?
- Code có comment tiếng Việt có dấu không?
- Tên biến, hàm, file, folder có dùng tiếng Anh đúng quy ước không?
- Có kiểm tra phiên bản Python/thư viện khi thêm dependency không?
- Có tránh hard-code GPU/CPU không?
- Pipeline có thể chạy từng bước độc lập không?
- Có thể chuyển phần training nặng sang Colab không?
- Có test hoặc hướng dẫn test không?
- Có cập nhật tài liệu môi trường nếu thay đổi dependency không?

---

## 17. Những điều không được làm

Không được:

- viết comment tiếng Việt không dấu;
- đặt tên biến/hàm/file/folder bằng tiếng Việt;
- đoán API thư viện khi chưa chắc phiên bản;
- cài dependency mới mà không kiểm tra phiên bản;
- hard-code `cuda` mà không kiểm tra GPU;
- hard-code đường dẫn tuyệt đối theo máy cá nhân;
- ghi đè dữ liệu gốc trong `data/raw/`;
- commit virtual environment;
- commit checkpoint hoặc dataset lớn;
- trộn toàn bộ pipeline vào một file duy nhất;
- bỏ qua Localization Accuracy hoặc Repair Accuracy;
- bỏ qua baseline AST-only;
- tuyên bố model hoạt động tốt trên bug thật nếu chỉ test trên bug synthetic;
- bịa tên paper, dataset hoặc kết quả thực nghiệm;
- để notebook chứa toàn bộ logic chính mà không có module trong `src/`.

---

## 18. Definition of Done

Một task được xem là hoàn thành khi:

- kết quả bám đúng yêu cầu đồ án;
- nội dung dùng đúng tài liệu theo thứ tự ưu tiên;
- code chạy được hoặc có hướng dẫn chạy rõ ràng;
- dependency được quản lý rõ;
- môi trường CPU/GPU được xử lý an toàn;
- pipeline được tách thành các bước có thể chạy độc lập;
- comment và tài liệu dùng tiếng Việt có dấu;
- tên trong code dùng tiếng Anh đúng quy ước;
- có test hoặc checklist kiểm tra;
- kết quả đánh giá có Localization Accuracy và Repair Accuracy nếu task liên quan đến model;
- output được lưu đúng thư mục trong `artifacts/` nếu có sinh file kết quả.
