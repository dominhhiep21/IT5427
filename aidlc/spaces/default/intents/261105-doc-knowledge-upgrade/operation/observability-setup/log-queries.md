# Log Queries

Nhật ký là JSONL, mỗi dòng một sự kiện, mọi dòng có `timestamp`, `level`, `run_id`, `stage`, `event`. Dưới đây là các truy vấn dùng thật, chạy bằng PowerShell (`Select-String`) hoặc `jq` nếu có.

## 1. Lần chạy gần nhất có thành công không

```powershell
Get-Content (Get-ChildItem logs\*.jsonl | Sort-Object LastWriteTime -Descending | Select-Object -First 1) |
  Select-String '"event":"pipeline.completed"'
```

## 2. Mọi lỗi của lần chạy hiện tại

```powershell
Get-Content (Get-ChildItem logs\*.jsonl | Sort-Object LastWriteTime -Descending | Select-Object -First 1) |
  Select-String '"level":"ERROR"'
```

## 3. Thời gian từng tầng

```powershell
Select-String -Path logs\*.jsonl -Pattern '"event":"stage.completed"' | Select-Object -Last 10
```

## 4. Truy vấn chậm

```powershell
Select-String -Path logs\*.jsonl -Pattern '"event":"integration.query.slow"'
```

## 5. Lần nạp có phải thử lại không

```powershell
Select-String -Path logs\*.jsonl -Pattern '"event":"integration.load.retried"'
```

Lặp lại thường xuyên là dấu hiệu khoá tệp hoặc đĩa có vấn đề.

## 6. Đối chiếu ghép bản ghi

```powershell
Select-String -Path logs\*.jsonl -Pattern '"event":"integration.linkage.(completed|failed)"'
```

## 7. Mã lỗi đóng

Mọi `error_code` phải thuộc `ERROR_CODES` trong `src/common/logging.py`; giá trị lạ bị chuẩn hoá thành `unknown`. Truy vấn để tìm giá trị lạ:

```powershell
Select-String -Path logs\*.jsonl -Pattern '"error_code":"unknown"' | Select-Object -Last 20
```

## 8. Điều cần nhớ

- Mỗi lần chạy một tệp, khoá bằng `run_id`; pipeline dọn còn 10 tệp gần nhất.
- Nhật ký **không** chứa giá trị ô dữ liệu, trừ `message` của `integration.linkage.failed` (có thể nhúng mã bản ghi — đã ghi ở `security-requirements.md` của U4).
- Không có log tập trung, không có dịch vụ ngoài: đọc trực tiếp trên máy.
