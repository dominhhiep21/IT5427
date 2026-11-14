# Entities — u2-features-and-models

Đơn vị: `u2-features-and-models` (kind `library`). Nguồn: `../../../inception/units-generation/unit-of-work.md` (định nghĩa U2), `../../../inception/domain-design/components.md`, `../../../inception/contract-design/contract-summary.md` (C1, C2, C2b, C3), `../../../inception/requirements-analysis/requirements.md`.

```yaml
entities:
  - name: TrainingFrame
    description: >
      Một dòng cho mỗi cặp đơn × món trong quần thể đã giao và có carrier date. Là đầu vào
      duy nhất của tầng mô hình.
    attributes:
      - { name: order_id, type: identifier, required: true, role: internal, note: "khoá chia tập; không bao giờ tách một đơn sang hai phía" }
      - { name: order_item_id, type: identifier, required: true, role: internal }
      - { name: date_key, type: date, required: true, role: internal, note: "ngày đặt; cột chia tập, không phải đặc trưng" }
      - { name: is_late, type: boolean, required: true, role: internal, note: "nhãn, kế thừa từ đơn chứa dòng hàng" }
      - { name: item_count, type: integer, required: true, role: feature, note: "SỐ MÓN CỦA ĐƠN (COUNT(*) theo order_id), không phải hằng số 1 trên mỗi dòng" }
      - { name: item_total, type: decimal, required: true, role: feature, note: "tổng giá + phí của ĐƠN (SUM theo order_id), lặp trên mọi dòng của đơn" }
      - { name: item_price_max, type: decimal, required: true, role: feature, note: "giá CAO NHẤT trong đơn, lặp trên mọi dòng của đơn — không phải giá của riêng dòng đó" }
      - { name: payment_type, type: string, required: true, role: feature, note: "lấy dòng payment_sequential = 1" }
      - { name: payment_installments, type: integer, required: true, role: feature, note: "MAX theo order_id" }
      - { name: customer_state, type: string, required: true, role: feature }
      - { name: customer_region, type: string, required: false, nullable: true, role: feature, note: "suy từ bang qua dim_customer lúc huấn luyện" }
      - { name: purchase_month, type: string, required: true, role: feature, note: "dim_date.month (số 1–12) dạng chuỗi, đúng như ma trận đã huấn luyện" }
      - { name: purchase_weekday, type: string, required: true, role: feature, note: "dim_date.weekday (0 = thứ Hai) dạng chuỗi" }
      - { name: has_items, type: boolean, required: true, role: feature }
      - { name: has_payment, type: boolean, required: true, role: feature }
      - { name: seller_state, type: string, required: false, nullable: true, role: feature, note: "từ dim_sellers qua v_fact_order_items; null → 'unknown' khi mã hoá" }
      - { name: handling_days, type: integer, required: false, nullable: true, role: feature, unit: ngày dương lịch, note: "số ngày từ NGÀY của order_approved_at đến NGÀY của order_delivered_carrier_date (duyệt → bàn giao); null khi thiếu một trong hai mốc, dòng vẫn giữ" }
      - { name: approval_days, type: integer, required: false, nullable: true, role: feature, unit: ngày dương lịch, note: "số ngày từ date_key đến NGÀY của order_approved_at (đặt → duyệt); null khi order_approved_at null, dòng vẫn giữ" }
    constraints:
      - "số dòng = 110.195; số đơn = 96.476; số dòng trễ = 8.713 (FR1.2)"
      - "14 cột đặc trưng đúng thứ tự khai ở `feature_contract` (rules.md); `role: internal` không bao giờ vào ma trận"
      - "không cột nào thuộc FORBIDDEN_COLUMNS; hai cột mốc thô chỉ vào dưới dạng `handling_days` / `approval_days`"
      - "hai đặc trưng ngày là số NGUYÊN ở độ phân giải ngày: mart chỉ có `date_key` (mốc mua đã mất giờ) nên chúng có sai số dưới một ngày — đánh đổi đã nhận, không mở lại U1"

  - name: CohortCounts
    description: >
      Bốn bộ đếm của quần thể, sinh từ CÙNG một truy vấn trả khung; không có truy vấn thứ hai.
      Hình dạng trả về của truy vấn là CẶP `(TrainingFrame, CohortCounts)` — không phải một DataFrame
      kèm thuộc tính ẩn, và `CohortCounts` không đi tiếp vào W2–W6.
    identity: "generated_at của lần đọc — hai lần đọc khác nhau là hai bộ đếm khác nhau"
    attributes:
      - { name: cohort_rows, type: integer, unit: dòng hàng, expected: 110195 }
      - { name: cohort_orders, type: integer, unit: đơn, expected: 96476 }
      - { name: late_rows, type: integer, unit: dòng hàng, expected: 8713 }
      - { name: excluded_missing_carrier, type: integer, unit: đơn, expected: 2, note: "đếm trên tập đơn TRƯỚC khi lọc carrier" }
      - { name: generated_at, type: string, format: iso8601-utc, note: "danh tính của bộ đếm; cũng là giá trị đi vào BaselineMeasurement.cohort_rows" }

  - name: SplitPlan
    description: Quyết định chia hai tập. KHÔNG phải dict `split` trong báo cáo (dict đó giữ sáu khoá thời gian/cỡ mẫu của v2).
    attributes:
      - { name: cut_date, type: date, const: "2018-04-01" }
      - { name: split_column, type: string, const: order_id, note: "chống rò rỉ giữa hai tập" }
      - { name: grain, type: string, const: "dòng hàng" }
      - { name: train_n, type: integer, required: true }
      - { name: test_n, type: integer, required: true }

  - name: BaselineMeasurement
    description: Kết quả đo baseline một đặc trưng, lắp từ hàm của U1 cộng bộ đếm của U2.
    attributes:
      - { name: feature, type: string, const: customer_state }
      - { name: auc, type: number, min: 0, max: 1, note: "đo trên đúng tập kiểm tra của mô hình" }
      - { name: cohort_rows, type: integer, note: "lấy từ CohortCounts, không đếm lại" }
      - { name: same_split_as_model, type: boolean, note: "luôn đúng vì hàm U1 kiểm cut_date == SPLIT_DATE" }

  - name: FittedModel
    description: Trạng thái đã khớp của mô hình triển khai, đủ để chấm điểm lại mà không khớp lại.
    attributes:
      - { name: kind, type: enum, values: [logistic_full, logistic_single_feature], note: "phân biệt mô hình triển khai với baseline một đặc trưng" }
      - { name: estimator, type: any, note: "bộ ước lượng đã fit" }
      - { name: categories, type: object, note: "danh sách phạm trù one-hot của từng trường phân loại" }
      - { name: scaler_means, type: array, note: "trung bình đã khớp trên tập huấn luyện" }
      - { name: scaler_scales, type: array, note: "độ lệch đã khớp trên tập huấn luyện" }
      - { name: feature_names, type: array, note: "đúng thứ tự 14 cột của feature_contract; gắn với ma trận đã huấn luyện" }
      - { name: state_regions, type: object, note: "ánh xạ bang → vùng quan sát được trên tập huấn luyện; cần vì biểu mẫu chỉ có bang người mua (FR3.1) mà score_item không được mở kết nối" }

  - name: ModelArtifact
    description: Cặp tệp trên đĩa trong data/models/ — payload pickle và metadata JSON.
    attributes:
      - { name: payload_path, type: path, note: "MODEL_FILE_NAME, mặc định logistic.pkl" }
      - { name: metadata_path, type: path, note: "MODEL_META_FILE_NAME, mặc định logistic.json" }
      - { name: trained_at, type: string, format: iso8601-utc }
      - { name: library_versions, type: object, note: "phải có để biết tệp thuộc phiên bản nào" }

  - name: ModelBlock
    description: Khối `model` của báo cáo v3 — 11 trường, counts chín khoá.
    attributes:
      - { name: target, type: string, const: is_late }
      - { name: unit, type: string, const: "dòng hàng" }
      - { name: split, type: object, note: "sáu khoá train_start/train_end/test_start/test_end/train_n/test_n" }
      - { name: auc, type: number }
      - { name: auc_tree, type: number }
      - { name: baseline_auc, type: number }
      - { name: beats_baseline, type: boolean, rule: "auc > baseline_auc trên giá trị đã làm tròn" }
      - { name: threshold, type: number, note: "nguồn DUY NHẤT của ngưỡng" }
      - { name: precision, type: number }
      - { name: recall, type: number }
      - { name: counts, type: object, note: "flagged, not_flagged, total, threshold_method, auc_below_target + bốn bộ đếm" }

  - name: PredictionContribution
    description: Một trường đóng góp vào log-odds; đã gộp mọi cột one-hot của trường đó.
    attributes:
      - { name: field, type: string, note: "tên trường, không phải tên cột one-hot" }
      - { name: sign, type: enum, values: [positive, negative], note: "dấu của đóng góp" }
      - { name: log_odds, type: number }

  - name: PredictionOutcome
    description: >
      Kết quả chấm MỘT dòng hàng của `score_item` (C3). Là giá trị trả về của hàm thuần — không đọc
      tệp, không mở kết nối, không mang trạng thái; giao diện chỉ hiển thị nó.
    attributes:
      - { name: probability, type: number, min: 0, max: 1, note: "xác suất lớp trễ; trả nguyên giá trị float, không làm tròn trước khi so ngưỡng" }
      - { name: verdict, type: enum, values: [below_threshold, at_or_above_threshold], note: "probability >= threshold ⇒ at_or_above_threshold; threshold đọc từ model.threshold của C2" }
      - { name: contributions, type: array, length: 3, item: PredictionContribution, note: "ba TRƯỜNG lớn nhất theo |log-odds|, đã gộp theo trường (BR2.10)" }
    constraints:
      - "cùng FittedModel + cùng item ⇒ cùng probability tuyệt đối (BR2.11)"
      - "không nhận cột nào trong feature_contract.forbidden, kể cả giá trị ngày thô của hai cột mốc"
```

## Tóm tắt

Chín entity: hai **sự thật của dữ liệu** (`TrainingFrame`, `CohortCounts`), ba **quyết định của mô hình** (`SplitPlan`, `BaselineMeasurement`, `FittedModel`), hai **hợp đồng ra ngoài** (`ModelArtifact`, `ModelBlock`), và hai **kiểu kết quả chấm điểm** (`PredictionOutcome`, cùng `PredictionContribution` là phần tử của nó).

Điều đáng chú ý: `SplitPlan` (quyết định chia) **khác** `split` (dict trong báo cáo, giữ sáu khoá của v2). Trộn hai thứ này là lỗi đã suýt xảy ra ở Contract Design, và nó sẽ làm mục mô hình trên dashboard hiện `?`.

Điều đáng chú ý thứ hai: `role: feature` / `role: internal` của `TrainingFrame` là cách đọc nhanh, nhưng **nguồn sự thật** cho danh sách đặc trưng là `feature_contract` trong `rules.md` — 14 cột, đúng thứ tự, kèm cách dẫn xuất và danh sách cấm. `order_id`, `order_item_id`, `date_key`, `is_late` không bao giờ vào ma trận.
