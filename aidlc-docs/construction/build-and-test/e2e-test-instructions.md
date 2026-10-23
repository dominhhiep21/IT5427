# E2E Test Instructions — Dashboard

## Mục tiêu

Kiểm tra dashboard thật trên trình duyệt Chromium headless: load, 3 tab, 4 KPI, không lỗi console.

## Chuẩn bị

```powershell
.\.venv\Scripts\python.exe -X utf8 -m src.dashboard
```

Mở `http://127.0.0.1:8050`.

## Playwright script

```python
from pathlib import Path
from playwright.sync_api import sync_playwright

exe = r"C:\Users\Admin\AppData\Local\ms-playwright\chromium-1248\chrome-win64\chrome.exe"
out = Path("aidlc-docs/construction/u3-dashboard-operations/code")
out.mkdir(parents=True, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, executable_path=exe)
    page = browser.new_page(viewport={"width": 1440, "height": 1000})
    errors = []
    page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" else None)
    page.goto("http://127.0.0.1:8050", wait_until="networkidle", timeout=60000)
    page.wait_for_timeout(2000)
    assert page.title() == "Olist | Bảng điều hành"
    assert page.locator(".tab").count() == 3
    assert page.locator(".kpi-card").count() == 4
    page.screenshot(path=str(out / "dashboard-overview.png"), full_page=True)
    page.locator(".tab").nth(1).click()
    page.wait_for_timeout(1000)
    page.screenshot(path=str(out / "dashboard-category.png"), full_page=True)
    page.locator(".tab").nth(2).click()
    page.wait_for_timeout(1000)
    page.screenshot(path=str(out / "dashboard-delivery.png"), full_page=True)
    assert errors == []
    browser.close()
```

## Kết quả mong đợi

- Title đúng.
- 3 tab.
- 4 KPI card.
- 0 console error.
- 3 ảnh screenshot.

## Ghi chú

- Nếu `chromium_headless_shell` chưa tải xong, dùng `executable_path` trỏ tới `chromium-1248/chrome-win64/chrome.exe`.
- Dashboard chỉ localhost, không cần auth.
