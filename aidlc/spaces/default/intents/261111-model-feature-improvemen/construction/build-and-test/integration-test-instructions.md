# Integration Test Instructions

## 1. Bộ `slow` gồm những gì

Mười lăm test, tất cả chạm dữ liệu thật hoặc sinh artefact:

| Tệp | Đơn vị | Điều nó khẳng định |
|---|---|---|
| `tests/data_quality/test_real_dataset.py` | nền | dị thường đã biết trên 9 CSV gốc |
| `tests/integration/test_u1_end_to_end.py` | U1 (đợt trước) | pipeline U1 đầu-cuối |
| `tests/integration/test_u2_end_to_end.py` | U1 | pipeline U2 đầu-cuối |
| `tests/integration/test_u3_end_to_end.py` | U1 | CLI, replay, dashboard |
| `tests/integration/test_u1_stats_end_to_end.py` | U2 | tầng `stats` viết báo cáo |
| `tests/integration/test_u1_mart_columns_end_to_end.py` | U2 | ba cột mart + bất biến số dòng |
| `tests/integration/test_u2_model_end_to_end.py` | U2 | 110.195/96.476/8.713/2, báo cáo v3, tệp mô hình |
| `tests/integration/test_u3_floor_end_to_end.py` | **U3** | cổng mốc sàn trên báo cáo thật |

## 2. Lệnh

Một tệp:

```
python -X utf8 -m pytest -m slow tests/integration/test_u3_floor_end_to_end.py -q
```

Toàn bộ bộ `slow` (nên chạy qua chuỗi xác nhận để có cả `--stage all` và `--stage stats` trước):

```
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify_intent.ps1
```

## 3. Điều phải biết trước khi chạy

- Bộ `slow` **ghi lại** `data/`, `warehouse/`, `logs/`, `data/models/`. Đó là artefact sinh ra, đã bị `.gitignore`; không phải mất dữ liệu người dùng.
- Đóng dashboard trước khi chạy `integrate` (khoá `warehouse/olist.duckdb`).
- View DuckDB chứa đường dẫn **tuyệt đối** vào Parquet, nên chuyển thư mục repo thì phải chạy lại `integrate`.
- Một ca nhạy tải: `tests/unit/test_linkage_score.py::test_scoring_two_hundred_thousand_pairs_stays_under_sixty_seconds` có thể đỏ khi máy bận (đo được 69,6 s khi tải 59%, 11 s khi chạy riêng). Không nới ngưỡng; chạy lại khi máy rảnh.

## 4. Kỳ vọng

| Lượt | Kết quả |
|---|---|
| `test_u3_floor_end_to_end.py` | 1 passed, ~25 s; `beats_floor(0,6482; 0,5297)` → True |
| Cả bộ `slow` trong chuỗi xác nhận | 723 passed tổng, phủ 92,71% |
