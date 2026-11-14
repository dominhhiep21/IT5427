# Câu hỏi — Thiết kế miền cho phần thống kê và mô hình

## Q1. [Tech] Ranh giới thành phần

A. Một mô-đun duy nhất trong `src/analytics` chứa cả kiểm định và mô hình
B. Hai mô-đun riêng trong cùng gói `src/analytics`: một cho kiểm định, một cho mô hình
C. Một gói mới riêng, tách khỏi `src/analytics`
X. Other (please specify)

[Answer]: B

## Q2. [Tech] Cách đọc dữ liệu cho phần mới

A. Qua `AnalyticsService` hiện có
B. Truy vấn DuckDB trực tiếp trong mô-đun mới
C. Qua một lớp đọc mart riêng, dùng chung cho cả hai phần
X. Other (please specify)

[Answer]: A

## Q3. [Tech] Ai chịu trách nhiệm ghi báo cáo

A. Mô-đun thống kê tự ghi cả hai phần
B. Một thành phần ghi báo cáo dùng chung, nhận kết quả từ hai phần
C. Tầng pipeline ghi sau khi cả hai phần trả kết quả
X. Other (please specify)

[Answer]: B

## Q4. [Tech] Tab đọc báo cáo bằng gì

A. Một hàm đọc tệp dùng chung, có kiểm cấu trúc
B. Đọc trực tiếp trong callback của tab
C. Khác — mô tả
X. Other (please specify)

[Answer]: A

## Q5. [Tech] Hợp đồng dữ liệu giữa hai phần

A. Một kiểu dữ liệu chung cho toàn bộ báo cáo
B. Mỗi phần một kiểu riêng, báo cáo là kiểu ghép
C. Dùng dict tự do, không định kiểu
X. Other (please specify)

[Answer]: A

## Consolidated Summary Confirmation

- Q1: hai mô-đun riêng trong cùng gói `src/analytics` — một cho kiểm định, một cho mô hình
- Q2: đọc dữ liệu qua `AnalyticsService` hiện có
- Q3: một thành phần ghi báo cáo dùng chung, nhận kết quả từ hai phần
- Q4: tab đọc qua một hàm đọc tệp dùng chung, có kiểm cấu trúc
- Q5: một kiểu dữ liệu chung cho toàn bộ báo cáo

- Looks correct
- Request changes

[Answer]: Looks correct

