# Log Queries — intent `261111-model-feature-improvemen`

Nhật ký là JSONL trong `logs/`, mỗi dòng một sự kiện có `timestamp`, `level`, `run_id`, `stage`, `event`. Dưới đây là các truy vấn chạy được bằng PowerShell trên máy này.

## 1. Lượt chạy gần nhất

```
Get-ChildItem logs\*.jsonl | Sort-Object LastWriteTime -Descending | Select-Object -First 1 |
  Get-Content | ConvertFrom-Json | Select-Object timestamp, level, stage, event
```

## 2. Mọi sự kiện lỗi hoặc cảnh báo

```
Get-Content logs\*.jsonl | ConvertFrom-Json | Where-Object { $_.level -in 'warning','error' } |
  Select-Object timestamp, stage, event
```

## 3. Sự kiện của khối Dự đoán (do U3 thêm)

```
Get-Content logs\*.jsonl | ConvertFrom-Json |
  Where-Object { $_.event -like 'prediction.*' } |
  Select-Object timestamp, event, verdict, threshold
```

Ba sự kiện: `prediction.model_unavailable` (warning, kèm thông điệp thô của `ModelError`), `prediction.scored` (info, chỉ `verdict` + `threshold`), `prediction.input_rejected` (info, chỉ danh sách id ô sai — **không** có giá trị người dùng nhập).

## 4. Thời gian từng tầng trong một lượt chạy

```
$run = (Get-Content logs\*.jsonl | ConvertFrom-Json | Sort-Object timestamp -Descending |
        Select-Object -First 1).run_id
Get-Content logs\*.jsonl | ConvertFrom-Json | Where-Object { $_.run_id -eq $run } |
  Select-Object timestamp, stage, event
```

## 5. Kiểm nhanh "báo cáo có mới hơn mã không"

```
(Get-Item data\reports\analysis.json).LastWriteTime
(Get-Item src\dashboard\prediction_section.py).LastWriteTime
```

Nếu mã mới hơn báo cáo, chạy lại `--stage stats` trước khi tin vào màn hình.

## 6. Giới hạn đã biết

- `prune_logs` giữ **10 tệp** `*.jsonl` gần nhất; log cũ hơn bị xoá.
- Tệp nhật ký của dashboard (`integration-<run_id>.jsonl`) do `_integration_logger` tạo khi `logs/` rỗng; `run_id` của nó dùng 6 chữ số microsecond, khác 8 hex của pipeline.
- Không có tập trung log, không có truy vấn từ xa.
