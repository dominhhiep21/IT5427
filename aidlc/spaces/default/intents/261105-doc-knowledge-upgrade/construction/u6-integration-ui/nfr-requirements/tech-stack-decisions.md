# Tech Stack Decisions — u6-integration-ui

Nguồn: `technology-stack.md`, `requirements.txt`, `functional-design/functional-spec.md`, `functional-design/frontend-components.md`, `inception/requirements-analysis/requirements.md` (NFR1, NFR4, C2), `inception/contract-design/contract-summary.md` (C9).

## 1. Đã chốt ở cấp dự án

| Hạng mục | Lựa chọn | Ghi chú |
|---|---|---|
| Nền giao diện | Dash (đã có) + **`dash-mantine-components` (CHƯA có trong `requirements.txt`, chưa cài trong `.venv`)** | FR5.4 buộc dùng DMC; đây là phụ thuộc **mới**, phải ghim và cài |
| Đồ thị | Plotly | Đã có; tab mới dùng bảng, không cần đồ thị mới |
| Kiểu dựng | Hàm Python trả `html`/`dmc` | Cùng mẫu `src/integration/card.py` |
| Kiểm thử | pytest + test dashboard hiện có | `test_dashboard_smoke.py` |

## 2. Quyết định riêng cho đơn vị này

| Mã | Quyết định | Lý do |
|---|---|---|
| TS-U6-1 | Tab mới dựng trong `src/integration/tab.py` (mới), không nhét vào `app.py` | `app.py` đã dài; tách để test được từng màn hình |
| TS-U6-2 | Bốn thẻ thay hẳn ba khối `result_block_ids`; **giữ `card_ids` (đã có từ C9) và `result_region_ids`** | `load_tab_config` (card.py) **nay đã** bắt buộc `card_ids`, `callback_ids` và `result_region_ids` (chứa `don-theo-thang`) — không còn đọc `result_block_ids`. Thay đổi phải giữ nguyên ba khoá đó và chỉ bỏ `result_block_ids`; `_tab_config` trong `app.py` dùng cấu hình mặc định khi tệp hỏng |
| TS-U6-3 | Dùng lại bộ token `data-state` hiện có, **cộng một token cho vùng chưa chạy**: `chua-chay`, `rong`, `dang-tai`, `day-du`, `mot-phan`, `loi` (sáu) | `STATE_PENDING` ("Chưa chạy") có thật trong `card.py`/`tab.py` và được `test_dashboard_smoke.py` khẳng định; `StateBlock` của tab phải nhận token này, nếu không vùng dựng lúc mở tab sẽ ném `ValueError`. Không tạo chuẩn thứ hai; năm token cũ giữ nguyên |
| TS-U6-4 | Xoá callback một-khối của tab cũ, thêm **sáu** callback riêng (`route`, `run_query`, `suggest_source`, `reload`, `load_overview`, callback của vùng kết quả); tổng callback của dashboard sau thay đổi là **8** (2 của ba tab cũ + 6 của tab mới) | Mỗi callback một việc; không đè `callback_id` của ba tab cũ. Hai test **đã** khẳng định 8 (`test_dashboard_smoke.py`, `test_u3_end_to_end.py`) — giữ nguyên, chỉ sửa chú thích cũ còn ghi "năm callback" |
| TS-U6-5 | **Không thêm gói mới**: `dash-mantine-components` **đã ghim `2.8.1`** trong `requirements.txt` và đang được `card.py`/`tab.py` import | Giữ nguyên `2.8.1`, **không** nâng 3.x: bản 3.x đòi `dash>=4.5.0` còn repo ghim `dash==4.4.1`. Lý do ghim đã ghi ở dòng chú thích trong `requirements.txt`; theo `project.md` — Mandated, phụ thuộc trực tiếp phải ghim và cài trong `.venv` |
| TS-U6-6 | Mọi điều khiển có `data-testid` | Test dashboard bám vào, không bám vào CSS |
| TS-U6-7 | Cấu hình tab đọc từ `config/integration-tab.yaml` theo C9, thiếu tệp thì dùng hằng mặc định bốn `card_id` **và** `result_region_ids=("don-theo-thang",)` | Tránh dashboard không mở được vì một tệp cấu hình |
| TS-U6-8 | **Bộ token màu và chữ lấy theo shadcn/ui** (yêu cầu của người làm, 2026-11-08), hiện thực bằng CSS custom properties trong `assets/style.css`, không dùng Tailwind | shadcn/ui là bộ token chứ không phải thư viện chạy được trong Dash; ta sao lại đúng giá trị: chữ **Geist** (dự phòng `ui-sans-serif, system-ui, sans-serif`), nền/chữ theo bảng neutral `oklch`, bán kính `--radius: 0.625rem`, viền `oklch(0.922 0 0)`, chữ phụ `oklch(0.556 0 0)`, chữ chính `oklch(0.145 0 0)`. Có cả bảng tối (`.dark`). Bảng đầy đủ ở §5 |

## 3. Chỉ tiêu kỹ thuật

```yaml
nfr_requirements:
  - id: NFR1.1
  - id: NFR1.2
  - id: NFR1.3
  - id: NFR1.4
  - id: NFR1.5
  - id: NFR2.1
  - id: NFR2.2
  - id: NFR3.1
  - id: NFR4.1
  - id: NFR5.1
  - id: NFR5.2
  - id: NFR6.1
```

| Mã | Chỉ tiêu | Ngưỡng | Đo bằng |
|---|---|---|---|
| NFR1.1–NFR1.4 | Xem `performance-requirements.md` §1 | < 2 giây | `time.perf_counter` trong test dashboard và log của lần chạy thật |
| NFR1.5 | Bấm "Chạy truy vấn" của vùng `don-theo-thang` | lần đầu ≤ 7 giây (5 nạp + 2 truy vấn); lần sau ≤ 2 giây | `elapsed_ms` do U1 trả về; đo trên dữ liệu thật |
| NFR2.1 | Độ phủ ≥ 80% | 80% | `pytest --cov=src --cov-fail-under=80` |
| NFR2.2 | Mỗi mô-đun mới có test riêng | `tests/unit/test_integration_tab.py` | Rà `tests/unit/` |
| NFR3.1 | ruff sạch | 0 vi phạm | `ruff check` + `ruff format --check` trên tệp của đơn vị |
| NFR4.1 | WCAG 2.1 AA | bàn phím, tiêu điểm, tương phản ≥ 4,5:1 | Rà thủ công + test cấu trúc (nút thật, có nhãn) |
| NFR5.1/NFR5.2 | Ba tab cũ và 5 KPI không đổi | khớp baseline | `test_dashboard_smoke.py`, `KpiReconciler` |
| NFR6.1 | Không mạng | 0 lời gọi | Rà mã |

## 4.1 Design tokens theo shadcn/ui (TS-U6-8)

Nguồn bằng chứng, lấy ngày 2026-11-08:

- Tài liệu chính thức (`context7`, `/websites/ui_shadcn`, trang `docs/theming`): bảng token neutral mặc định ở dạng `oklch`, `--radius: 0.625rem`, có nhánh `.dark`.
- Trang thật `https://ui.shadcn.com/docs/theming` (Chrome DevTools): `font-family: Geist, "Geist Fallback"`, cỡ chữ gốc 16px, tiêu đề `h1` đậm 600; `--radius: .625rem`, `--foreground` rất tối (`lab(0% 0 0)`), `--muted-foreground: lab(48.5% 0 0)`, `--border: lab(91% 0 0)`.

Áp vào Dash bằng biến CSS trong `assets/style.css` (Tailwind không chạy trong Dash):

| Biến | Sáng | Tối | Dùng ở |
|---|---|---|---|
| `--background` / `--foreground` | `oklch(1 0 0)` / `oklch(0.145 0 0)` | `oklch(0.145 0 0)` / `oklch(0.985 0 0)` | nền trang, chữ chính |
| `--card` / `--card-foreground` | `oklch(1 0 0)` / `oklch(0.145 0 0)` | `oklch(0.205 0 0)` / `oklch(0.985 0 0)` | bốn thẻ, panel |
| `--muted` / `--muted-foreground` | `oklch(0.97 0 0)` / `oklch(0.556 0 0)` | `oklch(0.269 0 0)` / `oklch(0.708 0 0)` | dòng phụ, nhãn, "kết quả cũ" |
| `--border` / `--ring` | `oklch(0.922 0 0)` / `oklch(0.708 0 0)` | `oklch(1 0 0 / 10%)` / `oklch(0.556 0 0)` | viền, tiêu điểm |
| `--primary` / `--primary-foreground` | `oklch(0.205 0 0)` / `oklch(0.985 0 0)` | `oklch(0.922 0 0)` / `oklch(0.205 0 0)` | nút chính |
| `--radius` | `0.625rem` | — | bo góc thẻ, nút, ô chọn |
| chữ | `Geist`, dự phòng `ui-sans-serif, system-ui, sans-serif` | — | toàn tab; cỡ gốc 16px; tiêu đề 600 |

**Ràng buộc quan trọng:** Geist phải **tự lưu** trong `assets/fonts/` (tệp `woff2`) và khai `@font-face`; không tải từ Google Fonts lúc chạy, vì NFR6 cấm mạng. Nếu không có tệp font hợp lệ, dùng ngay dãy dự phòng hệ thống — không chặn giao diện.

## 4. Việc cần làm ở bước sinh mã

- Tạo `src/integration/tab.py` với `IntegrationTab`, `OverviewScreen`, `DetailScreen`, `StateBlock` và bốn panel.
- Ghim `dash-mantine-components` trong `requirements.txt` và cài vào `.venv` (TS-U6-5).
- Thêm `assets/fonts/` (Geist `woff2`) và `@font-face` trong `assets/style.css`; khai bộ biến CSS ở §4.1 cho cả bảng sáng và tối; mọi màu trong tab mới đọc từ biến, không viết mã màu rời (TS-U6-8).
- Ghi bộ token vào `docs/design-tokens.md` để lần sau đổi màu chỉ sửa một chỗ.
- Sửa `config/integration-tab.yaml`: giữ `card_ids` bốn giá trị (đã có từ C9), bỏ `result_block_ids`, **thêm `result_region_ids`**; cập nhật `load_tab_config`/`TabConfig` (`src/integration/card.py`) và năm test của `test_integration_card.py` để không còn đòi `result_block_ids`.
- Cập nhật `src/dashboard/app.py`: dựng tab mới, giữ nguyên ba tab cũ, tổng **8** callback.
- Cập nhật `tests/unit/test_dashboard_smoke.py` (bốn thẻ + một vùng, 8 callback, `data-state` theo bộ token hiện có) và `tests/integration/test_u3_end_to_end.py` (8 callback); thêm `tests/unit/test_integration_tab.py`.
