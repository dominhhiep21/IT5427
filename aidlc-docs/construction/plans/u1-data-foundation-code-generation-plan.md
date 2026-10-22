# Kế hoạch Code Generation — U1 Data Foundation

**Unit**: U1 — Data Foundation
**Story**: US-01 → US-07
**Giai đoạn**: CONSTRUCTION - Code Generation (Part 1: Planning)
**Vị trí code**: workspace root (không đặt trong `aidlc-docs/`)

## 1. Bối cảnh unit

U1 tạo nền dữ liệu sạch cho U2/U3:

- Đọc 9 CSV, kiểm tra schema, hash, ghi raw Parquet.
- Làm sạch 8 bảng + gộp geolocation.
- Quality gate full/incremental.
- Báo cáo ingest/cleaning/quality/reconciliation.

**Phụ thuộc**: không có unit trước.
**Đầu ra cho U2**: `data/cleaned/*.parquet`, `quality-report.json`, schema ổn định.

## 2. Cấu trúc sẽ tạo

```
requirements.txt
pytest.ini
config.yaml
.gitignore
src/
  __init__.py
  config.py
  common/
    __init__.py
    types.py
    exceptions.py
    logging.py
    io.py
    memory.py
  ingest/
    __init__.py
    schemas.py
    reader.py
    reports.py
  clean/
    __init__.py
    customers.py
    sellers.py
    products.py
    orders.py
    items.py
    payments.py
    reviews.py
    geolocation.py
    pipeline.py
  quality/
    __init__.py
    checks.py
    gate.py
    allowlist.py
tests/
  conftest.py
  unit/
    test_config.py
    test_schema.py
    test_clean_orders.py
    test_clean_products.py
    test_clean_items.py
    test_clean_reviews.py
    test_geolocation.py
    test_quality_gate.py
  data_quality/
    test_real_dataset.py
  integration/
    test_u1_end_to_end.py
```

## 3. Quyết định triển khai

- Python package `src/`, import tuyệt đối.
- pandas + PyArrow; Parquet Snappy.
- Config `config.yaml` + dataclass `AppConfig`.
- Log JSON lines + console summary.
- AtomicWriter từng tệp.
- Không thêm CLI ở U1; U3 sẽ thêm `src/pipeline`. U1 chạy qua hàm/test.
- Không đọc/ghi ngoài workspace.
- Không sửa `dataset/`.

## 4. Các bước thực hiện

### Step 1 — Project scaffolding
- [x] Tạo `requirements.txt` (pandas, pyarrow, PyYAML, pytest, pytest-cov; pin sau khi cài).
- [x] Tạo `pytest.ini` với marker `slow`.
- [x] Tạo `config.yaml` (đường dẫn, bbox, IQR, memory thresholds, compression).
- [x] Tạo `.gitignore` (`.venv/`, `data/`, `warehouse/`, `logs/`, `__pycache__/`).
- [x] Tạo các `__init__.py`.
- **Story**: US-01.

### Step 2 — Config và kiểu dùng chung
- [x] `src/config.py`: `AppConfig`, `load_config`.
- [x] `src/common/types.py`: `TableSpec`, `IngestReport`, `CleaningReport`, `QualityReport`, `CheckResult`, `RunContext`.
- [x] `src/common/exceptions.py`: `PipelineError`, `SchemaError`, `QualityGateError`, `ConfigurationError`.
- **Story**: US-01, US-02.

### Step 3 — Logging, IO, memory
- [x] `src/common/logging.py`: `new_run_context`, `JsonLogger`.
- [x] `src/common/io.py`: `AtomicWriter`, `sha256_file`, `read_csv`, `read_parquet`.
- [x] `src/common/memory.py`: `MemoryProbe` (tracemalloc).
- **Story**: US-02.

### Step 4 — Schema contract
- [x] `src/ingest/schemas.py`: 9 `TableSpec` với cột, khóa, expected rows.
- [x] Hàm `validate_columns`.
- **Story**: US-01.

### Step 5 — Ingest
- [x] `src/ingest/reader.py`: `ingest_table`, `ingest_all`, `write_raw`.
- [x] Ghi hash, số dòng, thời điểm vào report.
- [x] Fail-fast khi thiếu cột/encoding.
- **Story**: US-01, US-02.

### Step 6 — Cleaning: customers, sellers, orders
- [x] `src/clean/customers.py`: chuẩn hóa city/state.
- [x] `src/clean/sellers.py`: chuẩn hóa city/state.
- [x] `src/clean/orders.py`: parse timestamp, `is_delivered`, `has_invalid_timestamp`.
- **Story**: US-04.

### Step 7 — Cleaning: products
- [x] `src/clean/products.py`: category fallback, translation, flags.
- **Story**: US-06.

### Step 8 — Cleaning: items, payments, reviews
- [x] `src/clean/items.py`: parse `shipping_limit_date`, IQR `price_outlier`.
- [x] `src/clean/payments.py`: giữ grain, kiểu số.
- [x] `src/clean/reviews.py`: parse ngày, `multiple_reviews_per_order`.
- **Story**: US-04, US-07.

### Step 9 — Cleaning: geolocation
- [x] `src/clean/geolocation.py`: dedupe, bbox, median, mode, bảo toàn 19.015 zip.
- **Story**: US-05.

### Step 10 — Cleaning pipeline
- [x] `src/clean/pipeline.py`: `clean_all`, thứ tự bảng, ghi cleaned Parquet, cleaning report.
- **Story**: US-04 → US-07.

### Step 11 — Quality gate
- [x] `src/quality/checks.py`: unique, FK, row count, domain.
- [x] `src/quality/allowlist.py`: baseline Q-01 → Q-10.
- [x] `src/quality/gate.py`: full/incremental, report, fail-fast.
- **Story**: US-03.

### Step 12 — Reports
- [x] `src/ingest/reports.py`: ingest/cleaning/quality/reconciliation JSON.
- [x] `reconciliation.json`: 378 đơn lệch, warning.
- **Story**: US-02, US-03.

### Step 13 — Unit tests
- [x] `tests/conftest.py`: fixture nhỏ tổng hợp.
- [x] Test config, schema, orders, products, items, reviews, geolocation, quality gate.
- [x] Không đọc `dataset/` trong unit test.
- **Story**: US-01 → US-07.

### Step 14 — Data quality + integration tests
- [x] `tests/data_quality/test_real_dataset.py` (marker `slow`): số dòng, join 99.441, 610 category, 8.427 outlier, 19.015 zip.
- [x] `tests/integration/test_u1_end_to_end.py`: chạy ingest → clean → quality trên CSV thật.
- **Story**: US-03, US-05.

### Step 15 — Documentation và xác minh
- [x] `aidlc-docs/construction/u1-data-foundation/code/code-summary.md`: file, interface, cách chạy test.
- [x] Cài dependency trong `.venv`, freeze phiên bản.
- [x] Chạy `pytest -m "not slow"` và `pytest` (slow).
- [x] Xác minh số liệu baseline; ghi kết quả.
- **Story**: US-01 → US-07.

## 5. Truy vết story

| Story | Bước |
|---|---|
| US-01 | 1, 2, 4, 5 |
| US-02 | 2, 3, 5, 12 |
| US-03 | 11, 12, 14 |
| US-04 | 6, 8, 10 |
| US-05 | 9, 14 |
| US-06 | 7 |
| US-07 | 8, 10 |

## 6. Phạm vi và ước lượng

- Khoảng **25-30 tệp**, ~1.500-2.000 dòng code + test.
- 15 bước tuần tự.
- Không bao gồm CLI U3, dashboard, star schema U2.
- Test nhanh (`-m "not slow"`) mục tiêu < 30 giây; test đầy đủ có thể 1-3 phút.

## 7. Điều kiện hoàn thành

- [x] Tất cả bước [x].
- [x] 9/9 CSV ingest; số dòng raw khớp.
- [x] 8 bảng cleaned giữ số dòng; geolocation 19.015 zip.
- [x] Quality gate pass full batch.
- [x] `pytest` pass; coverage cleaning/quality ≥ 70%.
- [x] Không có file nào trong `dataset/` bị thay đổi.
