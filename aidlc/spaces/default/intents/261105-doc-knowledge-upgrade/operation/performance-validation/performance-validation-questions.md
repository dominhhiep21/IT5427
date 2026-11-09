# Performance Validation — câu hỏi

Không có câu hỏi mới. Stage này đối chiếu từng yêu cầu phi chức năng với số đo thật; không đặt thêm ngưỡng nào.

## Consolidated Summary Confirmation

Tóm tắt để bạn xác nhận:

1. **Không có load test theo nghĩa tải đồng thời**: một người dùng, không endpoint. "Tải" thật là khối lượng dữ liệu (1.550.922 dòng vào, 806.705 cặp ghép) và độ trễ từng thao tác.
2. **Pipeline chạy 6/6 tầng trong ~18,3 giây**: ingest 5,12 s, clean 4,97 s, quality 0,45 s, integrate 3,46 s, linkage 3,98 s, analyze 0,29 s.
3. **Ghép bản ghi 3,98 s cho 806.705 cặp** (ngưỡng 60 s), tệp kết quả **4,07 MB** (trần 5 MB — biên mỏng nhất của hệ).
4. **Phủ 90,69%**, `ruff` sạch, 5 KPI lệch 0, số trên vùng khớp phép tính độc lập 0 sai lệch.
5. **14 chỉ tiêu NFR**: 13 đạt bằng số đo máy; NFR4 (tiếp cận) đạt bằng rà tay, chưa có test tự động — ghi là khoảng trống, không phải bỏ qua.
6. **Không đo p95/p99 và không giả lập nhiều người dùng**: phân vị chỉ có nghĩa khi có phân bố; kiến trúc không hỗ trợ tải đồng thời.

Does this all look correct?

- A. Looks correct
- B. Request changes

[Answer]: Looks correct