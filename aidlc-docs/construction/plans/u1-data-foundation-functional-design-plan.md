# Kế hoạch Functional Design — U1 Data Foundation

**Unit**: U1 — Data Foundation
**Story**: US-01 → US-07 (7 story)
**Giai đoạn**: CONSTRUCTION - Functional Design (Planning)

## 1. Bối cảnh

U1 chịu trách nhiệm biến 9 CSV thô thành dữ liệu sạch, có kiểm chứng:

- Ingestion + schema contract + hash.
- Quality gate.
- Cleaning timestamp, city, geolocation, category, payment/review grain, outlier flags.

Đầu ra: `data/raw/*.parquet`, `data/cleaned/*.parquet`, cleaning report, quality report.

## 2. Quy tắc đã chốt từ requirements/stories

- Geolocation gộp về **một dòng/zip** bằng trung vị lat/lng.
- Loại tọa độ ngoài khung Brazil trước khi gộp.
- 278 customer zip / 7 seller zip thiếu geolocation: giữ null, không mất đơn.
- 610 sản phẩm thiếu danh mục → `unknown` + `category_missing`.
- 2 danh mục thiếu bản dịch → giữ tên gốc + `translation_missing`.
- Payment giữ 103.886 dòng; review giữ 99.224 dòng; 547 đơn nhiều review (551 dòng dư) được gắn cờ.
- 775 đơn không có item vẫn giữ trong orders.
- Timestamp parse sang datetime; null được báo cáo, không bịa giá trị.
- Không xóa outlier; chỉ gắn cờ.

## 3. Câu hỏi cần trả lời

Vui lòng điền chữ cái sau mỗi `[Answer]:`. Khi hoàn tất, trả lời `done`.

### Câu 1 — Ngưỡng ngoại lai giá
Dùng ngưỡng IQR nào cho cờ ngoại lai?

A) IQR 1.5 (chuẩn) — gắn cờ nhiều hơn, vẫn giữ dòng (khuyến nghị)
B) IQR 3.0 — chỉ gắn cờ ngoại lai cực đoan
C) Gắn cả hai: `price_outlier` (1.5) và `price_extreme_outlier` (3.0)
X) Khác (vui lòng mô tả sau thẻ [Answer]:)

[Answer]: A

### Câu 2 — Chọn city/state đại diện cho zip
Sau khi gộp tọa độ, chọn city/state như thế nào khi một zip có nhiều cách viết?

A) Lấy mode (giá trị xuất hiện nhiều nhất); hòa thì chọn theo alphabet (khuyến nghị)
B) Để null nếu có nhiều biến thể; chỉ giữ lat/lng trung vị
C) Lấy dòng đầu tiên sau khi sắp xếp theo tên city
X) Khác (vui lòng mô tả sau thẻ [Answer]:)

[Answer]: A

### Câu 3 — Chính sách quality gate với bất thường đã biết
Các bất thường đã biết (775 đơn không item, 1 đơn không payment, 278/7 zip thiếu geo, 610 sản phẩm thiếu category, 547 đơn nhiều review) nên được xử lý thế nào?

A) Allowlist số lượng đã biết; fail nếu vượt ngưỡng hoặc xuất hiện loại lỗi mới (khuyến nghị)
B) Fail nghiêm ngặt với mọi bất thường, buộc sửa dữ liệu thủ công
C) Chỉ cảnh báo, không fail trừ khóa trùng/orphan
X) Khác (vui lòng mô tả sau thẻ [Answer]:)

[Answer]: A

### Câu 4 — Phạm vi cờ ngoại lai
Gắn cờ ngoại lai cho cột nào?

A) Chỉ `price` (khuyến nghị, đúng story US-04)
B) `price` + `freight_value`
C) `price` + `freight_value` + kích thước/thuộc tính sản phẩm
X) Khác (vui lòng mô tả sau thẻ [Answer]:)

[Answer]: A

## 4. Kế hoạch artifact

- [x] `business-logic-model.md` — luồng ingest → clean → quality; xử lý từng bảng.
- [x] `business-rules.md` — quy tắc chuẩn hóa, null, dedupe, flag, quality gate.
- [x] `domain-entities.md` — entity sau cleaning, khóa, quan hệ, cờ chất lượng.
- [x] Kiểm tra tính nhất quán với US-01 → US-07.

## 5. Checklist

- [x] Đọc unit definition và story map
- [x] Xác định phạm vi và quy tắc đã chốt
- [x] Tạo kế hoạch và câu hỏi
- [x] Thu thập câu trả lời
- [x] Phân tích mơ hồ/mâu thuẫn
- [x] Tạo artifact functional design
- [x] Cập nhật state và trình bày phê duyệt
