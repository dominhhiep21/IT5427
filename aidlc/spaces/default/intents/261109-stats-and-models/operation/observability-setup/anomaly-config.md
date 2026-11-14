# Anomaly Configuration

Nguồn: `alarms.md`, `slo-config.md`, `../../construction/build-and-test/test-results.md`, `../../construction/u1-statistics/nfr-design/reliability-design.md`.

## Không có phát hiện dị thường tự động, và có một lý do kỹ thuật

Phát hiện dị thường cần **một chuỗi thời gian để học đường cơ sở**. Dự án này chạy theo lệnh, mỗi lần một ảnh chụp; không có chuỗi, không có gì để học "bình thường là gì".

## Thay thế: ngưỡng tuyệt đối, đã có sẵn

| Thứ có thể bất thường | Cách bắt | Ở đâu |
|---|---|---|
| Số dòng bảng nguồn / mart lệch | 9 check số dòng của `StarSchemaValidator` | `--stage all` |
| 5 KPI baseline lệch | `KpiReconciler` với dung sai riêng | `--stage all` |
| Dị thường dữ liệu đã biết | allowlist 10 mục trong `src/quality/allowlist.py` | `quality` chế độ `full` |
| Giá trị ngoài miền | check `D-` (miền giá trị) | `QualityGate` |
| Bộ nhớ vượt ngưỡng | `MemoryProbe` so với `quality.memory_fail_mb` | test `slow` |
| Mô hình thoái hoá | AUC dưới mốc, ghi bằng `auc_below_target` | báo cáo |

Đây là **ngưỡng tuyệt đối**, không phải học từ dữ liệu — và với dữ liệu bất biến, ngưỡng tuyệt đối là công cụ đúng: baseline không trôi, nên một ngưỡng cố định không bao giờ lạc hậu.

## Điều đáng chú ý

Cái bẫy của phát hiện dị thường là nó báo động khi dữ liệu đổi — mà ở dự án này dữ liệu **không được phép đổi**. Nếu `dataset/` đổi, đó không phải dị thường cần phân tích, đó là lỗi quy trình: `dataset/` là bất biến.

## Điều không có

Không CloudWatch Anomaly Detection, không mô hình học đường cơ sở, không cảnh báo theo độ lệch chuẩn.
