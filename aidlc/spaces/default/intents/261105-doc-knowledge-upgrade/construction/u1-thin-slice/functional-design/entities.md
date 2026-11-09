# Entities — u1-thin-slice

Nguồn: `inception/units-generation/unit-of-work.md` (đơn vị U1), `inception/requirements-analysis/requirements.md` (FR1.2, FR2.1–FR2.4), `inception/domain-design/components.md` (thực thể `MediatedEntity` và `FieldMapping`).

```yaml
entities:
  - name: DonHang
    description: Một đơn hàng trong lược đồ trung gian, phiên bản tối thiểu cho lát cắt
    attributes:
      - name: ma_don
        type: string
        required: true
        unique: true
        source_table: olist_orders_dataset
        source_column: order_id
        description: Mã đơn, khoá chính của thực thể
      - name: ngay_dat
        type: timestamp
        required: true
        unique: false
        source_table: olist_orders_dataset
        source_column: order_purchase_timestamp
        description: Thời điểm đặt đơn, dùng để nhóm theo tháng
      - name: trang_thai
        type: enum
        required: true
        unique: false
        source_table: olist_orders_dataset
        source_column: order_status
        allowed: [created, approved, invoiced, processing, shipped, delivered, unavailable, canceled]
        description: Trạng thái đơn tại thời điểm trích xuất
      - name: ma_khach
        type: string
        required: true
        unique: false
        source_table: olist_orders_dataset
        source_column: customer_id
        description: Mã khách của đơn (customer_id, không phải customer_unique_id)
      - name: bang_giao
        type: string
        required: false
        unique: false
        source_table: olist_customers_dataset
        source_column: customer_state
        description: Bang nhận hàng; nguồn nằm ở bảng khách nên lát cắt này để rỗng và chưa nạp
    constraints:
      - ma_don là duy nhất trên toàn bộ thực thể
      - ngay_dat không được ở tương lai so với thời điểm chạy
      - bốn trường đầu nạp được từ một bảng nguồn duy nhất; bang_giao cần bảng khách nên thuộc đơn vị sau
    mappings:
      schema_kind: GAV
      list:
        - entity: DonHang
          field: ma_don
          source_table: olist_orders_dataset
          source_column: order_id
        - entity: DonHang
          field: ngay_dat
          source_table: olist_orders_dataset
          source_column: order_purchase_timestamp
        - entity: DonHang
          field: trang_thai
          source_table: olist_orders_dataset
          source_column: order_status
        - entity: DonHang
          field: ma_khach
          source_table: olist_orders_dataset
          source_column: customer_id
        - entity: DonHang
          field: bang_giao
          source_table: olist_customers_dataset
          source_column: customer_state
    relationships: []
```

## Tóm tắt

Một thực thể, năm trường, năm ánh xạ. Bốn trường đầu nạp được từ `olist_orders_dataset` — đủ cho lát cắt chạy mà không cần join. `bang_giao` có ánh xạ tới `olist_customers_dataset` nhưng **chưa được nạp trong lát cắt** vì cần bảng khách; trường này tồn tại để đơn vị sau dùng cho truy vấn giao trễ mà không phải đổi hình dạng thực thể.

`trang_thai` dùng đúng tám giá trị đang có trong dữ liệu Olist.

Ánh xạ giữ dạng `GAV`: mỗi trường trung gian là một biểu thức trên bảng nguồn, đúng hợp đồng C8 (U1 bàn giao tệp lược đồ đầu tiên cho U2).

**C8 — phần bàn giao thật.** Hợp đồng C8 khai hình dạng tệp: `entities` là danh sách bản ghi, mỗi trường có `field_name`, `source_table`, `source_column`, `data_type`, `loaded` (xem `contract-summary.md` §C8). Tệp `config/mediated-schema.yaml` hiện có **ba thực thể** (`don_hang`, `mat_hang`, `san_pham`) và `don_hang` có **bảy trường**: năm trường của lát cắt (`ma_don`, `ngay_dat`, `trang_thai`, `ma_khach`, `bang_giao`) cộng hai trường ngày giao (`ngay_giao_thuc_te`, `ngay_giao_du_kien`) do đơn vị sau thêm theo `change_policy` của C8. Trong bản bàn giao hiện tại **mọi trường đều `loaded: true`**, kể cả `bang_giao`; ghi chú "chưa nạp" của lát cắt chỉ đúng ở thời điểm Bolt 1. Ai đổi `loaded` phải sửa cả tệp lẫn mục này trong cùng thay đổi.
