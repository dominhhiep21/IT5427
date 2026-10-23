# Data Dictionary

## Dimensions

### dim_customer
Grain: `customer_id` (99.441).

| Cột | Kiểu | Mô tả |
|---|---|---|
| customer_id | string | PK, theo đơn |
| customer_unique_id | string | định danh người |
| zip_code_prefix | int | CEP |
| city | string | thành phố gốc |
| city_normalized | string | chuẩn hóa |
| state | string | bang |
| region | string | vùng IBGE |

### dim_product
Grain: `product_id` (32.951).

| Cột | Kiểu | Mô tả |
|---|---|---|
| product_id | string | PK |
| category | string | danh mục, `unknown` nếu thiếu |
| category_english | string | bản dịch/fallback |
| category_missing | bool | 610 sản phẩm |
| translation_missing | bool | 13 sản phẩm / 2 danh mục |

### dim_seller
Grain: `seller_id` (3.095).

| Cột | Kiểu | Mô tả |
|---|---|---|
| seller_id | string | PK |
| zip_code_prefix | int | CEP |
| city | string | thành phố |
| city_normalized | string | chuẩn hóa |
| state | string | bang |
| region | string | vùng IBGE |

### dim_geography
Grain: `zip_code_prefix` (19.015).

| Cột | Kiểu | Mô tả |
|---|---|---|
| zip_code_prefix | int | PK |
| lat_median | float | trung vị lat; null 5 zip |
| lng_median | float | trung vị lng; null 5 zip |
| city_mode | string | city phổ biến |
| state_mode | string | state phổ biến |
| region | string | vùng IBGE |

### dim_date
Grain: ngày (774).

| Cột | Kiểu | Mô tả |
|---|---|---|
| date_key | string | PK, YYYY-MM-DD |
| date | date | ngày |
| year / quarter / month / day / weekday | int | thuộc tính |
| is_sparse_period | bool | true cho 2016 |

## Facts

### fact_order_items
Grain: `(order_id, order_item_id)` — 112.650.

| Cột | Kiểu | Mô tả |
|---|---|---|
| order_id, order_item_id | string/int | khóa |
| customer_id, product_id, seller_id | string | FK |
| date_key | string | ngày mua |
| price, freight_value, item_total | float | doanh thu |
| price_outlier | bool | IQR 1.5 |
| order_status, is_delivered | string/bool | degenerate |

### fact_orders
Grain: `order_id` — 99.441.

| Cột | Kiểu | Mô tả |
|---|---|---|
| order_id | string | PK |
| customer_id | string | FK |
| date_key | string | ngày mua |
| category | string | category đại diện |
| order_status, is_delivered | string/bool | trạng thái |
| delivered_customer_date, estimated_delivery_date | datetime | mốc giao |
| delivery_days | float | số ngày |
| is_late | bool | chỉ delivered |
| has_items / has_payment / has_review | bool | cờ |

### fact_payments
Grain: `(order_id, payment_sequential)` — 103.886.

| Cột | Kiểu | Mô tả |
|---|---|---|
| order_id, payment_sequential | string/int | khóa |
| date_key | string | ngày mua |
| payment_type | string | phương thức |
| payment_installments | int | số kỳ |
| payment_value | float | giá trị |

### fact_reviews
Grain: `(review_id, order_id)` — 99.224.

| Cột | Kiểu | Mô tả |
|---|---|---|
| review_id, order_id | string | khóa |
| date_key | string | ngày tạo review |
| review_score | int | 1-5 |
| multiple_reviews_per_order | bool | 547 đơn |

## Aggregates

### agg_sales_daily
Grain: `(date_key, state, region, category)`.

| Cột | Mô tả |
|---|---|
| revenue | tổng item_total delivered |
| orders | distinct order_id |
| items | số dòng hàng |
| freight | tổng freight |
| is_sparse_period | 2016 |

### agg_delivery_daily
Grain: `(date_key, state, region, category)`.

| Cột | Mô tả |
|---|---|
| delivered_orders | số đơn delivered |
| late_orders | số đơn trễ |
| delivery_days_sum | tổng ngày giao |
| is_sparse_period | 2016 |
