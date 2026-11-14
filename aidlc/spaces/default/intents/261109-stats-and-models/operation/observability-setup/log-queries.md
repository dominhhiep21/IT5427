# Log Queries

Nguồn: `../../construction/{u1-statistics,u2-model}/infrastructure-design/monitoring-design.md`, `../../construction/u3-display/nfr-design/observability-design.md`, `src/common/logging.py`.

## Nhật ký hiện có

JSONL trong `logs/`, mỗi dòng một sự kiện với `timestamp`, `level`, `run_id`, `stage`, `event`. `prune_logs` giữ **10 tệp gần nhất**.

Bốn sự kiện của tầng `stats`: `stats_started`, `stats_finished`, `stats_test_skipped`, `stats_write_failed`.

## Truy vấn dùng thật

Không có ngôn ngữ truy vấn log ở đây; log là tệp cục bộ, nên "truy vấn" là đọc bằng mắt hoặc bằng một lệnh một dòng.

| Câu hỏi | Cách tra |
|---|---|
| Lần chạy này mất bao lâu? | tìm `stats_finished` cùng `run_id`, đọc thời lượng trong `event` |
| Có kiểm định nào bị bỏ? | tìm `stats_test_skipped`; lý do cũng nằm trong `StatsBlock.skipped` của báo cáo |
| Ghi tệp có hỏng không? | tìm `stats_write_failed`; nếu có thì tầng đã ném ở biên CLI |
| Tầng nào chạy trong lần này? | gom theo `stage`, đếm `event` |

## Vì sao không đi xa hơn

Lý do bỏ qua kiểm định **đã có chỗ đứng chính thức trong báo cáo** (`StatsBlock.skipped`), nên log chỉ cần chỉ đường chứ không phải chở dữ liệu. Một công cụ truy vấn log cho 10 tệp cục bộ là thêm một hệ thống để bảo trì mà không thêm câu trả lời nào.

## Điều không có

Không CloudWatch Logs Insights, không Elasticsearch, không Loki, không truy vấn có ngôn ngữ riêng. Không có gì để tổng hợp trên nhiều máy.
