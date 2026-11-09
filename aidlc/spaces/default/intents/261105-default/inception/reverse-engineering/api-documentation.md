# Tài liệu API và mô hình dữ liệu (API Documentation)

> Không có REST API hay internal API trong workspace. Tài liệu này mô tả **hợp đồng dữ liệu** của 9 CSV — tương đương API đầu vào của pipeline tương lai.

## REST APIs

Không có.

## Internal APIs

Không có.

## Mô hình dữ liệu

### `olist_orders_dataset.csv` — 99.441 dòng
- **Khóa chính**: `order_id` (duy nhất).
- **Quan hệ**: `customer_id` → `olist_customers_dataset.customer_id` (1:1 theo đơn); `order_id` → items/payments/reviews (1:N).
- **Trường**:

| Trường | Kiểu | Ghi chú |
|---|---|---|
| `order_id` | string | PK |
| `customer_id` | string | FK, duy nhất theo đơn |
| `order_status` | string | 8 trạng thái; `delivered` chiếm 96.478 |
| `order_purchase_timestamp` | string datetime | Bắt đầu vòng đời đơn |
| `order_approved_at` | string datetime | Null 160 |
| `order_delivered_carrier_date` | string datetime | Null 1.783 |
| `order_delivered_customer_date` | string datetime | Null 2.965 |
| `order_estimated_delivery_date` | string datetime | Hạn giao dự kiến |

- **Validation**: `order_id` unique; `order_purchase_timestamp` luôn có; không có trường hợp giao trước khi mua.

### `olist_customers_dataset.csv` — 99.441 dòng
- **Khóa chính**: `customer_id` (duy nhất).
- **Quan hệ**: `customer_unique_id` là định danh người thật (96.096 giá trị); zip code → geolocation.

| Trường | Kiểu | Ghi chú |
|---|---|---|
| `customer_id` | string | PK, theo từng đơn |
| `customer_unique_id` | string | Dùng cho phân tích khách hàng |
| `customer_zip_code_prefix` | int | 5 chữ số đầu của CEP |
| `customer_city` | string | Tên thành phố, có biến thể chính tả |
| `customer_state` | string | 27 bang |

### `olist_order_items_dataset.csv` — 112.650 dòng
- **Khóa chính**: `(order_id, order_item_id)`.
- **Quan hệ**: `order_id` → orders; `product_id` → products; `seller_id` → sellers.

| Trường | Kiểu | Ghi chú |
|---|---|---|
| `order_id` | string | FK |
| `order_item_id` | int | Thứ tự dòng hàng |
| `product_id` | string | FK |
| `seller_id` | string | FK |
| `shipping_limit_date` | string datetime | Hạn bàn giao cho carrier |
| `price` | float | Giá sản phẩm |
| `freight_value` | float | Phí vận chuyển |

- **Validation**: không trùng khóa; 775 đơn không có dòng hàng.

### `olist_order_payments_dataset.csv` — 103.886 dòng
- **Khóa chính**: `(order_id, payment_sequential)`.
- **Quan hệ**: `order_id` → orders (1:N).

| Trường | Kiểu | Ghi chú |
|---|---|---|
| `order_id` | string | FK |
| `payment_sequential` | int | Thứ tự giao dịch |
| `payment_type` | string | credit_card, boleto, voucher, debit_card, not_defined |
| `payment_installments` | int | Tối đa 24 kỳ |
| `payment_value` | float | Giá trị giao dịch |

- **Validation**: 99.440 đơn có thanh toán; 1 đơn không có.

### `olist_order_reviews_dataset.csv` — 99.224 dòng
- **Khóa chính**: `review_id` **không duy nhất** (98.410 giá trị).
- **Quan hệ**: `order_id` → orders; 547 đơn có nhiều đánh giá (551 dòng review dư).

| Trường | Kiểu | Ghi chú |
|---|---|---|
| `review_id` | string | Có 814 giá trị trùng |
| `order_id` | string | FK |
| `review_score` | int | 1-5; trung bình ~4,09 |
| `review_comment_title` | string | Null 87.656 |
| `review_comment_message` | string | Null 58.247 |
| `review_creation_date` | string datetime | Ngày tạo đánh giá |
| `review_answer_timestamp` | string datetime | Thời điểm phản hồi; trung vị ~40,2 giờ sau tạo |

### `olist_products_dataset.csv` — 32.951 dòng
- **Khóa chính**: `product_id`.
- **Quan hệ**: `product_category_name` → translation (73 giá trị, thiếu 2 bản dịch).

| Trường | Kiểu | Ghi chú |
|---|---|---|
| `product_id` | string | PK |
| `product_category_name` | string | Null 610 |
| `product_name_lenght` | float | Tên cột gốc viết sai chính tả `lenght` |
| `product_description_lenght` | float | Null cùng 610 dòng |
| `product_photos_qty` | float | Null cùng 610 dòng |
| `product_weight_g` | float | Null 2 |
| `product_length_cm` | float | Null 2 |
| `product_height_cm` | float | Null 2 |
| `product_width_cm` | float | Null 2 |

### `olist_sellers_dataset.csv` — 3.095 dòng
- **Khóa chính**: `seller_id`.
- **Quan hệ**: zip code → geolocation; `seller_id` → order_items.

| Trường | Kiểu | Ghi chú |
|---|---|---|
| `seller_id` | string | PK |
| `seller_zip_code_prefix` | int | 7 seller zip không có geolocation |
| `seller_city` | string | Tên thành phố |
| `seller_state` | string | 23 bang |

### `olist_geolocation_dataset.csv` — 1.000.163 dòng
- **Khóa chính**: Không có; nhiều dòng cho một `geolocation_zip_code_prefix` (trung bình 52,6 dòng/zip).
- **Quan hệ**: zip code → customers/sellers; phải aggregate trước khi join.

| Trường | Kiểu | Ghi chú |
|---|---|---|
| `geolocation_zip_code_prefix` | int | 19.015 zip duy nhất |
| `geolocation_lat` | float | Ngoại lai: -36,6 đến 45,1 |
| `geolocation_lng` | float | Ngoại lai: -101,5 đến 121,1 |
| `geolocation_city` | string | Tối đa 5 biến thể tên cho một zip |
| `geolocation_state` | string | Bang |

- **Validation**: 261.831 dòng trùng hoàn toàn; join trực tiếp gây bùng nổ số dòng.

### `product_category_name_translation.csv` — 71 dòng
- **Khóa chính**: `product_category_name`.
- **Quan hệ**: 1:1 với category của products.

| Trường | Kiểu | Ghi chú |
|---|---|---|
| `product_category_name` | string | Tên Bồ Đào Nha |
| `product_category_name_english` | string | Tên tiếng Anh |

- **Validation**: thiếu `pc_gamer` và `portateis_cozinha_e_preparadores_de_alimentos`.

## Quy tắc tích hợp đề xuất

1. Chuẩn hóa `customer_id` → `customer_unique_id` khi phân tích khách hàng.
2. Aggregate payments/reviews về grain `order_id` trước khi join với items.
3. Aggregate geolocation về một dòng/zip trước khi join.
4. Giữ `order_status` và cờ `is_delivered` thay vì xóa đơn không giao.
5. Left join category translation và gán nhãn `unknown` cho 2 danh mục thiếu.
