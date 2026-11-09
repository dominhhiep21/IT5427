# Rollback Runbook

## 1. Khi nào quay lui

| Dấu hiệu | Hành động |
|---|---|
| Bộ test nhanh hoặc chậm đỏ sau khi cập nhật | quay lui ngay, không sửa nóng |
| `pipeline run --stage all` trả `success=False` | quay lui; đọc `logs/*.jsonl` để biết tầng hỏng |
| `KpiReconciler` báo lệch KPI | quay lui; đây là cổng dữ liệu, không phải lỗi giao diện |
| Dashboard mở nhưng vùng `don-theo-thang` báo lỗi | kiểm bước 4 trước; nếu vẫn lỗi thì quay lui |
| Số liệu trên vùng khác phép tính độc lập | **dừng, không quay lui mù**: ghi lại rồi điều tra vì đây là lỗi đúng đắn dữ liệu |

## 2. Các bước quay lui

```powershell
# 1. Dừng dashboard (Ctrl+C) — bắt buộc trước khi xoá warehouse/
# 2. Về mã cũ
git checkout <commit trước>
# 3. Xoá sản phẩm sinh ra (KHÔNG đụng dataset/)
Remove-Item -Recurse -Force data, warehouse, logs, inbox
# 4. Dựng lại
.venv\Scripts\python.exe -X utf8 -m src.pipeline run --stage all
# 5. Chạy lại
.venv\Scripts\python.exe -X utf8 -m src.dashboard
```

Không có migration cơ sở dữ liệu nào phải đảo: mọi thứ trong `warehouse/` đều dẫn xuất từ `dataset/`.

## 3. Điều tuyệt đối không làm

- **Không** `git checkout` đè lên `dataset/` — dữ liệu gốc bất biến.
- **Không** sửa tay CSV trung gian trong `data/` để "cho khớp"; mọi tầng phải tái lập từ CSV gốc.
- **Không** hạ ngưỡng phủ hay bỏ cổng để lấy xanh.
- **Không** quay lui khi lỗi là "số liệu sai nhưng test xanh" — đó là tín hiệu cổng thiếu, cần điều tra trước.

## 4. Sau khi quay lui

Ghi lại: commit bị bỏ, triệu chứng, tầng hỏng, log `run_id` liên quan. Nếu lỗi thuộc loại "test xanh mà số sai", thêm một test vào `tests/unit/test_integration_correctness.py` trước khi sửa lại mã.

## 5. Thời gian

Toàn bộ quay lui mất khoảng 30 giây dựng lại dữ liệu (đo thật: pipeline 6 tầng ~18 giây cộng thời gian khởi động). Không có cửa sổ downtime cần thông báo vì chỉ một người dùng local.
