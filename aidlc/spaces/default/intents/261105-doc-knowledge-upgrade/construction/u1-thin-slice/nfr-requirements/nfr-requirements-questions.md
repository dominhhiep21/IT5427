# NFR Requirements — u1-thin-slice

Các ngưỡng phi chức năng của dự án đã chốt ở bước Requirements (NFR1–NFR6). Dưới đây chỉ hỏi hai điểm còn mở ở mức đơn vị.

## Q1. [Kỹ thuật] Truy vấn của lát cắt cần nhanh tới đâu?

NFR1 chung là dưới 2 giây mỗi tương tác. Truy vấn đếm đơn chỉ đọc một bảng nên có thể chặt hơn.

- A. Giữ ngưỡng chung 2 giây
- B. Đặt 1 giây cho truy vấn đếm đơn (chỉ đọc một bảng, không join)
- C. Không đặt ngưỡng riêng cho lát cắt
- D. Not yet defined (chưa xác định)
- X. Other (please specify)

[Answer]: A

## Q2. [Kỹ thuật] Có thêm kiểm thử hiệu năng tự động không?

Kiểm thử hiệu năng thường không ổn định trên máy cá nhân và tốn thời gian chạy.

- A. Không; chỉ ghi thời gian chạy vào kết quả và xem bằng mắt
- B. Có; thêm một test đo thời gian chạy truy vấn với ngưỡng cứng
- C. Có, nhưng đánh dấu `slow` để không chạy ở bộ nhanh
- D. Not yet defined (chưa xác định)
- X. Other (please specify)

[Answer]: B

## Consolidated Summary Confirmation

Tóm tắt các câu trả lời:

- Truy vấn của lát cắt giữ ngưỡng chung 2 giây (NFR1), không đặt ngưỡng chặt hơn.
- Có thêm một kiểm thử hiệu năng tự động: đo thời gian truy vấn, ngưỡng cứng 2 giây, chạy trong bộ test nhanh.

Các yêu cầu phi chức năng còn lại (độ phủ 80%, `ruff`, WCAG AA, không hồi quy KPI, chạy local) đã chốt ở bước Requirements và được ghi lại cho đơn vị này.

Does this all look correct before I generate the artifact?

- Looks correct
- Request changes

[Answer]: Looks correct
