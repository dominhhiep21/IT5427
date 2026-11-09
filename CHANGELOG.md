# Changelog

Mỗi mốc phát hành một mục `## v0.<n>.<m> — YYYY-MM-DD` với ba nhóm **Thêm**, **Sửa**, **Nội bộ**.
Nội dung viết cho người đọc: cái gì thay đổi với người dùng trước, chi tiết kỹ thuật sau.

## v0.1.0 — 2026-11-06

### Thêm

- Tab **Tích hợp** trên dashboard, mở đầu bằng thẻ "Số đơn theo tháng": tổng số đơn và số đơn
  từng tháng tách theo trạng thái, kèm thời gian chạy truy vấn và nhãn cho biết đang xem
  kết quả đầy đủ, một phần, rỗng hay lỗi.
- Tệp khai báo lược đồ trung gian `config/mediated-schema.yaml` với thực thể `don_hang`; bốn
  trường của bảng đơn được nạp, `bang_giao` mới chỉ được kiểm cột nguồn.
- Tệp cấu hình tab `config/integration-tab.yaml` khai id ổn định cho bốn thẻ tổng quan và
  khối kết quả, để đơn vị sau mở rộng mà không phải đặt lại tên.
- Workflow CI (`.github/workflows/ci.yml`) chạy lint, dựng dữ liệu và bộ test nhanh trên
  `windows-2022`.

### Sửa

- Dashboard nay có bốn tab; tab mới có callback riêng nên lỗi ở tab này không làm hỏng ba tab cũ.
- `logs/` chỉ giữ 10 tệp nhật ký gần nhất sau mỗi lần chạy pipeline.

### Nội bộ

- Thêm `ruff` (ghim `0.17.4`) làm cổng lint + format; cấu hình ở `ruff.toml` với ngưỡng dòng
  112 ký tự.
- Thêm `src/integration/` (mô hình, đọc lược đồ, nạp dữ liệu, viết lại + chạy truy vấn, thẻ).
- Đơn vị không có API HTTP; đầu vào duy nhất của tab là callback Dash.
