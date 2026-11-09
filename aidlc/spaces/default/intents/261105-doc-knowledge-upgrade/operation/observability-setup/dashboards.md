# Dashboards

## 1. Không dựng dashboard giám sát riêng

Hệ chạy một tiến trình local, một người dùng. Không có CloudWatch, không có Prometheus, không có dịch vụ nền nào để vẽ biểu đồ theo thời gian. Dựng một dashboard giám sát nữa sẽ là tầng thứ hai phải bảo trì mà không ai xem.

## 2. Thứ đóng vai "dashboard"

| Thứ | Cho biết gì | Lấy ở đâu |
|---|---|---|
| Tab "Tích hợp" của chính sản phẩm | Số liệu thật, trạng thái từng vùng, thời gian chạy | mở `python -X utf8 -m src.dashboard` |
| `QualityGate` chế độ `full` | 21 check cấu trúc + 9 check số dòng + 10 dị thường allowlist | `data/reports/quality.json` sau mỗi lần chạy pipeline |
| `KpiReconciler` | 5 KPI so với baseline, dung sai riêng | `data/reports/` cùng lần chạy |
| Nhật ký JSONL | Mọi sự kiện theo `run_id`, tầng, mức | `logs/<run_id>.jsonl` |

## 3. Cách đọc sức khoẻ trong 30 giây

```powershell
# Lần chạy gần nhất thành công hay không
Get-Content (Get-ChildItem logs\*.jsonl | Sort-Object LastWriteTime -Descending | Select-Object -First 1) |
  Select-String '"event":"pipeline.completed"'

# Có lỗi nào không
Get-Content logs\*.jsonl | Select-String '"level":"ERROR"' | Select-Object -Last 20
```

Nếu hai lệnh trên cho "completed success=True" và không có ERROR, hệ đang khoẻ. Không cần biểu đồ để biết điều đó.

## 4. Khi nào mới đáng dựng dashboard

Khi có người thứ hai dùng, hoặc khi pipeline chạy tự động theo lịch. Lúc đó mới cần biểu đồ theo thời gian; trước đó nó chỉ là hình thức.
