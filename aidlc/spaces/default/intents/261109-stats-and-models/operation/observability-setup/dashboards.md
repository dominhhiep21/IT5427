# Dashboards

Nguồn: `../../construction/{u1-statistics,u2-model,u3-display}/infrastructure-design/monitoring-design.md`, `../../construction/u3-display/nfr-design/observability-design.md`.

## Không có dashboard giám sát riêng, và đó là quyết định

Không có dịch vụ thường trực nên không có metric theo thời gian để vẽ. Một dashboard giám sát cho một tiến trình chạy 5 phút là một khung hình trống có trục thời gian.

## Thứ đóng vai dashboard

**Tab kết quả trên dashboard hiện có** — nó chính là bảng điều khiển của hệ thống này, và nó hiện đúng những gì người đọc cần:

| Vùng | Hiện gì | Nguồn |
|---|---|---|
| Dải tóm tắt | tỉ lệ trễ, số đơn đã giao, số kiểm định bị bỏ, AUC kèm dấu đạt/không đạt | `StatsBlock`, `ModelBlock` |
| Mục thống kê | năm phép kiểm định, mục null hiện lý do | `StatsBlock` |
| Dải skipped | kiểm định nào không chạy và vì sao | `StatsBlock.skipped` |
| Mục mô hình | AUC, ngưỡng, precision, recall — chỉ đọc | `ModelBlock` |
| Trạng thái | `rong`, `mot-phan`, `loi`, `day-du`, `chua-chay` | `ReportView.status` |

## Vì sao không dựng thêm

- Bảng điều khiển thứ hai cho cùng một sự thật là chỗ thứ hai để lệch.
- Không có chuỗi thời gian: mỗi lần chạy là một ảnh chụp, không phải một điểm trên đồ thị.
- Muốn so sánh giữa các lần chạy thì đọc `generated_at` và các con số trong tệp báo cáo; không cần một công cụ thứ hai.

## Điều không có

Không CloudWatch, không Grafana, không Prometheus, không dashboard theo thời gian. Không có gì để hiển thị theo thời gian.
