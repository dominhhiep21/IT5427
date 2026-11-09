# Danh mục thành phần — Olist E-commerce Data Pipeline

> Đơn vị thành phần là **gói Python** trong `src/` cộng ba khu vực hỗ trợ (`tests/`, `docs/`, `assets/`).
> Tên heading dưới đây là định danh thành phần được dùng lại trong `reverse-engineering-timestamp.md`
> (khối Scope of Analysis) — không đổi tên khi cập nhật.
> Danh mục tệp chi tiết theo từng tệp nằm ở `code-structure.md`; chữ ký hàm ở `api-documentation.md`.

## Tổng hợp

| Thành phần | Loại | Tệp | Dòng | Vai trò một câu |
|---|---|---:|---:|---|
| `src.config` | Hạ tầng | 1 | 143 | Nạp `config.yaml` thành `AppConfig` bất biến và tạo thư mục đầu ra |
| `src.common` | Thư viện dùng chung | 6 | 346 | IO nguyên tử, log JSONL, dataclass, ngoại lệ, đo bộ nhớ |
| `src.ingest` | Tầng ETL | 4 | 284 | Hợp đồng lược đồ 9 bảng, đọc CSV, ghi raw Parquet, báo cáo ingest |
| `src.clean` | Tầng ETL | 11 | 436 | Chuẩn hóa kiểu/chuỗi và gắn cờ chất lượng cho 9 bảng |
| `src.quality` | Cổng kiểm soát | 4 | 439 | 21 check cấu trúc + 9 check số dòng + 10 dị thường allowlist |
| `src.external` | Tích hợp nguồn ngoài | 3 | 176 | Lấy/đệm 27 bang IBGE và ánh xạ bang → 5 vùng |
| `src.integrate` | Tầng mô hình hóa | 9 | 792 | Star schema, kiểm grain/khóa, đối chiếu KPI, catalog DuckDB |
| `src.analytics` | Tầng truy vấn | 3 | 288 | 5 truy vấn chỉ đọc trên view DuckDB |
| `src.dashboard` | Tầng trình bày | 5 | 652 | Layout 3 tab, 2 callback, figure Plotly, định dạng Brazil |
| `src.pipeline` | Điều phối | 8 | 629 | CLI, chạy tầng, micro-batch, manifest, upsert, replay |
| `tests` | Kiểm thử | 26 | ~1.050 | 47 hàm test: unit, tích hợp, baseline dữ liệu thật |
| `docs` | Tài liệu | 3 | 223 | Từ điển dữ liệu, runbook vận hành, luận điểm 3V |
| `assets` | Tài nguyên tĩnh | 1 | 277 | CSS chủ đề cho dashboard |

Cột "Dòng" không tính các tệp `__init__.py` (tổng ~10 dòng); tổng mã Python trong `src/` ≈ 4.200 dòng.

## src.config

**Trách nhiệm**: đọc `config.yaml` (hoặc tệp được trỏ), ánh xạ sang `AppConfig` (frozen dataclass, 28 trường),
tính đường dẫn tuyệt đối từ `workspace_root`, và **tạo** toàn bộ thư mục đầu ra khi nạp.

**Tệp**: `src/config.py`.

**Biểu tượng công khai**: `AppConfig`, `PROJECT_ROOT`, `load_config`.

**Phụ thuộc**: `PyYAML`, `src.common.exceptions.ConfigurationError`.

**Được dùng bởi**: mọi điểm vào (`src.pipeline.cli`, `src.dashboard.__main__`) và mọi lớp nhận `config`.

**Ghi chú**: `raw_csv_dir` bắt buộc tồn tại, nếu không ném `ConfigurationError`; các giá trị mặc định
trùng với `config.yaml` nên thiếu khóa vẫn chạy. `quality.memory_warn_mb`/`memory_fail_mb` được nạp
nhưng **không nơi nào tiêu thụ**.

## src.common

**Trách nhiệm**: hạ tầng không phụ thuộc nghiệp vụ — ghi tệp nguyên tử, băm SHA-256, đọc CSV/Parquet,
tạo `RunContext`, ghi log JSONL, dataclass hợp đồng dữ liệu, cây ngoại lệ, đo bộ nhớ.

**Tệp**: `io.py` (88), `logging.py` (66), `types.py` (139), `exceptions.py` (23), `memory.py` (30), `__init__.py`.

**Biểu tượng công khai**: `AtomicWriter`, `read_csv`, `read_parquet`, `sha256_file`, `validate_columns`,
`JsonLogger`, `new_run_context`, 14 dataclass trong `types`, 5 ngoại lệ, `MemoryProbe`.

**Phụ thuộc**: `pandas`, `pyarrow` (gián tiếp qua `DataFrame.to_parquet`), thư viện chuẩn.

**Được dùng bởi**: tất cả gói `src.*` khác.

**Ghi chú**: `MemoryProbe` không được tham chiếu ở bất kỳ đâu (mã chết); `AtomicWriter.cleanup()`
xóa cả thư mục temp của lần chạy.

## src.ingest

**Trách nhiệm**: định nghĩa hợp đồng đầu vào cho 9 CSV (`TABLE_SPECS` gồm tên tệp, thứ tự cột, khóa tự nhiên,
số dòng kỳ vọng), đọc với `dtype=str` và `utf-8-sig`, băm SHA-256, ghi raw Parquet, dựng báo cáo ingest;
cung cấp tiện ích đối chiếu `payment_value` với `price + freight_value`.

**Tệp**: `schemas.py` (132), `reader.py` (75), `reports.py` (77), `__init__.py`.

**Biểu tượng công khai**: `TABLE_SPECS`, `ingest_table`, `ingest_all`, `ReportWriter`, `reconcile_payments`.

**Phụ thuộc**: `src.common.*`, `pandas`.

**Được dùng bởi**: `src.pipeline.stages`, `src.pipeline.micro_batch`, `src.pipeline.replay`,
`src.quality.gate` (đọc `TABLE_SPECS`), test tích hợp.

**Ghi chú**: `ingest_all` đặt `passed = all(rows == expected_rows)`; ingest **không** chặn pipeline —
`stages._run_all` vẫn chạy tiếp và chỉ đánh dấu stage `failed`.

## src.clean

**Trách nhiệm**: chuyển dữ liệu thô sang kiểu dùng được (số `Int64`, `float`, `datetime`), chuẩn hóa
văn bản (NFC, trim, gộp khoảng trắng, lower cho thành phố; upper cho bang), làm giàu danh mục sản phẩm
qua bảng dịch, gộp geolocation về **một dòng / mã bưu chính**, và gắn cờ dị thường thay vì xóa dòng.

**Tệp**: `pipeline.py` (91), `common.py` (58), `geolocation.py` (119), `products.py` (55), `orders.py` (29),
`items.py` (21), `reviews.py` (17), `payments.py` (16), `customers.py` (15), `sellers.py` (15), `__init__.py`.

**Biểu tượng công khai**: `clean_all` và 9 hàm `clean_*` (`clean_orders`, `clean_customers`, `clean_sellers`,
`clean_products`, `clean_translation`, `clean_order_items`, `clean_payments`, `clean_reviews`, `clean_geolocation`),
tiện ích `src.clean.common`.

**Phụ thuộc**: `pandas`, `src.common.types.GeoCleaningStats`.

**Được dùng bởi**: `src.pipeline.stages`, `src.pipeline.micro_batch` (dùng lại từng hàm cho batch),
`tests/conftest.py`, test đơn vị.

**Ghi chú**: `clean_geolocation` là nơi duy nhất thực hiện **khử trùng lặp + tổng hợp** (738.332 dòng sau
khử trùng lặp → 19.015 mã bưu chính), ngăn chặn bùng nổ join; bbox hợp lệ lấy từ `config.geolocation`
(vĩ độ −34..6, kinh độ −74..−34).

## src.quality

**Trách nhiệm**: cổng chất lượng sau khi làm sạch. Chế độ `incremental` chạy 21 check cấu trúc
(duy nhất, khóa ngoại, miền giá trị, giá trị cho phép). Chế độ `full` thêm 9 check số dòng và
10 bộ đếm dị thường so với allowlist. `enforce` biến báo cáo fail thành ngoại lệ chặn pipeline.

**Tệp**: `gate.py` (304), `checks.py` (121), `allowlist.py` (14), `__init__.py`.

**Biểu tượng công khai**: `QualityGate` (`run`, `enforce`), 6 hàm `checks.*`, `EXPECTED_ANOMALIES`.

**Phụ thuộc**: `pandas`, `src.common.types`, `src.common.exceptions`, `src.ingest.schemas`.

**Được dùng bởi**: `src.pipeline.stages`, `src.pipeline.micro_batch`, test.

**Ghi chú**: allowlist là **hợp đồng dữ liệu**: `orders_without_items=775`, `orders_without_payment=1`,
`customer_zips_missing_geo=278`, `seller_zips_missing_geo=7`, `products_missing_category=610`,
`orders_multiple_reviews=547`, `geo_exact_duplicates=261831`, `geo_outside_bbox=42`,
`geo_zips_without_coord=5`, `price_outliers=8427`. Mọi thay đổi dữ liệu nguồn sẽ làm fail chế độ `full`.

## src.external

**Trách nhiệm**: lấy danh mục 27 bang + vùng từ API IBGE, đệm vào `dataset/external/ibge/estados.json`
kèm metadata (SHA-256, thời điểm, nguồn), chịu lỗi mạng bằng retry rồi fallback cache; cung cấp
ánh xạ `state → region` và kiểm tra tính đầy đủ (27 bang, 5 vùng, không null, đủ bang có trong dữ liệu).

**Tệp**: `ibge.py` (131), `region.py` (45), `__init__.py`.

**Biểu tượng công khai**: `IbgeClient` (`fetch_states`, `fetch_municipalities`, `load_region_map`),
`RegionMapper` (`validate`, `attach`), `EXPECTED_REGIONS`.

**Phụ thuộc**: `urllib.request` (chuẩn), `pandas`, `src.common.*`.

**Được dùng bởi**: `src.integrate.pipeline`, `src.integrate.dimensions`, test.

**Ghi chú**: cache hợp lệ là điều kiện sống còn — môi trường không mạng vẫn chạy được nhờ
`estados.json` đi kèm (metadata ghi `source = bundled-official-snapshot`).

## src.integrate

**Trách nhiệm**: dựng star schema từ dữ liệu đã làm sạch — 5 dimension (`dim_customer`, `dim_product`,
`dim_seller`, `dim_geography`, `dim_date`), 4 fact (`fact_order_items`, `fact_orders`, `fact_payments`,
`fact_reviews`), 2 aggregate ngày (`agg_sales_daily`, `agg_delivery_daily`); kiểm grain/khóa/quan hệ;
đối chiếu 5 KPI với baseline; ghi mart nguyên tử và tạo 11 view DuckDB.

**Tệp**: `pipeline.py` (128), `dimensions.py` (118), `facts.py` (162), `aggregates.py` (87),
`validate.py` (147), `reconcile.py` (66), `catalog.py` (54), `connections.py` (30), `__init__.py`.

**Biểu tượng công khai**: `integrate_all`, `load_cleaned`, `IntegrationResult`, `DimensionBuilder`,
`FactBuilder`, `Aggregator`, `StarSchemaValidator`, `KpiReconciler`, `DuckDbCatalog`, `ConnectionFactory`,
`CLEANED_TABLES`, `VIEW_TABLES`.

**Phụ thuộc**: `pandas`, `duckdb`, `src.external`, `src.common`, và (import thừa) `src.analytics`.

**Được dùng bởi**: `src.pipeline.stages`, `src.pipeline.micro_batch`, `src.dashboard.app` (qua `ConnectionFactory`).

**Ghi chú**: `fact_orders.category` là **danh mục đại diện** của đơn (tổng `item_total` lớn nhất, ưu tiên
danh mục không thiếu); `is_late` chỉ đúng cho đơn `delivered`; `dim_date` phủ toàn dải ngày mua (774 ngày)
và gắn `is_sparse_period` cho 2016.

## src.analytics

**Trách nhiệm**: lớp truy vấn chỉ đọc. Dựng mệnh đề `WHERE` an toàn từ `KpiFilters`, chạy 5 truy vấn
tổng hợp trên view DuckDB, trả `dict`/`DataFrame` đã tính AOV và tỷ lệ trễ.

**Tệp**: `service.py` (281), `filters.py` (7), `__init__.py`.

**Biểu tượng công khai**: `AnalyticsService`, `KpiFilters` (re-export).

**Phụ thuộc**: `pandas`, `duckdb` (qua `ConnectionFactory`), `src.common.types`.

**Được dùng bởi**: `src.dashboard.app`, `src.pipeline.stages` (smoke test tầng `analyze`), test tích hợp.

**Ghi chú**: mọi truy vấn doanh thu đều **inner join `v_dim_date`**, nên đơn có `date_key` NULL
(`order_purchase_timestamp` lỗi) sẽ biến mất khỏi KPI — hiện tượng này không được test riêng.

## src.dashboard

**Trách nhiệm**: ứng dụng Plotly Dash tiếng Việt với thanh lọc (ngày, bang, vùng, danh mục, trạng thái),
dải 4 KPI, 3 tab (Tổng quan / Danh mục / Giao vận), cảnh báo giai đoạn 2016 thiếu dữ liệu, banner lỗi.

**Tệp**: `app.py` (486), `components.py` (111), `formatting.py` (39), `__main__.py` (16), `__init__.py`.

**Biểu tượng công khai**: `create_app`, `build_layout`, `build_dashboard_outputs`, `STATUS_OPTIONS`,
`components.*`, `formatting.*`.

**Phụ thuộc**: `dash`, `plotly`, `pandas`, `src.analytics`, `src.integrate.connections`, `assets/style.css`.

**Được dùng bởi**: `src/dashboard/__main__.py`, test smoke.

**Ghi chú**: hai tab "Tổng quan" và "Danh mục" vẽ **cùng một figure** từ `category_frame` (hai output
`category-bar` và `category-detail-bar` nhận đối tượng giống hệt); nút "Thử lại" trong banner lỗi
không có callback.

## src.pipeline

**Trách nhiệm**: điều phối toàn hệ thống — phân tích tham số CLI, chạy tầng hoặc toàn bộ, ghi
`run-summary.json`, xử lý micro-batch có manifest idempotent, upsert theo khóa tự nhiên, và sinh batch replay.

**Tệp**: `stages.py` (234), `micro_batch.py` (188), `cli.py` (81), `replay.py` (54), `manifest.py` (47),
`upsert.py` (21), `__main__.py` (4), `__init__.py`.

**Biểu tượng công khai**: `main`, `build_parser`, `run_all`, `run_stage`, `process_inbox`,
`BatchResult`, `generate`, `ManifestStore`, `upsert`, `STAGES`, `TABLE_KEYS`.

**Phụ thuộc**: hầu hết các gói `src.*` (đây là điểm ghép nối trung tâm).

**Được dùng bởi**: `python -m src.pipeline`, test.

**Ghi chú**: chỉ `micro-batch`/`replay` dùng `ManifestStore`; `run --stage all` không ghi manifest.
`process_inbox` sao toàn bộ `data/cleaned` vào temp cho mỗi batch (chi phí O(kích thước cleaned) mỗi lần).

## tests

**Trách nhiệm**: bộ kiểm thử ba tầng — unit (DataFrame nhỏ, fixture trong `conftest.py`), tích hợp
end-to-end trên dữ liệu thật (đánh dấu `slow`), và baseline dữ liệu (khẳng định các hằng số dị thường).

**Tệp**: `conftest.py` (320) + `unit/` 21 mô-đun + `integration/` 3 mô-đun + `data_quality/` 1 mô-đun.

**Biểu tượng công khai**: fixture `config`, `real_config`, `run`, `writer`, `logger`, `small_*`,
`region_map`, `small_cleaned`.

**Phụ thuộc**: `pytest`, `pandas`, toàn bộ `src.*`, `dataset/external/ibge/estados.json`.

**Được dùng bởi**: `pytest` theo `pytest.ini`.

**Ghi chú**: 47 hàm test, 6 hàm `slow`. Không có test cho `src/pipeline/stages.run_all` (đường `--stage all`),
`src/pipeline/micro_batch` (đường lỗi), `src/integrate/validate`, `src/integrate/reconcile`, `src/integrate/catalog`,
`src/analytics/service` ở mức đơn vị. Xem `code-quality-assessment.md`.

## docs

**Trách nhiệm**: tài liệu cho người đọc — từ điển dữ liệu star schema (`data-dictionary.md`),
runbook xử lý sự cố (`runbook.md`), và luận điểm 3V (`3v.md`).

**Tệp**: `data-dictionary.md` (134), `runbook.md` (62), `3v.md` (27).

**Được dùng bởi**: con người; không có mã nào đọc các tệp này.

**Ghi chú**: `README.md` còn nhắc `aidlc-docs/` nhưng thư mục này **không tồn tại** trong repo
(tham chiếu chết sau khi gỡ AI-DLC v1 — commit `41c422f`).

## assets

**Trách nhiệm**: một tệp CSS cung cấp token thiết kế (biến `--ink`, `--paper`, `--ochre`, `--clay`),
lưới biểu đồ, kiểu KPI card, bảng dữ liệu, banner lỗi.

**Tệp**: `assets/style.css` (277 dòng).

**Được dùng bởi**: `Dash(assets_folder=str(config.workspace_root / "assets"))` trong `src/dashboard/app.py`.

**Ghi chú**: đường dẫn assets tính từ `workspace_root` (thư mục chứa `config.yaml`), không phải từ gói
`src.dashboard` — chạy dashboard từ thư mục khác vẫn đúng miễn `config.yaml` được tìm thấy.
