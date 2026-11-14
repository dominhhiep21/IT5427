# Bolt Plan

Nguồn: `../units-generation/unit-of-work.md`, `../units-generation/unit-of-work-dependency.md`, `../contract-design/contract-summary.md`, `../requirements-analysis/requirements.md`, `../practices-discovery/team-practices.md`, `../domain-design/components.md`, và `delivery-planning-questions.md`.

## Bolt 1 — Nền tính toán (U1 + U2)

- **Đơn vị:** U1 (u1-statistics) và U2 (u2-model). [Q1]
- **Vì sao gộp:** hai đơn vị dùng chung kiểu báo cáo và chung tầng `stats`; tách ra thì mỗi đợt phải chờ một bản hợp đồng chưa hoàn chỉnh.
- **Định nghĩa xong:** chạy `python -X utf8 -m src.pipeline run --stage stats`, báo cáo phiên bản 2 có cả hai khối, mọi kiểm định không chạy được đều có lý do trong `skipped` và mỗi phép so sánh bang mang số đơn bị loại; `pytest -m "not slow"` xanh; `ruff` sạch; chuỗi xác nhận bốn bước chạy đúng.
- **Giả thuyết:** chứng minh rằng mart và DuckDB đủ cho cả kiểm định lẫn huấn luyện, và cách chia theo thời gian cho AUC ≥ 0,70.

## Bolt 2 — Hiển thị (U3)

- **Đơn vị:** U3 (u3-display). [Q1]
- **Vì sao sau:** tab đọc báo cáo do Bolt 1 sinh; làm trước thì không có dữ liệu thật để kiểm.
- **Định nghĩa xong:** tab mới hiện đủ các trạng thái của hàm đọc trên báo cáo thật, kể cả trạng thái rỗng `rong` khi chưa có tệp (không mượn trạng thái lỗi `loi`); ba test hình dạng dashboard đã cập nhật; `pytest -m "not slow"` xanh; xem bằng mắt ở 1280px.
- **Giả thuyết:** chứng minh rằng báo cáo đủ thông tin để hiển thị mà tab không phải tính toán gì.

## Thứ tự

Bolt 1 → Bolt 2, đúng thứ tự U1 → U2 → U3 đã chốt. [Q2] DAG là một chuỗi nên không có đợt nào chạy song song.

## Nhịp

Mỗi đợt khoảng một ngày. [Q5] Sau mỗi đợt chạy chuỗi xác nhận bốn bước rồi mới sang đợt kế. [Q4] Dừng ở mỗi mốc để người làm duyệt. [Q3]
