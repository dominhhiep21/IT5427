# Alarms

Nguồn: `dashboards.md`, `../../construction/ci-pipeline/quality-gates.md`, `../../construction/{u1-statistics,u2-model,u3-display}/infrastructure-design/monitoring-design.md`.

## Không có alarm, và đây là lý do cụ thể

Alarm tồn tại để đánh thức một người. Ở dự án này **không có ai trực**: người chạy là người dùng duy nhất, và họ biết lệnh vừa chạy hỏng ngay khi nó hỏng — vì exit code nằm trong terminal trước mặt họ.

Một alarm gửi tới người không trực là nhiễu, và nhiễu làm người ta bỏ qua cả những cảnh báo thật.

## Thứ đóng vai alarm

| Tín hiệu | Ai thấy | Khi nào |
|---|---|---|
| Mã thoát 1 của `run --stage all` hoặc `--stage stats` | người chạy, ngay lập tức | lỗi dữ liệu, `QualityGate` hỏng, `KpiMismatchError` |
| Dòng `stats_write_failed` trong nhật ký | người chạy, khi tra | ghi tệp hỏng |
| Dòng `stats_test_skipped` | người chạy, khi tra | một phép kiểm định bị bỏ |
| Tab hiện `loi` hoặc `rong` hoặc `mot-phan` | người đọc báo cáo | tệp hỏng, chưa có, hoặc thiếu khối |
| CI đỏ trên nhánh | người làm, qua GitHub | bất kỳ bước nào hỏng |

## Ngưỡng duy nhất đáng gọi là "cảnh báo"

`auc_below_target = true` — nhưng nó không phải alarm, nó là **nội dung báo cáo**: tab hiện "không đạt mốc 0,70" và người đọc tự quyết định. Đánh thức ai đó vì mô hình yếu là sai loại tín hiệu: chất lượng mô hình là mục tiêu cải tiến, không phải sự cố.

## Điều không có

Không CloudWatch alarm, không PagerDuty, không Slack webhook, không on-call rotation. Không có ai để gọi.
