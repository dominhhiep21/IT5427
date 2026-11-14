# Unit Test Instructions — u1-mart-and-baseline

Đơn vị: `u1-mart-and-baseline`. Chiến lược: **Standard** (5–8 test mỗi thành phần) + sàn phủ 80% của scope `feature`. Phương pháp: **TDD** (đỏ → xanh → refactor), theo `team.md` `## Testing Posture`.

## Lệnh, chính xác

Chạy trong thư mục repo, dùng `.venv`:

```
python -X utf8 -m pytest tests/unit/test_integrate_facts_columns.py tests/unit/test_integrate_seller_state.py tests/unit/test_analytics_baseline.py -q
```

Bộ nhanh (không chạm đĩa thật):

```
python -X utf8 -m pytest -m "not slow" -q
```

Test `slow` của đơn vị (chạy `dataset/` thật, chậm):

```
python -X utf8 -m pytest -m slow tests/integration/test_u1_mart_columns_end_to_end.py -q
```

Cổng phủ của repo (không hạ ngưỡng):

```
python -X utf8 -m pytest --cov=src --cov-fail-under=80
```

## Tệp test phải có

| Tệp | Lớp | Số test | Khẳng định gì |
|---|---|---|---|
| `tests/unit/test_integrate_facts_columns.py` | dữ liệu/mart | 7 | ba cột có mặt; `seller_state` **không** tên `state`; số dòng không đổi; hai cột mốc là datetime **và giữ được null**; cột cũ giữ nguyên |
| `tests/unit/test_integrate_seller_state.py` | truy cập dữ liệu | 5 | đến từ `dim_seller.state` (bang khách là `RJ`, bang người bán là `SP` nên không thể nhầm nguồn); `seller_id` lạ ⇒ null không ném; không mất dòng; phép nối không nhân dòng; giá trị hai chữ hoa |
| `tests/unit/test_analytics_baseline.py` | logic nghiệp vụ | 8 | AUC trong (0,1); tất định qua hai lần gọi; sai `cut_date` ⇒ `ModelError`; tập kiểm tra rỗng ⇒ `ModelError`; một lớp nhãn ⇒ `ModelError`; thiếu cột ⇒ `ModelError`; giá trị lạ không thêm cột; **một cột số khác bị bỏ qua hoàn toàn** (chứng minh baseline chỉ dùng một đặc trưng) |
| `tests/integration/test_u1_mart_columns_end_to_end.py` | end-to-end (`slow`) | 2 | `run --stage all` xanh, 9 bảng + 11 view + 5 KPI khớp; ba cột đọc được từ Parquet thật, không có cột `state` |

Tổng: **20 test đơn vị** + **2 test `slow`**.

## Ràng buộc khi viết test

- **TDD thật:** mỗi bước Red phải chạy và **thấy đỏ** trước khi viết mã; ghi lại lệnh và kết quả đỏ trong `code-summary.md`.
- **Không dựa vào `warehouse/` hay `data/marts/`** trong bộ nhanh (`TD-09`). Khung dữ liệu nhỏ dựng bằng `pandas` ngay trong test.
- **Không import `numpy`** — chỉ dùng `pandas` và `random` của thư viện chuẩn (`project.md` cấm thư viện chưa ghim; `numpy` chỉ có mặt gián tiếp qua `pandas`).
- **Không khẳng định một giá trị AUC cụ thể** — chỉ khẳng định hành vi (miền giá trị, tính tất định, các nhánh lỗi). Đây là luật của `project.md`.
- **Không** hạ `--cov-fail-under`, không đặt cờ riêng cho bộ nhanh, không thêm `per-file-ignores`.
- Test `slow` là **cổng hồi quy dữ liệu**: nó phải đỏ nếu một dòng mart đổi, và đỏ nếu một KPI lệch.
- Mọi lệnh chạy `python -X utf8`.

## Điều kiện coi là xong

1. Ba tệp test đơn vị tồn tại, xanh, phủ đủ các nhánh lỗi ở bảng trên.
2. Test `slow` xanh trên `dataset/` thật.
3. `python -X utf8 -m pytest -m "not slow" -q` xanh (không hồi quy bộ cũ).
4. `ruff check .` và `ruff format --check` sạch, tệp mới đã vào danh sách khai tay của `ci.yml`.
5. Cổng phủ 80% vẫn xanh trên toàn bộ bộ test.
