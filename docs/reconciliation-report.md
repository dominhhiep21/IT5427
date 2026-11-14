# Báo cáo đối soát chỉ số

> Tệp này do `python -X utf8 -m src.analytics` sinh ra. Không sửa tay: sửa kiểm tra trong `src/analytics/reconciliation.py` rồi chạy lại.

Phạm vi: mục 16 của bảng phân công — kiểm tra tổng tiền và số đơn, bảo đảm không đếm trùng do JOIN.

**Kết luận: ĐẠT.** 8 kiểm tra đạt, 0 không đạt, 9 mục ghi nhận, 0 bỏ qua.

Cách đọc trạng thái: **Đạt / KHÔNG ĐẠT** là kiểm tra có đúng–sai. **Ghi nhận** là minh họa một cái bẫy hoặc một khác biệt có lý do nghiệp vụ; nó không sai, nhưng người đọc KPI phải biết.

Phương pháp: tính cùng một con số bằng nhiều đường độc lập rồi so với nhau. Đường 'nguồn' đọc thẳng CSV gốc trong `dataset/` bằng DuckDB, không đi qua pipeline.

## Tổng hợp

| Mã | Nhóm | Kiểm tra | Trạng thái |
| --- | --- | --- | --- |
| DS-01 | A. Cấu trúc | Grain của bốn bảng fact | Đạt |
| DS-02 | A. Cấu trúc | Khóa của dimension là duy nhất | Đạt |
| DS-03 | A. Cấu trúc | Không có khóa ngoại mồ côi | Đạt |
| DS-04 | B. Nguồn ↔ kho | Số dòng: CSV gốc = bảng fact | Đạt |
| DS-05 | B. Nguồn ↔ kho | Doanh thu delivered tính bằng nhiều đường | Đạt |
| DS-06 | B. Nguồn ↔ kho | Số đơn delivered đếm bằng nhiều đường | Đạt |
| DS-07 | B. Nguồn ↔ kho | Số đơn giao trễ tính bằng nhiều đường | Đạt |
| DS-08 | B. Nguồn ↔ kho | KPI khớp baseline đã chốt | Đạt |
| DS-09 | C. Bẫy đếm trùng | Bẫy JOIN: dòng hàng × thanh toán | Ghi nhận |
| DS-10 | C. Bẫy đếm trùng | Bẫy JOIN: dòng hàng × đánh giá | Ghi nhận |
| DS-11 | C. Bẫy đếm trùng | Số đơn không cộng dồn được qua danh mục | Ghi nhận |
| DS-12 | C. Bẫy đếm trùng | AOV là tỷ số: không lấy trung bình của trung bình | Ghi nhận |
| DS-13 | D. Khác biệt đã biết | Tiền hàng so với tiền thanh toán theo từng đơn | Ghi nhận |
| DS-14 | D. Khác biệt đã biết | Độ nhạy của định nghĩa 'giao trễ' | Ghi nhận |
| DS-15 | D. Khác biệt đã biết | Đơn delivered thiếu ngày giao thực tế | Ghi nhận |
| DS-16 | D. Khác biệt đã biết | Đánh giá: đếm theo dòng hay theo đơn | Ghi nhận |
| DS-17 | D. Khác biệt đã biết | Hai cách đếm số đơn theo danh mục | Ghi nhận |

## A. Cấu trúc

### DS-01 — Grain của bốn bảng fact

**Trạng thái:** Đạt

**Vì sao kiểm tra:** Mỗi bảng fact phải đúng một dòng cho một khóa grain; có dòng trùng thì mọi phép SUM đều sai.

| Đại lượng | Giá trị |
| --- | ---: |
| `item_rows` | 112.650 |
| `item_keys` | 112.650 |
| `order_rows` | 99.441 |
| `order_keys` | 99.441 |
| `payment_rows` | 103.886 |
| `payment_keys` | 103.886 |
| `review_rows` | 99.224 |
| `review_keys` | 99.224 |

**Kết luận:** Cả bốn fact đúng grain: 112.650 dòng hàng, 99.441 đơn, 103.886 dòng thanh toán, 99.224 dòng đánh giá; số dòng bằng số khóa phân biệt.

<details><summary>Câu SQL</summary>

```sql
SELECT
    (SELECT COUNT(*) FROM v_fact_order_items) AS item_rows,
    (SELECT COUNT(*) FROM (SELECT DISTINCT order_id, order_item_id FROM v_fact_order_items)) AS item_keys,
    (SELECT COUNT(*) FROM v_fact_orders) AS order_rows,
    (SELECT COUNT(DISTINCT order_id) FROM v_fact_orders) AS order_keys,
    (SELECT COUNT(*) FROM v_fact_payments) AS payment_rows,
    (SELECT COUNT(*) FROM (SELECT DISTINCT order_id, payment_sequential FROM v_fact_payments)) AS payment_keys,
    (SELECT COUNT(*) FROM v_fact_reviews) AS review_rows,
    (SELECT COUNT(*) FROM (SELECT DISTINCT review_id, order_id FROM v_fact_reviews)) AS review_keys
```

</details>

### DS-02 — Khóa của dimension là duy nhất

**Trạng thái:** Đạt

**Vì sao kiểm tra:** JOIN fact với dimension chỉ an toàn (không nhân dòng) khi khóa dimension không trùng.

| Đại lượng | Giá trị |
| --- | ---: |
| `duplicate_customers` | 0 |
| `duplicate_products` | 0 |
| `duplicate_sellers` | 0 |
| `duplicate_dates` | 0 |

**Kết luận:** Bốn dimension dùng để ghép (khách hàng, sản phẩm, người bán, ngày) đều có khóa duy nhất, nên JOIN fact → dimension là quan hệ nhiều–một và không nhân bản dòng.

<details><summary>Câu SQL</summary>

```sql
SELECT
    (SELECT COUNT(*) - COUNT(DISTINCT customer_id) FROM v_dim_customer) AS duplicate_customers,
    (SELECT COUNT(*) - COUNT(DISTINCT product_id) FROM v_dim_product) AS duplicate_products,
    (SELECT COUNT(*) - COUNT(DISTINCT seller_id) FROM v_dim_seller) AS duplicate_sellers,
    (SELECT COUNT(*) - COUNT(DISTINCT date_key) FROM v_dim_date) AS duplicate_dates
```

</details>

### DS-03 — Không có khóa ngoại mồ côi

**Trạng thái:** Đạt

**Vì sao kiểm tra:** Truy vấn phân tích dùng INNER JOIN; một dòng fact không tìm thấy dimension sẽ bị rơi âm thầm và doanh thu bị thiếu.

| Đại lượng | Giá trị |
| --- | ---: |
| `items_without_order` | 0 |
| `items_without_product` | 0 |
| `items_without_seller` | 0 |
| `items_without_customer` | 0 |
| `items_without_date` | 0 |
| `orders_without_customer` | 0 |
| `orders_without_date` | 0 |
| `payments_without_order` | 0 |
| `reviews_without_order` | 0 |

**Kết luận:** Mọi dòng fact đều tìm thấy dimension tương ứng, nên INNER JOIN không làm rơi dòng nào.

<details><summary>Câu SQL</summary>

```sql
SELECT
    (SELECT COUNT(*) FROM v_fact_order_items l LEFT JOIN v_fact_orders r ON l.order_id = r.order_id WHERE r.order_id IS NULL) AS items_without_order,
    (SELECT COUNT(*) FROM v_fact_order_items l LEFT JOIN v_dim_product r ON l.product_id = r.product_id WHERE r.product_id IS NULL) AS items_without_product,
    (SELECT COUNT(*) FROM v_fact_order_items l LEFT JOIN v_dim_seller r ON l.seller_id = r.seller_id WHERE r.seller_id IS NULL) AS items_without_seller,
    (SELECT COUNT(*) FROM v_fact_order_items l LEFT JOIN v_dim_customer r ON l.customer_id = r.customer_id WHERE r.customer_id IS NULL) AS items_without_customer,
    (SELECT COUNT(*) FROM v_fact_order_items l LEFT JOIN v_dim_date r ON l.date_key = r.date_key WHERE r.date_key IS NULL) AS items_without_date,
    (SELECT COUNT(*) FROM v_fact_orders l LEFT JOIN v_dim_customer r ON l.customer_id = r.customer_id WHERE r.customer_id IS NULL) AS orders_without_customer,
    (SELECT COUNT(*) FROM v_fact_orders l LEFT JOIN v_dim_date r ON l.date_key = r.date_key WHERE r.date_key IS NULL) AS orders_without_date,
    (SELECT COUNT(*) FROM v_fact_payments l LEFT JOIN v_fact_orders r ON l.order_id = r.order_id WHERE r.order_id IS NULL) AS payments_without_order,
    (SELECT COUNT(*) FROM v_fact_reviews l LEFT JOIN v_fact_orders r ON l.order_id = r.order_id WHERE r.order_id IS NULL) AS reviews_without_order
```

</details>

## B. Nguồn ↔ kho

### DS-04 — Số dòng: CSV gốc = bảng fact

**Trạng thái:** Đạt

**Vì sao kiểm tra:** Pipeline không được làm mất hay sinh thêm dòng so với nguồn (làm sạch bằng cờ, không xóa dòng).

| Đại lượng | Giá trị |
| --- | ---: |
| `source_orders` | 99.441 |
| `fact_orders` | 99.441 |
| `source_items` | 112.650 |
| `fact_items` | 112.650 |
| `source_payments` | 103.886 |
| `fact_payments` | 103.886 |
| `source_reviews` | 99.224 |
| `fact_reviews` | 99.224 |

**Kết luận:** Khớp cả bốn bảng: 99.441 đơn, 112.650 dòng hàng, 103.886 thanh toán, 99.224 đánh giá.

<details><summary>Câu SQL</summary>

```sql
SELECT
    (SELECT COUNT(*) FROM src_orders) AS source_orders,
    (SELECT COUNT(*) FROM v_fact_orders) AS fact_orders,
    (SELECT COUNT(*) FROM src_order_items) AS source_items,
    (SELECT COUNT(*) FROM v_fact_order_items) AS fact_items,
    (SELECT COUNT(*) FROM src_payments) AS source_payments,
    (SELECT COUNT(*) FROM v_fact_payments) AS fact_payments,
    (SELECT COUNT(*) FROM src_reviews) AS source_reviews,
    (SELECT COUNT(*) FROM v_fact_reviews) AS fact_reviews
```

</details>

### DS-05 — Doanh thu delivered tính bằng nhiều đường

**Trạng thái:** Đạt

**Vì sao kiểm tra:** Cùng một định nghĩa doanh thu (price + freight_value của đơn delivered) phải cho cùng một số dù tính từ đâu.

| Đại lượng | Giá trị |
| --- | ---: |
| `fact_revenue` | 15.419.773,75 |
| `aggregate_revenue` | 15.419.773,75 |
| `source_revenue` | 15.419.773,75 |

**Kết luận:** Tính từ CSV gốc, bảng fact và bảng aggregate đều ra 15.419.773,75 BRL.

<details><summary>Câu SQL</summary>

```sql
SELECT
    (SELECT ROUND(SUM(item_total), 2) FROM v_fact_order_items WHERE is_delivered) AS fact_revenue,
    (SELECT ROUND(SUM(revenue), 2) FROM v_agg_sales_daily) AS aggregate_revenue,
    (SELECT ROUND(SUM(CAST(i.price AS DOUBLE) + CAST(i.freight_value AS DOUBLE)), 2)
     FROM src_order_items i JOIN src_orders o ON i.order_id = o.order_id
     WHERE o.order_status = 'delivered') AS source_revenue
```

</details>

### DS-06 — Số đơn delivered đếm bằng nhiều đường

**Trạng thái:** Đạt

**Vì sao kiểm tra:** Số đơn là mẫu số của AOV và tỷ lệ giao trễ; đếm ở grain đơn và đếm DISTINCT ở grain dòng hàng phải bằng nhau.

| Đại lượng | Giá trị |
| --- | ---: |
| `fact_orders` | 96.478 |
| `orders_from_items` | 96.478 |
| `aggregate_orders` | 96.478 |
| `source_orders` | 96.478 |

**Kết luận:** Mọi đường đếm đều ra 96.478 đơn delivered.

<details><summary>Câu SQL</summary>

```sql
SELECT
    (SELECT COUNT(*) FROM v_fact_orders WHERE is_delivered) AS fact_orders,
    (SELECT COUNT(DISTINCT order_id) FROM v_fact_order_items WHERE is_delivered) AS orders_from_items,
    (SELECT CAST(SUM(delivered_orders) AS BIGINT) FROM v_agg_delivery_daily) AS aggregate_orders,
    (SELECT COUNT(*) FROM src_orders WHERE order_status = 'delivered') AS source_orders
```

</details>

### DS-07 — Số đơn giao trễ tính bằng nhiều đường

**Trạng thái:** Đạt

**Vì sao kiểm tra:** Cờ is_late trong kho phải khớp với việc so trực tiếp hai mốc thời gian trong CSV gốc.

| Đại lượng | Giá trị |
| --- | ---: |
| `fact_late_orders` | 7.826 |
| `aggregate_late_orders` | 7.826 |
| `source_late_orders` | 7.826 |

**Kết luận:** Mọi đường tính đều ra 7.826 đơn giao trễ.

<details><summary>Câu SQL</summary>

```sql
SELECT
    (SELECT CAST(COALESCE(SUM(is_late::INT), 0) AS BIGINT) FROM v_fact_orders WHERE is_delivered) AS fact_late_orders,
    (SELECT CAST(SUM(late_orders) AS BIGINT) FROM v_agg_delivery_daily) AS aggregate_late_orders,
    (SELECT COUNT(*) FROM src_orders
     WHERE order_status = 'delivered'
       AND TRY_CAST(order_delivered_customer_date AS TIMESTAMP)
           > TRY_CAST(order_estimated_delivery_date AS TIMESTAMP)) AS source_late_orders
```

</details>

### DS-08 — KPI khớp baseline đã chốt

**Trạng thái:** Đạt

**Vì sao kiểm tra:** Năm KPI chuẩn của nhóm (README, mục KPI baseline) là hợp đồng hồi quy: lệch quá dung sai là lỗi.

| Đại lượng | Giá trị |
| --- | ---: |
| `revenue_delivered` | 15.419.773,75 |
| `delivered_orders` | 96.478 |
| `aov` | 159,83 |
| `late_orders` | 7.826 |
| `late_rate_pct` | 8,11 |
| `baseline_revenue_delivered` | 15.419.773,75 |
| `baseline_delivered_orders` | 96.478 |
| `baseline_aov` | 159,83 |
| `baseline_late_orders` | 7.826 |
| `baseline_late_rate_pct` | 8,11 |

**Kết luận:** Khớp baseline: doanh thu 15.419.773,75 BRL, 96.478 đơn, AOV 159,83 BRL, 7.826 đơn trễ (8,11%).

<details><summary>Câu SQL</summary>

```sql
WITH sales AS (
    SELECT SUM(item_total) AS revenue, COUNT(DISTINCT order_id) AS orders
    FROM v_fact_order_items
    WHERE is_delivered
),
delivery AS (
    SELECT COUNT(*) AS delivered, COALESCE(SUM(is_late::INT), 0) AS late
    FROM v_fact_orders
    WHERE is_delivered
)
SELECT ROUND(s.revenue, 2) AS revenue_delivered,
       s.orders AS delivered_orders,
       ROUND(s.revenue / s.orders, 2) AS aov,
       CAST(d.late AS BIGINT) AS late_orders,
       ROUND(100.0 * d.late / d.delivered, 2) AS late_rate_pct
FROM sales s CROSS JOIN delivery d
```

</details>

## C. Bẫy đếm trùng

### DS-09 — Bẫy JOIN: dòng hàng × thanh toán

**Trạng thái:** Ghi nhận

**Vì sao kiểm tra:** Hai bảng đều nhiều dòng trên một đơn. Ghép thẳng qua order_id tạo tích Descartes trong từng đơn, doanh thu bị nhân lên.

| Đại lượng | Giá trị |
| --- | ---: |
| `correct_revenue` | 15.419.773,75 |
| `naive_join_revenue` | 16.114.019,06 |
| `item_rows` | 110.197 |
| `joined_rows` | 115.035 |
| `orders_with_many_payments` | 2.961 |
| `inflation` | 694.245,31 |
| `inflation_pct` | 4,50 |

**Kết luận:** JOIN thẳng cho 16.114.019,06 BRL thay vì 15.419.773,75 BRL: thừa 694.245,31 BRL (4,50%), vì 2.961 đơn có nhiều dòng thanh toán làm 110.197 dòng hàng phình thành 115.035 dòng. Cách đúng: gộp thanh toán về grain đơn trước rồi mới ghép, hoặc không ghép hai fact này.

<details><summary>Câu SQL</summary>

```sql
SELECT
    (SELECT ROUND(SUM(item_total), 2) FROM v_fact_order_items WHERE is_delivered) AS correct_revenue,
    (SELECT ROUND(SUM(f.item_total), 2)
     FROM v_fact_order_items f JOIN v_fact_payments p ON f.order_id = p.order_id
     WHERE f.is_delivered) AS naive_join_revenue,
    (SELECT COUNT(*) FROM v_fact_order_items WHERE is_delivered) AS item_rows,
    (SELECT COUNT(*)
     FROM v_fact_order_items f JOIN v_fact_payments p ON f.order_id = p.order_id
     WHERE f.is_delivered) AS joined_rows,
    (SELECT COUNT(*) FROM (SELECT order_id FROM v_fact_payments GROUP BY order_id HAVING COUNT(*) > 1)) AS orders_with_many_payments
```

</details>

### DS-10 — Bẫy JOIN: dòng hàng × đánh giá

**Trạng thái:** Ghi nhận

**Vì sao kiểm tra:** INNER JOIN với bảng đánh giá sai theo hai chiều cùng lúc: đơn không có đánh giá bị rơi, đơn nhiều đánh giá bị nhân.

| Đại lượng | Giá trị |
| --- | ---: |
| `correct_revenue` | 15.419.773,75 |
| `naive_join_revenue` | 15.361.245,11 |
| `delivered_without_review` | 646 |
| `orders_with_many_reviews` | 547 |
| `difference` | -58.528,64 |

**Kết luận:** JOIN thẳng cho 15.361.245,11 BRL, lệch -58.528,64 BRL so với 15.419.773,75 BRL: 646 đơn delivered không có đánh giá bị loại, trong khi 547 đơn có nhiều đánh giá bị đếm lặp. Hai sai số ngược chiều bù trừ nhau nên con số trông 'gần đúng' — loại lỗi khó phát hiện nhất.

<details><summary>Câu SQL</summary>

```sql
SELECT
    (SELECT ROUND(SUM(item_total), 2) FROM v_fact_order_items WHERE is_delivered) AS correct_revenue,
    (SELECT ROUND(SUM(f.item_total), 2)
     FROM v_fact_order_items f JOIN v_fact_reviews r ON f.order_id = r.order_id
     WHERE f.is_delivered) AS naive_join_revenue,
    (SELECT COUNT(*) FROM v_fact_orders WHERE is_delivered AND NOT has_review) AS delivered_without_review,
    (SELECT COUNT(*) FROM (SELECT order_id FROM v_fact_reviews GROUP BY order_id HAVING COUNT(*) > 1)) AS orders_with_many_reviews
```

</details>

### DS-11 — Số đơn không cộng dồn được qua danh mục

**Trạng thái:** Ghi nhận

**Vì sao kiểm tra:** Doanh thu là số đo cộng được; số đơn thì không, vì một đơn có thể chứa hàng của nhiều danh mục.

| Đại lượng | Giá trị |
| --- | ---: |
| `distinct_orders` | 96.478 |
| `summed_orders_in_aggregate` | 97.276 |
| `orders_with_many_categories` | 780 |
| `overcount` | 798 |

**Kết luận:** Cộng cột orders của agg_sales_daily ra 97.276, nhiều hơn 798 so với 96.478 đơn thật, do 780 đơn thuộc nhiều danh mục. Vì vậy số đơn tổng luôn được đếm DISTINCT ở grain gốc; bảng aggregate chỉ dùng cho doanh thu và cho số đơn trong một danh mục.

<details><summary>Câu SQL</summary>

```sql
SELECT
    (SELECT COUNT(DISTINCT order_id) FROM v_fact_order_items WHERE is_delivered) AS distinct_orders,
    (SELECT CAST(SUM(orders) AS BIGINT) FROM v_agg_sales_daily) AS summed_orders_in_aggregate,
    (SELECT COUNT(*) FROM (
        SELECT f.order_id
        FROM v_fact_order_items f JOIN v_dim_product p ON f.product_id = p.product_id
        WHERE f.is_delivered
        GROUP BY f.order_id HAVING COUNT(DISTINCT p.category) > 1)) AS orders_with_many_categories
```

</details>

### DS-12 — AOV là tỷ số: không lấy trung bình của trung bình

**Trạng thái:** Ghi nhận

**Vì sao kiểm tra:** KPI dạng tỷ số (AOV, tỷ lệ giao trễ) phải tính lại từ tử số và mẫu số, không lấy trung bình các nhóm.

| Đại lượng | Giá trị |
| --- | ---: |
| `aov_overall` | 159,83 |
| `mean_of_monthly_aov` | 154,39 |
| `months` | 23 |

**Kết luận:** AOV đúng (tổng doanh thu / tổng số đơn) là 159,83 BRL; nếu lấy trung bình AOV của 23 tháng thì ra 154,39 BRL — sai vì tháng ít đơn được tính nặng ngang tháng nhiều đơn.

<details><summary>Câu SQL</summary>

```sql
WITH monthly AS (
    SELECT d.year, d.month, SUM(f.item_total) AS revenue, COUNT(DISTINCT f.order_id) AS orders
    FROM v_fact_order_items f
    JOIN v_dim_date d ON f.date_key = d.date_key
    WHERE f.is_delivered
    GROUP BY d.year, d.month
)
SELECT ROUND(SUM(revenue) / SUM(orders), 2) AS aov_overall,
       ROUND(AVG(revenue / orders), 2) AS mean_of_monthly_aov,
       COUNT(*) AS months
FROM monthly
```

</details>

## D. Khác biệt đã biết

### DS-13 — Tiền hàng so với tiền thanh toán theo từng đơn

**Trạng thái:** Ghi nhận

**Vì sao kiểm tra:** Hai nguồn độc lập cùng mô tả giá trị đơn. Chúng gần bằng nhau thì định nghĩa doanh thu đáng tin; phần lệch phải được giải thích.

| Đại lượng | Giá trị |
| --- | ---: |
| `orders_compared` | 98.665 |
| `orders_mismatched` | 303 |
| `orders_off_by_one_cent` | 273 |
| `orders_paid_more` | 264 |
| `orders_paid_less` | 39 |
| `paid_more_installment_pct` | 94,32 |
| `item_total` | 15.843.409,78 |
| `payment_total` | 15.846.280,17 |
| `difference` | 2.870,39 |
| `max_abs_difference` | 182,81 |
| `mismatch_share_pct` | 0,31 |

**Kết luận:** So 98.665 đơn có cả dòng hàng và thanh toán (mỗi bên gộp về grain đơn trước): 303 đơn lệch từ 0,02 BRL trở lên (0,31%), thêm 273 đơn lệch đúng 0,01 BRL do làm tròn. Tổng lệch 2.870,39 BRL, lệch lớn nhất 182,81 BRL. Trong nhóm lệch, 264 đơn khách trả nhiều hơn tiền hàng và 94,32% số đó trả góp nhiều kỳ — phù hợp với giả thuyết lãi trả góp, nhưng dữ liệu không có cột lãi nên chưa khẳng định được. Vì hai nguồn lệch nhau, nhóm chọn dòng hàng làm định nghĩa doanh thu duy nhất.

<details><summary>Câu SQL</summary>

```sql
WITH items AS (
    SELECT order_id, SUM(item_total) AS item_total FROM v_fact_order_items GROUP BY order_id
),
pays AS (
    SELECT order_id, SUM(payment_value) AS paid, MAX(payment_installments) AS installments
    FROM v_fact_payments
    GROUP BY order_id
),
compared AS (
    SELECT i.item_total, p.paid, p.installments, ROUND(p.paid - i.item_total, 2) AS diff
    FROM items i
    JOIN pays p ON i.order_id = p.order_id
)
SELECT COUNT(*) AS orders_compared,
       COUNT(*) FILTER (WHERE ABS(diff) > 0.011) AS orders_mismatched,
       COUNT(*) FILTER (WHERE ABS(diff) BETWEEN 0.009 AND 0.011) AS orders_off_by_one_cent,
       COUNT(*) FILTER (WHERE diff > 0.011) AS orders_paid_more,
       COUNT(*) FILTER (WHERE diff < -0.011) AS orders_paid_less,
       ROUND(100.0 * COUNT(*) FILTER (WHERE diff > 0.011 AND installments > 1)
             / NULLIF(COUNT(*) FILTER (WHERE diff > 0.011), 0), 2) AS paid_more_installment_pct,
       ROUND(SUM(item_total), 2) AS item_total,
       ROUND(SUM(paid), 2) AS payment_total,
       ROUND(SUM(paid) - SUM(item_total), 2) AS difference,
       ROUND(MAX(ABS(paid - item_total)), 2) AS max_abs_difference
FROM compared
```

</details>

### DS-14 — Độ nhạy của định nghĩa 'giao trễ'

**Trạng thái:** Ghi nhận

**Vì sao kiểm tra:** Ngày giao dự kiến trong dữ liệu luôn là 00:00. So theo mốc thời gian thì đơn giao trong chính ngày dự kiến cũng bị tính là trễ.

| Đại lượng | Giá trị |
| --- | ---: |
| `delivered_orders` | 96.478 |
| `late_by_timestamp` | 7.826 |
| `late_by_calendar_day` | 6.534 |
| `late_rate_by_timestamp_pct` | 8,11 |
| `late_rate_by_calendar_day_pct` | 6,77 |
| `same_day_orders` | 1.292 |

**Kết luận:** Định nghĩa của nhóm (so mốc thời gian) cho 7.826 đơn trễ (8,11%). Nếu so theo ngày lịch thì còn 6.534 đơn (6,77%); 1.292 đơn chênh lệch là đơn giao đúng trong ngày dự kiến. Nhóm giữ định nghĩa theo mốc thời gian vì nó khớp baseline và là cách tính chặt hơn, nhưng phải nói rõ khi trình bày.

<details><summary>Câu SQL</summary>

```sql
SELECT COUNT(*) AS delivered_orders,
       CAST(COALESCE(SUM(is_late::INT), 0) AS BIGINT) AS late_by_timestamp,
       CAST(COALESCE(SUM((CAST(order_delivered_customer_date AS DATE)
                          > CAST(order_estimated_delivery_date AS DATE))::INT), 0) AS BIGINT) AS late_by_calendar_day
FROM v_fact_orders
WHERE is_delivered
```

</details>

### DS-15 — Đơn delivered thiếu ngày giao thực tế

**Trạng thái:** Ghi nhận

**Vì sao kiểm tra:** Đơn thiếu ngày giao không tính được thời gian giao và mặc định không bị coi là trễ.

| Đại lượng | Giá trị |
| --- | ---: |
| `delivered_orders` | 96.478 |
| `delivered_without_date` | 8 |

**Kết luận:** 8 trong 96.478 đơn delivered không có ngày giao thực tế. Chúng vẫn nằm trong mẫu số tỷ lệ giao trễ nhưng bị loại khỏi thời gian giao trung bình; ảnh hưởng không đáng kể nhưng cần biết.

<details><summary>Câu SQL</summary>

```sql
SELECT COUNT(*) AS delivered_orders,
       COUNT(*) FILTER (WHERE order_delivered_customer_date IS NULL) AS delivered_without_date
FROM v_fact_orders
WHERE is_delivered
```

</details>

### DS-16 — Đánh giá: đếm theo dòng hay theo đơn

**Trạng thái:** Ghi nhận

**Vì sao kiểm tra:** Một đơn có thể có nhiều đánh giá. Phân tích ở grain đơn phải chọn một đánh giá cho mỗi đơn.

| Đại lượng | Giá trị |
| --- | ---: |
| `review_rows` | 99.224 |
| `orders_with_review` | 98.673 |
| `orders_with_many_reviews` | 547 |
| `avg_score_row_level` | 4,16 |
| `avg_score_order_level` | 4,16 |
| `extra_review_rows` | 551 |

**Kết luận:** 99.224 dòng đánh giá thuộc 98.673 đơn: 547 đơn có nhiều đánh giá, tạo 551 dòng dư. Điểm trung bình đơn delivered là 4,1557 nếu tính theo dòng và 4,1558 nếu mỗi đơn lấy đánh giá mới nhất. Phần phân tích dùng cách thứ hai.

<details><summary>Câu SQL</summary>

```sql
WITH review_per_order AS (
        SELECT order_id, review_score
        FROM v_fact_reviews
        QUALIFY ROW_NUMBER() OVER (
            PARTITION BY order_id ORDER BY date_key DESC, review_id DESC
        ) = 1
    )
SELECT (SELECT COUNT(*) FROM v_fact_reviews) AS review_rows,
       (SELECT COUNT(DISTINCT order_id) FROM v_fact_reviews) AS orders_with_review,
       (SELECT COUNT(*) FROM (SELECT order_id FROM v_fact_reviews GROUP BY order_id HAVING COUNT(*) > 1))
           AS orders_with_many_reviews,
       (SELECT ROUND(AVG(r.review_score), 4)
        FROM v_fact_reviews r JOIN v_fact_orders o ON r.order_id = o.order_id
        WHERE o.is_delivered) AS avg_score_row_level,
       (SELECT ROUND(AVG(l.review_score), 4)
        FROM review_per_order l JOIN v_fact_orders o ON l.order_id = o.order_id
        WHERE o.is_delivered) AS avg_score_order_level
```

</details>

### DS-17 — Hai cách đếm số đơn theo danh mục

**Trạng thái:** Ghi nhận

**Vì sao kiểm tra:** Kho có hai khái niệm: danh mục của từng dòng hàng (dim_product) và danh mục đại diện của đơn (fact_orders.category). Chúng cho số đơn khác nhau.

| Đại lượng | Giá trị |
| --- | ---: |
| `categories` | 74 |
| `categories_differing` | 55 |
| `sum_orders_any_item` | 97.276 |
| `sum_orders_dominant` | 96.478 |
| `max_difference` | 108 |

**Kết luận:** Trong 74 danh mục có 55 danh mục mà hai cách đếm lệch nhau (lệch lớn nhất 108 đơn). Đếm theo dòng hàng cộng lại ra 97.276 (một đơn tính cho mọi danh mục nó chứa); đếm theo danh mục đại diện cộng lại đúng 96.478. Hệ quả: khi lọc dashboard theo danh mục, thẻ KPI (đếm theo danh mục đại diện) và bảng danh mục (đếm theo dòng hàng) có thể hiện hai số đơn khác nhau cho cùng một danh mục. Doanh thu thì luôn tính theo dòng hàng.

<details><summary>Câu SQL</summary>

```sql
WITH by_item AS (
    SELECT p.category, COUNT(DISTINCT f.order_id) AS orders_any_item
    FROM v_fact_order_items f
    JOIN v_dim_product p ON f.product_id = p.product_id
    WHERE f.is_delivered
    GROUP BY p.category
),
by_order AS (
    SELECT category, COUNT(*) AS orders_dominant
    FROM v_fact_orders
    WHERE is_delivered
    GROUP BY category
)
SELECT COUNT(*) AS categories,
       CAST(SUM((COALESCE(i.orders_any_item, 0) <> COALESCE(o.orders_dominant, 0))::INT) AS BIGINT)
           AS categories_differing,
       CAST(SUM(i.orders_any_item) AS BIGINT) AS sum_orders_any_item,
       CAST(SUM(o.orders_dominant) AS BIGINT) AS sum_orders_dominant,
       MAX(ABS(COALESCE(i.orders_any_item, 0) - COALESCE(o.orders_dominant, 0))) AS max_difference
FROM by_item i
FULL JOIN by_order o ON i.category = o.category
```

</details>
