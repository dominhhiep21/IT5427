# Observability Design — u1-statistics

Nguồn: `../nfr-requirements/observability-requirements.md` (OBS-1…OBS-4), `../functional-design/rules.md` (BR1.6, BR1.11).

## Quyết định

| # | Quyết định | Phục vụ | Vì sao |
|---|---|---|---|
| OD-1 | Dùng đúng bộ trường mà logger hiện có phát ra; không thêm trường riêng cho tầng `stats` | OBS-1…OBS-4 | Công cụ đọc nhật ký không phải học thêm một hình dạng |
| OD-2 | Bốn sự kiện: bắt đầu, kết thúc (kèm thời lượng trong `event`), mỗi lần bỏ qua một kiểm định, và lỗi khi ghi tệp | OBS-1…OBS-4 | Đủ để trả lời "chạy mất bao lâu, bỏ qua cái gì, hỏng ở đâu" |
| OD-3 | Lý do bỏ qua **không** chỉ nằm trong nhật ký mà nằm trong chính báo cáo (`StatsBlock.skipped`) | OBS-3 | Nhật ký là thứ đọc tạm; báo cáo là thứ được lưu và được U3 hiển thị |
| OD-4 | Không metric, không tracing, không dashboard | — | Tiến trình chạy theo lệnh; thứ người đọc cần là tệp báo cáo |

## Sự kiện

| Sự kiện | Khi nào | Nội dung trong `event` |
|---|---|---|
| `stats_started` | Tầng bắt đầu | Định nghĩa doanh thu đang dùng |
| `stats_finished` | Tầng xong, trước khi trả đường dẫn | Số phép đã chạy, số phép bị bỏ, thời lượng |
| `stats_test_skipped` | Mỗi phần tử của `skipped` | Tên phép và lý do, nguyên văn như trong báo cáo |
| `stats_write_failed` | Ghi hoặc đọc lại hỏng, trước khi ném | Đường dẫn và lý do; dùng hàm ghi lỗi sẵn có kèm `error_code` |

## Tương quan

`run_id` là khoá tương quan duy nhất: mọi sự kiện của một lần chạy mang cùng một `run_id`, nên ghép được với các tầng khác trong cùng lần `--stage all` mà không cần thêm trường.

## Điều không làm

- Không ghi từng phép kiểm định thành một sự kiện: bốn dòng mỗi lần chạy không trả lời câu hỏi nào mà bốn sự kiện trên chưa trả lời.
- Không ghi đường dẫn dữ liệu vào nhật ký khi thành công: nó là hằng số trong `AppConfig`, và lặp lại nó ở mọi lần chạy chỉ làm loãng tệp.
