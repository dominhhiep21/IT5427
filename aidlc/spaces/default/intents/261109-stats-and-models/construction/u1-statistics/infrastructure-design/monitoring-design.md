# Monitoring Design — u1-statistics

Nguồn: `../nfr-design/observability-design.md`, `../nfr-requirements/observability-requirements.md`.

## Phạm vi

Không có dịch vụ thường trực nên không có dashboard, không có alert, không có SLO theo thời gian. "Giám sát" của đơn vị này là **đọc được ba câu trả lời sau một lần chạy**: mất bao lâu, bỏ qua kiểm định nào và vì sao, và có ghi được tệp không.

## Nguồn thông tin

| Nguồn | Chứa gì | Ai đọc |
|---|---|---|
| `logs/*.jsonl` | Bốn sự kiện của tầng `stats` (OD-2). Hàm `prune_logs` chỉ giữ 10 tệp gần nhất, nên một lần chạy cũ có thể đã bị dọn | Người chạy, khi cần tra một lần chạy gần đây |
| `data/reports/analysis.json` | Kết quả đầy đủ, kể cả `skipped` | Tab kết quả, và người đọc báo cáo |
| Mã thoát của lệnh | 0 nếu ghi được tệp, 1 nếu không | Chuỗi xác nhận bốn bước, CI |

## Ba câu hỏi và chỗ trả lời

| Câu hỏi | Trả lời ở đâu |
|---|---|
| Lần chạy này mất bao lâu? | `stats_finished`, thời lượng trong `event` |
| Kiểm định nào không chạy, vì sao? | `StatsBlock.skipped` trong tệp báo cáo; `stats_test_skipped` trong nhật ký |
| Có ghi được tệp không? | Mã thoát, và `stats_write_failed` nếu hỏng |

## Không đặt

- **Không alert.** Không có ai trực, và một cảnh báo gửi tới người không trực là nhiễu.
- **Không SLO.** Mốc 5 phút là ngân sách nghiệm thu trong test, không phải cam kết vận hành; biến nó thành SLO sẽ là hứa một thứ không có ai theo dõi.
- **Không bảng điều khiển riêng.** Tab kết quả do U3 dựng chính là bảng điều khiển của đơn vị này.

## Kiểm khi viết mã

Hai phép kiểm ở `../nfr-requirements/observability-requirements.md` § "Điều phải kiểm khi viết mã" là điều kiện nghiệm thu: đúng một sự kiện bắt đầu và một kết thúc mỗi lần chạy cùng `run_id`, và số sự kiện bỏ qua bằng `len(skipped)`.
