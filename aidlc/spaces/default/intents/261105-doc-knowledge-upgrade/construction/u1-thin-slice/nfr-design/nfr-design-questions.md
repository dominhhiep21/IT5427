# NFR Design — u1-thin-slice

Thiết kế kỹ thuật cho các yêu cầu phi chức năng đã chốt. Phần lớn NFR của lát cắt đã rõ cách làm; dưới đây chỉ hỏi hai điểm còn phải chọn.

## Q1. [Kỹ thuật] Khi đọc CSV nguồn lỗi giữa đường, xử lý thế nào?

Ảnh hưởng tới cách viết phần nạp và cách test lỗi.

- A. Thử lại một lần rồi báo lỗi (dữ liệu là tệp cục bộ, lỗi thường là vĩnh viễn)
- B. Không thử lại, báo lỗi ngay kèm tên tệp và dòng lỗi
- C. Thử lại ba lần có chờ tăng dần
- D. Not yet defined (chưa xác định)
- X. Other (please specify)

[Answer]: A

## Q2. [Kỹ thuật] Nhật ký sự kiện của tab mới ghi ở đâu?

Hệ đã có nhật ký JSONL theo `run_id` cho pipeline.

- A. Ghi chung tệp nhật ký của lần chạy gần nhất, thêm trường `stage="integration"`
- B. Ghi tệp riêng `logs/dashboard-<ngày>.jsonl`
- C. Không ghi nhật ký; chỉ hiện thời gian chạy trên màn hình
- D. Not yet defined (chưa xác định)
- X. Other (please specify)

[Answer]: A

## Consolidated Summary Confirmation

Tóm tắt các câu trả lời:

- Đọc CSV lỗi giữa đường: thử lại một lần rồi báo lỗi.
- Nhật ký của tab mới: ghi chung tệp nhật ký của lần chạy gần nhất, thêm trường `stage="integration"`.

Cách làm cho các NFR còn lại: đọc thẳng CSV bằng pandas với kiểm tra cột theo BR1.3, truy vấn chạy trên DuckDB in-memory, thẻ dựng một lần khi mở tab và đọc lại kết quả đã có, không có cache phân tán.

Does this all look correct before I generate the artifact?

- Looks correct
- Request changes

[Answer]: Looks correct
