# Integration Test Instructions

## 1. Ba test tích hợp end-to-end hiện có

| Tệp | Phạm vi | Marker |
|---|---|---|
| `tests/integration/test_u1_end_to_end.py` | nạp → clean → quality → đối chiếu thanh toán trên `dataset/` thật | `slow` |
| `tests/integration/test_u2_end_to_end.py` | lược đồ trung gian: 3 thực thể, 11 view, số dòng mart | `slow` |
| `tests/integration/test_u3_end_to_end.py` | dựng app thật, 4 tab, **8 callback** | `slow` |

Chạy:

```powershell
.venv\Scripts\python.exe -X utf8 -m pytest -m slow -q
```

## 2. Điều kiện trước khi chạy

- Đã chạy `.venv\Scripts\python.exe -X utf8 -m src.pipeline run --stage all` ít nhất một lần, để `warehouse/olist.duckdb` và `data/marts/` tồn tại (nợ `TD-09`: bộ "nhanh" chưa hermetic).
- Dashboard **phải đóng**: cùng tệp `warehouse/olist.duckdb` bị khoá.
- `dataset/` phải nguyên trạng; test đọc trực tiếp CSV.

## 3. Kiểm chứng xuyên đơn vị cần bổ sung (chưa có)

| Kịch bản | Vì sao đáng làm | Cách làm đề xuất |
|---|---|---|
| Chạy U4 sinh `linkage-customer.json` rồi mở tab đọc tệp **thật** | Hiện tab chỉ được test bằng payload dựng tay; đứt gãy C5 thật sẽ không lộ | thêm test `slow` dựng pipeline đầy đủ rồi gọi `load_linkage_result` |
| Cấu hình tab có **hai** vùng | Cơ chế duyệt `result_region_ids` mới chỉ được test với một vùng | dựng `TabConfig` với hai id và một renderer giả, khẳng định cả hai khối được dựng |
| Chọn nguồn khác `olist_csv` rồi chạy truy vấn | C3 mới được kiểm bằng đơn vị; chưa có test tích hợp nào chứng minh chọn nguồn **đổi** SQL/bảng đọc | thêm test truyền `partner_simulated` cho mẫu doanh thu và khẳng định `SchemaError` vì thiếu bảng |

## 4. Thứ tự chạy khi nghiệm thu một thay đổi

1. `pytest -m "not slow"` — dừng ngay nếu đỏ.
2. `pytest -m slow` — cần dữ liệu thật.
3. `python -X utf8 -m src.pipeline run --stage all` — xác nhận `QualityGate` và `KpiReconciler` xanh.
4. Mở dashboard, bấm "Chạy truy vấn" ở vùng `don-theo-thang`, thấy số liệu.
