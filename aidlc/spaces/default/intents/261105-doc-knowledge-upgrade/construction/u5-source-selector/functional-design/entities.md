# Entities — u5-source-selector

Nguồn: `inception/domain-design/components.md` (khối `SourceSelector`, hai thực thể `SourceProfile`, `SourceChoice` — `SourceProfile` sở hữu `tables`), `inception/contract-design/contract-summary.md` (C2 — đầu vào; C3 và C7 — đầu ra), `inception/units-generation/unit-of-work.md` §U5, `inception/requirements-analysis/requirements.md` (FR4.1–FR4.3), và câu trả lời của người làm trong `functional-design-questions.md` (Q1, Q2, Q4, Q6, Q7 đều chọn A).

**Bản sửa sau review 1:** `tables` được khôi phục trên `SourceProfile` (R-01); `is_simulated` là dữ kiện khai trong cấu hình, không suy ra (R-06); `SourceCatalogue` mang được nhánh "một phần" (R-03); bề mặt lỗi của C7 ghi cả hai lỗi có thể đến từ C2 (R-08).

```yaml
entities:
  - name: SourceProfile
    description: Hồ sơ một nguồn dữ liệu ứng viên — bảng phủ được, khả năng đáp ứng, chi phí và độ trễ ước tính
    attributes:
      - name: source_name
        type: string
        required: true
        unique: true
        allowed: [olist_csv, ibge_cache, partner_simulated]
        description: Định danh ổn định của nguồn; hiển thị bằng nhãn tiếng Việt riêng
      - name: label
        type: string
        required: true
        description: Nhãn hiển thị tiếng Việt, ví dụ "Olist (CSV trong dataset/)"
      - name: tables
        type: list[string]
        required: true
        description: >
          Các bảng nguồn mà nguồn này cung cấp, tên đúng như trong lược đồ trung gian
          (ví dụ olist_orders_dataset, olist_order_items_dataset). Đây là dữ kiện C3 trả cho U3
          trong selected_sources[].tables, và nó được KHAI trong tệp cấu hình của nguồn,
          không suy ra từ covered_fields (C2 chỉ có mã trường, không có ánh xạ trường → bảng).
      - name: covered_fields
        type: list[string]
        required: true
        description: >
          Các mã trường "entity.field" mà nguồn phủ được, mỗi mã phải có trong
          MediatedFieldCatalogue (C2).
      - name: coverage
        type: string
        required: true
        description: >
          Câu ngắn tiếng Việt mô tả khả năng đáp ứng, dẫn xuất từ covered_fields, ví dụ
          "Đủ ba bảng: đơn hàng, mặt hàng, sản phẩm"
      - name: has_data
        type: boolean
        required: true
        description: Cờ cấu hình, không phải phép dò tệp lúc chạy; thiếu khoá là lỗi (BR5.1), không có mặc định
      - name: cost_level
        type: integer
        required: true
        min: 1
        max: 5
        description: Chi phí tương đối; 1 là rẻ nhất
      - name: latency_ms
        type: integer
        required: true
        min: 0
        description: Độ trễ ước tính tính bằng mili giây
      - name: is_simulated
        type: boolean
        required: true
        description: >
          Dữ kiện khai trong tệp cấu hình (không suy ra, không có mặc định); true với nguồn
          mô phỏng. Nguồn mô phỏng không bao giờ được chọn cho truy vấn thật (BR5.11) và
          giao diện phải ghi chú nó là nguồn mô phỏng.
    constraints:
      - source_name là duy nhất trong một bộ hồ sơ
      - Mọi mã trong covered_fields phải tồn tại trong danh mục trường C2; mã lạ làm hỏng lượt nạp, không bị bỏ qua im lặng
      - tables rỗng hợp lệ khi và chỉ khi covered_fields rỗng — nguồn như `ibge_cache` không phủ trường nào của lược đồ trung gian
      - Mỗi tên trong `tables` phải thuộc `SOURCE_TABLES` của `src/integration/schema.py` (chín tên tệp đã bỏ `.csv`); tên lạ ném `SchemaError`
      - U5 không kiểm chéo trường ↔ bảng: C2 chỉ mang mã "entity.field", không mang ánh xạ thực thể → bảng nguồn, và U5 không có hợp đồng với C1. `tables` là dữ kiện khai theo BR5.1, chỉ được kiểm tên
      - Nguồn có is_simulated = true không được phát sinh lệnh gọi mạng dưới bất kỳ hình thức nào
      - has_data = false nghĩa là nguồn không đóng góp trường nào; hồ sơ vẫn hiển thị để thấy lý do loại

  - name: SourceChoice
    description: Một dòng quyết định cho một cặp (truy vấn, nguồn) — được chọn hay bị loại, kèm lý do bằng chữ
    attributes:
      - name: query_id
        type: string
        required: true
        description: Mã truy vấn mẫu (ba truy vấn của FR2.1)
      - name: source_name
        type: string
        required: true
        references: SourceProfile.source_name
      - name: is_selected
        type: boolean
        required: true
      - name: reason
        type: string
        required: true
        description: Lý do chọn hoặc loại, câu tiếng Việt; không bao giờ rỗng
      - name: missing_fields
        type: list[string]
        required: false
        description: Chỉ có khi nguồn bị loại vì thiếu trường; liệt kê đúng các mã trường còn thiếu
      - name: tables
        type: list[string]
        required: false
        description: >
          Chỉ có khi nguồn được chọn; lấy nguyên từ SourceProfile.tables của nguồn thắng,
          không tính lại từ covered_fields
    constraints:
      - Khoá của một dòng là (query_id, source_name)
      - Với một query_id, tối đa một dòng có is_selected = true
      - reason không được rỗng với mọi dòng, kể cả dòng được chọn
      - Không sử dụng màu sắc làm tín hiệu duy nhất trong cách trình bày các dòng này

  - name: SourceCatalogue
    description: Payload C7 — bảng nguồn cho giao diện, gồm hồ sơ, các quyết định đã có, và nhánh "một phần"
    attributes:
      - name: sources
        type: list[SourceProfile]
        required: true
        description: Toàn bộ nguồn ứng viên, kể cả nguồn không có dữ liệu
      - name: choices
        type: list[SourceChoice]
        required: true
        description: Các quyết định đã tính; rỗng khi chưa đề xuất nguồn cho truy vấn nào
      # Không có `generated_at`: dấu thời gian làm kết quả không tất định giữa hai lần dựng cùng một
      # cấu hình (SR-U5-12) và C7 không khai trường này.
      - name: partial_reason
        type: string
        required: false
        description: >
          Lý do danh mục đang ở trạng thái "một phần"; bắt buộc khi choices rỗng,
          ví dụ "chưa có kết quả đề xuất cho truy vấn đang chọn"
      - name: pending_query_id
        type: string
        required: false
        description: Truy vấn đang chờ đề xuất; bắt buộc khi partial_reason có mặt
      - name: query_fields
        type: dict[string, list[string]]
        required: true
        description: >
          Ánh xạ truy vấn → trường cần, nạp từ tệp cấu hình (W1 bước 6) và mang theo trong danh mục
          để hàm đề xuất nguồn đọc được mà không cần tham số thứ hai. Khoá là ba `query_id` của FR2.1.
    constraints:
      - sources không bao giờ rỗng
      - Khi choices rỗng thì partial_reason và pending_query_id cùng có mặt; lần đề xuất đầu tiên ghi choices và XOÁ hai trường đó
      - Chỉ thêm trường khi mở rộng payload, không đổi tên hay bỏ trường đã có (change policy của C7)

  - name: SourceSelection
    description: Payload C3 — kết quả chọn nguồn cho một truy vấn, cấp cho U3
    attributes:
      - name: query_id
        type: string
        required: true
      - name: selected_sources
        type: list
        required: true
        description: >
          Đúng một phần tử khi thành công; mỗi phần tử có source_name, tables (lấy từ
          SourceProfile.tables) và reason
      - name: rejected_sources
        type: list
        required: true
        description: Mọi nguồn còn lại, mỗi phần tử có source_name và reason
      - name: missing_fields
        type: list[string]
        required: false
        description: Hợp các trường mà không nguồn nào phủ; chỉ có khi không chọn được nguồn
      - name: catalogue
        type: SourceCatalogue
        required: true
        description: >
          Bản C7 đã cập nhật sau lần đề xuất này, để U6 vẽ bảng nguồn mà không phải tự dựng lại.
          Trường này là phần cộng thêm của C3 (change policy của C3 cho phép cộng thêm trường).
    constraints:
      - selected_sources rỗng khi và chỉ khi trả lỗi NoSourceAvailableError
      - selected_sources không bao giờ có nhiều hơn một phần tử trong đợt này
      - Nguồn trong selected_sources không bao giờ là nguồn mô phỏng (BR5.11)
      - Chỉ thêm trường khi mở rộng payload (change policy của C3)

relationships:
  - from: SourceChoice
    to: SourceProfile
    cardinality: many-to-one
    direction: SourceChoice.source_name tham chiếu SourceProfile.source_name
  - from: SourceCatalogue
    to: SourceProfile
    cardinality: one-to-many
    direction: danh mục chứa toàn bộ hồ sơ
  - from: SourceCatalogue
    to: SourceChoice
    cardinality: one-to-many
    direction: danh mục chứa các quyết định đã tính
  - from: SourceSelection
    to: SourceChoice
    cardinality: one-to-many
    direction: kết quả của một truy vấn là tập con các dòng quyết định của truy vấn đó
```

## Bề mặt lỗi

| Payload | Lỗi | Khi nào | Ai bắt |
|---|---|---|---|
| C7 `SourceCatalogue` | `NoSourceAvailableError` | không nguồn nào đủ trường cho truy vấn đang chọn (BR5.6) | U6 |
| C7 `SourceCatalogue` | `SchemaError` | danh mục trường C2 ném lỗi, hoặc hồ sơ nguồn vi phạm BR5.1–BR5.3 | U6 |
| C7 `SourceCatalogue` | `ConfigurationError` | thiếu tệp cấu hình nguồn hoặc C2 ném lỗi cấu hình | U6 |
| C3 `SourceSelection` | `NoSourceAvailableError` | như trên; ngoại lệ mang **hai** thuộc tính: `missing_fields` (hợp các trường không nguồn nào phủ) và `catalogue` (bản C7 đã cập nhật) để U6 vẫn vẽ được bảng nguồn và nêu trường thiếu | U3, U6 |

U5 không bọc lại lỗi của C2: `SchemaError` và `ConfigurationError` từ C2 lan truyền nguyên vẹn qua U5, chỉ thêm ngữ cảnh ở thông điệp. U6 và U3 phải bắt cả ba lớp lỗi trên.

## Tóm tắt thực thể

| Thực thể | Vai trò | Khoá | Ghi chú |
|---|---|---|---|
| `SourceProfile` | Hồ sơ một nguồn ứng viên | `source_name` | Ba nguồn: `olist_csv`, `ibge_cache`, `partner_simulated`; `tables` khai trong cấu hình |
| `SourceChoice` | Quyết định chọn/loại cho một cặp (truy vấn, nguồn) | `(query_id, source_name)` | Tối đa một dòng được chọn cho mỗi truy vấn; lý do luôn bằng chữ |
| `SourceCatalogue` | Payload C7 cho giao diện | — | Không bao giờ rỗng; `choices` rỗng đi kèm `partial_reason` và `pending_query_id` |
| `SourceSelection` | Payload C3 cho U3 | `query_id` | Đúng một nguồn được chọn khi thành công, không bao giờ là nguồn mô phỏng |

## Ràng buộc xuyên thực thể

- **Một nguồn thắng một truy vấn.** `SourceSelection.selected_sources` chỉ có một phần tử trong đợt này (Q4 = A); mọi nguồn khác phải xuất hiện trong `rejected_sources`, không được biến mất.
- **Không có dữ liệu thì không thắng.** Nguồn `has_data = false` hoặc có `covered_fields` rỗng không thể được chọn, bất kể chi phí thấp đến đâu.
- **Mô phỏng thì không thắng.** `partner_simulated` được chấm điểm như mọi nguồn nhưng không bao giờ vào `selected_sources` (BR5.11).
- **Trường là đơn vị đo khả năng đáp ứng.** Một nguồn "đủ trường" khi và chỉ khi tập trường truy vấn cần là tập con của `covered_fields` và `has_data` là true.
- **Bảng là dữ kiện khai, không suy ra.** `tables` đến từ tệp cấu hình và đi thẳng vào C3; không có phép suy nào từ mã trường sang tên bảng.
