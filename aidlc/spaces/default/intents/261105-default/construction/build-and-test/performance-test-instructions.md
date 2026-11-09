# Performance Test Instructions

## Mục tiêu

| Hạng mục | Mục tiêu | Kết quả đo |
|---|---|---|
| Pipeline đầy đủ | ≤ 10 phút | **~12,2 giây** |
| Dashboard load | ≤ 3 giây | **1,81 giây** |
| KPI query | ≤ 1 giây | **65-233 ms** |
| Micro-batch 10k dòng | ≤ 30 giây | **4,71 giây** (xử lý), 5,6 giây tổng |
| Dashboard filter | ≤ 3 giây | ~0,2-0,5 giây (callback) |

## Cách đo pipeline

```powershell
Measure-Command {
  .\.venv\Scripts\python.exe -X utf8 -m src.pipeline run --stage all
}
```

Hoặc xem `duration_seconds` trong `data/reports/run-summary.json`.

## Cách đo query KPI

```powershell
@'
import time
from src.config import load_config
from src.analytics.service import AnalyticsService
from src.common.types import KpiFilters
service = AnalyticsService(load_config())
for name, fn in [
    ("summary", lambda: service.kpi_summary(KpiFilters())),
    ("monthly", lambda: service.revenue_by_period(KpiFilters(), "month")),
    ("category", lambda: service.revenue_by_dimension(KpiFilters(), "category")),
]:
    times = []
    for _ in range(5):
        start = time.perf_counter(); fn(); times.append(time.perf_counter() - start)
    print(name, round(sorted(times)[2] * 1000, 1), "ms")
'@ | .\.venv\Scripts\python.exe -X utf8 -
```

## Cách đo dashboard load

Dùng Playwright (Chromium) và đo từ `goto` đến `networkidle`:

```python
import time
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    start = time.perf_counter()
    page.goto("http://127.0.0.1:8050", wait_until="networkidle")
    print("load", round(time.perf_counter() - start, 2), "s")
    browser.close()
```

## Cách đo micro-batch 10k

1. Tạo batch 10k orders từ `data/cleaned/orders.parquet`.
2. Ghi `inbox/perf-10k/orders.csv`.
3. Chạy:

```powershell
Measure-Command {
  .\.venv\Scripts\python.exe -X utf8 -m src.pipeline micro-batch --inbox inbox
}
```

Kết quả đã đo: **4,71 giây** xử lý batch, **5,6 giây** tổng.

## Kết luận

Tất cả mục tiêu hiệu năng đều đạt trên máy hiện tại (Windows, Python 3.13.5, SSD).
