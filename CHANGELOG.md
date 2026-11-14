# Changelog

Mỗi mốc phát hành một mục `## v0.<n>.<m> — YYYY-MM-DD` với ba nhóm **Thêm**, **Sửa**, **Nội bộ**.
Nội dung viết cho người đọc: cái gì thay đổi với người dùng trước, chi tiết kỹ thuật sau.

## v0.5.0 — 2026-11-13

### Thêm

- Mục thứ tư **Dự đoán** trong tab "Kết quả phân tích": nhập thông tin một **dòng hàng** (11 giá trị, mười
  thành phần) rồi bấm nút để chấm bằng tệp mô hình trong `data/models/`; kết quả in xác suất giao trễ, câu
  so với ngưỡng đang áp trong báo cáo, câu kết luận và **ba** đóng góp lớn nhất (log-odds, không phải tổng).
- Sáu trạng thái của mục ứng với sáu tình huống: **không có mục** khi báo cáo `rong`/`loi` hoặc thiếu khối mô
  hình; `chua-chay` (một dòng hướng dẫn, không có chữ số); `dang-tai` (spinner của `dcc.Loading`, nút **không**
  bị khoá); `day-du` (kết quả); `mo-hinh-chua-san` (nêu nguyên văn `data/models/` và lệnh
  `python -X utf8 -m src.pipeline run --stage stats`, nút bị vô hiệu); `loi` (dữ liệu nhập hoặc lỗi chấm,
  `role="alert"`). Trạng thái "có kết quả **chưa có ngưỡng**" của FR3.2 không dựng được dưới C2 vì khối mô
  hình bắt buộc `threshold` — đã ghi thành deviation D-1.
- Test `slow` **cổng mốc sàn** `tests/integration/test_u3_floor_end_to_end.py`: dựng lại toàn bộ pipeline trên
  dữ liệu thật rồi khẳng định tệp báo cáo thoả `beats_floor(auc, baseline_auc)`. Đây là **ngoại lệ có chủ
  đích duy nhất** của quy ước "không ghim một giá trị AUC vào test": nó khẳng định mốc sàn, không khẳng định
  mô hình phải giỏi tới đâu.

### Sửa

- Thẻ AUC trong dải tóm tắt **chỉ đọc cờ** `counts.auc_below_target` của báo cáo, và nhãn mốc lấy từ
  `AUC_TARGET` thay cho literal "0,70" — đổi mốc mục tiêu trong mã là nhãn đổi theo, không còn nhánh tự suy cờ.
- Nhãn grain ở khối mô hình đổi từ "đơn" sang **"dòng hàng"** ở cả ba chỗ (cỡ mẫu huấn luyện, cỡ mẫu kiểm tra,
  số dòng bị gắn cờ), khớp trường `unit` của báo cáo.
- Câu "Chỉ đọc: … không chọn lại được" ở khối mô hình được thay bằng câu nêu mục Dự đoán ở grain dòng hàng;
  `README.md` mục **Dashboard** và **Lưu ý** nói đúng `data/models/` do `run --stage stats` sinh ra và không
  nằm trong git.
- `README.md` mục **Test** khớp số đo mới: bộ nhanh **691 test**, bộ `slow` mười lăm test (có thêm test cổng
  mốc sàn), cổng phủ 80% vẫn tính trên toàn bộ bộ test.

### Nội bộ

- Dashboard nay có **10 callback** — thêm callback của mục Dự đoán với **một** `Output("du-doan-ket-qua",
  "children")`, **12** `Input` (nút + 11 giá trị; hai cờ dùng chung ô `o-co-hang`), không `State`,
  `prevent_initial_call=True`. Số `Output` của callback KPI vẫn **9**, `build_dashboard_outputs` vẫn trả **9**,
  tab vẫn **5 tab / 4 mục**.
- Thêm `src/dashboard/prediction_section.py`: `STATE_CODES` (27 UF), `PAYMENT_TYPES` (5), `INPUT_IDS` /
  `INPUT_FIELDS`, `DEFAULT_VALUES`, `TEXTS3`, `validate_form` (chín luật), `build_prediction_body`,
  `build_outcome_view`, `build_error_view`, `read_prediction_report`, `load_prediction_model`,
  `model_available`, `predict_outcome`, `register_prediction_callback`. Mô-đun chỉ dựng cây Dash: không mở
  kết nối, không đọc `warehouse/`, không gọi `AnalyticsService`.
- `assets/style.css` thêm `.analysis-tab .field-error` dùng `var(--text-2)` (14px, không token màu mới);
  `tests/unit/test_analysis_tab_contrast.py` canh luật đó.
- `ruff format --check` trong `ci.yml` phủ thêm ba đường dẫn của đợt này — `src/dashboard/prediction_section.py`,
  `tests/unit/test_u3_prediction_section.py`, `tests/integration/test_u3_floor_end_to_end.py` — nên danh sách
  khai tay nay **50** mục; `tests/unit/test_ci_config.py` ghim đúng ba đường dẫn đó trong `NEW_FILES`. Không
  thêm bước CI nào, `--cov-fail-under=80` giữ nguyên.

## v0.4.0 — 2026-11-11

### Thêm

- Tab thứ năm **Kết quả phân tích** trên dashboard: đọc `data/reports/analysis.json` rồi dựng dải tóm tắt
  bốn thẻ — tỉ lệ giao trễ (8,11%), số đơn đã giao (96.478), số kiểm định bị bỏ, AUC trên tập kiểm tra kèm
  dấu đạt/không đạt mốc 0,70 — rồi mục thống kê năm phép kiểm định và mục mô hình.
- Trạng thái của tab nói bằng bốn câu chữ khác nhau: `rong` nêu chưa có báo cáo kèm lệnh cần chạy, `mot-phan`
  nêu đúng khối còn thiếu và giữ chỗ của khối đó, `loi` nêu lý do kèm đường dẫn tệp, `day-du` không có câu
  thông báo. `chua-chay` chỉ tồn tại trong lúc callback đang đọc tệp.
- Kiểm định không chạy được vẫn hiện: dải `skipped` liệt kê từng phép kèm lý do, và mục tương quan / kiểm
  định nhóm / mùa vụ null hiện "không chạy được" thay vì bỏ trống.

### Sửa

- `README.md` mục **Dashboard** (4 tab → 5 tab) và **Test** khớp hình dạng mới: ba test end-to-end `slow`, và
  tab mới dựng `ReportView` trong bộ nhớ nên không đọc tệp báo cáo của repo.
- Tab mô hình **chỉ đọc**: hiện đúng ngưỡng đã báo cáo, không có thanh trượt hay ô nhập, vì hợp đồng C3 chỉ
  mang một ngưỡng đã chọn sẵn.

### Nội bộ

- Thêm `src/dashboard/analysis_tab.py`: tám thành phần trong một callback — `tab-callback`, `loading-shell`,
  `state-mapper`, `summary-strip`, `stats-section`, `skipped-banner`, `model-section`, `formatter`. Tab tự bọc
  `dmc.MantineProvider` vì gốc ứng dụng không có provider, và chỉ dùng lớp đã có trong `assets/style.css`
  (không thêm token màu nào).
- Dashboard nay có **9 callback** (2 của ba tab báo cáo + 6 của tab "Tích hợp" + 1 của tab mới) và **5 tab**;
  số output của callback KPI giữ nguyên **9**. Ba test hình dạng tra tab theo `value` thay cho
  `tabs.children[-1]`, vì tab thứ năm làm vị trí cuối trỏ sang tab mới.
- `ruff format --check` trong `ci.yml` phủ thêm `src/dashboard/analysis_tab.py` và
  `tests/unit/test_dashboard_analysis_tab.py`.

## v0.3.0 — 2026-11-11

### Thêm

- Bước mô hình trong tầng `stats`: huấn luyện bộ phân loại đơn giao trễ trên 96.478 đơn `delivered`, chia
  tập tại mốc **2018-04-01** (đơn rơi đúng ngày cắt thuộc tập kiểm tra, không xáo trộn), rồi chọn ngưỡng cảnh
  báo sao cho F1 cao nhất trên lưới 19 điểm 0,05…0,95.
- Khối `model` trong `data/reports/analysis.json`: `target`, `split`, `auc`, `threshold`, `precision`,
  `recall`, `counts`. Tầng `stats` ghép khối này với khối `stats` trong một lần ghi, nên đọc tệp trả trạng
  thái `day-du` thay vì `mot-phan`.
- `counts.auc_below_target` cho người đọc thấy ngay mô hình có đạt mốc AUC 0,70 hay không, và
  `counts.threshold_method` cho biết ngưỡng đến từ đâu.

### Sửa

- Tầng `stats` ghi tệp một lần cho cả hai khối; bước mô hình đứng sau bước thống kê, hỏng thì tệp báo cáo
  giữ nguyên bản cũ thay vì ghi một nửa.
- `README.md` mục **Chạy pipeline**, **Test** và **Lưu ý** khớp hành vi mới: tầng `stats` sinh cả hai khối, và
  mô hình không lưu ra đĩa nên mỗi lần chạy là một lần huấn luyện lại từ mart.

### Nội bộ

- Thêm `src/analytics/model.py`: 11 cột đặc trưng và 10 cột bị cấm là hằng số có tên, bảng đặc trưng dựng
  từ grain đơn, one-hot và chuẩn hoá khớp **chỉ** trên tập huấn luyện, `class_weight="balanced"`,
  `random_state` cố định, cảnh báo không hội tụ bị biến thành lỗi.
- `AnalyticsService.training_frame()` đọc bảng grain đơn bằng một truy vấn tham số hoá chỉ chạm các view trong
  `VIEW_TABLES`; gộp dòng hàng và dòng thanh toán về một dòng mỗi `order_id` trước khi ghép nên không nhân
  dòng.
- Ghim `scikit-learn==1.6.1` trong `requirements.txt` kèm lý do. Sau khi cài, `numpy` vẫn 2.2.1 và `scipy`
  vẫn 1.15.2, nên không phải ghim lại `numpy` và baseline KPI của U1 không đổi.
- `ruff format --check` trong `ci.yml` phủ thêm `src/analytics/model.py`, `src/analytics/service.py`,
  `tests/unit/test_analytics_model.py` và `tests/integration/test_u2_model_end_to_end.py`.

## v0.2.0 — 2026-11-10

### Thêm

- Tầng `stats` trong pipeline: `python -X utf8 -m src.pipeline run --stage stats` chạy năm phép kiểm định
  trên mart hiện có — tỉ lệ giao trễ kèm khoảng tin cậy Wilson, so sánh bang cao nhất với thấp nhất
  (ngưỡng 100 đơn đã giao), tương quan giá hàng với phí vận chuyển, kiểm định vùng × trễ, và phân rã
  mùa vụ chuỗi doanh thu tháng (chu kỳ 12, tối thiểu 24 tháng).
- Tệp báo cáo dùng chung `data/reports/analysis.json` (phiên bản 2): khối `stats` do tầng `stats` ghi,
  khối `model` dành cho đơn vị mô hình. Đọc tệp trả bốn trạng thái `rong`, `day-du`, `mot-phan`, `loi`
  nên bên đọc luôn có một giá trị để dựng giao diện thay vì một ngoại lệ.
- Kiểm định không đủ điều kiện thì trả `null` và ghi lại lý do trong `skipped`; các kiểm định còn lại
  vẫn chạy.

### Sửa

- Tỉ lệ giao trễ trong báo cáo là phân số 0–1, khác `late_rate_pct` 0–100 của KPI; tab nhân 100 khi hiển
  thị phần trăm.
- `README.md` mục **CI** và **Test** nay khớp `.github/workflows/ci.yml`: cổng phủ 80% tính trên toàn bộ
  bộ test (nhanh + `slow`) và có chạy trong CI.
- Workflow CI nhận thêm nhánh `feature/analysis-and-models` ở cả `push` và `pull_request`, và chạy
  `run --stage stats` sau bước dựng dữ liệu để tầng mới có cổng thật.

### Nội bộ

- Thêm `src/analytics/report.py` (kiểu dữ liệu C1/C2, ghi nguyên tử có bước đọc lại, hàm đọc bốn trạng
  thái) và `src/analytics/statistics.py` (năm phép kiểm định, bộ gom `skipped`).
- `AnalyticsService` có thêm ba phương thức đọc đã gộp ở SQL: `late_rates_by_state`,
  `price_freight_pairs`, `late_rates_by_region`; năm phương thức cũ giữ nguyên chữ ký.
- Ghim `scipy==1.15.2` trong `requirements.txt` kèm lý do; không thêm `statsmodels`.
- `stats` có mặt ở cả hai nơi khai danh sách tầng — `STAGES` trong `src/pipeline/stages.py` và `choices`
  của tham số `--stage` trong `src/pipeline/cli.py` — và một test giữ hai nơi đó khớp nhau. Chỗ lệch
  `TD-11` giữa danh sách tầng và báo cáo liệt kê tầng vẫn còn; đợt này chỉ không làm nó nặng thêm.
- `ruff format --check` trong `ci.yml` phủ thêm hai mô-đun mới và bốn tệp test mới.

## v0.1.0 — 2026-11-06

### Thêm

- Tab **Tích hợp** trên dashboard, mở đầu bằng thẻ "Số đơn theo tháng": tổng số đơn và số đơn
  từng tháng tách theo trạng thái, kèm thời gian chạy truy vấn và nhãn cho biết đang xem
  kết quả đầy đủ, một phần, rỗng hay lỗi.
- Tệp khai báo lược đồ trung gian `config/mediated-schema.yaml` với thực thể `don_hang`; bốn
  trường của bảng đơn được nạp, `bang_giao` mới chỉ được kiểm cột nguồn.
- Tệp cấu hình tab `config/integration-tab.yaml` khai id ổn định cho bốn thẻ tổng quan và
  khối kết quả, để đơn vị sau mở rộng mà không phải đặt lại tên.
- Workflow CI (`.github/workflows/ci.yml`) chạy lint, dựng dữ liệu và bộ test nhanh trên
  `windows-2022`.

### Sửa

- Dashboard nay có bốn tab; tab mới có callback riêng nên lỗi ở tab này không làm hỏng ba tab cũ.
- `logs/` chỉ giữ 10 tệp nhật ký gần nhất sau mỗi lần chạy pipeline.

### Nội bộ

- Thêm `ruff` (ghim `0.17.4`) làm cổng lint + format; cấu hình ở `ruff.toml` với ngưỡng dòng
  112 ký tự.
- Thêm `src/integration/` (mô hình, đọc lược đồ, nạp dữ liệu, viết lại + chạy truy vấn, thẻ).
- Đơn vị không có API HTTP; đầu vào duy nhất của tab là callback Dash.
