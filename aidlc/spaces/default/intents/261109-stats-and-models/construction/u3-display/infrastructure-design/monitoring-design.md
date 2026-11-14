# Monitoring Design — u3-display

Nguồn: `../nfr-design/performance-design.md`, `../nfr-design/logical-components.md`, `../nfr-requirements/performance-requirements.md`.

## Phạm vi

Tab chạy trong tiến trình Dash cục bộ, một người dùng. Không có dịch vụ thường trực nên không có dashboard giám sát, không alert, không SLO. "Giám sát" ở đây là **ba câu trả lời sau khi mở tab**.

## Ba câu hỏi và chỗ trả lời

| Câu hỏi | Trả lời ở đâu |
|---|---|
| Tab đang ở trạng thái nào? | Chính màn hình: `rong`, `mot-phan`, `loi`, `day-du`, `chua-chay` — mỗi trạng thái có câu chữ riêng (BR3.5) |
| Kiểm định nào không chạy, vì sao? | Dải `skipped` trong tab (BR3.6), cùng dữ liệu với `StatsBlock.skipped` |
| Báo cáo có mới không? | Trường `generated_at` của báo cáo, hiện ở dải tóm tắt |

## Nguồn thông tin

| Nguồn | Chứa gì | Ai đọc |
|---|---|---|
| Màn hình tab | Trạng thái, số liệu, phần thiếu | Người đọc báo cáo |
| `logs/*.jsonl` | Sự kiện của tầng `stats` đã sinh báo cáo | Người chạy, khi cần tra |

Tab **không tự ghi nhật ký**: nó chỉ đọc. Một tab ghi log riêng sẽ tạo nguồn thứ hai cho cùng một sự thật.

## Không đặt

- **Không alert.** Không ai trực; cảnh báo gửi tới người không trực là nhiễu.
- **Không SLO.** Mốc 1 giây là ngân sách nghiệm thu đo trong test, không phải cam kết vận hành.
- **Không bảng điều khiển riêng.** Tab này chính là bảng điều khiển.

## Kiểm khi viết mã

- Một test khẳng định tab dựng đúng một trong năm trạng thái và mỗi trạng thái có câu chữ riêng.
- Một test khẳng định `generated_at` của báo cáo được hiện ở dải tóm tắt.
