# Kế hoạch Code Generation — U2 Integration & Analytics

**Unit**: U2 — Integration & Analytics
**Story**: US-08 → US-14, US-19
**Giai đoạn**: CONSTRUCTION - Code Generation (Part 1: Planning)
**Vị trí code**: workspace root

## 1. Bối cảnh

U2 nhận cleaned Parquet từ U1, tạo IBGE reference, star schema, DuckDB catalog và analytics API.

**Phụ thuộc**: U1 cleaned Parquet + `quality-report.json`.
**Đầu ra cho U3**: `data/marts/*.parquet`, `warehouse/olist.duckdb`, `AnalyticsService`.

## 2. Cấu trúc sẽ tạo

```
src/
  external/
    __init__.py
    ibge.py
    region.py
  integrate/
    __init__.py
    dimensions.py
    facts.py
    aggregates.py
    connections.py
    catalog.py
    validate.py
    reconcile.py
    pipeline.py
  analytics/
    __init__.py
    filters.py
    service.py
tests/
  unit/
    test_region_mapper.py
    test_dimensions.py
    test_facts.py
    test_aggregates.py
    test_analytics.py
  integration/
    test_u2_end_to_end.py
dataset/external/ibge/
  estados.json          # bootstrap cache 27 bang
  metadata.json         # nguồn, hash, thời điểm
```

## 3. Quyết định triển khai

- Natural keys, DuckDB view trên Parquet.
- `dim_customer` grain `customer_id`.
- `dim_date` 774 ngày, `is_sparse_period`.
- Pre-aggregate `agg_sales_daily`, `agg_delivery_daily`.
- DuckDB `memory_limit=1GB`, `threads=4`.
- Dashboard read-only connection; pipeline write connection.
- **Offline cache**: môi trường hiện tại không truy cập được API IBGE (timeout). Tạo cache bootstrap 27 bang từ snapshot chính thức trong `dataset/external/ibge/`; `IbgeClient` ưu tiên cache, chỉ gọi API khi `--refresh-ibge` hoặc cache thiếu. Nếu cache thiếu + mạng lỗi → `ExternalSourceError`.

## 4. Các bước thực hiện

### Step 1 — Dependency và config
- [ ] Thêm `duckdb` vào `requirements.txt`; cài trong `.venv`, pin phiên bản.
- [ ] Bổ sung `config.yaml`: `duckdb_path`, `marts_dir`, `duckdb_memory_limit`, `duckdb_threads`, `ibge_url`, `ibge_timeout`, `ibge_retries`.
- [ ] Mở rộng `AppConfig`.
- **Story**: US-08, US-19.

### Step 2 — Shared types
- [ ] `src/common/types.py`: `KpiFilters`, `IntegrationReport`, `ValidationReport`, `KpiReconciliationReport`, `IbgeMetadata`.
- **Story**: US-08, US-14.

### Step 3 — IBGE client + region mapper
- [ ] `src/external/ibge.py`: cache, API, retry, metadata, `fetch_states`, `fetch_municipalities`.
- [ ] `src/external/region.py`: `RegionMapper`, 27 state → 5 region, validate.
- [ ] Tạo cache bootstrap `estados.json` + `metadata.json`.
- **Story**: US-19.

### Step 4 — Dimensions
- [ ] `src/integrate/dimensions.py`: `DimensionBuilder` cho customer/product/seller/geography/date.
- [ ] `dim_date` 774 ngày; `is_sparse_period`.
- **Story**: US-08, US-09, US-10.

### Step 5 — Facts
- [ ] `src/integrate/facts.py`: `FactBuilder` cho order_items/orders/payments/reviews.
- [ ] `item_total`, `delivery_days`, `is_late`, `has_*`.
- **Story**: US-08, US-10, US-14.

### Step 6 — Aggregates
- [ ] `src/integrate/aggregates.py`: `agg_sales_daily`, `agg_delivery_daily`.
- [ ] Grain `(date_key, state, region, category)`.
- **Story**: US-11, US-12, US-14.

### Step 7 — DuckDB connection + catalog
- [ ] `src/integrate/connections.py`: `ConnectionFactory` read-only/write, memory limit.
- [ ] `src/integrate/catalog.py`: tạo view `v_*` trên Parquet.
- **Story**: US-08, US-11.

### Step 8 — Validator + KPI reconciler
- [ ] `src/integrate/validate.py`: row counts, unique, fanout, region.
- [ ] `src/integrate/reconcile.py`: KPI baseline, tolerance 0,01.
- **Story**: US-08, US-14.

### Step 9 — Integration pipeline
- [ ] `src/integrate/pipeline.py`: build → temp → validate → promote → catalog → report.
- [ ] Ghi `integration-report.json`, `kpi-reconciliation.json`.
- **Story**: US-08 → US-14.

### Step 10 — Analytics service
- [ ] `src/analytics/filters.py`: `KpiFilters`.
- [ ] `src/analytics/service.py`: `kpi_summary`, `revenue_by_period`, `revenue_by_dimension`, `top_entities`, `delivery_kpis`.
- [ ] Chỉ SELECT; không cache.
- **Story**: US-11 → US-14.

### Step 11 — Unit tests
- [ ] Test region mapper 27/5; state lạ.
- [ ] Test dimensions row counts/date sparse.
- [ ] Test facts grain/item_total/late.
- [ ] Test aggregates totals.
- [ ] Test analytics filters/KPI.
- **Story**: US-08 → US-14, US-19.

### Step 12 — Integration tests + docs
- [ ] `tests/integration/test_u2_end_to_end.py`: U1 cleaned → U2 → DuckDB → KPI baseline.
- [ ] `aidlc-docs/construction/u2-integration-analytics/code/code-summary.md`.
- [ ] Chạy `pytest`; coverage integrate/analytics ≥ 70%.
- **Story**: US-08 → US-14.

## 5. Truy vết story

| Story | Bước |
|---|---|
| US-08 | 1, 2, 4, 5, 7, 8, 9 |
| US-09 | 4 |
| US-10 | 4, 5 |
| US-11 | 6, 7, 10 |
| US-12 | 6, 10 |
| US-13 | 10 |
| US-14 | 5, 6, 8, 10 |
| US-19 | 3 |

## 6. Phạm vi và ước lượng

- Khoảng **20-25 tệp**, ~1.200-1.800 dòng code + test.
- 12 bước.
- Không bao gồm dashboard U3.
- Test nhanh dùng fixture nhỏ; integration dùng cleaned Parquet thật.

## 7. Điều kiện hoàn thành

- [ ] `data/marts/*.parquet` đủ 5 dim + 4 fact + 2 agg.
- [ ] DuckDB catalog mở được, view trả đúng row counts.
- [ ] KPI baseline khớp: 15.419.773,75; 96.478; 159,83; 7.826; 8,11%.
- [ ] 27 state → 5 region.
- [ ] `pytest` pass; coverage ≥ 70%.
- [ ] Không đọc CSV trong integrate/analytics.
