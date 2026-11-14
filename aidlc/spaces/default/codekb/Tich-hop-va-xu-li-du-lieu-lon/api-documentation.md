# Hợp đồng API — Olist E-commerce Data Pipeline

> Hệ thống **không có HTTP/REST/GraphQL API công khai**. "API" ở đây là năm loại hợp đồng:
> (1) CLI, (2) hàm Python giữa các tầng, (3) view DuckDB và tệp trên đĩa, (4) callback Dash,
> (5) hợp đồng báo cáo phân tích `data/reports/analysis.json`.
> Cập nhật tập trung ngày 2026-11-11 tại commit `ea77bdf88d1431de11c36e1b739972bd594063f0` cho
> `src/analytics/`, `src/integrate/`, `src/dashboard/`, `src/pipeline/`; chữ ký của
> `src.integration`/`src.linkage` mô tả ở mức tên + hợp đồng đọc được từ test (không đọc sâu thân hàm).

## 1. CLI (`python -m src.pipeline`)

Bộ phân tích đối số: `src/pipeline/cli.py::build_parser` (79 dòng). **Ba lệnh con**, đều bắt buộc một lệnh
(khẳng định ở `tests/unit/test_pipeline_stages.py:157-161`). **Không có lệnh con nào cho thống kê/mô hình**:
việc đó là **tầng** `stats` của lệnh `run`.

### 1.1 `run`

| Tham số | Kiểu | Mặc định | Ý nghĩa |
|---|---|---|---|
| `--stage` | `all \| ingest \| clean \| integrate \| analyze \| stats` | `all` | Tầng cần chạy (**6** giá trị; `set(choices) == set(STAGES) | {"all"}`, khẳng định ở `test_pipeline_stages.py:149-154`) |
| `--refresh-ibge` | cờ | tắt | Bỏ qua cache IBGE, gọi API |

Hành vi: `all` chạy tuần tự ingest → clean → quality → integrate → linkage → analyze và trả
`RunSummary` (**6** mục `stages`) — **`stats` không nằm trong `all`** dù `STAGES` có tên đó; mỗi `--stage`
đơn lẻ chạy đúng một tầng (lưu ý: `--stage clean` đọc `data/raw/`, `--stage integrate` đọc `data/cleaned/`,
`--stage stats` đọc `data/marts/` + `warehouse/olist.duckdb`).

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

`python -m src.dashboard` — không có tham số; đọc `config.dashboard_host` (mặc định `127.0.0.1`)
và `dashboard_port` (mặc định `8050`), chạy `debug=False`.

## 2. Hàm Python giữa các tầng

Chữ ký dưới đây là hợp đồng nội bộ; thay đổi chúng ảnh hưởng trực tiếp tới `tests/`.

| Hàm / lớp | Chữ ký | Trả về | Ném |
|---|---|---|---|
| `src.config.load_config` | `(path: Path \| None = None) -> AppConfig` | cấu hình bất biến, đã tạo thư mục | `ConfigurationError` (thiếu tệp, thiếu `raw_csv_dir`) |
| `src.common.io.read_csv` | `(path, spec) -> DataFrame` | mọi cột `dtype=str` | `SchemaError` |
| `src.common.io.validate_columns` | `(df, spec) -> None` | — | `SchemaError` kèm `missing`/`extra` |
| `src.common.io.AtomicWriter` | `.write_parquet(df, path)`, `.write_json(payload, path)`, `.cleanup()` | — | `RuntimeError` nếu số dòng đọc lại khác |
| `src.common.logging.prune_logs` | `(logs_dir, logger, keep=10) -> int` | số tệp đã xóa | không ném |
| `src.common.kpis.validate_ledger` | `(entries) -> None` | — | `SchemaError` (trùng mã, đơn vị lạ, KPI tiền thiếu định nghĩa doanh thu) |
| `src.common.kpis.kpi` | `(kpi_id) -> KpiLedgerEntry` | dòng sổ KPI | `SchemaError` (mã lạ) |
| `src.ingest.reader.ingest_all` | `(config, run, writer, logger) -> (dict, IngestReport)` | 9 DataFrame thô + báo cáo | `SchemaError` |
| `src.clean.pipeline.clean_all` | `(raw, config, run, writer, logger) -> (dict, CleaningReport)` | 9 bảng đã sạch | — |
| `src.quality.gate.QualityGate.run` | `(datasets, mode="full", geo_stats=None, run_id="") -> QualityReport` | báo cáo check | `KeyError` nếu thiếu bảng |
| `src.quality.gate.QualityGate.enforce` | `(report) -> None` | — | `QualityGateError` |
| `src.external.ibge.IbgeClient.fetch_states` | `(refresh=False) -> (DataFrame, source)` | 27 bang + vùng | `ExternalSourceError` |
| `src.integrate.pipeline.integrate_all` | `(config, run, writer, logger, refresh_ibge=False) -> IntegrationResult` | dims/facts/aggregates + 2 báo cáo | `QualityGateError`, `FileNotFoundError` |
| `src.integrate.validate.StarSchemaValidator.validate` | `(dims, facts, run_id="") -> ValidationReport` | 9 check số dòng + 9 unique + `R-01`/`J-01`/`L-01` | `KeyError` (thiếu dataset) |
| `src.integrate.reconcile.KpiReconciler.reconcile` | `(dims, facts, run_id="") -> KpiReconciliationReport` | 5 chỉ số + 5 delta | — |
| `src.linkage.result.generate_linkage` | `(config, target_entity, run, writer, logger)` | kết quả ghép + tệp JSON | lỗi được ném lại sau khi cả hai đối tượng chạy |
| `src.integration.load.load_don_hang` | `(config) -> DataFrame`-like | bảng đơn đã làm sạch | `SchemaError`, lỗi theo mã đóng |
| `src.integration.schema.load_schema` | `(path) -> MediatedSchemaView` | lược đồ trung gian | `SchemaError`, `ConfigurationError` |
| `src.integration.rewrite.rewrite_plan` | `(entity) -> kế hoạch viết lại` | kế hoạch + SQL tham số hóa | `SchemaError` |
| `src.integration.selector.select_source` | `(catalogue, query_id, logger=None) -> SourceCatalogue` | nguồn được chọn | `NoSourceAvailableError` |
| `src.integration.card.load_tab_config` | `(path) -> TabConfig` | hợp đồng tab | `ConfigurationError` |
| `src.integration.tab.register_callbacks` | `(app, config, tab_config, logger_factory=None) -> None` | — (đăng ký **6** callback) | — |
| `src.pipeline.stages.run_all` | `(config, refresh_ibge=False) -> RunSummary` | tổng kết lần chạy (6 mục) | ném lại sau khi ghi log `run_failed` |
| `src.pipeline.stages.run_stage` | `(config, stage, refresh_ibge=False) -> RunSummary` | tổng kết tầng | `ValueError` (tầng lạ); ném lại sau `stage_failed` |
| `src.pipeline.micro_batch.process_inbox` | `(config, inbox_dir=None) -> list[BatchResult]` | kết quả từng batch | không ném — lỗi ghi vào `BatchResult.error` |
| `src.pipeline.replay.generate` | `(config, batches=3, target_dir=None) -> list[Path]` | thư mục batch đã tạo | `ValueError` (`batches < 1`) |
| `src.pipeline.upsert.upsert` | `(existing, new, keys) -> DataFrame` | bảng hợp nhất, sắp theo khóa | — |
| `src.dashboard.app.create_app` | `(config) -> Dash` | ứng dụng 5 tab + **9** callback | — |
| `src.dashboard.app.build_dashboard_outputs` | `(config, data: dict) -> tuple[9]` | 9 thành phần theo thứ tự cố định | không ném (bắt và trả banner) |

Ghi chú hợp đồng: tham số `config` ở mọi chữ ký là `AppConfig` (không có Protocol/type hint);
`run` là `RunContext`; `writer` là `AtomicWriter`; `logger` là `JsonLogger` hoặc `NullLogger`.

## 3. Dịch vụ phân tích (`AnalyticsService`)

`src/analytics/service.py` (387 dòng). **Chín** phương thức công khai; mọi phương thức tự mở một kết nối
`read_only` và đóng trong `finally`.

### 3.1 Năm phương thức KPI cũ

| Phương thức | Tham số | Trả về |
|---|---|---|
| `kpi_summary` | `filters: KpiFilters` | `dict`: `revenue`, `orders`, `aov`, `delivered_orders`, `late_orders`, `late_rate_pct`, `avg_review_score` |
| `revenue_by_period` | `filters`, `granularity ∈ {month, quarter, year}` | `DataFrame`: `year`, (`month`/`quarter`), `is_sparse_period`, `revenue`, `orders`, `aov` |
| `revenue_by_dimension` | `filters`, `dimension ∈ {category, region, state}` | `DataFrame`: `dimension`, `revenue`, `orders`, `freight`, `aov`, `freight_share_pct` |
| `top_entities` | `filters`, `entity ∈ {product, seller}`, `limit=10` | `DataFrame`: `entity_id`, `category`, `revenue`, `orders` |
| `delivery_kpis` | `filters`, `group_by ∈ {state, category, month}` | `DataFrame`: `dimension`, `delivered_orders`, `late_orders`, `avg_delivery_days`, `late_rate_pct` |

### 3.2 Bốn phương thức mới phục vụ tầng `stats` và mô hình

| Phương thức | Tham số | Trả về | Hợp đồng |
|---|---|---|---|
| `late_rates_by_state` | `filters` | `DataFrame`: `state`, `delivered_orders`, `late_orders` | Dùng `LATE_RATES_BY_STATE_SQL` + `GROUP BY c.state`; **luôn** thêm `o.is_delivered`; gộp ở SQL, không kéo dòng thô về Python (BR1.2, PD-2) |
| `late_rates_by_region` | `filters` | `DataFrame`: `region`, `is_late`, `delivered_orders` | Bảng đếm vùng × trễ, đủ để dựng bảng dự phòng 2 cột (BR1.4) |
| `price_freight_pairs` | `filters`, `limit=MAX_CORRELATION_ROWS (200_000)` | `DataFrame`: `price`, `freight_value` | Grain **dòng hàng**; lọc `f.is_delivered`, loại NULL, `ORDER BY f.order_id, f.order_item_id LIMIT ?` (BR1.3) |
| `training_frame` | — (không nhận `KpiFilters`) | `DataFrame` một dòng mỗi `order_id` | Đọc `TRAINING_FRAME_SQL`; **ném `ValueError`** nếu `order_id` bị lặp ("Bảng huấn luyện nhân dòng") |

`KpiFilters` (frozen dataclass, `src/common/types.py`) có: `start_date`, `end_date`, `state`, `region`,
`category`, `order_status` (mặc định `"delivered"`; giá trị `"all"`, `""` hoặc `None` = bỏ lọc trạng thái).
Hợp đồng ngầm: `revenue` **luôn** là `SUM(item_total)` (gồm phí vận chuyển), mọi truy vấn doanh thu đều
inner join `v_dim_date` (buộc `date_key` phải tồn tại trong `dim_date`, TD-12), và `_where` là **nơi duy nhất**
biết ghép bộ lọc (tham số `alias_fact`/`alias_customer`/`alias_date`/`alias_category`/`status_column`).

### 3.3 Hợp đồng của khung huấn luyện (`TRAINING_FRAME_SQL`)

`service.py:38-74`. Đây là **điểm khớp nối quan trọng nhất** giữa mart và mô hình:

- **Grain**: một dòng mỗi `order_id` (gộp bằng hai CTE `order_items` và `order_payments` trước khi join —
  đúng quy ước "gộp trước khi join để không nhân dòng").
- **Cột trả về** (16): `order_id`, `date_key`, `is_delivered`, `is_late`, `has_items`, `has_payment`,
  `customer_state`, `customer_region`, `purchase_month`, `purchase_weekday`, `item_count`, `item_total`,
  `item_price_max`, `payment_type`, `payment_installments`.
- **Nguồn**: chỉ các view trong `VIEW_TABLES` — `v_fact_orders`, `v_dim_customer`, `v_dim_date`,
  `v_fact_order_items`, `v_fact_payments`. Có test khẳng định mọi tên `v_*` xuất hiện trong câu SQL đều
  thuộc `VIEW_TABLES` (`tests/unit/test_analytics_model.py:617-622`).
- **Quy ước gộp**: `payment_type` lấy của `payment_sequential = 1`; `payment_installments` lấy `MAX`;
  `item_count` = `COUNT(*)`; `item_total` = `SUM(item_total)`; `item_price_max` = `MAX(price)`.
- **Không có** trong khung: `seller_id`, `seller_state`, `product_id`, `shipping_limit_date`,
  `order_approved_at`, `order_delivered_carrier_date`, `order_estimated_delivery_date`, thuộc tính sản phẩm.
  Bốn mốc thời gian sau **có** trong `data/cleaned/orders.parquet` nhưng **không** vào mart, và
  `order_estimated_delivery_date` **có** trong `fact_orders` nhưng truy vấn không chọn.

## 4. Mô-đun suy luận — `src.analytics.statistics` và `src.analytics.model`

### 4.1 `statistics.py` (313 dòng)

| Hàm | Chữ ký | Trả về | Hợp đồng |
|---|---|---|---|
| `confidence_for` | `(alpha=ALPHA) -> float` | `1 - alpha` | Một hằng số alpha duy nhất (BR1.7) |
| `z_critical` | `(alpha=ALPHA) -> float` | `norm.ppf(1 - alpha/2)` | Hai phía |
| `wilson_interval` | `(successes, total, z) -> tuple[float, float]` | khoảng kẹp trong `[0, 1]` | Khoảng Wilson |
| `late_rate` | `(delivered_orders, late_orders, alpha=ALPHA) -> ProportionResult` | `rate`, `ci_low`, `ci_high` | **`ValueError` khi `delivered_orders <= 0`** — dừng cả tầng |
| `compare_states` | `(rates: DataFrame, alpha) -> (list[ComparisonResult], SkipEntry \| None)` | tối đa 1 so sánh | Bang nhiều đơn nhất so với ít đơn nhất trong các bang ≥ `MIN_STATE_ORDERS = 100`; `excluded` = số đơn bị loại |
| `price_freight_correlation` | `(pairs, alpha) -> (CorrelationResult \| None, SkipEntry \| None)` | `r`, `n`, khoảng Fisher | Bỏ khi `n < 4` hoặc phương sai bằng 0; dùng `scipy_stats.pearsonr` |
| `region_late_test` | `(rows, alpha) -> (GroupTestResult \| None, SkipEntry \| None)` | `χ²`, `p`, `dof`, `min_expected` | Chỉ chạy khi mọi ô kỳ vọng ≥ `MIN_EXPECTED_CELL = 5`; `correction=False` |
| `seasonal_decomposition` | `(monthly, alpha) -> (SeasonalResult \| None, SkipEntry \| None)` | 4 chuỗi + `months` | Cộng tính cổ điển, chu kỳ 12, trung bình động giữa `min_periods=1`, tối thiểu 24 tháng |
| `ordered_skips` | `(entries) -> list[SkipEntry]` | mỗi tên tối đa một lần, thứ tự theo `SKIP_TESTS` | BR1.6 |
| `collect_stats` | `(service, filters, generated_at, alpha=ALPHA) -> StatsBlock` | khối đủ năm phép | Đọc dữ liệu **một lần cho mỗi phép** (PD-1) |
| `build_analysis_report` | `(config, generated_at=None, logger=None) -> AnalysisReport` | `stats` mới + **`model` cũ giữ nguyên** | Đọc tệp cũ; tệp cũ hỏng → ghi `stats.previous_report_unreadable` và `model = None` |

Hằng số hợp đồng: `ALPHA = 0.05`, `CONFIDENCE = 0.95`, `MIN_STATE_ORDERS = 100`,
`MIN_CORRELATION_ROWS = 4`, `MIN_EXPECTED_CELL = 5.0`, `SEASONAL_PERIOD = 12`,
`MIN_SEASONAL_MONTHS = 24`, `SEASONAL_METHOD = "classical_additive_12"`,
`GROUP_TEST_NAME = "chi_square_region_late"`, `SKIP_TESTS = ("state_comparison", "correlation",
"group_test", "seasonal")`.

### 4.2 `model.py` (368 dòng)

| Hàm | Chữ ký | Trả về / ném |
|---|---|---|
| `validate_features` | `(features: tuple[str, ...] = FEATURES) -> None` | `ModelError` khi có cột cấm, tên lặp, hoặc **số cột ≠ 11** |
| `delivered_population` | `(frame, expected_delivered=EXPECTED_DELIVERED, expected_late=EXPECTED_LATE)` | `DataFrame` chỉ đơn đã giao; `ModelError` khi thiếu cột hoặc lệch 96.478/7.826 |
| `build_feature_frame` | `(frame) -> DataFrame` | đúng 11 cột theo `FEATURES`; thiếu cột → `ModelError`; số → `fillna(0.0)`, cờ → `bool→float`, phân loại → `str` với `"unknown"` |
| `split_frame` | `(frame, split_date=SPLIT_DATE) -> (train, test)` | `ModelError` khi ngày không parse được hoặc một tập rỗng |
| `split_summary` | `(train, test, expected_total=96_478) -> dict` | 6 khóa `train_start/train_end/test_start/test_end/train_n/test_n`; `ModelError` khi thứ tự sai hoặc tổng lệch |
| `encode_features` | `(train_features, test_features) -> (matrix, matrix)` | one-hot + `StandardScaler` **khớp chỉ trên train** |
| `build_estimator` | `() -> LogisticRegression` | `class_weight="balanced"`, `max_iter=1000`, `random_state=42` |
| `train_classifier` | `(train_matrix, labels) -> LogisticRegression` | **`ModelError` nếu có `ConvergenceWarning`** |
| `choose_threshold` | `(labels, scores, grid=THRESHOLD_GRID) -> ThresholdPoint` | F1 lớn nhất; hoà → ngưỡng cao hơn; một lớp → `ModelError` |
| `auc_below_target` | `(auc) -> bool` | `auc < 0.70` |
| `validate_counts` | `(counts, test_n) -> None` | `flagged + not_flagged == total == test_n`, ngược lại `ModelError` |
| `build_model_block` | `(split, auc, threshold, precision, recall, flagged) -> ModelBlock` | làm tròn 4 chữ số, tính cờ trên giá trị **đã làm tròn**, `threshold` sau làm tròn phải ∈ (0,1) |
| `train_from_frame` | `(frame, expected_delivered=96_478, expected_late=7_826, logger=None) -> ModelBlock` | toàn bộ đường huấn luyện; ghi `model.trained` |
| `train_model` | `(config, logger=None) -> ModelBlock` | đọc `AnalyticsService(config).training_frame()` rồi `train_from_frame` |

Hằng số hợp đồng: `TARGET = "is_late"`, `SPLIT_DATE = "2018-04-01"`, `EXPECTED_DELIVERED = 96_478`,
`EXPECTED_LATE = 7_826`, `MODEL_DIGITS = 4`, `AUC_TARGET = 0.70`,
`THRESHOLD_METHOD = "max_f1_on_test_grid005"`, `THRESHOLD_GRID` = 19 điểm `0.05…0.95`,
`RANDOM_STATE = 42`, `MAX_ITER = 1000`, `BALANCED = "balanced"`, `UNKNOWN = "unknown"`,
`MODEL_TRAINED_EVENT = "model.trained"`.

**Hợp đồng đặc trưng (phải đọc trước khi sửa)**: `FEATURES` = 11 tên; `CATEGORICAL_FEATURES` = 5;
`NUMERIC_FEATURES` = 4; `FLAG_FEATURES` = 2; `FORBIDDEN_COLUMNS` = 10 tên, trong đó có
**`order_delivered_carrier_date`**. `validate_features()` buộc `set(FEATURES) ∩ set(FORBIDDEN) == ∅`,
không trùng tên, và **`len(features) == len(FEATURES)`** — mọi thay đổi số lượng đặc trưng phải sửa cả
hằng số lẫn luật này.

## 5. Hợp đồng báo cáo phân tích (`data/reports/analysis.json`)

`src/analytics/report.py`. **Phiên bản 2**, tên tệp cố định `analysis.json`, đường dẫn lấy từ
`config.reports_dir` (`report_path`), **không** nhận từ dòng lệnh (SEC-5). Khối dưới đây là **hình dạng**
(bốn giá trị `ci_*`/`z`/`seasonal` là số minh hoạ; số thật do dữ liệu quyết định):

```json
{
  "version": 2,
  "generated_at": "<ISO-8601 UTC>",
  "stats": {
    "generated_at": "<ISO-8601>",
    "alpha": 0.05,
    "confidence": 0.95,
    "late_rate": {"successes": 7826, "total": 96478, "rate": 0.0811, "ci_low": 0.0, "ci_high": 0.0},
    "comparisons": [
      {"first": "AL", "second": "RR", "difference": 0.0, "z": 0.0, "p_value": 0.0,
       "ci_low": 0.0, "ci_high": 0.0, "significant": false, "excluded": 0}
    ],
    "correlation": {"r": 0.0, "n": 110197, "ci_low": 0.0, "ci_high": 0.0},
    "group_test": {"test": "chi_square_region_late", "statistic": 0.0, "p_value": 0.0, "dof": 4, "min_expected": 5.0},
    "seasonal": {"revenue_definition": "price + freight_value của đơn delivered",
                 "method": "classical_additive_12", "period": 12,
                 "months": [], "observed": [], "trend": [], "seasonal": [], "residual": []},
    "skipped": [{"test": "correlation", "reason": "..."}]
  },
  "model": {
    "target": "is_late",
    "split": {"train_start": "...", "train_end": "...", "test_start": "2018-04-01", "test_end": "...",
              "train_n": 0, "test_n": 0},
    "auc": 0.5133, "threshold": 0.4, "precision": 0.0866, "recall": 0.2645,
    "counts": {"flagged": 0, "not_flagged": 0, "total": 0,
               "threshold_method": "max_f1_on_test_grid005", "auc_below_target": true}
  }
}
```

Bất biến (đều bị kiểm bởi `read_report`/`write_report`):

1. `version` phải **bằng 2** (không phải bool) — sai → trạng thái `loi`.
2. Mọi trường của cả hai khối phải đúng kiểu; thiếu/sai → `loi` kèm tên trường (`_ShapeError`).
3. `stats` và `model` **không được cùng null** — `_verify_pending` từ chối tệp như vậy.
4. Thiếu đúng một khối → trạng thái `mot-phan` với `missing = ("stats",)` hoặc `("model",)`.
5. Đủ hai khối → `day-du`; tệp không tồn tại → `rong` kèm gợi ý `RUN_STATS_HINT =
   "python -X utf8 -m src.pipeline run --stage stats"`.
6. Tỉ lệ trong báo cáo là **phân số 0–1** (khác `late_rate_pct` 0–100 của KPI); `ModelBlock` và mọi số
   khác làm tròn 4 chữ số, `correlation.r` 3 chữ số.
7. Ghi **một lần duy nhất** cho cả hai khối (`stages.run_stage("stats")`) và ghi nguyên tử
   (temp → parse lại → `os.replace`).

## 6. Kho dữ liệu DuckDB (11 view)

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
| `v_fact_orders` | `order_id` | `customer_id`, `date_key`, `category`, `order_status`, `is_delivered`, **`order_delivered_customer_date`**, **`order_estimated_delivery_date`**, `delivery_days`, `is_late`, `has_items`, `has_payment`, `has_review` |
| `v_fact_payments` | `order_id, payment_sequential` | `date_key`, `payment_type`, `payment_installments`, `payment_value` |
| `v_fact_reviews` | `review_id, order_id` | `date_key`, `review_score`, `multiple_reviews_per_order` |
| `v_agg_sales_daily` | `date_key, state, region, category` | `revenue`, `orders`, `items`, `freight`, `is_sparse_period` |
| `v_agg_delivery_daily` | `date_key, state, region, category` | `delivered_orders`, `late_orders`, `delivery_days_sum`, `is_sparse_period` |

Số view **11** bị khẳng định trong `tests/integration/test_u2_end_to_end.py:44`. Nguồn gốc từng cột (đọc
`src/integrate/facts.py` / `dimensions.py`):

- `v_fact_orders` = `FactBuilder.build_orders` (`facts.py:69-115`): 13 cột, `date_key` từ
  `order_purchase_timestamp`, `delivery_days` = (ngày giao − ngày mua)/86400, `is_late` = đã giao **và**
  giao sau `order_estimated_delivery_date`, `has_items/has_payment/has_review` = phép `isin` trên bảng
  tương ứng, `category` = danh mục chiếm nhiều tiền nhất của đơn (`_dominant_category`, `:44-67`).
  **`order_delivered_carrier_date` và `order_approved_at` không có trong view này** dù có trong cleaned.
- `v_fact_order_items` = `FactBuilder.build_order_items` (`facts.py:9-42`): 12 cột; `item_total` =
  `price.fillna(0) + freight_value.fillna(0)`; **`shipping_limit_date` bị làm rơi**;
  **không có `seller_state`** (bang người bán chỉ có ở `v_dim_seller.state`).
- `v_dim_product` chỉ giữ 4 cột danh mục — `product_weight_g`, `product_length_cm`, `product_height_cm`,
  `product_width_cm`, `product_photos_qty` có trong cleaned nhưng **không** vào mart.
- `v_dim_date` phủ toàn dải ngày mua (774 ngày), `is_sparse_period = year == 2016`.

`v_fact_orders` là nguồn khả dĩ cho mô hình phân loại đơn trễ **và** là nơi chứa rò rỉ đặc trưng: ba cột
`order_delivered_customer_date`, `delivery_days`, `is_late` chỉ có sau khi giao. Cột thứ tư mà
`FORBIDDEN_COLUMNS` đang cấm — `order_delivered_carrier_date` — **không** có trong view nên luật cấm hiện
đang cấm một cột không tồn tại trong khung huấn luyện.

## 7. Hợp đồng tệp trên đĩa

### 7.1 Đường dẫn (từ `config.yaml` → `AppConfig`)

`dataset/` (CSV nguồn) · `config/` (3 hợp đồng YAML) · `data/raw/` · `data/cleaned/` · `data/marts/` ·
`data/reports/` · `data/integration/` · `data/.tmp/<run_id>/` · `warehouse/olist.duckdb` ·
`logs/<run_id>.jsonl` · `inbox/` · `dataset/external/ibge/`.

**Không có** `data/models/` và `AppConfig` **không có** trường thư mục mô hình: hiện không có chỗ nào lưu
mô hình đã huấn luyện (`git grep` không thấy `joblib`/`pickle`).

### 7.2 Tên bảng Parquet (hợp đồng cứng)

- raw: `orders`, `customers`, `order_items`, `payments`, `reviews`, `products`, `sellers`, `geolocation`, `translation`.
- cleaned: như raw nhưng `geolocation` → `geolocation_zip`.
- marts: `dim_customer`, `dim_product`, `dim_seller`, `dim_geography`, `dim_date`,
  `fact_order_items`, `fact_orders`, `fact_payments`, `fact_reviews`, `agg_sales_daily`, `agg_delivery_daily`.

### 7.3 Báo cáo JSON trong `data/reports/`

| Tệp | Hình dạng (khóa cấp 1) | Nơi ghi |
|---|---|---|
| `ingest-report.json` | `run_id`, `files[]`, `passed` | `src/ingest/reports.py` |
| `cleaning-report.json` | `run_id`, `tables[]`, `geolocation` | `src/ingest/reports.py` |
| `quality-report.json` | `run_id`, `mode`, `checks[]`, `passed` | `src/ingest/reports.py` |
| `reconciliation.json` | `run_id`, `orders_compared`, `mismatch_count`, `max_abs_diff`, `examples[]` | `src/ingest/reports.py` |
| `integration-report.json` | `run_id`, `row_counts{11 bảng}`, `ibge_source`, `passed` | `src/integrate/pipeline.py` |
| `kpi-reconciliation.json` | `run_id`, `metrics{5 KPI}`, `deltas{5 KPI}`, `passed` | `src/integrate/pipeline.py` |
| **`analysis.json`** | `version`(2), `generated_at`, `stats{…}`, `model{…}` | `src/analytics/report.py` (chỉ tầng `stats`) |
| `run-summary.json` | `run_id`, `command`, `stages[]`, `success`, `started_at`, `finished_at` | `src/pipeline/stages.py` |

### 7.4 Kết quả tích hợp trong `data/integration/`

- `linkage-customer.json`, `linkage-seller.json` — kết quả ghép bản ghi; tab "Tích hợp" đọc lại để điền thẻ.
  Payload phải có các khóa `target_entity`, `run_id`, `computed_at`, `threshold`, `summary`, `pairs`, `skipped`
  (`src/integration/tab.py`); thiếu khóa → `LinkageResultInvalidError`, thiếu tệp →
  `LinkageResultMissingError` (trạng thái rỗng, không phải lỗi).

### 7.5 Nhật ký JSONL (`logs/<run_id>.jsonl`)

Mỗi dòng một đối tượng: `timestamp` (UTC ISO-8601, hậu tố `Z`), `level` (`INFO`/`WARNING`/`ERROR`),
`run_id`, `stage`, `event`, các trường bổ sung tùy sự kiện. Sự kiện tiêu biểu: `ingest_table`,
`ingest_complete`, `clean_table`, `quality_gate`, `ibge_cache_hit`, `ibge_fetched`,
`ibge_api_failed_using_cache`, `integrate_complete`, `analyze_smoke`, `batch_success`, `batch_failed`,
`stage_failed`, `run_failed`, `summary`, `integration.load.*`, `integration.query.*`, `integration.selector.*`,
`integration.linkage.*`, `integration.logs.pruned`, `integration.log.prune_failed`, và của đợt này:
**`model.trained`** (`auc`, `threshold`, `train_n`, `test_n`, `auc_below_target`),
**`stats_report_written`** (`path`, `skipped[]`, `comparisons`, `model_auc`, `model_threshold`,
`model_auc_below_target`), **`stats.previous_report_unreadable`** (`path`, `message`).
**Giữ tối đa 10 tệp** sau mỗi lần chạy (`prune_logs`).

### 7.6 Hợp đồng micro-batch

- Thư mục: `inbox/<batch_id>/<table>.csv`; `<table>` phải thuộc 9 tên bảng nguồn (nếu không → `ValueError`).
- Mỗi CSV phải khớp `TABLE_SPECS[table]` (tên và thứ tự cột, UTF-8) và ≤ `micro_batch.max_rows` (10.000 dòng).
- `inbox/manifest.json`: `{"batches": [{"batch_id", "files": [{"table", "file", "sha256", "status", "rows"?}], "status", "error", "processed_at"}]}`;
  `record` thay thế mục cùng `batch_id` và sắp theo `batch_id`.
- Khóa upsert theo bảng: `TABLE_KEYS` trong `src/pipeline/micro_batch.py`.

### 7.7 Hợp đồng cấu hình tab (`config/integration-tab.yaml`)

```yaml
tab_id: tich-hop
tab_label: Tích hợp
card_ids: [luoc-do-trung-gian, viet-lai-truy-van, ghep-ban-ghi, chon-nguon]
result_region_ids: [don-theo-thang]
callback_ids: [tich-hop-cap-nhat]
```

Bất biến: `card_ids` phải khớp `CARD_TITLES` trong `src/integration/tab.py`; `result_region_ids` phải có hàm
dựng tương ứng (id lạ → `ConfigurationError`); chỉ **thêm** id, không đổi tên id đã có. **Tab thứ năm không
có hợp đồng YAML**: `TAB_VALUE = "phan-tich"`, `TAB_LABEL = "Kết quả phân tích"` là hằng số trong
`src/dashboard/analysis_tab.py:30-31`, và `app.py` import chúng — thêm/bớt tab này là sửa mã, không sửa YAML.

### 7.8 Hợp đồng dữ liệu tham chiếu IBGE

`dataset/external/ibge/estados.json` giữ nguyên payload API (`id`, `sigla`, `nome`, `regiao{id,sigla,nome}`);
`metadata.json`: `url`, `fetched_at`, `sha256`, `states`, `municipalities`, `source`.
Cache chỉ được coi là hợp lệ khi parse ra đúng **27 bang / 5 vùng** (`IbgeClient._cache_valid`).

## 8. Callback Dashboard

Tổng **9 callback** trong `app.callback_map`; hai callback đầu thuộc bốn tab báo cáo, **sáu** callback do
`src.integration.tab.register_callbacks` đăng ký (năm của U6 + một sinh theo `result_region_ids`), **một**
của tab "Kết quả phân tích".

| Callback | Đầu vào | Đầu ra |
|---|---|---|
| `sync_filters` | `date-range.start_date`, `date-range.end_date`, `state-filter.value`, `region-filter.value`, `category-filter.value`, `status-filter.value` | `filters-store.data` (dict 6 khóa, `order_status` mặc định `delivered`) |
| `render_dashboard` | `filters-store.data` | **9 output theo thứ tự**: `kpi-cards.children`, `sparse-warning.children`, `revenue-trend.figure`, `category-bar.figure`, `category-detail-bar.figure`, `top-products.children`, `delivery-state.figure`, `delivery-category.figure`, `delivery-month.figure` |
| tab Tích hợp — tổng quan | `tabs.value` | `overview-cards.children`, `overview-panel.hidden` |
| tab Tích hợp — định tuyến | nút "Xem chi tiết" / "Quay lại" (pattern-matching id) | `screen-body.children` |
| tab Tích hợp — chạy truy vấn | `run-query` / `retry-query` / `query-template` | `query-result.children` |
| tab Tích hợp — đề xuất nguồn | `suggest-source` / `source-query` | `source-table.children` + `source-table.data-state` |
| tab Tích hợp — tải lại | `reload-token` | `reload-token.data` |
| tab Tích hợp — vùng lát cắt | `filters` của vùng | `don-theo-thang.children` |
| **tab phân tích** | `tabs.value` | **`analysis-result.children`** — `no_update` khi giá trị khác `"phan-tich"` |

Ràng buộc: `build_dashboard_outputs` **luôn** trả bộ 9 phần tử, kể cả khi lỗi (banner lỗi + figure rỗng),
để callback không vỡ layout. Test khẳng định `len(app.callback_map) == 9` (`test_dashboard_smoke.py:62`,
`test_u3_end_to_end.py:83`), `len(tabs.children) == 5` (`test_dashboard_smoke.py:57`,
`test_u3_end_to_end.py:87`), `len(outputs) == 9` (`test_dashboard_smoke.py:115,131`) và
`len(app.callback_map) == 6` cho riêng tab Tích hợp (`test_integration_tab.py:938`).
Id của thành phần chỉ tồn tại trong màn hình chi tiết **phải** dùng pattern-matching id, nếu dùng id cố định
Dash báo "nonexistent object" khi tải trang (`test_dashboard_smoke.py:81-98` ghi lại lỗi thật ngày 2026-11-09).

### 8.1 Hợp đồng của tab "Kết quả phân tích"

| Hạng mục | Giá trị cố định | Nơi khai |
|---|---|---|
| `value` / `label` của tab | `"phan-tich"` / `"Kết quả phân tích"` | `analysis_tab.py:30-31` |
| Vùng nội dung | `id="analysis-result"`, `data-state`, `aria-live="polite"` | `:34`, `:519-528` |
| Token | `rong`, `chua-chay` (chỉ UI), `day-du`, `mot-phan`, `loi` | `:36-37` + `report.STATUSES` |
| Ba khối, đúng thứ tự | `tom-tat` → `thong-ke` → `mo-hinh` | `SECTION_IDS:42-45` |
| Bốn thẻ tóm tắt | `ti-le-tre`, `so-don`, `so-bo-qua`, `auc` | `CARD_IDS:47` |
| Năm mục thống kê | `ti-le-tre`, `so-sanh-bang`, `tuong-quan`, `kiem-dinh-nhom`, `mua-vu` | `build_stats_items` |
| Bốn số đọc của mô hình | `auc`, `nguong`, `precision`, `recall` (**không** thanh trượt, **không** ô nhập) | `build_model_section:419-446` |
| Lớp CSS | mọi lớp dùng trong tab phải có trong `assets/style.css`; khối `.analysis-tab` **không** dùng `--text-3` | `test_dashboard_analysis_tab.py:485-490`, `test_analysis_tab_contrast.py:64-66` |

## 9. Hợp đồng lỗi

| Ngoại lệ | Tầng phát | Tầng bắt | Hành vi |
|---|---|---|---|
| `ConfigurationError` | `src.config`, `src.integration.card` | CLI / dashboard | dừng, in stderr, mã thoát 1; dashboard dùng hợp đồng tab mặc định |
| `SchemaError` | `src.common.io`, `src.integration.*` | CLI / `process_inbox` / tab | dừng tầng; trong tab hiển thị tại chỗ |
| `QualityGateError` | `src.quality`, `src.integrate.validate/reconcile` | CLI / `process_inbox` | chặn promote mart |
| `ExternalSourceError` | `src.external` | `integrate_all` (không bắt) | dừng pipeline (trừ khi cache còn hợp lệ) |
| `QueryExecutionError` | `src.integration.load`/`rewrite` | tab, `run_query_body` | hiển thị thông điệp lỗi trong vùng kết quả |
| `KpiMismatchError` | `src.integration.rewrite` | test, tab | lệch quá dung sai 0,01 BRL |
| `NoSourceAvailableError` | `src.integration.selector` | tab | liệt kê trường còn thiếu cho truy vấn |
| `LinkageResultMissingError` / `LinkageResultInvalidError` | `src.integration.tab` | tab | trạng thái rỗng / trạng thái lỗi của riêng thẻ đó |
| **`ModelError`** | `src.analytics.model` | `stages.run_stage("stats")` | tầng `stats` **dừng**, ghi `stage_failed`, **không** ghi tệp báo cáo (báo cáo cũ giữ nguyên) |
| **`ReportError`** | `src.analytics.report` (`write_report`/`_verify_pending`) | `stages.run_stage("stats")` | tệp tạm bị xóa, tệp cũ **không** bị thay |
| `ValueError` | CLI, tham số analytics (`granularity`/`dimension`/`entity`/`group_by`), `training_frame` khi nhân dòng, `micro_batch`, `replay` | CLI / `stages` | dừng hoặc batch `failed` |
| `Exception` (bắt rộng) | `src.pipeline.cli`, `stages`, `micro_batch`, `dashboard.app`, `dashboard.analysis_tab` | chính các tầng đó | ghi log/`error_banner`/trạng thái `loi`, rồi ném lại hoặc trả trạng thái |

Không có cơ chế retry ở tầng pipeline ngoài retry IBGE (`ibge_retries`, mặc định 2, backoff `1 + attempt`
giây) và retry một lần của lớp nạp CSV trong `src/integration/load.py`. `train_classifier` **không** retry:
không hội tụ là lỗi, không phải ghi chú.
