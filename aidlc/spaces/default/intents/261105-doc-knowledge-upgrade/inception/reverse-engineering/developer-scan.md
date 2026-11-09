## Developer Code Scan Results

### Scan Coverage

- **Analyzed deeply** (đọc từng tệp, hiểu và ghi lại):
  - `src/config.py`
  - `src/common/` (`exceptions.py`, `io.py`, `logging.py`, `memory.py`, `types.py`)
  - `src/ingest/` (`schemas.py`, `reader.py`, `reports.py`)
  - `src/clean/` (`common.py`, `orders.py`, `customers.py`, `sellers.py`, `products.py`, `items.py`, `payments.py`, `reviews.py`, `geolocation.py`, `pipeline.py`)
  - `src/quality/` (`checks.py`, `gate.py`, `allowlist.py`)
  - `src/external/` (`ibge.py`, `region.py`)
  - `src/integrate/` (`dimensions.py`, `facts.py`, `aggregates.py`, `validate.py`, `reconcile.py`, `catalog.py`, `connections.py`, `pipeline.py`)
  - `src/analytics/` (`service.py`, `filters.py`)
  - `src/dashboard/` (`app.py`, `components.py`, `formatting.py`, `__main__.py`)
  - `src/pipeline/` (`cli.py`, `stages.py`, `micro_batch.py`, `manifest.py`, `upsert.py`, `replay.py`, `__main__.py`)
  - `tests/conftest.py` và toàn bộ `tests/unit/`, `tests/integration/`, `tests/data_quality/`
  - `config.yaml`, `requirements.txt`, `pytest.ini`, `README.md`, `AGENTS.md`, `.gitignore`
  - `docs/runbook.md`, `docs/data-dictionary.md`, `docs/3v.md`
  - `assets/style.css`
  - `dataset/external/ibge/estados.json`, `dataset/external/ibge/metadata.json`
- **Skimmed only**:
  - `dataset/` — chỉ nắm bố cục 9 CSV, tên cột và số dòng kỳ vọng từ `src/ingest/schemas.py`, `AGENTS.md`, `docs/3v.md`; không mở nội dung CSV.
  - `doc/` — ghi nhận học liệu PDF (`Projects.pdf` là đề bài, các `*_SchemaAlignment/RecordLinkage/QueryProcessing/SourcesSelection`), `Quiz_DI.md`, `doc/quiz/`; không trích xuất nội dung PDF.
  - `data/`, `warehouse/`, `logs/`, `inbox/` — chỉ liệt kê tên tệp để xác nhận bố cục đầu ra; không đọc nội dung Parquet/JSON/JSONL.
- **Left out** (không mở, theo "What to Skip" và yêu cầu của lần quét):
  - `.venv/`
  - `__pycache__/` (mọi cấp)
  - `.pytest_cache/`
  - `.coverage`
  - `.git/`
  - `.aidlc/`, `aidlc/`, `.opencode/` (bản cài AI-DLC, không thuộc dự án)
  - `data/raw/`, `data/cleaned/`, `data/marts/`, `data/reports/`, `data/.tmp/` (sản phẩm sinh ra)
  - `warehouse/`, `logs/`, `inbox/` (sản phẩm sinh ra, bị `.gitignore`)

### Packages Found

- `src` — package Python (namespace ứng dụng) — Python 3.13 — gốc mã nguồn
- `src.common` — thư viện dùng chung — Python — IO nguyên tử, log, dataclass, ngoại lệ
- `src.config` — mô-đun cấu hình — Python — `AppConfig`, `load_config`
- `src.ingest` — tầng ETL — Python — hợp đồng lược đồ + đọc CSV + raw Parquet
- `src.clean` — tầng ETL — Python — chuẩn hóa + gắn cờ chất lượng
- `src.quality` — cổng kiểm soát — Python — 21 check + 9 count + 10 anomaly
- `src.external` — tích hợp nguồn ngoài — Python — IBGE 27 bang → 5 vùng
- `src.integrate` — mô hình hóa — Python — star schema + DuckDB catalog
- `src.analytics` — truy vấn — Python — 5 truy vấn chỉ đọc
- `src.dashboard` — trình bày — Python — Dash 3 tab, 2 callback
- `src.pipeline` — điều phối — Python — CLI, micro-batch, replay
- `tests` — kiểm thử — Python — unit + integration + data_quality

### Build System

- **Type**: pip + `requirements.txt` (không có `pyproject.toml`, `setup.py`, Makefile, Docker)
- **Config Files**: `requirements.txt` (8 ghim), `pytest.ini` (`testpaths = tests`, marker `slow`, `addopts = -ra`), `config.yaml` (cấu hình chạy)
- **Build Dependencies**: `python -m src.pipeline` và `python -m src.dashboard` chạy trực tiếp từ mã nguồn; `pyarrow` là engine ghi Parquet; `duckdb` là kho truy vấn; `dash`/`plotly` là runtime giao diện; không có bước biên dịch/đóng gói

### APIs Discovered

- CLI — `src/pipeline/cli.py` — 3 lệnh con (`run`, `micro-batch`, `replay`), 5 tùy chọn
- Python API nội bộ — 18 điểm vào công khai trên 10 gói (chi tiết: `api-documentation.md`)
- Kho dữ liệu SQL — `src/integrate/catalog.py` — 11 view DuckDB (`v_dim_*`, `v_fact_*`, `v_agg_*`)
- Callback Dash — `src/dashboard/app.py` — 2 callback, 9 output
- **Không có** HTTP/REST/GraphQL API, không có endpoint mạng do dự án tự phục vụ

### Frameworks & Libraries

- `pandas` — 2.2.3 — thao tác dữ liệu toàn pipeline
- `pyarrow` — 26.0.0 — engine Parquet
- `duckdb` — 2.0.0 — kho truy vấn trong tiến trình
- `dash` — 4.4.1 — framework dashboard
- `plotly` — 7.1.0 — đồ thị
- `PyYAML` — 6.0.2 — đọc `config.yaml`
- `pytest` — 9.1.1 — kiểm thử
- `pytest-cov` — 7.1.0 — đo độ phủ (không cấu hình ngưỡng)

### Test Coverage

- **Test Directories**: `tests/unit`, `tests/integration`, `tests/data_quality` (+ `tests/conftest.py`)
- **Test Frameworks**: `pytest` (marker `slow`), fixture DataFrame nhỏ + `real_config` trỏ `dataset/` thật
- **Coverage Config**: **absent** — không ngưỡng, không CI; `.coverage` chỉ tồn tại cục bộ và bị `.gitignore`
- **Số lượng**: 47 hàm test trên 25 mô-đun; 6 hàm `slow`
- **Thiếu**: không có test đơn vị cho `src/analytics/service.py`, `src/integrate/{validate,reconcile,catalog,connections}.py`, `src/pipeline/{stages,micro_batch}.py` (nhánh lỗi), `src/quality/checks.py`; `run_all` (`--stage all`) không được test

### Code Quality Indicators

- **Linting**: **không có** (`ruff`/`flake8`/`mypy`/`pyproject.toml`/`.pre-commit-config.yaml` đều vắng)
- **CI/CD**: **không có** pipeline nào (không `.github/workflows`, không `.gitlab-ci.yml`)
- **Documentation**: `README.md` đầy đủ (kiến trúc, lệnh, KPI, lưu ý), `docs/` có từ điển dữ liệu + runbook + 3V; docstring trong mã ở mức một dòng/mô-đun, không mô tả tham số; `README.md` còn tham chiếu chết tới `aidlc-docs/`
- **Kích thước/tổ chức**: 55 tệp `src/`, hàm thường ngắn; ngoại lệ `QualityGate.run` (~245 dòng), `build_layout` (~170 dòng), `build_dashboard_outputs` (~80 dòng)
- **Thực hành tốt**: ghi tệp nguyên tử, SQL tham số hóa, cây ngoại lệ theo tầng, log JSONL có `run_id`, 0 TODO/FIXME/HACK

### Technical Debt Signals

- **Manifest micro-batch đánh dấu `success` trước quality gate** → batch fail sau upsert bị `skipped` khi chạy lại: `src/pipeline/micro_batch.py:146`, `:169-175`; `src/pipeline/manifest.py:30-35`
- **Hằng số dữ liệu lặp 3–6 nơi**: `src/ingest/schemas.py:22-130`, `src/quality/gate.py:188-198`, `src/integrate/validate.py:12-22`, `src/integrate/reconcile.py:8-22`
- **Import thừa tạo phụ thuộc ngược**: `src/integrate/pipeline.py:10` (`AnalyticsService` không dùng)
- **Mã/cấu hình chết**: `src/common/memory.py` (`MemoryProbe` không được gọi), `memory_warn_mb`/`memory_fail_mb` (`src/config.py:45-46`), `src/analytics/filters.py` (shim), `src/clean/products.py:38-43` (rename vô nghĩa)
- **Dashboard trùng lặp/ma thuật**: hai output cùng figure (`src/dashboard/app.py:449-461`), nút "Thử lại" không callback (`components.py:99`), `"2017-01"` và "329 đơn" hard-code
- **8 chỗ `except Exception`**: `src/dashboard/app.py:68,424`; `src/external/ibge.py:56`; `src/integrate/connections.py:28`; `src/pipeline/cli.py:74`, `stages.py:176,227`; `micro_batch.py:169`
- **Test nhanh không hermetic**: `tests/unit/test_dashboard_smoke.py:15,23,30` và `tests/unit/test_cli.py:21` cần `warehouse/olist.duckdb` + `data/marts/` (bị gitignore)
- **Allowlist dị thường gắn chặt phiên bản dữ liệu**: `src/quality/allowlist.py:3-14`

## Handoff Summary

- **Intent-relevant finding**: Hệ thống hiện **chưa có biểu diễn hạng nhất** cho bốn nhóm kiến thức tích hợp
  dữ liệu mà `doc/` yêu cầu. `src/ingest/schemas.py` chỉ *kiểm tra* lược đồ (không có bảng ánh xạ/mediation
  cấu hình được); `src/clean/geolocation.py` chỉ khử trùng lặp + tổng hợp (không có ghép bản ghi mờ);
  `src/analytics/service.py` dựng SQL trực tiếp từ hằng số (không có lớp viết lại truy vấn);
  `src/external/ibge.py` là nguồn ngoài duy nhất (không có sổ đăng ký chọn nguồn). Vì vậy đợt nâng cấp sẽ
  phải **tạo gói/biên giới mới**, không chỉ thêm hàm vào mô-đun sẵn có. Về tab "Tích hợp": `src/dashboard/app.py`
  đang có đúng 3 `dcc.Tab` trong `build_layout` (dòng 275-351) và `build_dashboard_outputs` trả **tuple 9 phần tử**
  (cả nhánh lỗi, dòng 427-437); ba test khẳng định số lượng cứng sẽ fail khi thêm tab/output:
  `tests/unit/test_dashboard_smoke.py:14-19` (3 tab, 2 callback), `:22-26` (9 output),
  `tests/integration/test_u3_end_to_end.py:48` (2 callback).

- **Risks / follow-up**:
  1. **Hợp đồng hồi quy cứng** — số dòng 9 bảng, 10 bộ đếm allowlist và 5 KPI baseline được khẳng định trong
     mã và test; mọi thay đổi cleaning/ghép bản ghi sẽ làm `quality full` hoặc `KpiReconciler` fail
     (`src/integrate/reconcile.py:48-56`, `src/quality/gate.py:296-304`). Cần quyết định: cập nhật baseline
     có kiểm soát hay chạy tầng mới song song.
  2. **Thêm view/bảng phải sửa ≥ 10 điểm** (`src/ingest/schemas.py`, `src/clean/pipeline.py`, `src/quality/gate.py`,
     `src/quality/allowlist.py`, `src/integrate/{pipeline,validate,catalog}.py`, `src/pipeline/{stages,micro_batch}.py`,
     `tests/conftest.py`); test `tests/integration/test_u2_end_to_end.py:44` khẳng định đúng 11 view.
  3. **Phụ thuộc ngoài cho ghép bản ghi mờ chưa có** trong `requirements.txt`; nếu thêm, phải tạo venv + cập nhật
     requirements (ghi chú `AGENTS.md`: môi trường toàn cục không đủ gói), đồng thời giữ UTF-8 khi chạy.
  4. **Lỗi idempotency micro-batch (`TD-01`)** — nếu tab mới minh họa nạp tăng dần, lỗi này sẽ lộ khi trình diễn;
     nên sửa trước.
  5. **Bộ test nhanh phụ thuộc `warehouse/olist.duckdb` và `data/marts/`** (bị `.gitignore`) — build/test trên
     bản clone sạch sẽ đỏ nếu không dựng trước mart hoặc cô lập fixture.
  6. **DuckDB giữ đường dẫn tuyệt đối trong view** — đổi `workspace_root` (worktree, thư mục khác) phải chạy lại
     `integrate` trước khi mở dashboard; đồng thời dashboard read-only có thể tranh chấp khóa với `integrate`
     (`docs/runbook.md` đã ghi).
  7. **Không có CI/lint/type-check/ngưỡng phủ** — mọi chốt chất lượng hiện dựa vào 47 test và kỷ luật con người.
