# Incident Plan

## 1. Mức độ sự cố

Chỉ ba mức, vì chỉ một người và một máy.

| Mức | Định nghĩa | Ví dụ | Thời hạn phản ứng |
|---|---|---|---|
| **P1** | Số liệu **sai** hoặc dữ liệu gốc bị chạm | cổng đối chiếu đỏ; KPI lệch; `dataset/` bị sửa | ngay, trước mọi việc khác |
| **P2** | Hệ **không chạy được** nhưng dữ liệu còn nguyên | pipeline đỏ; dashboard không mở | trong ngày |
| **P3** | Hệ chạy, có điểm xấu nhưng không sai số | truy vấn chậm; một màn hình hiển thị xấu; log đầy | khi có thời gian |

Không có P4. Không có mức nào cần gọi người khác: không có người thứ hai.

## 2. Quy trình

1. **Nhận ra** — qua cổng (test/pipeline) hoặc qua mắt.
2. **Phân mức** theo bảng §1.
3. **Khoanh vùng** — ghi lại `run_id`, lệnh đã chạy, thông điệp lỗi **trước khi** sửa bất cứ gì.
4. **Sửa** — theo đúng runbook tương ứng ở `runbooks.md`.
5. **Kiểm lại** — chạy lại cả chuỗi; P1 phải chạy thêm cổng đối chiếu.
6. **Ghi** — một mục trong nhật ký §4, kể cả khi sự cố tự hết.

## 3. Điều cấm

- Không sửa `dataset/` để "cho khớp".
- Không hạ ngưỡng phủ, không bỏ cổng, không nới dung sai KPI để lấy xanh.
- Không quay lui khi lỗi là "số sai mà test xanh" — đó là thiếu cổng, phải thêm test trước.
- Không xoá nhật ký của lần chạy hỏng: đó là bằng chứng duy nhất.

## 4. Nhật ký sự cố

| Ngày | Mức | Triệu chứng | Nguyên nhân | Cách sửa | Test thêm |
|---|---|---|---|---|---|
| 2026-11-08 | P1 | Cổng nghiệm thu lát cắt bị chặn: thẻ số liệu không còn trên giao diện | U6 dựng lại thân tab theo C9 cũ, không có khái niệm vùng kết quả | thêm `result_region_ids` vào C9; tab dựng mọi vùng; thêm `STATE_PENDING` | `test_integration_tab_rejects_an_unknown_result_region`, `test_integration_tab_holds_the_thin_slice_region` |
| 2026-11-09 | P2 | Plan U5 bị engine từ chối vì `contract_sha256` lệch | khối `## Testing Contract` bị sửa tay trong lúc dọn tài liệu | khôi phục đúng văn bản engine render; không sửa hash | — (quy trình, không phải mã) |
| 2026-11-09 | P1 | Cả bốn nút "Xem chi tiết" của tab "Tích hợp" không mở được màn hình nào; console `ReferenceError: ... id 'back-schema'` | callback `route` khai `Input("back-<screen>")` cho những nút chỉ tồn tại **sau khi** màn hình chi tiết được dựng; test chỉ đếm callback, không chạy chúng | chuyển "Quay lại"/"Tải lại" sang pattern-matching id; `route_screen`/`reload_token` nhận id dạng `dict` | `test_screen_action_buttons_use_pattern_matching_ids` |
| 2026-11-09 | P1 | Vừa bấm tab "Tích hợp", màn hình chi tiết đầu tiên tự mở | Dash gọi callback với `n_clicks = 0` ngay khi thành phần khớp mẫu được tạo | `clicked_value(ctx.triggered)`; bỏ qua mọi lần gọi có giá trị 0 | `test_route_ignores_the_zero_click_dash_sends_when_the_buttons_are_created` |
| 2026-11-09 | P1 | Mở thẻ "Ghép bản ghi" treo trình duyệt hàng phút | dựng đủ 12.613 dòng "cặp bị bỏ qua" thành DOM | chỉ hiển thị 200 dòng đầu, nêu rõ đã cắt; tệp JSON giữ nguyên | `test_linkage_panel_caps_the_skipped_table_instead_of_building_every_row` |
| 2026-11-09 | P2 | Sau "Đề xuất nguồn", huy hiệu vẫn nói "Một phần — chưa có kết quả đề xuất" | callback chỉ thay bảng, không thay khối trạng thái | gộp `StateBlock` vào vùng `source-table`; thêm `Output(source-table, "data-state")` | `test_source_region_updates_the_status_badge_together_with_the_table` |

Bốn mục P1/P2 ngày 2026-11-09 (E1–E4) là lỗi thật phát hiện bằng trình duyệt **sau khi** workflow đã hoàn tất — chúng cho thấy bộ test hiện tại chỉ kiểm cây layout và số callback, không kiểm callback có chạy. Bằng chứng đầy đủ ở `construction/build-and-test/test-results.md` §7.

Hai mục đầu là sự cố thật đã xảy ra trong đợt này; chúng được ghi lại thay vì xoá dấu.

## 5. Hậu kiểm

Mỗi P1 bắt buộc thêm **một test** khoá lại. Mỗi P2 bắt buộc thêm **một dòng** vào runbook tương ứng. Không có ngoại lệ "lần này thôi".
