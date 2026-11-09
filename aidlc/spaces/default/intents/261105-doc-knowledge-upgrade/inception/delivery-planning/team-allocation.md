# Team Allocation — Nâng cấp tích hợp dữ liệu Olist

Một **mob** ở đây là nhóm người cùng làm một Bolt; với dự án này, "nhóm" chỉ gồm một người cộng các agent AI hỗ trợ.

## Phân bổ

| Bolt | Đơn vị | Người thực hiện | Ghi chú |
|---|---|---|---|
| Bolt 1 | U1 | Chủ dự án + aidlc-developer-agent | Lát cắt mỏng; cần người quyết định khi lược đồ tối thiểu phải mở rộng |
| Bolt 2 | U2 | Chủ dự án + aidlc-developer-agent | Việc chủ yếu là khai báo và kiểm tra dữ liệu |
| Bolt 3 | U5 | Chủ dự án + aidlc-developer-agent | Khối lượng nhỏ nhất trong sáu Bolt |
| Bolt 4 | U3 | Chủ dự án + aidlc-developer-agent + aidlc-architect-agent (khi cần) | Bolt rủi ro nhất; cần ý kiến kiến trúc nếu lược đồ phải đổi |
| Bolt 5 | U4 | Chủ dự án + aidlc-developer-agent | Có thể đổi chỗ với Bolt 4 nếu Bolt 4 bị kẹt |
| Bolt 6 | U6 | Chủ dự án + aidlc-design-agent (khi cần) | Kiểm tiếp cận và bố cục |

## Ghi chú về cách làm việc

- Bước Team Formation đã được bỏ qua vì là dự án một người; không có mob nhiều người, không có luân phiên driver.
- Người thực hiện quyết định mọi thay đổi phạm vi; không có bước phê duyệt nội bộ ngoài các cổng của quy trình.
- Mỗi Bolt kết thúc bằng lệnh xác nhận của dự án, chạy tuần tự; không có Bolt nào chạy song song vì người thực hiện đã chọn làm tuần tự.

## Năng lực và khoảng trống

| Năng lực | Mức hiện tại | Ghi chú |
|---|---|---|
| Python, pandas, DuckDB | Có sẵn | Nền của toàn bộ hệ thống |
| Plotly Dash | Có sẵn | Ba tab hiện có |
| Dash Mantine Components | Chưa có | Sẽ ghim vào `requirements.txt` ở Bolt 6 |
| `ruff` (lint + format) | Chưa có | Sẽ ghim ở Bolt 1 và dùng cho mọi Bolt sau |
| Ghép bản ghi xác suất | Chưa có | Thuật toán tự viết ở Bolt 5; thư viện so khớp chuỗi thêm nếu cần |
