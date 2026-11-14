# Architecture Decisions

Nguồn: `components.md`, `../requirements-analysis/requirements.md`, `../user-stories/stories.md`, `../refined-mockups/{mockups,interaction-spec,design-system-mapping}.md`, `../practices-discovery/team-practices.md`.

---

## ADR-001: Tách lưu trữ mô hình thành khối riêng

**Context.** Đợt này lần đầu phải lưu mô hình ra đĩa. `team.md` (`## Code Style`) quy định mô-đun suy luận là **hàm thuần trên `DataFrame`**, mọi I/O nằm ở `service.py`/`report.py`, và `stages.py` là nơi ghép nối duy nhất. Nếu để `pickle` trong `model.py`, mô-đun thuần mất tính chất đó và test nhanh sẽ chạm đĩa.

**Decision.** Tạo `ModelPersistence` là khối riêng, sở hữu định dạng và đường dẫn `data/models/`, nhận `FittedModel` từ `ModelModule` và chịu mọi I/O.

**Consequences.** Tích cực: giữ được quy ước hàm thuần; test của phần lưu tách khỏi test mô hình; định dạng tệp đổi ở một chỗ. Tiêu cực: thêm một mô-đun và một lớp nợ nếu sau này chỉ có một người dùng.

**Alternatives Rejected.** (a) Đặt `pickle` trong `model.py` — vi phạm quy ước I/O, và kéo `tmp_path` vào test của mô-đun thuần. (b) Đặt trong `stages.py` — `stages.py` là điểm ghép nối, không phải nơi sở hữu định dạng tệp.

---

## ADR-002: Hợp đồng báo cáo lên phiên bản 3, và thứ tự đọc an toàn

**Context.** Cần ghi thêm `auc_tree`, `baseline_auc`, `beats_baseline` và các bộ đếm ở grain dòng hàng. Tệp báo cáo là hợp đồng giữa pipeline và dashboard; dashboard phải chịu được tệp cũ.

**Decision.** Nâng `REPORT_VERSION` lên 3, **thuần thêm**: bảy trường đang có của khối `model` (`target`, `split`, `auc`, `threshold`, `precision`, `recall`, `counts` — `report.py:190-200`) giữ nguyên tên và nghĩa; thêm `unit`, `auc_tree`, `baseline_auc`, `beats_baseline`, tức mười một trường. Đọc tệp phiên bản khác trả trạng thái `loi` có thông điệp, **không** ném. Ghi theo đường nguyên tử: tệp tạm → parse lại → kiểm cấu trúc → thay.

**Consequences.** Tích cực: người đọc luôn biết tệp có đúng phiên bản hay không; không có báo cáo nửa vời. Tiêu cực: một lần chạy với tệp cũ sẽ hiện `loi` cho tới khi chạy lại `--stage stats` — chấp nhận, vì đó là sự thật.

**Alternatives Rejected.** (a) Giữ phiên bản 2 và thêm trường tuỳ chọn — bị loại: không phân biệt được "thiếu" với "cũ". (b) Tự nâng cấp tệp cũ khi đọc — bị loại: người đọc không được ghi.

---

## ADR-003: Đơn vị dự đoán là dòng hàng; nhãn kế thừa từ đơn

**Context.** Nhãn trễ là thuộc tính của **đơn**, nhưng đợt này dự đoán ở grain dòng hàng vì 1.278 đơn có nhiều người bán. Hai grain khác nhau trong cùng một mô hình là chỗ sinh rò rỉ.

**Decision.** Chấm điểm và báo mọi chỉ số ở grain **dòng hàng**; nhãn của mỗi dòng kế thừa từ đơn chứa nó; chia tập theo **`order_id`** để không đơn nào nằm ở cả hai phía.

**Consequences.** Tích cực: mô hình học được "người bán nào chịu trách nhiệm"; chỉ số khớp với đơn vị dự đoán. Tiêu cực: AUC ở grain dòng hàng **không so trực tiếp** được với AUC cũ ở grain đơn — phải đo lại baseline, đúng như FR1.3.

**Alternatives Rejected.** (a) Giữ grain đơn — bị loại: 1.278 đơn nhiều người bán không biểu diễn được. (b) Chia tập theo dòng — bị loại: cùng một đơn rơi cả hai phía, AUC bị thổi lên.

---

## ADR-004: Mô hình triển khai là logistic; cây chỉ để báo cáo

**Context.** Giao diện phải hiện **ba đóng góp log-odds cho từng dự đoán**. Mô hình cây không cho hệ số. Ở Market Research đã chốt "chạy cả hai, chọn theo AUC"; ở Rough Mockups quyết định đó bị đảo một phần.

**Decision.** Mô hình **triển khai** là hồi quy logistic. `HistGradientBoosting` vẫn được huấn luyện trên cùng đặc trưng/mốc/quần thể, nhưng chỉ để **báo cáo** `auc_tree` và cho biết đã bỏ bao nhiêu AUC để giữ khả năng giải thích.

**Consequences.** Tích cực: mỗi dự đoán giải thích được; không cần SHAP hay thư viện mới. Tiêu cực: nếu cây vượt trội, mô hình tốt hơn bị bỏ; con số đó phải hiện trong record để đánh đổi không bị che.

**Alternatives Rejected.** (a) Chọn theo AUC và bỏ phần đóng góp — bị loại: mất tiêu chí chất lượng thứ hai. (b) Dùng SHAP cho cây — bị loại: thêm phụ thuộc, trái TC-01.

---

## ADR-005: Giữ 10 output của dashboard, hạ AC2.5.6

**Context.** `AC2.5.6` đòi "nút ở trạng thái chờ" và "kết quả cũ mờ đi"; làm được cần **output thứ 11**. `FR3` đã chốt 10 callback / 10 output. `html.Button` **không** có `loading_state` trong `dash==4.4.1`, và thân tab đã nằm trong `dcc.Loading`.

**Decision.** Giữ **10 output**. Trạng thái "đang tính" biểu đạt bằng spinner có sẵn của `dcc.Loading`. `AC2.5.6` hạ xuống mức "có tín hiệu chờ nhìn thấy được", ghi việc hạ này vào record. Người làm chốt tại cổng Refined Mockups.

**Consequences.** Tích cực: hợp đồng bề mặt không phình; không thêm cơ chế trạng thái. Tiêu cực: nút không bị khoá khi đang tính — bấm hai lần cho cùng kết quả, vô hại nhưng không được ngăn.

**Alternatives Rejected.** (a) Nâng lên 11 output — bị loại ở cổng này: thêm một output phải kiểm và mọi test hình dạng sửa thêm một số, đổi lấy một tiện nghi nhỏ. (b) Dùng `running` của callback — bị loại: cùng lý do, và nó cũng cần output.

---

## ADR-006: Mục thứ tư dùng lại khuôn `_section`/`.chart-card`

**Context.** Ba mục hiện có dựng bằng `_section` với `className="chart-card"`; `assets/style.css` chỉ có 8 selector `.analysis-tab`, tất cả chỉ đổi màu chữ.

**Decision.** Mục "Dự đoán" dùng lại `_section` và `.chart-card` (nền, viền, bán kính, bóng có sẵn). Chỉ **thêm** CSS cho `fieldset`, nút và danh sách đóng góp — dưới `.analysis-tab`, dùng token có sẵn.

**Consequences.** Tích cực: mục mới trông cùng hệ; không thêm luật cho `section`. Tiêu cực: `fieldset` nằm trong thẻ cùng màu nền, phải phân biệt bằng `--surface-sunken` hoặc hạ bóng — chọn `--surface-sunken`.

**Alternatives Rejected.** (a) Tạo lớp `section` riêng — bị loại: hai hệ song song trong cùng tab. (b) Dùng style inline — bị loại: trái quy ước, và không test được bằng CSS token.

---

## ADR-007: Một vùng thông báo, và khối kết quả là con riêng

**Context.** `RESULT_BODY_ID` bọc **toàn bộ** panel và đã là `aria-live="polite"`. Thay con trực tiếp của nó sẽ khiến trình đọc màn hình đọc lại cả tab.

**Decision.** Không đặt `aria-live` thứ hai. Callback dự đoán ghi vào một `div` **con** của khối kết quả (id riêng, không `aria-live`), nằm trong `RESULT_BODY_ID`. Test khẳng định cấu trúc đó, không chỉ đếm số `aria-live`.

**Consequences.** Tích cực: thông báo đúng phạm vi. Tiêu cực: callback phải trả về đúng nút con, không trả về cả panel — ràng buộc này không tự nhiên và cần test canh.

**Alternatives Rejected.** (a) Đặt `aria-live` trên khối kết quả — bị loại: hai vùng lồng nhau đọc hai lần. (b) Bỏ `aria-live` của tab — bị loại: các mục khác đang dựa vào nó.

---

## ADR-008: Hai mô-đun thuần giữ đúng ranh giới I/O — chuyển ba lối tắt ra ngoài

**Context.** Năm phép kiểm định trong `statistics.py` (`late_rate`, `compare_states`, `price_freight_correlation`, `region_late_test`, `seasonal_decomposition`) đã là hàm thuần nhận `DataFrame`/`dict`. Nhưng tệp đó còn hai hàm **không** thuần: `collect_stats(service, filters, generated_at, alpha)` tại `statistics.py:276` nhận một `AnalyticsService` và tự gọi **năm** truy vấn (`kpi_summary`, `late_rates_by_state`, `price_freight_pairs`, `late_rates_by_region`, `revenue_by_period` — `:279-284`), rồi dựng `StatsBlock`; và `build_analysis_report(config, generated_at, logger)` tại `statistics.py:298-313` tự lấy `report_path`, `read_report`, **giữ nguyên khối `model` của báo cáo cũ** (`:311`) và tự dựng `AnalysisReport`. `model.py:338` có lối tắt thứ ba: `train_model` tự dựng `AnalyticsService(config)` để lấy khung huấn luyện. Vì thế khai `depends_on: []` hay "chỉ còn hàm thuần" cho hai khối là **sai với mã đang chạy**, và luật giữ khối `model` cũ đang nằm trong tệp thống kê chứ không thuộc khối nào.

**Decision.** Sau U2, chia lại đúng ba việc, mỗi việc **một** chủ:
1. **`PipelineStages`** lấy khung huấn luyện và `CohortCounts` từ `AnalyticsService`, gọi năm hàm thuần của `StatisticsModule`, gọi `ModelModule` để huấn luyện và chấm điểm (truyền `excluded_missing_carrier` vào), rồi gọi **`ReportContract.assemble_report`**. `collect_stats` và `build_analysis_report` **không còn** là entry point của `statistics.py`; `train_model` không còn tự dựng service.
2. **`ReportContract`** là chủ duy nhất của việc dựng `AnalysisReport`: `assemble_report(stats, model, stamp)` đọc báo cáo cũ và giữ nguyên khối `model` khi người gọi không truyền khối mới. Luật này là của hợp đồng (hai tầng cùng ghi một tệp), không phải của người gọi.
3. **`StatisticsModule`** và **`ModelModule`** chỉ còn hàm thuần; cả hai `depends_on: ReportContract` vì dùng kiểu `StatsBlock`/`ModelBlock` và các kiểu kết quả — đúng như import thật ở `statistics.py:11-24` và `model.py:14`.

**Consequences.** Tích cực: khai báo khớp mã sau U2; I/O nằm một chỗ; test hai mô-đun không cần đĩa; luật giữ khối `model` có chủ; không còn hai nơi cùng "dựng báo cáo". Tiêu cực: `run_stage("stats")` dài thêm phần lấy dữ liệu; `stages.py:12` và các test đang gọi `build_analysis_report`/`collect_stats` phải đổi chỗ gọi — thay đổi thật, ghi vào Functional Design.

**Alternatives Rejected.** (a) Khai `depends_on: AnalyticsService` cho cả hai khối — trung thực với mã hôm nay nhưng giữ nguyên vi phạm quy ước `team.md` và làm mất tính thuần mà cả đợt dựa vào. (b) Để nguyên hai hàm và chỉ ghi chú — bị loại: khối "thuần" khi đó không thuần, và tranh chấp ranh giới quay lại ở Functional Design. (c) Đặt luật giữ khối `model` trong `PipelineStages` — bị loại: đó là luật của hợp đồng, và để ở điểm ghép nối thì mỗi người gọi mới phải nhớ lại. (d) Chia `build_analysis_report` cho cả `PipelineStages` và `ReportContract` cùng lúc — bị loại: hai chủ cho một việc là đúng thứ lỗi mà vòng soát này bắt được.

---

## ADR-009: Không vẽ hai cạnh thật nằm ngoài catalogue

**Context.** Có hai import thật không đi theo hướng `ingest → clean → quality → integrate → analytics → dashboard`: `src/integrate/pipeline.py:10` import thừa `AnalyticsService` (miễn trừ `F401` ở `ruff.toml:27`, ghi là `TD-06`) — cạnh này nối hai khối **có** trong catalogue và chính nó làm đồ thị thật có vòng; và `src/dashboard/analysis_tab.py:27` import `STATE_ICONS`/`TEXTS` từ `src/integration/card.py` (ghi là `TD-26`, cố ý để hai tab dùng chung nhãn, khối đích nằm ngoài catalogue này).

**Decision.** Đồ thị trong `components.md` không vẽ cạnh nào trong hai cạnh đó, và nói rõ cả hai ngay dưới sơ đồ với đúng trạng thái của chúng: `TD-06` là cạnh trong catalogue nhưng là nợ cần xoá — vẽ nó thì khẳng định "không vòng" thành sai; `TD-26` trỏ ra ngoài catalogue.

**Consequences.** Tích cực: đồ thị nói về thiết kế đích, và không ai đọc sơ đồ rồi kết luận sai rằng repo sạch. Tiêu cực: người đọc mã thấy hai cạnh không có trên đồ thị — bù bằng chính ghi chú này và mã nợ tương ứng.

**Alternatives Rejected.** (a) Vẽ cả hai bằng nét đứt — bị loại: đồ thị thành hai loại cạnh và khẳng định "không vòng" mất nghĩa. (b) Xoá `TD-06` ngay trong đợt này — bị loại: ngoài phạm vi đã chốt ở Scope Definition. (c) Thêm `src/integration/card.py` thành khối thứ mười — bị loại: nó không đổi trong đợt này, và làm phình catalogue để mô tả một món nợ đã biết.
