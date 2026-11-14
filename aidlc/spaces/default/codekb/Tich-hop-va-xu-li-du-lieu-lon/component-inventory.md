# Danh mục thành phần — Olist E-commerce Data Pipeline

> Đơn vị thành phần là **gói Python** trong `src/` cộng bốn khu vực hỗ trợ (`tests/`, `docs/`, `assets/`,
> `config/`). Tên heading dưới đây là định danh thành phần được dùng lại trong
> `reverse-engineering-timestamp.md` (khối Scope of Analysis) — **không đổi tên khi cập nhật**.
> Danh mục tệp chi tiết theo từng tệp nằm ở `code-structure.md`; chữ ký hàm ở `api-documentation.md`.
> Lần cập nhật tập trung 2026-11-11 tại commit `ea77bdf88d1431de11c36e1b739972bd594063f0` đọc sâu
> `src.analytics`, `src.integrate`, `src.dashboard`, `src.pipeline` và `tests`; các thành phần khác giữ mô tả
> cũ với số dòng đã đo lại (chưa xác minh lại).

## Tổng hợp

| Thành phần | Loại | Tệp | Dòng | Vai trò một câu |
|---|---|---:|---:|---|
| `src.config` | Hạ tầng | 1 | 157 | Nạp `config.yaml` thành `AppConfig` bất biến (34 trường) và tạo thư mục đầu ra |
| `src.common` | Thư viện dùng chung | 7 | 551 | IO nguyên tử, log JSONL + giữ 10 tệp, dataclass, ngoại lệ, sổ KPI, đo bộ nhớ |
| `src.ingest` | Tầng ETL | 4 | 285 | Hợp đồng lược đồ 9 bảng, đọc CSV, ghi raw Parquet, báo cáo ingest |
| `src.clean` | Tầng ETL | 11 | 437 | Chuẩn hóa kiểu/chuỗi và gắn cờ chất lượng cho 9 bảng |
| `src.quality` | Cổng kiểm soát | 4 | 440 | 21 check cấu trúc + 9 check số dòng + 10 dị thường allowlist |
| `src.external` | Tích hợp nguồn ngoài | 3 | 177 | Lấy/đệm 27 bang IBGE và ánh xạ bang → 5 vùng |
| `src.integrate` | Tầng mô hình hóa | 9 | 793 | Star schema, kiểm grain/khóa, đối chiếu KPI, catalog DuckDB 11 view |
| `src.integration` | Tầng tích hợp dữ liệu | 9 | 4.138 | Lược đồ trung gian, nạp CSV, viết lại + chạy truy vấn, chọn nguồn, thẻ tab |
| `src.linkage` | Ghép bản ghi | 5 | 784 | Chỉ mục ứng viên, tính điểm, sinh kết quả ghép theo hai đối tượng |
| `src.analytics` | Tầng truy vấn + suy luận | 6 | **1.578** | 9 truy vấn chỉ đọc, 5 phép kiểm định, khung báo cáo 2 khối, bộ phân loại đơn trễ |
| `src.dashboard` | Tầng trình bày | 6 | **1.322** | Layout **5 tab**, **9 callback**, figure Plotly, định dạng Brazil, tab đọc báo cáo |
| `src.pipeline` | Điều phối | 8 | **668** | CLI 3 lệnh con, **5** tên tầng, micro-batch, manifest, upsert, replay |
| `tests` | Kiểm thử | 54 | **10.086** | **499** hàm test: unit (nhiều tệp tự dựng mart tạm), 12 test `slow` trên dữ liệu thật |
| `docs` | Tài liệu | 3 | — | Từ điển dữ liệu (11 bảng mart), runbook vận hành, luận điểm 3V |
| `assets` | Tài nguyên tĩnh | 1 | — | CSS chủ đề cho dashboard (đọc các khối `.analysis-tab`, `.integration-*`) |
| `config` | Hợp đồng cấu hình | 3 | — | 3 YAML: lược đồ trung gian, tab Tích hợp, hồ sơ nguồn |

Cột "Dòng" là số dòng vật lý đo trên đĩa (gồm cả các tệp `__init__.py`); tổng mã Python trong `src/` =
**11.333** dòng (74 tệp).

## src.config

**Trách nhiệm**: đọc `config.yaml` (hoặc tệp được trỏ), ánh xạ sang `AppConfig` (frozen dataclass, 34 trường),
tính đường dẫn tuyệt đối từ `workspace_root`, và **tạo** toàn bộ thư mục đầu ra khi nạp.

**Tệp**: `src/config.py` (157).

**Biểu tượng công khai**: `AppConfig`, `PROJECT_ROOT`, `load_config`.

**Phụ thuộc**: `PyYAML`, `src.common.exceptions.ConfigurationError`.

**Được dùng bởi**: mọi điểm vào (`src.pipeline.cli`, `src.dashboard.__main__`) và mọi lớp nhận `config`.

**Ghi chú**: `raw_csv_dir` bắt buộc tồn tại; 3 đường dẫn hợp đồng YAML (`mediated_schema_path`,
`integration_tab_path`, `integration_sources_path`) là trường hạng nhất. `reports_dir`/`temp_dir` được
`src/analytics/report.py` dùng để đặt tệp báo cáo và tệp tạm. `quality.memory_warn_mb`/`memory_fail_mb`
được nạp; `memory_fail_mb` nay được **test** dùng (`test_u1_stats_end_to_end.py:49`), `memory_warn_mb` vẫn
chưa ai đọc. **Không có** trường nào cho thư mục mô hình (`data/models/`) — muốn lưu mô hình phải thêm trường.

## src.common

**Trách nhiệm**: hạ tầng không phụ thuộc nghiệp vụ — ghi tệp nguyên tử, băm SHA-256, đọc CSV/Parquet,
tạo `RunContext`, ghi log JSONL + dọn log cũ, dataclass hợp đồng dữ liệu, cây ngoại lệ, **sổ KPI dùng chung**,
đo bộ nhớ.

**Tệp**: `types.py` (139), `logging.py` (119), `kpis.py` (108), `io.py` (88), `exceptions.py` (66),
`memory.py` (30), `__init__.py`.

**Biểu tượng công khai**: `AtomicWriter`, `read_csv`, `read_parquet`, `sha256_file`, `validate_columns`,
`JsonLogger`, `NullLogger`, `new_run_context`, `prune_logs`, 14 dataclass trong `types`, 9 ngoại lệ,
`KPI_LEDGER`/`KpiLedgerEntry`/`REVENUE_DEFINITION`/`validate_ledger`/`kpi`, `MemoryProbe`.

**Phụ thuộc**: `pandas`, `pyarrow` (gián tiếp qua `DataFrame.to_parquet`), thư viện chuẩn.

**Được dùng bởi**: tất cả gói `src.*` khác.

**Ghi chú**: `REVENUE_DEFINITION` là **một** định nghĩa doanh thu cho mọi KPI tiền, và `validate_ledger`
chạy ngay khi import như chốt tự kiểm; `src/analytics/report.py` chép lại chính chuỗi đó vào khối
`seasonal.revenue_definition`, `statistics.py` và `test_analytics_statistics.py` so lại với hằng số này.
`MemoryProbe` nay **có** người dùng (một test `slow`), khác với ghi chú "mã chết" của lần quét trước.

## src.ingest

**Trách nhiệm**: định nghĩa hợp đồng đầu vào cho 9 CSV (`TABLE_SPECS`), đọc với `dtype=str` và `utf-8-sig`,
băm SHA-256, ghi raw Parquet, dựng báo cáo ingest; cung cấp `reconcile_payments`.

**Tệp**: `schemas.py` (132), `reports.py` (77), `reader.py` (75), `__init__.py`.

**Biểu tượng công khai**: `TABLE_SPECS`, `ingest_table`, `ingest_all`, `ReportWriter`, `reconcile_payments`.

**Phụ thuộc**: `src.common.*`, `pandas`.

**Được dùng bởi**: `src.pipeline.stages`, `src.pipeline.micro_batch`, `src.pipeline.replay`,
`src.quality.gate`, `src.integration.schema`, test tích hợp.

**Ghi chú**: `ingest_all` đặt `passed = all(rows == expected_rows)`; ingest **không** chặn pipeline —
`stages._run_all` vẫn chạy tiếp và chỉ đánh dấu stage `failed`. `TABLE_SPECS["orders"]` có đủ 5 mốc thời gian
gồm **`order_delivered_carrier_date`**; `TABLE_SPECS["order_items"]` có **`shipping_limit_date`** — hai cột
mà mart hiện **không** mang xuống (xem `src.integrate`).

## src.clean

**Trách nhiệm**: chuyển dữ liệu thô sang kiểu dùng được (`Int64`, `float`, `datetime`), chuẩn hóa
văn bản (NFC, trim, gộp khoảng trắng, lower cho thành phố; upper cho bang), làm giàu danh mục sản phẩm
qua bảng dịch, gộp geolocation về **một dòng / mã bưu chính**, và gắn cờ dị thường thay vì xóa dòng.

**Tệp**: `geolocation.py` (119), `pipeline.py` (91), `common.py` (58), `products.py` (55), `orders.py` (29),
`items.py` (21), `reviews.py` (17), `payments.py` (16), `customers.py` (15), `sellers.py` (15), `__init__.py`.

**Biểu tượng công khai**: `clean_all` và 9 hàm `clean_*`, tiện ích `src.clean.common`.

**Phụ thuộc**: `pandas`, `src.common.types.GeoCleaningStats`.

**Được dùng bởi**: `src.pipeline.stages`, `src.pipeline.micro_batch`, `tests/conftest.py`, test đơn vị.

**Ghi chú**: `clean_geolocation` là nơi duy nhất thực hiện **khử trùng lặp + tổng hợp** (19.015 mã bưu chính),
ngăn chặn bùng nổ join. `clean_orders` **giữ đủ 5 mốc thời gian** và gắn `has_invalid_timestamp` +
`is_delivered` — nghĩa là dữ liệu cần cho khung dự đoán "bàn giao cho đơn vị vận chuyển" **đã có** ở tầng
cleaned, chỉ chưa được đưa vào mart.

## src.quality

**Trách nhiệm**: cổng chất lượng sau khi làm sạch. Chế độ `incremental` chạy 21 check cấu trúc; chế độ `full`
thêm 9 check số dòng và 10 bộ đếm dị thường so với allowlist. `enforce` biến báo cáo fail thành ngoại lệ.

**Tệp**: `gate.py` (304), `checks.py` (121), `allowlist.py` (14), `__init__.py`.

**Biểu tượng công khai**: `QualityGate` (`run`, `enforce`), 6 hàm `checks.*`, `EXPECTED_ANOMALIES`.

**Phụ thuộc**: `pandas`, `src.common.*`, `src.ingest.schemas`.

**Được dùng bởi**: `src.pipeline.stages`, `src.pipeline.micro_batch`, test.

**Ghi chú**: allowlist là **hợp đồng dữ liệu**: `orders_without_items=775`, `orders_without_payment=1`,
`customer_zips_missing_geo=278`, `seller_zips_missing_geo=7`, `products_missing_category=610`,
`orders_multiple_reviews=547`, `geo_exact_duplicates=261831`, `geo_outside_bbox=42`,
`geo_zips_without_coord=5`, `price_outliers=8427` (số được test tích hợp khẳng định lại, ví dụ
`test_u1_end_to_end.py:34,39`). **Không đếm lại số check trong lần quét này** — gói chỉ đọc ở mức tiêu đề.

## src.external

**Trách nhiệm**: lấy danh mục 27 bang + vùng từ API IBGE, đệm vào `dataset/external/ibge/estados.json`
kèm metadata, chịu lỗi mạng bằng retry rồi fallback cache; cung cấp ánh xạ `state → region` và kiểm tra
tính đầy đủ (27 bang, 5 vùng, không null).

**Tệp**: `ibge.py` (131), `region.py` (45), `__init__.py`.

**Biểu tượng công khai**: `IbgeClient`, `RegionMapper`, `EXPECTED_REGIONS`.

**Phụ thuộc**: `urllib.request` (chuẩn), `pandas`, `src.common.*`.

**Được dùng bởi**: `src.integrate.pipeline`, `src.integrate.dimensions`, test.

**Ghi chú**: cache hợp lệ là điều kiện sống còn — môi trường không mạng vẫn chạy được nhờ `estados.json`
đi kèm; CI không truyền `--refresh-ibge` vì lý do này.

## src.integrate

**Trách nhiệm**: dựng star schema từ dữ liệu đã làm sạch — 5 dimension, 4 fact, 2 aggregate; kiểm grain/khóa;
đối chiếu 5 KPI với baseline; ghi mart nguyên tử và tạo 11 view DuckDB.

**Tệp**: `facts.py` (162), `validate.py` (147), `pipeline.py` (128), `dimensions.py` (118),
`aggregates.py` (87), `reconcile.py` (66), `catalog.py` (54), `connections.py` (30), `__init__.py`.

**Biểu tượng công khai**: `integrate_all`, `load_cleaned`, `IntegrationResult`, `DimensionBuilder`,
`FactBuilder`, `Aggregator`, `StarSchemaValidator`, `KpiReconciler`, `DuckDbCatalog`, `ConnectionFactory`,
`CLEANED_TABLES`, `VIEW_TABLES`.

**Phụ thuộc**: `pandas`, `duckdb`, `src.external`, `src.common`, và (import thừa) `src.analytics`.

**Được dùng bởi**: `src.pipeline.stages`, `src.pipeline.micro_batch`, `src.dashboard.app` (qua `ConnectionFactory`),
`src.analytics.service` (cùng lý do), `src.analytics.model` (gián tiếp, qua service).

**Ghi chú (đọc kỹ trước khi mở rộng mart)**:
- `fact_orders` có **13 cột** (`facts.py:99-115`): `order_id`, `customer_id`, `date_key`, `category`,
  `order_status`, `is_delivered`, `order_delivered_customer_date`, `order_estimated_delivery_date`,
  `delivery_days`, `is_late`, `has_items`, `has_payment`, `has_review`. **Không có** `order_approved_at`,
  **không có** `order_delivered_carrier_date` (hai cột này có trong cleaned).
- `fact_order_items` có **12 cột**; **không có** `shipping_limit_date`, **không có** `seller_state`.
- `dim_product` chỉ giữ 4 cột danh mục; `dim_seller` có `state`/`region`; `dim_date` 774 ngày.
- `category` của `fact_orders` là **danh mục đại diện** (nhiều tiền nhất) của đơn; `is_late` chỉ đúng cho đơn
  `delivered` (kiểm bởi `L-01`); `dim_date` gắn `is_sparse_period` cho 2016.
- `StarSchemaValidator.EXPECTED` (9 số dòng) chỉ kiểm **số dòng**, không kiểm **tập cột** → thêm cột vào fact
  không làm cổng này đỏ, nhưng làm lệch `docs/data-dictionary.md` và mọi truy vấn `SELECT *`.
- `KpiReconciler` là chốt duy nhất của 5 KPI baseline; nó đọc `fact_order_items.is_delivered` cho doanh thu và
  `nunique(order_id)` cho số đơn.

## src.integration

**Trách nhiệm**: cài đặt bốn nhóm kiến thức tích hợp dữ liệu — (1) lược đồ trung gian khai báo được
(`config/mediated-schema.yaml` → `MediatedSchemaView`), (2) nạp CSV nguồn theo lược đồ, (3) viết lại
và chạy 3 mẫu truy vấn rồi đối chiếu KPI với tham chiếu, (4) chọn nguồn theo độ phủ trường/chi phí/độ trễ;
cộng lớp giao diện `card`/`tab` cho tab "Tích hợp".

**Tệp**: `tab.py` (1.380), `rewrite.py` (819), `selector.py` (543), `schema.py` (368), `card.py` (348),
`models.py` (253), `load.py` (240), `query.py` (186), `__init__.py`.

**Biểu tượng công khai**: `load_schema`, `build_field_catalogue`, `load_don_hang`, `clear_cache`,
`rewrite_plan`, `run_monthly_orders`, `load_source_catalogue`, `select_source`, `load_tab_config`,
`TabConfig`, `IntegrationTab`, `register_callbacks`, `CARD_TITLES`, `SCREENS`, `STATE_*`, `STATE_ICONS`,
`TEXTS`.

**Phụ thuộc**: `pandas`, `duckdb` (qua `src.integrate.connections`), `src.common.*`, `src.ingest.schemas`,
`dash`/`dash-mantine-components`, 3 hợp đồng YAML trong `config/`.

**Được dùng bởi**: `src.dashboard.app` (layout + 6 callback), `src.dashboard.analysis_tab` (dùng lại
`STATE_ICONS`/`TEXTS` để đồng bộ nhãn trạng thái với tab "Tích hợp"), và **không** nằm trong chuỗi
`run --stage`.

**Ghi chú**: đây là gói **lớn nhất** repo (4.138 dòng, 37% mã `src/`), `tab.py` một mình 1.380 dòng;
mọi định danh hướng người dùng bằng tiếng Việt không dấu. `analysis_tab.py` phụ thuộc chéo vào `card.py`
hai tên (`STATE_ICONS`, `TEXTS`) — đổi hai bảng đó là đổi tab phân tích.

## src.linkage

**Trách nhiệm**: ghép bản ghi giữa các nguồn — dựng chỉ mục ứng viên theo đối tượng (khách hàng, người bán),
chuẩn hóa thành phố, tính điểm tương đồng có ngưỡng, và ghi kết quả JSON vào `data/integration/`.

**Tệp**: `score.py` (231), `models.py` (217), `index.py` (186), `result.py` (149), `__init__.py`.

**Biểu tượng công khai**: `TARGET_ENTITIES`, `normalize_city`, `MatchPair`, `build_index`, `generate_linkage`.

**Phụ thuộc**: `pandas`, `src.common.*`, `src.clean.*`, `src.config`.

**Được dùng bởi**: `src.pipeline.stages._run_linkage` (tầng phụ trong `run --stage all`/`integrate`),
`src.integration.tab` (đọc kết quả để điền thẻ).

**Ghi chú**: chạy **một lần cho mỗi đối tượng**, lỗi của đối tượng này không chặn đối tượng kia
(`stages.py:77-88`).

## src.analytics

**Trách nhiệm**: gói duy nhất của tầng phân tích, nay có **bốn vai trò**:
(1) **truy vấn chỉ đọc** trên view DuckDB (`service.py`, 9 phương thức, `_where` là nơi duy nhất ghép bộ lọc);
(2) **kiểm định thống kê** (`statistics.py`, 5 phép + bộ gom `skipped`, dùng `scipy`);
(3) **mô hình phân loại đơn trễ** (`model.py`, 11 đặc trưng + 10 cột cấm, chia theo thời gian, logistic
cân trọng số, ngưỡng theo F1, AUC + cờ dưới 0,70);
(4) **hợp đồng báo cáo** (`report.py`, phiên bản 2, 12 dataclass, ghi nguyên tử, đọc 4 trạng thái).

**Tệp**: `model.py` (368), `report.py` (502), `service.py` (387), `statistics.py` (313), `filters.py` (7),
`__init__.py`.

**Biểu tượng công khai**: `AnalyticsService` (+ 4 hằng SQL và `MAX_CORRELATION_ROWS`), `KpiFilters`
(re-export qua `filters`), `wilson_interval`/`late_rate`/`compare_states`/`price_freight_correlation`/
`region_late_test`/`seasonal_decomposition`/`ordered_skips`/`collect_stats`/`build_analysis_report`,
`ModelError`/`TARGET`/`FEATURES`/`FORBIDDEN_COLUMNS`/`AUC_TARGET`/`SPLIT_DATE`/`EXPECTED_*`/`train_model`/
`train_from_frame`/`validate_features`/`delivered_population`/`build_feature_frame`/`split_frame`/
`encode_features`/`choose_threshold`/`build_model_block`, `ReportError`/`AnalysisReport`/`StatsBlock`/
`ModelBlock`/`ReportView`/`STATUS_*`/`REPORT_VERSION`/`report_path`/`write_report`/`read_report`.

**Phụ thuộc**: `pandas`, `duckdb` (qua `ConnectionFactory`), `scipy` (chỉ `statistics.py`),
`scikit-learn` (chỉ `model.py`), `src.common.*`, `src.integrate.connections`.

**Được dùng bởi**: `src.dashboard.app` (4 tab báo cáo), `src.dashboard.analysis_tab` (chỉ đọc
`report`/`model`/`statistics`), `src.pipeline.stages` (tầng `analyze` và tầng `stats`), test.

**Ghi chú (quan trọng nhất cho việc mở rộng)**:
- **`training_frame()` là cửa duy nhất** để lấy dữ liệu cho mô hình, và nó ở **grain đơn**; mọi thay đổi sang
  grain dòng hàng là thay đổi `TRAINING_FRAME_SQL` + `training_frame` + toàn bộ `model.py` phía sau.
- Mọi truy vấn doanh thu đều **inner join `v_dim_date`**, nên đơn có `date_key` NULL
  (`order_purchase_timestamp` lỗi) sẽ biến mất khỏi KPI — hiện tượng này không được test riêng (TD-12).
- `training_frame()` **không** nhận `KpiFilters` và **không** lọc `is_delivered`: việc lọc nằm ở
  `model.delivered_population`, nơi còn kiểm baseline 96.478/7.826.
- `model.py` và `statistics.py` **không** mở kết nối, **không** đọc/ghi tệp — đây là ranh giới giữ được
  tính "thuần" cho test (toàn bộ test của hai mô-đun này chạy trên `DataFrame`/DuckDB tạm).
- `report.py` là **nơi duy nhất** biết tên/phiên bản/cấu trúc `analysis.json`; `analysis_tab.py` và test đều
  đọc qua nó (`read_report`).

## src.dashboard

**Trách nhiệm**: ứng dụng Plotly Dash tiếng Việt với thanh lọc (ngày, bang, vùng, danh mục, trạng thái),
dải 4 KPI, **5 tab** (Tổng quan / Danh mục / Giao vận / Tích hợp / Kết quả phân tích), cảnh báo giai đoạn 2016
thiếu dữ liệu, banner lỗi.

**Tệp**: `app.py` (589), `analysis_tab.py` (566), `components.py` (111), `formatting.py` (39),
`__main__.py` (16), `__init__.py`.

**Biểu tượng công khai**: `create_app`, `build_layout`, `build_dashboard_outputs`, `STATUS_OPTIONS`,
`reset_integration_logs`, `_integration_logger`, `AnalysisTab`, `AnalysisPanel`, `register_callback`,
`TAB_VALUE="phan-tich"`, `TAB_LABEL="Kết quả phân tích"`, `SECTION_IDS`, `CARD_IDS`, `components.*`,
`formatting.*`.

**Phụ thuộc**: `dash`, `dash-mantine-components`, `plotly`, `pandas`, `src.analytics.*`,
`src.integration.card`/`tab`, `src.integrate.connections`, `src.common.logging`, `src.common.exceptions`,
`assets/style.css`.

**Được dùng bởi**: `src/dashboard/__main__.py`, test smoke, ba test tích hợp.

**Ghi chú**:
- Tab "Tổng quan" và tab "Danh mục" vẫn vẽ **cùng một figure** từ `category_frame` (`app.py:563-564`).
- Nút "Thử lại" (`components.py:99`) vẫn **không** có callback; chuỗi tháng bị cắt bằng hằng số `"2017-01"`
  (`app.py:530`); câu "329 đơn" là số chép tay (`components.py:108`).
- `create_app` dựng layout với **5 tab** và **9 callback**, bật `suppress_callback_exceptions=True`.
- Tab thứ năm **không** đọc tệp lúc dựng layout — đọc trong callback, đúng một lần mỗi lần chọn tab; mọi
  vùng đều có `aria-label`, không có `tabIndex` dương, mọi lớp CSS dùng trong tab phải tồn tại trong
  `assets/style.css`, và khối `.analysis-tab` không được dùng token `--text-3`.
- Tab thứ năm **chỉ đọc**: không thanh trượt, không ô nhập (`test_dashboard_analysis_tab.py:456-463`) —
  trái với hạng mục "vùng nhập liệu dự đoán" của intent hiện tại.

## src.pipeline

**Trách nhiệm**: điều phối toàn hệ thống — phân tích tham số CLI, chạy tầng hoặc toàn bộ, ghi
`run-summary.json`, chạy ghép bản ghi như tầng phụ, xử lý micro-batch có manifest idempotent, upsert theo
khóa tự nhiên, sinh batch replay, chạy tầng `stats` (kiểm định + mô hình + một lần ghi báo cáo), dọn log cũ.

**Tệp**: `stages.py` (274), `micro_batch.py` (188), `cli.py` (79), `replay.py` (54), `manifest.py` (47),
`upsert.py` (21), `__main__.py` (4), `__init__.py`.

**Biểu tượng công khai**: `main`, `build_parser`, `run_all`, `run_stage`, `process_inbox`, `BatchResult`,
`generate`, `ManifestStore`, `upsert`, `STAGES`, `TABLE_KEYS`.

**Phụ thuộc**: hầu hết các gói `src.*` (điểm ghép nối trung tâm), gồm `src.analytics.{model,report,service,
statistics}` và `src.linkage`.

**Được dùng bởi**: `python -m src.pipeline`, test.

**Ghi chú**:
- `STAGES` có **5** tên (`ingest`, `clean`, `integrate`, `analyze`, `stats`) nhưng `_run_all` ghi **6**
  `StageResult` (thêm `quality`, `linkage`) và **không chạy `stats`** — danh sách tầng và báo cáo tầng mô tả
  hai thứ khác nhau (TD-11).
- Nhánh `stats` là chỗ **duy nhất** ghi `analysis.json`, và nó làm đúng thứ tự: dựng khối `stats` → huấn luyện
  → `replace(model=...)` → `write_report`.
- `process_inbox` sao toàn bộ `data/cleaned` vào temp cho mỗi batch; đánh `success` cho **tệp** trước khi
  `QualityGate` chạy (TD-01).
- `cli.py` khai cứng 3 lệnh con; không có lệnh con cho thống kê/mô hình.

## tests

**Trách nhiệm**: bộ kiểm thử ba tầng — unit (DataFrame nhỏ / DuckDB tạm, fixture trong `conftest.py`), tích
hợp end-to-end trên dữ liệu thật (đánh dấu `slow`), và baseline dữ liệu (khẳng định các hằng số dị thường).

**Tệp**: `conftest.py` (361) + `unit/` **43** mô-đun `test_*.py` + `integration/` **5** mô-đun +
`data_quality/` **1** mô-đun = 54 tệp, 10.086 dòng, **499** hàm test (**12** hàm `slow`).

**Biểu tượng công khai**: fixture `config`, `real_config`, `run`, `writer`, `logger`, `small_*`,
`region_map`, `small_cleaned`.

**Phụ thuộc**: `pytest`, `pandas`, `duckdb` (dựng view tạm trong test), `scikit-learn` (import trực tiếp để
kiểm `LogisticRegression`), toàn bộ `src.*`, ba hợp đồng YAML trong `config/`,
`dataset/external/ibge/estados.json`.

**Được dùng bởi**: `pytest` theo `pytest.ini`; CI chạy bộ nhanh rồi bộ đầy đủ với ngưỡng phủ 80%.

**Ghi chú**: vùng quét sâu lần này xác nhận **số lượng cứng** đang bị khẳng định: **5 tab**
(`test_dashboard_smoke.py:57`, `test_u3_end_to_end.py:87`), **9 callback**
(`test_dashboard_smoke.py:62`, `test_u3_end_to_end.py:83`), **9 output** (`test_dashboard_smoke.py:115`),
**6** callback riêng của tab Tích hợp (`test_integration_tab.py:938`), **3** lệnh con CLI
(`test_pipeline_stages.py:157-161`), **11** view (`test_u2_end_to_end.py:44`), **5** tên tầng
(`test_pipeline_stages.py:134-135`), **11** đặc trưng (`test_analytics_model.py:193-199`), **10** cột cấm
(`:200-207`), **19** điểm ngưỡng (`:343-347`), **7** trường khối mô hình (`:497-515`).
Mọi mô-đun mới của đợt này đều có test riêng (kể cả `test_ci_config.py` cho `ci.yml`), trừ phần còn thiếu
đã ghi ở `code-quality-assessment.md` §3.2.

## docs

**Trách nhiệm**: tài liệu cho người đọc — từ điển dữ liệu star schema (`data-dictionary.md`), runbook xử lý
sự cố (`runbook.md`), và luận điểm 3V (`3v.md`).

**Tệp**: `data-dictionary.md` (134 dòng, đọc toàn văn lần này), `runbook.md`, `3v.md`.

**Được dùng bởi**: con người; không có mã nào đọc các tệp này.

**Ghi chú**: `data-dictionary.md` mô tả **11 bảng mart** (5 dim, 4 fact, 2 agg) với grain và cột; **không**
mô tả `v_*`, **không** mô tả `data/reports/analysis.json`, và `fact_orders` trong tài liệu cũng không có mốc
`order_delivered_carrier_date` — khớp mã, lệch với nhu cầu của khung dự đoán mới. `README.md` nhắc
`aidlc-docs/` nhưng thư mục này **không tồn tại** (tham chiếu chết sau khi gỡ AI-DLC v1).

## assets

**Trách nhiệm**: một tệp CSS cung cấp token thiết kế (biến CSS), lưới biểu đồ, kiểu KPI card, bảng dữ liệu,
banner lỗi, và các khối riêng của tab phân tích (`.analysis-tab`, `.integration-figures`,
`.integration-skipped`).

**Tệp**: `assets/style.css` (1.200+ dòng; lần này chỉ đọc các khối liên quan tới tab phân tích).

**Được dùng bởi**: `Dash(assets_folder=str(config.workspace_root / "assets"))` trong `src/dashboard/app.py:423`;
test đọc tệp trực tiếp để kiểm "mọi lớp phải được định nghĩa" và "tương phản WCAG AA".

**Ghi chú**: đường dẫn assets tính từ `workspace_root` (thư mục chứa `config.yaml`), không phải từ gói
`src.dashboard` — chạy dashboard từ thư mục khác vẫn đúng miễn `config.yaml` được tìm thấy. Thêm một lớp CSS
mới cho tab là phải thêm vào **cùng** thay đổi với tab, nếu không `test_every_class_is_defined_in_the_stylesheet`
đỏ.

## config

**Trách nhiệm**: ba hợp đồng YAML là **phụ thuộc cứng của runtime**: `mediated-schema.yaml` (lược đồ trung
gian), `integration-tab.yaml` (id thẻ/vùng/callback của tab Tích hợp), `integration-sources.yaml` (hồ sơ nguồn).

**Tệp**: 3 YAML.

**Được dùng bởi**: `src.integration.schema`/`card`/`selector`, `src.dashboard.app` (`_tab_config`), CI (bước
smoke nạp `integration-sources.yaml`), và `tests/conftest.py` (trỏ tuyệt đối vào tệp thật).

**Ghi chú**: thiếu/hỏng `integration-tab.yaml` → dashboard rơi về 4 thẻ mặc định (`_tab_config`);
thiếu `mediated-schema.yaml`/`integration-sources.yaml` → tab "Tích hợp" báo lỗi từng thẻ. Không có trường
phiên bản lược đồ, nên đổi cấu trúc YAML là breaking change ngầm (TD-08 mở rộng).
