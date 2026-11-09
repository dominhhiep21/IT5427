# Hợp đồng API — Olist E-commerce Data Pipeline

> Hệ thống **không có HTTP/REST/GraphQL API công khai**. "API" ở đây là bốn loại hợp đồng:
> (1) CLI, (2) hàm Python giữa các tầng, (3) view DuckDB và tệp trên đĩa, (4) callback Dash.
> Danh mục thành phần xem `component-inventory.md`.

## 1. CLI (`python -m src.pipeline`)

Bộ phân tích đối số: `src/pipeline/cli.py::build_parser`. Ba lệnh con, đều bắt buộc một lệnh.

### 1.1 `run`

| Tham số | Kiểu | Mặc định | Ý nghĩa |
|---|---|---|---|
| `--stage` | `all \| ingest \| clean \| integrate \| analyze` | `all` | Tầng cần chạy |
| `--refresh-ibge` | cờ | tắt | Bỏ qua cache IBGE, gọi API |

Hành vi: `all` chạy tuần tự ingest → clean → quality → integrate → analyze và trả
`RunSummary`; mỗi `--stage` đơn lẻ chạy đúng một tầng (lưu ý: `--stage clean` đọc `data/raw/`,
`--stage integrate` đọc `data/cleaned/`).

Đầu ra stdout:

```
run_id=<run_id> success=<bool>
  <stage>: <status> rows_in=<n> rows_out=<n> <giây>s
```

Mã thoát: `0` khi `summary.success`, `1` khi thất bại hoặc có exception (in `ERROR: ...` ra stderr).

### 1.2 `micro-batch`

| Tham số | Kiểu | Mặc định | Ý nghĩa |
|---|---|---|---|
| `--inbox` | đường dẫn | `config.inbox_dir` (`inbox/`) | Thư mục chứa các batch |

Đầu ra mỗi batch: `batch=<batch_id> status=<success|skipped|failed> rows=<n> <giây>s`.
Mã thoát: `0` nếu mọi batch `success` hoặc `skipped`, ngược lại `1`.

### 1.3 `replay`

| Tham số | Kiểu | Mặc định | Ý nghĩa |
|---|---|---|---|
| `--batches` | int ≥ 1 | 3 | Số tháng gần nhất cần cắt thành batch |

Đầu ra: `generated=<n> batches` rồi danh sách `batch=<id> status=<...>`.
Mã thoát như `micro-batch`.

### 1.4 Dashboard

`python -m src.dashboard` — không có tham số; đọc `config.dashboard.host` (mặc định `127.0.0.1`)
và `port` (mặc định `8050`), chạy `debug=False`.

## 2. Hàm Python giữa các tầng

Chữ ký dưới đây là hợp đồng nội bộ; thay đổi chúng ảnh hưởng trực tiếp tới `tests/`.

| Hàm / lớp | Chữ ký | Trả về | Ném |
|---|---|---|---|
| `src.config.load_config` | `(path: Path \| None = None) -> AppConfig` | cấu hình bất biến, đã tạo thư mục | `ConfigurationError` (thiếu tệp, thiếu `raw_csv_dir`) |
| `src.common.io.read_csv` | `(path: Path, spec: TableSpec) -> DataFrame` | mọi cột `dtype=str` | `SchemaError` (không thấy tệp, sai UTF-8, lệch cột) |
| `src.common.io.validate_columns` | `(df, spec) -> None` | — | `SchemaError` kèm `missing`/`extra` |
| `src.common.io.AtomicWriter` | `.write_parquet(df, path)`, `.write_json(payload, path)`, `.cleanup()` | — | `RuntimeError` nếu số dòng đọc lại khác |
| `src.ingest.reader.ingest_all` | `(config, run, writer, logger) -> (dict[str, DataFrame], IngestReport)` | 9 DataFrame thô + báo cáo | `SchemaError` |
| `src.clean.pipeline.clean_all` | `(raw, config, run, writer, logger) -> (dict, CleaningReport)` | 9 bảng đã sạch (gồm `geolocation_zip`) | — |
| `src.quality.gate.QualityGate.run` | `(datasets, mode="full", geo_stats=None, run_id="") -> QualityReport` | báo cáo check | `KeyError` nếu thiếu bảng |
| `src.quality.gate.QualityGate.enforce` | `(report) -> None` | — | `QualityGateError` liệt kê mọi check fail |
| `src.external.ibge.IbgeClient.fetch_states` | `(refresh=False) -> (DataFrame, source)` với `source ∈ {cache, api}` | 27 bang + vùng | `ExternalSourceError` khi API lỗi và cache không hợp lệ |
| `src.external.region.RegionMapper.validate` | `(region_map, states_in_data=None) -> None` | — | `ExternalSourceError` |
| `src.integrate.pipeline.integrate_all` | `(config, run, writer, logger, refresh_ibge=False) -> IntegrationResult` | dims/facts/aggregates + 2 báo cáo | `QualityGateError`, `FileNotFoundError` |
| `src.analytics.service.AnalyticsService` | 5 phương thức (mục 4) | `dict` hoặc `DataFrame` | `ValueError` (tham số phân vị/chiều không hợp lệ) |
| `src.pipeline.stages.run_all` | `(config, refresh_ibge=False) -> RunSummary` | tổng kết lần chạy | ném lại sau khi ghi log `run_failed` |
| `src.pipeline.stages.run_stage` | `(config, stage, refresh_ibge=False) -> RunSummary` | tổng kết tầng | `ValueError` (tầng lạ); ném lại sau khi ghi `stage_failed` |
| `src.pipeline.micro_batch.process_inbox` | `(config, inbox_dir=None) -> list[BatchResult]` | kết quả từng batch | không ném — lỗi ghi vào `BatchResult.error` |
| `src.pipeline.replay.generate` | `(config, batches=3, target_dir=None) -> list[Path]` | thư mục batch đã tạo | `ValueError` (`batches < 1`) |
| `src.pipeline.upsert.upsert` | `(existing, new, keys) -> DataFrame` | bảng hợp nhất, sắp theo khóa | — |
| `src.dashboard.app.create_app` | `(config) -> Dash` | ứng dụng đã gắn layout + 2 callback | — |

Ghi chú hợp đồng: tham số `config` ở mọi chữ ký là `AppConfig` (không có Protocol/type hint);
`run` là `RunContext`; `writer` là `AtomicWriter`; `logger` là `JsonLogger`.

## 3. Kho dữ liệu DuckDB (11 view)

`src/integrate/catalog.py` tạo `CREATE OR REPLACE VIEW v_<tên> AS SELECT * FROM read_parquet('<đường dẫn tuyệt đối>')`.
Tên view = tiền tố `v_` + tên bảng mart. Không có bảng vật lý, không phân quyền, kết nối dashboard là `read_only`.

| View | Grain | Cột chính |
|---|---|---|
| `v_dim_customer` | `customer_id` | `customer_unique_id`, `zip_code_prefix`, `city`, `city_normalized`, `state`, `region` |
| `v_dim_product` | `product_id` | `category`, `category_english`, `category_missing`, `translation_missing` |
| `v_dim_seller` | `seller_id` | `zip_code_prefix`, `city`, `city_normalized`, `state`, `region` |
| `v_dim_geography` | `zip_code_prefix` | `lat_median`, `lng_median`, `city_mode`, `state_mode`, `region` |
| `v_dim_date` | `date_key` (`YYYY-MM-DD`) | `date`, `year`, `quarter`, `month`, `day`, `weekday`, `is_sparse_period` |
| `v_fact_order_items` | `order_id, order_item_id` | `customer_id`, `product_id`, `seller_id`, `date_key`, `price`, `freight_value`, `item_total`, `price_outlier`, `order_status`, `is_delivered` |
| `v_fact_orders` | `order_id` | `customer_id`, `date_key`, `category`, `order_status`, `is_delivered`, 2 mốc ngày, `delivery_days`, `is_late`, `has_items`, `has_payment`, `has_review` |
| `v_fact_payments` | `order_id, payment_sequential` | `date_key`, `payment_type`, `payment_installments`, `payment_value` |
| `v_fact_reviews` | `review_id, order_id` | `date_key`, `review_score`, `multiple_reviews_per_order` |
| `v_agg_sales_daily` | `date_key, state, region, category` | `revenue`, `orders`, `items`, `freight`, `is_sparse_period` |
| `v_agg_delivery_daily` | `date_key, state, region, category` | `delivered_orders`, `late_orders`, `delivery_days_sum`, `is_sparse_period` |

Chi tiết kiểu/mô tả cột: `docs/data-dictionary.md` (nguồn của bảng trên, đã đối chiếu mã).

## 4. Dịch vụ phân tích (`AnalyticsService`)

| Phương thức | Tham số | Trả về |
|---|---|---|
| `kpi_summary` | `filters: KpiFilters` | `dict`: `revenue`, `orders`, `aov`, `delivered_orders`, `late_orders`, `late_rate_pct`, `avg_review_score` |
| `revenue_by_period` | `filters`, `granularity ∈ {month, quarter, year}` | `DataFrame`: `year`, (`month`/`quarter`), `is_sparse_period`, `revenue`, `orders`, `aov` |
| `revenue_by_dimension` | `filters`, `dimension ∈ {category, region, state}` | `DataFrame`: `dimension`, `revenue`, `orders`, `freight`, `aov`, `freight_share_pct` |
| `top_entities` | `filters`, `entity ∈ {product, seller}`, `limit=10` | `DataFrame`: `entity_id`, `category`, `revenue`, `orders` |
| `delivery_kpis` | `filters`, `group_by ∈ {state, category, month}` | `DataFrame`: `dimension`, `delivered_orders`, `late_orders`, `avg_delivery_days`, `late_rate_pct` |

`KpiFilters` (frozen dataclass) có: `start_date`, `end_date`, `state`, `region`, `category`,
`order_status` (mặc định `"delivered"`; giá trị `"all"`, `""` hoặc `None` = bỏ lọc trạng thái).
Hợp đồng ngầm: `revenue` **luôn** là `SUM(item_total)` gồm phí vận chuyển, và mọi truy vấn doanh thu
đều join `v_dim_date` (buộc `date_key` phải tồn tại trong `dim_date`).

## 5. Hợp đồng tệp trên đĩa

### 5.1 Đường dẫn (từ `config.yaml` → `AppConfig`)

`dataset/` (CSV nguồn) · `data/raw/` · `data/cleaned/` · `data/marts/` · `data/reports/` ·
`data/.tmp/<run_id>/` · `warehouse/olist.duckdb` · `logs/<run_id>.jsonl` · `inbox/` ·
`dataset/external/ibge/`.

### 5.2 Tên bảng Parquet (hợp đồng cứng)

- raw: `orders`, `customers`, `order_items`, `payments`, `reviews`, `products`, `sellers`, `geolocation`, `translation`.
- cleaned: như raw nhưng `geolocation` → `geolocation_zip`.
- marts: `dim_customer`, `dim_product`, `dim_seller`, `dim_geography`, `dim_date`,
  `fact_order_items`, `fact_orders`, `fact_payments`, `fact_reviews`, `agg_sales_daily`, `agg_delivery_daily`.

### 5.3 Báo cáo JSON trong `data/reports/`

| Tệp | Hình dạng (khóa cấp 1) | Nơi ghi |
|---|---|---|
| `ingest-report.json` | `run_id`, `files[]` (`table`, `file`, `rows`, `expected_rows`, `columns`, `sha256`, `read_at`), `passed` | `src/ingest/reports.py` |
| `cleaning-report.json` | `run_id`, `tables[]` (`table`, `rows_in`, `rows_out`, `null_counts`, `flag_counts`), `geolocation` (`raw_rows`, `deduped_rows`, `outside_bbox`, `zips`, `zips_without_coord`, `multi_city_zips`) | `src/ingest/reports.py` |
| `quality-report.json` | `run_id`, `mode`, `checks[]` (`check_id`, `name`, `passed`, `expected`, `actual`, `details`), `passed` | `src/ingest/reports.py` |
| `reconciliation.json` | `run_id`, `orders_compared`, `mismatch_count`, `max_abs_diff`, `examples[]` (10 đơn lệch lớn nhất) | `src/ingest/reports.py` |
| `integration-report.json` | `run_id`, `row_counts{11 bảng}`, `ibge_source` (`cache`/`api`), `passed` | `src/integrate/pipeline.py` |
| `kpi-reconciliation.json` | `run_id`, `metrics{5 KPI}`, `deltas{5 KPI}`, `passed` | `src/integrate/pipeline.py` |
| `run-summary.json` | `run_id`, `command`, `stages[]` (`stage`, `status`, `rows_in`, `rows_out`, `duration_seconds`, `error`), `success`, `started_at`, `finished_at` | `src/pipeline/stages.py` |

### 5.4 Nhật ký JSONL (`logs/<run_id>.jsonl`)

Mỗi dòng một đối tượng: `timestamp` (UTC ISO-8601, hậu tố `Z`), `level` (`INFO`/`WARNING`/`ERROR`),
`run_id`, `stage`, `event`, các trường bổ sung tùy sự kiện (ví dụ `table`, `rows_in`, `rows_out`,
`sha256`, `error_code`, `error`). Sự kiện tiêu biểu: `ingest_table`, `ingest_complete`, `clean_table`,
`quality_gate`, `ibge_cache_hit`, `ibge_fetched`, `ibge_api_failed_using_cache`, `integrate_complete`,
`analyze_smoke`, `batch_success`, `batch_failed`, `stage_failed`, `run_failed`, `summary`.

### 5.5 Hợp đồng micro-batch

- Thư mục: `inbox/<batch_id>/<table>.csv`; `<table>` phải thuộc 9 tên bảng nguồn (nếu không → `ValueError`).
- Mỗi CSV phải khớp `TABLE_SPECS[table]` (tên và thứ tự cột, UTF-8) và ≤ `micro_batch.max_rows` (10.000 dòng).
- `inbox/manifest.json`: `{"batches": [{"batch_id", "files": [{"table", "file", "sha256", "status", "rows"?}], "status", "error", "processed_at"}]}`;
  `record` thay thế mục cùng `batch_id` và sắp theo `batch_id`. `has_success(sha256)` trả `True`
  nếu bất kỳ tệp nào có hash đó với `status ∈ {success, skipped}`.
- Khóa upsert theo bảng: `TABLE_KEYS` trong `src/pipeline/micro_batch.py` (trùng khóa tự nhiên của `TABLE_SPECS`,
  riêng `geolocation_zip` dùng `zip_code_prefix`).

### 5.6 Hợp đồng dữ liệu tham chiếu IBGE

`dataset/external/ibge/estados.json` giữ nguyên payload API (`id`, `sigla`, `nome`, `regiao{id,sigla,nome}`);
`metadata.json`: `url`, `fetched_at`, `sha256`, `states`, `municipalities`, `source`.
Cache chỉ được coi là hợp lệ khi parse ra đúng **27 bang / 5 vùng** (`IbgeClient._cache_valid`).

## 6. Callback Dashboard

| Callback | Đầu vào | Đầu ra |
|---|---|---|
| `sync_filters` | `date-range.start_date`, `date-range.end_date`, `state-filter.value`, `region-filter.value`, `category-filter.value`, `status-filter.value` | `filters-store.data` (dict 6 khóa, `order_status` mặc định `delivered`) |
| `render_dashboard` | `filters-store.data` | 9 output theo thứ tự: `kpi-cards.children`, `sparse-warning.children`, `revenue-trend.figure`, `category-bar.figure`, `category-detail-bar.figure`, `top-products.children`, `delivery-state.figure`, `delivery-category.figure`, `delivery-month.figure` |

Ràng buộc: `build_dashboard_outputs` **luôn** trả bộ 9 phần tử, kể cả khi lỗi (banner lỗi + figure rỗng),
để callback không vỡ layout. Test khẳng định `len(app.callback_map) == 2`.

## 7. Hợp đồng lỗi

| Ngoại lệ | Tầng phát | Tầng bắt | Hành vi |
|---|---|---|---|
| `ConfigurationError` | `src.config` | CLI | dừng, in stderr, mã thoát 1 |
| `SchemaError` | `src.common.io` | CLI / `process_inbox` (ghi `BatchResult.error`) | dừng tầng |
| `QualityGateError` | `src.quality`, `src.integrate.validate/reconcile` | CLI / `process_inbox` | chặn promote mart |
| `ExternalSourceError` | `src.external` | `integrate_all` (không bắt) | dừng pipeline (trừ khi cache còn hợp lệ) |
| `ValueError` | CLI, tham số analytics, micro-batch | CLI | dừng hoặc batch `failed` |
| `Exception` (bắt rộng) | CLI, `stages`, `micro_batch`, `dashboard` | chính các tầng đó | ghi log/`error_banner`, rồi ném lại hoặc trả trạng thái |

Không có cơ chế retry ở tầng pipeline ngoài retry IBGE (`ibge.retries`, mặc định 2, backoff `1 + attempt` giây).
