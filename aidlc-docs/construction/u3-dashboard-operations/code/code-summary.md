# Code Summary — U3 Dashboard & Operations

**Ngày hoàn tất**: 2026-10-23
**Trạng thái**: Code + test + dashboard smoke hoàn tất; chờ phê duyệt

## 1. Tệp đã tạo

### Dashboard
- `src/dashboard/app.py` — Dash app, layout 3 tab, filter, callback, error state.
- `src/dashboard/components.py` — KPI card, chart card, table, banner.
- `src/dashboard/formatting.py` — BRL, ngày, số, phần trăm.
- `src/dashboard/__main__.py` — chạy localhost.
- `assets/style.css` — design tokens “market ledger”.

### Pipeline / CLI
- `src/pipeline/cli.py` — argparse `run`, `micro-batch`, `replay`.
- `src/pipeline/__main__.py`.
- `src/pipeline/stages.py` — stage runner + run summary.
- `src/pipeline/manifest.py` — manifest idempotency.
- `src/pipeline/upsert.py` — natural-key upsert.
- `src/pipeline/micro_batch.py` — batch transaction + U2 rebuild.
- `src/pipeline/replay.py` — tạo batch lịch sử theo tháng.

### Docs
- `README.md`
- `docs/data-dictionary.md`
- `docs/runbook.md`
- `docs/3v.md`

### Test
- `tests/unit/test_formatters.py`
- `tests/unit/test_manifest.py`
- `tests/unit/test_upsert.py`
- `tests/unit/test_dashboard_smoke.py`
- `tests/unit/test_cli.py`
- `tests/integration/test_u3_end_to_end.py`

## 2. Skill đã dùng

- **frontend-design** — định hướng “market ledger”, palette/typography, tránh dashboard template.
- **ui-styling** — design tokens, spacing, focus, responsive, reduced motion.
- **webapp-testing** — Playwright smoke + screenshot dashboard localhost.

## 3. Cách chạy

```powershell
# Pipeline đầy đủ
.\.venv\Scripts\python.exe -X utf8 -m src.pipeline run --stage all

# Dashboard
.\.venv\Scripts\python.exe -X utf8 -m src.dashboard

# Micro-batch
.\.venv\Scripts\python.exe -X utf8 -m src.pipeline micro-batch --inbox inbox

# Replay
.\.venv\Scripts\python.exe -X utf8 -m src.pipeline replay --batches 3

# Test
.\.venv\Scripts\python.exe -X utf8 -m pytest
```

## 4. Kết quả xác minh

| Kiểm tra | Kết quả |
|---|---|
| Test suite | **45 passed** |
| Coverage U3 | **75%** (dashboard app 89%) |
| CLI `run --stage all` | success, ~12 giây |
| Dashboard load | 3 tab, 4 KPI, 0 console error |
| Micro-batch | success, chạy lại skipped |
| Replay | success |
| Playwright screenshot | overview/category/delivery |

Ảnh:

- `aidlc-docs/construction/u3-dashboard-operations/code/dashboard-overview.png`
- `aidlc-docs/construction/u3-dashboard-operations/code/dashboard-category.png`
- `aidlc-docs/construction/u3-dashboard-operations/code/dashboard-delivery.png`

## 5. Điều chỉnh trong quá trình làm

- Đổi heading từ Georgia sang **Cambria** để hiển thị đúng dấu tiếng Việt.
- Việt hóa status filter, date placeholder, subtitle “đơn đã giao”.
- Loại giai đoạn 2016 khỏi chart tỷ lệ giao trễ theo tháng (vẫn giữ badge cảnh báo) để tránh spike 100% từ 1 đơn.
- Micro-batch upsert ở cleaned rồi rebuild U2; đảm bảo star schema luôn nhất quán.
- Replay tạo batch theo tháng từ cleaned orders.

## 6. Giới hạn

- ML dự báo giao trễ chưa triển khai (US-22 Could).
- Dashboard chỉ localhost, một người dùng.
- Playwright dùng full Chromium do headless shell tải chưa hoàn tất; không ảnh hưởng app.
- Micro-batch rebuild toàn bộ U2 marts, phù hợp batch nhỏ/demo.
