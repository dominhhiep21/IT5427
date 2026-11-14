# Intent Backlog — proto-Units

Nguồn: `scope-document.md`, `../intent-capture/intent-statement.md`, `../feasibility/{feasibility-assessment,constraint-register,raid-log}.md`.

## Ba đơn vị công việc

| # | Đơn vị | MoSCoW | Phụ thuộc | Giá trị khi xong |
|---|---|---|---|---|
| **U1** | Nới mart (thêm cột mốc + `seller_state`) và **đo baseline** trong khung/đơn vị mới | **Must** | — | có mốc so thật; mọi so sánh sau đó có nghĩa |
| **U2** | Đặc trưng mới + **hồi quy logistic triển khai** + mô hình cây để báo cáo + lưu mô hình logistic | **Must** | U1 | trả lời câu hỏi của cả đợt: đặc trưng có cứu được mô hình không |
| **U3** | Giao diện dự đoán trên tab "Kết quả phân tích" + mốc sàn 0,55 trong CI | **Must** | U2 | mô hình dùng được, không chỉ báo cáo được; có cổng chặn thoái hoá |

## Vì sao không có Should / Could / Won't

Không có hạng mục nào ở mức thấp hơn Must. Đó không phải thiếu cân nhắc — nó là hệ quả trực tiếp của hai quyết định đã chốt: Q9 = E (không loại trừ gì) và câu trả lời "làm đủ ba phần bất kể kết quả" ở stage này.

Đánh đổi đã ghi ở `scope-document.md` → *Rủi ro phạm vi*: không có đường cắt thoả thuận trước. Nếu thời gian cạn, việc cắt phải được khai thành thay đổi phạm vi, không tự quyết trong lúc code.

## Thứ tự và vì sao không thể đảo

| Bước | Làm gì | Nếu đảo thì hỏng ở đâu |
|---|---|---|
| 1 | U1: nới mart, dựng truy vấn quần thể, đo baseline | U2 sẽ không có mốc so — và một mô hình "0,62" không nói được gì khi không biết baseline trong khung mới là bao nhiêu |
| 2 | U2: đặc trưng, hai mô hình, chọn, lưu | U3 sẽ không có tệp mô hình để nạp, và sẽ phải huấn luyện tại chỗ — trái Q14 = A |
| 3 | U3: giao diện, phép kiểm lặp lại, mốc sàn | nếu làm trước, mốc sàn 0,55 neo vào con số chưa đo lại — đúng R-07 |

## Nội dung từng đơn vị, ở mức đủ để lập kế hoạch

**U1 — mở đường dữ liệu và dựng mốc**
- Thêm `order_approved_at`, `order_delivered_carrier_date` vào `v_fact_orders`; `seller_state` vào `v_fact_order_items`; **chỉ thêm cột, không đổi số dòng**.
- Cập nhật đồng thời `StarSchemaValidator`, `VIEW_TABLES` và các test khẳng định số cột, trong cùng thay đổi.
- Một truy vấn quần thể grain dòng hàng: đơn đã giao **và** có carrier date; 110.195 dòng, 8.713 dòng trễ, lọc 2 dòng thiếu carrier date và ghi rõ số bị lọc.
- Đo AUC baseline `customer_state` trong khung/đơn vị mới, chia tập theo `order_id` với mốc 2018-04-01 trên ngày đặt hàng; ghi con số vào record.

**U2 — đặc trưng và mô hình**
- Đặc trưng từ khung bàn giao: hai cột mốc ở dạng số ngày, bang người bán so với bang người mua, cùng các đặc trưng còn hiệu lực ở grain dòng hàng.
- Giữ nguyên danh sách cấm; chỉ nới đúng hai cột mốc, ở dạng số ngày.
- Chạy hồi quy logistic (**mô hình triển khai**) và `HistGradientBoosting` (**để báo cáo** đánh đổi) trên **cùng** bộ đặc trưng, cùng mốc cắt, cùng quần thể; ghi **cả hai** AUC.
- Lưu mô hình **logistic** vào `data/models/` kèm JSON mô tả đặc trưng và phiên bản thư viện; AUC của cây ghi vào record, kèm câu nói nó không được chọn vì cần hệ số.
- Test chặn rò rỉ: không đơn nào nằm ở cả hai tập.

**U3 — giao diện và cổng chất lượng**
- Vùng nhập liệu trên tab "Kết quả phân tích"; dự đoán từ mô hình đã lưu, không huấn luyện lại.
- Phép kiểm lặp lại: cùng đầu vào → cùng điểm, qua hai lần chạy và sau khi khởi động lại.
- Mốc sàn 0,55 trong CI, **xem lại sau** khi có baseline đo lại (nếu baseline > 0,55 thì mốc sàn phải nâng).

## Truy vết về mục tiêu

| Mục tiêu của đợt | Đơn vị phụ trách |
|---|---|
| AUC ≥ 0,70 và > baseline đo lại | U1 (mốc) → U2 (kết quả) |
| Giao diện dự đoán từ mô hình đã lưu | U2 (lưu) → U3 (nạp và hiển thị) |
| Không hồi quy 5 KPI / 9 bảng / 11 view | U1 (chỉ thêm cột) |
| Cổng chặn mô hình thoái hoá | U3 (mốc sàn) |
