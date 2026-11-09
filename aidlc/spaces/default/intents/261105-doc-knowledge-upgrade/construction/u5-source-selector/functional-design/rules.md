# Business Rules — u5-source-selector

Nguồn: `inception/domain-design/components.md` (khối `SourceSelector`), `inception/user-stories/stories.md` (US4.1, US4.2), `inception/contract-design/contract-summary.md` (C2, C3, C7), `inception/requirements-analysis/requirements.md` (FR2.1, FR4.1–FR4.3, FR5.5, NFR5), và câu trả lời trong `functional-design-questions.md` (Q1–Q7 đều chọn A).

**Bản sửa sau review 1:** `tables` và `is_simulated` nay là dữ kiện khai trong cấu hình (BR5.1, R-01/R-06); chi phí và độ trễ của cả ba nguồn được chốt kèm kết quả kỳ vọng (BR5.2, BR5.4, R-04); nguồn mô phỏng không bao giờ được chọn (BR5.11, R-05); danh sách lý do loại có đủ nhánh độ trễ và thứ tự ưu tiên (BR5.5, R-07); nhánh "một phần" có chỗ chở dữ kiện (BR5.9, R-03).

Bối cảnh: đơn vị này phải làm cho **tiêu chí chọn nguồn trở nên tường minh** thay vì mặc định. Trước đợt này, hệ thống chỉ có một nguồn và không có khái niệm "chọn"; bảng nguồn trên giao diện là nơi người xem kiểm tra rằng một quyết định chọn nguồn thật sự có luật đứng sau.

```yaml
rules:
  - id: BR5.1
    statement: Hồ sơ nguồn được khai trong tệp cấu hình tĩnh, đủ tám dữ kiện mỗi nguồn
    category: policy
    applies_to: SourceProfile
    trigger: khi nạp bộ hồ sơ
    logic: >
      Bộ hồ sơ nằm trong một tệp cấu hình (ví dụ config/integration-sources.yaml). Mỗi nguồn khai
      đủ: source_name, label, tables, covered_fields, has_data, cost_level, latency_ms, is_simulated.
      is_simulated và tables đều khai tường minh, không suy ra từ tên nguồn hay từ covered_fields.
      Nạp một lần cho cả ứng dụng; không dò tệp nguồn, không gọi mạng.
    violation: ConfigurationError, kèm tên tệp và trường thiếu hoặc sai
    source: FR4.1

  - id: BR5.2
    statement: Bộ nguồn ứng viên gồm đúng ba nguồn với chi phí và độ trễ đã chốt
    category: constraint
    applies_to: SourceProfile
    trigger: khi nạp bộ hồ sơ
    logic: >
      Ba nguồn và dữ kiện cố định trong đợt này:
      (1) olist_csv — "Olist (CSV trong dataset/)", tables = [olist_orders_dataset,
      olist_customers_dataset, olist_order_items_dataset, olist_products_dataset],
      covered_fields = toàn bộ trường của ba thực thể trong lược đồ trung gian (gồm cả
      don_hang.bang_giao lấy từ olist_customers_dataset, cần cho truy vấn "tỷ lệ giao trễ theo
      bang" của FR2.1), has_data = true, cost_level = 3, latency_ms = 800, is_simulated = false;
      (2) ibge_cache — "Cache IBGE cục bộ", tables = [] và covered_fields = [] (bảng địa lý không
      nằm trong lược đồ trung gian), has_data = true, cost_level = 2, latency_ms = 200,
      is_simulated = false;
      (3) partner_simulated — "Nguồn đối tác (mô phỏng)", tables = [olist_orders_dataset,
      olist_customers_dataset], covered_fields = chỉ các trường của thực thể don_hang (gồm
      don_hang.bang_giao, mà bảng chứa nó là olist_customers_dataset — nên bảng đó phải có trong
      tables), has_data = true, cost_level = 1, latency_ms = 50, is_simulated = true.
      Thêm nguồn thứ tư hoặc đổi các con số này là thay đổi phạm vi, phải chốt lại.
    violation: SchemaError khi source_name nằm ngoài tập ba nguồn đã chốt
    source: FR4.1; giả định A3; Q1 = A, Q2 = A

  - id: BR5.3
    statement: Khả năng đáp ứng của một nguồn là tập trường C2 mà nó phủ, mô tả bằng câu tiếng Việt
    category: calculation
    applies_to: SourceProfile
    trigger: khi dựng bảng nguồn
    logic: >
      covered_fields chứa các mã "entity.field" có trong MediatedFieldCatalogue (C2). coverage là
      câu ngắn tiếng Việt dẫn xuất từ tập đó, ví dụ "Đủ ba bảng: đơn hàng, mặt hàng, sản phẩm" hoặc
      "Chỉ có trường đơn hàng". Chuỗi này do máy dựng, không gõ tay trong tệp cấu hình.
      Phép kiểm của U5 đối chiếu mã trường với C2, và đối chiếu **tên** bảng trong tables với danh
      sách bảng nguồn của dự án (SOURCE_TABLES — chín tên tệp đã bỏ `.csv`). U5 KHÔNG kiểm chéo trường ↔ bảng: C2 không mang ánh
      xạ thực thể → bảng, và C1 (nơi có ánh xạ đó) không nằm trong hợp đồng của U5. tables là dữ
      kiện khai theo BR5.1, chỉ được kiểm tên.
    violation: >
      SchemaError khi covered_fields chứa mã trường không có trong C2, hoặc khi tables chứa tên bảng
      không nằm trong SOURCE_TABLES
    source: FR4.1; Q7 = A

  - id: BR5.4
    statement: Thứ tự xếp hạng nguồn là đủ trường, rồi chi phí, rồi độ trễ, rồi tên nguồn
    category: calculation
    applies_to: SourceChoice
    trigger: khi đề xuất nguồn cho một truy vấn
    logic: >
      Với mỗi nguồn: đủ trường = tập trường truy vấn cần là tập con của covered_fields VÀ
      has_data là true. Sắp xếp các nguồn đủ trường theo cost_level tăng dần, rồi latency_ms tăng
      dần, rồi source_name theo bảng chữ cái. Nguồn thắng là phần tử đầu tiên CÒN LẠI sau khi áp
      BR5.11 (loại nguồn mô phỏng). Tên nguồn ở bước cuối bảo đảm kết quả không phụ thuộc thứ tự
      khai báo.
      Kết quả kỳ vọng trong đợt này, với cả ba truy vấn mẫu của FR2.1: olist_csv được chọn;
      ibge_cache bị loại vì không phủ trường nào; partner_simulated bị loại theo BR5.11.
    violation: không có — luật xếp hạng
    source: FR4.1, FR2.1; Q3 = A

  - id: BR5.5
    statement: Mỗi truy vấn chọn đúng một nguồn; mọi nguồn còn lại được ghi vào danh sách bị loại
    category: policy
    applies_to: SourceSelection
    trigger: sau khi xếp hạng
    logic: >
      selected_sources có đúng một phần tử mang source_name, tables (nguyên từ SourceProfile.tables)
      và reason. rejected_sources chứa mọi nguồn khác, mỗi dòng một reason theo thứ tự ưu tiên xét:
      (1) is_simulated = true → "nguồn mô phỏng, chỉ dùng để so sánh";
      (2) has_data = false → "không có dữ liệu";
      (3) thiếu trường → "không đủ trường: <danh sách trường thiếu>";
      (4) đủ trường nhưng chi phí cao hơn → "chi phí cao hơn <nguồn thắng>";
      (5) cùng chi phí nhưng độ trễ cao hơn → "cùng chi phí nhưng độ trễ cao hơn <nguồn thắng>";
      (6) cùng chi phí và độ trễ → "cùng chi phí và độ trễ, xếp sau theo tên".
      Một nguồn thoả nhiều nhánh nhận lý do của nhánh đầu tiên theo thứ tự trên. Không nguồn nào
      được biến mất khỏi kết quả.
    violation: không có — luật phân loại
    source: FR4.2; C3; Q4 = A

  - id: BR5.6
    statement: Khi không nguồn nào đủ trường, không chọn nguồn nào và nêu rõ cái gì thiếu
    category: validation
    applies_to: SourceSelection
    trigger: khi mọi nguồn đều bị loại
    logic: >
      selected_sources rỗng; trả NoSourceAvailableError. Lỗi và payload mang missing_fields = hợp
      các trường mà không nguồn nào phủ, và với mỗi nguồn gần nhất ghi nguồn đó thiếu trường gì.
      Giao diện hiển thị thông báo này thay cho bảng kết quả; không hiển thị số 0 thay cho dữ liệu
      thiếu.
    violation: NoSourceAvailableError; lượt chạy không chọn nguồn nào
    source: FR4.2; AC4.2.2; Q5 = A

  - id: BR5.7
    statement: Nguồn mô phỏng không phát sinh bất kỳ lệnh gọi mạng nào
    category: policy
    applies_to: SourceProfile
    trigger: trong suốt vòng đời ứng dụng
    logic: >
      has_data và latency_ms là dữ kiện khai báo, không phải kết quả của một lần gọi thử. Mã của
      đơn vị này không import thư viện mạng và không mở kết nối tới bất kỳ địa chỉ nào. Nhãn của
      nguồn mô phỏng kèm ghi chú "nguồn mô phỏng" để người xem không nhầm với dữ liệu thật.
    violation: lỗi kiểm thử tĩnh; một lệnh gọi mạng là lỗi, không phải cảnh báo
    source: FR4.3; AC4.1.3; NFR6

  - id: BR5.8
    statement: Lý do chọn hoặc loại luôn là câu chữ tiếng Việt, không dựa vào màu sắc
    category: policy
    applies_to: SourceChoice
    trigger: khi dựng mỗi dòng quyết định
    logic: >
      Mọi dòng SourceChoice có reason khác rỗng và đọc được như một câu. Màu chỉ là trang trí thêm;
      nếu bỏ toàn bộ màu thì bảng vẫn trả lời được "vì sao nguồn này được chọn".
    violation: SchemaError khi reason rỗng
    source: FR4.2; AC4.1.2

  - id: BR5.9
    statement: Danh mục nguồn chưa có kết quả đề xuất thì báo "một phần", không báo rỗng
    category: constraint
    applies_to: SourceCatalogue
    trigger: khi giao diện đọc danh mục trước lần đề xuất đầu tiên
    logic: >
      Khi chưa có truy vấn nào được đề xuất: sources vẫn đầy đủ, choices rỗng, partial_reason =
      "chưa có kết quả đề xuất cho truy vấn đang chọn", pending_query_id = truy vấn cần đề xuất.
      Lần đề xuất đầu tiên ghi choices và xoá cả hai trường đó; vì vậy bất biến là "choices rỗng
      thì hai trường kia có mặt", không phải "khi và chỉ khi".
      Giao diện hiển thị bảng nguồn, không hiển thị trạng thái rỗng.
    violation: không có — luật hiển thị
    source: FR5.5 (nhánh "một phần"); C7 partial

  - id: BR5.10
    statement: Mọi mở rộng payload chỉ được cộng thêm trường
    category: policy
    applies_to: SourceCatalogue, SourceSelection
    trigger: khi thêm dữ kiện mới cho giao diện hoặc cho U3
    logic: >
      Trường đã có giữ nguyên tên và kiểu; trường mới là tuỳ chọn hoặc có giá trị mặc định. Không
      đổi tên source_name đã công bố, không bỏ trường đã có, vì U3 và U6 đọc cùng payload.
    violation: lỗi kiểm tra hợp đồng ở đơn vị tiêu thụ
    source: C3, C7 change policy

  - id: BR5.11
    statement: Nguồn mô phỏng không bao giờ được chọn cho một truy vấn thật
    category: policy
    applies_to: SourceChoice, SourceSelection
    trigger: sau khi xếp hạng, trước khi trả kết quả
    logic: >
      Mọi nguồn có is_simulated = true bị loại khỏi danh sách ứng viên thắng, kể cả khi nó có
      chi phí thấp nhất và đủ trường; lý do ghi trong rejected_sources là "nguồn mô phỏng, chỉ dùng
      để so sánh". Nguồn mô phỏng vẫn xuất hiện trong bảng nguồn (C7) để người xem thấy nó được
      đánh giá và bị loại có lý do. Hệ quả: selected_sources chỉ có thể là nguồn thật, nên U3 sinh
      SQL trên nguồn thật và FR2.5 còn so khớp được với src/analytics.
    violation: SchemaError nếu selected_sources chứa nguồn mô phỏng
    source: FR2.5, FR4.3; C3
```

## Tóm tắt luật

| Mã | Nhóm | Luật | Nguồn |
|---|---|---|---|
| BR5.1 | Chính sách | Hồ sơ nguồn trong tệp cấu hình tĩnh, đủ tám dữ kiện | FR4.1 |
| BR5.2 | Ràng buộc | Đúng ba nguồn, chi phí và độ trễ đã chốt | FR4.1, A3 |
| BR5.3 | Tính toán | Khả năng đáp ứng = tập trường C2; trường phải thuộc bảng đã khai | FR4.1, Q7 |
| BR5.4 | Tính toán | Xếp hạng: đủ trường → chi phí → độ trễ → tên; kết quả kỳ vọng là `olist_csv` | FR4.1, FR2.1 |
| BR5.5 | Chính sách | Đúng một nguồn được chọn; sáu nhánh lý do loại theo thứ tự ưu tiên | FR4.2, C3 |
| BR5.6 | Kiểm tra | Không nguồn nào đủ trường → `NoSourceAvailableError` | FR4.2, AC4.2.2 |
| BR5.7 | Chính sách | Nguồn mô phỏng không gọi mạng | FR4.3, AC4.1.3 |
| BR5.8 | Chính sách | Lý do luôn bằng chữ; bỏ màu vẫn hiểu được | FR4.2, AC4.1.2 |
| BR5.9 | Ràng buộc | Chưa đề xuất → "một phần" với lý do và truy vấn đang chờ | FR5.5, C7 |
| BR5.10 | Chính sách | Mở rộng payload chỉ cộng thêm trường | C3, C7 |
| BR5.11 | Chính sách | Nguồn mô phỏng không bao giờ được chọn | FR2.5, FR4.3 |

## Luật cố ý không có mã nguồn yêu cầu

- Không có. Cả mười một luật đều truy được về một `FR`, một điều khoản hợp đồng, hoặc một câu trả lời đã ghi.
