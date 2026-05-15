# Hướng dẫn resume training AST-only trên Colab runtime mới

Tài liệu này dùng khi runtime Colab cũ đã tắt hoặc sắp bị tắt, trong khi quá trình training `ast_only` đang chạy dở. Mục tiêu là khôi phục dữ liệu từ Google Drive, load `last_model.pt`, rồi tiếp tục training từ epoch đã lưu gần nhất.

## 1. Điều kiện cần có

Trên Google Drive cần có thư mục backup dạng:

```text
/content/drive/MyDrive/variable_misuse_training_backup/<timestamp>/
├── training_output.zip
├── graphs.zip
├── embedding.zip
└── shared_token_embedding_300000.zip
```

Trong lần backup gần nhất, thư mục đã xác nhận có:

```text
/content/drive/MyDrive/variable_misuse_training_backup/20260515_135106/
├── training_output.zip
├── graphs.zip
├── embedding.zip
└── shared_token_embedding_300000.zip
```

Ý nghĩa các file:

- `training_output.zip`: chứa checkpoint và metrics, gồm `best_model.pt`, `last_model.pt`, `metrics_history.json`.
- `graphs.zip`: chứa graph shards cho `ast_only`.
- `embedding.zip`: chứa shared token embedding artifacts.
- `shared_token_embedding_300000.zip`: bản zip gốc của shared embedding, dùng để dự phòng.

## 2. Cell 1 - Mount Drive và chọn backup mới nhất

```python
from google.colab import drive
from pathlib import Path

drive.mount("/content/drive")

BACKUP_ROOT = Path("/content/drive/MyDrive/variable_misuse_training_backup")

# Tự lấy backup mới nhất. Nếu muốn cố định, đổi thành:
# BACKUP_DIR = BACKUP_ROOT / "20260515_135106"
BACKUP_DIR = sorted([p for p in BACKUP_ROOT.iterdir() if p.is_dir()])[-1]

print("Using backup:", BACKUP_DIR)

for name in ["training_output.zip", "graphs.zip", "embedding.zip"]:
    path = BACKUP_DIR / name
    print(
        path,
        path.exists(),
        round(path.stat().st_size / (1024 ** 2), 2) if path.exists() else None,
        "MB",
    )
```

Nếu cell này báo thiếu `training_output.zip`, không nên chạy tiếp vì sẽ không có checkpoint để resume.

## 3. Cell 2 - Clone source code

```python
import os
import subprocess
import sys
from pathlib import Path

REPO_URL = "https://github.com/HuyBui2112/detecting_variable_misuse_bugs.git"
BRANCH = "main"
REPO_DIR = Path("/content/detecting_variable_misuse_bugs")

if not REPO_DIR.exists():
    subprocess.run(["git", "clone", "--branch", BRANCH, REPO_URL, str(REPO_DIR)], check=True)
else:
    subprocess.run(["git", "fetch", "origin"], cwd=REPO_DIR, check=True)
    subprocess.run(["git", "checkout", BRANCH], cwd=REPO_DIR, check=True)
    subprocess.run(["git", "pull", "--ff-only"], cwd=REPO_DIR, check=True)

os.chdir(REPO_DIR)
sys.path.insert(0, str(REPO_DIR / "src"))

!git log -1 --oneline
```

Notebook chỉ gọi code trong `src/` và `scripts/`, không chứa logic training chính.

## 4. Cell 3 - Kiểm tra Python, PyTorch và GPU

```python
!python --version
!python -m pip --version

import torch

print("torch:", torch.__version__)
print("cuda available:", torch.cuda.is_available())
print("cuda:", torch.version.cuda)

!nvidia-smi || true
!df -h /content
```

Nếu `cuda available: True`, training sẽ tự dùng GPU thông qua logic chọn device trong source code. Nếu là `False`, code vẫn chạy CPU nhưng sẽ chậm hơn nhiều.

## 5. Cell 4 - Khôi phục graph, embedding và checkpoint

```python
import zipfile
from pathlib import Path

CONTENT_ROOT = Path("/content")

GRAPH_VARIANT = "ast_only"
GRAPH_ROOT = CONTENT_ROOT / "graphs"
EMBEDDING_ROOT = CONTENT_ROOT / "embedding" / "shared_token_embedding_300000"
OUTPUT_ROOT = CONTENT_ROOT / "training_output"

restore_targets = [
    (BACKUP_DIR / "graphs.zip", GRAPH_ROOT),
    (BACKUP_DIR / "embedding.zip", CONTENT_ROOT / "embedding"),
    (BACKUP_DIR / "training_output.zip", OUTPUT_ROOT),
]

for zip_path, extract_dir in restore_targets:
    assert zip_path.exists(), f"Thiếu file backup: {zip_path}"
    if extract_dir.exists():
        print("Already exists, skip:", extract_dir)
        continue

    extract_dir.mkdir(parents=True, exist_ok=True)
    print("Extract:", zip_path, "->", extract_dir)
    with zipfile.ZipFile(zip_path) as archive:
        archive.extractall(extract_dir)

print("Done restore.")
```

Sau cell này, runtime mới sẽ có lại:

```text
/content/graphs/
/content/embedding/
/content/training_output/
```

## 6. Cell 5 - Kiểm tra cấu trúc sau khi khôi phục

```python
from pathlib import Path

target_train_dir = GRAPH_ROOT / GRAPH_VARIANT / "train"
target_dev_dir = GRAPH_ROOT / GRAPH_VARIANT / "dev"

LAST_CHECKPOINT = OUTPUT_ROOT / GRAPH_VARIANT / "last_model.pt"
BEST_CHECKPOINT = OUTPUT_ROOT / GRAPH_VARIANT / "best_model.pt"

checks = [
    GRAPH_ROOT,
    target_train_dir,
    target_dev_dir,
    EMBEDDING_ROOT,
    EMBEDDING_ROOT / "token_to_id.json",
    EMBEDDING_ROOT / "embedding_init.pt",
    OUTPUT_ROOT / GRAPH_VARIANT,
    LAST_CHECKPOINT,
    BEST_CHECKPOINT,
]

for path in checks:
    print(path, path.exists())

assert target_train_dir.exists()
assert target_dev_dir.exists()
assert list(target_train_dir.glob("*.jsonl")), "Không thấy train shard"
assert list(target_dev_dir.glob("*.jsonl")), "Không thấy dev shard"
assert (EMBEDDING_ROOT / "token_to_id.json").exists()
assert (EMBEDDING_ROOT / "embedding_init.pt").exists()
assert LAST_CHECKPOINT.exists(), "Không thấy last_model.pt để resume"
```

Nếu `LAST_CHECKPOINT` không tồn tại, kiểm tra lại `training_output.zip` trong Drive.

## 7. Cell 6 - Xem checkpoint đang dừng ở epoch nào

```python
import json
import torch

try:
    checkpoint = torch.load(LAST_CHECKPOINT, map_location="cpu", weights_only=False)
except TypeError:
    checkpoint = torch.load(LAST_CHECKPOINT, map_location="cpu")

print("Checkpoint epoch:", checkpoint["epoch"])
print("Resume sẽ chạy từ epoch:", checkpoint["epoch"] + 1)
print("Best monitor score:", checkpoint.get("best_monitor_score"))

history = checkpoint.get("history", [])
print("History length:", len(history))

if history:
    print(json.dumps(history[-1], ensure_ascii=False, indent=2))
```

Lưu ý: nếu checkpoint đang ở `epoch = 4`, lệnh resume với `--epochs 20` sẽ chạy từ epoch 5 đến epoch 20. Tham số `--epochs` là tổng số epoch cuối cùng, không phải số epoch chạy thêm.

## 8. Cell 7 - Resume training AST-only

```python
!PYTHONPATH=src python scripts/train_gnn.py \
  --graph-root "{GRAPH_ROOT}" \
  --embedding-root "{EMBEDDING_ROOT}" \
  --output-root "{OUTPUT_ROOT}" \
  --graph-variant "{GRAPH_VARIANT}" \
  --resume-from-checkpoint "{LAST_CHECKPOINT}" \
  --epochs 20 \
  --batch-size 8 \
  --hidden-dim 128 \
  --message-passing-steps 4 \
  --log-every 100 \
  --early-stopping-patience 3 \
  --early-stopping-min-delta 0.0001 \
  --monitor-metric combined \
  --lr-scheduler-patience 2 \
  --lr-scheduler-factor 0.5
```

Nếu bị thiếu bộ nhớ GPU, dùng cấu hình batch nhỏ hơn:

```python
!PYTHONPATH=src python scripts/train_gnn.py \
  --graph-root "{GRAPH_ROOT}" \
  --embedding-root "{EMBEDDING_ROOT}" \
  --output-root "{OUTPUT_ROOT}" \
  --graph-variant "{GRAPH_VARIANT}" \
  --resume-from-checkpoint "{LAST_CHECKPOINT}" \
  --epochs 20 \
  --batch-size 4 \
  --hidden-dim 128 \
  --message-passing-steps 4 \
  --log-every 100 \
  --early-stopping-patience 3 \
  --early-stopping-min-delta 0.0001 \
  --monitor-metric combined \
  --lr-scheduler-patience 2 \
  --lr-scheduler-factor 0.5
```

Không đổi `hidden_dim` hoặc `message_passing_steps` khi resume từ checkpoint cũ, vì kiến trúc model phải khớp checkpoint.

## 9. Cell 8 - Xem kết quả sau khi resume

```python
import json

summary_path = OUTPUT_ROOT / GRAPH_VARIANT / "training_summary.json"
metrics_path = OUTPUT_ROOT / GRAPH_VARIANT / "metrics_history.json"

print("summary:", summary_path, summary_path.exists())
print("metrics:", metrics_path, metrics_path.exists())

if summary_path.exists():
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    print("device:", summary.get("device"))
    print("best_monitor_score:", summary.get("best_monitor_score"))
    print("stopped_early:", summary.get("stopped_early"))
    print("last epoch:")
    print(json.dumps(summary["history"][-1], ensure_ascii=False, indent=2))
```

Cần báo cáo tối thiểu:

- `dev.localization_accuracy`
- `dev.repair_accuracy`
- `best_monitor_score`
- epoch tốt nhất hoặc epoch cuối.

## 10. Cell 9 - Backup checkpoint mới lên Drive

Luôn chạy cell này trước khi tắt runtime.

```python
from pathlib import Path
import time
import shutil

NEW_BACKUP_DIR = BACKUP_ROOT / f"ast_only_resume_{time.strftime('%Y%m%d_%H%M%S')}"
NEW_BACKUP_DIR.mkdir(parents=True, exist_ok=True)

archive_path = shutil.make_archive(
    str(NEW_BACKUP_DIR / "training_output"),
    "zip",
    root_dir=str(OUTPUT_ROOT),
)

print("Saved:", archive_path)
```

Nếu muốn lưu luôn metrics riêng để tải về máy:

```python
from google.colab import files

for name in ["metrics_history.json", "training_summary.json"]:
    path = OUTPUT_ROOT / GRAPH_VARIANT / name
    print(path, path.exists())
    if path.exists():
        files.download(str(path))
```

## 11. Quy tắc an toàn khi dừng runtime

- Nếu dừng cell giữa epoch, epoch đang chạy dở không được lưu.
- `last_model.pt` chỉ được cập nhật sau khi hoàn thành một epoch.
- `best_model.pt` chỉ được cập nhật khi metric dev tốt hơn trước.
- Vì output nằm trong `/content`, luôn backup sang Drive trước khi tắt runtime.
- Khi mở runtime mới, resume từ `last_model.pt`, không resume từ `best_model.pt` nếu mục tiêu là chạy tiếp quá trình training.

## 12. Kiểm tra nhanh sau mỗi lần backup

```python
for path in NEW_BACKUP_DIR.rglob("*"):
    if path.is_file():
        print(path, round(path.stat().st_size / (1024 ** 2), 2), "MB")
```

Backup hợp lệ tối thiểu phải có:

```text
training_output.zip
```

Nếu không muốn upload lại graph và embedding ở lần sau, nên giữ thêm:

```text
graphs.zip
embedding.zip
shared_token_embedding_300000.zip
```
