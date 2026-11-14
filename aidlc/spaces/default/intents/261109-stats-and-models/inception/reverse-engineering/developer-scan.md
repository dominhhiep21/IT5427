## Developer Code Scan Results

Quét tập trung (focused) trên năm đường dẫn của intent `261109-stats-and-models`, tại head commit
`ea77bdf88d1431de11c36e1b739972bd594063f0`. Chỉ đọc mã và cấu hình; **không** chạy test, build hay
chương trình của dự án.

### Scan Coverage

**Analyzed deeply** (đọc toàn bộ nội dung từng tệp):
- `src/analytics/service.py` (281 dòng) — 5 truy vấn chỉ đọc, dựng mệnh đề `WHERE` từ `KpiFilters`
- `src/analytics/filters.py` (7 dòng) — shim re-export `KpiFilters`
- `src/analytics/__init__.py` (1 dòng)
- `src/pipeline/cli.py` (81 dòng) — `build_parser`, `main`, ba lệnh con
- `src/dashboard/app.py` (575 dòng) — `build_layout`, `create_app`, 2 callback báo cáo, `build_dashboard_outputs`
- `src/dashboard/components.py` (111 dòng) — `kpi_strip`, `chart_card`, `empty_figure`, `error_banner`, `sparse_badge`
- `src/dashboard/formatting.py` (39 dòng) — định dạng số/tiền/%/ngày kiểu Brazil
- `src/dashboard/__main__.py` (16 dòng), `src/dashboard/__init__.py` (1 dòng)
- `tests/conftest.py` (361 dòng) — fixture `config`, `real_config`, `small_*`, `region_map`, `small_cleaned`
- `tests/unit/` — 36 mô-đun (gồm `test_dashboard_smoke.py`, `test_cli.py`, `test_formatters.py`,
  `test_filters.py`, `test_common_kpis.py`, `test_log_pruning.py`, `test_integration_*.py` 8 mô-đun,
  `test_linkage_*.py` 4 mô-đun, `test_clean_*`/`test_dimensions`/`test_facts`/`test_aggregates`/
  `test_quality_gate`/`test_config`/`test_io`/`test_manifest`/`test_upsert`/`test_ibge_client`/
  `test_region_mapper`/`test_geolocation`/`test_schema`)
- `tests/integration/` — 3 mô-đun end-to-end (`test_u1`, `test_u2`, `test_u3`)
- `tests/data_quality/test_real_dataset.py` — 3 baseline trên CSV thật
- `requirements.txt` (13 dòng, 10 gói ghim)

**Skimmed only** (đọc để lấy ngữ cảnh, không tính vào `analyzed.paths`):
- `src/config.py` (157 dòng) — đọc toàn bộ để biết 34 trường `AppConfig` và danh sách thư mục được tạo
- `src/pipeline/stages.py` (252 dòng) — đọc toàn bộ để hiểu hành vi `run --stage` và `StageResult`
- `src/common/types.py` (139), `src/common/kpis.py` (108), `src/common/exceptions.py` (66) — hợp đồng dữ liệu,
  sổ KPI, cây ngoại lệ
- `src/integrate/pipeline.py` — chỉ đọc khối import (dòng 1–26) để xác nhận `import` thừa `→ analytics`
- `src/quality/gate.py` — chỉ đọc khối import
- `src/integration/tab.py` (1.380 dòng), `src/integration/card.py` (348 dòng) — chỉ đọc danh mục định nghĩa
  công khai (`CARD_TITLES`, `SCREENS`, `STATE_*`, `IntegrationTab`, `register_callbacks`, `TabConfig`);
  thân hàm không đọc
- `src/integration/{models,schema,load,query,rewrite,selector}.py`, `src/linkage/*` — mức cấu trúc: số tệp,
  số dòng, tên định nghĩa lấy từ `grep`
- `config.yaml` (45), `config/integration-tab.yaml` (13), `pytest.ini` (5), `ruff.toml` (29),
  `.github/workflows/ci.yml` (51), `CHANGELOG.md` (30), `README.md` (grep theo mục), `.gitignore`
- `dataset/external/ibge/estados.json` — chỉ biết là hợp đồng 27 bang qua test, không mở lại

**Left out** (không mở theo "What to Skip" và theo brief):
- `dataset/` (9 CSV nguồn — dữ liệu, không phải mã), `doc/` (PDF học liệu, quiz)
- Sản phẩm sinh ra: `data/`, `warehouse/`, `logs/`, `inbox/`
- Môi trường/cache: `.venv/`, `__pycache__/`, `.pytest_cache/`, `.ruff_cache/`, `.tmp-diag/`
- `assets/style.css` — không mở trong lần này (đã đọc ở lần quét trước; chỉ được dashboard trỏ tới)
- Bản cài AI-DLC: `.aidlc/`, `aidlc/`, `.opencode/`, `.claude/`, `.codex/`, `.cursor/`, `.kiro/`
  (trừ `.github/workflows/ci.yml` của dự án, đã đọc)

### Packages Found

- `src` — package ứng dụng (thư viện + điểm vào CLI) — Python — 12 gói con, 70 mô-đun, 9.444 dòng
- `tests` — bộ kiểm thử — pytest — 45 tệp (40 mô-đun test), 7.358 dòng, 353 hàm test
- `config/` — hợp đồng cấu hình YAML (`mediated-schema.yaml`, `integration-tab.yaml`,
  `integration-sources.yaml`) — dữ liệu cấu hình, không phải mã
- `assets/` — CSS chủ đề — tài nguyên tĩnh

### Build System

- **Type**: không có hệ thống build; chạy trực tiếp từ mã nguồn bằng `python -m`, cài phụ thuộc bằng `pip`
- **Config Files**: `requirements.txt`, `pytest.ini`, `ruff.toml`, `config.yaml`, `config/*.yaml`,
  `.github/workflows/ci.yml`
- **Build Dependencies**: không có (không `pyproject.toml`, `setup.py`, `Makefile`, lock file)

### APIs Discovered

- CLI — `src/pipeline/cli.py` — 3 lệnh con: `run` (`--stage`, `--refresh-ibge`), `micro-batch` (`--inbox`),
  `replay` (`--batches`)
- API Python nội bộ — `src/analytics/service.py::AnalyticsService` — 5 phương thức
  (`kpi_summary`, `revenue_by_period`, `revenue_by_dimension`, `top_entities`, `delivery_kpis`)
- View DuckDB — 11 (`v_dim_*` ×5, `v_fact_*` ×4, `v_agg_*` ×2), tạo bởi `src/integrate/catalog.py`
- Callback Dash — 8 (2 của ba tab báo cáo + 6 của tab "Tích hợp")
- Hợp đồng tệp — báo cáo JSON trong `data/reports/`, kết quả tích hợp trong `data/integration/`,
  nhật ký JSONL trong `logs/`, `inbox/manifest.json`

### Frameworks & Libraries

- `pandas` 2.2.3 — khung dữ liệu, đọc/ghi CSV–Parquet
- `pyarrow` 26.0.0 — engine Parquet
- `duckdb` 2.0.0 — kho truy vấn trong tiến trình (chỉ view)
- `dash` 4.4.1 — dashboard; `dash-mantine-components` 2.8.1 — thành phần UI của tab "Tích hợp"
- `plotly` 7.1.0 — đối tượng đồ thị
- `PyYAML` 6.0.2 — đọc cấu hình YAML
- `pytest` 9.1.1 + `pytest-cov` 7.1.0 — kiểm thử, đo phủ
- `ruff` 0.17.4 — lint + format
- **Không có** thư viện thống kê hay học máy nào (`numpy`, `scipy`, `statsmodels`, `scikit-learn`
  không được ghim và không được import ở đâu — `grep` trên toàn repo không có kết quả)

### Test Coverage

- **Test Directories**: `tests/unit/` (36 mô-đun), `tests/integration/` (3), `tests/data_quality/` (1)
- **Test Frameworks**: `pytest` 9.1.1, marker `slow` (`pytest.ini`), `pytest-cov` 7.1.0
- **Coverage Config**: không có trong `pytest.ini`; ngưỡng 80% được cưỡng chế **trong CI**
  (`pytest --cov=src --cov-fail-under=80` trên toàn bộ bộ test, không chỉ bộ nhanh)

### Code Quality Indicators

- **Linting**: `ruff` 0.17.4 với `ruff.toml` (`line-length = 112`, `target-version = "py313"`,
  `select = ["E4","E7","E9","F"]`, 4 `per-file-ignores` F401/E402 cho nợ cũ)
- **CI/CD**: `.github/workflows/ci.yml` — `windows-2022`, Python 3.13: cài phụ thuộc → `ruff check .` →
  `ruff format --check` trên mã của đợt này → `python -X utf8 -m src.pipeline run --stage all` (dựng dữ liệu)
  → `pytest -m "not slow"` → `pytest --cov=src --cov-fail-under=80` → smoke nạp `config/integration-sources.yaml`
- **Documentation**: docstring một dòng đầu mô-đun/hàm; `README.md` mô tả 4 tab; `CHANGELOG.md` có mục
  `v0.1.0`; `docs/` 3 tệp (không mở lại lần này)

### Technical Debt Signals

- `src/dashboard/app.py:549-550` — hai output (`category-bar`, `category-detail-bar`) nhận **cùng một**
  đối tượng figure; tab "Tổng quan" và tab "Danh mục" vẽ trùng nội dung.
- `src/dashboard/app.py:516` — hằng số ma thuật `"2017-01"` cắt chuỗi tháng bằng so sánh chuỗi.
- `src/dashboard/components.py:99` — nút "Thử lại" có `id="retry-button"` nhưng không callback nào nhận.
- `src/dashboard/components.py:108` — câu cứng "chỉ có 329 đơn" (số liệu chép tay, không đọc từ dữ liệu).
- `src/dashboard/app.py:87` và `:517` — hai `except Exception` bắt rộng (bỏ lỗi cấu hình thành "không có dữ liệu").
- `src/dashboard/app.py:44,461-494` — cache toàn cục `_INTEGRATION_RUNS` theo `logs_dir`; test phải gọi
  `reset_integration_logs()` để cô lập.
- `src/dashboard/app.py:227,457` — `_tab_config(config)` được gọi hai lần trong một lần dựng app (đọc YAML hai lần).
- `src/analytics/service.py:50,153-165,185-197,225-237,261-272` — SQL dựng bằng f-string; alias và tên cột
  là hằng nội bộ nên không có đường chèn từ người dùng, nhưng `WHERE` nối thủ công và thứ tự tham số `?`
  phụ thuộc đúng thứ tự `clauses`/`params`.
- `src/analytics/service.py:57-59,67-68,80-81,94-96,160-161,192-193,230-231,267-268` — mọi truy vấn
  doanh thu/giao vận đều `JOIN v_dim_date`, nên đơn có `date_key` NULL biến mất khỏi KPI mà không cảnh báo.
- `src/pipeline/cli.py:19-33` — ba lệnh con khai cứng; thêm lệnh mới phải sửa `build_parser` + `main`
  + `tests/unit/test_cli.py`.
- `src/pipeline/stages.py:21` so với `:99-170` — `STAGES` có 4 tầng nhưng `_run_all` ghi 6 `StageResult`
  (`quality`, `linkage` không nằm trong `STAGES`); `StageResult` của tầng `analyze` không mang số liệu.
- `src/integrate/pipeline.py:10` — `import AnalyticsService` không dùng (đảo hướng phụ thuộc
  `integrate → analytics`), được `ruff.toml:27` miễn trừ `F401`.
- `tests/` — 7.358 dòng cho 353 hàm test; 10 mô-đun vượt 250 dòng (lớn nhất `test_integration_tab.py` 772 dòng
  và `test_integration_selector.py` 612 dòng); `test_dashboard_smoke.py` và `test_cli.py::test_main_analyze_stage`
  vẫn gọi `load_config()` của repo nên bộ "nhanh" cần `warehouse/olist.duckdb` + `data/marts/`.
- `requirements.txt:9-13` — hai gói mới (`dash-mantine-components`, `ruff`) kèm chú thích lý do; vẫn không có
  lock file và không ghim phụ thuộc bắc cầu.

## Handoff Summary

- **Intent-relevant finding**: Lớp phân tích hiện chỉ có **năm truy vấn mô tả** trong
  `src/analytics/service.py`, không có một dòng thống kê suy luận hay học máy nào trong `src/`
  (`grep` `t_test|chi2|confidence_interval|auc|logistic|corr\(` không khớp). Ba điểm chạm mà intent này
  sẽ phải sửa đều đang bị **test khẳng định số lượng cứng**: `tests/unit/test_dashboard_smoke.py:43,48,101`
  (`4 tab`, `8 callback`, `9 output`), `tests/integration/test_u3_end_to_end.py:49` (`8 callback`),
  và `src/pipeline/cli.py:19-33` (3 lệnh con, 5 lựa chọn `--stage`). Đường mở rộng rẻ nhất đã có sẵn tiền lệ:
  tab "Tích hợp" cấu hình bằng `config/integration-tab.yaml` + `TabConfig` + `register_callbacks`, và
  `create_app` đã bật `suppress_callback_exceptions=True` (`src/dashboard/app.py:415`) vì thân tab được
  dựng trong callback.
- **Risks / follow-up**:
  1. **Không có thư viện thống kê/ML nào được ghim.** `requirements.txt` có 10 gói, không `numpy`/`scipy`/
     `statsmodels`/`scikit-learn`; quy tắc dự án cấm import gói chưa ghim, nên S-01…S-05 (khoảng tin cậy,
     tương quan, kiểm định nhóm, phân rã mùa vụ, phân loại đơn trễ) buộc phải ghim thêm phụ thuộc **hoặc**
     tự cài đặt trên `numpy` (chỉ có mặt gián tiếp qua `pandas`, không được ghim trực tiếp).
  2. **Rò rỉ đặc trưng (leakage) là rủi ro thật của mô hình phân loại**: `v_fact_orders` chứa
     `order_delivered_customer_date`, `delivery_days`, `is_late` — ba cột chỉ biết sau khi giao; đặc trưng
     phải loại chúng, nếu không AUC sẽ đẹp giả tạo. `is_late` chỉ đúng cho đơn `delivered` (`is_delivered`).
  3. **Chốt hồi quy dữ liệu vẫn là hợp đồng cứng**: 5 KPI baseline (`KpiReconciler`) và allowlist dị thường
     không được đổi; mọi báo cáo thống kê mới phải đọc từ mart/view hiện có thay vì tính lại doanh thu theo
     cách khác, hoặc phải nêu rõ định nghĩa doanh thu (quy tắc dự án).
  4. **Bộ test nhanh chưa hermetic** (`TD-09`): test dashboard gọi `load_config()` của repo; CI xử lý bằng cách
     chạy `--stage all` trước khi test, nên thêm tab/thêm output mới phải giữ được chuỗi đó.
  5. Phần **ngoài** năm đường dẫn được quét sâu (`src/integration`, `src/linkage`, `src/clean`, `src/integrate`,
     `docs/`, `assets/`) giữ nguyên văn bản từ lần quét trước và **chưa được xác minh lại**; chỉ số dòng đã
     được đo lại trên đĩa.
