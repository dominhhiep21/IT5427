# Observability Setup — Câu hỏi

**Không có câu hỏi lựa chọn.** Stage này không đưa ra quyết định nào cần người làm chọn: hiện trạng quan sát đã được chốt từ trước trong `construction/u3-prediction-ui/infrastructure-design/monitoring-design.md` (nhật ký JSONL + ba sự kiện `prediction.*`, không metrics/tracing/alerting) và `team.md` `## Deployment` (một máy local, không dịch vụ nền).

Các tệp trong thư mục này ghi lại **đúng cái đang có** và nói rõ cái cố ý không xây, kèm điều kiện để xây sau nếu hoàn cảnh đổi (có môi trường chạy dài hạn, có lịch chạy, có nhiều tiến trình).

## Consolidated Summary Confirmation

Tóm tắt những gì stage này ghi nhận:

- **Không có dashboard giám sát, không alarm, không tracing, không phát hiện dị thường tự động** — vì không có dịch vụ nền, không có người trực, không có lịch chạy.
- **Cái thay thế đang chạy thật:** nhật ký JSONL trong `logs/` (mỗi lượt một `run_id`, ba sự kiện `prediction.model_unavailable` / `.scored` / `.input_rejected`); tab phân tích với bốn trạng thái báo cáo; `QualityGate` (21 + 9 + 10 check) và `KpiReconciler` (5 KPI) làm cổng chặn.
- **SLI đo được thay cho SLO phần trăm:** dữ liệu khớp baseline, `beats_floor` đúng, `score_item` < 200 ms, `load_model` < 2 s, dựng khối < 300 ms, và báo cáo không ở trạng thái `loi` sau một lượt `--stage stats` xanh.
- **Điều kiện để xây thêm** đã ghi rõ ở từng tệp: có môi trường chạy dài hạn → dashboard + alarm; có ≥ 30 lượt chạy đều → đường cơ sở cho phát hiện dị thường; có ≥ 2 tiến trình gọi nhau → tracing.
- **Không thêm phụ thuộc, không thêm bảng, không thêm dịch vụ** trong đợt này.

Does this all look correct?

[Answer]: Looks correct

