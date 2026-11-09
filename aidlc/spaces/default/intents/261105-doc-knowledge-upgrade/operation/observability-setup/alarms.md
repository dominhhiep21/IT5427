# Alarms

## 1. Không có paging, không có kênh thông báo

Không có on-call, không có người thứ hai để gọi. "Cảnh báo" ở đây là **dấu hiệu phải dừng lại**, không phải tin nhắn đẩy đi đâu.

## 2. Dấu hiệu phải dừng (thay cho alarm)

| Dấu hiệu | Ở đâu | Phải làm gì |
|---|---|---|
| `pipeline.completed` với `success=False` | `logs/*.jsonl` | dừng, đọc ERROR cùng `run_id` |
| Bất kỳ dòng `"level":"ERROR"` | `logs/*.jsonl` | đọc `event` và `message`; không bỏ qua |
| `KpiReconciler` báo lệch | `data/reports/` | **không** sửa baseline; điều tra dữ liệu đầu vào |
| `QualityGate` đỏ | `data/reports/quality.json` | dừng; đây là cổng dữ liệu |
| `integration.query.slow` | `logs/*.jsonl` | ghi nhận, không chặn; xem lại nếu lặp lại nhiều lần |
| `integration.load.retried` | `logs/*.jsonl` | bình thường nếu hiếm; lặp liên tục là dấu hiệu đĩa |
| Cổng đối chiếu lát cắt đỏ | `pytest tests/unit/test_integration_correctness.py -m slow` | dừng ngay: số liệu sai, không phải lỗi hiển thị |

## 3. Ngưỡng của những gì đã có

- **Bộ nhớ**: `quality.memory_warn_mb: 1536`, `memory_fail_mb: 2048` trong `config.yaml`.
- **Truy vấn chậm**: `SLOW_QUERY_MS = 2000` trong `src/integration/rewrite.py` — chỉ ghi WARNING, không chặn, vì BR3.8 chốt như vậy.
- **Tệp ghép**: trần 5 MB trong test; hiện 4,07 MB.
- **Nhật ký**: giữ 10 tệp gần nhất, dọn ở cuối mỗi lần chạy.

## 4. Điều không làm

- Không thêm dịch vụ thông báo (email, Slack, webhook): không có người nhận thứ hai, và NFR6 cấm gọi mạng từ dashboard.
- Không đặt alarm theo thời gian (ví dụ "quá 5 phút không có dữ liệu"): không có scheduler chạy nền.
