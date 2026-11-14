# Contract Summary — Cải thiện đặc trưng cho mô hình dự đoán đơn trễ

Nguồn: `../units-generation/{unit-of-work,unit-of-work-dependency}.md`, `../domain-design/{components,decisions}.md`, `../requirements-analysis/requirements.md`, `contract-design-questions.md` (Q1 = A, Q2 = A, Q3 = A).

Ba ranh giới, ba cơ chế. Hai cái đầu đi qua tệp hoặc qua gọi hàm; cái thứ ba — chấm điểm một dòng — cũng là gọi hàm nhưng đi **ngược chiều dữ liệu** (giao diện gọi mô hình), nên nó có hợp đồng riêng. Không ranh giới nào là mạng, nên **không** có timeout, retry, idempotency key hay versioning động.

## Contracts

| # | Provider Unit | Consumer | Mechanism | Owner |
|---|---|---|---|---|
| C1 | `u1-mart-and-baseline` | `u2-features-and-models` | Gọi hàm trong cùng tiến trình + **shared schema** mart | U1 |
| C2 | `u2-features-and-models` | `u3-prediction-ui` | **Tệp** `data/reports/analysis.json` (JSON, có phiên bản) | U2 |
| C2b | `u2-features-and-models` | `u3-prediction-ui` | **Tệp** `data/models/` — artefact, không phải hợp đồng có schema | U2 |
| C3 | `u2-features-and-models` | `u3-prediction-ui` | **Gọi hàm** chấm điểm một dòng, trong cùng tiến trình | U2 |

C2b không phải hợp đồng ngang hàng với C2: `pickle` không có schema và gắn với phiên bản thư viện đã sinh ra nó, nên nó **không** phải định dạng trao đổi giữa các máy — máy khác sinh lại tệp của mình. Nó được nêu để người đọc biết đường dẫn và metadata, không để hứa một hợp đồng.

Không có ranh giới **public/external** nào: không có consumer bên ngoài, không có API công khai; dashboard chỉ bind `127.0.0.1:8050` (`config.yaml`).

---

## C1 — `u1-mart-and-baseline` → `u2-features-and-models`

**Cơ chế.** Gọi hàm trong cùng tiến trình, cùng ngôn ngữ, cùng kiểu dữ liệu (`pandas.DataFrame`). Không serialize, không mạng. Hợp đồng gồm **schema cột** của mart và **chữ ký hàm** đo baseline.

```yaml
shared-schema:
  name: mart-columns-for-modelling
  version: 1
  owner: u1-mart-and-baseline
  provider_view: warehouse/olist.duckdb
  tables:
    - name: v_fact_orders
      grain: order_id
      added_columns:
        - name: order_approved_at
          type: timestamp
          nullable: true
          note: "160 giá trị null; chỉ được dùng ở dạng số ngày dẫn xuất"
        - name: order_delivered_carrier_date
          type: timestamp
          nullable: true
          note: "1.783 giá trị null; chỉ được dùng ở dạng số ngày dẫn xuất"
      invariants:
        - "row_count_unchanged: true"
    - name: v_fact_order_items
      grain: order_id + order_item_id
      added_columns:
        - name: seller_state
          type: string
          nullable: true
          note: "lấy từ dim_sellers, không suy từ địa chỉ khách"
      invariants:
        - "row_count_unchanged: true"

  function:
    name: measure_state_baseline
    owner_module: ModelModule (src/analytics/model.py)
    signature: |
      measure_state_baseline(
          frame: pandas.DataFrame,
          *,
          label_column: str,
          feature_column: str,
          cut_date: str,
          random_state: int,
      ) -> float
    model_form: "một đặc trưng phân loại, one-hot trên các phạm trù của tập huấn luyện, không chuẩn hoá, không đặc trưng khác — để phép so là `mô hình nhiều đặc trưng` với `một đặc trưng`"
    preconditions:
      - "frame là khung grain dòng hàng ĐÃ lọc delivered + có carrier date khi đo quần thể mới (U2); U1 kiểm hàm trên khung order-grain hiện có — hàm không phụ thuộc grain, chỉ phụ thuộc cột nhãn và cột chia"
      - "chia trên date_key với ĐÚNG cut_date mà mô hình triển khai dùng; cùng khoá chia; không đơn nào ở cả hai phía"
      - "feature_column = customer_state (đặc trưng baseline của FR1.3); giá trị lạ ở tập kiểm tra rơi vào phạm trù đã học, không tạo cột mới"
    split_rule: "chia theo cut_date trên ngày đặt hàng, cùng mốc và cùng khoá chia với mô hình triển khai; không đơn nào ở cả hai phía"
    returns: AUC trong (0,1) trên đúng tập kiểm tra do cut_date chia
    purity: không đọc ghi tệp, không mở kết nối, không giữ trạng thái
    errors: "raise ModelError khi quần thể kiểm tra rỗng hoặc chỉ có một lớp nhãn"
```

**Điều consumer phải giữ.** U2 không được đổi grain hai view, không được đổi tên cột đã có, không được lọc bớt dòng. Thêm cột là **an toàn**; đổi grain hoặc đổi lọc là **phá vỡ**, phải qua `StarSchemaValidator` + `KpiReconciler`.

**Bộ đếm quần thể không thuộc hợp đồng này.** `CohortCounts` (`cohort_rows` 110.195, `cohort_orders` 96.476, `late_rows` 8.713, `excluded_missing_carrier` 2) do **U2** sinh từ truy vấn grain dòng hàng, và chỉ đi vào báo cáo qua C2. U1 không sinh và không sở hữu nó — khai nó ở đây sẽ tạo nguồn thứ hai cho cùng bốn con số.

---

## C2 — `u2-features-and-models` → `u3-prediction-ui`

**Cơ chế.** Tệp trên đĩa, cùng máy nhưng **khác tiến trình**: dashboard và `run --stage stats` là hai tiến trình, nên người đọc có thể mở tệp đúng lúc người ghi đang thay nó. Thứ bảo vệ duy nhất là luật ghi **nguyên tử**: tệp tạm → parse lại → kiểm cấu trúc → `os.replace`.

```yaml
shared-schema:
  name: analysis-report
  version: 3
  owner: u2-features-and-models
  path: data/reports/analysis.json   # qua AppConfig.reports_dir, không nhận từ dòng lệnh (SEC-5)
  encoding: "UTF-8, ensure_ascii=false, indent=2"
  top_level:
    version: "{ type: integer, const: 3 }"
    generated_at: "{ type: string, format: iso8601-utc }"
    stats: "StatsBlock — người ghi bảo đảm luôn có; bộ đọc chỉ cấm cả hai khối cùng null (report.py:327-328), nên 'luôn có' là cam kết của C2, không phải điều bộ đọc kiểm"
    model: "ModelBlock — có khi tầng mô hình đã chạy; có thể vắng ở trạng thái mot-phan"
  ModelBlock:
    required:
      # --- bảy trường v2, giữ nguyên tên và nghĩa (ADR-002) ---
      - "{ name: target, type: string }"
      - "{ name: split, type: object }"
      - "{ name: auc, type: number, range: '(0,1)' }"
      - "{ name: threshold, type: number, range: '(0,1)', note: 'nguồn DUY NHẤT của ngưỡng cho khối dự đoán' }"
      - "{ name: precision, type: number, range: '[0,1]' }"
      - "{ name: recall, type: number, range: '[0,1]' }"
      - "{ name: counts, type: object }"
      # --- bốn trường mới của v3 ---
      - "{ name: unit, type: string, const: 'dòng hàng', note: 'nhãn đơn vị cho bốn chỉ số được chấm điểm (FR2.5)' }"
      - "{ name: auc_tree, type: number, range: '(0,1)', note: 'HistGradientBoosting; chỉ để báo cáo, không dùng để quyết định' }"
      - "{ name: baseline_auc, type: number, range: '(0,1)' }"
      - "{ name: beats_baseline, type: boolean, rule: 'bằng đúng auc > baseline_auc, tính trên giá trị ĐÃ làm tròn; do ModelModule tính, U3 chỉ đọc' }"
    split_required:
      - "{ name: train_start, type: string, format: date }"
      - "{ name: train_end, type: string, format: date }"
      - "{ name: test_start, type: string, format: date }"
      - "{ name: test_end, type: string, format: date }"
      - "{ name: train_n, type: integer }"
      - "{ name: test_n, type: integer }"
    split_note: >
      Sáu khoá này là hình dạng THẬT của dict `split` trong `model.py:172-179`, đang được
      hiển thị ở `analysis_tab.py:403-412` và khẳng định ở ba test. Entity `SplitPlan` trong
      `components.md` (cut_date/split_column/grain) mô tả QUYẾT ĐỊNH chia tập, không phải dict
      trong báo cáo — hai thứ khác nhau, đừng đổi dict theo entity.
    counts_required:
      - "{ name: flagged, type: integer, unit: dòng hàng, note: 'sau khi đổi grain, đếm trên dòng hàng; nhãn \"đơn\" hiện có ở tab phải đổi theo (U3)' }"
      - "{ name: not_flagged, type: integer, unit: dòng hàng }"
      - "{ name: total, type: integer, unit: dòng hàng, note: 'bằng split.test_n, tức cỡ mẫu kiểm tra ở grain dòng hàng' }"
      - "{ name: threshold_method, type: string }"
      - "{ name: auc_below_target, type: boolean, rule: 'bằng đúng auc < AUC_TARGET, tính trên giá trị ĐÃ làm tròn (BR2.6)' }"
      - "{ name: cohort_rows, type: integer, unit: dòng hàng }"
      - "{ name: cohort_orders, type: integer, unit: đơn }"
      - "{ name: late_rows, type: integer, unit: dòng hàng }"
      - "{ name: excluded_missing_carrier, type: integer, unit: đơn }"
    counts_invariants:
      - "flagged + not_flagged == total   (BR2.7, model.py:252-261)"
      - "total == split.test_n            (BR2.7)"
    rounding: "auc, precision, recall, threshold, baseline_auc, auc_tree làm tròn 4 chữ số; hai cờ tính trên giá trị đã làm tròn"
  StatsBlock:
    required:
      - "{ name: generated_at, type: string }"
      - "{ name: alpha, type: number }"
      - "{ name: confidence, type: number }"
      - "{ name: late_rate, type: object, fields: [successes, total, rate, ci_low, ci_high] }"
      - "{ name: comparisons, type: array, note: 'bắt buộc có mặt; có thể là mảng rỗng (_stats_block, report.py:478-487)' }"
      - "{ name: skipped, type: array, note: 'bắt buộc có mặt; có thể là mảng rỗng' }"
    nullable:
      - "{ name: correlation, type: object|null, note: 'khoá luôn có; null khi phép kiểm định bị bỏ qua' }"
      - "{ name: group_test, type: object|null }"
      - "{ name: seasonal, type: object|null }"
  read_states:
    - "{ state: day-du, condition: 'version == 3, model có mặt và đọc được' }"
    - "{ state: mot-phan, condition: 'version == 3 nhưng MỘT trong hai khối stats/model vắng hoặc null (read_report, report.py:300-307)' }"
    - "{ state: rong, condition: 'tệp không tồn tại' }"
    - "{ state: loi, condition: 'version != 3, JSON hỏng, hoặc không parse được' }"
  error_behaviour: "trả trạng thái loi kèm thông điệp và đường dẫn tệp; KHÔNG ném"
```

**Điều consumer phải giữ.** U3 **không** tính lại `auc_below_target`, **không** tự so `auc` với hằng số, **không** tự chọn ngưỡng: đọc `counts.auc_below_target` và `threshold`. Nhánh dự phòng hiện có (`analysis_tab.py:218-220` so lại `auc < AUC_TARGET` khi cờ vắng) **phải bị xoá** ở U3, vì với `version == 3` cờ là trường bắt buộc — giữ nó là nguồn thứ hai mà FR2.5 cấm. Cùng thay đổi đó phải rà **mọi chỗ đọc mềm** còn lại của tab (ví dụ `_model_block` dựng khối rỗng khi thiếu `model`) và ghi rõ chỗ nào đổi thành trạng thái `mot-phan` thay vì mặc định.

```yaml
artifact-descriptor:
  name: model-artifact
  owner: u2-features-and-models
  directory_config: "AppConfig.models_dir — trường MỚI, đọc từ khoá models_dir trong config.yaml, mặc định data/models; chưa tồn tại trong src/config.py hôm nay"
  filenames:
    payload: "MODEL_FILE_NAME + MODEL_META_FILE_NAME — hằng của ModelPersistence (mô-đun sở hữu định dạng tệp theo ADR-001), KHÔNG đặt trong report.py: report.py sở hữu hợp đồng báo cáo, không sở hữu định dạng tệp mô hình. Mặc định logistic.pkl / logistic.json"
  loader_contract: "load_model(models_dir) -> FittedModel | None; None khi thư mục hoặc tệp vắng (không ném). Lỗi nạp tệp hỏng thì raise ModelError"
  format: "pickle (thư viện chuẩn) cho payload"
  companion_metadata:
    keys: "[feature_names, library_versions, trained_at]"
    schema: "không có schema riêng — ba khoá trên là hợp đồng tối thiểu, thêm khoá là an toàn"
  guaranteed: |
    nạp lại cho đúng ma trận đặc trưng đã huấn luyện — danh sách phạm trù one-hot
    và tham số StandardScaler đã khớp trên tập huấn luyện; không khớp lại lúc dự đoán
  guarantees_refused:
    - "không phải định dạng trao đổi giữa các máy (gắn với phiên bản thư viện đã sinh ra nó)"
    - "không được commit (data/ nằm trong .gitignore)"
  absent_behaviour: "trạng thái 'mô hình chưa sẵn' kèm câu hướng dẫn nêu lệnh `python -X utf8 -m src.pipeline run --stage stats` và đường dẫn data/models/; không sập (FR3.2)"
  absent_variants:
    - "thư mục vắng (máy mới clone): coi là 'chưa có mô hình', hiện cùng câu hướng dẫn; load_config tạo thư mục rỗng"
    - "thư mục có nhưng tệp vắng: cùng trạng thái, cùng câu"
    - "tệp có nhưng nạp lỗi (pickle hỏng, phiên bản thư viện khác): lỗi có kiểu, hiện thông điệp; KHÔNG ném thô"
```

---

## C3 — `u2-features-and-models` → `u3-prediction-ui` (chấm điểm một dòng)

**Cơ chế.** Gọi hàm trong cùng tiến trình: giao diện dựng đầu vào từ biểu mẫu, gọi hàm thuần của U2, nhận xác suất và ba đóng góp. Hàm **không** đọc tệp và **không** mở kết nối — trạng thái đã lưu được nạp qua C2b rồi truyền vào.

```yaml
function-contract:
  name: score_item
  version: 1
  owner: u2-features-and-models
  module: ModelModule (src/analytics/model.py)
  signature: |
    score_item(
        model: FittedModel,          # đã nạp qua C2b, mang categories + scaler đã khớp
        item: Mapping[str, object],  # 11 giá trị nhập, đúng tên trường của FEATURES
        *,
        threshold: float,            # đọc từ model.threshold của C2 — không tự chọn
    ) -> PredictionOutcome
  PredictionOutcome:
    - "{ name: probability, type: number, range: '[0,1]' }"
    - "{ name: verdict, type: enum, values: [below_threshold, at_or_above_threshold] }"
    - "{ name: contributions, type: array, length: 3, note: 'ba TRƯỜNG lớn nhất theo |đóng góp|, mọi cột one-hot của cùng một trường đã gộp; mỗi phần tử gồm trường, dấu, giá trị log-odds' }"
  input_contract:
    required_keys: "[seller_state, customer_state, order_date, item_price, handling_days, approval_days, item_count, payment_type, installments, has_items, has_payment]"
    key_mapping: >
      Mười một khoá này là MƯỜI MỘT GIÁ TRỊ NHẬP của biểu mẫu (bảy ô lõi + bốn trường mặc định
      sửa được), KHÔNG phải danh sách `FEATURES`. Việc ánh xạ sang `FEATURES` — gồm dẫn xuất
      `purchase_month`/`purchase_weekday` từ `order_date`, `item_price_max`, `item_total`,
      `item_count` — do `score_item` làm, và `FEATURES` là hợp đồng của U2 (đã bảo đảm bởi
      `validate_features`). U3 không được dựng ma trận đặc trưng riêng.
    missing_or_invalid: "raise ModelError với thông điệp nêu TÊN TRƯỜNG; giao diện bắt và hiện lỗi tại ô, không để lọt ra ngoài tab"
    forbidden_input: "không nhận cột nào trong FORBIDDEN_COLUMNS, kể cả giá trị ngày thô của hai cột mốc"
  determinism: "cùng model + cùng item ⇒ cùng probability tuyệt đối; không dùng random, không phụ thuộc thời gian"
  constants:
    AUC_TARGET: "thuộc U2 (src/analytics/model.py); U3 chỉ đọc để hiện 'mốc đang áp' (AC3.1.1), không dùng để tự suy cờ"
    MODEL_AUC_FLOOR: "thuộc U2 (src/analytics/model.py), cạnh AUC_TARGET; U3 chỉ import cho test mốc sàn, không sửa tệp"
```

---

## Contract ownership rules

- **Ai sở hữu schema, người đó đổi.** C1 thuộc U1 (schema mart + chữ ký hàm). C2, C2b, C3 thuộc U2 — kể cả hai hằng số ngưỡng. U3 chỉ đọc và chỉ gọi. Một thay đổi hình dạng do U3 đề nghị phải do U2 thực hiện.
- **Thay đổi an toàn (additive)**: thêm trường vào `ModelBlock`/`StatsBlock`/metadata là an toàn khi consumer bỏ qua trường lạ; consumer **không** được giả định một tập trường đóng.
- **Thay đổi phá vỡ**: đổi `version`, đổi nghĩa một trường, đổi grain, hoặc bỏ trường. Với C2, đổi phá vỡ **phải** tăng `version`; mọi giá trị khác 3 rơi vào `loi` và dashboard nói rõ phải chạy lại `--stage stats` — nó **không** tự nâng cấp tệp (người đọc không được ghi).
- **Không có "đọc mềm".** Thiếu trường không được thay bằng mặc định: đó chính là cách phân biệt "tệp cũ" với "tệp thiếu", và là lý do `loi` tồn tại. Luật này cần **việc thi công** chứ không phải chỉ lời khai: `report.py:_model_block` (:457-468) và `ModelBlock.to_dict` (:190-215) hiện chỉ đọc bảy khoá v2 và để giá trị mặc định, nên tệp v3 thiếu `auc_tree`/`beats_baseline` vẫn ra `day-du`. U2 phải cho hai chỗ đó **kiểm đủ** bốn trường mới và năm khoá `counts` mới, để thiếu trường thật sự rơi vào `loi`.
- **Hai tầng cùng ghi một tệp.** `ReportContract.assemble_report` là nơi duy nhất dựng `AnalysisReport` và giữ khối `model` cũ khi tầng stats ghi lại (ADR-008). Không ai khác được dựng `AnalysisReport`.
- **Không có ranh giới nào cần SLA.** Không mạng, không gọi đồng bộ từ xa ⇒ không timeout, không retry, không circuit breaker. Hai thứ cần bảo vệ là **tính nguyên tử của tệp** (C2) và **tính tất định của hàm chấm điểm** (C3); cả hai đã nằm trong luật ở trên.

## Open questions

| Contract | Question | Blocks |
|---|---|---|
| Q3 (đã trả lời) | **Điểm chệch cần ghi:** bản tóm tắt đã chốt ở `contract-design-questions.md` nói **hai** ranh giới và "U1 sở hữu schema mart + `CohortCounts` + chữ ký hàm". Bản hợp đồng này có **ba** ranh giới (thêm C3) và **`CohortCounts` do U2 sinh**. Hai chỗ chệch phát sinh từ chính vòng soát (R-01, R-05), không phải từ câu trả lời Q3; tệp câu hỏi không được sửa sau khi chốt, nên điểm chệch được ghi ở đây thay vì sửa lịch sử. | Không chặn đơn vị nào — chỉ để người đọc sau không đối chiếu sai |
| — | Ngoài Q3, không còn điểm nào chưa chốt. | — |

**Một dòng về `counts`:** v3 có **chín** khoá (bốn khoá cũ của v2 + `auc_below_target` + bốn bộ đếm quần thể). `components.md` và `unit-of-work.md` đã được cập nhật cùng lúc với bản này; nếu thấy chỗ nào còn ghi "năm mục" thì đó là bản cũ cần sửa, không phải một cách đọc khác.
