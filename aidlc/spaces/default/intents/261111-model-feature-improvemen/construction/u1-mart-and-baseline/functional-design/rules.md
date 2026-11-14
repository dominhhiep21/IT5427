# Business Rules — u1-mart-and-baseline

Nguồn: `entities.md`, `../../../inception/requirements-analysis/requirements.md` (FR1.1, FR1.3, NFR4), `../../../inception/contract-design/contract-summary.md` (C1), `../../../inception/user-stories/stories.md` (US1.1), mã thật `src/integrate/{facts,dimensions,aggregates,validate,reconcile}.py`.

```yaml
rules:
  - id: BR1.1
    statement: Thêm cột vào mart không được đổi số dòng, không đổi grain, không đổi lọc.
    category: constraint
    applies_to: [MartOrder, MartOrderItem]
    trigger: mỗi lần dựng lại mart
    logic: >
      IF số dòng của bất kỳ bảng mart nào, hoặc số dòng của bất kỳ view nào, khác giá trị
      đã chốt trong hợp đồng số dòng THEN dừng trước khi ghi mart.
    violation: "QualityGateError từ StarSchemaValidator.enforce (validate.py:147); pipeline dừng, mart cũ còn nguyên"
    source: FR1.1

  - id: BR1.2
    statement: seller_state chỉ được lấy từ dim_seller theo seller_id.
    category: constraint
    applies_to: [MartOrderItem]
    trigger: dựng cột seller_state
    logic: >
      IF cột được điền bằng nguồn nào khác dim_seller (địa chỉ khách, geolocation của mã
      bưu chính người bán, hay hằng số) THEN coi là vi phạm. IF seller_id không có bản ghi
      dim_seller THEN để null; không bịa giá trị và không làm mất dòng.
    violation: "sai ngữ nghĩa, không phát hiện được bằng phép đếm dòng — test đơn vị của đơn vị này canh"
    source: FR1.1

  - id: BR1.3
    statement: Hai cột mốc thời gian ở nguyên dạng trong mart và bị cấm làm đặc trưng trực tiếp.
    category: policy
    applies_to: [MartOrder]
    trigger: dựng đặc trưng huấn luyện (U2)
    logic: >
      IF một mốc thời gian thô đi vào ma trận đặc trưng THEN từ chối. Chỉ giá trị dẫn xuất
      dạng số ngày mới được phép.
    violation: "ModelError từ validate_features của U2 (FORBIDDEN_COLUMNS)"
    source: FR1.3
    enforced_by: u2-features-and-models

  - id: BR1.4
    statement: Hàm đo baseline là hàm thuần, grain-neutral, chia trên date_key với đúng SPLIT_DATE.
    category: calculation
    applies_to: [MartOrder]
    trigger: gọi measure_state_baseline
    logic: >
      IF cut_date khác SPLIT_DATE của mô-đun THEN ném ModelError — người gọi không được tự
      chọn mốc chia, vì baseline và mô hình phải chia ở cùng một mốc. ELSE chia hai tập trên
      date_key, huấn luyện baseline MỘT đặc trưng trên tập huấn luyện, chấm điểm trên tập
      kiểm tra, trả AUC. Hàm không tự lọc dòng, không đọc tệp, không mở kết nối, không giữ
      trạng thái giữa các lần gọi.
    violation: "ModelError nêu cut_date nhận được và SPLIT_DATE đang áp"
    source: FR1.3

  - id: BR1.5
    statement: Baseline phải đo trên tập kiểm tra không rỗng và có đủ hai lớp nhãn.
    category: validation
    applies_to: [MartOrder]
    trigger: gọi measure_state_baseline
    logic: >
      IF tập kiểm tra rỗng THEN ném ModelError. IF tập kiểm tra chỉ có một lớp nhãn THEN ném
      ModelError, vì AUC không xác định. Không trả 0,0 và không trả null thay cho lỗi.
    violation: "ModelError nêu cỡ tập kiểm tra và số lớp nhãn"
    source: FR1.3

  - id: BR1.6
    statement: Ba cột mới phải giữ đúng kiểu dữ liệu và tính tuỳ chọn đã khai.
    category: validation
    applies_to: [MartOrder, MartOrderItem, MartColumnContract]
    trigger: dựng mart
    logic: >
      IF hai cột mốc không phải kiểu mốc thời gian THEN từ chối. IF seller_state không phải
      chuỗi hai chữ hoa khi khác null THEN từ chối. IF cột bị đặt NOT NULL trên dữ liệu thật
      (nơi có 160 và 1.783 giá trị thiếu) THEN từ chối, vì điều đó làm mất dòng.
    violation: "QualityGateError ở tầng mart; test đơn vị canh ba điều kiện"
    source: FR1.1

  - id: BR1.7
    statement: Cột mới của người bán phải tên seller_state, không được tên state.
    category: constraint
    applies_to: [MartOrderItem]
    trigger: đặt tên cột khi nối dim_seller
    logic: >
      IF cột mới mang tên state THEN từ chối, vì dim_customer đã có cột state và
      agg_sales_daily nối hai bảng, nên tên trùng sinh state_x/state_y và làm hỏng tổng hợp.
      THEN đổi tên state → seller_state ngay tại chỗ nối.
    violation: "hỏng agg_sales_daily; test đơn vị khẳng định tên cột sau khi dựng mart"
    source: FR1.1
```

## Tóm tắt luật

| ID | Nhóm | Một dòng |
|---|---|---|
| `BR1.1` | constraint | Ba cột thêm vào **không** làm đổi một dòng nào của 9 bảng và 11 view |
| `BR1.2` | constraint | `seller_state` chỉ đến từ `dim_seller`; thiếu thì null, không bịa |
| `BR1.3` | policy | Mốc thời gian thô bị cấm làm đặc trưng; chỉ số ngày dẫn xuất được phép (U2 cưỡng chế) |
| `BR1.4` | calculation | Baseline là hàm thuần, grain-neutral, chia trên `date_key` với `SPLIT_DATE` |
| `BR1.5` | validation | Tập kiểm tra rỗng hoặc một lớp ⇒ `ModelError` |
| `BR1.6` | validation | Kiểu dữ liệu và tính nullable của ba cột là hợp đồng |
| `BR1.7` | constraint | Tên cột phải là `seller_state`; `state` sẽ phá `agg_sales_daily` |

**Vì sao bảy luật.** Đơn vị này không có nghiệp vụ — nó là hạ tầng dữ liệu. Bảy luật trên là toàn bộ những gì có thể sai **âm thầm**: đếm dòng sai, nguồn cột sai, tên cột phá tổng hợp, chia tập sai mốc, tập kiểm tra suy biến, kiểu dữ liệu sai. Phần còn lại là quy ước mã, kiểm bằng `ruff` và test.

**Ba chỗ tôi cố ý ghi khác bản trước, vì bản trước sai với mã:**

- `BR1.1`/`BR1.6` nêu `QualityGateError`, không phải `SchemaError` — `StarSchemaValidator.enforce` ném `QualityGateError` (`validate.py:147`).
- `BR1.2` nói `dim_seller` (số ít) và cột nguồn tên `state`, đúng như `dimensions.py:47-63`; bản trước ghi `dim_sellers` và `seller_state` như thể đã có.
- `BR1.4` bắt hàm **kiểm** `cut_date` thay vì tin người gọi. Bản trước để `same_split_as_model` do người gọi khai — một lời hứa không kiểm được.

**Điều không có ở đây, và vì sao:** không luật nào về `cohort_rows = 110.195` hay `excluded_missing_carrier`. Bốn bộ đếm đó do U2 sinh; đặt luật ở đây sẽ tạo nguồn thứ hai cho cùng bốn con số — đúng thứ hợp đồng C1 đã loại.
