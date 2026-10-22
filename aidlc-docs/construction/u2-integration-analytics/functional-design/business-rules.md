# Business Rules — U2 Integration & Analytics

## Nhóm A — Dữ liệu tham chiếu IBGE

### BR-U2-01 — Tải và cache IBGE
- **Quy tắc**:
  1. Nếu `dataset/external/ibge/estados.json` tồn tại, có 27 bang và metadata hợp lệ → dùng cache.
  2. Nếu không, gọi API estados và municipios; lưu JSON + metadata (URL, fetched_at, sha256, row count).
  3. Không có cache + API lỗi → `ExternalSourceError`, dừng.
- **Không** gọi API mỗi lần chạy nếu cache hợp lệ.
- **Kiểm thử**: cache hit không gọi mạng; cache thiếu + mạng lỗi → exception.

### BR-U2-02 — Ánh xạ 27 bang → 5 vùng
- **Quy tắc**: `region_map` có đúng 27 state (uppercase 2 ký tự), 5 region chính thức.
- **Kiểm tra**: unique state; không null; mọi state trong customers/sellers phải có region.
- **Baseline**: 27 state, 5 region.
- **Kiểm thử**: state lạ → `ExternalSourceError`.

## Nhóm B — Dimensions

### BR-U2-03 — Grain dim_customer
- **Quy tắc**: `dim_customer` grain `customer_id` (99.441). Giữ `customer_unique_id` (96.096 unique).
- **Mua lặp lại**: dùng `COUNT(DISTINCT customer_unique_id)`, không dùng `customer_id`.
- **Không** gộp nhiều `customer_id` vào một dòng.
- **Kiểm thử**: 99.441 dòng; 96.096 unique_id; join fact không nhân bản.

### BR-U2-04 — Natural keys
- **Quy tắc**: Dùng ID gốc làm khóa:
  - `customer_id`, `product_id`, `seller_id`, `zip_code_prefix`, `date_key` (YYYY-MM-DD), `order_id`, `review_id`.
- **Không** tạo surrogate key số nguyên.
- **Lý do**: Truy vết trực tiếp về nguồn; đơn giản hóa DuckDB/Parquet.

### BR-U2-05 — dim_date
- **Quy tắc**: Sinh đủ 774 ngày từ 2016-09-04 đến 2018-10-17.
- `date_key = YYYY-MM-DD`.
- `is_sparse_period = (year == 2016)`.
- Có year, quarter, month, day, weekday.
- **Kiểm thử**: 774 dòng; 2016-12-31 sparse=true; 2017-01-01 sparse=false.

### BR-U2-06 — dim_product / dim_seller / dim_geography
- `dim_product` 32.951; giữ cờ category.
- `dim_seller` 3.095; region từ state.
- `dim_geography` 19.015; 5 zip null tọa độ vẫn giữ.
- **Kiểm thử**: row counts; region không null.

## Nhóm C — Facts

### BR-U2-07 — Grain fact
- `fact_order_items`: `(order_id, order_item_id)` — 112.650.
- `fact_orders`: `order_id` — 99.441.
- `fact_payments`: `(order_id, payment_sequential)` — 103.886.
- `fact_reviews`: `(review_id, order_id)` — 99.224.
- **Không** join payment/review trực tiếp vào fact_order_items.
- **Kiểm thử**: số dòng từng fact; join item × dims không đổi 112.650.

### BR-U2-08 — item_total
- **Quy tắc**: `item_total = price + freight_value` (null → 0).
- **Không** dùng `payment_value` trong fact_order_items.
- **Kiểm thử**: tổng all-status = 15.843.553,24 BRL.

### BR-U2-09 — delivery_days và is_late
- **Quy tắc**:
  - `delivery_days = (delivered_customer_date - order_purchase_timestamp).days`.
  - `is_late = is_delivered AND delivered_customer_date > estimated_delivery_date`.
- Đơn không delivered: `delivery_days = null`, `is_late = false`.
- **Baseline**: 7.826 đơn trễ / 96.478 delivered = 8,11%.
- **Kiểm thử**: tổng is_late = 7.826; đơn canceled có delivered date không bị tính.

### BR-U2-10 — Cờ order-level
- `has_items = order_id có trong fact_order_items`.
- `has_payment = order_id có trong fact_payments`.
- `has_review = order_id có trong fact_reviews`.
- **Baseline**: 775 không item; 1 không payment.
- **Không** xóa order thiếu item/payment.

### BR-U2-11 — Date key
- Fact order/items: `date_key` từ `order_purchase_timestamp`.
- Fact payments: cùng ngày mua của order.
- Fact reviews: từ `review_creation_date`.
- **Không** dùng ngày giao cho doanh thu.

## Nhóm D — Analytics

### BR-U2-12 — Doanh thu mặc định
- **Quy tắc**: `SUM(item_total)` trên đơn `delivered`.
- Doanh thu thanh toán `SUM(payment_value)` chỉ dùng đối soát.
- **Baseline delivered**: 15.419.773,75 BRL; all-status: 15.843.553,24 BRL.
- **Kiểm thử**: `kpi_summary` mặc định khớp delivered.

### BR-U2-13 — AOV
- **Quy tắc**: `AOV = revenue / COUNT(DISTINCT order_id)` trên cùng tập filtered.
- **Baseline delivered**: 159,83 BRL.
- **Không** chia cho số dòng item.

### BR-U2-14 — Tỷ lệ giao trễ
- **Quy tắc**: `late_orders / delivered_orders`; mẫu số chỉ đơn delivered.
- **Baseline**: 8,11%.
- **Không** đưa đơn canceled/shipped vào mẫu số.

### BR-U2-15 — Filters
- `KpiFilters`: start_date, end_date, state, region, category, order_status (mặc định delivered).
- Date lọc trên `date_key` (ngày mua).
- Category lọc trên `dim_product.category`.
- State/region lọc trên dim customer/geography.
- **Kiểm thử**: filter không có dữ liệu → DataFrame rỗng, không lỗi.

### BR-U2-16 — Top entity
- Xếp hạng theo doanh thu delivered.
- Tie-break theo ID tăng dần.
- `limit` mặc định 10.
- **Không** đưa entity không có đơn delivered vào top.

### BR-U2-17 — 2016 sparse
- Giữ toàn bộ 2016; `is_sparse_period = true`.
- KPI theo tháng trả cờ; dashboard hiển thị cảnh báo.
- **Không** nội suy hoặc loại bỏ.

### BR-U2-18 — Pre-aggregation
- `agg_sales_daily` và `agg_delivery_daily` được tính lại mỗi lần integrate.
- Grain `(date_key, state, region, category)`.
- Dashboard dùng agg cho bộ lọc phổ biến; ad hoc dùng view fact.
- **Kiểm thử**: tổng revenue từ agg = tổng từ fact.

### BR-U2-19 — DuckDB view
- View đọc Parquet, không copy.
- Tên view `v_*`.
- Analytics không đọc CSV.
- **Kiểm thử**: query view trả cùng số dòng fact.

### BR-U2-20 — Read-only analytics
- Analytics chỉ SELECT; không ghi mart.
- Dashboard không sửa dữ liệu.
- **Kiểm thử**: không có lệnh INSERT/UPDATE trong module analytics.

### BR-U2-21 — Idempotency
- Chạy integrate lại tạo cùng nội dung logic.
- Ghi atomic từng mart.
- Không append trùng.
- **Kiểm thử**: chạy 2 lần, row count không đổi.

### BR-U2-22 — KPI reconciliation
- So sánh KPI tính từ fact với baseline trong tài liệu.
- Sai lệch > 0,01 → fail test.
- **Baseline**: revenue delivered, orders, AOV, late rate.
