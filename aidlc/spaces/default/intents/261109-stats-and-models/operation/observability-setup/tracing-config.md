# Tracing Configuration

Nguồn: `log-queries.md`, `../../construction/u1-statistics/nfr-design/observability-design.md`.

## Không có distributed tracing, và lý do là cấu trúc

Tracing tồn tại để nối các chặng của **một request đi qua nhiều tiến trình**. Dự án này chạy toàn bộ trong **một tiến trình, một tệp, một lần chạy**. Không có chặng nào để nối.

## Thứ đóng vai tracing: `run_id`

`run_id` là khoá tương quan duy nhất và nó làm đúng việc tracing cần làm ở đây:

| Tracing thường cho gì | `run_id` cho gì |
|---|---|
| Nối các span của một request | Nối mọi sự kiện của một lần chạy `--stage all` |
| Xác định chặng chậm | Xác định tầng nào chạy lâu qua `stats_finished` |
| Nối qua nhiều dịch vụ | Nối các tầng `ingest → clean → integrate → analyze → stats` trong cùng tệp log |

Mọi sự kiện của một lần chạy mang cùng `run_id`, nên ghép được với các tầng khác mà không cần thêm trường nào. Đó cũng là lý do Q3 = A chốt "chỉ dùng đúng các trường hàm ghi hiện có".

## Điều không có

Không OpenTelemetry, không X-Ray, không Jaeger, không span, không trace ID riêng. Thêm chúng cho một tiến trình đơn là thêm một lớp mà không ai đọc.

## Khi nào cần tracing thật

Nếu mức B của đợt cải thiện đặc trưng biến mô hình thành một API có người gọi từ ngoài, lúc đó mới có request để trace — và lúc đó `run_id` không còn đủ. Việc thêm tracing thuộc đợt đó, không thuộc đợt này.
