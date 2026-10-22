# Business Rules — U1 Data Foundation

## Nhóm A — Ingestion và bảo toàn dữ liệu

### BR-01 — Dữ liệu gốc bất biến
- **Quy tắc**: Không mở tệp trong `dataset/` ở chế độ ghi; không đổi tên/xóa.
- **Lý do**: Bảo đảm khả năng tái lập và audit.
- **Kiểm thử**: So sánh SHA-256 trước/sau pipeline.

### BR-02 — Schema contract
- **Quy tắc**: Mỗi bảng phải có đúng danh sách cột và thứ tự trong `TableSpec`. Thiếu/thừa cột → `SchemaError`.
- **Lý do**: Tránh lỗi im lặng khi nguồn thay đổi.
- **Kiểm thử**: Giả lập thiếu cột, pipeline phải dừng.

### BR-03 — Encoding
- **Quy tắc**: Chỉ chấp nhận UTF-8 (có/không BOM). Lỗi decode → `SchemaError`.
- **Lý do**: Tránh mojibake tên thành phố/danh mục.

## Nhóm B — Chuẩn hóa thời gian

### BR-04 — Parse timestamp
- **Quy tắc**: Parse 5 cột thời gian của orders và `shipping_limit_date`, `review_creation_date`, `review_answer_timestamp` bằng `errors="coerce"`.
- **Null hợp lệ**:
  - `order_approved_at`: 160 null.
  - `order_delivered_carrier_date`: 1.783 null.
  - `order_delivered_customer_date`: 2.965 null.
- **Không hợp lệ**: giá trị nguồn khác null nhưng parse thất bại → gắn `has_invalid_timestamp = true`; tăng bộ đếm trong report.
- **Bắt buộc**: `order_purchase_timestamp` và `order_estimated_delivery_date` không được null; nếu null → `QualityGateError`.
- **Kiểm thử**: 0 invalid timestamp với dữ liệu hiện tại; null counts khớp baseline.

### BR-05 — Cờ trạng thái giao
- **Quy tắc**: `is_delivered = (order_status == "delivered")`.
- **Lý do**: KPI doanh thu mặc định chỉ tính đơn delivered.
- **Không** xóa đơn không delivered.

## Nhóm C — Chuẩn hóa chuỗi và địa lý

### BR-06 — Chuẩn hóa city/state
- **Quy tắc**: Với `customer_city`, `seller_city`, `geolocation_city`:
  1. Unicode NFC.
  2. Trim.
  3. Gộp khoảng trắng liên tiếp thành một.
  4. Lowercase.
  5. Ghi vào cột `*_normalized`; giữ cột gốc.
- **Không** bỏ dấu tiếng Bồ Đào Nha, không fuzzy match, không sửa tên không chắc chắn.
- **State**: trim + uppercase.
- **Kiểm thử**: `"Sao Paulo"`, `"sao  paulo"`, `"SÃO PAULO"` → cùng giá trị normalized (giữ dấu).

### BR-07 — Loại trùng geolocation
- **Quy tắc**: Loại các dòng trùng hoàn toàn trên 5 cột, giữ dòng đầu.
- **Baseline**: 261.831 dòng bị loại; còn 738.332 dòng.
- **Lý do**: Giảm nhiễu trước khi tính median/mode.

### BR-08 — Khung tọa độ hợp lệ
- **Quy tắc**: `valid_coord = lat ∈ [-34.0, 6.0] AND lng ∈ [-74.0, -34.0]`.
- **Baseline**: 42 dòng ngoài khung.
- **Lý do**: Loại tọa độ rõ ràng không thuộc Brazil.
- **Không** loại các dòng này khỏi việc tính city/state mode.

### BR-09 — Tọa độ đại diện
- **Quy tắc**: Với mỗi `zip_code_prefix`, `lat_median`/`lng_median` = trung vị của các dòng `valid_coord`.
- **Không** dùng mean; không lấy dòng đầu.
- **Kiểm thử**: zip có 3 tọa độ [1, 2, 100] → median = 2.

### BR-10 — City/state đại diện
- **Quy tắc**: Với mỗi zip, chọn `city_mode`/`state_mode` = giá trị xuất hiện nhiều nhất trên tất cả dòng không null (kể cả tọa độ ngoài khung).
- **Hòa**: chọn theo alphabet (giá trị nhỏ hơn).
- **Baseline**: 8.555 zip có > 1 biến thể city sau chuẩn hóa.
- **Lý do**: Giữ tên địa lý ổn định, tránh null không cần thiết.

### BR-11 — Bảo toàn đủ zip
- **Quy tắc**: Tập zip đầu ra = tất cả zip xuất hiện trong geolocation gốc (19.015). Left join với tọa độ đã gộp; zip không có tọa độ hợp lệ nhận `lat_median = null`, `lng_median = null`.
- **Baseline**: 19.010 zip có tọa độ; 5 zip null tọa độ.
- **Lý do**: Không mất zip khỏi dimension địa lý.

### BR-12 — Zip thiếu geolocation
- **Quy tắc**: 278 customer zip và 7 seller zip không có trong geolocation được giữ nguyên; khi join ở U2, trường địa lý = null.
- **Không** loại đơn/seller vì thiếu địa lý.
- **Kiểm thử**: join customers × geolocation vẫn trả 99.441 dòng.

## Nhóm D — Danh mục sản phẩm

### BR-13 — Thiếu danh mục
- **Quy tắc**: `product_category_name` null → `product_category_name = "unknown"`, `category_missing = true`.
- **Baseline**: 610 sản phẩm.
- **Không** xóa sản phẩm.

### BR-14 — Thiếu bản dịch
- **Quy tắc**: Left join translation. Không tìm thấy → `product_category_name_english = product_category_name` (tên gốc), `translation_missing = true`.
- **Baseline**: 2 danh mục (`pc_gamer`, `portateis_cozinha_e_preparadores_de_alimentos`), tương ứng 13 sản phẩm.
- **Không** dùng inner join.

## Nhóm E — Grain payment/review/item

### BR-15 — Payment grain
- **Quy tắc**: Giữ nguyên 103.886 dòng theo `(order_id, payment_sequential)`. Không cộng dồn, không dedupe.
- **Lý do**: Tránh nhân bản khi join item.

### BR-16 — Review grain
- **Quy tắc**: Giữ nguyên 99.224 dòng; khóa duy nhất là `(review_id, order_id)`. `review_id` đơn lẻ **không** duy nhất (814 trùng).
- **Cờ**: `multiple_reviews_per_order = true` nếu order_id có > 1 review (547 đơn; 551 dòng review dư).
- **Không** chọn review mới nhất và xóa các review khác.

### BR-17 — Item outlier
- **Quy tắc**: Tính Q1/Q3 của `price` trên toàn bộ 112.650 dòng. `price_outlier = price < Q1 - 1.5×IQR OR price > Q3 + 1.5×IQR`.
- **Baseline**: Q1/Q3 cho bounds xấp xỉ [-102,60; 277,40]; 8.427 dòng bị gắn cờ.
- **Không** xóa hoặc sửa giá.
- **Không** gắn cờ `freight_value` (theo quyết định Câu 4 = A).

### BR-18 — Không xóa dòng hợp lệ
- **Quy tắc**: Cleaning không được giảm số dòng của orders/customers/sellers/products/items/payments/reviews, trừ geolocation dedupe.
- **Kiểm thử**: row count cleaned = raw cho 8 bảng.

## Nhóm F — Quality gate

### BR-19 — Allowlist full batch
- **Quy tắc**: Ở chế độ full, các bất thường Q-01 → Q-10 phải bằng đúng baseline trong `business-logic-model.md`. Sai lệch → `QualityGateError`.
- **Q-11** (lệch payment/item) chỉ warning.
- **Lý do**: Phát hiện thay đổi dữ liệu ngoài dự kiến.

### BR-20 — Chế độ incremental
- **Quy tắc**: Không so số tuyệt đối; chỉ kiểm tra schema, khóa trong batch, orphan, null khóa, miền giá trị.
- **Không** fail vì tổng dòng tăng.

### BR-21 — Không ghi đè khi fail
- **Quy tắc**: Nếu quality gate fail, không ghi đè cleaned/mart của lần chạy trước.
- **Lý do**: Bảo vệ dashboard khỏi dữ liệu lỗi.

### BR-22 — Đối soát doanh thu
- **Quy tắc**: So sánh `SUM(payment_value)` theo đơn với `SUM(price + freight_value)`. Chênh > 0,01 ghi vào `reconciliation.json`.
- **Baseline**: 378 đơn lệch; không tự sửa.
- **Lý do**: Minh bạch khác biệt giữa hai định nghĩa doanh thu.

### BR-23 — Idempotency
- **Quy tắc**: Chạy lại cùng input tạo cùng output (nội dung xác định, không phụ thuộc thứ tự ngẫu nhiên). Ghi atomic: tệp tạm rồi thay thế.
- **Kiểm thử**: chạy 2 lần, so hash Parquet (trừ metadata thời gian nếu có).

### BR-24 — Báo cáo
- **Quy tắc**: Mỗi lần chạy ghi `ingest-report.json`, `cleaning-report.json`, `quality-report.json`, `reconciliation.json` với run_id.
- **Nội dung tối thiểu**: rows_in, rows_out, null counts, flag counts, checks, pass/fail.
