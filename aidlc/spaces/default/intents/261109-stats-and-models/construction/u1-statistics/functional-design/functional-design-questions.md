# Câu hỏi — Thiết kế chức năng cho u1-statistics

## Q1. [Tech] Nguồn dữ liệu cho từng nhóm kiểm định

A. Dùng `AnalyticsService` trên các view: `v_fact_orders` và `v_dim_customer` cho tỉ lệ; `v_fact_order_items` cho tương quan
B. Truy vấn trực tiếp các bảng Parquet
C. Dùng DataFrame đã tải sẵn trong bộ nhớ
X. Other (please specify)

[Answer]: A

## Q2. [Data] Định nghĩa doanh thu cho phân rã mùa vụ

A. `price + freight_value` của đơn `delivered`, đúng `REVENUE_DEFINITION`
B. `payment_value` của đơn `delivered`
C. Cả hai, báo cáo riêng
X. Other (please specify)

[Answer]: A

## Q3. [Data] Xử lý tháng thiếu dữ liệu trong chuỗi doanh thu

A. Chỉ dùng các tháng có đơn; ghi rõ số tháng thực có
B. Điền 0 cho tháng thiếu
C. Nội suy giá trị thiếu
X. Other (please specify)

[Answer]: B

## Q4. [Tech] Khi một kiểm định không đủ điều kiện chạy

A. Ghi `null` cho kết quả đó kèm lý do bằng chữ; các kiểm định khác vẫn chạy
B. Bỏ hẳn khỏi báo cáo
C. Dừng toàn bộ lần chạy
X. Other (please specify)

[Answer]: A

## Q5. [Tech] Số chữ số thập phân khi ghi báo cáo

A. Tỉ lệ và p-value 4 chữ số; hệ số tương quan 3 chữ số
B. Tất cả 2 chữ số
C. Giữ nguyên giá trị tính được
X. Other (please specify)

[Answer]: A
