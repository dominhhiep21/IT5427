# Entities — u1-mart-and-baseline

Đơn vị: `u1-mart-and-baseline` (kind `library`). Nguồn: `../../../inception/units-generation/unit-of-work.md` (định nghĩa U1 và ranh giới của nó), `../../../inception/domain-design/components.md`, `../../../inception/contract-design/contract-summary.md` (C1), `../../../inception/requirements-analysis/requirements.md`.

Phạm vi entity của đơn vị này là **hai bảng fact sau khi thêm cột** và **hợp đồng ba cột** mà nó bảo đảm. Đơn vị này **không** sở hữu `TrainingFrame` (grain dòng hàng thuộc U2), **không** sở hữu `CohortCounts` (bốn bộ đếm thuộc U2), và **không** sở hữu `BaselineMeasurement` (entity đó thuộc `ModelModule`, do U2 lắp; U1 chỉ cung cấp hàm trả một số).

```yaml
entities:
  - name: MartOrder
    description: >
      Một dòng cho mỗi đơn hàng (13 cột hiện có, thêm 2). Đơn vị này KHÔNG đổi grain
      (vẫn order_id), KHÔNG đổi lọc, KHÔNG đổi số dòng.
    attributes:
      - name: order_id
        type: identifier
        required: true
        unique: true
      - name: customer_id
        type: identifier
        required: true
      - name: date_key
        type: date
        required: true
        note: ngày đặt hàng; cột chia tập cho cả mô hình lẫn baseline
      - name: category
        type: string
        required: true
        note: phạm trù trội của đơn; "unknown" khi không xác định được
      - name: order_status
        type: string
        required: true
      - name: is_delivered
        type: boolean
        required: true
      - name: order_delivered_customer_date
        type: timestamp
        required: false
        nullable: true
      - name: order_estimated_delivery_date
        type: timestamp
        required: false
        nullable: true
      - name: delivery_days
        type: decimal
        required: false
        nullable: true
        note: đã có từ trước; số ngày đặt → giao khách
      - name: is_late
        type: boolean
        required: true
      - name: has_items
        type: boolean
        required: true
      - name: has_payment
        type: boolean
        required: true
      - name: has_review
        type: boolean
        required: true
      - name: order_approved_at
        type: timestamp
        required: false
        nullable: true
        added_by: u1-mart-and-baseline
        note: >
          160 giá trị null trên dữ liệu thật. Giữ nguyên dạng mốc thời gian; việc dẫn xuất
          thành số ngày là của U2, và dạng thô bị cấm làm đặc trưng (BR1.3).
      - name: order_delivered_carrier_date
        type: timestamp
        required: false
        nullable: true
        added_by: u1-mart-and-baseline
        note: 1.783 giá trị null trên dữ liệu thật; cùng quy tắc với order_approved_at.
    constraints:
      - "số dòng của bảng không đổi so với trước khi thêm cột (13 → 15 cột, số dòng nguyên)"
      - "không dòng nào bị thêm hoặc bớt vì hai cột mới"

  - name: MartOrderItem
    description: >
      Một dòng cho mỗi cặp đơn × món (12 cột hiện có, thêm 1). Không đổi grain
      (vẫn order_id + order_item_id) và không đổi số dòng.
    attributes:
      - name: order_id
        type: identifier
        required: true
        note: phần thứ nhất của khoá kép
      - name: order_item_id
        type: identifier
        required: true
        note: phần thứ hai của khoá kép
      - name: customer_id
        type: identifier
        required: true
      - name: product_id
        type: identifier
        required: true
      - name: seller_id
        type: identifier
        required: true
      - name: date_key
        type: date
        required: true
      - name: price
        type: decimal
        required: true
      - name: freight_value
        type: decimal
        required: true
      - name: item_total
        type: decimal
        required: true
        note: price + freight_value
      - name: price_outlier
        type: boolean
        required: true
      - name: order_status
        type: string
        required: true
      - name: is_delivered
        type: boolean
        required: true
      - name: seller_state
        type: string
        required: false
        nullable: true
        added_by: u1-mart-and-baseline
        allowed_values: "mã bang 2 chữ hoa; dữ liệu thật có 23 giá trị khác nhau"
        name_rule: >
          Tên PHẢI là `seller_state`, không được là `state`: `dim_customer` đã có cột `state`
          và `agg_sales_daily` nối hai bảng này, nên một cột tên `state` sẽ sinh `state_x`/
          `state_y` và làm hỏng tổng hợp (BR1.7).
        source_rule: >
          Lấy bằng nối `dim_seller` trên `seller_id` rồi đổi tên `state` → `seller_state`.
          KHÔNG suy từ địa chỉ khách, KHÔNG suy từ geolocation khi thiếu bản ghi.
        note: >
          Trên dữ liệu thật cả 3.095 người bán đều có bản ghi `dim_seller`, nên nhánh null
          không xảy ra ở dữ liệu này — nó vẫn phải có vì mart không được phép làm mất dòng
          khi nguồn thiếu.
    constraints:
      - "số dòng của bảng không đổi so với trước khi thêm cột (12 → 13 cột, số dòng nguyên)"
      - "mọi giá trị seller_state khác null phải khớp đúng một bản ghi dim_seller"

  - name: MartColumnContract
    description: >
      Hợp đồng ba cột mới (C1). Không phải bảng dữ liệu mà là danh sách điều kiện mà các
      tầng sau dựa vào.
    attributes:
      - name: view_name
        type: string
        required: true
        allowed_values: [v_fact_orders, v_fact_order_items]
      - name: column_name
        type: string
        required: true
        allowed_values: [order_approved_at, order_delivered_carrier_date, seller_state]
      - name: grain_preserved
        type: boolean
        required: true
        note: luôn đúng; đổi thành sai là thay đổi phá vỡ hợp đồng
      - name: row_count_before
        type: integer
        required: true
        note: lấy từ hợp đồng số dòng đã chốt (9 bảng + 11 view), không phải từ lần chạy trước
      - name: row_count_after
        type: integer
        required: true
        note: phải bằng row_count_before
    constraints:
      - "không cột nào trong danh sách này được đổi tên sau khi phát hành"
```

## Tóm tắt bộ entity

Ba entity: hai **bảng fact có thật** và một **danh sách điều kiện**. Không entity nào đổi grain — ba cột mới là thay đổi *thuần thêm* ở cấp cột, nên rủi ro hồi quy kiểm được bằng phép đếm dòng thay vì bằng cách đọc lại toàn bộ 5 KPI.

**Vì sao `BaselineMeasurement` không còn ở đây.** Bản trước khai nó là entity của U1 và cho hàm trả cả cấu trúc. Cả hai đều sai: `components.md` gán `BaselineMeasurement` cho `ModelModule`, và hợp đồng C1 đã chốt chữ ký trả `float`. Hàm của U1 trả **một số AUC**; cấu trúc mang `cohort_rows`/`same_split_as_model` do U2 lắp, vì `cohort_rows` chính là bộ đếm mà C1 cấm U1 khai.

**Vì sao tên cột là `seller_state` chứ không phải `state`.** Đây không phải chuyện đặt tên cho đẹp: `dim_customer` đã có cột `state`, và `agg_sales_daily` nối `dim_customer` với `fact_order_item`. Một cột tên `state` ở bảng fact sẽ sinh `state_x`/`state_y` và làm hỏng tổng hợp — tức đúng bất biến số dòng mà đơn vị này tồn tại để bảo vệ.
