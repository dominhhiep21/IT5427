# Kế hoạch Code Generation — U3 Dashboard & Operations

**Unit**: U3 — Dashboard & Operations
**Story**: US-15 → US-18, US-20 → US-22
**Giai đoạn**: CONSTRUCTION - Code Generation (Part 1: Planning)
**Vị trí code**: workspace root

## 1. Bối cảnh

U3 xây dashboard, CLI, micro-batch, replay, docs và test end-to-end trên U1/U2.

**Phụ thuộc**: `data/marts`, `warehouse/olist.duckdb`, `AnalyticsService`.
**Đầu ra**: dashboard chạy localhost, CLI một lệnh, batch processor, tài liệu.

## 2. Cấu trúc sẽ tạo

```
src/
  dashboard/
    __init__.py
    __main__.py
    app.py
    components.py
    formatting.py
  pipeline/
    __init__.py
    __main__.py
    cli.py
    stages.py
    manifest.py
    upsert.py
    micro_batch.py
    replay.py
assets/
  style.css
docs/
  data-dictionary.md
  runbook.md
  3v.md
tests/
  unit/
    test_formatters.py
    test_manifest.py
    test_upsert.py
  dashboard/
    test_dashboard_smoke.py
  integration/
    test_u3_end_to_end.py
README.md
```

## 3. Kỹ năng sẽ dùng

- **frontend-design** (đã load): định hướng “market ledger”, palette/typography, tránh dashboard template.
- **ui-styling**: design tokens, spacing, accessibility, responsive.
- **webapp-testing**: Playwright smoke + screenshot dashboard localhost.

## 4. Quyết định triển khai

- Dash server-side callback; `dcc.Store` giữ filter.
- Chart đọc `agg_sales_daily`/`agg_delivery_daily`.
- CLI argparse; stage runner U1/U2.
- Micro-batch: `inbox/{batch_id}/{table}.csv`; manifest; temp cleaned; upsert natural key; promote; U2 rebuild.
- Replay: chia cleaned orders theo tháng.
- Không ML.
- Dashboard `127.0.0.1:8050`.

## 5. Các bước thực hiện

### Step 1 — Dependencies + config
- [x] Thêm `dash`, `plotly` vào `requirements.txt`; cài trong `.venv`, pin phiên bản.
- [x] Bổ sung config: `inbox_dir`, `max_batch_rows`, `batch_timeout_seconds`, `dashboard_host`, `dashboard_port`.
- **Story**: US-15, US-18.

### Step 2 — Formatters + design tokens
- [x] `src/dashboard/formatting.py`: BRL, ngày, số.
- [x] `assets/style.css`: palette, typography, focus, reduced motion, responsive.
- **Story**: US-17.

### Step 3 — Dashboard components + layout
- [x] `src/dashboard/components.py`: KPI card, chart, table, banner.
- [x] `src/dashboard/app.py`: layout 3 tab, filter bar, `dcc.Store`.
- **Story**: US-15, US-16.

### Step 4 — Dashboard callbacks
- [x] Callback filter → KPI/chart.
- [x] Error/empty state.
- [x] `src/dashboard/__main__.py`.
- **Story**: US-15, US-16, US-17.

### Step 5 — CLI + stage runner
- [x] `src/pipeline/cli.py`: argparse `run`, `micro-batch`, `replay`.
- [x] `src/pipeline/stages.py`: ingest/clean/integrate/analyze/all.
- [x] `src/pipeline/__main__.py`.
- **Story**: US-20.

### Step 6 — Manifest + upsert
- [x] `src/pipeline/manifest.py`: load/save, hash idempotency.
- [x] `src/pipeline/upsert.py`: natural key merge.
- **Story**: US-18.

### Step 7 — Micro-batch processor
- [x] `src/pipeline/micro_batch.py`: scan inbox, clean batch, temp cleaned, validate, promote, U2 rebuild.
- [x] Batch result/report.
- **Story**: US-18.

### Step 8 — Replay generator
- [x] `src/pipeline/replay.py`: chia cleaned orders theo tháng, ghi batch CSV.
- **Story**: US-18.

### Step 9 — Docs
- [x] `README.md`: cài đặt, chạy, dashboard, batch, troubleshooting.
- [x] `docs/data-dictionary.md`, `docs/runbook.md`, `docs/3v.md`.
- **Story**: US-20.

### Step 10 — Unit tests
- [x] Formatters.
- [x] Manifest idempotency.
- [x] Upsert keys.
- **Story**: US-21.

### Step 11 — Dashboard smoke + integration
- [x] `tests/dashboard/test_dashboard_smoke.py`: layout/callback smoke.
- [x] `tests/integration/test_u3_end_to_end.py`: CLI all + micro-batch + dashboard.
- **Story**: US-21.

### Step 12 — Verification
- [x] `pytest` full.
- [x] `python -m src.pipeline run --stage all`.
- [x] `python -m src.dashboard` + Playwright screenshot.
- [x] Coverage dashboard/pipeline ≥ 70%.
- [x] Ghi code summary.
- **Story**: US-15 → US-21.

## 6. Truy vết story

| Story | Bước |
|---|---|
| US-15 | 1, 3, 4 |
| US-16 | 3, 4 |
| US-17 | 2, 3, 4 |
| US-18 | 1, 6, 7, 8 |
| US-20 | 5, 9 |
| US-21 | 10, 11, 12 |
| US-22 | Không triển khai (Could) |

## 7. Phạm vi và ước lượng

- Khoảng **20-25 tệp**, ~1.500-2.000 dòng code + test + CSS.
- 12 bước.
- ML không làm.
- Dashboard test bằng Dash test client + Playwright smoke.

## 8. Điều kiện hoàn thành

- [x] Dashboard 3 tab, filter, KPI/chart, tiếng Việt.
- [x] CLI `run --stage all`, `micro-batch`, `replay`.
- [x] Micro-batch idempotent, batch lỗi không phá mart.
- [x] README + docs.
- [x] `pytest` pass; coverage ≥ 70%.
- [x] Playwright screenshot dashboard thành công.
