# Drift Report — intent `261111-model-feature-improvemen`

Đối chiếu **điều đã định** với **điều đã xảy ra**. Chỉ ghi cái lệch, và nói rõ cái nào đã xử lý.

## 1. Lệch so với kế hoạch ban đầu

| # | Đã định | Thực tế | Trạng thái |
|---|---|---|---|
| D1 | AUC mục tiêu ≥ 0,70 | **0,6482** | **chưa đạt**; đặc trưng mới cải thiện +0,135 so với baseline, cờ dưới mốc bật đúng. Không che, không chỉnh ngưỡng |
| D2 | Trạng thái "có kết quả chưa có ngưỡng" (FR3.2 / AC2.5.3) | **không dựng được** dưới C2 (khối mô hình bắt buộc `threshold`) | ghi thành **deviation D-1**, AC đánh `N/A` có lý do |
| D3 | "10 output" của FR3 | thực chất là **9 Output của callback KPI + 1 Output mới**; `build_dashboard_outputs` giữ 9 | ghi thành **deviation D-2** |
| D4 | 18 bước Code Generation U3 | làm đủ 18, nhưng **thêm 3 test ngân sách** (PR3.1–PR3.3) sau chặng C vì phát hiện thiếu | đã ghi trong `code-summary.md` |
| D5 | Không dựng lát cắt mỏng (Q2 = A) dù scope `feature` khai `skeleton: on` | giữ nguyên lựa chọn; điểm lệch vẫn còn trong `team.md` | **chưa giải quyết**, là điểm lệch đã biết |
| D6 | Danh sách `ruff format` "34 mục" trong `team.md` | thực tế **50** sau đợt này (47 trước) | sẽ sửa qua nghi thức learnings ở cổng đóng intent |
| D7 | Thời gian mở tab +20% (PR3.4) là ngưỡng cần kiểm | **chưa có cặp số trước/sau** | khoảng trống thật, ghi trong `performance-validation/test-results.md` |

## 2. Lệch so với thiết kế đã duyệt (đã sửa)

| # | Thiết kế | Mã | Xử lý |
|---|---|---|---|
| D8 | `aria-label` trên từng ô | Dash 4.4.1 từ chối prop đó trên `dcc` | thay bằng `html.Label` + `data-field`; **sửa tài liệu theo mã** |
| D9 | `dcc.Loading` là anh em của `form` | mã đặt `Loading` **trong** `Fieldset` | sửa sơ đồ trong `frontend-components.md` |
| D10 | Lỗi hiện "dưới đúng ô" | chỉ có một `Output`, nên lỗi nằm trong vùng kết quả với `data-field` | sửa mô tả ở §5 |
| D11 | Tên sự kiện nhật ký dùng gạch dưới | repo dùng dấu chấm | sửa `monitoring-design.md` |
| D12 | `Input` = 11 | thực tế 12 `Input` (hai cờ cùng trỏ `o-co-hang.value`) | sửa `frontend-components.md` §4 |

## 3. Không lệch

- Số đơn vị (3), số Bolt (3), thứ tự U1 → U2 → U3.
- Ba cột mart thêm vào, không đổi số dòng của 9 bảng và 11 view.
- 14 đặc trưng, `FORBIDDEN_COLUMNS`, chia tập theo `order_id`, mốc `2018-04-01`.
- Báo cáo v3: 11 trường, 9 khoá `counts`.
- Bề mặt: 10 callback, 4 mục, 5 tab, 4 thẻ; 9 Output của callback KPI.
- Không thêm phụ thuộc; không sửa `dataset/`; không hạ cổng phủ.

## 4. Điểm lệch phải xử lý tiếp

D1 (AUC 0,70) và D5 (skeleton) là hai điểm lệch **cần quyết định của đợt sau**, không phải lỗi của đợt này. D6 và D7 là hai việc nhỏ còn treo.
