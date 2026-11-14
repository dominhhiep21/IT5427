# Rules — u1-statistics

Nguồn: `../../../inception/requirements-analysis/requirements.md`, `../../../inception/contract-design/contract-summary.md` (C1, C2 — phiên bản 2), `functional-design-questions.md`, và `entities.md`.

`category` chỉ dùng năm giá trị: `validation`, `authorization`, `constraint`, `calculation`, `policy`. `source` chỉ trỏ tới mã FR/NFR; quyết định đến từ câu hỏi thiết kế nằm ở trường `decided_by`.

```yaml
rules:
  - id: BR1.1
    category: calculation
    statement: Tỉ lệ giao trễ tính trên đơn đã giao, kèm khoảng tin cậy Wilson
    applies_to: ProportionResult của StatsBlock.late_rate
    trigger: Tầng stats bắt đầu, sau khi đọc dữ liệu
    logic: "IF is_delivered = true THEN total = COUNT(*); successes = SUM(is_late); rate = successes / total; ci = Wilson(rate, total, z(1 - alpha/2))"
    violation: "total = 0 thì dừng cả tầng: không có đơn đã giao thì không có báo cáo để ghi"
    source: FR1.1

  - id: BR1.2
    category: calculation
    statement: So sánh bang có tỉ lệ trễ cao nhất với bang thấp nhất trong các bang đủ 100 đơn đã giao, và ghi số đơn của các bang bị loại
    applies_to: StatsBlock.comparisons và trường excluded của ComparisonResult
    trigger: Sau BR1.1
    logic: "eligible = bang có COUNT(delivered) >= 100; excluded = SUM(COUNT(delivered)) của các bang còn lại; IF |eligible| >= 2 THEN chọn đúng một cặp max-rate / min-rate, difference = rate_max - rate_min, z gộp, p hai phía, CI Newcombe, significant = p < alpha; ELSE comparisons = []"
    violation: "Ít hơn hai bang đủ điều kiện thì comparisons rỗng và thêm một SkipEntry với test = state_comparison"
    source: FR1.2

  - id: BR1.3
    category: calculation
    statement: Tương quan Pearson giữa giá hàng và phí vận chuyển, khoảng tin cậy Fisher
    applies_to: StatsBlock.correlation
    trigger: Sau BR1.1
    logic: "IF price và freight_value đều khác null THEN n = COUNT(*); r = pearson(price, freight); z = atanh(r); se = 1 / sqrt(n - 3); CI = tanh(z ± z(1 - alpha/2) * se)"
    violation: "n < 4 thì correlation = null và thêm SkipEntry với test = correlation; cận dưới là 4 vì se = 1/sqrt(n-3) không xác định ở n = 3"
    source: FR1.3

  - id: BR1.4
    category: validation
    statement: Kiểm định độc lập giữa vùng giao hàng và tình trạng trễ, chỉ chạy khi mọi ô kỳ vọng đạt tối thiểu 5
    applies_to: StatsBlock.group_test
    trigger: Sau BR1.1
    logic: "nguồn: v_fact_orders nối v_dim_customer theo customer_id, chỉ giữ is_delivered = true; hai biến là dim_customer.region và fact_orders.is_late; dựng bảng dự phòng vùng × trễ; min_expected = MIN(expected); IF min_expected >= 5 THEN chi-square với dof = (số vùng - 1) * (2 - 1); ELSE group_test = null"
    violation: "min_expected < 5 thì group_test = null và thêm SkipEntry với test = group_test, reason nêu ô kỳ vọng nhỏ nhất"
    source: FR1.4

  - id: BR1.5
    category: calculation
    statement: Phân rã mùa vụ chuỗi doanh thu tháng, chu kỳ 12, tháng không có đơn được điền 0
    applies_to: StatsBlock.seasonal
    trigger: Sau BR1.1
    logic: "nguồn: v_agg_sales_daily, cột revenue (tổng item_total) — mart này đã lọc is_delivered và đã mã hoá price + freight_value; gộp theo tháng của date_key (date_key là ngày đặt hàng, không phải ngày giao); dựng trục tháng liên tục từ tháng của đơn delivered sớm nhất tới tháng của đơn delivered muộn nhất, điền 0 cho tháng thiếu; IF độ dài trục >= 24 THEN phân rã cộng tính cổ điển chu kỳ 12 với trung bình động giữa có cửa sổ thu hẹp ở hai đầu; revenue_definition = REVENUE_DEFINITION; method = 'classical_additive_12'"
    violation: "Dưới 24 tháng trên trục liên tục thì seasonal = null và thêm SkipEntry với test = seasonal"
    note: "Bốn tháng cuối 2016 là tháng thưa, nhưng vẫn nằm trên trục vì bỏ chúng thì chỉ còn 22 tháng và không đủ một chu kỳ 12; sự thưa thớt hiện ra ở chính cột observed, nên người đọc thấy được tháng nào ít đơn thay vì bị giấu đi"
    source: FR1.5

  - id: BR1.6
    category: constraint
    statement: Kiểm định không đủ điều kiện thì trả null và ghi một SkipEntry, các kiểm định khác vẫn chạy
    applies_to: StatsBlock.skipped và các trường kết quả tuỳ chọn
    trigger: Mọi nhánh violation của BR1.2, BR1.3, BR1.4, BR1.5
    logic: "IF điều kiện không đạt THEN result = null; skipped.append(SkipEntry(test, reason)); tiếp tục kiểm định kế tiếp"
    violation: "Không được ném ngoại lệ ra ngoài tầng chỉ vì một kiểm định không đủ điều kiện"
    source: FR1.4

  - id: BR1.7
    category: calculation
    statement: alpha và confidence lấy từ một hằng số duy nhất, không truyền rời
    applies_to: StatsBlock.alpha và StatsBlock.confidence
    trigger: Dựng StatsBlock
    logic: "alpha = ALPHA (0.05); confidence = 1 - alpha (0.95)"
    violation: "Thiếu một trong hai thì không ghi báo cáo"
    source: FR1.1

  - id: BR1.8
    category: calculation
    statement: Số thực được làm tròn khi ghi — tỉ lệ, p-value và khoảng tin cậy 4 chữ số; hệ số tương quan 3 chữ số
    applies_to: Mọi trường số thực của StatsBlock
    trigger: Trước khi ghi tệp
    logic: "round(rate, 4); round(p_value, 4); round(ci_*, 4); round(r, 3)"
    violation: "Không làm tròn thì không ghi"
    source: FR3.1
    decided_by: Q5 (Functional Design)

  - id: BR1.9
    category: validation
    statement: Hàm đọc trả đúng bốn trạng thái rong, day-du, mot-phan, loi theo C2
    applies_to: ReportView
    trigger: Bất kỳ lệnh đọc báo cáo nào
    logic: "IF tệp không tồn tại THEN rong; ELSE IF không parse được JSON THEN loi với message nêu đường dẫn; ELSE IF version != REPORT_VERSION THEN loi (xem BR1.10); ELSE IF thiếu trường bắt buộc hoặc sai kiểu THEN loi với message nêu tên trường; ELSE IF stats hoặc model là null THEN mot-phan với missing liệt kê khối thiếu; ELSE day-du"
    violation: "Không ném ngoại lệ ra ngoài biên đọc; mọi hỏng hóc thành một ReportView"
    note: "Thứ tự kiểm là cố định: tồn tại → parse → version → cấu trúc. Nhờ vậy một tệp phiên bản cũ luôn nhận thông điệp phiên bản, không bị báo nhầm thành thiếu trường"
    source: FR3.1

  - id: BR1.10
    category: validation
    statement: Tệp báo cáo phiên bản khác REPORT_VERSION bị coi là không dùng được
    applies_to: ReportView.status và ReportView.message
    trigger: Sau khi đọc được JSON
    logic: "IF version != 2 THEN status = loi; message nêu phiên bản đọc được và việc phải chạy lại tầng stats"
    violation: "Không cố đọc tiếp một tệp sai phiên bản"
    source: FR3.1

  - id: BR1.11
    category: policy
    statement: Báo cáo được ghi qua AtomicWriter, rồi đọc lại để kiểm cấu trúc trước khi thay tệp cũ
    applies_to: write_report
    trigger: Sau khi dựng xong AnalysisReport
    logic: "ghi tệp tạm; đọc lại: parse JSON, kiểm version đọc được và không cùng null cả stats lẫn model; IF một bước kiểm hỏng THEN xoá tệp tạm và ném ở biên CLI; ELSE os.replace(tệp tạm, đích)"
    violation: "Không để lại tệp dở hay tệp tạm, và không thay tệp cũ bằng một tệp không đọc được"
    note: "Trước khi dựng báo cáo mới, tầng stats đọc lại tệp cũ để giữ khối model của U2. Nếu tệp cũ không đọc được thì khối model coi như vắng mặt, báo cáo ghi ra thành mot-phan và có một dòng cảnh báo trong nhật ký; không dừng cả tầng, vì bước kiểm định vẫn có kết quả dùng được và U2 chạy lại sẽ dựng lại khối đó"
    source: FR3.2
```

## Tóm tắt quy tắc

| Mã | Loại | Một dòng |
|---|---|---|
| BR1.1 | calculation | Tỉ lệ trễ trên đơn đã giao, khoảng Wilson |
| BR1.2 | calculation | Bang cao nhất so với bang thấp nhất, ngưỡng 100 đơn, ghi `excluded` |
| BR1.3 | calculation | Tương quan giá–phí, khoảng Fisher |
| BR1.4 | validation | Vùng × trễ, chi-square khi mọi ô kỳ vọng đạt 5 |
| BR1.5 | calculation | Doanh thu từ `agg_sales_daily`, chu kỳ 12, tối thiểu 24 tháng, điền 0 |
| BR1.6 | constraint | Không đủ điều kiện → `null` + `SkipEntry` |
| BR1.7 | calculation | `alpha` và `confidence` từ một hằng số |
| BR1.8 | calculation | Làm tròn 4 chữ số, hệ số tương quan 3 chữ số |
| BR1.9 | validation | Bốn trạng thái đọc, gồm `rong` |
| BR1.10 | validation | Sai phiên bản → `loi` |
| BR1.11 | policy | `AtomicWriter`, đọc lại kiểm cấu trúc trước khi thay tệp |

## Kiểm tra ràng buộc

| Mã | Kiểm bằng | Ở đâu |
|---|---|---|
| BR1.1 | So khớp tỉ lệ và khoảng tin cậy với phép tính độc lập | Test đơn vị có dữ liệu mẫu; test `slow` trên dữ liệu thật |
| BR1.2 | Bang dưới 100 đơn không xuất hiện; `excluded` bằng tổng đơn của chúng; đúng một phần tử trong `comparisons` | Test đơn vị |
| BR1.3 | `n` bằng số dòng hợp lệ; `n = 3` thì trả `null`; khoảng tin cậy chứa `r` | Test đơn vị |
| BR1.4 | Bảng có ô kỳ vọng dưới 5 thì `group_test` là `null` và có `SkipEntry`; `dof` bằng `số vùng - 1` | Test đơn vị |
| BR1.5 | Chuỗi tháng liên tục, có 0 ở tháng thiếu; dưới 24 tháng thì `null`; tổng doanh thu khớp `agg_sales_daily` | Test đơn vị; test `slow` đối chiếu baseline |
| BR1.6 | `skipped` có đúng một dòng cho mỗi kiểm định bị bỏ, không trùng tên | Test đơn vị |
| BR1.7 | `confidence` luôn bằng `1 - alpha` | Test đơn vị |
| BR1.8 | Mọi số thực trong tệp có đúng số chữ số đã chốt | Test đơn vị trên tệp ghi ra |
| BR1.9 | Năm tệp mẫu: không tồn tại, hỏng, thiếu một khối, đủ hai khối, sai kiểu trường | Test đơn vị |
| BR1.10 | Tệp `version = 1` trả `loi` và thông điệp nêu việc chạy lại | Test đơn vị |
| BR1.11 | Tệp tạm bị làm hỏng sau khi ghi thì tệp cũ còn nguyên và có ngoại lệ | Test đơn vị với thư mục tạm |

## Ghi chú về thang đo

Tỉ lệ trong báo cáo là phân số 0–1, khác `late_rate_pct` 0–100 của KPI hiện có. Tab nhân 100 khi hiển thị phần trăm. Ghi rõ để không trộn hai thang.

## Ghi chú về nguồn dữ liệu

Bốn nguồn, cùng đọc qua `AnalyticsService` trên các view của mart:

| Nguồn | Dùng cho | Vì sao |
|---|---|---|
| `v_fact_orders` | trễ, ngày đặt, ngày giao | đã có `is_delivered`, `is_late`, `order_purchase_timestamp` |
| `v_dim_customer` | bang, vùng | ghép theo `customer_id`, quan hệ 1:1 |
| `v_fact_order_items` | giá hàng, phí vận chuyển | grain dòng hàng, đúng cho tương quan |
| `v_agg_sales_daily` | doanh thu tháng cho BR1.5 | đã gộp sẵn theo ngày và đã lọc `is_delivered`, nên không phải join lại grain thô |
