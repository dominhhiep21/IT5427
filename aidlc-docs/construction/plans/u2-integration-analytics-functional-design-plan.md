# Kế hoạch Functional Design — U2 Integration & Analytics

**Unit**: U2 — Integration & Analytics
**Story**: US-08 → US-14, US-19 (8 story)
**Giai đoạn**: CONSTRUCTION - Functional Design (Planning)

## 1. Bối cảnh

U2 nhận `data/cleaned/*.parquet` từ U1 và tạo:

- Dữ liệu tham chiếu IBGE (27 bang → 5 vùng).
- Star schema: dimension + fact.
- DuckDB catalog/view trên Parquet.
- Analytics API cho KPI doanh thu, danh mục, vùng, top seller/product, giao trễ.

**Phụ thuộc**: U1 hoàn tất; cleaned Parquet + quality report.
**Đầu ra cho U3**: `data/marts/*.parquet`, `warehouse/olist.duckdb`, hàm analytics.

## 2. Mô hình star schema đề xuất

### Dimensions
- `dim_customer`: `customer_id` (PK), `customer_unique_id`, zip, city, state, region.
- `dim_product`: `product_id` (PK), category, category_english, flags.
- `dim_seller`: `seller_id` (PK), zip, city, state, region.
- `dim_geography`: `zip_code_prefix` (PK), lat/lng, city, state, region.
- `dim_date`: `date_key` (PK), date, year, quarter, month, day, weekday.

### Facts
- `fact_order_items`: grain `(order_id, order_item_id)`; customer/product/seller/date keys; price, freight, item_total, price_outlier.
- `fact_orders`: grain `order_id`; customer/date keys; status, is_delivered, delivery_days, is_late, has_items, has_payment, has_review.
- `fact_payments`: grain `(order_id, payment_sequential)`; type, installments, value.
- `fact_reviews`: grain `(review_id, order_id)`; score, dates, multiple flag.

### Quan hệ
- `fact_order_items` → dim_customer, dim_product, dim_seller, dim_date.
- `fact_orders` → dim_customer, dim_date.
- `fact_payments` / `fact_reviews` → fact_orders (order_id) và dim_date.

## 3. Analytics đề xuất

- `kpi_summary(filters)`: doanh thu, số đơn, AOV, tỷ lệ giao trễ.
- `revenue_by_period(filters, granularity)`: tháng/quý/năm.
- `revenue_by_dimension(filters, dimension)`: category/region/state.
- `top_entities(filters, entity, limit)`: product/seller.
- `delivery_kpis(filters, group_by)`: state/category/month.

## 4. Câu hỏi cần trả lời

Vui lòng điền chữ cái sau mỗi `[Answer]:`. Khi hoàn tất, trả lời `done`.

### Câu 1 — Grain của dim_customer
Chọn grain dimension khách hàng:

A) `customer_id` (theo đơn), kèm `customer_unique_id`; phân tích mua lặp dùng unique_id (khuyến nghị)
B) `customer_unique_id` (theo người), cần bridge table để nối order
C) Hai dimension riêng: `dim_customer_order` và `dim_customer_unique`
X) Khác (vui lòng mô tả sau thẻ [Answer]:)

[Answer]: A

### Câu 2 — Khóa dimension/fact
Dùng loại khóa nào?

A) Natural key (string ID gốc) để truy vết (khuyến nghị)
B) Surrogate key số nguyên cho mọi dimension
C) Natural key cho fact, surrogate key cho dimension
X) Khác (vui lòng mô tả sau thẻ [Answer]:)

[Answer]: A

### Câu 3 — Nguồn dữ liệu IBGE
Cách lấy dữ liệu IBGE:

A) Gọi API chính thức IBGE (estados/municipios), cache JSON/CSV (khuyến nghị)
B) Tải file CSV/JSON chính thức từ website IBGE
C) Đóng gói sẵn bảng 27 bang → 5 vùng trong repo, không gọi mạng
X) Khác (vui lòng mô tả sau thẻ [Answer]:)

[Answer]: A

### Câu 4 — Phục vụ analytics
Cách tổ chức lớp analytics:

A) View DuckDB trên fact/dim + pre-aggregate các KPI phổ biến (khuyến nghị)
B) Chỉ view DuckDB, tính on-the-fly
C) Chỉ bảng KPI tổng hợp sẵn, không view chi tiết
X) Khác (vui lòng mô tả sau thẻ [Answer]:)

[Answer]: A

### Câu 5 — Xử lý giai đoạn 2016
Dữ liệu 2016 chỉ có 329 đơn:

A) Giữ trong mart, gắn cờ `is_sparse_period` và hiển thị cảnh báo (khuyến nghị)
B) Loại 2016 khỏi mart phân tích
C) Giữ nhưng không gắn cờ
X) Khác (vui lòng mô tả sau thẻ [Answer]:)

[Answer]: A

## 5. Checklist

- [x] Đọc unit definition, story map, U1 cleaned schema
- [x] Đề xuất star schema và analytics
- [x] Tạo kế hoạch và câu hỏi
- [x] Thu thập câu trả lời
- [x] Phân tích mơ hồ/mâu thuẫn
- [x] Tạo `business-logic-model.md`, `business-rules.md`, `domain-entities.md`
- [x] Cập nhật state và trình bày phê duyệt
