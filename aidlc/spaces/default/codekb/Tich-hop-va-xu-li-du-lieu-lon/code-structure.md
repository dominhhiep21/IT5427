# Cấu trúc mã nguồn — Olist E-commerce Data Pipeline

> Đây là artifact sở hữu danh mục tệp và cách phân loại; `component-inventory.md` chỉ
> tổng hợp theo thành phần và trỏ về đây. Số dòng là số dòng vật lý của tệp tại commit
> `41c422ffd7f3b27a2f78a67eaccc43a00d13c77e`.

## 1. Bố cục gói

```
<repo>/
├── config.yaml                 cấu hình đường dẫn, parquet, geo bbox, quality, duckdb, ibge, micro_batch, dashboard
├── requirements.txt            8 phụ thuộc ghim phiên bản
├── pytest.ini                  testpaths = tests; marker slow; addopts = -ra
├── README.md                   kiến trúc, lệnh chạy, KPI baseline, lưu ý vận hành
├── AGENTS.md                   trạng thái repo + quy ước làm việc dữ liệu
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── common/                 exceptions, io, logging, memory, types
│   ├── ingest/                 schemas, reader, reports
│   ├── clean/                  common, orders, customers, sellers, products, items, payments, reviews, geolocation, pipeline
│   ├── quality/                checks, gate, allowlist
│   ├── external/               ibge, region
│   ├── integrate/              dimensions, facts, aggregates, validate, reconcile, catalog, connections, pipeline
│   ├── analytics/              service, filters
│   ├── dashboard/              app, components, formatting, __main__
│   └── pipeline/               cli, stages, micro_batch, manifest, upsert, replay, __main__
├── tests/
│   ├── conftest.py             320 dòng fixture dùng chung
│   ├── unit/                   21 mô-đun test nhanh
│   ├── integration/            3 test end-to-end (đánh dấu slow, dùng dữ liệu thật)
│   └── data_quality/           1 mô-đun baseline trên CSV thật (slow)
├── assets/style.css            277 dòng CSS chủ đề (biến CSS, lưới biểu đồ)
├── docs/                       data-dictionary.md, runbook.md, 3v.md
├── dataset/                    9 CSV gốc + external/ibge/{estados,metadata}.json
├── data/ raw|cleaned|marts|reports|.tmp   (sinh ra, bị .gitignore)
├── warehouse/olist.duckdb      (sinh ra, bị .gitignore)
├── logs/<run_id>.jsonl         (sinh ra, bị .gitignore)
├── inbox/                      (sinh ra/đầu vào micro-batch, bị .gitignore)
└── doc/                        học liệu PDF + quiz (không thuộc mã ứng dụng)
```

Tổng: **55 tệp Python** trong `src/` (~4.200 dòng), **25 mô-đun test** với **47 hàm test**
(6 hàm đánh dấu `slow`), 1 tệp CSS. Không có `pyproject.toml`, `setup.py`, CI, Makefile.

## 2. Phân loại tệp nguồn

| Tệp | Loại | Dòng | Vai trò |
|---|---|---:|---|
| `src/config.py` | Configuration | 143 | `AppConfig` frozen dataclass; `load_config` đọc YAML, tạo thư mục |
| `src/common/types.py` | Model/Entity | 139 | 14 dataclass: `TableSpec`, `RunContext`, các báo cáo, `KpiFilters`, `IbgeMetadata` |
| `src/common/exceptions.py` | Model/Entity | 23 | Gốc `PipelineError` + `SchemaError`, `QualityGateError`, `ConfigurationError`, `ExternalSourceError` |
| `src/common/io.py` | Utility/Helper | 88 | `sha256_file`, `validate_columns`, `read_csv`, `read_parquet`, `AtomicWriter` |
| `src/common/logging.py` | Utility/Helper | 66 | `new_run_context` (run_id, temp dir, log path), `JsonLogger` (JSONL + console) |
| `src/common/memory.py` | Utility/Helper | 30 | `MemoryProbe` dùng `tracemalloc` — **không được tham chiếu ở đâu** |
| `src/ingest/schemas.py` | Model/Entity | 132 | `TABLE_SPECS`: 9 hợp đồng cột/khóa/số dòng kỳ vọng |
| `src/ingest/reader.py` | Service/UseCase | 75 | `ingest_table`, `ingest_all`: đọc, băm, ghi raw, tổng hợp báo cáo |
| `src/ingest/reports.py` | Repository/DAO | 77 | `ReportWriter` ghi 4 báo cáo JSON; `reconcile_payments` đối chiếu item vs payment |
| `src/clean/common.py` | Utility/Helper | 58 | `normalize_text` (NFC/trim/gộp khoảng trắng/lower), `normalize_state`, ép kiểu, `iqr_bounds`, đếm null/flag |
| `src/clean/orders.py` | Service/UseCase | 29 | Parse 5 cột thời gian, cờ `has_invalid_timestamp`, `is_delivered` |
| `src/clean/customers.py` | Service/UseCase | 15 | Chuẩn hóa city/state, zip → Int64 |
| `src/clean/sellers.py` | Service/UseCase | 15 | Như customers cho người bán |
| `src/clean/products.py` | Service/UseCase | 55 | Ép số, gán `unknown` cho danh mục thiếu, left join bảng dịch, cờ `translation_missing` |
| `src/clean/items.py` | Service/UseCase | 21 | Ép kiểu + cờ `price_outlier` theo IQR |
| `src/clean/payments.py` | Service/UseCase | 16 | Ép kiểu thanh toán |
| `src/clean/reviews.py` | Service/UseCase | 17 | Parse ngày + cờ `multiple_reviews_per_order` |
| `src/clean/geolocation.py` | Service/UseCase | 119 | Lọc bbox, khử trùng lặp, trung vị lat/lng, mode city/state, đếm biến thể thành phố |
| `src/clean/pipeline.py` | Service/UseCase | 91 | `clean_all` điều phối 9 bảng, ghi cleaned, dựng `CleaningReport` |
| `src/quality/checks.py` | Utility/Helper | 121 | 6 kiểm tra tái dùng: unique, foreign key, row count, between, min, allowed values |
| `src/quality/gate.py` | Service/UseCase | 304 | `QualityGate.run` (21 check + 9 count + 10 anomaly khi `full`), `enforce` |
| `src/quality/allowlist.py` | Configuration | 14 | `EXPECTED_ANOMALIES`: 10 bộ đếm dị thường được chấp nhận |
| `src/external/ibge.py` | Repository/DAO | 131 | `IbgeClient`: cache `estados.json`, gọi API bằng `urllib`, retry, fallback cache, metadata SHA-256 |
| `src/external/region.py` | Service/UseCase | 45 | `RegionMapper.validate` (27 bang, 5 vùng), `attach` (map state → region) |
| `src/integrate/dimensions.py` | Service/UseCase | 118 | `DimensionBuilder`: dim_customer/product/seller/geography/date |
| `src/integrate/facts.py` | Service/UseCase | 162 | `FactBuilder`: fact_order_items/orders/payments/reviews; category đại diện theo doanh thu |
| `src/integrate/aggregates.py` | Service/UseCase | 87 | `Aggregator`: agg_sales_daily, agg_delivery_daily (grain ngày × bang × vùng × danh mục) |
| `src/integrate/validate.py` | Service/UseCase | 147 | `StarSchemaValidator`: 9 check số dòng + 9 check khóa + region not null + join không nở + `is_late` chỉ cho delivered |
| `src/integrate/reconcile.py` | Service/UseCase | 66 | `KpiReconciler`: 5 KPI so với baseline, dung sai riêng từng KPI |
| `src/integrate/catalog.py` | Repository/DAO | 54 | `DuckDbCatalog.create` tạo 11 view; `list_views` |
| `src/integrate/connections.py` | Repository/DAO | 30 | `ConnectionFactory` write/read_only + PRAGMA memory_limit/threads |
| `src/integrate/pipeline.py` | Service/UseCase | 128 | `integrate_all`: nạp cleaned, IBGE, dims, facts, agg, validate, reconcile, ghi mart, catalog |
| `src/analytics/service.py` | Service/UseCase | 281 | 5 truy vấn: `kpi_summary`, `revenue_by_period`, `revenue_by_dimension`, `top_entities`, `delivery_kpis` |
| `src/analytics/filters.py` | Utility/Helper | 7 | Re-export `KpiFilters` (shim) |
| `src/pipeline/cli.py` | Controller/Handler | 81 | `argparse` 3 lệnh con; in tóm tắt; mã thoát 0/1 |
| `src/pipeline/stages.py` | Service/UseCase | 234 | `run_all`, `run_stage`, `StageResult`, `RunSummary`; ghi `run-summary.json` |
| `src/pipeline/micro_batch.py` | Service/UseCase | 188 | `process_inbox`: hash, skip, upsert, gate incremental, promote, integrate |
| `src/pipeline/manifest.py` | Repository/DAO | 47 | `ManifestStore`: load/save nguyên tử, `has_success`, `record` theo `batch_id` |
| `src/pipeline/upsert.py` | Utility/Helper | 21 | Upsert theo khóa tự nhiên (loại dòng cũ cùng khóa, nối dòng mới, sắp xếp) |
| `src/pipeline/replay.py` | Service/UseCase | 54 | `generate`: cắt N tháng gần nhất từ cleaned thành CSV batch |
| `src/pipeline/__main__.py`, `src/dashboard/__main__.py` | Configuration | 4 / 16 | Điểm vào `python -m` |
| `src/dashboard/app.py` | Controller/Handler | 486 | Layout 3 tab, 2 callback, dựng figure/bar/table, chặn lỗi |
| `src/dashboard/components.py` | Static/Asset | 111 | `kpi_card`, `kpi_strip`, `chart_card`, `empty_figure`, `error_banner`, `sparse_badge` |
| `src/dashboard/formatting.py` | Utility/Helper | 39 | Định dạng số kiểu Brazil (`1.234,56`), BRL, %, ngày `dd/mm/yyyy` |
| `tests/**` | Test | ~1.050 | 25 mô-đun test, fixture DataFrame nhỏ + `real_config` |

Không có thư mục **Migration** (không có cơ sở dữ liệu quan hệ có lược đồ di trú; DuckDB chỉ chứa view
được tạo lại mỗi lần chạy) và không có **Middleware** (không có HTTP API).

## 3. Mẫu thiết kế và quy ước

### 3.1 Mẫu lặp lại

- **Hàm làm sạch thuần theo bảng**: mỗi bảng nguồn một mô-đun, chữ ký `clean_<table>(df, ...) -> DataFrame`,
  luôn `out = df.copy()` trước khi sửa (tránh biến đổi đối số), thêm cột cờ thay vì lọc.
- **Builder có trạng thái tối thiểu**: `DimensionBuilder`, `FactBuilder`, `Aggregator`,
  `StarSchemaValidator`, `KpiReconciler`, `DuckDbCatalog` không giữ dữ liệu, chỉ có `build_all`/`validate`.
- **Tiêm phụ thuộc qua tham số `config`** (không dùng container DI); các lớp nhận `config` không có
  type hint/protocol, dựa vào thuộc tính của `AppConfig`.
- **Ghi tệp nguyên tử** qua `AtomicWriter` (temp trong `data/.tmp/<run_id>/`, đọc lại kiểm tra, `os.replace`).
- **Báo cáo = dataclass → JSON**: `ReportWriter` dùng `dataclasses.asdict`; `integrate_all` dùng `__dict__`
  (hai cách tuần tự hóa khác nhau trong cùng hệ thống).
- **Nhật ký JSONL**: mỗi lần chạy một `run_id` dạng `<UTC>%Y%m%dT%H%M%S>-<8 hex>`, mọi sự kiện
  có `timestamp`, `level`, `run_id`, `stage`, `event` + trường tùy biến.
- **Lỗi theo tầng**: ném `SchemaError` (đầu vào), `QualityGateError` (chất lượng), `ExternalSourceError`
  (nguồn ngoài), `ConfigurationError` (cấu hình); CLI bắt `Exception` ở biên và trả mã thoát 1.
- **SQL tham số hóa**: `AnalyticsService._where` ghép mệnh đề từ danh sách trắng các bộ lọc và truyền
  tham số qua `?`; danh sách cột/`GROUP BY` chọn từ dict hằng, không nối chuỗi từ đầu vào người dùng.

### 3.2 Quy ước đặt tên

- Mô-đun và hàm `snake_case`, lớp `PascalCase`, hằng `UPPER_SNAKE`; tiền tố bảng đích (`dim_`, `fact_`, `agg_`).
- Cột cờ là mệnh đề khẳng định, đọc lên hiểu ngay: `is_delivered`, `is_late`, `has_items`, `has_payment`,
  `has_review`, `category_missing`, `translation_missing`, `price_outlier`, `multiple_reviews_per_order`.
- ID check chất lượng có tiền tố nhóm: `U-` unique, `F-` foreign key, `D-` miền giá trị, `R-` số dòng,
  `A-` dị thường, `C-` count star schema, `J-` join, `L-` logic.

### 3.3 Hướng phụ thuộc (thực tế)

```
config ─┐
common ─┼─→ ingest ─→ clean ─→ quality ─→ integrate ─→ analytics ─→ dashboard
        │                                    ↑
        └─→ external ─────────────────────────┘
pipeline (điều phối) ─→ ingest, clean, quality, integrate, analytics, dashboard
```

Vi phạm đã phát hiện (một chiều bị đảo): `src/integrate/pipeline.py` import `AnalyticsService` nhưng
không dùng (dòng 10) — xem `code-quality-assessment.md` TD-06. Không có import vòng thực sự.

## 4. Điểm vào

| Điểm vào | Lệnh | Ghi chú |
|---|---|---|
| Pipeline | `python -m src.pipeline run --stage all\|ingest\|clean\|integrate\|analyze [--refresh-ibge]` | `src/pipeline/__main__.py` → `cli.main` |
| Micro-batch | `python -m src.pipeline micro-batch [--inbox <dir>]` | Mặc định `config.inbox_dir` |
| Replay | `python -m src.pipeline replay --batches N` | Tạo batch trong `inbox/replay/` rồi xử lý |
| Dashboard | `python -m src.dashboard` | `app.run(host, port, debug=False)` |
| Test | `python -m pytest [-m "not slow"]` | `pytest.ini` giới hạn `testpaths = tests` |

Mọi lệnh Python phải chạy UTF-8 (`-X utf8` hoặc `PYTHONUTF8=1`) do đường dẫn có ký tự tiếng Việt
và dữ liệu Bồ Đào Nha (`README.md`, `docs/runbook.md`, `AGENTS.md`).

## 5. Ghi chú biên

- `tests/unit/test_dashboard_smoke.py`, `tests/unit/test_cli.py::test_main_analyze_stage` gọi
  `load_config()` mặc định của repo → cần `warehouse/olist.duckdb` và `data/marts/` đã tồn tại.
  Đây là phụ thuộc ngầm của bộ test "nhanh" vào dữ liệu sinh ra (xem `code-quality-assessment.md` TD-09).
- `src/config.py` tạo thư mục đầu ra ngay khi nạp cấu hình, kể cả khi chỉ chạy test — tác dụng phụ
  có chủ đích nhưng làm test không hoàn toàn cô lập.
