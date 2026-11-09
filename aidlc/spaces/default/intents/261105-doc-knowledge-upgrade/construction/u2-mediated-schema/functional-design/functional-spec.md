# Functional Spec — u2-mediated-schema

Đơn vị: `u2-mediated-schema` (Lược đồ trung gian). Phục vụ US1.2, US1.3 (AC1.2.x, AC1.3.x) và phần dữ liệu của US1.1, US6.1. Sở hữu tệp khai báo lược đồ, bộ nạp và kiểm tra, cùng hai hợp đồng C1 (cho U3) và C2 (cho U5). **Không** sinh SQL, **không** gọi DuckDB, **không** hiển thị gì.

## Nguồn vào

| Thứ | Lấy từ | Ghi chú |
|---|---|---|
| Tệp khai báo | `config/mediated-schema.yaml` do U1 bàn giao (C8) | U1 đã bàn giao **ba thực thể** (`don_hang` 7 trường, `mat_hang` 5, `san_pham` 2, mọi trường `loaded: true`); U2 chỉ đọc và kiểm |
| Danh sách bảng nguồn và cột | `src/ingest/schemas.py` (`TABLE_SPECS`) | Một nguồn sự thật duy nhất; không khai lại tên bảng/cột ở chỗ khác |
| Siêu dữ liệu CSV | tiêu đề tệp trong `dataset/` | Kiểm cột nêu trong ánh xạ có thật |

## Workflow 1 — Nạp và kiểm lược đồ

1. Đọc `config/mediated-schema.yaml` bằng `yaml.safe_load`; tệp không đọc được → `SchemaError` nêu đường dẫn và lỗi.
2. Kiểm cấu trúc: `schema_kind` phải là `GAV`; mỗi thực thể có `name`, `source_tables`, `fields` không rỗng; mỗi trường có `field_name`, `source_table`, `source_column`, `data_type` thuộc tập đóng `string|integer|decimal|timestamp`, và cờ `loaded` (mặc định `true` nếu thiếu).
3. Kiểm mọi `field_name` là duy nhất trong một thực thể; mọi `source_table` xuất hiện trong `entities[].source_tables`.
4. Với mỗi thực thể: đọc **tiêu đề** các tệp nguồn của nó (không đọc dữ liệu) và kiểm từng `source_column` có thật.
5. Trả `MediatedSchemaView` (C1) gồm `entities`, `mappings`, `schema_kind`.

**Lỗi:** nêu **tên trường và tên cột**; không tự sửa ánh xạ, không tự bỏ qua trường sai (BR2.5).

## Workflow 2 — Cung cấp view cho U3 (C1)

1. Trả `entities` (name, description, source_tables), `mappings` (dict theo tên thực thể, mỗi phần tử có `field_name`, `source_table`, `source_column`, `data_type`), `schema_kind`.
2. Không lọc theo truy vấn: U3 hỏi trường nào thì đọc trường đó từ view.

## Workflow 3 — Cung cấp danh mục trường cho U5 (C2)

1. Trả `fields_by_entity`: dict tên thực thể → danh sách chuỗi `"entity.field"`.
2. Danh mục dẫn xuất từ view, không đọc lại tệp.

## Workflow 4 — Một phần và lỗi

| Tình huống | Hành vi |
|---|---|
| Thiếu một thực thể trong tệp nhưng tệp vẫn hợp lệ | Trả view với các thực thể có được; kèm kênh `partial` nêu tệp thiếu thực thể nào và vì sao (BR2.8) |
| Ba thực thể đều có | Không có `partial` |
| Một trường trỏ tới bảng nguồn không khai trong `source_tables` | `SchemaError` — đây là lỗi cấu trúc, không phải "một phần" |
| Tệp thiếu hẳn | `ConfigurationError` (không phải `SchemaError`): thiếu tệp là lỗi cấu hình, khớp `src/integration/schema.py` và test `test_load_schema_rejects_a_missing_file` đang xanh |

## Hợp đồng bàn giao

| Hợp đồng | Nội dung | Ghi chú |
|---|---|---|
| C8 (nhận từ U1) | Tệp lược đồ **ba thực thể** — `don_hang` 7 trường, `mat_hang` 5, `san_pham` 2, mọi trường `loaded: true`; U2 chỉ đọc và kiểm, không mở rộng | Không đổi tên/thứ tự trường đang có, không đổi tên `don_hang` |
| C1 (bàn giao U3) | `MediatedSchemaView` | `change_policy`: chỉ thêm trường |
| C2 (bàn giao U5) | `MediatedFieldCatalogue` | `change_policy`: chỉ thêm tên trường |

## Không nằm trong đơn vị này

| Không làm | Vì sao |
|---|---|
| Sinh SQL, kế hoạch viết lại | Thuộc U3 |
| Chọn nguồn | Thuộc U5 |
| Hiển thị màn hình lược đồ | Thuộc U6 (đọc view qua C6) |
| Đọc dữ liệu nguồn để kiểm giá trị | Chỉ kiểm tiêu đề; kiểm giá trị thuộc tầng chất lượng đã có |

## Giả định và câu hỏi mở

| # | Nội dung | Trạng thái |
|---|---|---|
| A1 | Tệp lược đồ do người sửa tay, không sinh tự động | Đúng theo C8; vì vậy mọi lỗi phải nêu rõ chỗ sai |
| A2 | Ba thực thể dùng chung bảng nguồn ở mức bảng, không join trong ánh xạ | Đúng GAV: mỗi trường là một biểu thức trên **một** bảng |
| Q1 | Khi một trường có `loaded: false`, U2 có cần đưa nó vào `mappings` không? (Tệp C8 hiện tại **không còn ca này**: mọi trường đều `loaded: true`, kể cả `bang_giao`.) | Không chặn: luật vẫn giữ cho trường hợp tương lai — đưa vào (U3 có thể đọc) và giữ cờ `loaded` để bên dùng biết trường chưa được nạp |
| Q2 | Có cần kiểm cả kiểu dữ liệu khớp với cột nguồn (ví dụ cột ngày phải là `timestamp`) không? | Không chặn: hiện chỉ kiểm kiểu thuộc tập đóng; kiểm khớp kiểu cần đọc dữ liệu, thuộc tầng chất lượng |
