# TỔNG HỢP KIẾN THỨC TỪ CÁC BÀI BÁO KHOA HỌC (PAPERS) 
*(Phục vụ đồ án: Graph Neural Networks in Program Analysis - Detecting Variable Misuse Bugs)*

Tài liệu này tổng hợp các kiến thức gốc từ các bài báo khoa học (papers) được chỉ định, đối chiếu trực tiếp với yêu cầu của tài liệu hướng dẫn đồ án (`instruction.md`).

---

## 1. Giới thiệu bài toán (Variable Misuse)

Lỗi sử dụng sai biến (Variable Misuse) là một loại lỗi ngữ nghĩa trong lập trình.
- **Định nghĩa**: Theo bài báo *"Learning to Represent Programs with Graphs" (Allamanis et al., 2018)*, lỗi này xảy ra khi một biến được sử dụng sai tại một vị trí trong chương trình, thay cho một biến khác đúng hơn có sẵn trong cùng phạm vi (scope). 
- **Đặc điểm**: Mã nguồn có lỗi này thường vẫn đúng về mặt cú pháp và có thể biên dịch thành công (do các biến có cùng kiểu dữ liệu), dẫn đến việc các công cụ phân tích tĩnh hoặc trình biên dịch truyền thống không thể phát hiện.
- **Giải pháp Neural / GNN**: *"Graph Neural Networks in Program Analysis" (Allamanis, Chapter 22)* chỉ ra rằng, phân tích chương trình dựa trên Machine Learning giúp suy luận xác suất về tính chính xác của các biến dựa trên ngữ cảnh mã nguồn thay vì chỉ dựa vào phân tích tĩnh chặt chẽ.

---

## 2. Dữ liệu và Tiền xử lý (Datasets)

Các mô hình Neural Network hiện đại cho Code thường yêu cầu biểu diễn mã nguồn với các đặc trưng cấu trúc sâu.
- **Tập dữ liệu**: 
  - Đồ án đề xuất `ETHPy150` (Python) và `GitHub Java Corpus`.
  - Bài báo *"Global Relational Models of Source Code" (Hellendoorn et al., ICLR 2020)* cung cấp tập dữ liệu `GreatEL` và `Varsity` chuyên biệt cho bài toán Variable Misuse, chứa các đồ thị mã nguồn phong phú.
- **Tiền xử lý (Preprocessing)**: Mã nguồn không chỉ giữ nguyên ở dạng văn bản mà được phân tích bằng thư viện (`javalang` cho Java, hoặc module `ast` cho Python) để xây dựng Cây cú pháp trừu tượng (Abstract Syntax Tree - AST).

---

## 3. Biểu diễn Mã nguồn bằng Đồ thị (Graph Construction)

Đây là cốt lõi của các mô hình GNN. Dựa trên *"Learning to Represent Programs with Graphs" (Allamanis et al., 2018)*, mã nguồn được chuyển hóa thành đồ thị $G = (V, E)$.

**A. Các Nút (Nodes)**
- Nút cú pháp (Syntax nodes): Các cấu trúc như `IfStatement`, `WhileStatement`, `MethodDeclaration`.
- Nút từ vựng (Syntax tokens / Leaves): Các định danh (tên biến, tên hàm), từ khóa, toán tử.

**B. Các loại Cạnh (Edge Types)**
Cạnh được phân loại để thể hiện cả luồng cú pháp và luồng ngữ nghĩa (Control Flow & Data Flow):
1. **Child / Parent**: Liên kết các nút trong cây AST. Thể hiện cấu trúc cú pháp của chương trình.
2. **NextToken**: Liên kết các nút lá (token) theo thứ tự xuất hiện từ trái qua phải, giúp mô hình nắm bắt được luồng văn bản tuần tự (sequential flow).
3. **LastRead / LastWrite (LastUse)**: Kết nối sự xuất hiện của một biến tại một vị trí với vị trí gần nhất mà biến đó được đọc hoặc được gán (ghi) giá trị trước đó. (Luồng dữ liệu - Data flow).
4. **ComputedFrom**: Kết nối một biến ở vế trái của biểu thức gán với tất cả các biến ở vế phải được dùng để tính toán ra nó.
5. **ReturnsTo**: Kết nối các lệnh `return` với nút khai báo hàm tương ứng.
6. **GuardedBy**: Kết nối biến với điều kiện logic kiểm soát đoạn code sử dụng biến đó.

*=> Việc tích hợp Data Flow (LastRead/LastWrite) cho phép mô hình dễ dàng vượt qua giới hạn phụ thuộc xa (long-range dependencies) mà các mô hình tuần tự như RNNs/LSTMs truyền thống thường thất bại.*

---

## 4. Cơ sở Lý thuyết & Các Mô hình (Models)

### 4.1. Gated Graph Neural Networks (GGNN)
- Được sử dụng làm nền tảng trong *"Learning to Represent Programs with Graphs"*.
- **Cơ chế**: Tại mỗi bước học, các nút trao đổi thông điệp (message passing) dọc theo các cạnh. Mỗi loại cạnh có một ma trận trọng số riêng. Nút sẽ cập nhật trạng thái ẩn (hidden state) của nó bằng một hàm Gated Recurrent Unit (GRU) dựa trên thông điệp nhận được. Cuối cùng, trạng thái ẩn này được dùng để tính toán xác suất dự đoán biến phù hợp tại vị trí bị lỗi.

### 4.2. GREAT (Graph Relational Embedding Attention Transformer)
- Đề xuất trong *"Global Relational Models of Source Code" (Hellendoorn et al., ICLR 2020)*.
- **Cơ chế**: Giải quyết điểm yếu của GNN truyền thống (chỉ truyền thông điệp cục bộ) bằng cách lai tạo giữa Transformer (mô hình tuần tự toàn cục) và Graph. GREAT điều chỉnh cơ chế "Self-Attention" của Transformer bằng cách cộng thêm "Relational Bias" dựa trên các loại cạnh (AST, Data flow) nối giữa 2 nút trong đồ thị.
- **Hiệu quả**: Mô hình GREAT cải thiện độ chính xác 10-15% so với GNN truyền thống, đồng thời học nhanh hơn và dùng ít tham số hơn.

### 4.3. BugLab - Học tự giám sát (Self-Supervised Learning)
- Đề xuất trong *"Self-Supervised Bug Detection and Repair" (Allamanis et al., NeurIPS 2021)*.
- **Vấn đề**: Thiếu tập dữ liệu khổng lồ chứa lỗi thực tế đã được gán nhãn.
- **Giải pháp**: Huấn luyện theo cơ chế đồng huấn luyện (co-training) hai mô hình:
  - *Selector (Người tạo lỗi)*: Học cách cố ý sửa các đoạn code đúng thành code có lỗi (ví dụ, thay tên biến đúng bằng biến sai).
  - *Detector (Người phát hiện)*: Học cách phát hiện và sửa các lỗi do Selector tạo ra.
- Cách tiếp cận này giúp học phát hiện Variable Misuse hiệu quả mà không cần dữ liệu có nhãn thủ công.

---

## 5. Hiện thực & Đánh giá (Evaluation Metrics)

### 5.1. Các Độ đo (Metrics)
Dựa theo các phương pháp nghiên cứu chuẩn:
- **Localization Accuracy (Độ chính xác định vị)**: Tỉ lệ phần trăm mô hình xác định chính xác dòng code / vị trí nút có chứa biến sử dụng sai.
- **Repair Accuracy (Độ chính xác sửa lỗi)**: Trong trường hợp đã xác định được vị trí lỗi, đây là tỉ lệ mô hình đề xuất đúng tên biến thay thế từ tập hợp các biến có sẵn trong phạm vi (scope).

### 5.2. So sánh khả năng (Neural Bug Detectors vs Humans)
- Trong bài báo *"Are Neural Bug Detectors Comparable to Software Developers on Variable Misuse Bugs?" (Richter et al., 2022)*, các nghiên cứu thực nghiệm đã được tiến hành để so sánh GNN với con người.
- **Kết quả**: 
  - Mô hình Neural có hiệu suất gần tương đương (comparable) với nhóm các lập trình viên chuyên nghiệp trong việc phân loại và định vị lỗi Variable Misuse.
  - Tuy nhiên, khuyết điểm của các mô hình là thường đưa ra tỉ lệ báo động giả (false alarms) cao hơn so với con người.
  - Sự kết hợp giữa khả năng bắt phụ thuộc xa (long-range dependencies nhờ luồng dữ liệu) giúp GNN phát hiện những lỗi khó mà bằng mắt thường (ngữ cảnh hẹp) con người dễ bỏ sót.

---
*Tài liệu được tổng hợp hoàn toàn dựa trên các kiến thức cốt lõi và kết quả thực nghiệm từ danh sách các ấn phẩm khoa học được cung cấp.*
