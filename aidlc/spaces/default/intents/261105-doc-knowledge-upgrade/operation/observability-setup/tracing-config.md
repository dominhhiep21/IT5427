# Tracing Config

## 1. Không có distributed tracing

Không có nhiều tiến trình, không có gọi mạng giữa các dịch vụ, không có OpenTelemetry, không có X-Ray. Thêm tracing vào một tiến trình duy nhất là chi phí không đổi lấy thông tin nào.

## 2. `run_id` đóng vai trace id

Mỗi lần chạy pipeline sinh một `run_id`. Mọi sự kiện của lần chạy đó mang cùng `run_id`, cùng `stage`, và `timestamp`. Đó là đủ để dựng lại trình tự:

```powershell
$run = "20261109T042432-42e24658"
Get-Content "logs\$run.jsonl" | ForEach-Object { $_ }
```

Trình tự sự kiện của một lần chạy điển hình: `pipeline.started` → `stage.started`/`stage.completed` cho từng tầng → `pipeline.completed`. Trong tầng tích hợp: `integration.load.*`, `integration.query.*`, `integration.sources.*`, `integration.linkage.*`.

## 3. Tương quan giữa dashboard và nhật ký

- Dashboard (phiên) có `RunContext` riêng với `run_id` dạng `<YYYYMMDDTHHMMSS>-<micro>` và `stage="integration"`, ghi nối vào tệp nhật ký mới nhất hoặc mở tệp `integration-<run_id>.jsonl`.
- Kết quả truy vấn mang `plan_id` (sinh mỗi lần chạy), nên đối chiếu được một con số trên màn hình với một dòng nhật ký cụ thể.

## 4. Khi nào mới cần tracing thật

Khi hệ tách thành nhiều tiến trình hoặc gọi dịch vụ ngoài thường xuyên. Hiện chỉ có một lời gọi ngoài có điều kiện (IBGE, trong `integrate`), và nó nằm trong `run_id` của pipeline — không cần span riêng.
