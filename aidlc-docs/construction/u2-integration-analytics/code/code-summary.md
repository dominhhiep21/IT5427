# Code Summary — U2 Integration & Analytics

**Ngày hoàn tất**: 2026-10-23
**Trạng thái**: Code + test hoàn tất; chờ phê duyệt

## 1. Tệp đã tạo

### `src/external/`
- `ibge.py` — `IbgeClient`: cache, API, retry 2 lần, timeout 10s, metadata SHA-256.
- `region.py` — `RegionMapper`: validate 27 state/5 region, gắn region.

### `src/integrate/`
- `dimensions.py` — `DimensionBuilder` cho 5 dimension.
- `facts.py` — `FactBuilder` cho 4 fact; `item_total`, `delivery_days`, `is_late`, `has_*`.
- `aggregates.py` — `agg_sales_daily`, `agg_delivery_daily`.
- `connections.py` — `ConnectionFactory` read-only/write; DuckDB memory limit.
- `catalog.py` — `DuckDbCatalog`, 11 view `v_*`.
- `validate.py` — `StarSchemaValidator` row counts, unique, fanout.
- `reconcile.py` — `KpiReconciler` baseline KPI.
- `pipeline.py` — `integrate_all`, build → validate → promote → catalog.

### `src/analytics/`
- `filters.py` — `KpiFilters`.
- `service.py` — `AnalyticsService` với 5 nhóm query.

### Cache IBGE
- `dataset/external/ibge/estados.json` — 27 bang, snapshot chính thức.
- `dataset/external/ibge/metadata.json` — nguồn, hash, thời điểm.

### Test
- `tests/unit/test_region_mapper.py`
- `tests/unit/test_dimensions.py`
- `tests/unit/test_facts.py`
- `tests/unit/test_aggregates.py`
- `tests/unit/test_ibge_client.py`
- `tests/unit/test_filters.py`
- `tests/integration/test_u2_end_to_end.py`

## 2. Cách chạy

```powershell
# Test nhanh
.\.venv\Scripts\python.exe -X utf8 -m pytest -m "not slow"

# Toàn bộ test
.\.venv\Scripts\python.exe -X utf8 -m pytest

# Coverage U2
.\.venv\Scripts\python.exe -X utf8 -m pytest --cov=src.integrate --cov=src.analytics --cov=src.external --cov-report=term
```

## 3. Kết quả xác minh

| Kiểm tra | Kết quả |
|---|---|
| Test suite | **31 passed** |
| Coverage U2 | **89%** (analytics 91%, integrate 91-100%) |
| Dimensions | 99.441 / 32.951 / 3.095 / 19.015 / 774 |
| Facts | 112.650 / 99.441 / 103.886 / 99.224 |
| DuckDB views | 11 |
| Doanh thu delivered | **15.419.773,75 BRL** |
| Số đơn delivered | **96.478** |
| AOV | **159,83 BRL** |
| Đơn giao trễ | **7.826** |
| Tỷ lệ giao trễ | **8,11%** |
| Query KPI median | 65-233 ms (mục tiêu ≤ 1s) |
| 27 bang → 5 vùng | Pass |

## 4. Quyết định triển khai đáng chú ý

- **Offline IBGE**: API IBGE không truy cập được từ máy này (timeout). Dùng cache bootstrap 27 bang tại `dataset/external/ibge/`; `IbgeClient` ưu tiên cache, chỉ gọi API khi `refresh=True`. Nếu cache thiếu + mạng lỗi → `ExternalSourceError`.
- **Dominant category**: mỗi order được gán một category đại diện (ưu tiên category đã biết, sau đó item_total lớn nhất) để `agg_delivery_daily` không nhân bản order.
- **Natural keys** cho toàn bộ dim/fact.
- **DuckDB** `memory_limit=1GB`, `threads=4`.
- **Không cache KPI**; query trực tiếp DuckDB.

## 5. Điều chỉnh so với phân tích ban đầu

- **Đơn giao trễ**: **7.826** (không phải 7.827). Một đơn `canceled` có ngày giao nhưng bị loại khỏi mẫu số delivered.
- **Đơn nhiều review**: **547 đơn** (551 dòng dư), không phải 551 đơn.
- **Thiếu bản dịch**: **13 sản phẩm** thuộc 2 danh mục.
- **Zip nhiều biến thể city**: **8.555** sau chuẩn hóa.

## 6. Giới hạn hiện tại

- Chưa có dashboard (U3).
- Chưa có CLI orchestration đầy đủ (U3).
- Chưa có micro-batch (U3).
- `avg_review_score` trong `kpi_summary` tính trên đơn delivered, không phải toàn bộ review.

## 7. Output

- `data/marts/*.parquet` — 5 dim + 4 fact + 2 aggregate.
- `warehouse/olist.duckdb` — 11 view.
- `data/reports/integration-report.json`
- `data/reports/kpi-reconciliation.json`
