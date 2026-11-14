# Business Rules — u3-prediction-ui

Nguồn: `functional-spec.md`, `frontend-components.md`, `../../../inception/requirements-analysis/requirements.md` (FR3, FR3.1–FR3.5, FR2.6, NFR5, NFR6), `../../../inception/user-stories/stories.md` (US2.1–US2.5, US3.1–US3.2), `../../../inception/contract-design/contract-summary.md` (C3), `../../../inception/domain-design/decisions.md` (ADR-005, ADR-008).

Đánh số bắt đầu từ **BR3.11**: các luật hiển thị của đợt trước (dải tóm tắt, ba mục, trạng thái báo cáo) vẫn đang ràng buộc mã hiện có — không định nghĩa lại, không đổi nghĩa.

```yaml
rules:
  - id: BR3.11
    statement: Tab có BỐN mục đúng thứ tự tóm tắt → thống kê → mô hình → dự đoán; mục mới là H3 cùng cấp ba mục kia.
    category: constraint
    applies_to: [AnalysisPanel, PredictionSection]
    trigger: dựng tab khi báo cáo đủ
    logic: >
      IF báo cáo day-du THEN dựng bốn mục với data-section lần lượt tom-tat, thong-ke, mo-hinh, du-doan;
      mục du-doan đặt sau mo-hinh, tiêu đề là html.H3, dùng lại _section và .chart-card.
      IF báo cáo rong/loi THEN không dựng mục du-doan (xem BR3.23).
    violation: "test hình dạng đỏ khi thứ tự hoặc số mục sai"
    source: FR3, AC2.1.1

  - id: BR3.12
    statement: Khối mới không thêm thẻ tóm tắt thứ năm, không đặt tabIndex dương, và mọi vùng nội dung có aria-label hoặc heading ngữ nghĩa.
    category: constraint
    applies_to: [PredictionSection]
    trigger: kiểm cấu trúc cây thành phần
    logic: >
      IF có thẻ tóm tắt thứ năm THEN từ chối. IF bất kỳ nút/ô nào mang tabIndex > 0 THEN từ chối.
      IF một vùng nội dung không có aria-label và không nằm dưới heading ngữ nghĩa THEN từ chối.
    violation: "test duyệt cây khẳng định bốn thẻ, không tabIndex dương, aria-label có mặt"
    source: NFR6, AC2.1.2

  - id: BR3.13
    statement: Hình dạng bề mặt sau thay đổi là 10 callback, 4 mục của tab, 5 tab; Output của callback KPI giữ nguyên 9 và callback mới khai đúng 1.
    category: constraint
    applies_to: [Dashboard]
    trigger: đếm app.callback_map và Output
    logic: >
      Callback KPI giữ đúng 9 Output trong MỘT callback và build_dashboard_outputs vẫn trả 9 giá trị;
      callback mới của khối Dự đoán thêm đúng 1 callback với 1 Output. IF len(app.callback_map) khác 10,
      hoặc build_dashboard_outputs khác 9, hoặc callback mới khai khác 1 Output THEN từ chối. Con số "10
      output" của FR3 là 9 Output của callback KPI cộng 1 Output mới — không phải tổng Output của mọi callback.
    violation: "ba tệp test hình dạng đỏ: test_dashboard_smoke, test_dashboard_analysis_tab, test_u3_end_to_end"
    source: FR3, AC2.1.3

  - id: BR3.14
    statement: Khối không tự đặt aria-live; RESULT_BODY_ID là nơi thông báo duy nhất. Không thêm token màu mới ngoài assets/style.css.
    category: constraint
    applies_to: [PredictionSection]
    trigger: kiểm cây thành phần và CSS
    logic: >
      IF khối chứa aria-live THEN từ chối. IF mã dùng mã màu không có trong style.css (trừ LOADING_COLOR
      đã có tiền lệ) THEN từ chối. Hai kết quả phân biệt bằng CHỮ, không bằng màu.
    violation: "test khẳng định không aria-live thứ hai và không token màu mới"
    source: NFR5, AC2.1.4

  - id: BR3.15
    statement: TEXTS["model_caption"] và README.md mục Dashboard không còn câu khẳng định tab chỉ đọc; chữ dưới 16px dùng token --text-2 đạt tương phản >= 4,5:1.
    category: policy
    applies_to: [TEXTS, README]
    trigger: đọc câu chữ và kiểm tương phản
    logic: >
      IF model_caption hoặc README còn nói khối mô hình chỉ đọc/không nhập được THEN từ chối.
      IF chữ dưới 16px trong khối dùng màu khác --text-2 THEN từ chối.
    violation: "test đọc TEXTS và README; test tương phản đỏ"
    source: FR3, AC2.1.5

  - id: BR3.16
    statement: Câu mở đầu của khối nói rõ dự đoán dành cho MỘT DÒNG HÀNG (một món trong một đơn, có người bán riêng).
    category: policy
    applies_to: [TEXTS]
    trigger: đọc caption của khối
    logic: >
      IF caption không nêu "dòng hàng" và không nêu "một món" THEN từ chối.
    violation: "test đọc caption khẳng định cụm từ"
    source: AC2.1.6

  - id: BR3.17
    statement: Bấm Dự đoán với dữ liệu hợp lệ trả xác suất, phép so với ngưỡng trong báo cáo, và một câu kết luận nói về dòng hàng.
    category: calculation
    applies_to: [PredictionOutcomeView]
    trigger: người dùng bấm nút
    logic: >
      IF 11 giá trị hợp lệ THEN load_model(); IF None THEN BR3.25. ELSE score_item(model, item,
      threshold=report.model.threshold) — ngưỡng LUÔN đọc từ báo cáo, hàm không có giá trị mặc định (C3).
      Hiển thị xác suất (format_percent(probability * 100)), câu so ngưỡng, câu kết luận về dòng hàng.
    violation: "test đơn vị dựng cây từ mô hình giả lập khẳng định ba phần tử"
    source: FR3.1, AC2.2.1

  - id: BR3.18
    statement: Bốn trường payment_type, installments, has_items, has_payment hiện đúng giá trị mặc định và sửa được.
    category: constraint
    applies_to: [PredictionForm]
    trigger: dựng biểu mẫu
    logic: >
      payment_type mặc định 'credit_card', installments mặc định 1, has_items và has_payment mặc định
      được chọn. Cả bốn có điều khiển trên màn hình (Dropdown/Input/Checklist) — không ẩn, không khoá.
    violation: "test đọc props khẳng định giá trị mặc định và loại điều khiển"
    source: FR3.1, AC2.2.2

  - id: BR3.19
    statement: Ô trống hoặc sai định dạng hiện lỗi TẠI Ô ĐÓ, không ném và không làm sập tab.
    category: validation
    applies_to: [PredictionForm]
    trigger: bấm Dự đoán với dữ liệu không hợp lệ
    logic: >
      Kiểm từng trường theo miền ở functional-spec §5. IF sai THEN trả cây có thông điệp lỗi dưới đúng
      ô đó và giữ nguyên phần còn lại; IF false THEN không gọi score_item. ModelError của U2 lọt xuống
      thì hiện nguyên văn trong khối, không ném ra khỏi callback.
    violation: "test gọi callback với ô trống và ô sai dạng, khẳng định lỗi tại ô và không exception"
    source: FR3.1, AC2.2.3

  - id: BR3.20
    statement: Phần giải thích có đúng BA dòng, mỗi dòng một TRƯỜNG, mọi cột one-hot của trường đã gộp trước khi chọn lớn nhất.
    category: calculation
    applies_to: [PredictionContributionView]
    trigger: dựng kết quả
    logic: >
      Lấy outcome.contributions của score_item (đã gộp theo trường ở U2). IF số dòng khác 3 THEN từ chối.
      IF hai dòng cùng trường THEN từ chối.
    violation: "test khẳng định 3 dòng và không trùng trường"
    source: FR3.3, AC2.3.1, AC2.3.3

  - id: BR3.21
    statement: Nhãn của phần giải thích là "Ba đóng góp lớn nhất (log-odds, không phải tổng)".
    category: policy
    applies_to: [PredictionContributionView]
    trigger: dựng kết quả
    logic: >
      IF nhãn khác nguyên văn THEN từ chối.
    violation: "test so khớp chuỗi nguyên văn trong TEXTS"
    source: FR3.3, AC2.3.2

  - id: BR3.22
    statement: Cùng 11 giá trị đầu vào cho cùng một xác suất tuyệt đối, kể cả qua nhiều lần bấm và sau khi khởi động lại dashboard.
    category: calculation
    applies_to: [PredictionSection]
    trigger: chấm điểm
    logic: >
      Khối chỉ dùng trạng thái đã nạp từ tệp mô hình (categories, scaler, feature_names, state_regions)
      và threshold đọc từ báo cáo. IF khối khớp lại phạm trù/scaler lúc dự đoán, dùng random, hay đọc
      đồng hồ THEN từ chối.
    violation: "test đơn vị gọi hai lần và so tuyệt đối; test slow dựng lại panel từ cùng tệp"
    source: FR3.4, AC2.4.1, AC2.4.2

  - id: BR3.23
    statement: Báo cáo rong hoặc loi thì tab KHÔNG có mục Dự đoán.
    category: constraint
    applies_to: [AnalysisPanel]
    trigger: mở tab khi báo cáo thiếu hoặc lỗi
    logic: >
      IF status rong THEN không dựng du-doan, hiện lệnh cần chạy. IF status loi THEN không dựng
      du-doan, hiện lý do và đường dẫn tệp. IF status mot-phan và report.model is None THEN cũng
      không dựng du-doan (không có gì để chấm).
    violation: "test dựng panel với báo cáo rỗng/lỗi, khẳng định không có du-doan"
    source: FR3.2, AC2.5.1, AC2.5.2

  - id: BR3.24
    statement: Không có nhánh "có kết quả nhưng chưa có ngưỡng": C2 bắt buộc threshold trong khối mô hình, và thiếu khối mô hình thì không chấm được nên không có mục Dự đoán.
    category: constraint
    applies_to: [PredictionSection]
    trigger: đọc báo cáo mot-phan
    logic: >
      IF report.model is None THEN không dựng mục du-doan (BR3.23). IF report.model có mặt THEN
      threshold luôn có (report.py::_model_block từ chối tệp thiếu trường, trả loi). IF thiết kế dựng
      nhánh hiển thị xác suất không kèm ngưỡng THEN từ chối — score_item(..., *, threshold) không có
      giá trị mặc định.
    violation: "test dựng báo cáo mot-phan thiếu khối mô hình, khẳng định không có du-doan"
    source: FR3.2, AC2.5.3, C2, C3

  - id: BR3.25
    statement: Báo cáo đủ nhưng data/models/ vắng (hoặc payload hỏng) thì khối hiện một câu chứa nguyên văn "python -X utf8 -m src.pipeline run --stage stats" và "data/models/".
    category: policy
    applies_to: [PredictionSection, TEXTS]
    trigger: load_model trả None hoặc ném ModelError
    logic: >
      IF load_model trả None THEN hiện câu hướng dẫn chứa cả hai nguyên văn trên, tắt nút, không hiện
      xác suất. Câu đó **dùng lại `RUN_STATS_HINT` của `report.py`** thay vì viết bản thứ hai. IF load_model ném ModelError THEN giữ nút tắt, hiện **cùng câu hướng dẫn cố định** và
      ghi thông điệp thô vào nhật ký — KHÔNG hiện str(error) vì nó chứa đường dẫn tuyệt đối (SR3.10).
      Tab không sập trong cả hai nhánh.
    violation: "test dựng panel với models_dir rỗng và với tệp hỏng, khẳng định hai nguyên văn, không exception, và cây không chứa đường dẫn tuyệt đối"
    source: FR3.2, AC2.5.4

  - id: BR3.26
    statement: Trạng thái chua-chay hiện đúng một dòng hướng dẫn bấm nút và KHÔNG hiện số nào.
    category: constraint
    applies_to: [PredictionOutcomeView]
    trigger: mở khối trước lần dự đoán đầu
    logic: >
      IF chưa bấm THEN vùng kết quả chỉ có câu hướng dẫn; IF có bất kỳ chữ số nào THEN từ chối.
    violation: "test khẳng định câu và không có chữ số trong vùng kết quả"
    source: AC2.5.5

  - id: BR3.27
    statement: Trạng thái "đang tính" do spinner của dcc.Loading thể hiện; nút KHÔNG bị khoá và không có Output thứ mười một.
    category: constraint
    applies_to: [PredictionSection]
    trigger: callback đang chạy
    logic: >
      dcc.Loading(custom_spinner) bọc vùng kết quả. IF thiết kế thêm Output thứ hai cho trạng thái chờ,
      hoặc đặt nút disabled trong lúc chạy, THEN từ chối — ADR-005 và unit-of-work.md §U3 ghi rõ
      "spinner của dcc.Loading là đủ", "nút không bị khoá khi đang tính".
    violation: "test đếm Output của callback mới đúng 1; cây có dcc.Loading bọc vùng kết quả"
    source: AC2.5.6, ADR-005

  - id: BR3.28
    statement: Thẻ AUC chỉ đọc counts.auc_below_target; nhãn nêu GIÁ TRỊ MỐC ĐANG ÁP lấy từ AUC_TARGET, không hard-code "0,70"; auc_tree không làm đổi kết luận; nhánh tự suy cờ bị xoá.
    category: calculation
    applies_to: [SummaryCard]
    trigger: dựng thẻ auc
    logic: >
      below = report.model.counts["auc_below_target"]. IF khối mô hình thiếu cờ đó THEN read_report đã
      trả loi (9 khoá counts là bắt buộc), nên giao diện KHÔNG dựng lại phép so model.auc < AUC_TARGET.
      Nhãn = "không đạt mốc {format_number(AUC_TARGET, 2)}" hoặc "đạt mốc {…}". Nhánh dự phòng hiện có
      (analysis_tab.py::_auc_note) và test test_auc_card_falls_back_to_the_value_when_the_flag_is_absent
      bị xoá trong cùng thay đổi — C2 cấm consumer tự suy cờ.
    violation: "test đổi AUC_TARGET giả lập rồi khẳng định nhãn đổi theo; nhánh dự phòng không còn trong mã"
    source: FR2.6, AC3.1.1, AC3.1.2, AC3.1.3, C2

  - id: BR3.29
    statement: Cổng mốc sàn có test đơn vị cho cả hai nhánh và đúng một test slow khẳng định nhánh xanh trên tệp báo cáo thật do --stage stats sinh.
    category: policy
    applies_to: [SlowSuite]
    trigger: chạy bộ slow
    logic: >
      Test đơn vị gọi beats_floor với cặp giá trị dựng tay cho cả true và false. Test slow đọc
      read_report(report_path(real_config)) sau run_stage(config, "stats") và khẳng định
      beats_floor(model.auc, model.baseline_auc) is True; IF dùng fixture/báo cáo dựng tay THEN từ chối.
    violation: "test cổng đỏ khi auc dưới max(floor, baseline_auc); xanh trên dữ liệu thật"
    source: NFR5, AC3.2.1, AC3.2.2

  - id: BR3.30
    statement: Nhãn grain của khối mô hình đổi từ "đơn" sang "dòng hàng" cho split.train_n, split.test_n và counts.flagged; giá trị số không đổi và ba trường được đọc trực tiếp, không đọc mềm.
    category: policy
    applies_to: [ModelSection]
    trigger: dựng mục Mô hình
    logic: >
      IF nhãn còn ghi "đơn" cho ba con số đó THEN từ chối — dự đoán đã ở grain dòng hàng (C2), nên
      nhãn "đơn" là mô tả sai đơn vị. Ba giá trị đọc trực tiếp từ ModelBlock đã kiểm đủ trường
      (split["train_n"], split["test_n"], counts["flagged"]), không dùng .get() với giá trị mặc định.
    violation: "test đọc chuỗi hiển thị khẳng định 'dòng hàng' và không còn 'đơn' ở ba dòng đó"
    source: C2, FR3

  - id: BR3.31
    statement: Lớp .field-error được thêm vào assets/style.css và mọi tệp nguồn/test mới được thêm vào danh sách khai tay của ci.yml:35 cùng lúc với việc tạo tệp.
    category: policy
    applies_to: [Assets, CI]
    trigger: thêm tệp
    logic: >
      IF mã dùng className "field-error" mà assets/style.css không có luật đó THEN từ chối. IF tệp
      src/ hoặc tests/ mới không có trong danh sách ruff format --check của ci.yml THEN từ chối.
    violation: "test_ci_config.py đỏ khi thiếu tệp; kiểm style.css có .field-error"
    source: team.md ## Code Style, TD-20
```

## Tóm tắt luật

| Luật | Nhóm | Câu một dòng |
|---|---|---|
| BR3.11 | constraint | Bốn mục đúng thứ tự; mục Dự đoán sau Mô hình, là `H3` |
| BR3.12 | constraint | Không thẻ thứ năm, không `tabIndex` dương, mọi vùng có nhãn ngữ nghĩa |
| BR3.13 | constraint | 10 callback / 4 mục / 5 tab; Output KPI giữ 9, callback mới 1 |
| BR3.14 | constraint | Một `aria-live` duy nhất; không token màu mới |
| BR3.15 | policy | Bỏ câu "chỉ đọc"; chữ nhỏ dùng `--text-2` |
| BR3.16 | policy | Câu mở đầu nói rõ "một dòng hàng" |
| BR3.17 | calculation | Bấm nút → xác suất + so ngưỡng (đọc từ báo cáo) + kết luận |
| BR3.18 | constraint | Bốn trường mặc định hiện đúng và sửa được |
| BR3.19 | validation | Sai ô → lỗi tại ô, không ném |
| BR3.20 | calculation | Ba đóng góp, gộp theo trường |
| BR3.21 | policy | Nhãn log-odds nguyên văn |
| BR3.22 | calculation | Cùng đầu vào ⇒ cùng xác suất |
| BR3.23 | constraint | `rong`/`loi`/thiếu khối mô hình ⇒ không có mục Dự đoán |
| BR3.24 | constraint | Không có nhánh "kết quả thiếu ngưỡng" (C2 bắt buộc threshold) |
| BR3.25 | policy | Thiếu `data/models/` hoặc payload hỏng ⇒ câu lệnh + đường dẫn |
| BR3.26 | constraint | `chua-chay` ⇒ không hiện số |
| BR3.27 | constraint | "Đang tính" do `dcc.Loading`; nút không khoá, không Output thứ hai |
| BR3.28 | calculation | Thẻ AUC chỉ đọc cờ; nhãn từ `AUC_TARGET`; xoá nhánh dự phòng |
| BR3.29 | policy | Cổng mốc sàn: hai nhánh đơn vị + một test `slow` thật |
| BR3.30 | policy | Nhãn grain đổi "đơn" → "dòng hàng" ở ba con số |
| BR3.31 | policy | `.field-error` vào CSS; tệp mới vào danh sách `ci.yml` |
