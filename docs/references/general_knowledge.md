# TỔNG HỢP KIẾN THỨC MÔN HỌC: MẠNG XÃ HỘI (SOCIAL NETWORK)

---

## Chương 1: Tổng quan mạng xã hội (Social Network) & Ứng dụng

### 1.1. Giới thiệu về Mạng xã hội
- **Định nghĩa tổng quát**: Mạng xã hội (Social Network) là một đồ thị mô tả sự tương tác giữa các cá thể có cùng mối quan tâm, có liên hệ trực tiếp hay gián tiếp. 
- Mạng xã hội là dịch vụ nối kết các thành viên cùng sở thích trên internet lại với nhau với nhiều mục đích khác nhau không phân biệt không gian và thời gian.
- **Cấu trúc mạng xã hội**: Một mạng xã hội bao gồm một tập hợp các thành phần/thực thể (nodes - nút) có thể là một cá thể, một tập thể, thậm chí là một tổ chức có liên kết, ràng buộc lẫn nhau thông qua các mối quan hệ xã hội (edges/links - liên kết).
- **Mạng xã hội (social media)**: Phương tiện tương tác của con người để tạo, chia sẻ và trao đổi thông tin và ý tưởng trong cộng đồng ảo và mạng một cách trực tuyến.

### 1.2. Đặc điểm và lợi ích của Mạng xã hội
**Lợi ích**:
- Cập nhật tin tức, kiến thức, xu thế nhanh chóng.
- Cải thiện chất lượng và tốc độ của báo chí và dịch vụ.
- Kết nối bạn bè, gia đình, cộng đồng.
- Kết nối yêu thương và hòa nhập quốc tế.
- Cải thiện kỹ năng sống, kiến thức.
- Kinh doanh, quảng cáo miễn phí.
- Tiết kiệm kinh phí, thời gian, sức lực.
- Động viên tinh thần và chia sẻ cảm xúc.
- Quảng bá hình ảnh cho những người nổi tiếng.

**Tác hại (Khía cạnh tiêu cực)**:
- Giảm tương tác giữa người với người.
- Tăng mong muốn gây chú ý.
- Xao nhãng mục tiêu cá nhân.
- Nguy cơ trầm cảm.
- Giết chết sự sáng tạo.
- Bạo lực trên mạng.
- Tình yêu dễ đổ vỡ.
- Mất ngủ, thiếu riêng tư.

### 1.3. Mô hình Mạng xã hội (Social Network Model)
Trong công nghệ thông tin, mạng xã hội trực tuyến là nơi kết nối các thành viên cùng sở thích trên Internet không phân biệt không gian và thời gian thông qua các dịch vụ mạng xã hội (Facebook, Twitter, Myspace, YouTube, Flickr,...). 
Các nút mạng (Nodes) là sự hợp tác của công cụ, dịch vụ trực tuyến (như thư điện tử, diễn đàn thảo luận, blogs, chat,...).

### 1.4. Một số nguyên tắc xã hội cơ bản
1. **Ảnh hưởng xã hội (Social Influence)**: Quan hệ xã hội ảnh hưởng đến sở thích, hành vi, quyết định của con người.
2. **Đồng cảm (Homophily)**: "Sự tương tự tạo ra kết nối".
3. **Sự gần gũi (Proximity)**: "Những người gần nhau sẽ dễ phát sinh mối quan hệ".
4. **Chuyền tiếp (Transitivity)**: Nếu có liên kết A với B, và B với C, trong một mạng có tính chuyền tiếp thì A sẽ dễ dàng kết nối với C.
5. **Cầu (Bridges)**: Cạnh và node kết nối hai nhóm đúc (nếu loại bỏ các bridge này thì đồ thị bị chia cắt), mang lại sự giao tiếp trọng yếu.

### 1.5. Phân tích Mạng xã hội (Social Network Analysis - SNA)
**Định nghĩa**: SNA là việc ứng dụng các phương pháp đo lường, tính toán lên các dữ liệu mạng (ví dụ: dữ liệu di động, dữ liệu từ Facebook, Twitter...) để hiểu rõ cấu trúc, quan hệ và dòng thông tin.
**Ứng dụng**: 
- Phát triển các hệ thống gợi ý (Recommender Systems) như: khuyến nghị mua hàng, khuyến nghị du lịch, khuyến nghị phim/bài hát.
- Hỗ trợ kinh doanh trực tuyến, ra quyết định chiến lược, quản lý thương hiệu (Social CRM).

**Khó khăn và Thách thức**:
- Độ phức tạp tính toán rất cao. Ví dụ: Với mạng có 30 nodes, mỗi node có thể tồn tại liên kết hoặc không, sẽ tạo ra một không gian trạng thái khổng lồ ($2^{435}$ networks).
- Dữ liệu lớn (Big Data), thay đổi liên tục theo thời gian thực (Velocity, Volume, Variety).

### 1.6. Dữ liệu từ mạng xã hội
Quá trình phân tích mạng xã hội đòi hỏi phải thu thập và xử lý các loại dữ liệu sau:
- **Dữ liệu cá nhân**: Hồ sơ (tuổi, giới tính, nghề nghiệp), sở thích, hành vi/thói quen, cảm xúc, tính cách.
- **Dữ liệu quan hệ**: Các mối liên kết bạn bè (ví dụ: Facebook), quan hệ công việc, chuyên môn (LinkedIn), quan hệ theo dõi một chiều (Twitter), quan hệ giữa cá nhân và doanh nghiệp/người nổi tiếng.
- **Dữ liệu cộng đồng**: Những cá nhân có cùng sở thích tham gia vào các nhóm (Group trên Facebook, LinkedIn...).

### 1.7. Các bài toán phổ biến trong phân tích mạng xã hội
1. **Phát hiện cộng đồng (Community Detection)**: 
   - Cộng đồng tách rời hoặc cộng đồng giao nhau.
   - Các phương pháp phân chia, dựa trên mô-đun hóa, dựa trên phổ, dựa trên suy luận thống kê.
   - Một số thuật toán phổ biến: Thuật toán phân tách Girvan-Newman, CONGA, CONGO, gán nhãn COPRA...
2. **Dự đoán liên kết (Link Prediction)**: Dự đoán các liên kết/tương tác tiềm năng có thể xuất hiện trong tương lai dựa trên cấu trúc hiện tại.
3. **Phân tích vai trò (Role Analysis)**: Tìm ra những cá thể đóng vai trò quan trọng (Promoters, Amplifiers, Curators...).
4. **Phân tích quan điểm (Sentiment Analysis)**: Xác định xem ý kiến là tích cực (positive), tiêu cực (negative) hay trung tính (neutral). Giúp đánh giá thái độ của khách hàng đối với sản phẩm/dịch vụ.
5. **Giám sát sự kiện (Event Monitoring)**: Nhận diện, nắm bắt các luồng thông tin, sự kiện nóng, các chủ đề nổi bật từ đó có biện pháp xử lý kịp thời.

---

## Chương 2: Mô hình hóa và Biểu diễn Mạng xã hội

### 2.1. Xác định và Mô hình hóa Mạng xã hội (MXH)
Trong phân tích mạng xã hội, ta xem xét mạng xã hội như là một đồ thị mạng bao gồm các đỉnh (nodes) và các cạnh (links).
Mô hình hóa MXH là một đồ thị gồm các thành phần: $SN = (V, E, L(V), L(E))$
- **V (Tập đỉnh)**: Tập các nút (nodes, vertices, agents, actors, players,...). Trong mạng xã hội, đỉnh được xem như là các tác nhân (actors) hay thực thể (entities).
- **E (Tập cạnh)**: Tập các cạnh (edges, links, ties) nối giữa các tập đỉnh, đại diện cho mối quan hệ giữa các thực thể.
- **L(V)**: Nhãn đỉnh.
- **L(E)**: Nhãn cạnh.

**Phân loại tập cạnh**:
- **Đồ thị có hướng (Directed Graph)**: Cạnh dạng trực tiếp, được biểu diễn bằng đường thẳng có hướng (mũi tên). Thể hiện mối quan hệ một chiều.
- **Đồ thị vô hướng (Undirected Graph)**: Cạnh dạng gián tiếp, biểu diễn bằng đường thẳng vô hướng. Thể hiện mối quan hệ hai chiều.

### 2.2. Mức độ quan hệ (Tie Strength)
Ngoài ra, đối với đồ thị, một thành phần quan trọng là **trọng số của cạnh (Weight)**. Trọng số của cạnh được định nghĩa là đơn vị dùng để xác định mức độ hay tần suất liên kết giữa 2 đỉnh trong đồ thị.
- Tần số tương tác.
- Lượng thông tin trao đổi.
- Cạnh/Liên kết biểu diễn quan hệ $\rightarrow$ trọng số cạnh.

### 2.3. Các cách biểu diễn đồ thị
Có 4 cách chính để biểu diễn đồ thị trên máy tính:
1. **Ma trận kề (Adjacency Matrix)**: Dùng mảng 2 chiều để lưu trữ.
2. **Danh sách cạnh (Edge List)**: Liệt kê tất cả các cạnh.
3. **Danh sách kề (Adjacency List)**: Mỗi đỉnh lưu danh sách các đỉnh kề nó.
4. **Ma trận liên thuộc (Incidence Matrix)**.

**Phân tích ma trận kề**:
- **Mạng quan hệ có hướng**: Ma trận kề thường **không đối xứng**.
- **Mạng quan hệ vô hướng**: Ma trận kề luôn **đối xứng**.
- **Mạng có trọng số**: Các phần tử trong ma trận kề chứa giá trị trọng số thay vì chỉ 0 (không có cạnh) và 1 (có cạnh).

### 2.4. Các loại đồ thị (Types of graphs)
- **Tree**: Cây.
- **Directed acyclic graph (DAG)**: Đồ thị có hướng không có chu trình.
- **Bipartite graph**: Đồ thị hai phía.
- **Complete graph**: Đồ thị đầy đủ (tất cả các cặp đỉnh đều có cạnh nối).

### 2.5. Các đặc trưng cơ bản (Fundamental objects)
- **Bậc của đỉnh (Degree)**: Tổng số cạnh liên kết với đỉnh đó (đối với đồ thị vô hướng).
- Đối với đồ thị có hướng, bậc của đỉnh chia thành:
  - **Bậc vào (In-Degree)**: Số cạnh hướng vào đỉnh.
  - **Bậc ra (Out-Degree)**: Số cạnh hướng ra khỏi đỉnh.
- **Đồ thị liên thông vô hướng**: Từ một đỉnh bất kỳ có thể đi đến tất cả các đỉnh còn lại.
- **Đồ thị liên thông có hướng**: Liên thông mạnh (đường đi có hướng giữa mọi cặp đỉnh) và liên thông yếu (liên thông khi bỏ qua hướng của cạnh).

### 2.6. Mật độ mạng (Network Density)
Mật độ mạng là tỷ lệ giữa số cạnh có trên đồ thị với tất cả số cạnh có thể có (số cạnh tối đa).
- Số cạnh tối đa trong đồ thị có hướng ($N$ đỉnh): $L_{max} = N(N-1)$
- Số cạnh tối đa trong đồ thị vô hướng: $L_{max} = \frac{N(N-1)}{2}$
- Mật độ đồ thị: 
$$d(G) = \frac{L}{L_{max}}$$
*(Trong đó $L$ là số cạnh thực tế hiện có trong đồ thị)*

### 2.7. Đặc tính của một số mạng thực tế
| Network (Mạng) | Directed (Có hướng) | Weighted (Trọng số) | Multigraph (Đa đồ thị) | Self-loops (Vòng lặp) |
|---|---|---|---|---|
| WWW | Yes | No | Yes | Yes |
| Protein interactions | No | No | No | Yes |
| Collaboration network | No | Yes | Yes | No |
| Mobile phone calls | Yes | Yes | No | No |
| Facebook Friendship | No | No | No | No |

---

## Chương 3: Các đặc trưng mạng (Network Characteristics)

### 3.1. Các phương pháp đo lường mạng (Network Measurement)
Để đo lường và đánh giá các đặc trưng của mạng, ta thường sử dụng các thông số sau:
- **Phân bố đỉnh (Degree Distribution)**: Kí hiệu là $P(k)$.
- **Chiều dài đường đi (Path length)**: Kí hiệu là $h$.
- **Hệ số phân cụm (Clustering Coefficient)**: Kí hiệu là $C$.

### 3.2. Phân bố đỉnh (Degree Distribution)
Phân bố đỉnh $P(k)$ là xác suất ngẫu nhiên chọn một đỉnh trong mạng và đỉnh đó có bậc là $k$.
Gọi $N_k$ là số lượng các đỉnh có bậc là $k$. Tổng số đỉnh trong đồ thị là $N$.
Công thức chuẩn hóa (Histogram):
$$P(k) = \frac{N_k}{N}$$

**a. Phân bố đỉnh cho đồ thị vô hướng (Undirected Graph)**
Bậc trung bình (Average degree) của một đồ thị vô hướng có $N$ đỉnh và $L$ cạnh được tính bằng:
$$\langle k \rangle = \frac{\sum_{i=1}^N \text{deg}(i)}{N} = \frac{2L}{N}$$

**b. Phân bố đỉnh cho đồ thị có hướng (Directed Graph)**
Đối với đồ thị có hướng, ta xét bậc vào (Indegree) và bậc ra (Outdegree).
- Bậc vào (Indegree): Số lượng các liên kết trỏ đến đỉnh $i$.
- Bậc ra (Outdegree): Số lượng các liên kết xuất phát từ đỉnh $i$.
*(Lưu ý: Mỗi một vòng lặp (self-loop) sẽ cộng thêm 1 vào bậc vào và 1 vào bậc ra của đỉnh đó).*
Bậc trung bình (Average degree) của đồ thị có hướng:
$$\langle k^{in} \rangle = \langle k^{out} \rangle = \frac{\sum \text{indeg}(i)}{N} = \frac{\sum \text{outdeg}(i)}{N} = \frac{L}{N}$$

### 3.3. Đường đi (Path)
Đường đi là một chuỗi các đỉnh trong đó mỗi đỉnh được liên kết với đỉnh tiếp theo.
- Đường đi có thể tự cắt ngang và đi qua một cạnh nhiều lần.
- Trong đồ thị có hướng, đường đi phải tuân theo chiều của mũi tên.

### 3.4. Hệ số phân cụm (Clustering Coefficient)
Hệ số phân cụm đo lường mức độ các đỉnh hàng xóm của một đỉnh $i$ kết nối (liên kết) với nhau. Nói cách khác, "Bao nhiêu phần trăm bạn bè của bạn cũng là bạn bè của nhau?".

Cho một đỉnh $i$ có bậc là $k_i$. Hệ số phân cụm của đỉnh $i$, kí hiệu là $C_i$ (với $C_i \in [0,1]$), được tính bằng công thức:
$$C_i = \frac{2e_i}{k_i(k_i - 1)}$$
Trong đó:
- $k_i$ là bậc của đỉnh $i$ (số lượng hàng xóm của đỉnh $i$).
- $e_i$ là số lượng các cạnh thực tế tồn tại giữa các hàng xóm của đỉnh $i$.
- Dạng tổng quát của mẫu số $\frac{k_i(k_i - 1)}{2}$ chính là số lượng cạnh tối đa có thể có giữa $k_i$ hàng xóm.

### 3.5. Cấu trúc cộng đồng (Community Structure)
Các đỉnh trong mạng thường có xu hướng liên kết với nhau tạo thành các nhóm chặt chẽ (tightly knit groups). Giữa các nhóm này thường chỉ tồn tại các kết nối lỏng lẻo, thưa thớt (looser connections).

---

## Chương 4: Độ đo Trung tâm (Centrality Measures) & Tầm ảnh hưởng (Key Players)

### 4.1. Tổng quan về Độ đo Trung tâm (Centrality)
Centrality là các biện pháp nhằm xác định tầm quan trọng tương đối của một đỉnh (node) trong một đồ thị mạng. Việc xác định các đỉnh quan trọng giúp phân tích sự lan truyền thông tin, xác định người có tầm ảnh hưởng (influencers) và phân tích tính liên kết của toàn bộ mạng.

Các loại độ đo trung tâm phổ biến:
1. Độ đo trung tâm theo bậc (Degree Centrality).
2. Độ đo trung tâm dựa trên trung gian (Betweenness Centrality).
3. Độ đo trung tâm theo sự lân cận (Closeness Centrality).
4. Độ đo trung tâm điều hòa (Harmonic Centrality).
5. Độ đo trung tâm Eigenvector (Eigenvector Centrality).
6. PageRank.

### 4.2. Độ đo Trung tâm theo Bậc (Degree Centrality)
Độ đo này xác định tầm quan trọng của một đỉnh dựa trên số lượng liên kết trực tiếp tới đỉnh đó.
- Công thức: $C_D(v) = deg(v)$
- Công thức chuẩn hóa: $C'_D(v) = \frac{deg(v)}{n-1}$ (với $n$ là số đỉnh của đồ thị).
- **Ý nghĩa**: Đỉnh có Degree Centrality cao là đỉnh hoạt động tích cực, có nhiều mối quan hệ, thu hút nhiều sự quan tâm. Đỉnh này có khả năng lan truyền thông tin nhanh đến những đỉnh lân cận.

### 4.3. Độ đo Trung tâm dựa trên Trung gian (Betweenness Centrality)
Đại lượng này đo mức độ một đỉnh đóng vai trò là "cầu nối" dọc theo các đường đi ngắn nhất giữa các cặp đỉnh khác.
- Đặt $\sigma_{st}$ là tổng số đường đi ngắn nhất giữa $s$ và $t$. $\sigma_{st}(v)$ là số đường đi ngắn nhất giữa $s$ và $t$ mà đi qua $v$.
- Khả năng tham gia vào mối liên lạc: $\delta_{st}(v) = \frac{\sigma_{st}(v)}{\sigma_{st}}$
- Công thức Betweenness Centrality của đỉnh $v$: 
$$C_B(v) = \sum_{s \neq v \neq t \in V} \delta_{st}(v)$$
- Công thức chuẩn hóa (cho đồ thị vô hướng): Chia $C_B(v)$ cho $\frac{(n-1)(n-2)}{2}$.
- **Ý nghĩa**: Một đỉnh có Betweenness Centrality cao có tầm ảnh hưởng lớn trong mạng, đóng vai trò kiểm soát luồng thông tin. Nếu loại bỏ nút này, sự giao tiếp trong mạng có thể bị chia cắt thành nhiều phần.

### 4.4. Độ đo Trung tâm theo sự Lân cận (Closeness Centrality)
Đo lường khoảng cách từ một đỉnh đến tất cả các đỉnh còn lại trong đồ thị.
- Đặt $d(u,v)$ là khoảng cách đường đi ngắn nhất từ đỉnh $u$ đến đỉnh $v$.
- Công thức:
$$C_C(u) = \frac{1}{\sum_{v=1}^{n-1} d(u,v)}$$
- Công thức chuẩn hóa:
$$C'_C(u) = \frac{n-1}{\sum_{v=1}^{n-1} d(u,v)}$$
- **Ý nghĩa**: Đỉnh có Closeness Centrality lớn nhất (hoặc đường đi ngắn nhất trung bình nhỏ nhất) có thể truyền đạt và tiếp nhận thông tin từ các đỉnh khác trong mạng một cách nhanh nhất.

### 4.5. Độ đo Trung tâm Điều hòa (Harmonic Centrality)
Là trung bình điều hòa của đường đi ngắn nhất từ một đỉnh đến tất cả các đỉnh khác.
- Công thức:
$$CH(i) = \frac{1}{n-1} \sum_{j \neq i} \frac{1}{d_{ij}}$$

### 4.6. Độ đo Trung tâm Eigenvector (Eigenvector Centrality)
Gán điểm số (trọng số) cho các nút trong mạng dựa trên nguyên tắc: "Kết nối tới một node có điểm số cao sẽ đóng góp nhiều điểm hơn so với kết nối tới một node có điểm số thấp".
- Biểu diễn bằng phương trình: $Ax = \lambda x$
*(Trong đó $A$ là ma trận kề, $\lambda$ là giá trị riêng (eigenvalue), $x$ là vector riêng (eigenvector) chứa điểm số tương ứng của các đỉnh).*

### 4.7. PageRank Centrality
PageRank đánh giá độ quan trọng của một trang web (hay một node) dựa trên tần suất một người dùng ngẫu nhiên lướt đến đó.
- Công thức:
$$PR(x) = \frac{1-\alpha}{N} + \alpha \left( \sum_{k=1}^n \frac{PR(k)}{C(k)} \right)$$
*(Trong đó $\alpha$ là Damping factor - thường chọn bằng 0.85, $N$ là tổng số đỉnh, $PR(k)$ là PageRank của đỉnh kề hướng vào $x$, $C(k)$ là bậc ra của đỉnh $k$).*

### 4.8. Ứng dụng tìm Tác nhân chính (Key Player)
Nghiên cứu của Stephen Borgatti chia bài toán Key Player thành 2 dạng:
- **KPP-1**: Tìm một tập $k$ đỉnh mà nếu loại bỏ sẽ làm gián đoạn tối đa việc giao tiếp giữa các nút còn lại (Làm phân mảnh mạng). Độ đo Betweenness được sử dụng cho bài toán này.
- **KPP-2**: Tìm một tập $k$ đỉnh có khả năng lan truyền thông tin ưu việt nhất qua mạng. Độ đo Degree và Closeness được sử dụng.

**Quy trình tìm phần tử chính yếu (Key Player)**:
1. **Bước 1**: Tìm tất cả các đường đi ngắn nhất từ 1 đỉnh đến tất cả các đỉnh còn lại trong đồ thị (Dùng thuật toán BFS).
2. **Bước 2**: Tính độ đo trung tâm theo bậc (Degree Centrality) cho từng đỉnh.
3. **Bước 3**: Tính độ đo trung tâm trung gian (Betweenness Centrality).
4. **Bước 4**: Tính độ đo trung tâm theo sự lân cận (Closeness Centrality).
5. **Bước 5**: Tổng hợp và so sánh các độ đo để kết luận đỉnh (hoặc tập đỉnh) là Key Player.

---

## Chương 5: Khám phá Cộng đồng (Community Detection)

### 5.1. Giới thiệu về Cộng đồng (Community)
- **Khái niệm**: Cộng đồng trong mạng là tập các thực thể (đỉnh) có những tính chất tương tự nhau và/hoặc cùng đóng một vai trò nào đó trong mạng xã hội. Các đỉnh trong một cộng đồng thường có liên kết nội bộ dày đặc (densely linked), trong khi liên kết giữa các cộng đồng lại thưa thớt.
- **Mục tiêu**: Từ đồ thị mạng xã hội cho trước, thuật toán cần phát hiện được các cấu trúc cộng đồng, từ đó phân tích mối liên hệ bên trong và giữa các cộng đồng với nhau.
- **Ứng dụng**: Phân cụm đối tượng khách hàng chung sở thích, gom nhóm Web Client có vị trí địa lý gần nhau để tối ưu hóa truy xuất, xác định các hội nhóm trên mạng xã hội, v.v.

### 5.2. Các hướng tiếp cận Phân hoạch Đồ thị (Graph Partitioning)
Việc chia cắt đồ thị để tìm các cụm có thể đi theo 2 hướng chính:
1. **Divisive methods (Phương pháp phân chia/Từ trên xuống)**: Lặp đi lặp lại việc xác định và loại bỏ các cạnh kết nối giữa các vùng dày đặc. (Cắt các kết nối lỏng lẻo).
2. **Agglomerative methods (Phương pháp gộp/Từ dưới lên)**: Lặp đi lặp lại việc xác định và gộp các đỉnh có liên kết mạnh, có khả năng thuộc về cùng một vùng lại với nhau.

### 5.3. Thuật toán Girvan-Newman
Đây là một phương pháp **Divisive method** nổi tiếng để khám phá cộng đồng, được đề xuất bởi Girvan và Newman (2002).

**Độ đo trung gian của cạnh (Edge Betweenness)**:
- Edge Betweenness của một cạnh là số lượng các đường đi ngắn nhất giữa tất cả các cặp đỉnh trong đồ thị đi qua cạnh đó.
- Ý tưởng: Các cạnh nối giữa 2 cộng đồng tách biệt (weak ties) sẽ có giá trị Edge Betweenness rất cao, bởi vì tất cả các đường đi ngắn nhất từ một đỉnh ở mô-đun này sang đỉnh ở mô-đun kia đều phải đi qua cạnh đó.

**Các bước của thuật toán Girvan-Newman** (Áp dụng cho đồ thị vô hướng):
1. **Bước 1**: Tính toán giá trị Edge Betweenness cho tất cả các cạnh trong đồ thị.
2. **Bước 2**: Tìm cạnh có giá trị Edge Betweenness cao nhất và loại bỏ nó khỏi đồ thị. (Nếu có nhiều cạnh có cùng giá trị lớn nhất, ta loại bỏ tất cả chúng).
3. **Bước 3**: Việc loại bỏ cạnh có thể làm đồ thị bị chia cắt thành nhiều thành phần liên thông nhỏ hơn. Tính toán lại Edge Betweenness cho tất cả các cạnh còn lại của đồ thị mới.
4. **Bước 4**: Lặp lại Bước 2 và Bước 3 cho đến khi không còn cạnh nào trong đồ thị (hoặc cho đến khi đồ thị được phân rã thành số cụm mong muốn).

**Đặc điểm**:
- Kết quả của quá trình là một bản đồ phân cấp dạng cây (Dendrogram). Trong đó, lá của cây là các đỉnh riêng lẻ, gốc của cây đại diện cho toàn bộ đồ thị.
- Thuật toán này chỉ cung cấp chuỗi phân tách liên tiếp các cộng đồng, nhưng không chỉ ra được điểm phân tách nào là "tốt nhất" để quyết định số lượng cộng đồng. Để tìm điểm phân tách tốt nhất, người ta sử dụng khái niệm **Tính mô-đun (Modularity)**.

---

## Chương 6: Đánh giá của người dùng trong dữ liệu mạng xã hội và Mạng có dấu

### 6.1. Đánh giá của người dùng (User-User Evaluations)
Trên mạng xã hội, người dùng thường xuyên thể hiện các đánh giá tích cực hoặc tiêu cực đối với người khác hoặc nội dung của họ. Việc đánh giá có thể được thể hiện qua hành động (Like, Vote, Trust) hoặc qua văn bản (Comment, Review).
Có 2 yếu tố chính thúc đẩy đánh giá của con người:
1. **Status (Địa vị/Trạng thái)**: Mức độ được công nhận, thành tựu, danh tiếng trong cộng đồng (Ví dụ: số bài đăng, số huy hiệu).
2. **Similarity (Sự tương đồng)**: Sự chia sẻ sở thích, quan điểm giữa người đánh giá (A) và người được đánh giá (B).

**Đánh giá tuyệt đối vs Đánh giá tương đối**:
- **Tuyệt đối**: Người A đánh giá dựa hoàn toàn vào đặc điểm của người B.
- **Tương đối**: Người A so sánh bản thân với B trước khi đưa ra đánh giá. Thực tế chứng minh đánh giá mang tính chất tương đối nhiều hơn. Việc đánh giá phụ thuộc vào sự chênh lệch địa vị $\Delta = S_A - S_B$. Khi sự chênh lệch quá lớn, ta có thể thấy hiện tượng "Mercy Bounce" (Cú nảy xót xa), nơi xác suất đánh giá tích cực tăng lên một chút do sự đồng cảm của những người có độ tương đồng với nhau.

### 6.2. Mạng có dấu (Signed Networks)
Thay vì chỉ thể hiện việc có kết nối hay không, các liên kết trong mạng có thể mang ý nghĩa tích cực (+) hoặc tiêu cực (-).
- **Cạnh dương (+)**: Thể hiện tình bạn, sự tin tưởng, liên minh, đánh giá tích cực.
- **Cạnh âm (-)**: Thể hiện sự thù địch, không tin tưởng, phản đối, đánh giá tiêu cực.

### 6.3. Thuyết cân bằng cấu trúc (Theory of Structural Balance)
Xuất phát từ nguyên lý tâm lý học xã hội của Fritz Heider (1946):
- "Bạn của bạn là bạn của tôi." (+)
- "Kẻ thù của kẻ thù là bạn của tôi." (+)
- "Kẻ thù của bạn là kẻ thù của tôi." (-)

**Đánh giá tính cân bằng trên một bộ 3 đỉnh (Triad)**:
Xét một đồ thị đầy đủ gồm 3 đỉnh, mạng lưới được gọi là cân bằng (Balanced) nếu:
- Cả 3 cạnh đều mang dấu (+) (3 người đều là bạn).
- Có đúng 1 cạnh mang dấu (+) và 2 cạnh mang dấu (-) (2 người là bạn, cùng chung kẻ thù là người thứ 3).
Mạng lưới bị mất cân bằng (Unbalanced) nếu:
- Cả 3 cạnh đều mang dấu (-) (Không ai ưa ai, tạo ra sự căng thẳng).
- Có đúng 2 cạnh mang dấu (+) và 1 cạnh mang dấu (-) (2 người bạn của 1 người lại là kẻ thù của nhau).

**Định lý Cartwright-Harary (Từ cục bộ đến toàn cục)**:
Nếu tất cả các bộ 3 đỉnh (tam giác) trong mạng đều cân bằng, thì mạng lưới lớn đó có tính chất:
1. Hoặc là toàn bộ mạng lưới chỉ chứa các cạnh dương (+).
2. Hoặc mạng có thể được phân tách thành đúng 2 nhóm (2 liên minh / phe phái), sao cho mọi liên kết bên trong một nhóm đều là dương (+), và mọi liên kết giữa 2 nhóm đều là âm (-).

### 6.4. Thuật toán kiểm tra mạng có cân bằng hay không
Một đồ thị mạng có dấu là cân bằng khi và chỉ khi nó không chứa chu trình có độ dài lẻ gồm toàn các cạnh âm. Các bước kiểm tra:
1. **Bước 1**: Tìm các thành phần liên thông tạo bởi các cạnh dương (+).
   - Nếu trong một thành phần liên thông dương lại chứa một cạnh âm (-), ta kết luận ngay mạng **không cân bằng**.
2. **Bước 2**: Gộp các đỉnh trong mỗi thành phần liên thông dương thành một siêu đỉnh (Super-node).
3. **Bước 3**: Kết nối 2 siêu đỉnh $A$ và $B$ bằng một cạnh âm (-) nếu có bất kỳ cạnh âm nào giữa một thành viên của $A$ và một thành viên của $B$. Đồ thị thu được gọi là đồ thị thu gọn (Reduced Graph).
4. **Bước 4**: Sử dụng thuật toán BFS trên đồ thị thu gọn để gán các siêu đỉnh vào 2 phe phân biệt (ví dụ: Trái - Phải). Nếu có bất kỳ 2 siêu đỉnh nào có kết nối với nhau mà bị gán vào cùng một phe, mạng lưới là **không cân bằng**. Ngược lại là **cân bằng**.

---

## Chương 7: Dự đoán liên kết (Link Prediction)

### 7.1. Giới thiệu bài toán Dự đoán liên kết
Bài toán dự đoán liên kết là: Cho trước cấu trúc của một mạng xã hội tại thời điểm hiện tại, dự đoán những liên kết (cạnh) mới nào có khả năng sẽ hình thành trong tương lai, hoặc suy luận ra những liên kết hiện đang tồn tại nhưng bị thiếu do không quan sát được.
- **Trực giác**: Trong mạng xã hội, hai đỉnh "gần gũi" về mặt khoảng cách mạng sẽ có xác suất cao kết nối với nhau (Ví dụ: hai người có nhiều bạn chung).

### 7.2. Dự đoán liên kết dựa vào độ tương đồng (Similarity-based heuristics)
Phương pháp cơ bản nhất là tính toán một điểm số tương đồng $S_{xy}$ cho mỗi cặp đỉnh $(x, y)$ chưa có kết nối. Mọi cặp chưa có kết nối được xếp hạng theo $S_{xy}$ giảm dần, những cặp có điểm cao nhất được dự đoán sẽ xuất hiện liên kết.

**A. Các độ tương đồng cục bộ (Local link prediction heuristics)**
Các độ đo này chỉ sử dụng thông tin của tập láng giềng kề trực tiếp với hai đỉnh. Gọi $\Gamma(x)$ là tập các đỉnh kề (láng giềng) của $x$, $k_x = |\Gamma(x)|$ là bậc của $x$.
1. **Common Neighbors (CN)**: Số lượng bạn chung. $CN(x,y) = |\Gamma(x) \cap \Gamma(y)|$
2. **Jaccard (JC)**: Tỷ lệ bạn chung trên tổng số bạn. $JC(x,y) = \frac{|\Gamma(x) \cap \Gamma(y)|}{|\Gamma(x) \cup \Gamma(y)|}$
3. **Adamic-Adar (AA)**: Đánh trọng số cho bạn chung; bạn chung có ít mối quan hệ (bậc thấp) được đánh giá cao hơn. $AA(x,y) = \sum_{z \in \Gamma(x) \cap \Gamma(y)} \frac{1}{\log(k_z)}$
4. **Preferential Attachment (PA)**: Người có nhiều bạn dễ kết nối với nhau. $PA(x,y) = k_x \times k_y$
5. **Salton (Cosine Similarity)**: $Salton(x,y) = \frac{|\Gamma(x) \cap \Gamma(y)|}{\sqrt{k_x \times k_y}}$
6. **Sørensen**: $Sørensen(x,y) = \frac{2|\Gamma(x) \cap \Gamma(y)|}{k_x + k_y}$
7. **Hub Promoted Index (HPI)**: $HPI(x,y) = \frac{|\Gamma(x) \cap \Gamma(y)|}{\min(k_x, k_y)}$
8. **Hub Depressed Index (HDI)**: $HDI(x,y) = \frac{|\Gamma(x) \cap \Gamma(y)|}{\max(k_x, k_y)}$
9. **Leicht-Holme-Newman (LHN1)**: $LHN1(x,y) = \frac{|\Gamma(x) \cap \Gamma(y)|}{k_x \times k_y}$
10. **Resource Allocation (RA)**: Tương tự AA nhưng không dùng logarit. $RA(x,y) = \sum_{z \in \Gamma(x) \cap \Gamma(y)} \frac{1}{k_z}$

**B. Các độ tương đồng toàn cục (Global link prediction heuristics)**
Sử dụng thông tin của toàn bộ cấu trúc mạng lưới.
1. **Katz Score**: Tính tổng số lượng đường đi có chiều dài $l$ giữa $x$ và $y$, trong đó đường đi càng dài thì trọng số $\beta^l$ (penalty) càng nhỏ.
   $$S_{xy}^{Katz} = \sum_{l=1}^{\infty} \beta^l \cdot |paths_{xy}^{\langle l \rangle}|$$
2. **Hitting Time**: Thời gian kỳ vọng để một người đi dạo ngẫu nhiên (Random walk) từ đỉnh $x$ chạm tới đỉnh $y$.

### 7.3. Dự đoán liên kết dựa vào các mô hình xác suất
Thay vì dùng trực tiếp các độ đo heuristics, mô hình xác suất tiến hành học các tham số để diễn đạt phân phối xác suất hình thành liên kết.
- **Các mô hình điển hình**: Mô hình quan hệ xác suất (PRM) sử dụng Mạng Bayes (RBNs), Mạng Markov (RMNs), hoặc Mạng quan hệ phụ thuộc (RDNs - sử dụng phương pháp Pseudo-likelihood).
- Việc suy luận dựa trên cấu trúc của tập dữ liệu huấn luyện, giải quyết bài toán qua các thuộc tính của thực thể và quan hệ.

### 7.4. Dự đoán dấu của liên kết (Predicting Edge Signs)
Trong mạng có dấu (Signed Networks), khi biết có liên kết tồn tại giữa 2 đỉnh, bài toán đặt ra là dự đoán xem liên kết đó mang dấu (+) hay (-).
- **Phương pháp học máy**: Phân loại nhị phân (Binary Classification) với nhãn +1 và -1. Các thuật toán như Logistic Regression có thể được sử dụng.
- **Đặc trưng (Features) sử dụng**: 
  - *Node degree features*: Số lượng cạnh âm/dương ra/vào của 2 đỉnh.
  - *Triad features*: Số lượng các loại tam giác (cân bằng/mất cân bằng) mà liên kết đó tham gia tạo thành.
- **Kết nối với Lý thuyết xã hội**:
  - Bài toán này có thể được giải thích thông qua **Thuyết cân bằng cấu trúc** (Structural Balance) và **Lý thuyết địa vị** (Theory of Status). 
  - Trong *Theory of Status*, liên kết $u \xrightarrow{+} v$ ngụ ý $v$ có địa vị cao hơn $u$, trong khi $u \xrightarrow{-} v$ ngụ ý $v$ có địa vị thấp hơn $u$. Việc kết hợp 2 lý thuyết xã hội này giúp các mô hình Machine Learning dự đoán tính chất của cạnh với độ chính xác cao.

---

## Phần Ôn tập: Các trọng tâm kiến thức của môn học
Dưới đây là danh sách tổng hợp các chủ đề và từ khóa quan trọng cốt lõi cần nắm vững trong toàn bộ học phần Mạng xã hội:

### 1. Lý thuyết Đồ thị cơ bản
- Các khái niệm cơ bản: Bậc (Degree), Cạnh (Edge), Ma trận kề (Adjacency Matrix).
- Phân loại đồ thị: Đồ thị vô hướng (Undirected), có hướng (Directed), đồ thị có trọng số (Weighted).
- Các dạng đồ thị đặc biệt: Đồ thị đầy đủ (Complete graph), Đồ thị hai phía (Bipartite graph).
- Đồ thị ngẫu nhiên $G_{n,p}$: Đồ thị có $n$ đỉnh, xác suất tồn tại cạnh giữa 2 đỉnh là $p$. Số lượng cạnh kỳ vọng.
- Các bài toán trên đồ thị: Tìm đường đi ngắn nhất (Shortest Path), Công thức tính số cạnh tối đa cho mạng lưới $n$ đỉnh $\frac{n(n-1)}{2}$, Thuật toán duyệt cây BFS và DFS.

### 2. Các hệ số đo trung tâm và đặc tính mạng
- Mức độ liên kết cục bộ: Hệ số cụm của đỉnh (Clustering coefficient), Hệ số cụm trung bình của toàn đồ thị.
- Mức độ kết nối toàn cục: Khoảng cách, Đường kính (Diameter).
- Các độ đo trung tâm (Centrality measures):
  - Degree Centrality (Trung tâm bậc)
  - Betweenness Centrality (Trung tâm trung gian)
  - Closeness Centrality (Trung tâm gần gũi)
  - Harmonic Centrality
  - Eigenvector Centrality (Trung tâm vector riêng)
  - PageRank

### 3. Bài toán Khám phá cộng đồng (Gom cụm - Community Detection)
- Các thuật toán trọng tâm:
  - Thuật toán **Girvan-Newman**: Dựa trên việc tính toán và loại bỏ dần các cạnh có Edge Betweenness cao nhất. (Nắm vững phương pháp tính Edge Betweenness thông thường và phương pháp tính hiệu quả qua BFS).
  - Thuật toán **Louvain**: Tối ưu hóa tính mô-đun (Modularity) qua phương pháp agglomerative.

### 4. Dự đoán liên kết trong Mạng xã hội (Link Prediction)
- Cơ sở lý thuyết xã hội: Lý thuyết cân bằng cấu trúc (Theory of Structural Balance), Lý thuyết trạng thái/địa vị (Theory of Status).
- Dự đoán liên kết sử dụng các độ đo tương đồng cục bộ (Local similarities):
  - Common Neighbors (CN)
  - Jaccard (JC)
  - Adamic-Adar (AA)
  - Preferential Attachment (PA)

### 5. Sự lan truyền trên mạng (Information Diffusion) (*)
- Nắm vững khái niệm về tiến trình lan truyền thông tin (diffusion process) trên mạng xã hội.
- Mô hình lan truyền dịch bệnh / thông tin: **Mô hình SIR** (Susceptible - Infected - Recovered).
*(Ghi chú: Chủ đề này được đề cập trong trọng tâm ôn tập, yêu cầu sinh viên có kiến thức tổng quan về các trạng thái S, I, R và sự chuyển đổi giữa chúng trong mạng lưới).*

---
**[KẾT THÚC TÀI LIỆU TỔNG HỢP KIẾN THỨC MÔN HỌC MẠNG XÃ HỘI]**
