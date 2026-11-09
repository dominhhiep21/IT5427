# Entities — u3-query-rewriter

Nguồn: `inception/domain-design/components.md` (khối `QueryRewriter` và `SemanticLayer`), `inception/contract-design/contract-summary.md` (C1, C3, C4), `inception/requirements-analysis/requirements.md` (FR2.1–FR2.5, FR6.1–FR6.2), `inception/user-stories/stories.md` (US2.1–US2.3, US6.2), và câu trả lời trong `functional-design-questions.md` (Q1–Q6 đều chọn A).

```yaml
entities:
  - name: QueryTemplate
    description: Một truy vấn mẫu trên lược đồ trung gian, cùng mẫu SQL nguồn và ánh xạ trường
    attributes:
      - name: template_id
        type: string
        required: true
        unique: true
        allowed: [doanh_thu_theo_danh_muc, doanh_thu_theo_thang, ty_le_giao_tre_theo_bang]
        description: Phải trùng đúng ba query_id mà U5 đã khai trong config/integration-sources.yaml
      - name: title
        type: string
        required: true
        description: Nhãn hiển thị tiếng Việt, ví dụ "Doanh thu theo danh mục"
      - name: mediated_query_text
        type: string
        required: true
        description: Truy vấn viết trên lược đồ trung gian (ba thực thể), hiển thị cạnh SQL nguồn
      - name: source_sql
        type: string
        required: true
        description: >
          Mẫu SQL nguồn khai tay, có placeholder tham số "?"; không sinh động từ kế hoạch (Q2 = A).
          Chỉ dùng cột có thật trong dataset/; không nối chuỗi từ đầu vào người dùng.
      - name: plan
        type: list[RewriteStep]
        required: true
        description: Kế hoạch viết lại từng bước, thứ tự cố định, mô tả cùng mẫu SQL ở trên
      - name: kpi
        type: KpiDefinition
        required: true
        description: Định nghĩa KPI mà truy vấn này hiện thực
    constraints:
      - Bộ mẫu **mới** đúng ba mã, không thêm không bớt trong đợt này; vùng `don-theo-thang` của lát cắt vẫn tồn tại song song trong `result_region_ids` (FR2.1)
      - template_id trùng đúng ba query_id của U5; lệch mã là lỗi cấu hình, không phải lỗi dữ liệu

  - name: RewriteStep
    description: Một bước của kế hoạch viết lại — thực thể trung gian, bảng nguồn, điều kiện join
    attributes:
      - name: step
        type: integer
        required: true
        description: Số thứ tự từ 1, tăng dần, không nhảy cóc
      - name: mediated_entity
        type: string
        required: true
        allowed: [don_hang, mat_hang, san_pham]
      - name: source_table
        type: string
        required: true
        description: Một trong chín bảng nguồn của dự án
      - name: join_condition
        type: string
        required: false
        description: Điều kiện nối với bước trước, bằng chữ; rỗng ở bước đầu
    constraints:
      - Bước đầu tiên luôn là thực thể được truy vấn chính (don_hang cho cả ba mẫu)
      - Mỗi bước chỉ nêu một bảng; bảng lặp lại ở bước sau là lỗi thiết kế

  - name: KpiDefinition
    description: Định nghĩa KPI dùng chung cho dashboard và lớp truy vấn (FR6.1)
    attributes:
      - name: kpi_id
        type: string
        required: true
        unique: true
      - name: title
        type: string
        required: true
      - name: formula
        type: string
        required: true
        description: Công thức bằng chữ, ví dụ "tổng price + freight_value của đơn delivered"
      - name: revenue_definition
        type: string
        required: true
        description: >
          Bắt buộc với mọi KPI doanh thu: "price + freight_value của đơn delivered" (Q1 = A),
          khớp src/analytics hiện tại
      - name: unit
        type: string
        required: true
        allowed: [BRL, percent, count]
      - name: reference_value
        type: decimal
        required: false
        description: Giá trị tham chiếu đã ghi, dùng cho so sánh nhanh; không thay phép so trực tiếp
    constraints:
      - Khai một lần trong src/analytics/kpis.py; dashboard và lớp truy vấn đọc từ đó, không định nghĩa lại (Q6 = A)
      - KPI doanh thu thiếu revenue_definition là lỗi, không phải cảnh báo

  - name: SourceSelection
    description: Kết quả chọn nguồn nhận từ U5 qua C3 (đầu vào, không do U3 sở hữu)
    attributes:
      - name: query_id
        type: string
        required: true
      - name: selected_sources
        type: list
        required: true
        description: Đúng một phần tử khi thành công; mang source_name, tables, reason
      - name: rejected_sources
        type: list
        required: true
      - name: catalogue
        type: SourceCatalogue
        required: true
        description: Bản C7 đã cập nhật, U3 chỉ đọc
      - name: missing_fields
        type: list[string]
        required: false
        description: Chỉ có khi U5 không chọn được nguồn; đi kèm NoSourceAvailableError, U3 truyền nguyên vẹn
    constraints:
      - U3 không tự chọn nguồn và không sửa C3/C7
      - Khi U5 ném NoSourceAvailableError, U3 trả nguyên vẹn lỗi đó (Q4 = A)

  - name: QueryRunResult
    description: Payload C4 — kết quả một lần chạy truy vấn mẫu, cấp cho giao diện
    attributes:
      - name: plan_id
        type: string
        required: true
      - name: template_id
        type: string
        required: true
        references: QueryTemplate.template_id
      - name: template_title
        type: string
        required: true
      - name: mediated_query_text
        type: string
        required: true
        description: Hiển thị cạnh SQL nguồn (FR2.2)
      - name: rewrite_plan
        type: list[RewriteStep]
        required: true
      - name: source_sql
        type: string
        required: true
        description: SQL nguồn của lần chạy này, còn đọc lại được sau đó (FR2.4)
      - name: rows
        type: list
        required: true
      - name: row_count
        type: integer
        required: true
      - name: elapsed_ms
        type: integer
        required: true
        description: Thời gian chạy SQL trên DuckDB, đo quanh lời gọi (Q5 = A)
      - name: total_orders
        type: integer
        required: false
        description: Chỉ mẫu doanh thu; đếm đơn delivered phân biệt trong dải tham số
      - name: months
        type: list[string]
        required: false
        description: Chỉ mẫu doanh thu theo tháng; các tháng "YYYY-MM" có trong kết quả, tăng dần
      - name: partial
        type: list[string]
        required: false
        description: >
          Rỗng khi mọi nhóm đối chiếu được; khác rỗng khi một nhóm không đối chiếu được, mỗi phần
          tử là một câu nêu nhóm và lý do (ví dụ "nhóm SP-01: analytics không trả giá trị")
      - name: kpi_definitions
        type: list[KpiDefinition]
        required: true
      - name: kpi_comparison
        type: list[KpiComparison]
        required: true
    constraints:
      - row_count bằng đúng số phần tử của rows
      - elapsed_ms là số nguyên không âm

  - name: KpiComparison
    description: Kết quả đối chiếu **một nhóm** của một KPI giữa truy vấn viết lại và src/analytics
    attributes:
      - name: kpi_id
        type: string
        required: true
      - name: group_key
        type: string
        required: true
        description: >
          Khoá nhóm: tên danh mục, tháng "YYYY-MM", hoặc mã bang. Nhóm tổng dùng khoá "__all__"
          cho số dòng và tổng tiền.
      - name: expected_value
        type: decimal
        required: true
        description: Giá trị src/analytics trả về cho cùng nhóm và cùng bộ tham số
      - name: actual_value
        type: decimal
        required: true
      - name: delta
        type: decimal
        required: true
        description: expected_value − actual_value, giữ nguyên dấu để hiển thị
      - name: tolerance
        type: decimal
        required: true
        description: 0 cho tiền tệ và số dòng; 0 cho phần trăm sau khi làm tròn 2 chữ số hai bên
      - name: matches
        type: boolean
        required: true
    constraints:
      - matches đúng khi và chỉ khi |delta| <= tolerance
      - Một dòng `__all__` so số dòng và tổng tiền của cả kết quả
      - Sai lệch khác 0 với tiền tệ hoặc số dòng là không khớp, không được làm tròn cho khớp
      - Nhóm có ở một bên mà không có ở bên kia vẫn phải có dòng, với giá trị 0 ở bên thiếu và matches = false

relationships:
  - from: QueryTemplate
    to: RewriteStep
    cardinality: one-to-many
    direction: mẫu sở hữu kế hoạch từng bước
  - from: QueryTemplate
    to: KpiDefinition
    cardinality: one-to-one
    direction: mỗi mẫu hiện thực một KPI
  - from: QueryRunResult
    to: QueryTemplate
    cardinality: one-to-one
    direction: kết quả trỏ về mẫu đã chạy
  - from: QueryRunResult
    to: KpiComparison
    cardinality: one-to-many
    direction: mỗi lần chạy mang kết quả đối chiếu của (các) KPI liên quan
```

## Tóm tắt thực thể

| Thực thể | Vai trò | Khoá | Ghi chú |
|---|---|---|---|
| `QueryTemplate` | Truy vấn mẫu + mẫu SQL nguồn + kế hoạch | `template_id` | Đúng ba mẫu; `template_id` trùng `query_id` của U5 |
| `RewriteStep` | Một bước của kế hoạch viết lại | `step` | Thứ tự cố định, một bảng mỗi bước |
| `KpiDefinition` | Định nghĩa KPI dùng chung | `kpi_id` | Khai một lần ở `src/analytics/kpis.py` |
| `SourceSelection` | Đầu vào từ U5 (C3) | `query_id` | U3 chỉ đọc, không chọn nguồn |
| `QueryRunResult` | Payload C4 cho giao diện | — | Mang cả hai bản SQL và kết quả đối chiếu |
| `KpiComparison` | Đối chiếu một KPI | `kpi_id` | Dung sai 0 với tiền tệ và số dòng |

## Ràng buộc xuyên thực thể

- **Một định nghĩa doanh thu duy nhất**: mọi KPI doanh thu mang `revenue_definition` = `price + freight_value` của đơn `delivered` (Q1 = A). Không mẫu nào tự định nghĩa lại.
- **SQL là mẫu khai tay**: `source_sql` nằm trong `QueryTemplate`, `plan` chỉ mô tả nó (Q2 = A). Sinh động là thay đổi thiết kế, phải chốt lại.
- **Đối chiếu bằng số thật**: `KpiComparison.expected_value` lấy từ lời gọi `src/analytics` trong cùng lần chạy (Q3 = A), không lấy từ hằng ghi sẵn.
- **Lỗi của U5 không bị nuốt**: `SourceSelection` không có mặt nghĩa là truyền `NoSourceAvailableError` ra ngoài (Q4 = A).
