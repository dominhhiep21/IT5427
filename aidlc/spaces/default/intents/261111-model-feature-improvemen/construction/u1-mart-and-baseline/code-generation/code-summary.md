# Code Summary — u1-mart-and-baseline

## Đã làm gì

Ba cột mới vào mart và một hàm đo baseline. Không đổi grain, không đổi lọc, không đổi câu SQL view.

| Tệp | Thay đổi |
|---|---|
| `src/integrate/facts.py` | `build_order_items`: nối `dim_seller[["seller_id","state"]]` rồi **đổi tên `state` → `seller_state`** ngay tại chỗ nối; thêm cột vào danh sách trả về. `build_orders`: thêm `order_approved_at` và `order_delivered_carrier_date` vào danh sách trả về. |
| `src/analytics/model.py` | Thêm `measure_state_baseline` — hàm thuần, `-> float` theo hợp đồng C1, kiểm `cut_date == SPLIT_DATE`, ném `ModelError` cho ba nhánh lỗi. |
| `tests/unit/test_integrate_facts_columns.py` | 7 test: ba cột có mặt, không có cột `state`, số dòng không đổi, hai cột mốc là datetime **và giữ được null**, cột cũ giữ nguyên. |
| `tests/unit/test_integrate_seller_state.py` | 5 test: nguồn từ `dim_seller` (bang khách `RJ` ≠ bang người bán `SP`), `seller_id` lạ ⇒ null, không mất dòng, nối không nhân dòng, giá trị hai chữ hoa. |
| `tests/unit/test_analytics_baseline.py` | 8 test: AUC trong (0,1), tất định, ba nhánh `ModelError`, giá trị lạ không thêm cột, **một cột số khác bị bỏ qua hoàn toàn**. |
| `tests/integration/test_u1_mart_columns_end_to_end.py` | 2 test `slow`: số dòng + 5 KPI + 11 view; ba cột đọc được từ Parquet thật. |
| `.github/workflows/ci.yml` | Thêm **bốn** tệp test mới vào danh sách khai tay của `ruff format --check`. Không đổi ngưỡng phủ. |

## TDD — bằng chứng đỏ trước xanh

| Lớp | Lệnh đỏ đầu tiên | Kết quả |
|---|---|---|
| Mart | `pytest tests/unit/test_integrate_facts_columns.py` | 6 failed (`KeyError: 'seller_state'`, thiếu hai cột mốc) |
| Truy cập dữ liệu | `pytest tests/unit/test_integrate_seller_state.py` | 5 failed (không có cột `seller_state`) |
| Logic nghiệp vụ | `pytest tests/unit/test_analytics_baseline.py` | 7 failed (`AttributeError: measure_state_baseline`) |

Sau khi viết mã: **20 passed**. Bộ nhanh: **543 passed, 14 deselected** — không hồi quy. Test `slow` của đơn vị: **2 passed** trên `dataset/` thật.

## Kiểm tra đã chạy

```
python -X utf8 -m pytest tests/unit/test_integrate_facts_columns.py tests/unit/test_integrate_seller_state.py tests/unit/test_analytics_baseline.py -q   → 20 passed
python -X utf8 -m pytest -m "not slow" -q                                                                                                              → 545 passed, 14 deselected
python -X utf8 -m pytest -m slow tests/integration/test_u1_mart_columns_end_to_end.py -q                                                                → 2 passed
python -X utf8 -m ruff check .                                                                                                                          → All checks passed
python -X utf8 -m ruff format --check <danh sách ci.yml:35>                                                                                             → 50 files already formatted
```

## Quyết định trong lúc thi công

1. **Đổi tên tại chỗ nối, không ở cuối.** `dim_customer` có cột `state`; `agg_sales_daily` nối hai bảng, nên một cột `state` ở bảng fact sẽ sinh `state_x`/`state_y`. Đổi tên ngay sau `merge` là chỗ duy nhất không thể quên.
2. **Nối `left`, không `inner`.** `inner` sẽ làm mất dòng khi `seller_id` không có trong `dim_seller` — đúng thứ `BR1.1` cấm.
3. **`pd.get_dummies` thay vì `OneHotEncoder`.** Cần `reindex(columns=...)` để giá trị lạ ở tập kiểm tra không sinh cột mới; `get_dummies` cho việc đó gọn hơn và không thêm phụ thuộc.
4. **`measure_state_baseline` trả `float`, không trả cấu trúc.** Hợp đồng C1 đã chốt `-> float`; `cohort_rows`/`same_split_as_model` thuộc U2.
5. **`ruff format` trên `facts.py` chạm cả dòng cũ.** Tệp này **không** nằm trong danh sách format của `ci.yml`, nhưng `team.md` cho phép dọn một tệp khi có người sửa tới. Diff vì thế rộng hơn ba cột — đây là hệ quả có chủ đích, không phải dọn toàn repo.

## Điều chưa làm, và vì sao

- **`FORBIDDEN_COLUMNS` chưa thêm hai cột mốc** — thuộc U2 (`BR1.3` ghi `enforced_by: u2-features-and-models`).
- **`CohortCounts` chưa có** — thuộc U2.
- **Chưa commit** — quyết định của người làm.
