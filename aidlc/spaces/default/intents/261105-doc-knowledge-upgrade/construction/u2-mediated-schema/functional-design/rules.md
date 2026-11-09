# Business Rules — u2-mediated-schema

Nguồn: `inception/domain-design/components.md` (khối `MediatedSchema`: ba thực thể, ánh xạ GAV, kiểm cột nguồn, báo lỗi nêu trường và cột), `inception/requirements-analysis/requirements.md` (FR1.1–FR1.4), `inception/contract-design/contract-summary.md` (C1, C2, C8), `inception/user-stories/stories.md` (US1.2, US1.3).

```yaml
rules:
  - id: BR2.1
    statement: Lược đồ phải khai đủ ba thực thể trung gian
    category: validation
    applies_to: MediatedSchemaView
    trigger: khi nạp tệp khai báo
    logic: >
      Trường `entities` phải chứa `don_hang`, `mat_hang`, `san_pham`. Thiếu thực thể nào thì
      view vẫn trả các thực thể có được, kèm kênh `partial` nêu tên thực thể thiếu và lý do.
      Đây là "một phần", không phải lỗi cấu trúc.
    violation: kênh partial có mặt; bên dùng hiện trạng thái "một phần"
    source: FR1.1

  - id: BR2.2
    statement: Mọi ánh xạ phải trỏ tới bảng và cột nguồn có thật
    category: validation
    applies_to: FieldMapping
    trigger: khi nạp tệp khai báo
    logic: >
      `source_table` là **tên tệp nguồn** như C8 đang dùng (`olist_orders_dataset`, `olist_customers_dataset`, …),
      không phải khoá nội bộ của `TABLE_SPECS`. Bộ nạp tra `TableSpec` theo `file_name`, không đòi người
      sửa tệp biết khoá nội bộ. `source_column` phải có trong tiêu đề thật của tệp đó.
      Với trường có `loaded: false`, vẫn kiểm cột nguồn.
    violation: SchemaError nêu tên trường và tên cột; dừng nạp
    source: FR1.2

  - id: BR2.3
    statement: Tên bảng, tên cột và tên trường phải là định danh hợp lệ
    category: validation
    applies_to: FieldMapping
    trigger: khi nạp tệp khai báo
    logic: >
      Mỗi tên phải khớp `^[a-z][a-z0-9_]*$`, tối đa 64 ký tự, và (với bảng/cột) nằm trong tập
      cho phép lấy từ `TABLE_SPECS` và tiêu đề thật. Không "làm sạch" tên sai; từ chối.
    violation: SchemaError
    source: FR1.2

  - id: BR2.4
    statement: Lược đồ là GAV, mỗi trường là một biểu thức trên đúng một bảng nguồn
    category: policy
    applies_to: FieldMapping
    trigger: khi kiểm cấu trúc
    logic: >
      `schema_kind` phải bằng `GAV`. Mỗi trường có đúng một `source_table`; không có trường nào
      trỏ tới hai bảng, không có điều kiện join trong ánh xạ.
    violation: SchemaError nêu trường vi phạm
    source: FR1.1

  - id: BR2.5
    statement: Kiểu dữ liệu thuộc tập đóng
    category: validation
    applies_to: FieldMapping
    trigger: khi kiểm cấu trúc
    logic: >
      `data_type` phải thuộc `string | integer | decimal | timestamp`. Giá trị khác là lỗi,
      không tự quy về `string`.
    violation: SchemaError nêu trường và kiểu sai
    source: FR1.3

  - id: BR2.6
    statement: Tên trường duy nhất trong một thực thể, thứ tự ổn định
    category: validation
    applies_to: MediatedEntity
    trigger: khi kiểm cấu trúc
    logic: >
      Hai trường cùng `field_name` trong một thực thể là lỗi. Thứ tự trường giữ theo tệp khai báo,
      để bảng hiển thị và danh mục trường ổn định giữa các lần chạy.
    violation: SchemaError nêu tên trường trùng
    source: FR1.2

  - id: BR2.7
    statement: Danh mục trường dẫn xuất từ view, không đọc lại tệp
    category: calculation
    applies_to: MediatedFieldCatalogue
    trigger: khi bên dùng hỏi danh mục
    logic: >
      `fields_by_entity[name]` = danh sách `"<name>.<field_name>"` theo đúng thứ tự trường của
      thực thể đó. Không có mục cho thực thể thiếu.
    violation: không có
    source: FR1.3

  - id: BR2.8
    statement: Lỗi phải nêu tên trường và tên cột, không tự sửa
    category: policy
    applies_to: SchemaError
    trigger: khi một ánh xạ sai
    logic: >
      Câu lỗi phải chứa `field_name` và `source_column` (và `source_table` khi có).
      Không có nhánh nào tự sửa tệp, tự đổi cột hay tự bỏ qua trường sai.
    violation: không có — quy tắc về thông điệp lỗi
    source: FR1.2

  - id: BR2.9
    statement: Thay đổi chỉ được cộng thêm
    category: policy
    applies_to: MediatedSchemaView, MediatedFieldCatalogue
    trigger: khi sửa tệp khai báo
    logic: >
      Thêm thực thể hoặc trường là thay đổi an toàn; đổi nghĩa một trường, đổi `source_column`
      của trường đang dùng, hoặc đổi tên thực thể là thay đổi phá vỡ và phải sửa cả bên dùng
      (U3, U5) cùng test trong một thay đổi.
    violation: không có — quy tắc hợp đồng
    source: FR1.4
```

## Tóm tắt quy tắc

| Mã | Loại | Nội dung ngắn |
|---|---|---|
| BR2.1 | Kiểm tra | Đủ ba thực thể; thiếu thì là "một phần" |
| BR2.2 | Kiểm tra | Mọi ánh xạ trỏ tới bảng/cột nguồn có thật |
| BR2.3 | Kiểm tra | Định danh hợp lệ, không làm sạch ngầm |
| BR2.4 | Chính sách | GAV: một trường, một bảng, không join |
| BR2.5 | Kiểm tra | `data_type` thuộc tập đóng |
| BR2.6 | Kiểm tra | `field_name` duy nhất, thứ tự ổn định |
| BR2.7 | Tính toán | Danh mục trường dẫn xuất từ view |
| BR2.8 | Chính sách | Lỗi nêu trường và cột, không tự sửa |
| BR2.9 | Chính sách | Chỉ thay đổi cộng thêm |
