# Design System Mapping

Nguồn: `mockups.md`, `interaction-spec.md`, `assets/style.css`, `src/dashboard/analysis_tab.py`, `src/integration/card.py`.

## Nguyên tắc ánh xạ

Ba mục hiện có của tab dựng bằng `_section_header` + `_section`, dùng `dmc` cho tiêu đề và `html.*` cho phần còn lại. Khối mới **theo đúng khuôn đó** — không đưa thêm thư viện thành phần nào.

| Thành phần mockup | Dựng bằng | Lớp CSS có sẵn | Ghi chú |
|---|---|---|---|
| `<section aria-label>` | `html.Section` | **không có** | `style.css` chỉ có 8 selector `.analysis-tab` (dòng 1196–1204), **tất cả** chỉ đặt `color`. Không selector nào cho `section`, `fieldset`, `ul`, `button` của tab — phần còn lại phải **thêm** |
| Tiêu đề "Dự đoán" | `html.H3` | **không có** cho `H3` của tab | ba mục hiện có dùng `_section_header`, tiêu đề là **sans 15px** qua `.chart-header h3` — **không** phải `--font-display`. Khối mới theo đúng khuôn đó |
| Câu dẫn đơn vị dòng hàng | `html.P` | — | `--text-2` |
| Biểu mẫu | `html.Fieldset` + `html.Legend` | **không có** | xem khối CSS dưới |
| **Mười một giá trị nhập**, dựng bằng **10 thành phần** | 3 `dcc.Dropdown` (2 bang + `payment_type`), 6 `dcc.Input` (ngày, giá, hai số ngày, số món, `installments`), 1 `dcc.Checklist` hai mục (`has_items`, `has_payment`) | `.dash-dropdown` cao **38px** (`style.css:492`) | checklist hai mục gánh **hai** giá trị, nên 11 giá trị ≠ 11 thành phần |
| Nút chính / phụ | `html.Button` | **không có** | thêm selector mới |
| Ba dòng đóng góp | `html.Ul` / `html.Li` | **không có** | thêm selector mới |

## Chỗ **phải** thêm CSS, và giới hạn của nó

`fieldset` chưa có style trong `assets/style.css`. Cần thêm **một** khối, dùng token có sẵn:

```css
.analysis-tab fieldset {
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: var(--space-5);
  background: var(--surface);
  box-shadow: var(--shadow-sm);
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--space-4);
}
@media (min-width: 1024px) {
  .analysis-tab fieldset { grid-template-columns: 1fr 1fr; }
}
```

Không định nghĩa token mới. Không đổi giá trị token đang có. Không đụng style của mục khác — selector đều nằm dưới `.analysis-tab`.

## Token nào được dùng, và vì sao không hơn

| Token | Dùng ở | Không dùng ở |
|---|---|---|
| `--space-4`, `--space-5`, `--space-6` | gap, padding, khoảng cách mục | `--space-7` (48px) — quá rộng cho một khối trong tab |
| `--radius`, `--radius-sm` | `fieldset`, nút | `--radius-lg`, `--radius-pill` |
| `--shadow-sm` | `fieldset` | `--shadow-md` — không cần nổi hơn các mục khác |
| `--text`, `--text-2` | mọi chữ | **`--text-3`** — chỉ 3,85:1, đã bị loại ở đợt trước |
| `--accent`, `--accent-hover` | nút chính | `--danger`, `--clay`, `--ochre` — kết quả không dùng màu |
| `--surface`, `--surface-sunken` | nền | `--paper` cho khối (chỉ dùng cho nền trang) |

## Đối chiếu với `src/integration/card.py`

`analysis_tab.py` đang mượn `STATE_ICONS`/`TEXTS` của `card.py` (nợ `TD-26`). Khối mới **không** mượn gì thêm từ đó: nó không có trạng thái icon, và câu chữ của nó là câu chữ của tab phân tích, không phải của tab Tích hợp. Ghi rõ để không ai mở rộng mối phụ thuộc chéo đó.

## Ba chỗ phải sửa **ngoài** khối, cùng thay đổi — **năm tệp**, không phải ba

| Tệp | Sửa gì | Vì sao |
|---|---|---|
| `src/dashboard/analysis_tab.py` | `TEXTS["model_caption"]` — bỏ câu "Chỉ đọc: … không chọn lại được" | nó nói tab không có ô nhập, mà sắp có |
| `README.md` mục Dashboard | cùng nội dung | đang chép lại câu đó |
| `tests/unit/test_dashboard_analysis_tab.py` | ba mục → **bốn**; thêm ca cho mười một điều khiển và bốn trạng thái mới | hình dạng tab đổi là đổi hợp đồng |
| **`tests/unit/test_dashboard_smoke.py`** | `len(app.callback_map) == 9` (dòng 62) → **10**; `len(outputs) == 9` ở **cả hai chỗ**: dòng 115 **và** dòng 131 → **10** | FR3 đã chốt 10 callback / 10 output; bỏ sót là CI đỏ |
| **`tests/integration/test_u3_end_to_end.py`** | 9 callback (dòng 83) → **10** | cùng lý do, test `slow` |

## Trạng thái "đang tính" không được thêm callback — và cũng không có `loading_state`

`html.Button` **không** có prop `loading_state` trong `dash==4.4.1` (đã kiểm: gói không chứa chuỗi đó). Thân tab đã nằm trong `dcc.Loading` (`analysis_tab.py:534-539`), nên bọc thêm loader chỉ lồng hai spinner.

Vì vậy trạng thái 3 được biểu đạt bằng **spinner có sẵn** của `dcc.Loading` đang bọc thân tab. Nút **không** bị khoá, và kết quả cũ vẫn hiện trong lúc chờ.

**Hệ quả phải nói rõ:** AC2.5.6 của `stories.md` đòi "nút ở trạng thái chờ" và "kết quả cũ mờ đi". Hai vế đó cần **một output thứ mười một** (để bật/tắt `disabled` và lớp mờ), tức phá hợp đồng 10 output. Đây là **quyết định còn mở**, chuyển Functional Design: hoặc nới hợp đồng lên 11 output, hoặc hạ AC2.5.6 xuống mức "spinner của tab là đủ". Mặc định đề nghị: **giữ 10 output**, và ghi việc hạ AC vào record.

## Điều mapping này không làm

Không tạo design system mới. Không thêm font. Không thêm breakpoint mới ngoài 1024px (mốc 1280px đã có trong test). Không đổi token nào đang chạy — mọi thay đổi CSS đều là **thêm** selector mới dưới `.analysis-tab`.
