# Integration Test Instructions

## Purpose

Kiểm tra U1 → U2 → U3 và micro-batch/replay trên dữ liệu thật.

## Test Scenarios

### Scenario 1 — U1 → U2

- **Mô tả**: cleaned Parquet từ U1 tạo được star schema + DuckDB.
- **Test**: `tests/integration/test_u2_end_to_end.py`.
- **Kỳ vọng**:
  - 5 dim + 4 fact + 2 aggregate.
  - KPI: 15.419.773,75 BRL; 96.478 đơn; AOV 159,83; 7.826 trễ; 8,11%.
  - 11 DuckDB view.

### Scenario 2 — U2 → U3 dashboard

- **Mô tả**: dashboard đọc DuckDB, layout 3 tab, callback trả KPI/chart.
- **Test**: `tests/unit/test_dashboard_smoke.py`.
- **Kỳ vọng**: 3 tab, 4 KPI card, 2 callback, 0 lỗi layout.

### Scenario 3 — CLI full pipeline

- **Mô tả**: `run --stage all` chạy ingest → clean → quality → integrate → analyze.
- **Test**: chạy thủ công + `tests/integration/test_u3_end_to_end.py`.
- **Kỳ vọng**: success, ~12 giây.

### Scenario 4 — Micro-batch

- **Mô tả**: batch CSV trong `inbox/{batch_id}/` được clean, upsert, quality gate, rebuild U2.
- **Test**: `tests/integration/test_u3_end_to_end.py` + smoke thủ công.
- **Kỳ vọng**: success; chạy lại cùng hash → skipped; batch lỗi không phá mart.

### Scenario 5 — Replay

- **Mô tả**: chia cleaned orders theo tháng, tạo batch lịch sử, xử lý tuần tự.
- **Test**: `tests/integration/test_u3_end_to_end.py`.
- **Kỳ vọng**: batch success; KPI cuối khớp baseline.

## Setup

```powershell
# Đảm bảo đã chạy U1/U2
.\.venv\Scripts\python.exe -X utf8 -m src.pipeline run --stage all
```

## Run Integration Tests

```powershell
.\.venv\Scripts\python.exe -X utf8 -m pytest -m slow -q
```

Kỳ vọng: **6 slow tests passed** (U1, U2, U3 + data quality).

## Logs

- `logs/{run_id}.jsonl`
- `data/reports/integration-report.json`
- `data/reports/kpi-reconciliation.json`
- `data/reports/quality-report.json`

## Cleanup

- Xóa `inbox/*` nếu chỉ chạy thử.
- Không xóa `data/marts` hoặc `warehouse/olist.duckdb` nếu muốn giữ dashboard.
