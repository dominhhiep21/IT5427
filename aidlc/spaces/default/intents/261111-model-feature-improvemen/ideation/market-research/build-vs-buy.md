# Build vs Buy

Nguồn: `../intent-capture/intent-statement.md`, `competitive-analysis.md`, `requirements.txt`, `aidlc/spaces/default/memory/project.md`, `src/analytics/model.py`.

## Không có gì để "buy" — nhưng có một quyết định thật về thư viện

Không có ngân sách, không có tài khoản đám mây, không có nhà cung cấp để mua [intent-statement]. Vậy "build vs buy" ở đây là: **tự viết bao nhiêu, và dùng thư viện có sẵn bao nhiêu**. Đây không phải câu hỏi hình thức — nó quyết định cả khối lượng công việc lẫn rủi ro.

## Bốn lựa chọn

| # | Lựa chọn | Được không | Vì sao |
|---|---|---|---|
| B1 | Dùng `scikit-learn` đã ghim (1.6.1) | **Được, đang dùng** | đã có trong `requirements.txt`, chạy trên Python 3.13/Windows, không cần cài thêm |
| B2 | Tự viết lại hồi quy logistic bằng tay | Được nhưng **không nên** | đã có trong B1; viết lại là tự tạo một nguồn sai số thứ hai không ai kiểm |
| B3 | Thêm thư viện ngoài (`xgboost`, `lightgbm`, `catboost`) | **Không được** | quy tắc dự án: không import thư viện chưa ghim trong `requirements.txt`; và xem B4 — không cần |
| B4 | Dùng mô hình cây **có sẵn trong `scikit-learn`** (`HistGradientBoostingClassifier`) | **Được** | cùng một thư viện đã ghim, nên **không thêm phụ thuộc nào**; hỗ trợ giá trị thiếu và biến phân loại tốt hơn hồi quy logistic |

## Điểm quan trọng nhất của mục này

B3 và B4 trông giống nhau nhưng khác hẳn: thêm `xgboost` là **thêm một phụ thuộc** và vi phạm quy tắc dự án; dùng `HistGradientBoostingClassifier` là dùng thêm **một lớp có sẵn** trong thư viện đã ghim. Cùng là "mô hình cây", nhưng chỉ một cách được phép — và nó được phép mà không cần thay đổi `requirements.txt`.

Vì Q9 = E đã bỏ khuyến nghị "không thêm loại mô hình mới" của đợt trước [intent-statement], nhánh B4 trở nên khả dụng **mà không cần thương lượng lại về phụ thuộc**.

## Thứ tự: thử cả hai ngay, nhưng trên **cùng một bộ đặc trưng**

Q2 = C chọn thử cả hai mô hình ngay từ đầu rồi chọn theo AUC. Cách đó chấp nhận mất khả năng đọc hệ số của hồi quy logistic — và chấp nhận nó **có ý thức**, vì mục tiêu của đợt là chứng minh đặc trưng có cứu được mô hình, không phải giữ một mô hình dễ giải thích [intent-statement].

| Bước | Việc | Vì sao |
|---|---|---|
| 1 | Đo lại baseline trong khung mới | không có mốc thì mọi so sánh sau đều vô nghĩa |
| 2 | Dựng đặc trưng mới, chạy **cả hai** mô hình trên cùng tập, cùng mốc cắt, cùng quần thể | giữ được phép so công bằng |
| 3 | So theo AUC, ghi **cả hai** con số chứ không chỉ con số thắng | con số thua cũng là bằng chứng |
| 4 | Nếu cả hai vẫn thua baseline: một lần thử cuối bằng mô hình cây với cấu hình khác, rồi kết luận | Q3 = B đòi đúng một lần thử cuối trước khi bỏ hướng |

**Cái bẫy mà cách này vẫn tránh được:** nếu chỉ chạy mô hình cây và thấy AUC tăng, không biết công lao thuộc về đặc trưng hay thuật toán. Chạy **cả hai trên cùng đặc trưng** thì tách được hai phần: hiệu số giữa hai mô hình là tác động của thuật toán, còn cả hai so với baseline là tác động của đặc trưng.

Đó cũng là điều đợt trước đã không làm: thêm 10 đặc trưng cùng lúc rồi không thể nói cái nào có ích — và kết quả là cả nhóm cùng có hại [feedback-loop].

## Chi phí đã chấp nhận

Hồi quy logistic cho hệ số đọc được: dấu và độ lớn của từng đặc trưng. Mô hình cây không cho điều đó. Chọn Q2 = C nghĩa là đợt này **đánh đổi khả năng giải thích lấy AUC**, và đánh đổi đó phải được ghi trong báo cáo cuối chứ không im lặng.

## Điều không có

Không mua nền tảng ML, không thuê dịch vụ dự đoán, không dùng API bên thứ ba. Lý do không phải tiết kiệm — mà là không có gì để mua cho một mô hình chạy một lần trên một tệp CSV cục bộ.
