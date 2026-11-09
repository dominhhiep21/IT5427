# Code Summary — u6-integration-ui

## Ba lỗi chỉ trình duyệt thấy, sửa bằng chrome-devtools (2026-11-09)

Sau khi workflow kết thúc, tab "Tích hợp" được kiểm bằng trình duyệt thật trên `127.0.0.1:8050`. Ba lỗi dưới đây **không test nào bắt được**, vì test chỉ kiểm cây layout và số callback, không chạy callback như Dash chạy:

| # | Lỗi | Bản sửa | Test khoá |
|---|---|---|---|
| E1 | Bốn nút "Xem chi tiết" không mở được gì; console `ReferenceError` vì `Input('back-schema')` trỏ tới id chỉ tồn tại **bên trong** màn hình chi tiết | nút "Quay lại"/"Tải lại" dùng pattern-matching id `{"type": "back"|"reload", "screen": ...}`; `route_screen`/`reload_token` nhận `dict`; `Input(..., ALL)` | `test_screen_action_buttons_use_pattern_matching_ids` |
| E2 | Vừa bấm tab là màn hình chi tiết đầu tiên tự mở | Dash phát callback với `n_clicks = 0` khi thành phần khớp mẫu vừa được tạo; thêm `clicked_value(ctx.triggered)` và bỏ qua giá trị 0 | `test_route_ignores_the_zero_click_dash_sends_when_the_buttons_are_created` |
| E3 | Mở thẻ "Ghép bản ghi" treo trình duyệt | bảng "cặp bị bỏ qua" dựng đủ 12.613 dòng DOM; nay chỉ 200 dòng đầu (`SKIPPED_ROWS_SHOWN`) kèm câu nêu rõ đã cắt | `test_linkage_panel_caps_the_skipped_table_instead_of_building_every_row` |
| E4 | Sau "Đề xuất nguồn" huy hiệu vẫn nói "chưa có kết quả đề xuất" | gộp `StateBlock` vào vùng `source-table`; callback trả `(node, data-state)` qua `region_state` | `test_source_region_updates_the_status_badge_together_with_the_table` |

`SourcePanel` vì vậy dựng tay thay vì qua `_panel`: khối trạng thái phải nằm **trong** vùng thay được, còn `dmc.Select` + nút "Đề xuất nguồn" ở ngoài để không bị dựng lại mỗi lần bấm.

Sau khi sửa: **380 test nhanh + 9 chậm xanh**, phủ **90,63%**, `ruff check` sạch, pipeline `6/6` tầng `success=True`. Bằng chứng lượt kiểm trình duyệt đầy đủ ở `construction/build-and-test/test-results.md` §7; sự cố ghi ở `operation/incident-response/incident-plan.md`.

## Gia cố C9: dựng mọi vùng kết quả (2026-11-09)

Trước đây `tab.py` dựng **cứng** `don-theo-thang`: mọi id khác trong `result_region_ids` bị bỏ qua im lặng, trái điều khoản C9 "U6 phải dựng mọi `result_region_ids`". Nay:

- `IntegrationTab` duyệt `tab_config.result_region_ids`, dựng một khối cho mỗi id qua `_region_component`.
- `register_callbacks` đăng ký một callback riêng cho mỗi vùng (mỗi vùng một `Output`), qua `_region_callback`.
- Id không có hàm dựng → `ConfigurationError` nêu tên id, thay vì bỏ qua.

Test khoá: `test_integration_tab_rejects_an_unknown_result_region` trong `tests/unit/test_integration_tab.py`; hình dạng dashboard vẫn **4 tab, 8 callback, 4 thẻ + 1 vùng** với cấu hình hiện tại.


Nguồn: kế hoạch đã duyệt, hướng dẫn test, và các lần chạy ghi trong tài liệu này.

## 1. Đã dựng gì

| Lớp | Tệp | Nội dung |
|---|---|---|
| Tab | `src/integration/tab.py` (mới) | `IntegrationTab`, `OverviewScreen` (bốn thẻ, hai dòng số liệu), `ResultRegion` (vùng `don-theo-thang` trong thân tab), `DetailScreen`, `StateBlock` (năm token hiện có), bốn panel, **sáu** handler và `register_callbacks` |
| Khung app | `src/dashboard/app.py` | Dựng tab mới, giữ hai callback cũ, tổng **8** callback, `suppress_callback_exceptions` |
| Cấu hình tab | `src/integration/card.py`, `config/integration-tab.yaml` | `TabConfig.card_ids` + `result_region_ids`; chỉ bỏ `result_block_ids`; bỏ `build_integration_tab` cùng ba hàm phụ thuộc |
| Lỗi C5 | `src/common/exceptions.py` | `LinkageResultMissingError`, `LinkageResultInvalidError` |
| Trình bày | `assets/style.css` | Khối CSS cho thẻ, màn hình, khối SQL, dấu "kết quả cũ"; không đổi quy tắc cũ |
| Phụ thuộc | `requirements.txt` | Ghim `dash-mantine-components==2.8.1` |
| Test | `tests/unit/test_integration_tab.py` (mới, 46 hàm); `test_integration_card.py`, `test_dashboard_smoke.py`, `tests/integration/test_u3_end_to_end.py` cập nhật | 4 thẻ **+ 1 vùng**, 8 callback, bốn màn hình, năm trạng thái |

## 2. Kết quả kiểm chứng

| Cổng | Lệnh | Kết quả |
|---|---|---|
| Test của đơn vị | `pytest tests/unit/test_integration_tab.py tests/unit/test_dashboard_smoke.py` | **54 passed** |
| Bộ nhanh toàn repo | `pytest -m "not slow"` | **367 passed, 7 deselected** |
| Lint/định dạng | `ruff check` + `ruff format --check` | sạch (toàn danh sách CI: 32 tệp) |
| Phủ dòng | bộ nhanh | `tab.py` 88%, `card.py` 100%, `app.py` 93% |
| Số đo callback trên dữ liệu thật | `load_overview` 62 ms · `run_query` 457 ms · `route` 670 ms · `suggest_source` < 1 ms | đều dưới 2 giây |
| Layout phục vụ | `/_dash-layout`, `/_dash-dependencies` | HTTP 200, 8 callback |

## 3. Rà WCAG 2.1 AA (NFR4.1)

- Điều khiển là `<button>`/`<a>` thật, có nhãn chữ.
- Tab bàn phím đi hết bốn thẻ và bốn màn hình; không bẫy tiêu điểm.
- `:focus-visible` có viền tương phản; chữ thường dùng màu đạt ≥ 4,5:1 trên nền hiện tại.
- Không dùng màu làm tín hiệu duy nhất: mỗi `StateBlock` mang câu chữ; dòng "Kết quả cũ" là chữ, không chỉ là màu.

## 4. Điểm lệch kế hoạch

| # | Lệch | Lý do |
|---|---|---|
| 1 | `route` có hai `Output` (`overview-panel.hidden`, `screen-body.children`) | Ẩn tổng quan cần một đích thứ hai; ràng buộc "không hai callback cùng một `Output`" vẫn giữ (6 callback, 7 đích, mỗi đích một callback) |
| 2 | `reload` phát `reload-token`, `route` phản ứng theo token | Tránh hai callback cùng `Output` |
| 3 | Thêm `src/common/exceptions.py` | Hai kiểu lỗi C5 đã được hợp đồng khai, phải nằm ở tệp lỗi chung |
| 4 | `card.py` mất `build_integration_tab` và bốn test cũ của nó | Hành vi ba khối đã bị thay theo `frontend-components.md` §1; thay bằng hai test khoá hình dạng C9 |
| 5 | Thêm khối CSS cho tab mới | Không có bố cục nếu thiếu; không đổi quy tắc cũ |
| 6 | Ba hàm nhỏ `query_triggered`, `suggest_triggered`, `source_table_body` | W3/W4: đổi ô chọn không tự chạy truy vấn/đề xuất nguồn |

## 5. Việc chưa làm

- NFR2.1, NFR5.1, NFR5.2 đo đầy đủ ở Build and Test (`--stage all`, bộ `slow`, `KpiReconciler`).
- Chưa có test tự động cho tương phản màu và thứ tự tiêu điểm: rà thủ công ở §3.
