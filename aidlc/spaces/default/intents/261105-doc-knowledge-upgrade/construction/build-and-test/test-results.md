# Test Results — Olist integration upgrade

Mọi số dưới đây chạy trên máy phát triển, dữ liệu thật trong `dataset/`, ngày 2026-11-09.

## 1. Bộ test

| Lần chạy | Lệnh | Kết quả | Thời gian |
|---|---|---|---|
| Bộ nhanh | `.venv\Scripts\python.exe -X utf8 -m pytest -m "not slow" -q` | **380 passed, 9 deselected** | 13,14 s |
| Bộ chậm | `.venv\Scripts\python.exe -X utf8 -m pytest -m slow -q` | **9 passed, 380 deselected** | 61,02 s |
| Cổng phủ | `.venv\Scripts\python.exe -X utf8 -m pytest --cov=src --cov-fail-under=80 -q` | **389 passed**, phủ **90,63%** (3852 câu lệnh, 361 bỏ sót) | 89,30 s |

Ngưỡng 80% đạt ở mức tổng thể `src/`. Các mô-đun còn dưới 80% là nợ cũ, không phải mã của đợt này: `src/common/memory.py` 0%, `src/pipeline/__main__.py` 0%, `src/dashboard/__main__.py` 0%, `src/pipeline/stages.py` 52%, `src/pipeline/cli.py` 62%, `src/external/ibge.py` 66%, `src/pipeline/micro_batch.py` 78%. Mã mới của đợt: `src/integration/tab.py` 88%, `card.py` 98%, `query.py` 100%, `selector.py` 97%, `rewrite.py` 84%, `schema.py` 96%, `load.py` 96%.

## 2. Pipeline trên dữ liệu thật

`run=20261109T073820-24fb09f7 success=True`

| Tầng | Dòng vào | Dòng ra | Thời gian |
|---|---|---|---|
| ingest | 1.550.922 | 1.550.922 | 5,90 s |
| clean | 1.550.922 | 569.774 | 5,55 s |
| quality | 569.774 | 569.774 | 0,46 s |
| integrate | — | — | 3,84 s |
| linkage | — | — | 4,27 s |
| analyze | — | — | 0,35 s |

## 3. Lint và định dạng

`ruff check src tests` → 0 vi phạm. `ruff format --check` trên ba tệp của đợt sửa (`src/integration/tab.py`, `tests/unit/test_integration_tab.py`, `tests/unit/test_dashboard_smoke.py`) → đã đúng định dạng. Chạy `ruff format --check` toàn repo còn **28 tệp cũ** chưa qua formatter; theo quy ước của team (`team.md` — Code Style), nợ này được dọn theo từng tệp khi có người sửa tới, không bằng một lần format toàn repo lẫn vào thay đổi chức năng.

## 4. Cổng đúng đắn dữ liệu của lát cắt

`tests/unit/test_integration_correctness.py` (2 test, marker `slow`): số đơn theo `(tháng, trạng thái)` trên vùng `don-theo-thang` khớp **0 sai lệch** với phép tính độc lập bằng pandas đọc thẳng `dataset/olist_orders_dataset.csv`. Cổng xanh ngay lần chạy đầu — nghĩa là số liệu vốn đã đúng, và từ nay mọi thay đổi bộ nạp/truy vấn đều bị chặn nếu làm lệch.

## 5. Kiểm chứng ngoài test

- Cấu hình thật `config/integration-tab.yaml` khai bốn `card_ids` + `result_region_ids: [don-theo-thang]`; `src/integration/tab.py` dựng **mọi** vùng trong danh sách, mỗi vùng một callback riêng; id lạ → `ConfigurationError`.
- Ánh xạ truy vấn→trường của `config/integration-sources.yaml` khớp hằng `TEMPLATE_MEDIATED_FIELDS` của U3 (có test khoá).
- Mỗi trường trong `covered_fields` của cả ba hồ sơ nguồn thuộc một bảng mà hồ sơ đó khai (có test khoá).

## 6. Điều chưa kiểm được tự động

- **Tương phản màu và thứ tự tiêu điểm** của tab: kiểm bằng mắt và công cụ đo tương phản; chưa có test tự động.
- **`bang_giao` luôn `None`**: lược đồ khai `loaded: true` nhưng `load_don_hang` chỉ đọc bảng khoá `olist_orders_dataset`, không join `olist_customers_dataset`. Ghi thành nợ (`TD-16`) thay vì sửa trong đợt này, vì nó đổi hành vi của thực thể `don_hang` mà U3/U4 đang dùng.
- **Hai bảng `agg_sales_daily`, `agg_delivery_daily`** chưa có baseline số dòng trên dữ liệu thật; `test_u2_end_to_end.py` chỉ khẳng định 11 view tồn tại và số dòng 9 bảng mart.

## 7. Kiểm bằng trình duyệt thật (chrome-devtools, 2026-11-09)

Kiểm trên `http://127.0.0.1:8050/`, dashboard chạy từ mã nguồn hiện tại. Ba lỗi **chỉ trình duyệt mới thấy** đã được tìm ra và sửa trong cùng ngày; mỗi lỗi có test khoá mới.

| Lỗi | Triệu chứng | Nguyên nhân | Bản sửa | Test khoá |
|---|---|---|---|---|
| E1 | Cả bốn nút "Xem chi tiết" không mở được màn hình nào; console `ReferenceError: A nonexistent object was used in an Input ... 'back-schema'` | `route` khai `Input("back-<screen>", "n_clicks")` cho bốn nút chỉ tồn tại **sau khi** màn hình chi tiết được dựng | pattern-matching id `{"type": "back", "screen": ...}` + `ALL`; `route_screen`/`reload_token` nhận id dạng dict | `test_screen_action_buttons_use_pattern_matching_ids` |
| E2 | Vừa bấm tab "Tích hợp", màn hình chi tiết đầu tiên **tự mở** | Dash gọi lại callback ngay khi thành phần khớp mẫu được tạo, với `n_clicks = 0` | `clicked_value(ctx.triggered)`; bỏ qua mọi lần gọi có giá trị 0 | `test_route_ignores_the_zero_click_dash_sends_when_the_buttons_are_created` |
| E3 | Mở thẻ "Ghép bản ghi" làm **treo trình duyệt** hàng phút | bảng "cặp bị bỏ qua" dựng đủ **12.613 dòng** thành DOM | chỉ hiển thị 200 dòng đầu kèm câu "Hiển thị 200 trong 12.613 …; tệp kết quả vẫn giữ đủ mọi dòng" (`SKIPPED_ROWS_SHOWN`) | `test_linkage_panel_caps_the_skipped_table_instead_of_building_every_row` |
| E4 | Sau khi bấm "Đề xuất nguồn", huy hiệu vẫn nói "Một phần — chưa có kết quả đề xuất cho truy vấn đang chọn" | callback chỉ thay bảng, không thay khối trạng thái | gộp khối trạng thái vào vùng `source-table`, thêm `Output(source-table, "data-state")` | `test_source_region_updates_the_status_badge_together_with_the_table` |

Kết quả lượt kiểm cuối (trang mới, console chỉ còn 2 cảnh báo accessibility có từ trước, không có HTTP 4xx/5xx):

| Thao tác | Kết quả đo |
|---|---|
| Mở tab "Tích hợp" | 4 thẻ; **không** màn hình nào tự mở (`detailOpen: false`) |
| Bấm "Chạy truy vấn" | `Một phần`; **Tổng toàn kỳ 99.441 đơn**; 136 dòng cả kỳ; **31 ms**; 12 tháng × trạng thái, 64 dòng hiển thị; lý do "thiếu trạng thái approved" |
| Mở/đóng "Lược đồ trung gian" | mở được, 3 tab thực thể, 14 trường; "Quay lại" đóng đúng |
| Mở "Truy vấn viết lại" + bấm "Chạy" | `Đầy đủ`; **74 dòng · 83 ms**; hiện SQL trung gian, SQL nguồn, kế hoạch 3 bước, bảng doanh thu theo danh mục |
| Mở "Ghép bản ghi" | `Đầy đủ`; 732 cặp, tỉ lệ ghép đúng 53,01% (388/732), 2.997 nhóm trùng; 934 dòng DOM thay vì 13.347 |
| Mở "Chọn nguồn" + bấm "Đề xuất nguồn" | Olist được chọn (`Có`); Cache IBGE bị loại kèm **danh sách trường thiếu**; nguồn mô phỏng ghi rõ lý do; `data-state` đổi `mot-phan` → `day-du` |
| Bấm "Tải lại" trên màn hình chi tiết | dựng lại đúng màn hình, giữ nguyên số liệu, console sạch |

Sau khi sửa và chạy lại toàn bộ: **380 test nhanh + 9 test chậm xanh**, phủ **90,63%**, `ruff check` sạch, pipeline `run=20261109T073820-24fb09f7` **6/6 tầng** `success=True` (~20,4 s).

Điều **vẫn** chưa kiểm được tự động: tương phản màu, thứ tự tiêu điểm bàn phím, và hành vi của Dash khi thành phần khớp mẫu được tạo — ba lỗi trên cho thấy khoảng trống này là thật, không phải giả định. Ghi thành việc của đợt sau trong `operation/feedback-optimization/feedback-loop.md`.
