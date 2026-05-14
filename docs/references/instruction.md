# Bài tập 05: Graph Neural Networks in Program Analysis - Detecting Variable Misuse Bugs

## 1. Giới thiệu bài toán (1 điểm)

- **Vấn đề:** Lỗi sử dụng sai biến (Variable Misuse) xảy ra khi lập trình viên sử dụng nhầm một biến hiện có thay vì biến đúng (ví cả hai đều có cùng kiểu dữ liệu). Trình biên dịch thường không phát hiện được lỗi này vì nó đúng về mặt cú pháp nhưng sai về mặt logic.
- **Giải pháp GNN:** Biểu diễn mã nguồn dưới dạng đồ thị bao gồm các nút (biến, toán tử, lệnh) và các cạnh (luồng điều khiển - Control Flow, luồng dữ liệu - Data Flow). GNN sẽ học cách "hiểu" ngữ cảnh của mã để dự đoán biến nào là phù hợp nhất tại một vị trí cụ thể.

## 2. Dữ liệu (1 điểm)

- **Tập dữ liệu đề xuất:** `ETHPy150 (cho Python)` hoặc `GitHub Java Corpus`. Tuy nhiên, để làm demo tốt nhất, bạn nên dùng tập dữ liệu từ paper `"GreatEL"` hoặc `"Varsity"`.
- **Nguồn dữ liệu:**
  - Py150 Dataset: https://www.sri.inf.ethz.ch/py150
  - CuBERT Datasets: https://github.com/google-research/google-research/tree/master/cubert
- **Mô tả:** Dữ liệu bao gồm các tệp mã nguồn đã được chuyển đổi sang dạng AST (Abstract Syntax Tree) bổ sung thêm các cạnh đặc biệt như LastUse, LastWrite, ComputedFrom.
- **Trực quan:** Vẽ sơ đồ một đoạn code ngắn và đồ thị tương ứng của nó để minh họa các "nút" và "cạnh".

## 3. Cơ sở lý thuyết & Model (2 điểm)

**Danh sách các paper tham khảo:**

1. "Great: Graph-based Representation Attentional Network for Variable Misuse".
2. "Variable Misuse Detection with Relational Graph Attention Networks".
3. "Context-Aware Bug Detection using Deep Learning on Graphs".
4. "Self-Supervised Learning for Program Analysis with GNNs".
5. "Deep Learning for Source Code Modeling: A Survey".

**Cơ chế hoạt động:**
Graph Construction: Xây dựng đồ thị từ mã nguồn. Các loại cạnh quan trọng:

- Child/Parent: Cạnh trong cây AST.
- NextToken: Luồng tuyến tính của code.
- LastRead/LastWrite: Luồng dữ liệu của biến.

## 4. Hiện thực & Đánh giá (4 điểm)

**Các bước thực hiện:**

1. Tiền xử lý: Sử dụng thư viện javalang (cho Java) hoặc ast (cho Python) để phân tích code thành cây AST.
2. Xây dựng đồ thị: Dùng NetworkX hoặc trực tiếp chuyển sang định dạng của DGL hoặc PyTorch Geometric.
3. Học nhúng (Embedding): Chuyển các token (tên biến, từ khóa) thành vector thông qua một bộ Word2Vec hoặc dùng trực tiếp các lớp Embedding.
4. Huấn luyện GNN: Sử dụng mô hình Gated Graph Neural Network (GGNN) – loại GNN rất hiệu quả cho phân tích chương trình (được nhắc đến nhiều trong tài liệu bạn gửi).
5. Dự đoán: Tại một vị trí biến bị nghi ngờ, model sẽ tính toán xác suất cho tất cả các biến có sẵn trong phạm vi (scope) và chọn biến có xác suất cao nhất.

**Cách đánh giá:**

- Tối ưu (1đ): So sánh độ chính xác khi sử dụng chỉ AST truyền thống so với việc thêm các cạnh luồng dữ liệu (Data Flow).
- Trực quan kết quả (1đ): \* Bảng so sánh Localization Accuracy (Khả năng tìm đúng vị trí lỗi) và Repair Accuracy (Khả năng sửa đúng lỗi).
  - Vẽ đồ thị các biến trong một hàm và đánh dấu node bị dự đoán lỗi bằng màu đỏ.
- Diễn giải (1đ): Phân tích xem GNN có bắt được lỗi khi biến bị dùng sai nằm cách xa vị trí khai báo hay không (long-range dependencies).
