# Risk and Sequencing Rationale — Cải thiện đặc trưng cho mô hình dự đoán đơn trễ

Nguồn: `bolt-plan.md`, `delivery-planning-questions.md` (Q1 = A, Q2 = A, Q5 = A), `../units-generation/unit-of-work-dependency.md`, `../domain-design/decisions.md`.

**Bolt** ở đây là một lượt chạy xuyên các stage Construction cho một phần việc, kết thúc bằng thứ chạy được và kiểm được trên dữ liệu thật.

## Heuristic: rủi ro trước — nhưng DAG đã chọn thứ tự

Heuristic được dùng là **risk-first** (làm phần rủi ro nhất trước), không phải WSJF và không phải value-first. Nhưng phải nói ngay một điều để không tự lừa: **thứ tự không phải do heuristic chọn.** DAG `u1 → u2 → u3` là một chuỗi thẳng, nên chỉ có **một** thứ tự tô-pô hợp lệ. Việc của tài liệu này là trả lời: *đi đúng thứ tự đó có phải là điều may mắn hay không?*

**Có.** Rủi ro lớn nhất của đợt nằm đúng ở đơn vị đầu tiên:

| Hạng | Rủi ro | Vì sao nghiêm trọng | Bolt kiểm nó |
|---|---|---|---|
| 1 | **Hồi quy mart/KPI** ở U1 | Chạm tầng dùng chung: một lỗi grain làm đỏ 5 KPI, 9 bảng mart, 11 view và toàn bộ test tích hợp cũ | Bolt 1 |
| 2 | **Grain dòng hàng làm rò rỉ hoặc thổi AUC** ở U2 | Chia tập sai khoá là loại lỗi cho ra AUC đẹp mà vô nghĩa — không thấy được bằng mắt | Bolt 2 |
| 3 | **Không vượt được baseline** ở U2 | Mục tiêu của cả đợt; nếu sai thì Bolt 3 không nên làm | Bolt 2 |
| 4 | **Vượt ngân sách 300 s** ở U2 | Grain dòng hàng ≈112.650 dòng thay vì 96.478 đơn | Bolt 2 |
| 5 | **Vỡ hình dạng bề mặt** ở U3 | 10 callback/10 output canh ở ba tệp test; sửa trễ thì phải sửa cả năm chỗ | Bolt 3 |

Q5 = A chốt rủi ro số một là hồi quy mart/KPI — và nó trùng Bolt 1. Đó là lý do **không cần đổi thứ tự**: rủi ro lớn nhất vốn đã ở đầu đường.

## Vì sao không chấm WSJF (Q2 = A)

WSJF xếp hạng công việc để chọn **cái gì làm trước** khi có nhiều đường. Ở đây có đúng một đường. Chấm điểm sẽ cho ra một bảng số trông khoa học nhưng **không thể đổi bất cứ quyết định nào** — và một bảng như thế tệ hơn không có bảng, vì nó khiến người đọc sau tưởng thứ tự đã được cân nhắc bằng số.

Thay vào đó: lập luận bằng lời, và một bảng rủi ro như trên — thứ thật sự dùng được khi có người hỏi "vì sao Bolt 1 trước?".

## Vì sao không value-first (Q1 = B bị loại)

Giá trị người dùng thấy nằm ở **Bolt 3** (mục Dự đoán). Đẩy nó lên đầu là bất khả thi về **dữ liệu**, không phải về ý thích: vùng dự đoán đọc `model.threshold` và nạp tệp mô hình, mà cả hai chỉ tồn tại sau Bolt 2. Một Bolt 3 làm trước sẽ chỉ dựng được khung rỗng và **không kiểm được** trạng thái `day-du` — tức định nghĩa xong của nó không thể đạt.

Đây là chỗ dễ tự lừa nhất, nên ghi rõ: value-first không bị loại vì "rủi ro quan trọng hơn giá trị"; nó bị loại vì **không thực hiện được**.

## Vì sao không lát cắt mỏng

Scope `feature` khai `skeleton: on`, nhưng người làm đã chốt **không dựng lát cắt mỏng** (Q2 của đợt = A), và `project.md` ghi điểm lệch này. Hệ quả cho kế hoạch: **không có Bolt nào mang mốc walking skeleton**, và không có checkpoint skeleton ở đầu Construction. Cái giá đã biết: rủi ro khớp nối dồn về Bolt 3; phần bù là mỗi Bolt có test end-to-end riêng trên dữ liệu thật.

## Vì sao ba Bolt chứ không hai hay bốn (Q3 = A)

- **Hai Bolt (gộp U1+U2)**: một Bolt sẽ có **hai** định nghĩa xong chồng nhau — "mart không đổi số dòng" và "mô hình vượt baseline" — và người duyệt không biết nên dừng ở đâu khi cái thứ nhất đỏ. Gộp cũng làm một lần giao hàng chạm cả mart lẫn mô hình, tức rủi ro 1 và rủi ro 2-4 trong cùng một cửa sổ.
- **Bốn Bolt (tách U3 đôi)**: hai nửa của U3 — bề mặt và nối số + mốc sàn — không kiểm được độc lập. Nửa bề mặt dựng xong mà chưa nối số thì không có gì để kiểm ngoài cấu trúc cây, và nửa sau vẫn phải chờ đúng Bolt trước. Tách ra chỉ thêm một cổng duyệt, không thêm thông tin.
- **Ba Bolt**: mỗi Bolt một đơn vị, một định nghĩa xong, một giả thuyết độ tin cậy, một demo. Đây là kích cỡ nhỏ nhất mà mỗi lần giao hàng vẫn **chạy được** trên dữ liệu thật.

## Rủi ro còn lại, không có Bolt nào kiểm

| Rủi ro | Vì sao không kiểm được trong đợt | Xử lý |
|---|---|---|
| Một người làm, không soát chéo mã | Mô hình đội đã chốt (Team Formation) | Bù bằng test end-to-end từng đơn vị + test hình dạng bề mặt; không có cơ chế nào khác |
| `pickle` gắn với phiên bản thư viện | Bản chất của định dạng | Đã ghi trong hợp đồng C2b: không phải định dạng trao đổi; máy khác sinh lại |
| Ngân sách 300 s có thể vẫn vượt sau tối ưu | Chỉ biết sau khi đo thật | Bolt 2 đo và sửa ngân sách **có chủ đích**; nếu vượt, đó là quyết định ghi lại, không phải nới ngầm |
| Chất lượng mô hình thấp hơn kỳ vọng 0,70 | Không hứa trước được bằng thiết kế | Mốc sàn `max(MODEL_AUC_FLOOR, baseline_auc)` bắt thoái hoá; nếu AUC thấp, US1.3 bắt ghi quyết định giữ/hạ mốc kèm lý do |
