# Thành phần ứng dụng (Components)

## 1. Cấu trúc package

```
src/
  config.py              # AppConfig + load YAML
  common/                # logging, IO, hash, manifest, kiểu dùng chung
  ingest/                # đọc CSV, schema contract, raw Parquet
  quality/               # kiểm tra khóa, orphan, số dòng
  clean/                 # chuẩn hóa dữ liệu theo bảng
  external/              # IBGE download/cache + ánh xạ vùng
  integrate/             # fact/dimension + DuckDB catalog
  analytics/             # truy vấn KPI
  dashboard/             # Plotly Dash
  pipeline/              # CLI orchestrator + micro-batch
tests/                   # unit + data quality
```

Quyết định: **tổ chức theo tầng**, DataFrame trong bộ nhớ, Parquet tại ranh giới stage, orchestrator Python CLI, Dash truy vấn DuckDB, cấu hình `config.yaml`.

## 2. Danh sách component

### config
- **Mục đích**: Nạp cấu hình đường dẫn, cổng dashboard, ngưỡng chất lượng.
- **Trách nhiệm**: Đọc `config.yaml`, áp giá trị mặc định, kiểm tra thư mục/tệp bắt buộc, trả `AppConfig` bất biến.
- **Interface**: `load_config(path: Path | None) -> AppConfig`.
- **Phụ thuộc**: Không.

### common
- **Mục đích**: Tiện ích dùng chung cho mọi tầng.
- **Trách nhiệm**: Tạo run context/log, hash SHA-256, đọc/ghi Parquet, đọc CSV theo contract, quản lý manifest micro-batch, định dạng thời gian.
- **Interface**: `RunContext`, `sha256_file`, `read_csv`, `write_parquet`, `read_parquet`, `ManifestStore`.
- **Phụ thuộc**: `config`.

### ingest
- **Mục đích**: Đưa 9 CSV vào pipeline an toàn.
- **Trách nhiệm**: Kiểm tra sự hiện diện, encoding, thứ tự cột; ghi raw Parquet; ghi báo cáo số dòng/hash.
- **Interface**: `ingest_all`, `ingest_table`, `validate_columns`.
- **Phụ thuộc**: `config`, `common`, `ingest/schemas.py`.
- **Không làm**: Không làm sạch nghiệp vụ, không sửa CSV.

### quality
- **Mục đích**: Cổng chặn dữ liệu lỗi.
- **Trách nhiệm**: Kiểm tra unique, foreign key, row count, null bắt buộc, miền giá trị; fail-fast.
- **Interface**: `run_quality_gate`, các hàm `check_*`.
- **Phụ thuộc**: `common`.

### clean
- **Mục đích**: Chuẩn hóa từng bảng nguồn.
- **Trách nhiệm**: Parse timestamp, chuẩn hóa city, gộp geolocation, dịch danh mục, xử lý null, tạo cờ chất lượng/ngoại lai.
- **Interface**: `clean_orders`, `clean_customers`, `clean_geolocation`, `clean_products`, `clean_payments`, `clean_reviews`, `clean_items`, `clean_sellers`.
- **Phụ thuộc**: `config`, `common`.
- **Không làm**: Không join star schema, không tính KPI.

### external
- **Mục đích**: Quản lý dữ liệu tham chiếu IBGE.
- **Trách nhiệm**: Tải, cache, kiểm tra hash; ánh xạ 27 bang → 5 vùng; fail-fast khi thiếu cache và mất mạng.
- **Interface**: `fetch_ibge`, `load_region_map`, `validate_region_map`.
- **Phụ thuộc**: `config`, `common`.

### integrate
- **Mục đích**: Tạo star schema.
- **Trách nhiệm**: Xây dimension/fact, ghi mart Parquet, tạo DuckDB view/table.
- **Interface**: `build_dimensions`, `build_facts`, `write_marts`, `create_duckdb_catalog`.
- **Phụ thuộc**: `config`, `common`, `clean` (kiểu dữ liệu), `external` (vùng).

### analytics
- **Mục đích**: Cung cấp KPI đã định nghĩa.
- **Trách nhiệm**: Truy vấn DuckDB; tính doanh thu, AOV, tăng trưởng, danh mục, vùng, top seller/product, giao trễ.
- **Interface**: `revenue_by_period`, `revenue_by_dimension`, `top_entities`, `delivery_kpis`, `kpi_summary`.
- **Phụ thuộc**: `integrate` (catalog), `common`.
- **Không làm**: Không đọc CSV, không sửa mart.

### dashboard

- **Mục đích**: Giao diện Plotly Dash tiếng Việt.
- **Trách nhiệm**: Layout, bộ lọc, KPI card, biểu đồ, callback, định dạng ngày/tiền, trạng thái lỗi/rỗng.
- **Interface**: `create_app`, `register_callbacks`, `build_layout`.
- **Phụ thuộc**: `analytics`, `config`.

### pipeline
- **Mục đích**: Điều phối toàn bộ luồng.
- **Trách nhiệm**: CLI stage, thứ tự chạy, run summary, micro-batch manifest, replay.
- **Interface**: `run_stage`, `run_all`, `run_micro_batch`, `replay`.
- **Phụ thuộc**: tất cả component runtime.

### tests
- **Mục đích**: Bảo vệ logic và dữ liệu.
- **Trách nhiệm**: Unit test cleaning/KPI, test schema, test join không bùng nổ, test category fallback, test quality gate.
- **Interface**: pytest; không phải component runtime.
- **Phụ thuộc**: tất cả component cần test.

## 3. Ràng buộc component

- `dashboard` không import `ingest`, `clean`, `pipeline`.
- `analytics` chỉ đọc DuckDB/Parquet, không ghi.
- `clean` không biết `dashboard`.
- `ingest` không gọi `clean`.
- Mọi component nhận `AppConfig`/`RunContext` qua tham số, không đọc biến toàn cục.
