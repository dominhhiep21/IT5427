# Business Rules — u3-query-rewriter

Nguồn: `inception/domain-design/components.md` (`QueryRewriter`, `SemanticLayer`), `inception/requirements-analysis/requirements.md` (FR2.1–FR2.5, FR6.1–FR6.2, NFR1), `inception/user-stories/stories.md` (US2.1–US2.3, US6.2), `inception/contract-design/contract-summary.md` (C1, C3, C4), câu trả lời trong `functional-design-questions.md` (Q1–Q6 đều chọn A), và hiện trạng `src/integration/query.py`, `src/analytics/`, `config/integration-tab.yaml`.

**Bản sửa sau review 1:** xử lý mẫu `don-theo-thang` đang có trong mã (R-01); định nghĩa tham số/bộ lọc dùng chung (R-02); đối chiếu KPI theo từng nhóm thay vì một cặp số (R-03); chốt ngữ nghĩa "lệch" và ghi rõ quyết định đảo với C4 (R-04); bổ sung bốn trường vào lược đồ trung gian để truy vấn viết được (R-05); sửa máy trạng thái và kênh `partial` (R-06, R-07); sửa số bước của mẫu giao trễ và quan hệ với `query_fields` (R-08); tách sổ KPI khỏi kiểu payload để không vòng import (R-09).

```yaml
rules:
  - id: BR3.1
    statement: Tab "Tích hợp" có đúng ba mẫu riêng; mẫu cũ don-theo-thang giữ nguyên cho báo cáo cũ
    category: constraint
    applies_to: QueryTemplate
    trigger: khi nạp bộ mẫu
    logic: >
      Bộ mẫu của tab "Tích hợp" có **ba mẫu mới**: doanh_thu_theo_danh_muc, doanh_thu_theo_thang,
      ty_le_giao_tre_theo_bang — trùng ba query_id của U5. Mẫu don-theo-thang là mẫu của lát cắt
      mỏng U1, **không thuộc FR2.1**, và C9 nay khai nó bằng khoá riêng `result_region_ids`.
      **U3 cộng thêm** ba vùng mới vào `result_region_ids`, cạnh `don-theo-thang`; **không** thay
      thế, **không** xoá vùng đang có, **không** chạm `card_ids` (change-policy của C9 chỉ cho thêm).
      Trong cùng thay đổi: cập nhật `config/integration-tab.yaml`, `src/integration/tab.py` (dựng
      thêm vùng cho ba mẫu), và các test đang ghim hình dạng tab. Sau thay đổi, tab có **bốn vùng**.
    violation: ConfigurationError nêu mã thiếu, thừa hoặc lạ
    source: FR2.1, FR5.6

  - id: BR3.2
    statement: Doanh thu là price + freight_value của đơn delivered
    category: calculation
    applies_to: KpiDefinition, QueryTemplate
    trigger: khi dựng định nghĩa KPI và khi viết mẫu SQL
    logic: >
      Mọi KPI doanh thu dùng price + freight_value của các dòng hàng thuộc đơn có
      order_status = 'delivered'; loại trừ trạng thái khác một cách tường minh. Định nghĩa ghi trong
      KpiDefinition.revenue_definition và hiển thị kèm KPI. Để truy vấn trung gian viết được trên
      lược đồ, `mat_hang` mang thêm trường `gia_van_chuyen` (từ order_items.freight_value) — xem
      BR3.11.
    violation: KPI doanh thu thiếu định nghĩa doanh thu là lỗi khởi tạo
    source: FR2.5, FR6.2; Q1 = A

  - id: BR3.3
    statement: Mỗi mẫu có kế hoạch viết lại từng bước, thứ tự cố định
    category: constraint
    applies_to: RewriteStep
    trigger: khi dựng QueryTemplate
    logic: >
      Bước 1 luôn là don_hang (bảng olist_orders_dataset). Số bước của ba mẫu:
      doanh_thu_theo_danh_muc 3 bước (don_hang → mat_hang/olist_order_items_dataset →
      san_pham/olist_products_dataset); doanh_thu_theo_thang 2 bước (don_hang → mat_hang);
      ty_le_giao_tre_theo_bang 2 bước (don_hang/olist_orders_dataset → olist_customers_dataset cho
      bang_giao, vì don_hang.bang_giao lấy từ bảng khách). Mỗi bước nêu một bảng và điều kiện join
      với bước trước; bước 1 rỗng điều kiện.
    violation: ConfigurationError nêu mẫu và bước sai
    source: FR2.3

  - id: BR3.4
    statement: SQL nguồn là mẫu khai tay có placeholder, không sinh động
    category: policy
    applies_to: QueryTemplate
    trigger: khi dựng mẫu và khi chạy
    logic: >
      source_sql là chuỗi khai trong mã, có placeholder "?" cho tham số. Kế hoạch từng bước mô tả
      cùng mẫu đó, không sinh ra nó. Sinh SQL động từ kế hoạch là thay đổi thiết kế, phải chốt lại.
    violation: không có — luật thiết kế
    source: FR2.2; Q2 = A

  - id: BR3.5
    statement: SQL nguồn chỉ tham chiếu bảng và cột có thật, tham số hoá mọi giá trị
    category: validation
    applies_to: QueryTemplate
    trigger: khi dựng mẫu và trước khi chạy
    logic: >
      Mọi bảng trong SQL thuộc chín bảng nguồn; mọi cột có trong tiêu đề tệp nguồn tương ứng.
      Giá trị truyền vào dùng placeholder "?", không nối chuỗi từ đầu vào người dùng. Tên cột của
      ba mẫu khớp những trường mà U5 đã khai trong query_fields của config/integration-sources.yaml
      — sau khi tập trường đó được bổ sung bốn trường ở BR3.11.
    violation: SchemaError nêu bảng hoặc cột không có thật
    source: FR2.2

  - id: BR3.6
    statement: Đối chiếu từng nhóm kết quả với src/analytics, dung sai 0 cho tiền và số dòng
    category: calculation
    applies_to: KpiComparison
    trigger: sau khi truy vấn trả về
    logic: >
      Cả ba mẫu trả nhiều dòng nhóm (theo danh mục, theo tháng, theo bang), nên đối chiếu theo từng
      nhóm: mỗi nhóm có group_key, expected_value (từ src/analytics), actual_value, delta,
      tolerance và matches. Dung sai theo đơn vị: **0,01 cho giá trị tiền tệ** (cùng dung sai
      src/integrate/reconcile.py đang dùng, vì src/analytics làm tròn 2 chữ số), **0 cho số dòng**,
      và **0,01 cho tỷ lệ phần trăm** sau khi cả hai bên làm tròn 2 chữ số. Dòng `__all__` so số
      dòng và tổng tiền của cả kết quả. matches đúng khi và chỉ khi |delta| <= tolerance; không nới
      dung sai để cho khớp.
      Nếu bất kỳ nhóm nào matches = false, lần chạy ném `KpiMismatchError` đúng như C4 và
      components.md đã chốt — **không** đảo ngữ nghĩa của hợp đồng. Lỗi mang danh sách nhóm lệch và
      delta của từng nhóm để giao diện nêu tên truy vấn và mức lệch (AC2.1.3).
    violation: KpiMismatchError nêu truy vấn, nhóm và delta
    source: FR2.5; Q3 = A

  - id: BR3.7
    statement: Không có nguồn thì không chạy truy vấn
    category: policy
    applies_to: QueryRunResult
    trigger: trước khi sinh SQL
    logic: >
      U3 yêu cầu C3 từ U5. Nếu U5 ném NoSourceAvailableError, U3 truyền nguyên vẹn lỗi đó ra ngoài
      (cùng lớp, cùng missing_fields, cùng catalogue) và không chạy truy vấn nào. Không có đường
      chạy trên nguồn mặc định, không tự chọn nguồn.
    violation: NoSourceAvailableError lan truyền
    source: FR2.2; Q4 = A

  - id: BR3.8
    statement: Thời gian chạy đo quanh lời gọi SQL, trả trong C4
    category: calculation
    applies_to: QueryRunResult
    trigger: khi chạy truy vấn
    logic: >
      elapsed_ms = mili giây của riêng lời gọi DuckDB, đo bằng time.perf_counter quanh lời gọi,
      không tính chọn nguồn hay dựng kế hoạch. Số nguyên không âm. Ngưỡng NFR1 là 2000 ms; vượt
      ngưỡng là ghi nhận, không phải lỗi chặn.
    violation: không có
    source: NFR1; Q5 = A

  - id: BR3.9
    statement: Sổ KPI là dữ liệu trong src/analytics/kpis.py; kiểu payload ở lại models.py
    category: policy
    applies_to: KpiDefinition
    trigger: khi khai và khi đọc
    logic: >
      Sổ KPI (mã, nhãn, công thức, định nghĩa doanh thu, đơn vị, giá trị tham chiếu) nằm duy nhất
      trong **src/common/kpis.py** — mô-đun trung lập ở gốc chuỗi phụ thuộc, không import
      src/analytics hay src/integration. Dataclass `KpiDefinition` trong src/integration/models.py
      chỉ là hình chiếu của sổ đó cho payload C4; src/analytics và src/integration cùng đọc
      src/common/kpis.py, không tầng nào import tầng kia để lấy định nghĩa. Chiều phụ thuộc
      `common → ingest → clean → quality → integrate → analytics → dashboard` của team.md vì vậy
      được giữ nguyên.
    violation: trùng kpi_id hoặc import vòng
    source: FR6.1; Q6 = A

  - id: BR3.10
    statement: Một lần chạy mang cả hai bản SQL, kế hoạch và kết quả đối chiếu
    category: constraint
    applies_to: QueryRunResult
    trigger: khi trả kết quả
    logic: >
      QueryRunResult luôn có mediated_query_text, source_sql và rewrite_plan để hiển thị hai bản
      cạnh nhau và đọc lại SQL của lần chạy gần nhất. row_count = len(rows). Kết quả lần chạy trước
      bị ghi đè nhưng đường đọc "SQL lần chạy gần nhất" vẫn trả bản mới nhất.
      `total_orders` chỉ điền cho hai mẫu doanh thu (số đơn delivered phân biệt trong dải tham số);
      `months` chỉ điền cho mẫu doanh thu theo tháng (các tháng "YYYY-MM" có trong kết quả, tăng dần);
      cả hai để None ở mẫu giao trễ. Ba trường này được khai trong C4 (cộng thêm) cùng thay đổi này.
      `partial` rỗng khi mọi nhóm đối chiếu được; khác rỗng khi một nhóm không đối chiếu được, mang
      lý do bằng chữ (ví dụ "nhóm SP-01: analytics không trả giá trị"). Lỗi làm hỏng cả lần chạy
      (analytics không chạy được) thì ném ngoại lệ, không dùng `partial`.
    violation: lỗi kiểm tra kiểu ở nơi dựng kết quả
    source: FR2.2, FR2.3, FR2.4

  - id: BR3.11
    statement: Bốn trường được bổ sung vào lược đồ trung gian để ba mẫu viết được
    category: constraint
    applies_to: QueryTemplate
    trigger: trước khi sinh mã
    logic: >
      Ba mẫu cần dữ kiện mà lược đồ ba thực thể hiện chưa mang: giá vận chuyển (order_items.
      freight_value), ngày giao thực tế (orders.order_delivered_customer_date), ngày giao dự kiến
      (orders.order_estimated_delivery_date), bang giao (customers.customer_state) và tên danh mục
      sản phẩm (products.product_category_name). Bốn trường sau đã có trong lược đồ và **đều
      `loaded: true`** — tệp C8 hiện có 7 trường `don_hang` với mọi trường đã bật cờ, nên không
      còn thao tác bật cờ nào.
      Thay đổi chỉ cộng thêm, theo chính sách C8: thêm `mat_hang.gia_van_chuyen`, nếu chưa có. Phép
      sửa này thuộc đơn vị U3 vì không ai khác cần các trường đó, và phải cập nhật lược đồ, tập
      trường của U5 (`config/integration-sources.yaml`) và test của U2 trong cùng một thay đổi.
    violation: SchemaError khi mẫu SQL dùng trường không có trong lược đồ
    source: FR2.5, FR3.x (giao trễ)

  - id: BR3.12
    statement: Tham số và bộ lọc dùng chung cho SQL và cho lời gọi src/analytics
    category: calculation
    applies_to: QueryRunResult
    trigger: khi chạy và khi đối chiếu
    logic: >
      Bộ tham số của một lần chạy gồm: khoảng ngày đặt (`ngay_tu`, `ngay_den`, có thể rỗng nghĩa
      là toàn bộ dải), và `trang_thai` cố định 'delivered' cho hai mẫu doanh thu, rỗng cho mẫu giao
      trễ. Đúng bộ tham số đó được truyền vào cả SQL (qua "?") và lời gọi src/analytics (qua bộ lọc
      của nó). Không có tham số nào chỉ áp cho một bên.
    violation: SchemaError khi tham số sai kiểu hoặc ngày không hợp lệ
    source: FR2.5
```

## Tóm tắt luật

| Mã | Nhóm | Luật | Nguồn |
|---|---|---|---|
| BR3.1 | Ràng buộc | Ba mẫu riêng cho tab mới; `don-theo-thang` của báo cáo cũ giữ nguyên | FR2.1, FR5.6 |
| BR3.2 | Tính toán | Doanh thu = `price + freight_value` của đơn `delivered` | FR2.5, FR6.2 |
| BR3.3 | Ràng buộc | Kế hoạch từng bước; 3 / 2 / 2 bước | FR2.3 |
| BR3.4 | Chính sách | SQL là mẫu khai tay có placeholder | FR2.2 |
| BR3.5 | Kiểm tra | Bảng/cột có thật; tham số hoá | FR2.2 |
| BR3.6 | Tính toán | Đối chiếu từng nhóm; 0,01 tiền, 0 số dòng, 0,01 phần trăm; lệch → `KpiMismatchError` | FR2.5 |
| BR3.7 | Chính sách | Không có nguồn thì không chạy; lỗi lan nguyên vẹn | FR2.2 |
| BR3.8 | Tính toán | `elapsed_ms` đo quanh lời gọi SQL | NFR1 |
| BR3.9 | Chính sách | Sổ KPI ở `kpis.py`, kiểu payload ở `models.py` | FR6.1 |
| BR3.10 | Ràng buộc | Kết quả mang hai bản SQL + đối chiếu + `partial` | FR2.2–FR2.4 |
| BR3.11 | Ràng buộc | Bổ sung bốn trường vào lược đồ trung gian | FR2.5 |
| BR3.12 | Tính toán | Một bộ tham số cho cả SQL và analytics | FR2.5 |

## Luật cố ý không có mã nguồn yêu cầu

- Không có. Cả mười hai luật đều truy được về một `FR`, một `NFR`, hoặc một câu trả lời đã ghi.
