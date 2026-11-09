# Code Summary — u3-query-rewriter

## Gia cố hợp đồng C3 (2026-11-09)

`_checked_selection` trước đây chỉ kiểm `query_id` rồi trả tên nguồn — C3 bị tiêu thụ hình thức. Nay nó kiểm thêm: nếu nguồn thắng **có khai** `tables` thì tập bảng đó phải chứa mọi bảng mà mẫu truy vấn đọc; thiếu thì `SchemaError` nêu tên bảng thiếu. Kết quả chọn nguồn không khai bảng nào (bộ dựng thử trong test) được bỏ qua phép kiểm để không báo lỗi sai.

Test khoá: `test_a_selected_source_must_declare_every_table_the_template_reads` và `test_a_selected_source_that_declares_no_tables_is_not_checked` trong `tests/unit/test_integration_rewrite.py`. Chuỗi xác nhận sau thay đổi: 375 test nhanh + 9 `slow` xanh, `pipeline run --stage all` xanh 6/6 tầng.


Nguồn: kế hoạch đã duyệt, hướng dẫn test, và các lần chạy ghi trong tài liệu này.

## 1. Đã dựng gì

| Lớp | Tệp | Nội dung |
|---|---|---|
| Sổ KPI | `src/common/kpis.py` (mới) | Ba KPI + `so_dong`, định nghĩa doanh thu `price + freight_value` của đơn `delivered`; không import analytics/integration |
| Mô hình | `src/integration/models.py` | `QueryTemplate`; `KpiComparison` thêm `group_key`, `delta`; `QueryRunResult` thêm `total_orders`/`months`/`partial` |
| Viết lại + chạy | `src/integration/rewrite.py` (mới) | Ba mẫu SQL hằng có `?`; kế hoạch 3/2/2 bước; nạp CSV vào DuckDB trong bộ nhớ; `elapsed_ms`/`load_ms`; bốn sự kiện log; đối chiếu từng nhóm + `__all__`; `KpiMismatchError`; `partial`; `run_template`, `latest_sql` |
| Lỗi | `src/common/exceptions.py` | `KpiMismatchError` mang `groups = ((kpi_id, group_key, delta), …)` |
| Lược đồ | `config/mediated-schema.yaml` | Thêm `mat_hang.gia_van_chuyen`, `don_hang.ngay_giao_thuc_te`, `don_hang.ngay_giao_du_kien`; xác nhận `bang_giao`, `ten_danh_muc` đã `loaded: true` |
| Cấu hình | `config/integration-sources.yaml`, `config/integration-tab.yaml` | Ba truy vấn dùng thêm ba trường mới; tab giữ `don-theo-thang` + thêm ba vùng |
| Tab | `src/integration/card.py`, `src/dashboard/app.py` | Ba khối kết quả theo ba mẫu, song song vùng `don-theo-thang`; gỡ callback một-khối (dữ liệu mẫu mới cần C3, thuộc U6) |
| Load | `src/integration/load.py` | Guard "một bảng nguồn" nới thành "đọc bảng khoá + ghi `integration.load.skipped`", hành vi `DonHang` không đổi |
| Test | `tests/unit/test_integration_rewrite.py` (41 hàm), `test_common_kpis.py` (10 hàm) | Phủ ba mẫu, định danh, tham số, đối chiếu, `partial`, lỗi |

## 2. Kết quả kiểm chứng

| Cổng | Lệnh | Kết quả |
|---|---|---|
| Test của đơn vị | `pytest tests/unit/test_integration_rewrite.py tests/unit/test_common_kpis.py` | **51 passed** |
| Bộ nhanh toàn repo | `pytest -m "not slow"` | **323 passed, 7 deselected** |
| Lint/định dạng | `ruff check` + `ruff format --check` trên bảy tệp | sạch |
| Chạy thật ba mẫu | so với `src/analytics` | ba mẫu khớp tuyệt đối; `elapsed_ms` 59–122 ms (ngưỡng 2000) |

## 3. Điểm lệch kế hoạch (đã ghi trong kế hoạch hoặc do phát sinh)

1. `test_integration_query.py` không phải sửa — không khẳng định nào ghim sự thật đã đổi.
2. Sửa thêm `test_integration_model.py`, `test_integration_selector.py`, `test_integration_load.py` vì cùng một sự thật dữ liệu được khai ở nhiều nơi.
3. `load.py` nới guard một-bảng-nguồn (hành vi `DonHang` không đổi).
4. `app.py` gỡ callback của tab thay vì trỏ vào `result_block_ids[0]`; callback của tab là **6**, tổng dashboard **8**.
5. `run_template` có thêm `reference=` và `csv_dir=` (keyword-only) để tiêm hàm tham chiếu và thư mục CSV trong test.
6. `total_orders` cần một lời gọi SQL thứ hai (`COUNT(DISTINCT)` không dùng được với `GROUP BY`).
7. Nhóm thiếu danh mục dùng nhãn `unknown`, khớp `src/clean/products.py`.
8. `kpi_definitions` mang hai dòng (KPI + `so_dong`) — cộng thêm theo C4.

## 4. Việc chưa làm

- **`src/integration/selector.py` (U5) đã được format lại** trong đơn vị này (thay đổi có chủ đích) để CI bước `ruff format --check src/integration` xanh; `ruff format --check src/integration` nay sạch (8 tệp).
- **Phép so với `src/analytics` thật chỉ mới chạy tay**, chưa thành test tự động: 51 unit test đều tiêm hàm tham chiếu giả. Phép so thật thuộc Build and Test (bộ `slow` + `--stage all`), nơi `warehouse/olist.duckdb` tồn tại.
- **Mép ngày của `DATE_PREDICATE` chưa có test ghim** (cận trên dùng `< ngày_đến + 1 ngày`).
- NFR1.1, NFR2.1, NFR5.1, NFR5.2 đo đầy đủ ở Build and Test (bộ `slow`, `--stage all`).
