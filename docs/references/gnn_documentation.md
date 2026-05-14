# Tổng hợp kiến thức gốc về Graph Neural Networks liên quan đến đề tài Variable Misuse

## 1. Phạm vi và nguyên tắc tổng hợp

Tài liệu này chỉ tổng hợp lại kiến thức có trong tài liệu gốc _Graph Neural Networks: Foundations, Frontiers, and Applications_ và đối chiếu với yêu cầu bắt buộc trong `docs/references/base/instruction.md`. Nội dung không triển khai thêm đề xuất riêng ngoài tài liệu gốc hoặc ngoài yêu cầu của file hướng dẫn đồ án.

Các phần gốc được chọn vì có liên quan trực tiếp đến đề tài:

- Chương 22 - **Graph Neural Networks in Program Analysis**: nguồn chính, có phần **Case Study: Detecting Variable Misuse Bugs**.
- Chương 3 - **Graph Neural Networks**: tổng quan GNN, các hướng nền tảng như node classification, expressive power, scalability, interpretability, robustness.
- Chương 4 - **Graph Neural Networks for Node Classification**: nền tảng node representation, supervised GNN, GCN, GAT, message passing, over-smoothing.
- Chương 5 - **The Expressive Power of Graph Neural Networks**: message passing GNN, giới hạn biểu diễn, 1-WL, distance/higher-order attributes.
- Chương 6 - **Graph Neural Networks: Scalability**: vấn đề mở rộng và các kiểu sampling.
- Chương 7 - **Interpretability in Graph Neural Networks**: giải thích node, edge, feature quan trọng.
- Chương 8 - **Graph Neural Networks: Adversarial Robustness**: độ bền trước thay đổi nhỏ trên graph.
- Chương 14 - **Graph Structure Learning**: học/cải thiện cấu trúc graph.
- Chương 16 - **Heterogeneous Graph Neural Networks**: graph có nhiều loại node/cạnh.
- Chương 18 - **Graph Neural Networks: Self-supervised Learning**: học tự giám sát khi thiếu nhãn.

Ghi chú đối chiếu với hướng dẫn đồ án: `instruction.md` yêu cầu bài toán **Graph Neural Networks in Program Analysis - Detecting Variable Misuse Bugs**, trong đó dữ liệu được biểu diễn bằng AST và các cạnh đặc biệt như `LastUse`, `LastWrite`, `ComputedFrom`; mô hình hướng đến GGNN; đánh giá bằng localization accuracy, repair accuracy và so sánh AST-only với AST + Data Flow.

## 2. Kiến thức gốc từ Chương 22: Graph Neural Networks in Program Analysis

### 2.1. Program analysis và vai trò của machine learning

Theo Chương 22, program analysis là lĩnh vực xác định các thuộc tính hành vi của chương trình. Các phương pháp truyền thống thường dựa trên lập luận hình thức để chứng minh hoặc bác bỏ một mệnh đề về hành vi chương trình, ví dụ chương trình luôn thỏa một điều kiện, hoặc luôn dừng.

Tuy nhiên, các phương pháp hình thức không học được những mẫu lập trình thường gặp hoặc các tín hiệu mơ hồ trong mã thật, chẳng hạn tên biến, comment, quy ước đặt tên và idiom cú pháp. Machine learning-based program analysis nhắm đến khả năng suy luận xác suất từ các mẫu này. Đổi lại, nó không cung cấp bảo đảm tuyệt đối như formal methods.

Chương 22 phân biệt một số dạng dùng machine learning trong program analysis:

- **Specification tuning**: dùng machine learning để tinh chỉnh hoặc hậu xử lý một phân tích hình thức, giảm false positives nhưng có thể giảm recall/soundness.
- **Specification inference**: học dự đoán một specification hợp lý từ code có sẵn, rồi dùng specification đó cho các phân tích truyền thống.
- **Black-box analysis learning**: mô hình machine learning trực tiếp thực hiện phân tích và đưa cảnh báo mà không tạo ra một specification tường minh. Variable misuse detection thuộc nhóm này.

### 2.2. Vì sao graph phù hợp với program analysis

Chương 22 nhấn mạnh rằng nhiều phương pháp program analysis truyền thống vốn đã dùng biểu diễn graph, chẳng hạn:

- syntax tree,
- control flow graph,
- data flow graph,
- program dependence graph,
- call graph.

Một chương trình có thể được xem như tập các thực thể không đồng nhất liên hệ với nhau bằng nhiều loại quan hệ. Vì vậy, chương trình có thể ánh xạ thành một **heterogeneous directed graph** `G = (V, E)`, trong đó mỗi thực thể là node, còn mỗi quan hệ kiểu `r` là edge `(vi, r, vj)`.

Hai điểm khác với knowledge graph thông thường:

- node và edge có thể được trích xuất xác định từ source code và artifact của chương trình;
- thường có một graph cho mỗi program hoặc code snippet.

Chương 22 cũng nhấn mạnh không có một cách duy nhất hoặc được chấp nhận rộng rãi để chuyển chương trình thành graph. Việc chọn node/edge là một dạng feature engineering và phụ thuộc nhiệm vụ. Các biểu diễn khác nhau đánh đổi giữa khả năng biểu diễn thuộc tính chương trình, kích thước graph và chi phí tạo graph.

### 2.3. Program graph trong Chương 22

Chương 22 trình bày một biểu diễn graph lấy cảm hứng từ Allamanis et al. (2018b), trong đó mỗi source code file được mô hình hóa như một graph. Biểu diễn này gồm các nhóm node và edge chính sau.

#### Tokens

Source code ban đầu là chuỗi ký tự. Ngôn ngữ lập trình có thể được tokenizer/lexer tách xác định thành chuỗi token. Mỗi token được biểu diễn thành một token node. Các token node được nối bằng cạnh `NextToken` để tạo thành chuỗi tuyến tính.

Ý nghĩa với đề tài: phần này là nguồn gốc cho cạnh `NextToken` được nêu trong `instruction.md`.

#### Syntax

Chuỗi token được parse thành syntax tree. Token là các lá của cây, còn các node còn lại là syntax node. Các syntax node và token được nối bằng cạnh loại `Child` để tạo thành cấu trúc cây.

Cấu trúc syntax cung cấp ngữ cảnh về vai trò cú pháp của token và nhóm token thành expression/statement. Đây là cơ sở cho việc dùng AST trong đề tài.

Ý nghĩa với đề tài: phần này tương ứng với cạnh `Child/Parent` trong `instruction.md`.

#### Symbols

Chương 22 giới thiệu symbol node. Với Python, symbol gồm các biến, hàm, package có sẵn trong một scope. Sau khi parse code, Python tạo symbol table chứa các symbol trong file. Mỗi symbol được tạo một node. Mỗi identifier token hoặc expression node được nối đến symbol node mà nó tham chiếu.

Symbol node đóng vai trò điểm quy chiếu trung tâm giữa các lần sử dụng biến. Chương 22 nêu rõ symbol node hữu ích để mô hình hóa quan hệ xa, ví dụ cách một object/variable được sử dụng qua nhiều vị trí.

Ý nghĩa với đề tài: đây là kiến thức gốc giải thích vì sao variable misuse cần xét các biến trong scope và các lần sử dụng biến.

#### Data Flow

Chương 22 thêm data-flow edges để truyền thông tin về execution. Vì luồng dữ liệu thực tế có thể không xác định do branch, loop, if statement, graph có thể thêm cạnh biểu thị tất cả đường hợp lệ mà dữ liệu có thể chảy qua chương trình.

Trong ví dụ của Chương 22, cạnh `MayNextUse` biểu diễn các lần sử dụng có thể tiếp theo của một giá trị. Chương 22 ghi rằng cách xây dựng này giống với program dependence graph trong compiler và program analysis truyền thống.

Khác với các cạnh deterministic như syntax edge, `MayNextUse` không biểu diễn quan hệ chắc chắn duy nhất. Nó phác thảo các luồng dữ liệu có thể xảy ra trong thực thi.

Ý nghĩa với đề tài: đây là nền tảng gốc cho yêu cầu dùng các cạnh luồng dữ liệu như `LastUse`, `LastWrite`, `ComputedFrom` trong `instruction.md`.

### 2.4. Vì sao đưa node/edge xác định vào graph thay vì để neural network tự học

Chương 22 đặt câu hỏi: nếu chỉ từ token và `NextToken` đã có thể xác định các node/edge khác, vì sao không để neural network tự học? Câu trả lời của tài liệu:

- các graph representation như syntax và data flow có thể trích xuất rẻ bằng compiler/interpreter;
- cung cấp trực tiếp thông tin này giúp mô hình không phải dùng capacity để học lại các sự kiện xác định;
- các node/edge này đưa inductive bias có ích cho program analysis.

Điểm này trực tiếp ủng hộ cách đề tài yêu cầu biểu diễn mã nguồn bằng AST cộng thêm data-flow edges.

### 2.5. Các graph representation thay thế trong Chương 22

Chương 22 nêu rằng biểu diễn ở trên chỉ là một cách. Có các biểu diễn khác:

- Biểu diễn local nhấn mạnh syntax và intraprocedural data flow. Biểu diễn này hữu ích cho variable misuse và type inference trong Chương 22.
- Có thể thêm cạnh `GuardedBy` để chỉ statement bị điều kiện guard.
- Có thể thêm cạnh `SubtokenOf` để nối token với subtoken chung, ví dụ `max_len` và `min_len` cùng có subtoken `len`.
- Có biểu diễn nhấn mạnh data/control flow và bỏ thông tin ngôn ngữ tự nhiên trong identifier/comment, phù hợp với một số compiler analysis nhưng không phải mọi nhiệm vụ.
- Có biểu diễn hypergraph toàn cục nhấn mạnh type constraints toàn chương trình, phù hợp type annotation prediction nhưng Chương 22 nói khó dùng cho variable misuse.
- Có biểu diễn extrinsic kết hợp code với metadata như documentation hoặc Q&A, nhưng Chương 22 nhận xét dạng này không phù hợp với hai program analyses được thảo luận trong chương.

## 3. Kiến thức gốc từ Chương 22: GNN cho program graph

### 3.1. Lý do dùng GNN cho program graph

Chương 22 cho biết trước GNN đã có nhiều cách học từ program graph, ví dụ chiếu graph thành sequence, tree hoặc path. Sequence-based model đơn giản và hiệu quả tính toán, nhưng có thể bỏ lỡ pattern cấu trúc phức tạp như data flow và control flow. Path-based method trích các đường đi từ tree/graph và có thể học một phần thông tin cú pháp/ngữ nghĩa, nhưng vẫn là phép chiếu mất thông tin.

GNN làm việc trực tiếp trên graph, vì vậy có thể dùng đầy đủ hơn các thực thể và quan hệ trong chương trình.

### 3.2. Node representation ban đầu

Theo Chương 22, khi dùng GNN cho program graph:

- mỗi entity/node `vi` được nhúng thành vector ban đầu `nvi`;
- với token node và symbol node, string representation được subtokenize, ví dụ `max_len` thành `max`, `len`;
- vector ban đầu của node có thể được tính bằng pooling embedding của các subtoken;
- với syntax node, trạng thái ban đầu là embedding của loại syntax node.

Đây là kiến thức gốc về việc dùng subtoken và node type trong program graph.

### 3.3. Directed heterogeneous graph và inverse edges

Chương 22 mô tả rằng sau khi có node representation ban đầu, có thể dùng bất kỳ GNN architecture nào xử lý được directed heterogeneous graph để tính network embedding cho node.

Tài liệu ký hiệu graph mở rộng là `G' = (V, E ∪ Einv)`, trong đó `Einv` là tập inverse edges của `E`. Nghĩa là với mỗi edge `(vi, r, vj)` có thể thêm edge ngược `(vj, r^-1, vi)`.

Ý nghĩa với đề tài: `Child/Parent` trong `instruction.md` là ví dụ tự nhiên của cạnh xuôi/ngược trong graph cú pháp.

### 3.4. GGNN trong tài liệu gốc

Chương 22 ghi chú rằng **GGNNs** từng là lựa chọn phổ biến trong program graph, dù các kiến trúc khác sau đó cho thấy cải thiện trên một số nhiệm vụ. Đây là căn cứ gốc phù hợp với `instruction.md`, nơi yêu cầu dùng GGNN cho phân tích chương trình.

## 4. Kiến thức gốc từ Chương 22: Detecting Variable Misuse Bugs

### 4.1. Định nghĩa variable misuse

Chương 22 định nghĩa variable misuse là việc sử dụng sai một biến thay vì một biến khác đã có trong scope. Trong ví dụ của chương, code dùng `min_len` ở nơi cần dùng `max_len` để truncate content đúng.

Mô hình cần làm hai việc:

- **localize**: xác định vị trí bug nếu có;
- **repair**: đề xuất biến thay thế.

Đây khớp trực tiếp với yêu cầu đánh giá `Localization Accuracy` và `Repair Accuracy` trong `instruction.md`.

### 4.2. Tính thực tế của variable misuse

Chương 22 nêu variable misuse thường xảy ra, có thể do thao tác copy-paste cẩu thả và có thể xem như một loại typo. Tài liệu dẫn kết quả:

- Karampatsis và Sutton (2020) tìm thấy hơn 12% bug trong một tập Java codebase lớn là variable misuse.
- Tarlow et al. (2020) tìm thấy 6% Java build errors trong hệ thống kỹ thuật của Google là variable misuse.
- Con số này là lower bound vì compiler Java chỉ phát hiện variable misuse qua type checker.

### 4.3. Vì sao đây là black-box analysis learning

Chương 22 xếp variable misuse vào black-box analysis learning. Không có specification tường minh về ý định của người dùng. GNN phải suy ra khả năng có bug từ:

- coding patterns phổ biến;
- thông tin ngôn ngữ tự nhiên trong comment;
- tên định danh như `min`, `max`, `len`;
- quan hệ trong program graph.

Mục tiêu cụ thể trong Chương 22 là:

- chỉ ra node buggy, ví dụ token `min_len`;
- gợi ý symbol sửa, ví dụ `max_len`.

### 4.4. Localization module

Sau khi GNN tính network embedding `hvi` cho mọi node trong program graph, Chương 22 xét tập `Vvu` gồm các token node tham chiếu đến variable usages.

Localization module được biểu diễn như pointer network trên `Vvu ∪ {/0}`, trong đó `/0` là sự kiện “no bug”. Mô hình tính phân phối xác suất trên các vị trí sử dụng biến và vị trí đặc biệt “không có bug”.

Trong training có giám sát, loss là cross-entropy theo vị trí ground-truth.

### 4.5. Repair module

Khi đã có vị trí variable misuse `vbug`, repair cũng được biểu diễn như pointer network, nhưng trên các symbol node nằm trong scope tại vị trí lỗi.

Chương 22 ký hiệu `Vs@vbug` là tập symbol node của các candidate symbols trong scope tại `vbug`, trừ symbol hiện tại của `vbug`. Xác suất sửa bằng symbol `si` được tính từ embedding của vị trí lỗi và embedding của candidate symbol.

Trong training có giám sát, loss là cross-entropy theo ground-truth repair.

### 4.6. Dữ liệu huấn luyện variable misuse

Chương 22 nêu rằng nếu có dataset lớn gồm variable misuse bug và fix tương ứng, mô hình GNN có thể được train supervised. Tuy nhiên dataset như vậy khó thu thập ở quy mô deep learning yêu cầu.

Vì vậy, các công trình trong hướng này thường tự động chèn random variable misuse bugs vào code lấy từ open-source repositories như GitHub để tạo corpus bug ngẫu nhiên.

Tài liệu nhấn mạnh bug ngẫu nhiên phải tạo cẩn thận. Nếu bug quá hiển nhiên, mô hình học được sẽ không hữu ích. Ví dụ, generator nên tránh tạo bug khiến biến bị dùng trước khi được định nghĩa (`use-before-def`). Dù corpus ngẫu nhiên không hoàn toàn đại diện cho bug thật, chúng đã được dùng để train mô hình có thể bắt một số bug thật.

### 4.7. Đánh giá variable misuse theo Chương 22

Chương 22 nêu rằng các mô hình variable misuse đạt accuracy tương đối cao trên corpus bug ngẫu nhiên, có báo cáo lên đến khoảng 75% theo Hellendoorn et al. (2019b). Tuy nhiên, với bug thật, dù có recall được một số lỗi, precision thường thấp, khiến triển khai thực tế còn khó. Đây vẫn là open research problem.

Tài liệu cũng đưa ví dụ một bug thật được GNN-based variable misuse detector bắt được: developer truyền `identity_pool` thay vì `identity_pool_id` vào exception khi `identity_pool` là `None`.

## 5. Kiến thức gốc từ Chương 4: Node Classification và Message Passing

### 5.1. Node classification

Chương 4 định nghĩa node classification là nhiệm vụ phân loại node vào các nhãn định trước. GNN học node representations bằng cách kết hợp graph structure information và node attributes.

Ký hiệu cơ bản:

- `G = (V, E)` là graph;
- `A` là adjacency matrix;
- `X` là node attribute matrix;
- `H` là node representation học được.

Với đề tài, phần này liên quan vì localization có thể xem là dự đoán trên các node sử dụng biến, còn repair dùng embedding của vị trí bug và candidate symbol node như Chương 22.

### 5.2. General framework của GNN

Chương 4 trình bày ý tưởng cốt lõi của GNN: cập nhật node representation lặp lại bằng cách kết hợp representation của hàng xóm và representation hiện tại của chính node.

Mỗi layer có hai hàm:

- **AGGREGATE**: tổng hợp thông tin từ neighbor nodes;
- **COMBINE**: cập nhật representation của node từ thông tin đã tổng hợp và representation hiện tại.

Sau layer cuối, node representations được dùng cho downstream task, ví dụ node classification bằng softmax. Khi có labeled nodes, mô hình có thể train bằng loss như cross-entropy và backpropagation.

### 5.3. Graph Convolutional Networks

Chương 4 trình bày GCN như một kiến trúc GNN phổ biến vì đơn giản và hiệu quả. GCN cập nhật node representation bằng cách tổng hợp có chuẩn hóa từ neighbor nodes và chính node đó. Trong GCN, graph được thêm self-connection qua `A + I`.

Ý chính cần giữ lại: GCN là dạng GNN dùng graph structure và node feature để lan truyền/tổng hợp thông tin qua các cạnh.

### 5.4. Graph Attention Networks

Chương 4 trình bày GAT như một biến thể dùng attention để gán trọng số khác nhau cho các neighbor khi tổng hợp thông tin. Thay vì dùng cùng một quy tắc trung bình/chuẩn hóa cố định, attention học mức độ quan trọng của neighbor đối với node đang cập nhật.

Ý chính cần giữ lại: GAT liên quan đến đề tài vì graph chương trình có nhiều quan hệ; attention là cơ chế gốc để học neighbor/cạnh nào quan trọng trong quá trình dự đoán.

### 5.5. Neural Message Passing Networks

Chương 4 đưa Neural Message Passing Networks như một khung tổng quát cho GNN. Message passing gồm việc truyền message qua edge, tổng hợp message và cập nhật hidden state của node.

Ý chính cần giữ lại: đây là cơ chế nền tảng giải thích vì sao thông tin từ syntax edge, token edge và data-flow edge có thể đi đến node vị trí lỗi.

### 5.6. Over-smoothing

Chương 4 nêu over-smoothing là khó khăn chung khi train deep GNN: khi số layer tăng, node representations có xu hướng trở nên giống nhau, làm giảm khả năng phân biệt node. Đây là vấn đề nền tảng cần biết khi dùng nhiều bước lan truyền trên graph.

## 6. Kiến thức gốc từ Chương 3: Tổng quan các hướng GNN liên quan

Chương 3 mô tả GNN là framework học trên graph-structured data, trong đó graph có thể biểu diễn quan hệ phức tạp giữa các đối tượng. Tài liệu nêu program analysis là một trong các domain mà GNN đã được áp dụng.

Chương 3 tổ chức nghiên cứu GNN theo ba trục:

- **Foundations**: phương pháp GNN, expressive power, scalability, interpretability, adversarial robustness.
- **Frontiers**: graph classification, link prediction, graph generation/transformation, graph matching, graph structure learning, dynamic GNN, heterogeneous GNN, AutoML, self-supervised GNN.
- **Applications**: các lĩnh vực ứng dụng của GNN, trong đó có program analysis và software mining.

Với đề tài, các phần có tác dụng trực tiếp là foundations và program analysis; các frontier chỉ giữ khi chúng giải thích graph structure, heterogeneous graph hoặc self-supervised learning mà Chương 22 cũng nhắc đến.

## 7. Kiến thức gốc từ Chương 5: Expressive Power

Chương 5 tập trung vào năng lực biểu diễn của GNN. Nội dung có liên quan đến đề tài:

- Message passing là framework được dùng rộng rãi để xây dựng GNN.
- MP-GNN có giới hạn biểu diễn; các mô hình thông thường có quan hệ với khả năng phân biệt của kiểm tra Weisfeiler-Lehman bậc 1.
- Có các hướng tăng sức biểu diễn như thêm random attributes, deterministic distance attributes và higher-order graph neural networks.

Ý nghĩa đối chiếu với đề tài: trong variable misuse, hai biến trong cùng scope có thể có ngữ cảnh gần giống nhau. Kiến thức gốc về expressive power giải thích vì sao cần biểu diễn graph đủ giàu bằng syntax, symbol và data-flow edges như Chương 22 đã mô tả.

## 8. Kiến thức gốc từ Chương 6: Scalability

Chương 6 nêu GNN gặp khó khi áp dụng cho graph lớn vì yêu cầu lưu adjacency matrix và intermediate feature matrices, gây áp lực bộ nhớ và chi phí tính toán.

Các nhóm sampling được trình bày:

- **Node-wise sampling**, ví dụ GraphSAGE;
- **Layer-wise sampling**, ví dụ FastGCN;
- **Graph-wise sampling**, ví dụ Cluster-GCN và GraphSAINT.

Ý nghĩa đối chiếu với đề tài: code corpus có thể tạo nhiều program graph hoặc graph lớn; kiến thức này là nền tảng để hiểu vấn đề mở rộng khi dùng GNN trên nhiều file/code snippet.

## 9. Kiến thức gốc từ Chương 7: Interpretability

Chương 7 cho biết interpretability/explanation trong GNN có thể tập trung vào:

- important nodes;
- important edges;
- important features của node hoặc edge.

Các nhóm phương pháp giải thích được trình bày gồm:

- approximation-based explanation;
- relevance-propagation based explanation;
- perturbation-based approaches;
- generative explanation;
- attention-based interpretable modeling;
- disentangled representation learning.

Ý nghĩa đối chiếu với đề tài: `instruction.md` yêu cầu trực quan graph và đánh dấu node bị dự đoán lỗi. Kiến thức gốc từ Chương 7 cung cấp cơ sở để xem node/edge/feature quan trọng là dạng giải thích hợp lệ trong GNN.

## 10. Kiến thức gốc từ Chương 8: Adversarial Robustness

Chương 3 và Chương 8 mô tả robustness của GNN thông qua việc tạo thay đổi nhỏ trên input graph rồi quan sát thay đổi lớn trong kết quả dự đoán. Các nghiên cứu về robustness gồm adversarial attacks, adversarial training và certified robustness.

Ý nghĩa đối chiếu với đề tài: program graph cũng là input graph; do đó việc thay đổi node, edge, token hoặc quan hệ trong graph có thể ảnh hưởng đến dự đoán. Đây là kiến thức nền, không phải yêu cầu triển khai chính trong `instruction.md`.

## 11. Kiến thức gốc từ Chương 14: Graph Structure Learning

Chương 14 trình bày graph structure learning như hướng học cấu trúc graph cho GNN. Nội dung gồm:

- traditional graph structure learning;
- supervised và unsupervised graph structure learning;
- joint graph structure and representation learning;
- học discrete graph structures;
- học weighted graph structures;
- kết nối với graph generation, adversarial defenses và transformer.

Ý nghĩa đối chiếu với đề tài: Chương 22 nói việc chọn node/edge trong program graph là task-dependent và không có biểu diễn duy nhất. Chương 14 là nền tảng cho ý tưởng cấu trúc graph có thể được học hoặc điều chỉnh, nhưng `instruction.md` đang yêu cầu graph construction từ AST và data-flow edges.

## 12. Kiến thức gốc từ Chương 16: Heterogeneous Graph Neural Networks

Chương 16 định nghĩa heterogeneous graph là graph gồm nhiều loại node hoặc nhiều loại edge. Chương này cũng nêu các thách thức của heterogeneous graph embedding, gồm:

- heterogeneity về structure;
- heterogeneity về attributes;
- yêu cầu bảo toàn semantic/structure/properties;
- các hướng shallow model và deep model;
- message passing-based methods cho HGNN.

Ý nghĩa đối chiếu với đề tài: Chương 22 mô tả program graph là heterogeneous directed graph, gồm token node, syntax node, symbol node và nhiều loại edge như `Child`, `OccurrenceOf`, `MayNextUse`, `NextToken`.

## 13. Kiến thức gốc từ Chương 18: Self-supervised Learning

Chương 18 trình bày self-supervised learning cho GNN trong bối cảnh deep learning phụ thuộc nhiều vào dữ liệu gán nhãn. Tài liệu phân loại:

- training strategies: self-training, pre-training/fine-tuning, joint training;
- loss functions: classification/regression loss, contrastive learning loss;
- pretext tasks: node-level, graph-level, node-graph-level;
- pretext tasks dựa trên structure, feature hoặc hybrid.

Ý nghĩa đối chiếu với đề tài: Chương 22 nêu dataset bug thật khó thu thập ở quy mô lớn, nên các công trình variable misuse thường tạo bug ngẫu nhiên trong code open-source. Chương 18 cung cấp nền tảng tổng quát về học khi nhãn hạn chế, nhưng không thay thế case study variable misuse trong Chương 22.

## 14. Bảng đối chiếu kiến thức gốc với yêu cầu đề tài

| Yêu cầu trong `instruction.md` | Kiến thức gốc tương ứng trong tài liệu GNN                                                                                  |
| ------------------------------ | --------------------------------------------------------------------------------------------------------------------------- |
| Biểu diễn code thành graph     | Chương 22: program graph là heterogeneous directed graph với token, syntax, symbol, data-flow relations                     |
| AST, Child/Parent              | Chương 22: syntax tree với `Child` edge nối syntax node và token; inverse edges được dùng trong GNN graph                   |
| NextToken                      | Chương 22: token node được nối thành linear chain bằng `NextToken`                                                          |
| Data Flow                      | Chương 22: `MayNextUse` biểu diễn các luồng dữ liệu có thể xảy ra; giống program dependence graph                           |
| LastUse/LastWrite/ComputedFrom | `instruction.md` nêu cụ thể; Chương 22 cung cấp nền tảng gốc rộng hơn về data-flow edge trong program graph                 |
| Symbol/biến trong scope        | Chương 22: symbol node đại diện biến/hàm/package trong scope; repair chọn candidate symbols trong scope                     |
| GGNN                           | Chương 22: GGNN từng là lựa chọn phổ biến cho program graph                                                                 |
| Localization                   | Chương 22: localization module là pointer network trên variable usage token nodes và “no bug” event                         |
| Repair                         | Chương 22: repair là pointer network trên symbol nodes trong scope tại vị trí lỗi                                           |
| Dữ liệu bug                    | Chương 22: bug thật khó thu thập; nhiều công trình tự chèn random variable misuse bugs vào code open-source                 |
| Đánh giá localization/repair   | Chương 22: mô hình cần localize bug và suggest repair; `instruction.md` yêu cầu đo Localization Accuracy và Repair Accuracy |
| Trực quan node/cạnh quan trọng | Chương 7: explanation của GNN có thể là important nodes, important edges hoặc important features                            |
| Long-range dependencies        | Chương 22: symbol nodes hữu ích để mô hình hóa quan hệ xa giữa các lần dùng biến                                            |

## 15. Tóm tắt ngắn gọn phần kiến thức gốc cần dùng cho đề tài

Kiến thức gốc quan trọng nhất nằm ở Chương 22. Chương này trực tiếp trình bày GNN trong program analysis và case study variable misuse. Một chương trình có thể được biểu diễn thành heterogeneous directed graph gồm token node, syntax node, symbol node và data-flow edge. GNN nhận graph này, tạo embedding cho node, rồi dùng embedding để làm hai bước của variable misuse detection: localize vị trí dùng sai biến và repair bằng cách chọn symbol trong scope.

Các chương nền tảng còn lại được dùng để giải thích cơ chế chung: GNN học node representation bằng aggregate/combine hoặc message passing; node classification là nhiệm vụ nền; GGNN là kiến trúc từng được dùng phổ biến cho program graph; heterogeneous graph phù hợp với code graph; interpretability cho phép giải thích bằng important nodes/edges/features; scalability và expressive power là các vấn đề nền khi áp dụng GNN cho graph lớn hoặc graph có cấu trúc phức tạp.

## 16. Nguồn đã dùng

- `docs/references/base/instruction.md`
- Ảnh chụp mục lục sách trong `docs/references/docs/capture_019_p19-19.png` đến `docs/references/docs/capture_025_p25-25.png`
- Chapter 3: Graph Neural Networks - `https://graph-neural-networks.github.io/static/file/chapter3.pdf`
- Chapter 4: Graph Neural Networks for Node Classification - `https://graph-neural-networks.github.io/static/file/chapter4.pdf`
- Chapter 5: The Expressive Power of Graph Neural Networks - `https://graph-neural-networks.github.io/static/file/chapter5.pdf`
- Chapter 6: Graph Neural Networks: Scalability - `https://graph-neural-networks.github.io/static/file/chapter6.pdf`
- Chapter 7: Interpretability in Graph Neural Networks - `https://graph-neural-networks.github.io/static/file/chapter7.pdf`
- Chapter 8: Graph Neural Networks: Adversarial Robustness - `https://graph-neural-networks.github.io/static/file/chapter8.pdf`
- Chapter 14: Graph Neural Networks: Graph Structure Learning - `https://graph-neural-networks.github.io/static/file/chapter14.pdf`
- Chapter 16: Heterogeneous Graph Neural Networks - `https://graph-neural-networks.github.io/static/file/chapter16.pdf`
- Chapter 18: Graph Neural Networks: Self-supervised Learning - `https://graph-neural-networks.github.io/static/file/chapter18.pdf`
- Chapter 22: Graph Neural Networks in Program Analysis - `https://graph-neural-networks.github.io/static/file/chapter22.pdf`
