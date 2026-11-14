# Developer Code Scan — Olist E-commerce Data Pipeline

> Lần quét **tập trung** (FOCUSED), độ sâu **Standard**, ngày 2026-11-11, tại commit
> `ea77bdf88d1431de11c36e1b739972bd594063f0` trên nhánh `feature/analysis-and-models`
> (cây làm việc có thay đổi chưa commit — xem §"Trạng thái cây làm việc").
> Chỉ **đọc** mã và cấu hình; không chạy test, không chạy pipeline, không chạy chương trình của dự án.
> Artifact chín tệp của CodeKB được dựng song song trong
> `.../.aidlc-engine/codekb-stage-Tich-hop-va-xu-li-du-lieu-lon/`.

## Developer Code Scan Results

### Scan Coverage

**Analyzed deeply** (nằm trong tập đường dẫn của pre-scan snapshot; đã đọc từng dòng):

- `src/analytics/service.py` (387 dòng) — 5 truy vấn KPI cũ + 4 phương thức mới của tầng `stats`
  (`late_rates_by_state`, `late_rates_by_region`, `price_freight_pairs`, `training_frame`) và 4 hằng SQL
  cấp mô-đun (`TRAINING_FRAME_SQL`, `LATE_RATES_BY_STATE_SQL`, `LATE_RATES_BY_REGION_SQL`,
  `PRICE_FREIGHT_PAIRS_SQL`).
- `src/analytics/model.py` (368 dòng) — `FEATURES`/`FORBIDDEN_COLUMNS`, `delivered_population`,
  `build_feature_frame`, `split_frame`, `encode_features`, `train_classifier`, `choose_threshold`,
  `build_model_block`, `train_from_frame`, `train_model`.
- `src/analytics/statistics.py` (313 dòng) — `wilson_interval`, `late_rate`, `compare_states`,
  `price_freight_correlation`, `region_late_test`, `seasonal_decomposition`, `collect_stats`,
  `build_analysis_report`.
- `src/analytics/report.py` (502 dòng) — `REPORT_VERSION = 2`, `AnalysisReport`/`StatsBlock`/`ModelBlock`,
  `write_report`, `read_report`, bốn trạng thái `rong|day-du|mot-phan|loi`.
- `src/analytics/filters.py` (7 dòng) — shim re-export `KpiFilters`.
- `src/integrate/facts.py` (162), `dimensions.py` (118), `aggregates.py` (87), `validate.py` (147),
  `reconcile.py` (66), `catalog.py` (54), `connections.py` (30), `pipeline.py` (128) — nguồn gốc từng cột
  của 11 bảng mart và 11 view DuckDB.
- `src/dashboard/app.py` (589) — `build_layout` 5 tab, 2 callback báo cáo (9 output), `_tab_config`,
  `create_app` (9 callback), `_integration_logger`, `build_dashboard_outputs`.
- `src/dashboard/analysis_tab.py` (566) — tab thứ năm: `AnalysisTab`, `AnalysisPanel`, `state_for`,
  `summary_cards`, `build_stats_section`, `build_model_section`, `sections_for`, `render_analysis`,
  `register_callback`.
- `src/dashboard/components.py` (111), `formatting.py` (39), `__main__.py` (16).
- `src/pipeline/stages.py` (274) — `STAGES` 5 tên, `_run_all` 6 `StageResult`, nhánh `stats`,
  `run_all`/`run_stage`.
- `src/pipeline/cli.py` (79) — `build_parser` 3 lệnh con, `--stage` 6 lựa chọn.
- `src/pipeline/micro_batch.py` (188), `manifest.py` (47), `replay.py` (54), `upsert.py` (21).
- `tests/conftest.py` (361) — 12 fixture, `config` và `real_config`.
- `tests/unit/`: `test_analytics_model.py` (646), `test_analytics_statistics.py` (429),
  `test_analytics_report.py` (283), `test_pipeline_stages.py` (261), `test_dashboard_smoke.py` (176),
  `test_dashboard_analysis_tab.py` (627), `test_analysis_tab_contrast.py` (66), `test_ci_config.py` (108),
  `test_cli.py` (21).
- `tests/integration/`: `test_u1_end_to_end.py` (72), `test_u2_end_to_end.py` (99),
  `test_u3_end_to_end.py` (120), `test_u1_stats_end_to_end.py` (130), `test_u2_model_end_to_end.py` (95).
- `tests/data_quality/test_real_dataset.py` (52) và các mô-đun `tests/unit/test_*.py` còn lại: đọc tiêu đề
  và khẳng định chính, không đọc từng dòng (xem "Skimmed only").

**Skimmed only** (đọc ở mức gói/lát cắt, không xác minh toàn bộ):

- `src/ingest/` — đọc trọn `schemas.py` (132 dòng) để biết cột nguồn (`order_items` có
  `shipping_limit_date`; `orders` có `order_delivered_carrier_date`); `reader.py`, `reports.py` chỉ đọc
  chữ ký hàm.
- `src/clean/` — đọc trọn `orders.py` (29 dòng) vì mốc `order_delivered_carrier_date` là tâm điểm của
  intent; 10 mô-đun còn lại chỉ đọc tiêu đề.
- `src/quality/` — chỉ đọc mức gói; số check 21/9/10 **không** đếm lại lần này.
- `src/common/` — đọc trọn `kpis.py` (108 dòng, vì `REVENUE_DEFINITION` được `report.py`/`statistics.py`
  dùng lại); `types.py`, `io.py`, `logging.py`, `exceptions.py`, `memory.py` chỉ đọc chữ ký.
- `src/external/`, `src/integration/`, `src/linkage/` — chỉ đọc mức gói; các con số 1.380 dòng
  (`integration/tab.py`), 819 (`rewrite.py`), 543 (`selector.py`) là **đo trên đĩa**, không phải phân tích
  lại.
- `src/config.py` (157) — đọc trọn, vì `report.py` cần `config.reports_dir`/`config.temp_dir` và intent
  cần biết `AppConfig` có trường nào cho mô hình đã lưu (không có).
- `config.yaml` (45), `requirements.txt` (27), `pytest.ini` (5), `ruff.toml` (29),
  `.github/workflows/ci.yml` (toàn văn), `README.md` (mục Kiến trúc / Chạy pipeline / Dashboard / Test /
  Lint / CI / Lưu ý), `CHANGELOG.md` (mục lục `v0.2.0`–`v0.4.0`), `docs/data-dictionary.md` (toàn văn),
  `AGENTS.md`, `.gitignore`, `assets/style.css` (chỉ các khối `.analysis-tab`/`.integration-*`).
- `tests/unit/` các mô-đun còn lại (`test_integration_*` 5 tệp, `test_linkage_*` 4 tệp, `test_*` nhỏ):
  chỉ `grep` khẳng định, không đọc thân test.

**Left out** (không mở):

- `dataset/` (9 CSV gốc + `dataset/external/ibge/`) — dữ liệu gốc bất biến, không phải mã.
- `doc/` (PDF học liệu) — không phải mã ứng dụng; `doc/BT.pdf` là slide ảnh.
- Sản phẩm sinh ra: `data/`, `warehouse/`, `logs/`, `inbox/`, `.tmp-diag/`.
- Môi trường và cache: `.venv/`, `__pycache__/`, `.pytest_cache/`, `.ruff_cache/`.
- Bản cài AI-DLC: `.aidlc/`, `aidlc/`, `.opencode/`, `.claude/`, `.kiro/`, `.codex/`, `.cursor/`.

### Packages Found

- `src.analytics` — thư viện phân tích + kiểm định + mô hình — Python — 6 tệp / 1.578 dòng: lớp truy vấn
  chỉ đọc, năm phép kiểm định, khung báo cáo, bộ phân loại đơn trễ.
- `src.integrate` — tầng mô hình hóa — Python — 9 tệp / 793 dòng: 5 dimension, 4 fact, 2 aggregate,
  kiểm grain/khóa, đối chiếu KPI, catalog 11 view DuckDB.
- `src.dashboard` — tầng trình bày — Python — 6 tệp / 1.322 dòng: 5 tab, 9 callback, 9 output báo cáo.
- `src.pipeline` — điều phối — Python — 8 tệp / 668 dòng: CLI 3 lệnh con, 5 tên tầng, micro-batch,
  manifest, upsert, replay.
- `tests` — kiểm thử — Python — 54 tệp / 10.086 dòng: 49 mô-đun `test_*`, 499 hàm test, 12 hàm `slow`.
- (Ngoài vùng sâu, đo trên đĩa để đối chiếu:) `src.integration` 9/4.138 · `src.linkage` 5/784 ·
  `src.common` 7/551 · `src.clean` 11/437 · `src.quality` 4/440 · `src.ingest` 4/285 ·
  `src.external` 3/177 · `src/config.py` 157 · `src/__init__.py` 3.

Tổng `src/`: **74 tệp Python / 11.333 dòng** (lần quét trước: 70 / 9.444).

### Build System

- **Type**: không có build system. Chạy trực tiếp từ mã nguồn bằng `python -m src.pipeline` /
  `python -m src.dashboard`; phụ thuộc khai trong `requirements.txt` (12 ghim), không lock file,
  không `pyproject.toml`, không `setup.py`, không `Makefile`, không `Dockerfile`.
- **Config Files**: `requirements.txt`, `pytest.ini`, `ruff.toml`, `config.yaml`,
  `config/{mediated-schema,integration-tab,integration-sources}.yaml`, `.github/workflows/ci.yml`,
  `.gitignore`.
- **Build Dependencies**: `setup-python@v5` (3.13, cache pip) → `pip install -r requirements.txt` →
  `ruff check` → `ruff format --check` (danh sách khai tay) → `run --stage all` → `run --stage stats` →
  `pytest -m "not slow"` → `pytest --cov=src --cov-fail-under=80` → smoke nạp
  `config/integration-sources.yaml`.

### APIs Discovered

- **CLI** — `src/pipeline/cli.py::build_parser` — **3 lệnh con** (`run`, `micro-batch`, `replay`), trong đó
  `run --stage` nhận **6 giá trị**: `all|ingest|clean|integrate|analyze|stats`.
- **Hàm Python giữa các tầng** — `AnalyticsService` **9 phương thức** công khai (5 KPI cũ + 4 mới);
  `src.analytics.model` 10 hàm công khai; `src.analytics.statistics` 10 hàm; `src.analytics.report`
  3 hàm (`report_path`, `write_report`, `read_report`) + 11 dataclass.
- **View DuckDB** — `src/integrate/catalog.py::VIEW_TABLES` — **11 view** `v_dim_*`/`v_fact_*`/`v_agg_*`
  trên Parquet.
- **Callback Dash** — `src/dashboard/app.py` 2 callback (9 output) + `src/integration/tab.py`
  `register_callbacks` 6 callback + `src/dashboard/analysis_tab.py::register_callback` 1 callback
  = **9 callback** trong `app.callback_map`.
- **Hợp đồng tệp** — `data/reports/analysis.json` (phiên bản **2**, hai khối `stats` + `model`),
  `data/reports/{ingest,cleaning,quality,reconciliation,integration,kpi-reconciliation,run-summary}.json`,
  `data/integration/linkage-{customer,seller}.json`, `logs/<run_id>.jsonl`, `inbox/manifest.json`.
- **Không có** HTTP/REST/GraphQL API, không endpoint mạng ngoài dashboard localhost.

### Frameworks & Libraries

| Thư viện | Phiên bản | Vai trò |
|---|---|---|
| `pandas` | 2.2.3 | khung dữ liệu, đọc/ghi CSV-Parquet, groupby/merge |
| `pyarrow` | 26.0.0 | engine Parquet |
| `duckdb` | 2.0.0 | kho truy vấn trong tiến trình, view trên Parquet |
| `dash` | 4.4.1 | framework dashboard |
| `plotly` | 7.1.0 | đối tượng đồ thị |
| `PyYAML` | 6.0.2 | đọc `config.yaml` + 3 hợp đồng YAML |
| `pytest` | 9.1.1 | khung kiểm thử |
| `pytest-cov` | 7.1.0 | đo phủ, cưỡng chế 80% trong CI |
| `dash-mantine-components` | 2.8.1 | thành phần UI (tab "Tích hợp" + `dmc.Title`/`dmc.MantineProvider` của tab phân tích) |
| `ruff` | 0.17.4 | lint + format |
| `scipy` | 1.15.2 | **mới**: phân phối chuẩn tắc (Wilson/Newcombe, Fisher z), chi bình phương, `pearsonr` |
| `scikit-learn` | 1.6.1 | **mới**: `LogisticRegression`, `StandardScaler`, `roc_auc_score`, `ConvergenceWarning` |

`numpy` **không ghim** (chỉ bắc cầu qua `pandas` 2.2.3, hiện 2.2.1 — `requirements.txt:23-26` ghi rõ hệ quả).
Không có `statsmodels`, không `xgboost`/`lightgbm`, không `joblib` khai trực tiếp.

### Test Coverage

- **Test Directories**: `tests/unit` (43 mô-đun `test_*.py`), `tests/integration` (5 mô-đun),
  `tests/data_quality` (1 mô-đun), `tests/conftest.py`; thêm 3 `__init__.py`.
- **Test Frameworks**: `pytest` 9.1.1 + `pytest-cov` 7.1.0; marker `slow` khai trong `pytest.ini`;
  `addopts = -ra`. Không có `mock`/`responses`/`hypothesis` — thay bằng `monkeypatch` và DuckDB tạm.
- **Coverage Config**: `pytest-cov` **có ngưỡng nhưng đặt trong CI**, không trong `pytest.ini`
  (`--cov-fail-under=80`, chạy trên **toàn bộ** bộ test). `pytest.ini` không có `--cov`.
- **Đo trên đĩa**: 54 tệp / 49 mô-đun `test_*` / **499** hàm test / **12** hàm đánh dấu `slow` /
  **10.086** dòng. Lần quét trước: 45 / 40 / 353 / 9 / 7.358.

### Code Quality Indicators

- **Linting**: `ruff` 0.17.4, `ruff.toml` (`line-length = 112`, `target-version = "py313"`,
  `select = ["E4","E7","E9","F"]`, `extend-exclude` 8 mục). Năm `per-file-ignores` đều là nợ cũ có ghi chú:
  `F401` cho `src/integrate/connections.py`, `src/integrate/pipeline.py`, `src/pipeline/micro_batch.py`,
  `src/quality/gate.py`; `E402` cho `tests/conftest.py`.
- **CI/CD**: `.github/workflows/ci.yml` — `windows-2022`, Python 3.13, cache pip; trigger
  `push`/`pull_request` trên **3 nhánh** `main`, `feature/update-ui-ux`, `feature/analysis-and-models`;
  7 bước (cài → lint/format → `run --stage all` → `run --stage stats` → test nhanh → phủ 80% → smoke nguồn).
  Không có bước build/đóng gói/deploy.
- **Documentation**: `README.md` 11 mục (kiến trúc, cài đặt, chạy pipeline, dashboard **5 tab**, micro-batch,
  replay, test, lint, CI, KPI baseline, lưu ý); `CHANGELOG.md` bốn mốc `v0.1.0`–`v0.4.0`; `docs/` ba tệp
  (`data-dictionary.md` mô tả **11 bảng mart**, `runbook.md`, `3v.md`); docstring một dòng ở đầu mô-đun/hàm;
  **0** `TODO`/`FIXME`/`HACK` trong `src/`.
- **Điểm yếu đã thấy**: `docs/data-dictionary.md` **không** mô tả `data/reports/analysis.json`, không mô tả
  `v_*` (chỉ 11 bảng mart), và `fact_orders` ở tài liệu cũng **không** có mốc bàn giao cho đơn vị vận chuyển
  — khớp với mã, lệch với nhu cầu của intent này.

### Technical Debt Signals

| Dấu hiệu | Vị trí | Ghi chú |
|---|---|---|
| Cùng một sự thật khai nhiều nơi | `src/ingest/schemas.py`, `src/integrate/validate.py` (`EXPECTED`), `src/integrate/reconcile.py` (`BASELINE`), `src/analytics/model.py` (`EXPECTED_DELIVERED`/`EXPECTED_LATE`), `README.md`, test tích hợp | **Nay thêm một chỗ**: baseline 96.478/7.826 xuất hiện lần thứ ba trong `model.py:22-23` |
| `STAGES` lệch báo cáo tầng | `src/pipeline/stages.py:24` (`STAGES` 5 tên) so với `_run_all` (`:102-173`, **6** `StageResult`) | `--stage all` **không** chạy tầng `stats`; `stats` chỉ chạy khi gọi đích danh |
| Import thừa tạo phụ thuộc ngược | `src/integrate/pipeline.py:10` (`AnalyticsService`), miễn trừ `ruff.toml:27` | Vẫn nguyên; nay nặng hơn vì `analytics` đã lớn gấp 5 |
| Manifest đánh `success` trước khi qua cổng | `src/pipeline/micro_batch.py:146` so với `:149-158`; `src/pipeline/manifest.py:30-35` | Batch fail sau upsert vẫn bị `skipped` ở lần chạy lại |
| Trạng thái toàn cục trong dashboard | `src/dashboard/app.py:50` `_INTEGRATION_RUNS`, `:505-508` `reset_integration_logs` | Test phải gọi reset; hành vi phụ thuộc thứ tự |
| Đầu ra theo vị trí | `src/dashboard/app.py:511-589` tuple **9** phần tử ở cả hai nhánh | Thêm output phải sửa 2 chỗ + 3 test |
| Hằng số ma thuật / số chép tay | `src/dashboard/app.py:530` (`"2017-01"`), `src/dashboard/components.py:108` ("329 đơn"), `:99` nút "Thử lại" không có callback | Vẫn nguyên |
| Hai output vẽ cùng một figure | `src/dashboard/app.py:563-564` (`category-bar` và `category-detail-bar`) | Vẫn nguyên |
| Bắt lỗi rộng ở biên | `src/dashboard/app.py:93-94`, `:531-544`; `src/dashboard/analysis_tab.py:556-557`; `src/external/ibge.py`; `src/integrate/connections.py:26-29` | Lỗi cấu hình bị hiển thị thành "không có dữ liệu" |
| Kiểm tra thân thiện định dạng khai tay | `.github/workflows/ci.yml` danh sách `ruff format --check` (35 mục) | Tệp mới quên thêm là không được kiểm; `tests/unit/test_ci_config.py` canh việc này |
| Kiểm tra phụ thuộc vào dữ liệu sinh ra | `tests/unit/test_dashboard_smoke.py:114,121,127,136` gọi `load_config()` của repo; `tests/unit/test_cli.py:20-21` | Bộ "nhanh" vẫn chưa hermetic; CI che bằng `run --stage all` + `run --stage stats` trước khi test |

### Trạng thái cây làm việc (bắt buộc ghi lại)

Commit đầu là `ea77bdf` nhưng **cây làm việc đang khác commit đó**: 23 mục đã sửa (11 tệp thuộc dự án + 12 tệp
trong workspace AI-DLC) và 18 mục chưa được theo dõi (13 trong số đó là tệp mã/test của dự án). Lần quét này
mô tả **cây làm việc trên đĩa**, không mô tả commit:

- Sửa (11 tệp dự án): `.github/workflows/ci.yml`, `CHANGELOG.md`, `README.md`, `assets/style.css`,
  `requirements.txt`, `src/analytics/service.py`, `src/dashboard/app.py`, `src/pipeline/cli.py`,
  `src/pipeline/stages.py`, `tests/integration/test_u3_end_to_end.py`,
  `tests/unit/test_dashboard_smoke.py` (cộng 12 tệp `aidlc/**`: 9 tệp codekb, `intents.json`, 2 tệp memory).
- Mới (chưa commit, 4 tệp mã): `src/analytics/{model,report,statistics}.py`, `src/dashboard/analysis_tab.py`.
- Mới (chưa commit, 8 tệp test): `tests/integration/{test_u1_stats_end_to_end,test_u2_model_end_to_end}.py`,
  `tests/unit/{test_analytics_model,test_analytics_report,test_analytics_statistics,test_ci_config,test_dashboard_analysis_tab,test_analysis_tab_contrast,test_pipeline_stages}.py`.
- Nhánh: `feature/analysis-and-models` (đi trước `main` 1 commit).

Hệ quả: nội dung các tệp trên **chưa** nằm trong `ea77bdf`. Fingerprint của khối Scope of Analysis băm
trạng thái **trên đĩa**, nên nó vẫn đúng cho lần đối chiếu sau, nhưng một người đọc commit `ea77bdf` sẽ
thấy mã khác.

## Handoff Summary

### Packages, tiến trình và hình dạng

- Hệ thống vẫn là **monolith theo tầng chạy batch**, một tiến trình, trao đổi giữa tầng bằng Parquet trên
  đĩa; DuckDB chỉ giữ **view**; dashboard là mặt phẳng duy nhất có mạng (localhost).
- Hai đường dữ liệu song song vẫn tồn tại: `dataset → … → marts → DuckDB → analytics → dashboard` và nhánh
  `dataset CSV → src.integration → tab "Tích hợp"`. Intent này đi trên **đường thứ nhất**.

### Intent-relevant finding (những điều đợt này sẽ chạm, kèm bằng chứng)

1. **`AnalyticsService` dựng khung huấn luyện ở grain ĐƠN, không phải grain dòng hàng.**
   `TRAINING_FRAME_SQL` (`src/analytics/service.py:38-74`) gộp `v_fact_order_items` về một dòng mỗi đơn
   (`item_count`, `item_total = SUM(item_total)`, `item_price_max = MAX(price)`) và `v_fact_payments` về một
   dòng mỗi đơn (`MAX(payment_installments)`, `payment_type` của `payment_sequential = 1`), rồi
   `LEFT JOIN` vào `v_fact_orders` + `v_dim_customer` + `v_dim_date`. `training_frame()`
   (`service.py:377-387`) chỉ đọc `TRAINING_FRAME_SQL` và **ném `ValueError` khi `order_id` bị lặp**.
   Không có `seller_id`, không có `shipping_limit_date`, không có mốc bàn giao cho đơn vị vận chuyển.
   → Đổi sang **đơn vị dòng hàng** là đổi hẳn truy vấn này, không phải thêm cột.

2. **Danh sách đặc trưng và danh sách cấm đều là hằng số có kích thước cố định.**
   `src/analytics/model.py:36-70`: `CATEGORICAL_FEATURES` 5 (`payment_type`, `customer_state`,
   `customer_region`, `purchase_month`, `purchase_weekday`), `NUMERIC_FEATURES` 4 (`item_count`,
   `item_total`, `item_price_max`, `payment_installments`), `FLAG_FEATURES` 2 (`has_items`, `has_payment`),
   `FEATURES` **11** tên, `FORBIDDEN_COLUMNS` **10** tên:
   `order_delivered_customer_date`, **`order_delivered_carrier_date`**, `delivery_days`, `is_late`,
   `late_days`, `review_score`, `review_comment_title`, `review_comment_message`, `is_delivered`,
   `has_review`.
   `validate_features()` (`:87-100`) còn **buộc đúng 11 cột** (`len(features) != len(FEATURES)` → lỗi).
   → Hai cản trở trực tiếp cho intent: (a) `order_delivered_carrier_date` đang bị cấm, trong khi khung dự
   đoán mới lấy chính nó làm mốc quan sát; (b) luật "đúng 11 cột" chặn mọi việc thêm bớt đặc trưng.

3. **Baseline của mô hình là hằng số grain đơn.** `EXPECTED_DELIVERED = 96_478`,
   `EXPECTED_LATE = 7_826` (`model.py:22-23`), được `delivered_population()` (`:103-119`) dùng để **từ chối**
   khung lệch chuẩn; `split_frame` cắt tại `SPLIT_DATE = "2018-04-01"` và **đơn rơi đúng ngày cắt thuộc tập
   kiểm tra** (`:140-156`); `split_summary` (`:159-179`) buộc `train_end < test_start` và
   `train_n + test_n == 96_478`. → Đổi đơn vị dự đoán là đổi cả bốn hằng số/ba luật này.

4. **Mart không có cột mốc bàn giao, và `v_fact_order_items` không có bang người bán.**
   `FactBuilder.build_orders` (`src/integrate/facts.py:69-115`) trả đúng 13 cột — danh sách ở `:99-115` —
   gồm `order_delivered_customer_date` và `order_estimated_delivery_date` nhưng **không** có
   `order_delivered_carrier_date` lẫn `order_approved_at`, dù cleaned orders có cả hai
   (`src/clean/orders.py:9-15`). `build_order_items` (`facts.py:27-42`) trả 12 cột có `seller_id` nhưng
   **không** có `seller_state`, và **làm rơi** `shipping_limit_date` (có trong `TABLE_SPECS["order_items"]`,
   `src/ingest/schemas.py:37-51`). `dim_seller` có `state`/`region`, `dim_product` chỉ giữ 4 cột danh mục
   (không còn `product_weight_g`/kích thước). → U1 của intent ("thêm 2 cột mốc vào `v_fact_orders`, thêm
   `seller_state` vào `v_fact_order_items`") là thay đổi **builder**, không phải thay đổi truy vấn; tên bảng
   và số view (11) giữ nguyên, `StarSchemaValidator.EXPECTED` (`src/integrate/validate.py:12-22`) cũng giữ
   nguyên vì số dòng không đổi.

5. **Tab thứ năm đã tồn tại và đang được khai là "chỉ đọc, không ô nhập".**
   `src/dashboard/analysis_tab.py` dựng ba khối `tom-tat|thong-ke|mo-hinh` (`SECTION_IDS`, `:42-47`); bốn thẻ
   tóm tắt `ti-le-tre|so-don|so-bo-qua|auc` (`CARD_IDS`, `:47`); một callback duy nhất
   `Output("analysis-result", "children")` trên `Input("tabs", "value")` (`:561-566`) và
   `render_analysis` trả `no_update` khi tab khác được chọn (`:548-558`). Hai câu chữ đang chặn đường:
   `TEXTS["model_caption"] = "Chỉ đọc: tab hiện đúng ngưỡng đã báo cáo, không chọn lại được"` (`:58`) và
   test `tests/unit/test_dashboard_analysis_tab.py:456-463`
   (`test_model_block_offers_no_input_control`) khẳng định khối `mo-hinh` **không** chứa
   `Slider`/`Input`/`RangeSlider`. → U3 của intent (vùng nhập liệu dự đoán) **mâu thuẫn** với cả câu chữ,
   test, và README mục Dashboard (`README.md:101-105`).

6. **Báo cáo là hợp đồng phiên bản 2 với 7 trường mô hình.** `REPORT_VERSION = 2`,
   `REPORT_FILE_NAME = "analysis.json"` (`src/analytics/report.py:15-16`); `ModelBlock` có đúng 7 trường
   `target, split, auc, threshold, precision, recall, counts` (`:190-211`) và `_model_block` (`:457-468`)
   **từ chối** tệp thiếu trường. `counts` đang mang `flagged`, `not_flagged`, `total`, `threshold_method`,
   `auc_below_target`. `read_report` trả bốn trạng thái `rong|day-du|mot-phan|loi` (`:25-29`) và
   `report.py` ghi **một lần duy nhất** (`:248-267`). → Lưu mô hình + thêm số liệu (baseline AUC, AUC cây)
   là thay đổi **phiên bản tệp** hoặc **bộ trường**, và mọi reader (`analysis_tab`, test) phải theo.

7. **Tầng `stats` là nơi duy nhất ghi báo cáo, và nó không nằm trong `--stage all`.**
   `STAGES = ("ingest", "clean", "integrate", "analyze", "stats")` (`src/pipeline/stages.py:24`) nhưng
   `_run_all` (`:91-179`) chạy ingest → clean → quality → integrate → linkage → analyze rồi ghi **6**
   `StageResult`, **không** chạy `stats`. Nhánh `stats` (`:241-259`) dựng báo cáo bằng
   `build_analysis_report` rồi `train_model`, `replace(report, model=model)`, `write_report`. CI gọi
   `run --stage stats` thành bước riêng sau `--stage all`.

8. **Không có chỗ nào lưu mô hình.** Không có `models_dir` trong `AppConfig` (34 trường,
   `src/config.py:15-52`), không có `joblib`/`pickle` trong `src/`, không có `data/models/` trong
   `.gitignore` lẫn `config.yaml`. → "Lưu mô hình vào `data/models/`" là thêm trường cấu hình + tạo thư mục
   + ghim/khai báo cách tuần tự hóa.

9. **Ngưỡng chất lượng hiện có: AUC ≥ 0,70 và cờ `auc_below_target`.** `AUC_TARGET = 0.70`,
   `THRESHOLD_METHOD = "max_f1_on_test_grid005"`, `THRESHOLD_GRID` 19 điểm 0,05…0,95
   (`model.py:25-27`); `choose_threshold` hoà thì **chọn ngưỡng cao hơn** (`:241-243`);
   `build_model_block` làm tròn 4 chữ số **trước** khi tính cờ (`:272-296`). Số thật trên dữ liệu đã giao:
   AUC **0,5133**, ngưỡng 0,40, precision 0,0866, recall 0,2645 (khẳng định trong
   `tests/integration/test_u3_end_to_end.py:116-118` và `tests/unit/test_dashboard_analysis_tab.py:461-463`).

10. **Câu chữ người dùng và trạng thái giao diện bằng tiếng Việt, số theo định dạng Brazil.**
    `src/dashboard/formatting.py:27-30` (`format_percent` **không** nhân 100 — `analysis_tab` tự nhân, xem
    `:191`), `assets/style.css` phải chứa **mọi** lớp mà tab dùng
    (`tests/unit/test_dashboard_analysis_tab.py:485-490`) và khối `.analysis-tab` không được dùng
    `--text-3` (`tests/unit/test_analysis_tab_contrast.py:64-66`).

### Risks / follow-up (những sự thật tầng sau phải giữ)

- **Mâu thuẫn cần giải quyết tường minh, không được làm mờ:**
  (a) `FORBIDDEN_COLUMNS` cấm `order_delivered_carrier_date` — chính là mốc của khung dự đoán mới;
  (b) `validate_features` buộc đúng 11 đặc trưng;
  (c) `test_model_block_offers_no_input_control` + `TEXTS["model_caption"]` + README cấm vùng nhập liệu
  trên tab phân tích;
  (d) `EXPECTED_DELIVERED`/`EXPECTED_LATE` là hằng grain đơn;
  (e) `--stage all` không chạy `stats` trong khi `STAGES` có `stats`.
- **Hợp đồng không được đổi số:** 5 KPI baseline (`src/integrate/reconcile.py:8-22`), số dòng 9 bảng nguồn
  (`src/ingest/schemas.py`), 9 bảng mart (`StarSchemaValidator.EXPECTED`), **11 view**
  (`VIEW_TABLES`, `tests/integration/test_u2_end_to_end.py:44`).
- **Hình dạng giao diện là hợp đồng cứng:** 5 tab / 9 callback
  (`tests/unit/test_dashboard_smoke.py:57,62`; `tests/integration/test_u3_end_to_end.py:83,87`), 9 output
  (`tests/unit/test_dashboard_smoke.py:115`), 6 callback riêng của tab "Tích hợp"
  (`tests/unit/test_integration_tab.py:938`), 3 lệnh con CLI
  (`tests/unit/test_pipeline_stages.py:157-161`).
- **Ba tệp khai cùng một danh sách tệp format:** thêm tệp mới thì phải thêm vào
  `ruff format --check` trong `ci.yml` **và** vào `NEW_FILES` của `tests/unit/test_ci_config.py:14-29`.
- **Ngân sách thời gian đã thành test**: `tests/integration/test_u1_stats_end_to_end.py:48` (300 s),
  `test_u2_model_end_to_end.py:31-32` (900 s cho tầng và 900 s cho riêng bước mô hình) — mọi thay đổi làm
  bước mô hình chậm hơn đáng kể sẽ đỏ ở đây.
- **Tính lặp lại đã thành test**: `test_u2_model_end_to_end.py:95` khẳng định hai lần huấn luyện cho cùng
  bốn chỉ số đã làm tròn; `test_u1_stats_end_to_end.py:122-129` khẳng định hai lần chạy `stats` cho cùng
  tệp sau khi bỏ `generated_at`.
- **`MemoryProbe` nay có người dùng** (`test_u1_stats_end_to_end.py:16,40-49`) — nợ `TD-04` chỉ còn phần
  `memory_warn_mb` chưa ai đọc. Prior CodeKB nói "không được tham chiếu ở đâu" → đã lỗi thời.
