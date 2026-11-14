# Business Rules — u2-features-and-models

Nguồn: `entities.md`, `../../../inception/requirements-analysis/requirements.md` (FR1.2, FR1.4, FR2.1–FR2.8, FR3.1, FR3.3, NFR5), `../../../inception/contract-design/contract-summary.md` (C1, C2, C2b, C3), `../../../inception/domain-design/decisions.md` (ADR-001, ADR-003, ADR-004, ADR-008).

```yaml
feature_contract:
  version: 1
  owner: u2-features-and-models
  module: ModelModule (src/analytics/model.py)
  constant: FEATURES
  feature_count: 14
  order_is_part_of_contract: true
  validation: >
    validate_features(features = FEATURES) từ chối khi tập tên khác, khi có tên lặp, khi THỨ TỰ khác
    `features` dưới đây, hoặc khi có cột trong `forbidden`. build_feature_frame trả đúng 14 cột theo
    đúng thứ tự này — thứ tự là một phần của hợp đồng vì `FittedModel.feature_names` gắn với nó.
  change_rule: >
    Danh sách này là hợp đồng của C3; thêm/bớt/đổi tên một cột là thay đổi phá vỡ, phải sửa đồng thời
    model.py (FEATURES + FORBIDDEN_COLUMNS + validate_features), TRAINING_FRAME_SQL, test đơn vị,
    test end-to-end và README.md — như `project.md` `## Mandated` yêu cầu.
  features:
    - item_count
    - item_total
    - item_price_max
    - payment_type
    - payment_installments
    - customer_state
    - customer_region
    - purchase_month
    - purchase_weekday
    - has_items
    - has_payment
    - seller_state
    - handling_days
    - approval_days
  groups:
    categorical:
      encoding: >
        one-hot; phạm trù khớp trên tập huấn luyện; null → 'unknown'; giá trị lạ ở tập kiểm tra rơi vào
        'unknown', không tạo cột mới.
      columns:
        - { name: payment_type, derivation: "MAX(CASE WHEN payment_sequential = 1 THEN payment_type END) theo order_id" }
        - { name: customer_state, derivation: "v_dim_customer.state" }
        - { name: customer_region, derivation: "v_dim_customer.region" }
        - { name: purchase_month, derivation: "v_dim_date.month của date_key, dạng chuỗi ('1'..'12')" }
        - { name: purchase_weekday, derivation: "v_dim_date.weekday của date_key, dạng chuỗi ('0' = thứ Hai)" }
        - { name: seller_state, new: true, derivation: "v_fact_order_items.seller_state (lấy từ dim_sellers, không suy từ địa chỉ khách)" }
    numeric:
      encoding: float64 rồi StandardScaler khớp trên tập huấn luyện
      missing: "0.0 — giữ nguyên quy ước hiện có của NUMERIC_FEATURES (model.py:174-176); không suy diễn, không nội suy"
      columns:
        - { name: item_count, unit: món, grain: đơn, derivation: "COUNT(*) trên các dòng hàng của đơn — số món của đơn, lặp trên mọi dòng của đơn" }
        - { name: item_total, unit: BRL, grain: đơn, derivation: "SUM(f.item_total) theo order_id — tổng giá + phí của đơn, lặp trên mọi dòng" }
        - { name: item_price_max, unit: BRL, grain: đơn, derivation: "MAX(f.price) theo order_id — giá cao nhất trong đơn, lặp trên mọi dòng" }
        - { name: payment_installments, unit: kỳ, grain: đơn, derivation: "MAX(p.payment_installments) theo order_id" }
        - { name: handling_days, type: integer, unit: ngày dương lịch, grain: dòng hàng, new: true, derivation: "số ngày từ NGÀY của order_approved_at đến NGÀY của order_delivered_carrier_date (duyệt → bàn giao); null khi thiếu một trong hai mốc, dòng vẫn giữ" }
        - { name: approval_days, type: integer, unit: ngày dương lịch, grain: dòng hàng, new: true, derivation: "số ngày từ date_key đến NGÀY của order_approved_at (đặt → duyệt); null khi order_approved_at null, dòng vẫn giữ" }
      resolution_note: >
        Mart không có cột `order_purchase_timestamp` — `v_fact_orders` chỉ có `date_key` (ngày, đã mất
        phần giờ) — nên `approval_days` đo từ `date_key` đến ngày duyệt. Cả hai đặc trưng là số nguyên
        ngày dương lịch. Đánh đổi đã nhận: chúng có sai số dưới một ngày; muốn chính xác đến giờ thì phải
        thêm cột mốc mua vào mart, việc đó thuộc một đơn vị khác và KHÔNG làm ở đây. Biểu mẫu C3 hỏi đúng
        hai con số ngày đó, nên train và serve cùng độ phân giải.
    flags:
      encoding: bool → float64; null → false
      columns: [has_items, has_payment]
  order_level_aggregates:
    columns: [item_count, item_total, item_price_max]
    statement: >
      Ba cột là tổng hợp của ĐƠN, lặp trên mọi dòng hàng của đơn đó — không phải số đo của riêng dòng.
      Giữ nguyên tên và nghĩa như TRAINING_FRAME_SQL hiện tại (service.py:38-46), chỉ đổi grain của
      khung chứa chúng.
    rationale: >
      Chúng không phải rò rỉ vì mọi đầu vào của chúng đều biết được NGAY LÚC ĐẶT HÀNG — số món, giá
      món, phí của đơn — và không phụ thuộc kết quả giao hàng. Cùng ba con số này còn tính được ở lúc
      chấm điểm từ hai giá trị nhập `item_price` và `item_count`, nên train và serve nói cùng một nghĩa.
  forbidden:
    - order_delivered_customer_date
    - order_delivered_carrier_date
    - order_approved_at
    - delivery_days
    - is_late
    - late_days
    - review_score
    - review_comment_title
    - review_comment_message
    - is_delivered
    - has_review
  forbidden_note: >
    `order_approved_at` là mục THÊM của đợt này; `order_delivered_carrier_date` đã nằm trong danh sách
    từ trước. Hai cột mốc thô chỉ được dùng để lọc quần thể (FR2.1) và dẫn xuất thành `handling_days` /
    `approval_days`. Mốc đặt hàng KHÔNG có cột thô trong mart — chỉ có `date_key` ở độ phân giải ngày,
    và `date_key` nằm trong `not_features`: nó là cột chia tập, không phải đặc trưng.
  not_features: [order_id, order_item_id, date_key, is_late, is_delivered]
  serve_inputs:
    required: [seller_state, customer_state, order_date, item_price, handling_days, approval_days, item_count, payment_type, installments, has_items, has_payment]
    mapping:
      - "purchase_month ← str(order_date.month); purchase_weekday ← str(order_date.weekday()) — cùng không gian số-dạng-chuỗi với lúc huấn luyện, không cần đọc dim_date"
      - "customer_region ← ánh xạ bang → vùng đã lưu trong FittedModel.state_regions; bang lạ → 'unknown'"
      - "item_price_max ← item_price; item_total ← item_price × item_count; item_count ← item_count (một món có giá trị 1)"
      - "payment_installments ← installments; seller_state/customer_state/payment_type/hai cờ lấy nguyên từ đầu vào"
      - "handling_days/approval_days ← hai ô số ngày của biểu mẫu, đúng nghĩa duyệt→bàn giao và đặt→duyệt, cùng độ phân giải ngày với lúc huấn luyện"
      - "item_total ở lúc chấm điểm không có phí vận chuyển vì FR3.1 không có ô đó — sai lệch này được ghi nhận, không che"

rules:
  - id: BR2.1
    statement: Quần thể là các dòng hàng của đơn đã giao VÀ có carrier date; khung và bốn bộ đếm đến từ CÙNG một truy vấn, trả về cặp (TrainingFrame, CohortCounts).
    category: calculation
    applies_to: [TrainingFrame, CohortCounts]
    trigger: dựng khung huấn luyện
    logic: >
      IF một dòng thuộc đơn không delivered THEN loại. IF đơn thiếu order_delivered_carrier_date THEN
      loại và ĐẾM vào excluded_missing_carrier — phép đếm này chạy trên tập đơn TRƯỚC khi lọc carrier,
      nên nó phải nằm trong chính câu truy vấn đó. IF truy vấn trả một DataFrame kèm thuộc tính ẩn THEN
      từ chối: hình dạng trả về là cặp (TrainingFrame, CohortCounts), hai thứ rời nhau. Không có truy vấn
      thứ hai, không lọc rồi đếm lại ở Python.
    violation: >
      ModelError nếu cohort_rows/cohort_orders/late_rows/excluded_missing_carrier khác 110195/96476/8713/2,
      hoặc nếu len(frame) khác cohort_rows.
    source: FR1.2

  - id: BR2.2
    statement: Chia tập theo order_id tại SPLIT_DATE; giao hai tập order_id phải rỗng; tổng số dòng lấy từ CohortCounts.
    category: constraint
    applies_to: [SplitPlan]
    trigger: chia tập
    logic: >
      IF chọn DÒNG HÀNG ngẫu nhiên thay vì gán cả đơn theo order_id THEN từ chối — cùng một đơn rơi cả
      hai phía và AUC bị thổi lên. Chia theo date_key không phải chỗ sinh rò rỉ (ngày đặt là thuộc tính
      của đơn, mọi dòng của một đơn cùng một phía); chỗ sinh rò rỉ là chia ở grain dòng. THEN giao hai
      tập order_id rỗng và một phía rỗng là lỗi. split_summary kiểm train_n + test_n == cohort_rows của
      CohortCounts — KHÔNG dùng EXPECTED_DELIVERED = 96.478 nữa.
    violation: "ModelError nêu số đơn giao nhau, cỡ tập rỗng, hoặc tổng lệch cohort_rows"
    source: FR2.2

  - id: BR2.3
    statement: Đặc trưng gồm đúng 14 cột — 11 cột cũ giữ nguyên tên và nghĩa, cộng seller_state, handling_days, approval_days — đúng thứ tự của feature_contract.
    category: constraint
    applies_to: [TrainingFrame]
    trigger: dựng ma trận đặc trưng
    logic: >
      IF ma trận không có đúng 14 tên của feature_contract.features THEN từ chối. IF thứ tự khác THEN
      từ chối — FittedModel.feature_names gắn với thứ tự đó. IF một cột trong feature_contract.forbidden
      có mặt THEN từ chối; hai cột mốc thời gian thô không bao giờ được là đặc trưng, kể cả ở dạng ngày
      thô. IF một cột trong not_features lọt vào ma trận THEN từ chối. validate_features kiểm cả ba phép
      trên (tập tên, thứ tự, danh sách cấm).
    violation: "ModelError từ validate_features; test đơn vị canh đủ 14 tên, đúng thứ tự, và danh sách cấm"
    source: FR2.1

  - id: BR2.4
    statement: Hai mô hình dùng cùng đặc trưng, cùng mốc, cùng quần thể, cùng random_state.
    category: policy
    applies_to: [FittedModel]
    trigger: huấn luyện
    logic: >
      IF cây được huấn luyện trên tập khác, mốc khác, hay seed khác với logistic THEN từ chối.
      Mô hình triển khai là logistic; cây chỉ để ghi auc_tree.
    violation: "ModelError; chạy hai lần phải cho cùng auc_tree"
    source: FR2.3

  - id: BR2.5
    statement: Ngưỡng chọn trên lưới THRESHOLD_GRID theo F1 trên tập kiểm tra, rồi ghi vào model.threshold.
    category: calculation
    applies_to: [ModelBlock]
    trigger: chọn ngưỡng
    logic: >
      IF ngưỡng sau làm tròn không nằm trong (0,1) THEN từ chối. Ngưỡng là nguồn DUY NHẤT cho
      khối dự đoán; không consumer nào được tự chọn ngưỡng khác.
    violation: "ModelError"
    source: FR2.5

  - id: BR2.6
    statement: Baseline đo lại trong cùng khung; beats_baseline và auc_below_target tính trên giá trị đã làm tròn.
    category: calculation
    applies_to: [BaselineMeasurement, ModelBlock]
    trigger: dựng ModelBlock
    logic: >
      IF baseline_auc được lấy từ số cũ (0,5133 ở grain đơn) hoặc đo ở khung khác THEN từ chối.
      THEN beats_baseline = (auc > baseline_auc), và auc_below_target = (auc < AUC_TARGET), cả hai
      trên giá trị ĐÃ làm tròn 4 chữ số để tệp không mâu thuẫn với chính nó.
    violation: "ModelError nếu hai cờ không khớp phép so; test slow đỏ nếu auc <= baseline_auc"
    source: FR2.7

  - id: BR2.7
    statement: analysis.json là phiên bản 3, khối model 11 trường, counts 9 khoá; tệp v2 đọc ra trạng thái loi.
    category: validation
    applies_to: [ModelBlock]
    trigger: ghi hoặc đọc báo cáo
    logic: >
      IF version != 3 THEN trả trạng thái loi kèm thông điệp, KHÔNG ném. IF thiếu một trong bốn
      trường mới hoặc một trong năm khoá counts mới THEN cũng là loi — không được lấp bằng mặc định.
    violation: "trạng thái loi; dashboard hiện lý do và đường dẫn tệp"
    source: FR2.5

  - id: BR2.8
    statement: Mô hình lưu bằng pickle kèm metadata, nạp lại đúng trạng thái tiền xử lý đã khớp.
    category: constraint
    applies_to: [FittedModel, ModelArtifact]
    trigger: lưu hoặc nạp mô hình
    logic: >
      IF lúc chấm điểm phải khớp lại phạm trù hay scaler trên dữ liệu mới THEN từ chối. Vắng tệp
      là trạng thái bình thường trả None; tệp hỏng là ModelError.
    violation: "ModelError; giao diện hiện trạng thái 'mô hình chưa sẵn'"
    source: FR2.4

  - id: BR2.9
    statement: assemble_report là entry point duy nhất dựng AnalysisReport và giữ khối model cũ.
    category: policy
    applies_to: [ModelBlock]
    trigger: tầng stats ghi báo cáo
    logic: >
      IF bất kỳ chỗ nào khác dựng AnalysisReport THEN từ chối trong review. collect_stats,
      build_analysis_report và train_model không còn là entry point và không tự dựng AnalyticsService.
    violation: "vi phạm ADR-008; test đơn vị khẳng định chỉ một đường dựng báo cáo"
    source: FR2.5

  - id: BR2.10
    statement: Ba đóng góp log-odds gộp theo TRƯỜNG, không theo cột one-hot.
    category: calculation
    applies_to: [PredictionContribution]
    trigger: giải thích một dự đoán
    logic: >
      IF hai dòng cùng một trường (ví dụ customer_state=SP và customer_state=RJ) THEN gộp thành
      một dòng trước khi chọn ba lớn nhất. Nhãn ghi rõ "log-odds, không phải tổng".
    violation: "test đơn vị khẳng định không có hai dòng cùng trường"
    source: FR3.3

  - id: BR2.11
    statement: score_item chấm một dòng hàng từ trạng thái đã lưu, dựng đủ 14 đặc trưng từ 11 giá trị nhập, và tất định.
    category: calculation
    applies_to: [PredictionOutcome, PredictionContribution]
    trigger: giao diện gọi chấm điểm (C3)
    logic: >
      IF hàm khớp lại phạm trù hay scaler trên dữ liệu lúc dự đoán THEN từ chối — chỉ dùng trạng thái
      của FittedModel nạp qua C2b (categories, scaler_means/scaler_scales, feature_names, state_regions).
      THEN kiểm 11 khoá nhập của feature_contract.serve_inputs; thiếu hoặc sai miền THEN raise ModelError
      nêu TÊN TRƯỜNG. THEN dựng đúng 14 cột theo feature_contract.serve_inputs.mapping — dẫn xuất
      purchase_month/purchase_weekday từ order_date, customer_region từ state_regions, item_price_max và
      item_total từ item_price, item_count từ đầu vào — rồi chấm bằng trạng thái đã lưu và trả
      PredictionOutcome (probability, verdict so với threshold đọc từ model.threshold, contributions gộp
      theo trường của BR2.10). IF hàm dùng random, đọc đồng hồ, hay phụ thuộc thứ tự gọi THEN từ chối:
      cùng FittedModel + cùng item ⇒ cùng probability tuyệt đối.
    violation: "ModelError nêu tên trường; test đơn vị khẳng định hai lần gọi cho cùng xác suất"
    source: FR3.3, FR3.4

  - id: BR2.12
    statement: MODEL_AUC_FLOOR và hàm so mốc sàn thuộc U2, đặt trong model.py cạnh AUC_TARGET.
    category: calculation
    applies_to: [ModelBlock]
    trigger: kiểm mốc sàn
    logic: >
      MODEL_AUC_FLOOR khởi đầu 0,55 đặt cạnh AUC_TARGET trong model.py. Hàm thuần
      beats_floor(auc, baseline_auc, floor=MODEL_AUC_FLOOR) -> bool trả auc >= max(floor, baseline_auc),
      so trên hai giá trị ĐÃ làm tròn 4 chữ số đọc từ báo cáo (cùng chỗ BR2.6 đã làm tròn), để mốc sàn
      không bao giờ thấp hơn baseline và hai cổng không thể cho hai kết luận trái nhau. Đây là sàn chống
      thoái hoá, KHÔNG phải giá trị kỳ vọng của chất lượng mô hình: nó được nâng khi baseline vượt nó.
      U3 chỉ import hằng số và gọi hàm, không sửa model.py.
    violation: "ModelError nếu floor không nằm trong (0,1); test đơn vị canh cả nhánh đỏ và nhánh xanh"
    source: NFR5
```

## Tóm tắt

| ID | Nhóm | Một dòng |
|---|---|---|
| `BR2.1` | calculation | Quần thể dòng hàng, một truy vấn, bốn bộ đếm, trả cặp `(TrainingFrame, CohortCounts)` |
| `BR2.2` | constraint | Chia theo `order_id`, giao rỗng, tổng lấy từ `CohortCounts` |
| `BR2.3` | constraint | Đúng 14 đặc trưng, đúng thứ tự; `FORBIDDEN_COLUMNS` bị từ chối |
| `BR2.4` | policy | Hai mô hình cùng đặc trưng/mốc/quần thể/seed |
| `BR2.5` | calculation | Ngưỡng trên lưới, ghi vào báo cáo, là nguồn duy nhất |
| `BR2.6` | calculation | Baseline đo lại; hai cờ tính trên giá trị đã làm tròn |
| `BR2.7` | validation | v3, 11 trường, 9 khoá; thiếu ⇒ `loi` |
| `BR2.8` | constraint | `pickle` + metadata; không khớp lại lúc chấm điểm |
| `BR2.9` | policy | `assemble_report` là đường duy nhất |
| `BR2.10` | calculation | Ba đóng góp gộp theo trường |
| `BR2.11` | calculation | `score_item`: 11 giá trị nhập → 14 đặc trưng, trạng thái đã lưu, tất định |
| `BR2.12` | calculation | `MODEL_AUC_FLOOR` + `beats_floor` thuộc U2; U3 chỉ import và gọi |

**Hợp đồng đặc trưng đọc thế nào.** `feature_contract` ở đầu tệp này là nguồn sự thật duy nhất cho danh sách đặc trưng: 14 cột, chia ba nhóm mã hoá, kèm cách dẫn xuất từng cột, danh sách cấm, và ánh xạ 11 giá trị nhập của C3 sang 14 cột. `entities.md` mô tả cùng các cột đó ở dạng thuộc tính; nếu hai tệp lệch nhau thì `feature_contract` đúng và `entities.md` phải sửa.

**Ba cột tổng hợp theo đơn, không phải rò rỉ.** `item_count`, `item_total`, `item_price_max` là số món, tổng giá + phí và giá cao nhất của **đơn**, lặp trên mọi dòng hàng của đơn. Chúng chỉ dùng đầu vào biết được lúc đặt hàng, không phụ thuộc kết quả giao hàng, và cùng ba con số đó vẫn tính được ở lúc chấm điểm từ `item_price` + `item_count` — nên đổi grain khung không đổi nghĩa của chúng.

**Hai đặc trưng thời gian ở độ phân giải ngày, và cái giá của nó.** Mart không có `order_purchase_timestamp` — `v_fact_orders` chỉ có `date_key`, đã mất phần giờ — nên `approval_days` đo từ `date_key` đến **ngày** duyệt, còn `handling_days` đo giữa **ngày** duyệt và **ngày** bàn giao; cả hai là số nguyên ngày dương lịch. Đánh đổi đã nhận: sai số dưới một ngày. Muốn chính xác đến giờ phải thêm cột mốc mua vào mart — việc đó thuộc đơn vị khác và không làm ở đây.

**Điều không có ở đây:** không luật nào đặt một giá trị AUC cụ thể làm kỳ vọng (`project.md` cấm). Chất lượng mô hình được **ghi ra và hiển thị**; ràng buộc duy nhất là mốc sàn `max(MODEL_AUC_FLOOR, baseline_auc)`, và hằng số `MODEL_AUC_FLOOR` cùng hàm `beats_floor` **thuộc U2** (BR2.12) — U3 chỉ `import` hằng số và gọi hàm, không sửa `model.py`.
