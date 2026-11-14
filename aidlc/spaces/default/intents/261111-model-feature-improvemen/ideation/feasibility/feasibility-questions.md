# Câu hỏi — Feasibility & Constraints

## Q1. Đưa hai cột mốc và bang người bán tới chỗ mô hình đọc bằng cách nào

Mart hiện **không có** `order_delivered_carrier_date`, `order_approved_at` (trong `v_fact_orders`) và `seller_state` (trong `v_fact_order_items`). Nhưng `data/cleaned/orders.parquet` có đủ hai cột mốc, và `v_dim_seller` có `state`.

- A. **Nới mart**: thêm 2 cột mốc vào `v_fact_orders`, thêm `seller_state` vào `v_fact_order_items`; chỉ thêm cột, **không** đổi số dòng. Giữ nguyên tắc "analytics đọc mart", nhưng phải cập nhật `StarSchemaValidator`, `VIEW_TABLES` và test cùng lúc
- B. **Đọc cleaned qua `AnalyticsService`**: thêm một truy vấn `read_parquet` trong lớp có sẵn; không đụng mart, không đổi hợp đồng 11 view, nhưng tạo nguồn đọc thứ hai cho analytics
- C. Chưa xác định — chốt ở Domain Design
- X. Khác (vui lòng nêu rõ)

[Answer]: A

## Q2. Mô hình lưu ở đâu và bằng định dạng gì

Giao diện dự đoán cần mô hình dùng lại được; đợt trước không lưu mô hình ở đâu cả.

- A. Lưu một tệp nhị phân trong `data/models/` (đã bị `.gitignore`) kèm một tệp JSON mô tả đặc trưng và phiên bản thư viện
- B. Lưu vào `warehouse/` cạnh DuckDB
- C. Không lưu tệp; huấn luyện lại khi mở tab (trái với Q14 = A đã chốt "lưu lại")
- D. Chưa xác định — chốt ở Infrastructure Design
- X. Khác (vui lòng nêu rõ)

[Answer]: A

## Q3. Hai dòng hàng thiếu carrier date thì làm gì

Trên 110.197 dòng hàng thuộc đơn đã giao, đúng **2** dòng không có `order_delivered_carrier_date`.

- A. Lọc khỏi quần thể; ghi rõ số bị lọc trong báo cáo
- B. Giữ lại và gán bằng mốc gần nhất (ví dụ ngày đặt) — không khuyến nghị, vì tạo dữ liệu không có thật
- C. Chưa xác định
- X. Khác (vui lòng nêu rõ)

[Answer]: A

## Q4. Mốc cắt tập huấn luyện/kiểm tra có giữ 2018-04-01

Mốc cũ chia theo ngày **đặt hàng** ở grain đơn (64.322 / 32.156). Khung mới dự đoán lúc bàn giao, đơn vị dòng hàng.

- A. Giữ nguyên 2018-04-01, vẫn chia theo ngày đặt hàng — để so sánh được với đợt trước
- B. Giữ 2018-04-01 nhưng chia theo ngày **bàn giao**, vì đó là thời điểm dự đoán
- C. Chọn mốc khác (nêu ở phần trả lời)
- D. Chưa xác định — chốt ở Functional Design
- X. Khác (vui lòng nêu rõ)

[Answer]: A

## Consolidated Summary Confirmation

Bốn câu đã trả lời. Bản tóm tắt để bạn xác nhận:

- **Đường dữ liệu** [Q1 = A]: **nới mart** — thêm 2 cột mốc vào `v_fact_orders` và `seller_state` vào `v_fact_order_items`, **chỉ thêm cột, không đổi số dòng**; phải cập nhật `StarSchemaValidator`, `VIEW_TABLES` và test cùng lúc.
- **Lưu mô hình** [Q2 = A]: tệp nhị phân trong `data/models/` (đã bị `.gitignore`) + JSON mô tả đặc trưng và phiên bản thư viện.
- **Hai dòng hàng thiếu carrier date** [Q3 = A]: lọc khỏi quần thể, ghi rõ số bị lọc trong báo cáo. Quần thể còn **110.195** dòng hàng.
- **Mốc cắt** [Q4 = A]: giữ **2018-04-01**, chia theo **ngày đặt hàng** — kèm hệ quả đã ghi: một đơn đặt trước mốc nhưng bàn giao sau mốc nằm ở tập huấn luyện, làm yếu tính "ngoài thời gian" của phép chia (R-08). Chấp nhận để giữ so sánh với 64.322/32.156 của đợt trước.
- **Dữ liệu đo được**: 110.195 dòng hàng, 96.476 đơn, 2.970 người bán, 8.713 dòng trễ (7,91%), 1.278 đơn nhiều người bán.
- **Vẫn là giả thuyết**: AUC ≥ 0,70 với khung mới — 110.195 dòng chứng minh **đủ mẫu**, không chứng minh **đủ tín hiệu** (R-01).

- Looks correct
- Request changes

[Answer]: Looks correct
