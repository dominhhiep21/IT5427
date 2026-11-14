# Incident Response — Câu hỏi

Stage này không có lựa chọn nào cần bạn quyết định: quy mô một người, một máy local đã chốt mức độ và cách phản ứng. Dưới đây là bản tóm tắt để bạn xác nhận.

## Consolidated Summary Confirmation

- **Tám runbook** cho tám sự cố thật xảy ra được: báo cáo `loi`, mô hình chưa sẵn, cổng dữ liệu đỏ, cổng phủ đỏ, mốc sàn đỏ, dashboard không bind được, ca nhạy tải của `linkage`, và hoàn nguyên một thay đổi.
- **Bốn mức P1–P4** hạ theo quy mô một người: P1 = số liệu sai có thể dẫn tới quyết định sai (hoặc `dataset/` bị đụng), P2 = bề mặt chính không dùng được, P3 = cổng đỏ nhưng kết quả vẫn đúng, P4 = khó chịu.
- **Năm điều cấm khi xử lý sự cố:** hạ cổng phủ, cập nhật baseline/allowlist không ghi lý do, hạ `MODEL_AUC_FLOOR`, sửa `dataset/`, nới ngưỡng thời gian ngầm.
- **Ma trận leo thang cố ý trống phần on-call/SLA/kênh thông báo** — không có người thứ hai và không có dịch vụ nền; ghi rõ điều kiện phải đổi (có người thứ hai hoặc có môi trường chạy tự động).
- **Sau P1/P2 phải có test canh** nếu lỗi tái phát được, ghi vào `test-results.md`.

Does this all look correct?

[Answer]: Looks correct
