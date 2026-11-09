# Health Check Report — local release 2026-11-09

## 1. Sức khoẻ của lần chạy

| Tín hiệu | Giá trị | Ngưỡng | Kết luận |
|---|---|---|---|
| Tầng pipeline chạy thành công | 6/6 | 6/6 | đạt |
| Thời gian toàn pipeline | ~18,3 s (5,12 + 4,97 + 0,45 + 3,46 + 3,98 + 0,29) | không đặt trần | bình thường |
| Bản ghi bị loại khi nạp đơn | 0 | < 1% số dòng | đạt |
| `KpiReconciler` | 5 KPI lệch 0 | 0 | đạt |
| `QualityGate` chế độ `full` | xanh | xanh | đạt |
| Phủ dòng | 90,69% | ≥ 80% | đạt |
| `ruff` | 0 vi phạm | 0 | đạt |

## 2. Tín hiệu cần theo dõi tiếp

- **Bộ nhớ**: `config.yaml` đặt `quality.memory_warn_mb: 1536` và `memory_fail_mb: 2048`. Lần chạy này không vượt ngưỡng (pipeline không báo cảnh báo bộ nhớ). Nếu sau này thấy cảnh báo, xem `src/common/memory.py`.
- **Nhật ký**: mỗi lần chạy sinh một tệp JSONL mang `run_id`; pipeline dọn còn 10 tệp gần nhất. Không có cơ chế xoay vòng khác.
- **Tệp ghép**: `data/integration/linkage-customer.json` ~4,07 MB, sát trần 5 MB. Nếu dữ liệu nguồn tăng, đây là chỗ vượt ngưỡng đầu tiên.

## 3. Không có gì để giám sát từ xa

Không có dịch vụ chạy nền, không có endpoint công khai, không có SLO theo thời gian. "Sức khoẻ" của hệ này là kết quả của lần chạy gần nhất cộng với việc người mở dashboard thấy số liệu đúng — không phải một bảng dashboard giám sát.

## 4. Việc phải làm nếu một tín hiệu đỏ

| Tín hiệu | Bước đầu tiên |
|---|---|
| Pipeline `success=False` | đọc `logs/<run_id>.jsonl`, lọc `level=ERROR`, xác định tầng hỏng |
| KPI lệch | **không** sửa baseline; xem `src/integrate/reconcile.py` và dữ liệu đầu vào |
| Phủ tụt dưới 80% | viết thêm test; **không** hạ `--cov-fail-under` |
| Tệp ghép vượt 5 MB | xem lại trần 10.000 cặp và phần `skipped` (chưa bị trần nào chặn) |
