# Entities — u2-mediated-schema

Nguồn: `inception/domain-design/components.md` (khối `MediatedSchema`: `MediatedEntity`, `FieldMapping`), `inception/contract-design/contract-summary.md` (C1 `MediatedSchemaView`, C2 `MediatedFieldCatalogue`, C8), `inception/user-stories/stories.md` (US1.2), `inception/units-generation/unit-of-work.md` (§U2 — biên giới "không sinh SQL, không gọi DuckDB, không hiển thị").

```yaml
entities:
  - name: MediatedEntity
    description: Một thực thể trung gian (don_hang, mat_hang, san_pham) cùng các bảng nguồn nó dùng
    attributes:
      - name: name
        type: string
        required: true
        unique: true
        description: Tên thực thể, định danh hợp lệ (BR2.3)
      - name: description
        type: string
        required: false
        description: Câu mô tả ngắn, không tham gia bất kỳ phép kiểm nào
      - name: source_tables
        type: list[string]
        required: true
        description: >
          Tên tệp nguồn thực thể này dùng (ví dụ olist_orders_dataset). Mỗi tên phải khớp
          `TableSpec.file_name` trong src/ingest/schemas.py; tra theo file_name, không theo khoá nội bộ.
    constraints:
      - Đúng ba thực thể được khai: don_hang, mat_hang, san_pham (BR2.1)
      - Không thực thể nào có hai bảng nguồn trùng nhau
      - Mỗi thực thể phải khai tập trường; tập rỗng là lỗi cấu trúc, không phải "một phần"
      - `mat_hang` giữ khoá join tới `don_hang` và `san_pham` (ví dụ mã đơn, mã sản phẩm) để U3 ghép được
    relationships:
      - entity: FieldMapping
        kind: has-many
        description: Mỗi thực thể có nhiều trường; mỗi trường thuộc đúng một thực thể

  - name: FieldMapping
    description: Ánh xạ một trường trung gian tới đúng một bảng và cột nguồn (GAV)
    attributes:
      - name: field_name
        type: string
        required: true
        unique: true
        description: Tên trường trung gian, duy nhất trong thực thể (BR2.6)
      - name: source_table
        type: string
        required: true
        description: Phải nằm trong source_tables của thực thể và trong TABLE_SPECS (BR2.2)
      - name: source_column
        type: string
        required: true
        description: Phải có thật trong tiêu đề tệp nguồn (BR2.2)
      - name: data_type
        type: enum
        required: true
        allowed: [string, integer, decimal, timestamp]
        description: Tập đóng (BR2.5)
      - name: loaded
        type: boolean
        required: false
        description: >
          Mặc định true. false nghĩa là trường đã khai và đã kiểm cột nhưng chưa được nạp
          (ví dụ bang_giao của don_hang ở lát cắt U1); vẫn nằm trong mappings để U3 biết.
    constraints:
      - Mỗi trường có đúng một source_table; không join trong ánh xạ (BR2.4)
      - Thứ tự trường giữ theo tệp khai báo (BR2.6)

  - name: MediatedSchemaView
    description: Payload của hợp đồng C1 bàn giao cho U3
    attributes:
      - name: entities
        type: list[MediatedEntity]
        required: true
      - name: mappings
        type: dict[string, list[FieldMapping]]
        required: true
      - name: schema_kind
        type: string
        required: true
        description: Hằng "GAV"
      - name: partial
        type: object
        required: false
        description: >
          Khi thiếu thực thể — { missing: [...], reason: "<câu tiếng Việt>" }; không có khi đủ ba.
    constraints:
      - `mappings` có khoá cho mọi thực thể có trong `entities`, không có khoá thừa

  - name: MediatedFieldCatalogue
    description: Payload của hợp đồng C2 bàn giao cho U5
    attributes:
      - name: fields_by_entity
        type: dict[string, list[string]]
        required: true
        description: Tên thực thể → danh sách "entity.field" theo thứ tự trường (BR2.7)
```

## Ghi chú thiết kế

- **Bốn thực thể, hai trong `components.md`.** `MediatedEntity` và `FieldMapping` là hai thực thể miền của khối `MediatedSchema`. `MediatedSchemaView` và `MediatedFieldCatalogue` là **hình chiếu của payload C1/C2**, không phải thực thể miền mới; chúng tồn tại để U2 và bên dùng có một hình dạng chung, và đổi theo hợp đồng.
- **`loaded` không phải cờ chất lượng.** Nó nói "trường này đã có trong lược đồ nhưng chưa được nạp ở đơn vị nào đó" — U3 vẫn phải thấy nó để quyết định; nếu coi `loaded: false` là "không tồn tại" thì U3 sẽ không biết trường đó có thể dùng ở đơn vị sau.
- **`partial` là kênh của C1**, không phải cờ lỗi: thiếu thực thể là trạng thái dữ liệu, còn ánh xạ sai là lỗi cấu trúc (`SchemaError`). Hai thứ này không được trộn.
