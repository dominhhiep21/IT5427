# Cấu trúc mã nguồn — Olist E-commerce Data Pipeline

> Đây là artifact sở hữu danh mục tệp và cách phân loại; `component-inventory.md` chỉ
> tổng hợp theo thành phần và trỏ về đây. **Số dòng đã được đo lại trên đĩa** ngày 2026-11-11 tại commit
> `ea77bdf88d1431de11c36e1b739972bd594063f0` (cây làm việc có thay đổi chưa commit); phần phân tích sâu
> áp cho `src/analytics/`, `src/integrate/`, `src/dashboard/`, `src/pipeline/`, `tests/` — các tệp khác giữ
> mô tả từ lần quét trước (chưa đọc lại).

## 1. Bố cục gói

```
<repo>/
├── config.yaml                 paths, parquet, geolocation bbox, quality (memory), duckdb, ibge, micro_batch, dashboard
├── config/                     hợp đồng YAML: mediated-schema.yaml, integration-tab.yaml, integration-sources.yaml
├── requirements.txt            12 phụ thuộc ghim phiên bản (thêm scipy, scikit-learn ở đợt này)
├── pytest.ini                  testpaths = tests; marker slow; addopts = -ra
├── ruff.toml                   lint + format: line-length 112, target py313, select E4/E7/E9/F
├── README.md                   kiến trúc, lệnh chạy, KPI baseline, dashboard 5 tab, CI có bước stats
├── CHANGELOG.md                bốn mốc v0.1.0 → v0.4.0 (v0.2.0 stats, v0.3.0 model, v0.4.0 tab phân tích)
├── AGENTS.md                   trạng thái repo + quy ước làm việc dữ liệu
├── .github/workflows/ci.yml    CI windows-2022: lint → run all → run stats → test nhanh → phủ 80% → smoke
├── src/
│   ├── __init__.py
│   ├── config.py                AppConfig (frozen, 34 trường), load_config
│   ├── common/                  exceptions, io, logging (+prune_logs), memory, types, kpis
│   ├── ingest/                  schemas, reader, reports
│   ├── clean/                   common, orders, customers, sellers, products, items, payments, reviews, geolocation, pipeline
│   ├── quality/                 checks, gate, allowlist
│   ├── external/                ibge, region
│   ├── integrate/               dimensions, facts, aggregates, validate, reconcile, catalog, connections, pipeline
│   ├── integration/             models, schema, load, rewrite, query, selector, card, tab
│   ├── linkage/                 models, index, score, result
│   ├── analytics/               service, statistics, model, report, filters        ← 3 tệp mới ở đợt này
│   ├── dashboard/               app, analysis_tab, components, formatting, __main__  ← 1 tệp mới
│   └── pipeline/                cli, stages, micro_batch, manifest, upsert, replay, __main__
├── tests/
│   ├── conftest.py              361 dòng fixture dùng chung
│   ├── unit/                    43 mô-đun test nhanh
│   ├── integration/             5 test end-to-end (đánh dấu slow, dùng dữ liệu thật)
│   └── data_quality/            1 mô-đun baseline trên CSV thật (slow)
├── assets/style.css            CSS chủ đề (chỉ đọc các khối .analysis-tab / .integration-*)
├── docs/                       data-dictionary.md, runbook.md, 3v.md
├── dataset/                    9 CSV gốc + external/ibge/{estados,metadata}.json
├── data/ raw|cleaned|marts|reports|integration|.tmp   (sinh ra, bị .gitignore)
├── warehouse/olist.duckdb      (sinh ra, bị .gitignore)
├── logs/<run_id>.jsonl         (sinh ra, bị .gitignore; giữ 10 tệp gần nhất)
├── inbox/                      (sinh ra/đầu vào micro-batch, bị .gitignore)
└── doc/                        học liệu PDF + quiz (không thuộc mã ứng dụng)
```

Tổng: **74 tệp Python** trong `src/` (**11.333** dòng), **54 tệp test** trong `tests/` (**49** mô-đun
`test_*` với **499** hàm test, **12** hàm `slow`, **10.086** dòng), 1 tệp CSS. Không có `pyproject.toml`,
`setup.py`, `Makefile`, lock file.

Quy mô theo gói (số tệp / số dòng): `src.integration` 9/4.138 · `src.analytics` 6/**1.578** ·
`src.dashboard` 6/**1.322** · `src.integrate` 9/793 · `src.linkage` 5/784 · `src.pipeline` 8/668 ·
`src.common` 7/551 · `src.quality` 4/440 · `src.clean` 11/437 · `src.ingest` 4/285 · `src.external` 3/177 ·
`src/config.py` 157 · `src/__init__.py` 3.

## 2. Phân loại tệp nguồn

### 2.1 Vùng quét sâu lần này — `src/analytics/`

| Tệp | Loại | Dòng | Vai trò |
|---|---|---:|---|
| `src/analytics/service.py` | Repository/DAO | 387 | `AnalyticsService`: **9** phương thức chỉ đọc trên view DuckDB; `_where` dựng mệnh đề từ `KpiFilters`; 4 hằng SQL cấp mô-đun; `MAX_CORRELATION_ROWS = 200_000` |
| `src/analytics/statistics.py` | Service/UseCase | 313 | Năm phép kiểm định (`wilson_interval`, `late_rate`, `compare_states`, `price_freight_correlation`, `region_late_test`, `seasonal_decomposition`), `ordered_skips`, `collect_stats`, `build_analysis_report` |
| `src/analytics/model.py` | Service/UseCase | 368 | `FEATURES`/`FORBIDDEN_COLUMNS`/`ModelError`; `validate_features`, `delivered_population`, `build_feature_frame`, `split_frame`, `split_summary`, `encode_features`, `build_estimator`, `train_classifier`, `choose_threshold`, `auc_below_target`, `validate_counts`, `build_model_block`, `train_from_frame`, `train_model` |
| `src/analytics/report.py` | Model/Entity | 502 | Khung báo cáo phiên bản 2: 12 dataclass (`SkipEntry`, `ProportionResult`, `ComparisonResult`, `CorrelationResult`, `GroupTestResult`, `SeasonalResult`, `StatsBlock`, `ModelBlock`, `AnalysisReport`, `ReportView`, `ThresholdPoint` ở model.py), `report_path`, `write_report`, `read_report`, bộ parser `_parse_report` |
| `src/analytics/filters.py` | Utility/Helper | 7 | Shim re-export `KpiFilters` (`__all__`) |
| `src/analytics/__init__.py` | Configuration | 1 | Gói rỗng |

### 2.2 Vùng quét sâu lần này — `src/integrate/`

| Tệp | Loại | Dòng | Vai trò |
|---|---|---:|---|
| `src/integrate/facts.py` | Service/UseCase | 162 | `FactBuilder`: `build_order_items` (12 cột, có `seller_id`, **rơi** `shipping_limit_date`), `build_orders` (**13 cột**, `is_late`/`delivery_days`/`has_*`), `_dominant_category`, `build_payments`, `build_reviews` |
| `src/integrate/validate.py` | Service/UseCase | 147 | `StarSchemaValidator.EXPECTED` (9 số dòng), 9 check unique, `R-01` region null, `J-01` join không nở, `L-01` `is_late` chỉ cho đơn đã giao |
| `src/integrate/pipeline.py` | Service/UseCase | 128 | `integrate_all`, `load_cleaned`, `CLEANED_TABLES`, `IntegrationResult`; dòng 10 import thừa `AnalyticsService` |
| `src/integrate/dimensions.py` | Service/UseCase | 118 | `DimensionBuilder.build_customer/product/seller/geography/date` |
| `src/integrate/aggregates.py` | Service/UseCase | 87 | `Aggregator.build_sales`/`build_delivery` (chỉ đơn `delivered`) |
| `src/integrate/reconcile.py` | Service/UseCase | 66 | `KpiReconciler` (`BASELINE` 5 KPI, `TOLERANCE` 5 dung sai) |
| `src/integrate/catalog.py` | Repository/DAO | 54 | `VIEW_TABLES` **11** bảng, `DuckDbCatalog.create`, `list_views` |
| `src/integrate/connections.py` | Repository/DAO | 30 | `ConnectionFactory.write`/`read_only`, PRAGMA memory/threads; `read_only` nuốt lỗi PRAGMA |
| `src/integrate/__init__.py` | Configuration | 1 | Gói rỗng |

### 2.3 Vùng quét sâu lần này — `src/dashboard/`

| Tệp | Loại | Dòng | Vai trò |
|---|---|---:|---|
| `src/dashboard/app.py` | Controller/Handler | 589 | `build_layout` (**5 tab**), `create_app` (2 callback báo cáo + gọi 6 + 1 callback của hai tab kia), `build_dashboard_outputs` (**9** output, hai nhánh), `_tab_config`, `_integration_logger`, `reset_integration_logs`, `_options`, `_line_chart`/`_bar_chart`/`_table` |
| `src/dashboard/analysis_tab.py` | Controller/Handler | 566 | `TAB_VALUE="phan-tich"`, `SECTION_IDS` (`tom-tat|thong-ke|mo-hinh`), `CARD_IDS` (4 thẻ), `ResultTabState`, `SummaryCard`, `state_for`, `StateBanner`, `summary_cards`, `build_stats_items`, `build_model_section`, `sections_for`, `AnalysisPanel`, `AnalysisTab`, `render_analysis`, `register_callback` |
| `src/dashboard/components.py` | Static/Asset | 111 | `kpi_card`, `kpi_strip`, `chart_card`, `empty_figure`, `error_banner` (nút "Thử lại" **không** có callback), `sparse_badge` |
| `src/dashboard/formatting.py` | Utility/Helper | 39 | Định dạng số kiểu Brazil, BRL, `format_percent` (**không** nhân 100), ngày `dd/mm/yyyy` |
| `src/dashboard/__main__.py` | Configuration | 16 | Điểm vào `python -m src.dashboard` |
| `src/dashboard/__init__.py` | Configuration | 1 | Gói rỗng |

### 2.4 Vùng quét sâu lần này — `src/pipeline/`

| Tệp | Loại | Dòng | Vai trò |
|---|---|---:|---|
| `src/pipeline/stages.py` | Service/UseCase | 274 | `STAGES` **5** tên; `_run_all` (6 `StageResult`, **không** chạy `stats`); nhánh `stats` (dựng báo cáo → `train_model` → `replace` → `write_report`); `run_all`, `run_stage`, `_run_linkage`, `_load_raw`/`_load_cleaned`, `_write_summary` |
| `src/pipeline/micro_batch.py` | Service/UseCase | 188 | `process_inbox`, `TABLE_KEYS`, `BatchResult`, `_clean_batch_table`; đánh `success` cho tệp **trước** khi gate chạy |
| `src/pipeline/cli.py` | Controller/Handler | 79 | `build_parser` (**3** lệnh con; `--stage` nhận **6** giá trị), `main` in tóm tắt, mã thoát 0/1 |
| `src/pipeline/replay.py` | Service/UseCase | 54 | `generate` cắt batch theo tháng từ cleaned |
| `src/pipeline/manifest.py` | Repository/DAO | 47 | `ManifestStore.load/save/has_success/record` |
| `src/pipeline/upsert.py` | Utility/Helper | 21 | `upsert(existing, new, keys)` theo khóa tự nhiên |
| `src/pipeline/__main__.py` | Configuration | 4 | Điểm vào `python -m src.pipeline` |
| `src/pipeline/__init__.py` | Configuration | 1 | Gói rỗng |

### 2.5 Vùng quét sâu lần này — `tests/`

| Tệp | Loại | Dòng | Vai trò |
|---|---|---:|---|
| `tests/conftest.py` | Test | 361 | 12 fixture: `config` (tmp_path), `real_config` (dataset thật), `run`, `writer`, `logger`, 9 `small_*`, `region_map`, `small_cleaned` |
| `tests/unit/test_analytics_model.py` | Test | 646 | 40+ ca cho `model.py` + 5 ca cho `TRAINING_FRAME_SQL` trên DuckDB tạm; có ca khẳng định SQL chỉ chạm `VIEW_TABLES` |
| `tests/unit/test_dashboard_analysis_tab.py` | Test | 627 | 39 ca: trạng thái, thứ tự khối, bốn thẻ, khối thống kê/mô hình, a11y, "mọi lớp CSS phải có trong stylesheet", callback đọc tệp đúng một lần |
| `tests/unit/test_analytics_statistics.py` | Test | 429 | Năm phép kiểm định + ba phương thức đọc mới của service |
| `tests/unit/test_analytics_report.py` | Test | 283 | Ghi/đọc báo cáo, bốn trạng thái, từ chối sai phiên bản/thiếu trường |
| `tests/unit/test_pipeline_stages.py` | Test | 261 | `STAGES` 5 tên, `choices` của CLI khớp `STAGES|{"all"}`, 3 lệnh con, tầng `stats` chạy thật trên mart 730 dòng dựng bằng SQL |
| `tests/unit/test_dashboard_smoke.py` | Test | 176 | 5 tab, 9 callback, 9 output, 4 thẻ tab Tích hợp, pattern-matching id (5 test chạm `load_config()` thật) |
| `tests/unit/test_ci_config.py` | Test | 108 | Đọc `ci.yml` bằng YAML: 3 nhánh, danh sách `ruff format --check` phủ 14 tệp mới, thứ tự all→stats→test, cổng 80% không bị hạ, `scikit-learn==1.6.1` được ghim |
| `tests/unit/test_analysis_tab_contrast.py` | Test | 66 | Tương phản WCAG AA của token, `.analysis-tab` không dùng `--text-3` |
| `tests/unit/test_cli.py` | Test | 21 | 2 ca parser + 1 ca chạy thật `--stage analyze` (**không** còn khẳng định 3 lệnh con — đã chuyển sang `test_pipeline_stages.py:157-161`) |
| `tests/integration/test_u1_stats_end_to_end.py` | Test (slow) | 130 | Tầng `stats` trên dữ liệu thật: 5 phép, `correlation.n == 110_197`, ngân sách 300 s, bộ nhớ, hai lần chạy cho cùng tệp |
| `tests/integration/test_u2_model_end_to_end.py` | Test (slow) | 95 | Bước mô hình: baseline 96.478/7.826, 11 đặc trưng, cắt tại `2018-04-01`, 4 số đã làm tròn, ngân sách 900 s, tính lặp lại |
| `tests/integration/test_u3_end_to_end.py` | Test (slow) | 120 | Micro-batch, KPI, hình dạng dashboard (**9 callback, 5 tab**), và `test_u3_analysis_tab_renders_the_real_report` đọc báo cáo thật (AUC 0,5133) |
| `tests/integration/{test_u1,test_u2}_end_to_end.py` | Test (slow) | 72 / 99 | Pipeline thật: 9 báo cáo, số dòng cleaned, 9 số dòng mart, 11 view, 5 KPI |

### 2.6 Vùng giữ nguyên từ lần quét trước (số dòng đã đo lại, phân tích chưa xác minh lại)

| Tệp | Loại | Dòng | Vai trò |
|---|---|---:|---|
| `src/config.py` | Configuration | 157 | `AppConfig` frozen dataclass (34 trường); `load_config` đọc YAML, tạo thư mục |
| `src/common/types.py` | Model/Entity | 139 | 14 dataclass: `TableSpec`, `RunContext`, các báo cáo, `KpiFilters`, `IbgeMetadata` |
| `src/common/kpis.py` | Model/Entity | 108 | Sổ KPI: 3 mẫu truy vấn + dòng đếm, `REVENUE_DEFINITION`, `validate_ledger`, `kpi` |
| `src/common/logging.py` | Utility/Helper | 119 | `new_run_context`, `JsonLogger`, `NullLogger`, `prune_logs` |
| `src/common/io.py` | Utility/Helper | 88 | `sha256_file`, `validate_columns`, `read_csv`, `read_parquet`, `AtomicWriter` |
| `src/common/exceptions.py` | Model/Entity | 66 | `PipelineError` + các ngoại lệ con (schema, quality, config, external, query, KPI mismatch, no-source, linkage) |
| `src/common/memory.py` | Utility/Helper | 30 | `MemoryProbe` — **nay có người dùng**: `tests/integration/test_u1_stats_end_to_end.py` |
| `src/ingest/schemas.py` | Model/Entity | 132 | `TABLE_SPECS`: 9 hợp đồng cột/khóa/số dòng kỳ vọng |
| `src/ingest/reader.py` | Service/UseCase | 75 | `ingest_table`, `ingest_all` |
| `src/ingest/reports.py` | Repository/DAO | 77 | `ReportWriter` (4 báo cáo), `reconcile_payments` |
| `src/clean/common.py` | Utility/Helper | 58 | `normalize_text`, `normalize_state`, ép kiểu, `iqr_bounds`, đếm null/flag |
| `src/clean/pipeline.py` | Service/UseCase | 91 | `clean_all` điều phối 9 bảng |
| `src/clean/geolocation.py` | Service/UseCase | 119 | Lọc bbox, khử trùng lặp, trung vị lat/lng, mode city/state |
| `src/clean/products.py` | Service/UseCase | 55 | Ép số, `unknown` cho danh mục thiếu, left join bảng dịch |
| `src/clean/{orders,items,reviews,payments,customers,sellers}.py` | Service/UseCase | 29/21/17/16/15/15 | Làm sạch theo bảng (`clean_orders` giữ đủ 5 mốc thời gian, gồm `order_delivered_carrier_date`) |
| `src/quality/gate.py` | Service/UseCase | 304 | `QualityGate.run` (21 check + 9 count + 10 anomaly khi `full`), `enforce` |
| `src/quality/checks.py` | Utility/Helper | 121 | 6 kiểm tra tái dùng |
| `src/quality/allowlist.py` | Configuration | 14 | `EXPECTED_ANOMALIES`: 10 bộ đếm dị thường |
| `src/external/ibge.py` | Repository/DAO | 131 | `IbgeClient`: cache, `urllib`, retry, fallback, metadata SHA-256 |
| `src/external/region.py` | Service/UseCase | 45 | `RegionMapper.validate`/`attach` |
| `src/integration/models.py` | Model/Entity | 253 | Dataclass frozen của lớp tích hợp |
| `src/integration/schema.py` | Service/UseCase | 368 | `load_schema`, `build_field_catalogue`, `EntityMapping`/`FieldMapping` |
| `src/integration/load.py` | Repository/DAO | 240 | `load_don_hang`, `clean_rows`, `clear_cache` |
| `src/integration/rewrite.py` | Service/UseCase | 819 | `rewrite_plan`, chạy truy vấn đã viết lại, đối chiếu KPI |
| `src/integration/query.py` | Service/UseCase | 186 | `run_monthly_orders` |
| `src/integration/selector.py` | Service/UseCase | 543 | Hồ sơ nguồn, `select_source` |
| `src/integration/card.py` | Static/Asset | 348 | `TabConfig`, `load_tab_config`, 6 trạng thái thẻ, `render_integration_card`, `STATE_ICONS`, `TEXTS` |
| `src/integration/tab.py` | Controller/Handler | 1.380 | `IntegrationTab`, 4 thẻ, 4 màn hình chi tiết, `register_callbacks` (**6** callback, trong đó 1 sinh theo `result_region_ids`) |
| `src/linkage/{models,index,score,result}.py` | Model/Service | 217/186/231/149 | Ghép bản ghi theo hai đối tượng |

Không có thư mục **Migration** (không có cơ sở dữ liệu quan hệ có lược đồ di trú; DuckDB chỉ chứa view
được tạo lại mỗi lần chạy) và không có **Middleware** (không có HTTP API).

## 3. Mẫu thiết kế và quy ước

### 3.1 Mẫu lặp lại

- **Hàm làm sạch thuần theo bảng**: mỗi bảng nguồn một mô-đun, chữ ký `clean_<table>(df, ...) -> DataFrame`,
  luôn `out = df.copy()` trước khi sửa, thêm cột cờ thay vì lọc.
- **Builder không trạng thái**: `DimensionBuilder`, `FactBuilder`, `Aggregator`,
  `StarSchemaValidator`, `KpiReconciler`, `DuckDbCatalog` chỉ có `build_*`/`validate`/`reconcile`.
- **Mô-đun suy luận là tập hàm thuần trên `DataFrame`** (`statistics.py`, `model.py`): không mở kết nối,
  không đọc tệp, không giữ trạng thái; mọi I/O nằm ở `service.py` (đọc DuckDB) và `report.py` (ghi/đọc tệp).
  `stages.py` là nơi duy nhất ghép ba mô-đun này.
- **Hằng số có tên thay vì literal rải rác**: `SPLIT_DATE`, `TARGET`, `AUC_TARGET`, `THRESHOLD_METHOD`,
  `THRESHOLD_GRID`, `EXPECTED_DELIVERED`, `EXPECTED_LATE`, `MODEL_DIGITS`, `RANDOM_STATE`, `MAX_ITER`,
  `REPORT_VERSION`, `RATE_DIGITS`/`P_VALUE_DIGITS`/`INTERVAL_DIGITS`/`STATISTIC_DIGITS`/`CORRELATION_DIGITS`,
  `STATUS_*` (bốn trạng thái), `SKIP_TESTS`, `MIN_STATE_ORDERS`, `MIN_CORRELATION_ROWS`,
  `MIN_EXPECTED_CELL`, `SEASONAL_PERIOD`, `MIN_SEASONAL_MONTHS`, `MAX_CORRELATION_ROWS`.
- **Tiêm phụ thuộc qua tham số `config`** (không dùng container DI); các lớp nhận `config` không có
  type hint/protocol, dựa vào thuộc tính của `AppConfig`.
- **Ghi tệp nguyên tử** qua `AtomicWriter` (temp trong `data/.tmp/<run_id>/`, đọc lại kiểm tra, `os.replace`);
  báo cáo phân tích có thêm bước **parse lại và kiểm cấu trúc** trước khi thay tệp.
- **Báo cáo = dataclass → JSON**: `ReportWriter` dùng `dataclasses.asdict`; `integrate_all` dùng `__dict__`;
  `report.py` dùng `to_dict()` tường minh cho từng dataclass (cách thứ ba, và là cách duy nhất kiểm soát
  được thứ tự/độ chính xác của số).
- **Nhật ký JSONL**: mỗi lần chạy một `run_id` dạng `<UTC>%Y%m%dT%H%M%S>-<8 hex>`, mọi sự kiện
  có `timestamp`, `level`, `run_id`, `stage`, `event` + trường tùy biến; `prune_logs` giữ 10 tệp gần nhất.
  Sự kiện mới của đợt này: `model.trained`, `stats_report_written`,
  `stats.previous_report_unreadable`.
- **Lỗi theo tầng**: `SchemaError`, `QualityGateError`, `ExternalSourceError`, `ConfigurationError`,
  `QueryExecutionError`, `KpiMismatchError`, `NoSourceAvailableError`, `LinkageResult*Error`, cộng hai lỗi
  mới cùng gốc `PipelineError`: **`ModelError`** (`model.py:73-74`) và **`ReportError`**
  (`report.py:35-36`). CLI bắt `Exception` ở biên và trả mã thoát 1.
- **SQL tham số hóa**: `AnalyticsService._where` ghép mệnh đề từ danh sách trắng các bộ lọc và truyền
  tham số qua `?`; danh sách cột/`GROUP BY` chọn từ dict hằng. Bốn hằng SQL mới là **chuỗi tĩnh** ở cấp
  mô-đun, chỉ nối thêm mệnh đề `_where` — không nối chuỗi từ đầu vào người dùng.
- **Hàm dựng giao diện là hàm thuần trả cây Dash** (`chart_card`, `kpi_strip`, `StateBlock`,
  `IntegrationCard`, `AnalysisPanel`, `_section`), được test bằng cách duyệt cây và đọc `props` chứ không
  mở trình duyệt.
- **`catch` ở biên, không ở giữa**: `cli.main`, `stages.run_stage`, `process_inbox`, `tab.py`,
  `analysis_tab.render_analysis` bắt và chuyển thành trạng thái/mã lỗi; các tầng trong ném tiếp.

### 3.2 Quy ước đặt tên

- Mô-đun và hàm `snake_case`, lớp `PascalCase`, hằng `UPPER_SNAKE`; tiền tố bảng đích (`dim_`, `fact_`, `agg_`).
- Cột cờ là mệnh đề khẳng định: `is_delivered`, `is_late`, `has_items`, `has_payment`, `has_review`,
  `category_missing`, `translation_missing`, `price_outlier`, `multiple_reviews_per_order`,
  `auc_below_target`, `is_sparse_period`.
- ID check chất lượng có tiền tố nhóm: `U-` unique, `F-` foreign key, `D-` miền giá trị, `R-` số dòng,
  `A-` dị thường, `C-` count star schema, `J-` join, `L-` logic.
- **ID nghiệp vụ trong chú thích mã** của đợt này dùng dạng `BR1.1`–`BR3.10` (thống kê/báo cáo),
  `TS-2`/`TS-6`…`TS-9` (kỹ thuật), `NFR1.x`/`NFR3.x`/`NFR4.2`/`NFR5.x`, `PD-1`/`PD-2`, `SEC-2`/`SEC-5`,
  `SD-1`/`SD-1b` — dẫn thẳng vào docstring và chú thích.
- Lớp tích hợp dùng **định danh tiếng Việt không dấu** cho thực thể/trường (`don_hang`, `ma_don`, `trang_thai`)
  và **id kebab-case tiếng Việt** cho thành phần giao diện (`tich-hop`, `luoc-do-trung-gian`, `don-theo-thang`,
  `phan-tich`, `tom-tat`, `thong-ke`, `mo-hinh`, `ti-le-tre`, `so-don`, `so-bo-qua`, `auc`).
- Trạng thái giao diện là token đóng: `rong`, `chua-chay`, `dang-tai`, `day-du`, `mot-phan`, `loi`.

### 3.3 Hướng phụ thuộc (thực tế)

```
config ─┐
common ─┼─→ ingest ─→ clean ─→ quality ─→ integrate ─→ analytics ─→ dashboard
        │                                    ↑              ↑  ↑
        └─→ external ─────────────────────────┘              │  │
        └─→ integration ──────────────────────────────────── │  │
        └─→ linkage ─────────────────────────────────────────┘  │
                                                                │
   analytics.service ─→ analytics.statistics ─┐                 │
   analytics.service ─→ analytics.model ──────┼─→ analytics.report
   pipeline.stages ─→ analytics.{statistics,model,report} ──────┘
pipeline (điều phối) ─→ ingest, clean, quality, integrate, analytics, linkage
```

- Trong gói `analytics`, hướng là `service ← statistics`, `service ← model`, `report ← statistics`,
  `report ← model` (report **không** import service/statistics/model → không có vòng).
  `model.py` import `report.ModelBlock`, `service.AnalyticsService`; `statistics.py` import `report` (11 tên),
  `service.AnalyticsService`, `common.kpis.REVENUE_DEFINITION`, `common.types.KpiFilters`.
- `dashboard.analysis_tab` import `analytics.report`/`model`/`statistics` (chỉ **đọc**),
  `dashboard.formatting`, và `integration.card` (dùng lại `STATE_ICONS`/`TEXTS`) — một phụ thuộc chéo
  giao diện↔giao diện mới, cần biết khi đổi `card.py`.
- Vi phạm đã phát hiện (một chiều bị đảo): `src/integrate/pipeline.py:10` import `AnalyticsService` nhưng
  không dùng — xem `code-quality-assessment.md` TD-06. Không có import vòng thực sự.

## 4. Điểm vào

| Điểm vào | Lệnh | Ghi chú |
|---|---|---|
| Pipeline | `python -m src.pipeline run --stage all\|ingest\|clean\|integrate\|analyze\|stats [--refresh-ibge]` | `src/pipeline/__main__.py` → `cli.main`; `all` **không** gồm `stats` |
| Micro-batch | `python -m src.pipeline micro-batch [--inbox <dir>]` | Mặc định `config.inbox_dir` |
| Replay | `python -m src.pipeline replay --batches N` | Tạo batch trong `inbox/replay/` rồi xử lý |
| Dashboard | `python -m src.dashboard` | `app.run(host, port, debug=False)` |
| Test | `python -m pytest [-m "not slow"] [--cov=src --cov-fail-under=80]` | `pytest.ini` giới hạn `testpaths = tests` |
| CI | đẩy nhánh `main` / `feature/update-ui-ux` / `feature/analysis-and-models` | `.github/workflows/ci.yml` |

Mọi lệnh Python phải chạy UTF-8 (`-X utf8` hoặc `PYTHONUTF8=1`) do đường dẫn có ký tự tiếng Việt
và dữ liệu Bồ Đào Nha (`README.md`, `docs/runbook.md`, `AGENTS.md`).

## 5. Ghi chú biên

- **Vẫn không có lệnh CLI con nào cho thống kê/mô hình**: `build_parser` chỉ có `run`, `micro-batch`,
  `replay`; việc thống kê là **tầng thứ năm** của `run --stage` (`stats`), đúng như quyết định Q5 = B của đợt
  trước. Ba lệnh con được khẳng định ở `tests/unit/test_pipeline_stages.py:157-161`.
- **`--stage all` không chạy `stats`**: `_run_all` (`stages.py:91-179`) chỉ chạy 6 mục
  ingest/clean/quality/integrate/linkage/analyze. Muốn có `analysis.json` phải gọi `--stage stats` (CI làm
  đúng vậy ở bước riêng).
- `python -m src.pipeline run --stage analyze` chỉ chạy `AnalyticsService.kpi_summary` như **smoke test**
  (`stages.py:235-240`) và ghi sự kiện `analyze_smoke`; không kiểm định gì thêm.
- `tests/unit/test_dashboard_smoke.py`, `tests/unit/test_cli.py::test_main_analyze_stage` gọi
  `load_config()` mặc định của repo → cần `warehouse/olist.duckdb` và `data/marts/` đã tồn tại.
  Đây là phụ thuộc ngầm của bộ test "nhanh" vào dữ liệu sinh ra (xem `code-quality-assessment.md` TD-09);
  CI xử lý bằng cách chạy `--stage all` (và `--stage stats`) trước khi test. **Ngược lại**, 5 mô-đun test
  mới của đợt này (`test_analytics_*`, `test_dashboard_analysis_tab`, `test_pipeline_stages`) dựng mart
  và tệp báo cáo trong `tmp_path` nên **không** phụ thuộc dữ liệu sinh ra — đây là mẫu nên noi theo.
- `src/config.py` tạo thư mục đầu ra ngay khi nạp cấu hình, kể cả khi chỉ chạy test — tác dụng phụ
  có chủ đích nhưng làm test không hoàn toàn cô lập.
- `tests/` nay **10.086 dòng**, gần bằng 0,89 lần toàn bộ `src/` (11.333 dòng); 7 mô-đun vượt 470 dòng
  (lớn nhất `test_integration_tab.py` 983). Chi phí bảo trì test đã lớn hơn chi phí bảo trì vài tầng mã.
- **`# noqa` là mẫu đã có tiền lệ, không phải ngoại lệ mới**: `src/dashboard/analysis_tab.py:556`
  (`# noqa: BLE001`) và `:565` (`# noqa: ANN001`), cộng 7 chỗ có từ đợt trước
  (`src/integration/tab.py:1295,1325,1335,1350,1361,1375`, `card.py:333`, `rewrite.py:750`). Các mã này
  **không** nằm trong `select` của `ruff.toml` nên hiện là ghi chú không tác dụng; nếu sau này bật thêm luật
  thì chúng thành ngoại lệ thật.
- **`TODO`/`FIXME`/`HACK` trong `src/`: 0 lần** (đếm lại trên toàn `src/`), khớp quy ước "không mang ghi chú
  nợ dang dở trong mã".
