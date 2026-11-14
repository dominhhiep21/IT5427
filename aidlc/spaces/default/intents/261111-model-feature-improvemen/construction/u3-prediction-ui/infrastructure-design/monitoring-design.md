# Monitoring Design — u3-prediction-ui

Nguồn: `../nfr-design/security-design.md` (SD3.4, SD3.5), `../nfr-design/logical-components.md` (§3 miền lỗi), `src/common/logging.py`, `src/analytics/report.py`, `../../../../memory/team.md` `## Deployment`.

## 1. Cái đã có, không xây lại

Repo **không** có Prometheus/Grafana/APM. Tín hiệu vận hành hiện có, và đủ cho một công cụ chạy localhost:

| ID | Tín hiệu | Nơi | Nội dung |
|---|---|---|---|
| MON3.1 | Nhật ký JSONL mỗi lần chạy | `logs/*.jsonl` (gốc repo — `config.yaml` → `logs_dir`) | `run_id` (`<UTC>-%Y%m%dT%H%M%S>-<8 hex>`), `timestamp`, `level`, `stage`, `event`; `prune_logs` giữ 10 tệp gần nhất cho lượt chạy pipeline |
| MON3.2 | Trạng thái báo cáo | `analysis.json` → `ReportView.status` | `rong`, `loi`, `mot-phan`, `day-du` — cũng là thứ giao diện hiển thị |
| MON3.3 | Nhật ký trạng thái tab | hiện không có | tab chỉ hiển thị, không ghi — giữ nguyên |
| MON3.4 | Cổng kiểm tra sau khi chạy | `QualityGate`, `KpiReconciler` trong `run_stage` | 21 + 9 + 10 check; pipeline chỉ xanh khi hai cổng xanh |

## 2. Bổ sung của đơn vị này

| ID | Tín hiệu mới | Nơi ghi | Mức | Ghi chú |
|---|---|---|---|---|
| MON3.5 | `prediction.model_unavailable` | tệp `logs/*.jsonl` mới nhất (qua `_integration_logger(config)` của `app.py`) | `warning` | ghi khi LC3.11 hoặc LC3.5 không nạp được tệp mô hình; kèm **thông điệp thô** của `ModelError` (chỉ trong nhật ký — SD3.4) |
| MON3.6 | `prediction.scored` | cùng nơi | `info` | chỉ ghi `verdict` và `threshold`; **không** ghi 11 giá trị nhập (SD3.5) |
| MON3.7 | `prediction.input_rejected` | cùng nơi | `info` | chỉ ghi **danh sách id ô** sai, không ghi giá trị |

Tên sự kiện dùng **dấu chấm** như phần còn lại của repo (`integration.log.no_pipeline_run`, `model.saved`), không dùng gạch dưới.

Ba sự kiện dùng đúng `JsonLogger` mà dashboard đã có: `_integration_logger(config)` gắn vào tệp `*.jsonl` mới nhất trong `logs/`, hoặc mở `logs/integration-<run_id>.jsonl` khi thư mục rỗng; `stage="integration"`, `run_id = %Y%m%dT%H%M%S-<6 chữ số microsecond>`. Đây **không** phải `run_id` 8 hex của pipeline — khác định dạng, cùng khuôn `event/level/run_id`. Lưu ý: `prune_logs` glob **mọi** `*.jsonl` trong `logs/`, nên nó cũng dọn tệp integration theo thứ tự cũ-mới (giữ 10 tệp) — không có chính sách riêng cho tệp integration.

## 3. Cái cố ý **không** làm

| Không làm | Vì sao |
|---|---|
| Metrics endpoint, Prometheus, OpenTelemetry | công cụ localhost một người dùng; thêm hạ tầng quan sát là chi phí không có người trả |
| Truy vết phân tán | một tiến trình, không có lời gọi mạng |
| Alerting/email/Slack | không có kênh, không có người trực |
| Ghi lại giá trị biểu mẫu để "phân tích sử dụng" | là dữ liệu người dùng; SD3.5 cấm; không có yêu cầu nào |
| Dashboard riêng cho sức khoẻ khối dự đoán | khối đã có sáu trạng thái hiển thị đúng thứ người dùng cần biết |

## 4. SLI/SLO

Không đặt SLO phần trăm cho một công cụ chạy tay. Thay vào đó là ba chỉ số **đo được** trong test:

| Chỉ số | Ngưỡng | Đo ở đâu |
|---|---|---|
| Tỉ lệ dựng mục Dự đoán thành công khi báo cáo `day-du` | 100% (không ném) | test đơn vị + `try/except` ở `analysis_tab` |
| Tỉ lệ lần bấm trả kết quả hoặc câu lỗi có hướng dẫn (không im lặng) | 100% | test 6 trạng thái |
| Thời gian chấm một dòng | < 200 ms | PR3.1 |

## 5. Đọc nhật ký khi có sự cố

1. `logs/` → tệp mới nhất; lọc `event = prediction_model_unavailable`.
2. Nếu có: chạy `python -X utf8 -m src.pipeline run --stage stats` rồi mở lại tab.
3. Nếu không có mà khối vẫn trống: kiểm `analysis.json` (`status`, `model`), rồi `warehouse/olist.duckdb` tồn tại.
4. Nếu `prediction_input_rejected` xuất hiện nhiều: đọc danh sách id ô để biết ô nào bị từ chối — **không** có giá trị nào trong nhật ký, đúng thiết kế.

## 6. Truy vết yêu cầu

| Yêu cầu | Được đáp bởi |
|---|---|
| SR3.7 (không log giá trị người dùng) | MON3.6, MON3.7 |
| SD3.4 (lỗi mô hình chỉ vào nhật ký) | MON3.5 |
| PR3.5 (≤ 1 đọc báo cáo + ≤ 1 nạp mô hình mỗi lần bấm) | không phải tín hiệu nhật ký; kiểm bằng test giả lập |
| NFR3.1 (cổng phủ, CI) | `cicd-pipeline.md` CI3.2 |
