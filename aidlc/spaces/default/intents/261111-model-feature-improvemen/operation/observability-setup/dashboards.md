# Dashboards — intent `261111-model-feature-improvemen`

## 1. Không có dashboard giám sát, và đó là quyết định

Repo chạy trên **một máy Windows local**, một người dùng, không có dịch vụ nền. `monitoring-design.md` của U3 (§3) đã chốt: không metrics endpoint, không Prometheus/Grafana, không OpenTelemetry. Thêm một dashboard giám sát cho một tiến trình bind `127.0.0.1` là hạ tầng không có người trả.

## 2. "Dashboard" đang có, dưới dạng khác

| Thứ đóng vai dashboard | Ở đâu | Cho biết gì |
|---|---|---|
| Tab "Kết quả phân tích" | `src/dashboard/analysis_tab.py` | trạng thái báo cáo (`rong`/`loi`/`mot-phan`/`day-du`), 4 thẻ tóm tắt, 5 phép kiểm định, khối mô hình, mục Dự đoán |
| Dòng trạng thái của tab | `ResultTabState` | lý do khi thiếu dữ liệu, kèm lệnh cần chạy |
| Nhật ký JSONL | `logs/*.jsonl` | mỗi lượt chạy pipeline: `run_id`, `stage`, `event`, `level`; chart không cần thiết vì mỗi lượt là một dòng thời gian |
| Kết quả `QualityGate`/`KpiReconciler` | `data/reports/*.json` | 21 + 9 + 10 check cấu trúc và 5 KPI |

## 3. Nếu sau này cần dashboard thật

Điều kiện tiên quyết: có môi trường chạy dài hạn (staging/production). Khi đó mới đáng dựng metrics endpoint + một dashboard bốn ô: (a) số lượt chạy theo ngày, (b) tỉ lệ lượt chạy đỏ, (c) thời gian tầng `stats`, (d) số lần `prediction.model_unavailable`. Hiện tại cả bốn đọc được bằng tay từ `logs/` trong vài giây.

## 4. Nguồn của các con số trên

| Nguồn | Dùng cho |
|---|---|
| `../construction/u3-prediction-ui/nfr-design/performance-design.md` (PD3.1–PD3.6, PR3.1–PR3.5) | ngân sách thời gian và hình dạng tải mà dashboard sẽ hiển thị nếu có |
| `../construction/u3-prediction-ui/nfr-design/security-design.md` (SD3.4, SD3.5, SD3.7) | quy định cái gì **không** được hiện ra dashboard/nhật ký: giá trị biểu mẫu, đường dẫn tuyệt đối |
| `../construction/u3-prediction-ui/infrastructure-design/infrastructure-specification.md` (INF3.3–INF3.6, INF3.13) | vòng đời tệp và việc **không** thêm dịch vụ nền; cũng là lý do không có dashboard giám sát riêng |
| `../construction/u3-prediction-ui/infrastructure-design/monitoring-design.md` (MON3.1–MON3.7) | ba sự kiện `prediction.*` và nơi ghi của chúng |
