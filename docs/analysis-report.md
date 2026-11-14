# Báo cáo phân tích dữ liệu Olist

> Tệp này do `python -X utf8 -m src.analytics` sinh ra từ kho dữ liệu (`data/marts/`). Không sửa tay: sửa truy vấn trong `src/analytics/insights.py` rồi chạy lại.

Phạm vi: mục 17–20 của bảng phân công (phân tích kinh doanh, sản phẩm và người bán, giao vận, đánh giá khách hàng). Dữ liệu: đơn `delivered` đặt từ tháng 2016-09 đến tháng 2018-08.

Định nghĩa KPI: xem `docs/kpi-definitions.md`. Bằng chứng số liệu đáng tin: xem `docs/reconciliation-report.md` (toàn bộ kiểm tra đạt).

## Ba quy ước khi đọc số liệu

1. **Doanh thu** = `price + freight_value` của các dòng hàng thuộc đơn `delivered`.
2. **Số đơn** luôn đếm `DISTINCT order_id` ở grain gốc; không cộng số đơn của các nhóm con.
3. Bảng nhiều dòng trên một đơn (dòng hàng, thanh toán, đánh giá) được **gộp về grain đơn trước khi JOIN**.

## Mục 17 — Phân tích kinh doanh

### KPI tổng quan

**Câu hỏi:** Toàn kỳ, sàn bán được bao nhiêu, bao nhiêu đơn, giá trị đơn trung bình là bao nhiêu?

| Chỉ số | Giá trị |
| --- | ---: |
| Doanh thu (price + freight, đơn delivered) | 15.419.773,75 BRL |
|   trong đó tiền hàng | 13.221.498,11 BRL |
|   trong đó phí vận chuyển | 2.198.275,64 BRL (14,26%) |
| Số đơn delivered | 96.478 |
| Số dòng hàng | 110.197 |
| Giá trị đơn trung bình (AOV) | 159,83 BRL |
| Số dòng hàng trên một đơn | 1,142 |
| Số khách hàng (customer_unique_id) | 93.358 |
| Số người bán có đơn | 2.970 |
| Số sản phẩm có bán | 32.216 |
| Tỷ lệ giao trễ | 8,11% |
| Thời gian giao trung bình | 12,56 ngày |
| Điểm đánh giá trung bình | 4,16 |

**Nhận xét:**

- Trung bình một đơn chỉ có 1,142 dòng hàng, nên AOV (159,83 BRL) gần với giá một món hàng cộng phí ship.
- Phí vận chuyển chiếm 14,26% doanh thu. Con số doanh thu của nhóm gồm cả phí này; nếu chỉ tính tiền hàng thì thấp hơn tương ứng.

<details><summary>Câu SQL</summary>

```sql
WITH review_per_order AS (
    SELECT order_id, review_score
    FROM v_fact_reviews
    QUALIFY ROW_NUMBER() OVER (
        PARTITION BY order_id ORDER BY date_key DESC, review_id DESC
    ) = 1
),
sales AS (
    SELECT SUM(item_total) AS revenue,
           SUM(price) AS product_revenue,
           SUM(freight_value) AS freight,
           COUNT(DISTINCT order_id) AS orders,
           COUNT(*) AS items,
           COUNT(DISTINCT seller_id) AS sellers,
           COUNT(DISTINCT product_id) AS products
    FROM v_fact_order_items
    WHERE is_delivered
),
delivery AS (
    SELECT COUNT(DISTINCT c.customer_unique_id) AS customers,
           COUNT(*) AS delivered_orders,
           CAST(SUM(o.is_late::INT) AS BIGINT) AS late_orders,
           AVG(o.delivery_days) AS avg_delivery_days,
           AVG(r.review_score) AS avg_review_score
    FROM v_fact_orders o
    JOIN v_dim_customer c ON o.customer_id = c.customer_id
    LEFT JOIN review_per_order r ON o.order_id = r.order_id
    WHERE o.is_delivered
)
SELECT ROUND(s.revenue, 2) AS revenue,
       ROUND(s.product_revenue, 2) AS product_revenue,
       ROUND(s.freight, 2) AS freight,
       ROUND(100.0 * s.freight / s.revenue, 2) AS freight_share_pct,
       s.orders, s.items,
       ROUND(s.revenue / s.orders, 2) AS aov,
       ROUND(1.0 * s.items / s.orders, 3) AS items_per_order,
       d.customers, s.sellers, s.products,
       d.late_orders,
       ROUND(100.0 * d.late_orders / d.delivered_orders, 2) AS late_rate_pct,
       ROUND(d.avg_delivery_days, 2) AS avg_delivery_days,
       ROUND(d.avg_review_score, 2) AS avg_review_score
FROM sales s CROSS JOIN delivery d
```

</details>

### Doanh thu, số đơn, AOV theo tháng

**Câu hỏi:** Doanh thu và số đơn thay đổi thế nào theo thời gian? Tháng nào cao điểm?

| Tháng | Doanh thu (BRL) | Số đơn | AOV (BRL) | Phí ship / doanh thu (%) | Tăng so với tháng trước (%) |
| --- | ---: | ---: | ---: | ---: | ---: |
| 2016-09 | 143,46 | 1 | 143,46 | 5,92 | – |
| 2016-10 | 46.490,66 | 265 | 175,44 | 13,26 | – |
| 2016-12 | 19,62 | 1 | 19,62 | 44,44 | – |
| 2017-01 | 127.482,37 | 750 | 169,98 | 12,30 | – |
| 2017-02 | 271.239,32 | 1.653 | 164,09 | 13,65 | 112,77 |
| 2017-03 | 414.330,95 | 2.546 | 162,74 | 13,31 | 52,75 |
| 2017-04 | 390.812,40 | 2.303 | 169,70 | 12,83 | -5,68 |
| 2017-05 | 566.851,40 | 3.546 | 159,86 | 13,67 | 45,04 |
| 2017-06 | 490.050,37 | 3.135 | 156,32 | 13,90 | -13,55 |
| 2017-07 | 566.299,08 | 3.872 | 146,25 | 14,96 | 15,56 |
| 2017-08 | 645.832,36 | 4.193 | 154,03 | 14,11 | 14,04 |
| 2017-09 | 701.077,49 | 4.150 | 168,93 | 13,36 | 8,55 |
| 2017-10 | 751.117,01 | 4.478 | 167,73 | 13,70 | 7,14 |
| 2017-11 | 1.153.364,20 | 7.289 | 158,23 | 14,36 | 53,55 |
| 2017-12 | 843.078,29 | 5.513 | 152,93 | 13,88 | -26,90 |
| 2018-01 | 1.077.887,46 | 7.069 | 152,48 | 14,22 | 27,85 |
| 2018-02 | 966.168,41 | 6.555 | 147,39 | 14,46 | -10,36 |
| 2018-03 | 1.120.598,24 | 7.003 | 160,02 | 14,92 | 15,98 |
| 2018-04 | 1.132.878,93 | 6.798 | 166,65 | 14,07 | 1,10 |
| 2018-05 | 1.128.774,52 | 6.749 | 167,25 | 13,40 | -0,36 |
| 2018-06 | 1.011.978,29 | 6.099 | 165,93 | 15,41 | -10,35 |
| 2018-07 | 1.027.807,28 | 6.159 | 166,88 | 15,55 | 1,56 |
| 2018-08 | 985.491,64 | 6.351 | 155,17 | 14,91 | -4,12 |

**Nhận xét:**

- Tháng cao nhất là 2017-11 với 1.153.364,20 BRL và 7.289 đơn.
- Trong năm 2018 doanh thu tháng dao động trong khoảng 966.168,41 BRL – 1.132.878,93 BRL (tháng cao nhất chỉ gấp 1,17 lần tháng thấp nhất): giai đoạn tăng nhanh đã chuyển sang đi ngang.
- AOV theo tháng nằm trong khoảng 146,25 BRL – 169,98 BRL, hẹp hơn nhiều so với biên độ của số đơn, nên biến động doanh thu chủ yếu do số đơn.
- 3 tháng đầu (2016-09, 2016-10, 2016-12) chỉ có 267 đơn, được đánh dấu là giai đoạn thưa dữ liệu và không dùng để tính tăng trưởng.

<details><summary>Câu SQL</summary>

```sql
WITH monthly AS (
    SELECT d.year, d.month,
           BOOL_OR(d.is_sparse_period) AS is_sparse_period,
           SUM(f.item_total) AS revenue,
           COUNT(DISTINCT f.order_id) AS orders,
           COUNT(*) AS items,
           SUM(f.freight_value) AS freight
    FROM v_fact_order_items f
    JOIN v_dim_date d ON f.date_key = d.date_key
    WHERE f.is_delivered
    GROUP BY d.year, d.month
)
SELECT printf('%d-%02d', year, month) AS period,
       is_sparse_period,
       ROUND(revenue, 2) AS revenue,
       orders,
       items,
       ROUND(revenue / orders, 2) AS aov,
       ROUND(100.0 * freight / revenue, 2) AS freight_share_pct,
       -- Chỉ tính tăng trưởng khi tháng trước liền kề và không thuộc giai đoạn thưa dữ liệu.
       CASE
           WHEN (year * 12 + month) - LAG(year * 12 + month) OVER w = 1
                AND NOT LAG(is_sparse_period) OVER w
           THEN ROUND(100.0 * (revenue - LAG(revenue) OVER w) / LAG(revenue) OVER w, 2)
       END AS revenue_mom_pct
FROM monthly
WINDOW w AS (ORDER BY year, month)
ORDER BY year, month
```

</details>

### Những ngày có nhiều đơn nhất

**Câu hỏi:** Có ngày nào đột biến đơn hàng không?

| Ngày đặt | Số đơn | So với ngày trung bình (lần) |
| --- | ---: | ---: |
| 2017-11-24 | 1.147 | 7,30 |
| 2017-11-25 | 487 | 3,10 |
| 2017-11-27 | 395 | 2,50 |
| 2017-11-26 | 382 | 2,40 |
| 2017-11-28 | 372 | 2,40 |

**Nhận xét:**

- Ngày nhiều đơn nhất là 2017-11-24 với 1.147 đơn, gấp 7,3 lần ngày trung bình — đúng ngày Black Friday 2017.
- Đột biến theo sự kiện là dấu hiệu của đặc trưng Velocity: tải dữ liệu không đều theo thời gian.

<details><summary>Câu SQL</summary>

```sql
SELECT o.date_key AS order_date,
       COUNT(*) AS orders,
       ROUND(COUNT(*) / AVG(COUNT(*)) OVER (), 1) AS times_daily_average
FROM v_fact_orders o
WHERE o.is_delivered
GROUP BY o.date_key
ORDER BY orders DESC, o.date_key
LIMIT ?
-- tham số ?: 5
```

</details>

### So sánh cùng kỳ năm trước

**Câu hỏi:** So cùng các tháng của năm trước, kinh doanh tăng trưởng bao nhiêu?

| Năm | Từ tháng | Đến tháng | Doanh thu (BRL) | Số đơn | AOV (BRL) |
| --- | ---: | ---: | ---: | ---: | ---: |
| 2017 | 1 | 8 | 3.472.898,25 | 21.998 | 157,87 |
| 2018 | 1 | 8 | 8.451.584,77 | 52.783 | 160,12 |

**Nhận xét:**

- Cùng kỳ tháng 1–8, so với năm 2017 thì năm 2018 có doanh thu +143,36%, số đơn +139,94%, AOV +1,43%.
- Thay đổi doanh thu chủ yếu đến từ số đơn (quy mô), không phải từ giá trị mỗi đơn: doanh thu = số đơn × AOV, mà AOV gần như không đổi.

<details><summary>Câu SQL</summary>

```sql
WITH base AS (
    SELECT d.year, d.month, f.item_total, f.order_id
    FROM v_fact_order_items f
    JOIN v_dim_date d ON f.date_key = d.date_key
    WHERE f.is_delivered
),
last_year AS (SELECT MAX(year) AS y FROM base),
cutoff AS (SELECT MAX(b.month) AS m FROM base b, last_year l WHERE b.year = l.y)
SELECT b.year,
       MIN(b.month) AS from_month,
       MAX(b.month) AS to_month,
       ROUND(SUM(b.item_total), 2) AS revenue,
       COUNT(DISTINCT b.order_id) AS orders,
       ROUND(SUM(b.item_total) / COUNT(DISTINCT b.order_id), 2) AS aov
FROM base b, last_year l, cutoff k
WHERE b.year IN (l.y, l.y - 1) AND b.month <= k.m
GROUP BY b.year
ORDER BY b.year
```

</details>

### Số đơn theo ngày trong tuần

**Câu hỏi:** Khách đặt hàng nhiều vào ngày nào trong tuần?

| Ngày | Số đơn | Doanh thu (BRL) | Tỷ trọng (%) |
| --- | ---: | ---: | ---: |
| Thứ Hai | 15.701 | 2.530.094,03 | 16,41 |
| Thứ Ba | 15.503 | 2.473.688,63 | 16,04 |
| Thứ Tư | 15.076 | 2.396.255,54 | 15,54 |
| Thứ Năm | 14.323 | 2.283.871,03 | 14,81 |
| Thứ Sáu | 13.685 | 2.222.443,15 | 14,41 |
| Thứ Bảy | 10.555 | 1.705.802,70 | 11,06 |
| Chủ nhật | 11.635 | 1.807.618,67 | 11,72 |

**Nhận xét:**

- Thứ Hai nhiều đơn nhất (15.701), Thứ Bảy ít nhất (10.555).
- Cộng cả kỳ, mỗi thứ từ Thứ Hai đến Thứ Sáu có trung bình 14.858 đơn, mỗi thứ cuối tuần có 11.095 đơn (-25,32%).

<details><summary>Câu SQL</summary>

```sql
SELECT d.weekday AS weekday_index,
       CASE d.weekday
           WHEN 0 THEN 'Thứ Hai' WHEN 1 THEN 'Thứ Ba' WHEN 2 THEN 'Thứ Tư'
           WHEN 3 THEN 'Thứ Năm' WHEN 4 THEN 'Thứ Sáu' WHEN 5 THEN 'Thứ Bảy'
           ELSE 'Chủ nhật'
       END AS weekday,
       COUNT(DISTINCT f.order_id) AS orders,
       ROUND(SUM(f.item_total), 2) AS revenue,
       ROUND(100.0 * SUM(f.item_total) / SUM(SUM(f.item_total)) OVER (), 2) AS revenue_share_pct
FROM v_fact_order_items f
JOIN v_dim_date d ON f.date_key = d.date_key
WHERE f.is_delivered
GROUP BY d.weekday
ORDER BY d.weekday
```

</details>

### Doanh thu theo vùng của khách hàng

**Câu hỏi:** Doanh thu tập trung ở vùng nào của Brazil?

| Vùng | Doanh thu (BRL) | Số đơn | AOV (BRL) | Tỷ trọng (%) | Phí ship / doanh thu (%) |
| --- | ---: | ---: | ---: | ---: | ---: |
| Sudeste | 9.961.654,32 | 66.200 | 150,48 | 64,60 | 13,18 |
| Sul | 2.238.309,37 | 13.814 | 162,03 | 14,52 | 15,03 |
| Nordeste | 1.822.543,32 | 9.044 | 201,52 | 11,82 | 17,86 |
| Centro-Oeste | 995.927,67 | 5.624 | 177,09 | 6,46 | 14,96 |
| Norte | 401.339,07 | 1.796 | 223,46 | 2,60 | 18,50 |

**Nhận xét:**

- Vùng Sudeste chiếm 64,60% doanh thu.
- Vùng Norte vừa có AOV cao nhất (223,46 BRL) vừa có tỷ trọng phí ship cao nhất (18,50%): một phần giá trị đơn cao ở vùng này là cước vận chuyển.

<details><summary>Câu SQL</summary>

```sql
SELECT c.region,
       ROUND(SUM(f.item_total), 2) AS revenue,
       COUNT(DISTINCT f.order_id) AS orders,
       ROUND(SUM(f.item_total) / COUNT(DISTINCT f.order_id), 2) AS aov,
       ROUND(100.0 * SUM(f.item_total) / SUM(SUM(f.item_total)) OVER (), 2) AS revenue_share_pct,
       ROUND(100.0 * SUM(f.freight_value) / SUM(f.item_total), 2) AS freight_share_pct
FROM v_fact_order_items f
JOIN v_dim_customer c ON f.customer_id = c.customer_id
WHERE f.is_delivered
GROUP BY c.region
ORDER BY revenue DESC, c.region
```

</details>

### Cơ cấu phương thức thanh toán

**Câu hỏi:** Khách trả tiền bằng phương thức nào? (đo trên bảng thanh toán, không trộn với dòng hàng)

| Phương thức | Số đơn có dùng | Số dòng thanh toán | Giá trị (BRL) | Tỷ trọng giá trị (%) | Số kỳ trả góp TB |
| --- | ---: | ---: | ---: | ---: | ---: |
| credit_card | 74.304 | 74.586 | 12.101.094,88 | 78,46 | 3,50 |
| boleto | 19.191 | 19.191 | 2.769.932,58 | 17,96 | 1,00 |
| voucher | 3.679 | 5.493 | 343.013,19 | 2,22 | 1,00 |
| debit_card | 1.485 | 1.486 | 208.421,12 | 1,35 | 1,00 |

**Nhận xét:**

- credit_card chiếm 78,46% giá trị thanh toán, trung bình 3,50 kỳ trả góp.
- Cột 'Số đơn có dùng' cộng lại ra 98.659, lớn hơn số đơn delivered, vì một đơn có thể trả bằng nhiều phương thức. Đây là số đo không cộng dồn được.

<details><summary>Câu SQL</summary>

```sql
SELECT p.payment_type,
       COUNT(DISTINCT p.order_id) AS orders,
       COUNT(*) AS payment_rows,
       ROUND(SUM(p.payment_value), 2) AS payment_value,
       ROUND(100.0 * SUM(p.payment_value) / SUM(SUM(p.payment_value)) OVER (), 2) AS value_share_pct,
       ROUND(AVG(p.payment_installments), 2) AS avg_installments
FROM v_fact_payments p
JOIN v_fact_orders o ON p.order_id = o.order_id
WHERE o.is_delivered
GROUP BY p.payment_type
ORDER BY payment_value DESC, p.payment_type
```

</details>

### Khách hàng mua lại

**Câu hỏi:** Bao nhiêu khách quay lại mua lần hai? (đếm theo customer_unique_id, không phải customer_id)

| Chỉ số | Giá trị |
| --- | ---: |
| Số khách hàng | 93.358 |
| Số đơn delivered | 96.478 |
| Khách mua từ 2 đơn trở lên | 2.801 |
| Tỷ lệ mua lại | 3,00% |
| Số đơn trung bình mỗi khách | 1,033 |
| Số đơn nhiều nhất của một khách | 15 |

**Nhận xét:**

- Chỉ 3,00% khách quay lại mua lần hai: sàn tăng trưởng nhờ khách mới, chưa giữ chân được khách cũ.
- Phải đếm theo `customer_unique_id`. Nếu đếm theo `customer_id` (mã sinh mới cho mỗi đơn) thì tỷ lệ mua lại luôn bằng 0 — một lỗi ngữ nghĩa điển hình của bộ dữ liệu này.

<details><summary>Câu SQL</summary>

```sql
WITH per_customer AS (
    SELECT c.customer_unique_id, COUNT(*) AS orders
    FROM v_fact_orders o
    JOIN v_dim_customer c ON o.customer_id = c.customer_id
    WHERE o.is_delivered
    GROUP BY c.customer_unique_id
)
SELECT COUNT(*) AS customers,
       CAST(SUM(orders) AS BIGINT) AS orders,
       CAST(SUM((orders > 1)::INT) AS BIGINT) AS repeat_customers,
       ROUND(100.0 * AVG((orders > 1)::INT), 2) AS repeat_rate_pct,
       ROUND(AVG(orders), 3) AS orders_per_customer,
       MAX(orders) AS max_orders_one_customer
FROM per_customer
```

</details>

### Phân bố trạng thái đơn hàng

**Câu hỏi:** Bao nhiêu phần trăm đơn được giao thành công? (cơ sở để chỉ tính KPI trên đơn delivered)

| Trạng thái | Số đơn | Tỷ trọng (%) | Số đơn có dòng hàng |
| --- | ---: | ---: | ---: |
| delivered | 96.478 | 97,02 | 96.478 |
| shipped | 1.107 | 1,11 | 1.106 |
| canceled | 625 | 0,63 | 461 |
| unavailable | 609 | 0,61 | 6 |
| invoiced | 314 | 0,32 | 312 |
| processing | 301 | 0,30 | 301 |
| created | 5 | 0,01 | 0 |
| approved | 2 | 0,00 | 2 |

**Nhận xét:**

- 97,02% đơn ở trạng thái delivered. Mọi KPI doanh thu chỉ tính trên nhóm này, vì đơn hủy hoặc chưa giao chưa phải doanh thu thực nhận.

<details><summary>Câu SQL</summary>

```sql
SELECT order_status,
       COUNT(*) AS orders,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS share_pct,
       CAST(SUM(has_items::INT) AS BIGINT) AS orders_with_items
FROM v_fact_orders
GROUP BY order_status
ORDER BY orders DESC, order_status
```

</details>

## Mục 18 — Phân tích sản phẩm và người bán

### Xếp hạng danh mục theo doanh thu

**Câu hỏi:** Danh mục nào mang lại nhiều doanh thu nhất? Doanh thu tập trung đến mức nào?

| Hạng | Danh mục | Tên tiếng Anh | Doanh thu (BRL) | Số đơn | Số dòng hàng | Doanh thu / đơn (BRL) | Tỷ trọng (%) | Lũy kế (%) |
| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | beleza_saude | health_beauty | 1.412.089,53 | 8.647 | 9.465 | 163,30 | 9,16 | 9,16 |
| 2 | relogios_presentes | watches_gifts | 1.264.333,12 | 5.495 | 5.859 | 230,09 | 8,20 | 17,36 |
| 3 | cama_mesa_banho | bed_bath_table | 1.225.209,26 | 9.272 | 10.953 | 132,14 | 7,95 | 25,30 |
| 4 | esporte_lazer | sports_leisure | 1.118.256,91 | 7.530 | 8.431 | 148,51 | 7,25 | 32,55 |
| 5 | informatica_acessorios | computers_accessories | 1.032.723,77 | 6.530 | 7.644 | 158,15 | 6,70 | 39,25 |
| 6 | moveis_decoracao | furniture_decor | 880.329,92 | 6.307 | 8.160 | 139,58 | 5,71 | 44,96 |
| 7 | utilidades_domesticas | housewares | 758.392,25 | 5.743 | 6.795 | 132,06 | 4,92 | 49,88 |
| 8 | cool_stuff | cool_stuff | 691.680,89 | 3.559 | 3.718 | 194,35 | 4,49 | 54,37 |
| 9 | automotivo | auto | 669.454,75 | 3.810 | 4.140 | 175,71 | 4,34 | 58,71 |
| 10 | ferramentas_jardim | garden_tools | 567.145,68 | 3.448 | 4.268 | 164,49 | 3,68 | 62,38 |
| 11 | brinquedos | toys | 547.061,06 | 3.804 | 4.030 | 143,81 | 3,55 | 65,93 |
| 12 | bebes | baby | 466.727,65 | 2.809 | 2.982 | 166,15 | 3,03 | 68,96 |
| 13 | perfumaria | perfumery | 443.171,63 | 3.086 | 3.340 | 143,61 | 2,87 | 71,83 |
| 14 | telefonia | telephony | 379.202,62 | 4.093 | 4.430 | 92,65 | 2,46 | 74,29 |
| 15 | moveis_escritorio | office_furniture | 335.211,36 | 1.254 | 1.668 | 267,31 | 2,17 | 76,47 |

**Nhận xét:**

- Dẫn đầu là beleza_saude (health_beauty) với 1.412.089,53 BRL, chiếm 9,16%.
- 5 danh mục đầu chiếm 39,25% và chỉ cần 18 trên 74 danh mục để đạt 80% doanh thu.
- Xếp theo doanh thu và theo giá trị mỗi đơn cho hai bức tranh khác nhau: pcs chỉ có 177 đơn nhưng mỗi đơn 1.290,11 BRL.
- Nhóm `unknown` (sản phẩm thiếu danh mục ở nguồn) đứng hạng 22 với 1,28% doanh thu. Nhóm giữ lại và gắn nhãn thay vì xóa, để tổng doanh thu không hụt.

<details><summary>Câu SQL</summary>

```sql
WITH by_category AS (
    SELECT p.category,
           MIN(p.category_english) AS category_english,
           SUM(f.item_total) AS revenue,
           SUM(f.price) AS price_total,
           COUNT(DISTINCT f.order_id) AS orders,
           COUNT(*) AS items
    FROM v_fact_order_items f
    JOIN v_dim_product p ON f.product_id = p.product_id
    WHERE f.is_delivered
    GROUP BY p.category
)
SELECT ROW_NUMBER() OVER (ORDER BY revenue DESC, category) AS rank,
       category,
       category_english,
       ROUND(revenue, 2) AS revenue,
       orders,
       items,
       ROUND(revenue / orders, 2) AS revenue_per_order,
       ROUND(price_total / items, 2) AS avg_item_price,
       ROUND(100.0 * revenue / SUM(revenue) OVER (), 2) AS share_pct,
       ROUND(100.0 * SUM(revenue) OVER (
           ORDER BY revenue DESC, category ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
       ) / SUM(revenue) OVER (), 2) AS cum_share_pct
FROM by_category
ORDER BY rank
```

</details>

### Sản phẩm bán chạy nhất theo doanh thu

**Câu hỏi:** Những sản phẩm nào đóng góp doanh thu lớn nhất?

| Hạng | Mã sản phẩm | Danh mục | Doanh thu (BRL) | Số lượng bán | Số đơn | Giá TB (BRL) |
| ---: | --- | --- | ---: | ---: | ---: | ---: |
| 1 | bb50f2e236e5eea0100680137654686c | beleza_saude | 67.258,03 | 194 | 186 | 327,63 |
| 2 | d1c427060a0f73f6b889a5c7c61f2ac4 | informatica_acessorios | 58.957,31 | 332 | 313 | 137,41 |
| 3 | 6cdd53843498f92890544667809f1595 | beleza_saude | 57.933,73 | 153 | 148 | 350,67 |
| 4 | 99a4788cb24856965c36a24e339b6058 | cama_mesa_banho | 49.907,50 | 477 | 456 | 88,15 |
| 5 | 3dd2a17168ec895c781a9191c1e95ad7 | informatica_acessorios | 47.876,06 | 272 | 253 | 149,94 |
| 6 | d6160fb7873f184099d9bc95e30376af | pcs | 47.314,18 | 33 | 33 | 1.392,40 |
| 7 | aca2eb7d00ea1a7b8ebd4e68314663af | moveis_decoracao | 44.197,75 | 520 | 425 | 71,35 |
| 8 | 5f504b3a1c75b73d6151be81eb05bdc9 | cool_stuff | 41.725,81 | 63 | 63 | 598,95 |
| 9 | 25c38557cf793876c5abdd5931f922db | bebes | 40.311,95 | 38 | 38 | 1.023,88 |
| 10 | 53b36df67ebb7c41585e8d54d6772e08 | relogios_presentes | 39.713,49 | 321 | 304 | 116,68 |

**Nhận xét:**

- 10 sản phẩm đứng đầu chỉ chiếm 3,21% doanh thu: doanh thu phân tán trên rất nhiều sản phẩm (đuôi dài), không phụ thuộc vài mặt hàng.
- Bộ dữ liệu ẩn tên sản phẩm nên chỉ xếp hạng được theo mã và danh mục.

<details><summary>Câu SQL</summary>

```sql
SELECT ROW_NUMBER() OVER (ORDER BY SUM(f.item_total) DESC, f.product_id) AS rank,
       f.product_id,
       p.category,
       ROUND(SUM(f.item_total), 2) AS revenue,
       COUNT(*) AS units,
       COUNT(DISTINCT f.order_id) AS orders,
       ROUND(AVG(f.price), 2) AS avg_price
FROM v_fact_order_items f
JOIN v_dim_product p ON f.product_id = p.product_id
WHERE f.is_delivered
GROUP BY f.product_id, p.category
ORDER BY rank
LIMIT ?
-- tham số ?: 10
```

</details>

### Người bán hàng đầu: doanh thu kèm chất lượng phục vụ

**Câu hỏi:** Người bán nào lớn nhất, và họ có giao đúng hạn, được đánh giá tốt không?

| Hạng | Mã người bán | Bang | Doanh thu (BRL) | Số đơn | Tỷ trọng (%) | Điểm đánh giá TB | Tỷ lệ giao trễ (%) |
| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: |
| 1 | 4869f7a5dfa277a7dca6462dcf3b52b2 | SP | 247.007,06 | 1.124 | 1,60 | 4,15 | 11,57 |
| 2 | 7c67e1448b00f6e969d365cea6b010ab | SP | 237.806,69 | 973 | 1,54 | 3,50 | 10,07 |
| 3 | 4a3ca9315b744ce9f8e9374361493884 | SP | 231.220,43 | 1.772 | 1,50 | 3,85 | 11,00 |
| 4 | 53243585a1d6dc2643021fd1853d8905 | BA | 230.797,02 | 348 | 1,50 | 4,19 | 4,31 |
| 5 | fa1c13f2614d7b5c4749cbc52fecda94 | SP | 200.833,50 | 578 | 1,30 | 4,37 | 10,21 |
| 6 | da8622b14eb17ae2831f4ac5b9dab84a | SP | 184.706,78 | 1.311 | 1,20 | 4,18 | 7,63 |
| 7 | 7e93a43ef30c4f03f38b393420bc753a | SP | 171.973,55 | 319 | 1,12 | 4,36 | 5,64 |
| 8 | 1025f0e2d44d7041d6cf58b6550e0bfa | SP | 171.924,96 | 910 | 1,11 | 4,01 | 10,11 |
| 9 | 7a67c85e85bb2ce8582c35f2203ad736 | SP | 160.278,52 | 1.145 | 1,04 | 4,28 | 5,94 |
| 10 | 955fee9216a65b617aa5c0531780ce60 | SP | 156.606,48 | 1.261 | 1,02 | 4,20 | 7,77 |

**Nhận xét:**

- Xếp hạng người bán chỉ theo doanh thu là chưa đủ, nên bảng kèm hai chỉ số chất lượng: điểm đánh giá và tỷ lệ giao trễ.
- Trong nhóm đầu, người bán hạng 2 có điểm đánh giá thấp nhất (3,50) và người bán hạng 1 giao trễ nhiều nhất (11,57%): doanh thu lớn không đồng nghĩa phục vụ tốt.
- Đánh giá và cờ giao trễ thuộc về đơn hàng. Với đơn có nhiều người bán, chúng được tính cho mọi người bán trong đơn — một giả định đơn giản hóa cần nêu rõ.

<details><summary>Câu SQL</summary>

```sql
WITH review_per_order AS (
    SELECT order_id, review_score
    FROM v_fact_reviews
    QUALIFY ROW_NUMBER() OVER (
        PARTITION BY order_id ORDER BY date_key DESC, review_id DESC
    ) = 1
),
seller_orders AS (
    -- Gộp về grain (người bán, đơn) trước khi gắn đánh giá và cờ giao trễ của đơn.
    SELECT seller_id, order_id, SUM(item_total) AS revenue, COUNT(*) AS items
    FROM v_fact_order_items
    WHERE is_delivered
    GROUP BY seller_id, order_id
),
by_seller AS (
    SELECT so.seller_id,
           SUM(so.revenue) AS revenue,
           COUNT(*) AS orders,
           SUM(so.items) AS items,
           AVG(r.review_score) AS avg_review_score,
           100.0 * AVG(o.is_late::INT) AS late_rate_pct
    FROM seller_orders so
    JOIN v_fact_orders o ON so.order_id = o.order_id
    LEFT JOIN review_per_order r ON so.order_id = r.order_id
    GROUP BY so.seller_id
)
SELECT ROW_NUMBER() OVER (ORDER BY b.revenue DESC, b.seller_id) AS rank,
       b.seller_id,
       s.state,
       ROUND(b.revenue, 2) AS revenue,
       b.orders,
       CAST(b.items AS BIGINT) AS items,
       ROUND(b.revenue / b.orders, 2) AS revenue_per_order,
       ROUND(100.0 * b.revenue / SUM(b.revenue) OVER (), 2) AS share_pct,
       ROUND(b.avg_review_score, 2) AS avg_review_score,
       ROUND(b.late_rate_pct, 2) AS late_rate_pct
FROM by_seller b
JOIN v_dim_seller s ON b.seller_id = s.seller_id
ORDER BY rank
LIMIT ?
-- tham số ?: 10
```

</details>

### Mức độ tập trung doanh thu theo người bán

**Câu hỏi:** Doanh thu phụ thuộc vào một nhóm nhỏ người bán đến mức nào (quy luật Pareto)?

| Chỉ số | Giá trị |
| --- | ---: |
| Số người bán có đơn delivered | 2.970 |
| Doanh thu trung vị của một người bán | 1.038,63 BRL |
| 10 người bán lớn nhất | 12,93% |
| 1% người bán lớn nhất | 25,47% |
| 10% người bán lớn nhất | 66,29% |
| 20% người bán lớn nhất | 81,62% |

**Nhận xét:**

- 20% người bán lớn nhất tạo ra 81,62% doanh thu — rất gần quy luật Pareto 80/20.
- Một người bán điển hình chỉ đạt 1.038,63 BRL trong cả kỳ: phần lớn người bán rất nhỏ.

<details><summary>Câu SQL</summary>

```sql
WITH by_seller AS (
    SELECT seller_id, SUM(item_total) AS revenue
    FROM v_fact_order_items
    WHERE is_delivered
    GROUP BY seller_id
),
ranked AS (
    SELECT revenue,
           ROW_NUMBER() OVER (ORDER BY revenue DESC, seller_id) AS rn,
           COUNT(*) OVER () AS n,
           SUM(revenue) OVER () AS total
    FROM by_seller
)
SELECT MAX(n) AS active_sellers,
       ROUND(MEDIAN(revenue), 2) AS median_seller_revenue,
       ROUND(100.0 * SUM(CASE WHEN rn <= 10 THEN revenue ELSE 0 END) / MAX(total), 2) AS top10_sellers_share_pct,
       ROUND(100.0 * SUM(CASE WHEN rn <= CEIL(n * 0.01) THEN revenue ELSE 0 END) / MAX(total), 2)
           AS top_1pct_share_pct,
       ROUND(100.0 * SUM(CASE WHEN rn <= CEIL(n * 0.10) THEN revenue ELSE 0 END) / MAX(total), 2)
           AS top_10pct_share_pct,
       ROUND(100.0 * SUM(CASE WHEN rn <= CEIL(n * 0.20) THEN revenue ELSE 0 END) / MAX(total), 2)
           AS top_20pct_share_pct
FROM ranked
```

</details>

### Người bán theo bang

**Câu hỏi:** Người bán tập trung ở bang nào?

| Bang | Số người bán | Doanh thu (BRL) | Tỷ trọng (%) |
| --- | ---: | ---: | ---: |
| SP | 1.769 | 9.957.056,91 | 64,57 |
| PR | 335 | 1.424.161,25 | 9,24 |
| MG | 236 | 1.184.427,54 | 7,68 |
| RJ | 163 | 911.918,67 | 5,91 |
| SC | 184 | 717.739,37 | 4,65 |

**Nhận xét:**

- Người bán ở bang SP tạo ra 64,57% doanh thu. Nguồn cung tập trung ở một bang phù hợp với việc đơn gửi đi vùng xa mất nhiều ngày hơn (xem tuyến giao ở mục 19).

<details><summary>Câu SQL</summary>

```sql
SELECT s.state,
       COUNT(DISTINCT f.seller_id) AS sellers,
       ROUND(SUM(f.item_total), 2) AS revenue,
       ROUND(100.0 * SUM(f.item_total) / SUM(SUM(f.item_total)) OVER (), 2) AS revenue_share_pct
FROM v_fact_order_items f
JOIN v_dim_seller s ON f.seller_id = s.seller_id
WHERE f.is_delivered
GROUP BY s.state
ORDER BY revenue DESC, s.state
LIMIT ?
-- tham số ?: 5
```

</details>

### Danh mục theo chất lượng trải nghiệm

**Câu hỏi:** Danh mục nào bị đánh giá thấp hoặc hay giao trễ? (xếp theo điểm đánh giá, không theo doanh thu)

| Danh mục | Số đơn | Điểm đánh giá TB | Đánh giá 1–2 sao (%) | Tỷ lệ giao trễ (%) | Số ngày giao TB |
| --- | ---: | ---: | ---: | ---: | ---: |
| moveis_escritorio | 1.251 | 3,65 | 21,84 | 9,19 | 20,66 |
| cama_mesa_banho | 9.201 | 4,01 | 15,85 | 8,79 | 13,01 |
| unknown | 1.332 | 4,05 | 16,09 | 8,93 | 12,80 |
| telefonia | 4.074 | 4,06 | 13,93 | 8,54 | 12,97 |
| moveis_decoracao | 6.199 | 4,07 | 14,95 | 8,58 | 13,13 |
| informatica_acessorios | 6.513 | 4,08 | 14,53 | 7,72 | 13,18 |
| bebes | 2.761 | 4,12 | 13,76 | 9,34 | 12,74 |
| relogios_presentes | 5.475 | 4,12 | 13,58 | 8,55 | 12,82 |
| eletronicos | 2.502 | 4,13 | 13,01 | 9,87 | 12,95 |
| automotivo | 3.794 | 4,15 | 12,87 | 8,65 | 12,34 |

**Nhận xét:**

- Chỉ xét danh mục có từ 500 đơn trở lên để điểm trung bình đủ tin cậy.
- Thấp nhất là moveis_escritorio: điểm 3,65, 21,84% đánh giá 1–2 sao, giao trung bình 20,66 ngày. Cao nhất là malas_acessorios (4,37).
- Danh mục dùng ở đây là danh mục đại diện của đơn (`fact_orders.category`), để mỗi đơn chỉ tính một lần.

<details><summary>Câu SQL</summary>

```sql
WITH review_per_order AS (
    SELECT order_id, review_score
    FROM v_fact_reviews
    QUALIFY ROW_NUMBER() OVER (
        PARTITION BY order_id ORDER BY date_key DESC, review_id DESC
    ) = 1
)
-- fact_orders.category là danh mục đại diện của đơn: mỗi đơn đúng một danh mục,
-- nên điểm đánh giá và cờ giao trễ của đơn không bị chia hay nhân theo dòng hàng.
SELECT o.category,
       COUNT(*) AS delivered_orders,
       ROUND(AVG(r.review_score), 2) AS avg_review_score,
       ROUND(100.0 * AVG((r.review_score <= 2)::INT), 2) AS low_review_pct,
       ROUND(100.0 * AVG(o.is_late::INT), 2) AS late_rate_pct,
       ROUND(AVG(o.delivery_days), 2) AS avg_delivery_days
FROM v_fact_orders o
LEFT JOIN review_per_order r ON o.order_id = r.order_id
WHERE o.is_delivered
GROUP BY o.category
HAVING COUNT(*) >= ?
ORDER BY avg_review_score ASC, o.category
-- tham số ?: 500
```

</details>

## Mục 19 — Phân tích giao vận

### Tổng quan giao vận

**Câu hỏi:** Giao một đơn mất bao lâu? Bao nhiêu phần trăm đơn giao trễ, và trễ bao nhiêu ngày?

| Chỉ số | Giá trị |
| --- | ---: |
| Số đơn delivered | 96.478 |
| Thời gian giao trung bình | 12,56 ngày |
| Thời gian giao trung vị | 10,22 ngày |
| 90% đơn được giao trong | 23,10 ngày |
| Số đơn giao trễ | 7.826 |
| Tỷ lệ giao trễ | 8,11% |
| Đơn trễ thì trễ trung bình | 9,55 ngày |
| Đơn đúng hạn đến sớm trung bình | 13,01 ngày |
| Đơn thiếu ngày giao thực tế | 8 |

**Nhận xét:**

- Trung bình (12,56 ngày) lớn hơn trung vị (10,22 ngày): phân phối lệch phải, một số ít đơn giao rất lâu kéo trung bình lên. Vì vậy báo cáo nêu cả trung vị và phân vị 90.
- Đơn đúng hạn đến sớm trung bình 13,01 ngày so với ngày dự kiến: ngày dự kiến được đặt rất dè dặt. Tỷ lệ trễ vì thế đo việc 'vượt cam kết', không đo tốc độ giao.

<details><summary>Câu SQL</summary>

```sql
WITH delivered AS (
    SELECT o.delivery_days, o.is_late, (epoch(o.order_delivered_customer_date) - epoch(o.order_estimated_delivery_date)) / 86400.0 AS days_vs_estimate
    FROM v_fact_orders o
    WHERE o.is_delivered
)
SELECT COUNT(*) AS delivered_orders,
       CAST(SUM((delivery_days IS NULL)::INT) AS BIGINT) AS missing_delivery_date,
       ROUND(AVG(delivery_days), 2) AS avg_delivery_days,
       ROUND(MEDIAN(delivery_days), 2) AS median_delivery_days,
       ROUND(QUANTILE_CONT(delivery_days, 0.9), 2) AS p90_delivery_days,
       CAST(SUM(is_late::INT) AS BIGINT) AS late_orders,
       ROUND(100.0 * AVG(is_late::INT), 2) AS late_rate_pct,
       ROUND(AVG(CASE WHEN is_late THEN days_vs_estimate END), 2) AS avg_days_late_when_late,
       ROUND(AVG(CASE WHEN NOT is_late THEN -days_vs_estimate END), 2) AS avg_days_early_when_on_time
FROM delivered
```

</details>

### Giao vận theo vùng

**Câu hỏi:** Vùng nào giao lâu và trễ nhiều nhất?

| Vùng | Số đơn | Ngày giao TB | Trung vị | Phân vị 90 | Tỷ lệ trễ (%) | Phí ship / đơn (BRL) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Nordeste | 9.044 | 20,01 | 17,32 | 33,11 | 14,33 | 35,99 |
| Norte | 1.796 | 22,59 | 20,16 | 36,57 | 9,80 | 41,35 |
| Centro-Oeste | 5.624 | 15,02 | 13,28 | 24,22 | 7,97 | 26,49 |
| Sudeste | 66.200 | 10,75 | 8,71 | 19,62 | 7,45 | 19,84 |
| Sul | 13.814 | 14,03 | 12,12 | 24,03 | 7,05 | 24,35 |

**Nhận xét:**

- Vùng Nordeste trễ nhiều nhất (14,33%), vùng Sul ít nhất (7,05%), gấp 2,0 lần.
- Vùng Norte giao lâu nhất (22,59 ngày) nhưng không phải vùng trễ nhiều nhất: giao lâu và giao trễ là hai khái niệm khác nhau, vì ngày dự kiến đã tính đến khoảng cách.
- Phí ship mỗi đơn được gộp từ bảng dòng hàng về grain đơn trước khi ghép, để một đơn nhiều dòng không bị đếm nhiều lần.

<details><summary>Câu SQL</summary>

```sql
WITH freight_per_order AS (
    SELECT order_id, SUM(freight_value) AS freight
    FROM v_fact_order_items
    GROUP BY order_id
)
SELECT c.region,
       COUNT(*) AS delivered_orders,
       ROUND(AVG(o.delivery_days), 2) AS avg_delivery_days,
       ROUND(MEDIAN(o.delivery_days), 2) AS median_delivery_days,
       ROUND(QUANTILE_CONT(o.delivery_days, 0.9), 2) AS p90_delivery_days,
       CAST(SUM(o.is_late::INT) AS BIGINT) AS late_orders,
       ROUND(100.0 * AVG(o.is_late::INT), 2) AS late_rate_pct,
       ROUND(AVG(fp.freight), 2) AS avg_freight_per_order
FROM v_fact_orders o
JOIN v_dim_customer c ON o.customer_id = c.customer_id
LEFT JOIN freight_per_order fp ON o.order_id = fp.order_id
WHERE o.is_delivered
GROUP BY c.region
ORDER BY late_rate_pct DESC, c.region
```

</details>

### Giao vận theo bang

**Câu hỏi:** Bang nào có tỷ lệ giao trễ cao nhất, thấp nhất?

| Bang | Vùng | Số đơn | Ngày giao TB | Trung vị | Phân vị 90 | Tỷ lệ trễ (%) | Phí ship / đơn (BRL) |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| AL | Nordeste | 397 | 24,54 | 22,33 | 39,45 | 23,93 | 38,58 |
| MA | Nordeste | 717 | 21,57 | 19,19 | 34,31 | 19,67 | 42,95 |
| PI | Nordeste | 476 | 19,46 | 16,30 | 30,07 | 15,97 | 42,98 |
| CE | Nordeste | 1.279 | 21,27 | 18,21 | 34,72 | 15,32 | 36,50 |
| SE | Nordeste | 335 | 21,52 | 18,01 | 35,46 | 15,22 | 40,94 |
| BA | Nordeste | 3.256 | 19,34 | 16,91 | 31,82 | 14,04 | 29,96 |
| RJ | Sudeste | 12.350 | 15,31 | 12,04 | 29,09 | 13,47 | 23,95 |
| TO | Norte | 274 | 17,66 | 15,87 | 27,95 | 12,77 | 42,35 |
| PA | Norte | 946 | 23,77 | 21,08 | 39,24 | 12,37 | 39,70 |
| ES | Sudeste | 1.995 | 15,79 | 13,64 | 25,35 | 12,23 | 24,57 |
| RR | Norte | 41 | 29,39 | 25,01 | 53,19 | 12,20 | 48,34 |
| MS | Centro-Oeste | 701 | 15,62 | 13,94 | 24,65 | 11,55 | 27,02 |
| PB | Nordeste | 517 | 20,43 | 18,15 | 34,95 | 11,03 | 48,84 |
| PE | Nordeste | 1.593 | 18,45 | 15,70 | 30,91 | 10,80 | 35,83 |
| RN | Nordeste | 474 | 19,28 | 16,06 | 32,94 | 10,76 | 39,26 |
| SC | Sul | 3.546 | 14,95 | 13,02 | 25,80 | 9,76 | 24,85 |
| GO | Centro-Oeste | 1.957 | 15,61 | 13,95 | 24,84 | 8,18 | 26,25 |
| RS | Sul | 5.345 | 15,30 | 13,18 | 25,88 | 7,15 | 24,80 |
| DF | Centro-Oeste | 2.080 | 12,97 | 11,36 | 21,64 | 7,07 | 23,86 |
| MT | Centro-Oeste | 886 | 18,06 | 16,11 | 27,76 | 6,77 | 32,77 |
| SP | Sudeste | 40.501 | 8,76 | 7,21 | 15,77 | 5,89 | 17,33 |
| MG | Sudeste | 11.354 | 12,01 | 10,31 | 20,20 | 5,61 | 23,46 |
| PR | Sul | 4.923 | 11,99 | 10,43 | 20,12 | 5,00 | 23,49 |
| AP | Norte | 67 | 27,19 | 24,35 | 34,67 | 4,48 | 41,30 |
| AM | Norte | 145 | 26,43 | 25,88 | 39,13 | 4,14 | 37,45 |
| AC | Norte | 80 | 21,04 | 18,35 | 31,07 | 3,75 | 45,55 |
| RO | Norte | 243 | 19,37 | 17,58 | 29,52 | 2,88 | 46,43 |

**Nhận xét:**

- Trong các bang có từ 100 đơn trở lên, AL trễ nhiều nhất (23,93%) và RO ít nhất (2,88%).
- SP có nhiều đơn nhất (40.501 đơn, giao trung bình 8,76 ngày) và cũng là bang giao nhanh nhất.
- 3 bang (RR, AP, AC) có dưới 100 đơn: tỷ lệ của các bang này dao động mạnh theo vài đơn, không nên xếp hạng.

<details><summary>Câu SQL</summary>

```sql
WITH freight_per_order AS (
    SELECT order_id, SUM(freight_value) AS freight
    FROM v_fact_order_items
    GROUP BY order_id
)
SELECT c.state, c.region,
       COUNT(*) AS delivered_orders,
       ROUND(AVG(o.delivery_days), 2) AS avg_delivery_days,
       ROUND(MEDIAN(o.delivery_days), 2) AS median_delivery_days,
       ROUND(QUANTILE_CONT(o.delivery_days, 0.9), 2) AS p90_delivery_days,
       CAST(SUM(o.is_late::INT) AS BIGINT) AS late_orders,
       ROUND(100.0 * AVG(o.is_late::INT), 2) AS late_rate_pct,
       ROUND(AVG(fp.freight), 2) AS avg_freight_per_order
FROM v_fact_orders o
JOIN v_dim_customer c ON o.customer_id = c.customer_id
LEFT JOIN freight_per_order fp ON o.order_id = fp.order_id
WHERE o.is_delivered
GROUP BY c.state, c.region
ORDER BY late_rate_pct DESC, c.state, c.region
```

</details>

### Giao vận theo tháng đặt hàng

**Câu hỏi:** Chất lượng giao vận thay đổi thế nào theo thời gian?

| Tháng đặt | Số đơn | Ngày giao TB | Đơn trễ | Tỷ lệ trễ (%) |
| --- | ---: | ---: | ---: | ---: |
| 2016-09 | 1 | 54,81 | 1 | 100,00 |
| 2016-10 | 265 | 19,60 | 3 | 1,13 |
| 2016-12 | 1 | 4,69 | 0 | 0,00 |
| 2017-01 | 750 | 12,65 | 23 | 3,07 |
| 2017-02 | 1.653 | 13,17 | 53 | 3,21 |
| 2017-03 | 2.546 | 12,95 | 142 | 5,58 |
| 2017-04 | 2.303 | 14,92 | 181 | 7,86 |
| 2017-05 | 3.546 | 11,32 | 128 | 3,61 |
| 2017-06 | 3.135 | 12,01 | 121 | 3,86 |
| 2017-07 | 3.872 | 11,59 | 133 | 3,43 |
| 2017-08 | 4.193 | 11,15 | 139 | 3,32 |
| 2017-09 | 4.150 | 11,85 | 216 | 5,20 |
| 2017-10 | 4.478 | 11,86 | 237 | 5,29 |
| 2017-11 | 7.289 | 15,16 | 1.043 | 14,31 |
| 2017-12 | 5.513 | 15,39 | 462 | 8,38 |
| 2018-01 | 7.069 | 14,08 | 464 | 6,56 |
| 2018-02 | 6.555 | 16,95 | 1.048 | 15,99 |
| 2018-03 | 7.003 | 16,30 | 1.496 | 21,36 |
| 2018-04 | 6.798 | 11,50 | 361 | 5,31 |
| 2018-05 | 6.749 | 11,42 | 556 | 8,24 |
| 2018-06 | 6.099 | 9,24 | 83 | 1,36 |
| 2018-07 | 6.159 | 8,96 | 276 | 4,48 |
| 2018-08 | 6.351 | 7,73 | 660 | 10,39 |

**Nhận xét:**

- Ba tháng trễ nhiều nhất: 2018-03 (21,36%), 2018-02 (15,99%), 2017-11 (14,31%).
- Tỷ lệ trễ dao động mạnh giữa các tháng, từ 1,13% đến 21,36%; con số 8,11% của cả kỳ che mất các đợt tăng vọt này.
- Hệ số tương quan Pearson giữa số đơn của tháng và tỷ lệ trễ là 0,58: tháng nhiều đơn có xu hướng trễ nhiều hơn, nhưng đây mới là tương quan trên ít điểm dữ liệu, chưa đủ để kết luận giao vận quá tải.

<details><summary>Câu SQL</summary>

```sql
SELECT printf('%d-%02d', d.year, d.month) AS period,
       COUNT(*) AS delivered_orders,
       ROUND(AVG(o.delivery_days), 2) AS avg_delivery_days,
       CAST(SUM(o.is_late::INT) AS BIGINT) AS late_orders,
       ROUND(100.0 * AVG(o.is_late::INT), 2) AS late_rate_pct
FROM v_fact_orders o
JOIN v_dim_date d ON o.date_key = d.date_key
WHERE o.is_delivered
GROUP BY d.year, d.month
ORDER BY d.year, d.month
```

</details>

### Phân bố thời gian giao hàng

**Câu hỏi:** Phần lớn đơn được giao trong bao nhiêu ngày?

| Thời gian giao | Số đơn | Tỷ trọng (%) | Tỷ lệ trễ (%) |
| --- | ---: | ---: | ---: |
| 0–7 ngày | 26.100 | 27,06 | 0,88 |
| 8–14 ngày | 40.188 | 41,66 | 1,29 |
| 15–21 ngày | 17.697 | 18,34 | 4,84 |
| 22–28 ngày | 6.880 | 7,13 | 28,15 |
| Trên 28 ngày | 5.605 | 5,81 | 76,45 |

**Nhận xét:**

- 68,72% đơn được giao trong vòng 14 ngày.
- Nhóm trên 28 ngày chỉ chiếm 5,81% số đơn nhưng 76,45% trong số đó bị trễ.

<details><summary>Câu SQL</summary>

```sql
WITH bucketed AS (
    SELECT CASE
               WHEN delivery_days <= 7 THEN 1
               WHEN delivery_days <= 14 THEN 2
               WHEN delivery_days <= 21 THEN 3
               WHEN delivery_days <= 28 THEN 4
               ELSE 5
           END AS bucket_index,
           is_late
    FROM v_fact_orders
    WHERE is_delivered AND delivery_days IS NOT NULL
)
SELECT bucket_index,
       CASE bucket_index
           WHEN 1 THEN '0–7 ngày' WHEN 2 THEN '8–14 ngày' WHEN 3 THEN '15–21 ngày'
           WHEN 4 THEN '22–28 ngày' ELSE 'Trên 28 ngày'
       END AS delivery_time,
       COUNT(*) AS orders,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS share_pct,
       ROUND(100.0 * AVG(is_late::INT), 2) AS late_rate_pct
FROM bucketed
GROUP BY bucket_index
ORDER BY bucket_index
```

</details>

### Giao trong bang so với giao liên bang

**Câu hỏi:** Khoảng cách (người bán và khách khác bang) ảnh hưởng thế nào tới thời gian giao?

| Tuyến | Số đơn | Tỷ trọng (%) | Ngày giao TB | Tỷ lệ trễ (%) |
| --- | ---: | ---: | ---: | ---: |
| Trong bang | 34.580 | 35,84 | 7,95 | 6,08 |
| Liên bang | 61.898 | 64,16 | 15,13 | 9,25 |

**Nhận xét:**

- 64,16% đơn là giao liên bang, mất trung bình 15,13 ngày so với 7,95 ngày của đơn trong bang, và trễ 9,25% so với 6,08%.
- Khoảng cách địa lý giữa người bán và khách là yếu tố đi kèm rõ nhất với thời gian giao.

<details><summary>Câu SQL</summary>

```sql
WITH route AS (
    -- Một đơn là "liên bang" nếu có ít nhất một dòng hàng do người bán ở bang khác gửi.
    SELECT f.order_id, MAX((s.state <> c.state)::INT) AS cross_state
    FROM v_fact_order_items f
    JOIN v_dim_seller s ON f.seller_id = s.seller_id
    JOIN v_dim_customer c ON f.customer_id = c.customer_id
    GROUP BY f.order_id
)
SELECT CASE WHEN r.cross_state = 1 THEN 'Liên bang' ELSE 'Trong bang' END AS route,
       COUNT(*) AS delivered_orders,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS share_pct,
       ROUND(AVG(o.delivery_days), 2) AS avg_delivery_days,
       ROUND(100.0 * AVG(o.is_late::INT), 2) AS late_rate_pct
FROM route r
JOIN v_fact_orders o ON r.order_id = o.order_id
WHERE o.is_delivered
GROUP BY r.cross_state
ORDER BY r.cross_state
```

</details>

## Mục 20 — Phân tích đánh giá khách hàng

### Phân bố điểm đánh giá

**Câu hỏi:** Khách hài lòng đến mức nào? (mỗi đơn tính một đánh giá)

| Điểm | Số đơn | Tỷ trọng (%) |
| ---: | ---: | ---: |
| 1 | 9.353 | 9,76 |
| 2 | 2.920 | 3,05 |
| 3 | 7.918 | 8,26 |
| 4 | 18.894 | 19,72 |
| 5 | 56.747 | 59,22 |

**Nhận xét:**

- 59,22% đơn được 5 sao, nhưng điểm 1 sao (9,76%) lại nhiều hơn điểm 2 sao (3,05%) và 3 sao (8,26%). Phân bố có hai đỉnh: khách hoặc rất hài lòng, hoặc rất bất mãn.
- Tổng cộng 12,81% đơn bị đánh giá 1–2 sao. Điểm trung bình che mất nhóm này, nên phần sau theo dõi thêm tỷ lệ đánh giá thấp.

<details><summary>Câu SQL</summary>

```sql
WITH review_per_order AS (
    SELECT order_id, review_score
    FROM v_fact_reviews
    QUALIFY ROW_NUMBER() OVER (
        PARTITION BY order_id ORDER BY date_key DESC, review_id DESC
    ) = 1
)
SELECT r.review_score,
       COUNT(*) AS orders,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS share_pct
FROM review_per_order r
JOIN v_fact_orders o ON r.order_id = o.order_id
WHERE o.is_delivered
GROUP BY r.review_score
ORDER BY r.review_score
```

</details>

### Điểm đánh giá: đơn đúng hạn so với đơn giao trễ

**Câu hỏi:** Đơn giao trễ có điểm đánh giá khác đơn đúng hạn không?

| Tình trạng giao | Số đơn có đánh giá | Điểm TB | Đánh giá 1–2 sao (%) | Đánh giá 5 sao (%) |
| --- | ---: | ---: | ---: | ---: |
| Đúng hạn | 88.171 | 4,29 | 9,22 | 62,43 |
| Giao trễ | 7.661 | 2,57 | 54,05 | 22,24 |

**Nhận xét:**

- Đơn đúng hạn được 4,29 điểm, đơn giao trễ được 2,57 điểm (chênh 1,72 điểm).
- Tỷ lệ đánh giá 1–2 sao là 54,05% ở đơn trễ so với 9,22% ở đơn đúng hạn, gấp 5,9 lần.

<details><summary>Câu SQL</summary>

```sql
WITH review_per_order AS (
    SELECT order_id, review_score
    FROM v_fact_reviews
    QUALIFY ROW_NUMBER() OVER (
        PARTITION BY order_id ORDER BY date_key DESC, review_id DESC
    ) = 1
)
SELECT CASE WHEN o.is_late THEN 'Giao trễ' ELSE 'Đúng hạn' END AS delivery_status,
       COUNT(*) AS orders_with_review,
       ROUND(AVG(r.review_score), 2) AS avg_review_score,
       ROUND(100.0 * AVG((r.review_score <= 2)::INT), 2) AS low_review_pct,
       ROUND(100.0 * AVG((r.review_score = 5)::INT), 2) AS five_star_pct
FROM review_per_order r
JOIN v_fact_orders o ON r.order_id = o.order_id
WHERE o.is_delivered
GROUP BY o.is_late
ORDER BY o.is_late
```

</details>

### Điểm đánh giá theo mức độ trễ

**Câu hỏi:** Trễ càng lâu thì điểm có càng thấp không (quan hệ liều lượng – đáp ứng)?

| Mức độ so với ngày dự kiến | Số đơn có đánh giá | Điểm TB | Đánh giá 1–2 sao (%) |
| --- | ---: | ---: | ---: |
| Sớm từ 7 ngày trở lên | 70.929 | 4,32 | 8,98 |
| Sớm dưới 7 ngày | 17.234 | 4,20 | 10,24 |
| Trễ tới 3 ngày | 2.636 | 3,77 | 19,12 |
| Trễ 3–7 ngày | 1.773 | 2,32 | 61,25 |
| Trễ 7–14 ngày | 1.748 | 1,74 | 78,15 |
| Trễ trên 14 ngày | 1.504 | 1,71 | 78,79 |

**Nhận xét:**

- Điểm trung bình giảm đều qua từng mức trễ, từ 4,32 xuống 1,71: trễ càng lâu điểm càng thấp.
- Quan hệ kiểu 'liều lượng – đáp ứng' này làm mối liên hệ đáng tin hơn so với chỉ so hai nhóm, nhưng vẫn chưa phải bằng chứng nhân quả.

<details><summary>Câu SQL</summary>

```sql
WITH review_per_order AS (
    SELECT order_id, review_score
    FROM v_fact_reviews
    QUALIFY ROW_NUMBER() OVER (
        PARTITION BY order_id ORDER BY date_key DESC, review_id DESC
    ) = 1
),
scored AS (
    SELECT r.review_score, (epoch(o.order_delivered_customer_date) - epoch(o.order_estimated_delivery_date)) / 86400.0 AS days_vs_estimate
    FROM review_per_order r
    JOIN v_fact_orders o ON r.order_id = o.order_id
    WHERE o.is_delivered AND o.order_delivered_customer_date IS NOT NULL
),
bucketed AS (
    SELECT review_score,
           CASE
               WHEN days_vs_estimate <= -7 THEN 1
               WHEN days_vs_estimate <= 0 THEN 2
               WHEN days_vs_estimate <= 3 THEN 3
               WHEN days_vs_estimate <= 7 THEN 4
               WHEN days_vs_estimate <= 14 THEN 5
               ELSE 6
           END AS bucket_index
    FROM scored
)
SELECT bucket_index,
       CASE bucket_index
           WHEN 1 THEN 'Sớm từ 7 ngày trở lên' WHEN 2 THEN 'Sớm dưới 7 ngày'
           WHEN 3 THEN 'Trễ tới 3 ngày' WHEN 4 THEN 'Trễ 3–7 ngày'
           WHEN 5 THEN 'Trễ 7–14 ngày' ELSE 'Trễ trên 14 ngày'
       END AS delay_level,
       COUNT(*) AS orders_with_review,
       ROUND(AVG(review_score), 2) AS avg_review_score,
       ROUND(100.0 * AVG((review_score <= 2)::INT), 2) AS low_review_pct
FROM bucketed
GROUP BY bucket_index
ORDER BY bucket_index
```

</details>

### Kiểm định chi-bình-phương về tính độc lập

**Câu hỏi:** Khác biệt về điểm giữa đơn đúng hạn và đơn trễ có thể chỉ do ngẫu nhiên không?

Giả thuyết H0: tình trạng giao (đúng hạn / trễ) và điểm đánh giá độc lập với nhau.

| | 1 sao | 2 sao | 3 sao | 4 sao | 5 sao | Tổng |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Đúng hạn (thực tế) | 5.812 | 2.320 | 7.046 | 17.950 | 55.043 | 88.171 |
| Đúng hạn (kỳ vọng nếu độc lập) | 8.605 | 2.687 | 7.285 | 17.384 | 52.211 | |
| Giao trễ (thực tế) | 3.541 | 600 | 872 | 944 | 1.704 | 7.661 |
| Giao trễ (kỳ vọng nếu độc lập) | 748 | 233 | 633 | 1.510 | 4.536 | |

| Chỉ số | Giá trị |
| --- | ---: |
| Số đơn trong bảng chéo | 95.832 |
| Thống kê chi-bình-phương | 14.218,96 |
| Bậc tự do | 4 |
| p-value | < 0,001 |
| Cramér's V | 0,385 (trung bình) |

**Nhận xét:**

- p-value < 0,001 nên bác bỏ H0 ở mức ý nghĩa 5%: hai biến có liên hệ về mặt thống kê.
- Với 95.832 đơn, gần như khác biệt nào cũng có ý nghĩa thống kê, nên phải đọc thêm độ mạnh: Cramér's V = 0,385, mức trung bình.
- Dòng 'kỳ vọng nếu độc lập' cho thấy lệch nằm ở đâu: đơn trễ nhận điểm 1 sao nhiều hơn hẳn mức kỳ vọng.
- Kiểm định được tự cài bằng Python thuần trong `src/analytics/stats.py` và có test đối chiếu giá trị chuẩn.

<details><summary>Câu SQL</summary>

```sql
WITH review_per_order AS (
    SELECT order_id, review_score
    FROM v_fact_reviews
    QUALIFY ROW_NUMBER() OVER (
        PARTITION BY order_id ORDER BY date_key DESC, review_id DESC
    ) = 1
)
SELECT o.is_late, r.review_score, COUNT(*) AS orders
FROM review_per_order r
JOIN v_fact_orders o ON r.order_id = o.order_id
WHERE o.is_delivered
GROUP BY o.is_late, r.review_score
ORDER BY o.is_late, r.review_score
```

</details>

### Một yếu tố khác cũng đi kèm điểm thấp: đơn có nhiều người bán

**Câu hỏi:** Ngoài giao trễ, còn yếu tố nào đi kèm điểm thấp? (lý do không kết luận nhân quả)

| Tình trạng giao | Số người bán trong đơn | Số đơn có đánh giá | Điểm TB |
| --- | --- | ---: | ---: |
| Đúng hạn | 1 người bán | 86.927 | 4,31 |
| Đúng hạn | Từ 2 người bán | 1.244 | 2,87 |
| Giao trễ | 1 người bán | 7.644 | 2,57 |
| Giao trễ | Từ 2 người bán | 17 | 2,00 |

**Nhận xét:**

- Ngay cả khi giao đúng hạn, đơn có từ 2 người bán chỉ được 2,87 điểm so với 4,31 của đơn một người bán.
- Vậy giao trễ không phải yếu tố duy nhất đi kèm điểm thấp. Một phân tích nhân quả phải kiểm soát các yếu tố như thế này.

<details><summary>Câu SQL</summary>

```sql
WITH review_per_order AS (
    SELECT order_id, review_score
    FROM v_fact_reviews
    QUALIFY ROW_NUMBER() OVER (
        PARTITION BY order_id ORDER BY date_key DESC, review_id DESC
    ) = 1
),
sellers_per_order AS (
    SELECT order_id, COUNT(DISTINCT seller_id) AS sellers
    FROM v_fact_order_items
    GROUP BY order_id
)
SELECT CASE WHEN o.is_late THEN 'Giao trễ' ELSE 'Đúng hạn' END AS delivery_status,
       CASE WHEN s.sellers > 1 THEN 'Từ 2 người bán' ELSE '1 người bán' END AS sellers_in_order,
       COUNT(*) AS orders_with_review,
       ROUND(AVG(r.review_score), 2) AS avg_review_score
FROM review_per_order r
JOIN v_fact_orders o ON r.order_id = o.order_id
JOIN sellers_per_order s ON r.order_id = s.order_id
WHERE o.is_delivered
GROUP BY o.is_late, (s.sellers > 1)
ORDER BY o.is_late, (s.sellers > 1)
```

</details>

### Kết luận về mối liên hệ giữa giao trễ và đánh giá

Giao trễ và điểm đánh giá thấp **đi kèm nhau rõ rệt và có ý nghĩa thống kê**. Báo cáo này **không kết luận giao trễ là nguyên nhân** của điểm thấp, vì bốn lý do:

1. Đây là dữ liệu quan sát, không phải thí nghiệm có nhóm đối chứng.
2. Có yếu tố khác cùng đi kèm điểm thấp (đơn nhiều người bán, khác biệt giữa các danh mục) và các yếu tố này có thể liên quan tới cả việc giao trễ.
3. Một phần đơn delivered không có đánh giá; khách không đánh giá có thể khác khách có đánh giá.
4. Kiểm định chi-bình-phương chỉ cho biết hai biến không độc lập, không cho biết chiều tác động.

Muốn kết luận nhân quả cần thêm một mô hình có kiểm soát biến (ví dụ hồi quy logistic cho xác suất nhận 1–2 sao) hoặc một thử nghiệm thực tế.

## Hạn chế

- Dữ liệu là một mẫu lịch sử tĩnh; năm đầu rất thưa và các tháng cuối chưa đủ đơn delivered.
- Doanh thu gồm phí vận chuyển và không trừ hoàn hủy sau giao; đây là doanh thu gộp, không phải lợi nhuận.
- Tên sản phẩm và danh tính người bán đã được ẩn danh, nên chỉ phân tích được theo mã và danh mục.
- Các mối liên hệ trong báo cáo là mô tả; chưa có mô hình nhân quả hay dự báo.
