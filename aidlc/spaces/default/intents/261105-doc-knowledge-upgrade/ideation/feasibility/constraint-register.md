# Constraint Register — Nâng cấp tích hợp dữ liệu Olist

Bối cảnh từ `intent-statement.md` và các câu trả lời của bước Feasibility.

## Ràng buộc kỹ thuật

| ID | Ràng buộc | Nguồn | Ảnh hưởng |
|---|---|---|---|
| TC-01 | Chỉ ăn khớp với hệ thống trong repo: pipeline, `data/marts`, `warehouse/olist.duckdb`, dashboard Dash | Q1 = A | Không cần hợp đồng tích hợp ngoài; có thể đổi cấu trúc mart nếu giữ tương thích nội bộ |
| TC-02 | Ngôn ngữ và thư viện hiện có: Python 3.13, pandas, DuckDB, Plotly Dash | Q3 = A | Phần mới phải viết trong cùng môi trường; không dùng Spark/Kafka/Docker |
| TC-03 | Được thêm thư viện Python mã nguồn mở nhỏ, chạy local | Q3 = B | Phải cập nhật `requirements.txt` và ghi rõ lý do từng thư viện |
| TC-04 | Không dùng đám mây hay hạ tầng ngoài máy local | Q6 = A | Không có dịch vụ ngoài; mọi thứ chạy bằng một lệnh trên máy |
| TC-05 | Dữ liệu gốc trong `dataset/` là bất biến | `intent-statement.md`, quy ước repo | Mọi biến đổi ghi ra thư mục dẫn xuất mới |
| TC-06 | Không hồi quy KPI baseline và bộ test hiện có | `intent-statement.md` (chỉ số thành công) | Phải chạy test trước và sau khi thêm phần mới |

## Ràng buộc tổ chức

| ID | Ràng buộc | Nguồn | Ảnh hưởng |
|---|---|---|---|
| OC-01 | Thời gian khoảng 1–2 tuần | Q4 = B | Phải cắt phạm vi từng nhóm xuống mức minh hoạ |
| OC-02 | Không có mốc nộp cố định, tự quyết tiến độ | Q5 = A | Không có điểm dừng bên ngoài; cần tự đặt mốc kiểm tra |
| OC-03 | Một người làm, tự quyết toàn bộ | `intent-statement.md` (Q7 ở Intent Capture) | Không có bước chờ duyệt nội bộ ngoài các cổng của quy trình |

## Ràng buộc pháp lý / tuân thủ

| ID | Ràng buộc | Nguồn | Ảnh hưởng |
|---|---|---|---|
| RC-01 | Không có yêu cầu quy định hay dữ liệu cá nhân | Q2 = A | Không cần che dữ liệu, phân quyền hay nhật ký truy cập |
| RC-02 | Dữ liệu đã ẩn danh; dashboard chỉ chạy localhost | Q2 = A | Không phát sinh nghĩa vụ công bố hay lưu trữ dữ liệu cá nhân |

## Ràng buộc ngân sách

| ID | Ràng buộc | Nguồn | Ảnh hưởng |
|---|---|---|---|
| BC-01 | Chỉ công cụ/thư viện mã nguồn mở, miễn phí | `build-vs-buy.md` (Q4 ở Market Research) | Loại nhóm thương mại khỏi phần triển khai |
| BC-02 | Không chi phí hạ tầng | Q6 = A, Q5 = A | Toàn bộ chạy trên máy cá nhân |
