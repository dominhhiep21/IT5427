# Code Summary — u3-prediction-ui

Đơn vị `ui` của intent `261111-model-feature-improvemen`. Kế hoạch đã duyệt:
`code-generation-plan.md` (18 bước, ba chặng). Tài liệu này ghi kết quả **chặng A (bước 1–7)**,
**chặng B (bước 8–15)** và **chặng C (bước 16–18)**.

## Chặng A

**Phạm vi đã làm:** khối dựng cây thuần của mục Dự đoán — hằng đóng, `validate_form`,
`build_prediction_body`, `model_available`, và mục thứ tư của tab. **Không** có callback mới, không
sửa `app.py`, `assets/style.css`, `README.md`, `ci.yml`, `CHANGELOG.md`.

### Lệnh và mốc

Mọi lệnh chạy bằng Python của repo (`.venv`) với UTF-8. Python toàn cục của máy không có `pytest`
nên `python -X utf8 -m pytest` thất bại với `No module named pytest`; mọi số đo dưới đây dùng
`.\.venv\Scripts\python.exe -X utf8`.

| Bước | Lệnh | Kết quả |
|---|---|---|
| 1 — Runner | `python -X utf8 -m pytest -m "not slow" -q` | **đỏ kiểu môi trường**: `No module named pytest` → chuyển sang `.venv` |
| 1 — Runner | `.\.venv\Scripts\python.exe -X utf8 -m pytest -m "not slow" -q` | **623 passed, 14 deselected in 47.01s** (mốc) |
| 2 — Hằng + validator, Red | `... -m pytest tests/unit/test_u3_prediction_section.py -q` | **1 error in 0.31s** — `ImportError: cannot import name 'prediction_section' from 'src.dashboard'` |
| 3 — Green | cùng lệnh | 2 failed, 22 passed → sửa allowlist stdlib của test và câu docstring mô-đun → **24 passed in 1.22s** |
| 4 — Sáu trạng thái, Red | cùng lệnh | **1 error in 1.48s** — `ImportError: cannot import name 'build_prediction_body' from 'src.dashboard.prediction_section'` |
| 5 — Green | cùng lệnh | **40 passed in 1.79s** |
| 6 — Bốn mục, Red | `... -m pytest tests/unit/test_dashboard_analysis_tab.py -q` | **4 failed, 39 passed in 2.53s** — `SECTION_IDS` còn ba mục; `sections_for` chưa có mục thay thế; `analysis_tab` chưa có `model_available` (hai test) |
| 7 — Green | cùng lệnh | **44 passed in 2.27s** |

### Xác nhận sau chặng A

| Lệnh | Kết quả |
|---|---|
| `... -m pytest tests/unit/test_u3_prediction_section.py tests/unit/test_dashboard_analysis_tab.py -q` | **84 passed in 2.07s** |
| `... -m pytest -m "not slow" -q` | **670 passed, 14 deselected in 43.35s** (623 → 670, +47) |
| `... -m ruff check .` | **All checks passed!** |
| `... -m ruff format --check src/dashboard/prediction_section.py src/dashboard/analysis_tab.py tests/unit/test_u3_prediction_section.py` | **3 files already formatted** |
| `... -m pytest tests/unit/test_dashboard_smoke.py -q` | **10 passed in 4.80s** — `len(app.callback_map) == 9`, `build_dashboard_outputs` vẫn 9 |

### Tệp tạo mới

- `src/dashboard/prediction_section.py` — `TOKEN_PENDING`/`TOKEN_MODEL_MISSING`,
  id thành phần (`FORM_ID`, `SUBMIT_ID`, `RESULT_BODY_ID`, `LOADING_ID`, `CHECKLIST_ID`), `STATE_CODES`
  (27 UF), `PAYMENT_TYPES` (5), `INPUT_IDS` (11 trường / 10 thành phần), `DEFAULT_VALUES`,
  `TEXTS3`, `FIELD_LABELS`, `FIELD_ERRORS`, `validate_form`, `build_prediction_body`,
  `model_available`. Miền số dùng lại `MAX_DAYS` và `STATE_CODE_LENGTH` của U2; câu hướng dẫn dùng
  lại `RUN_STATS_HINT` của `report.py`.
- `tests/unit/test_u3_prediction_section.py` — 40 test: hằng đóng, 9 luật `validate_form` +
  biên, cây 10 thành phần/11 giá trị, bốn trường mặc định, sáu trạng thái dựng được, không lộ đường
  dẫn, `model_available` (vắng tệp / payload tốt / payload hỏng có ghi nhật ký / nạp đúng một lần),
  và ba chốt ranh giới phụ thuộc (không phụ thuộc mới, không `AnalyticsService`/`warehouse`, không
  mạng, không literal bí mật).

### Tệp sửa

- `src/dashboard/analysis_tab.py` — `SECTION_PREDICTION = "du-doan"` trong `SECTION_IDS` (bốn mục);
  `sections_for(view, model_present=False)` bọc **riêng** lời gọi mục Dự đoán trong `try/except` và
  trả mục thay thế khi nó ném; bỏ mục Dự đoán khi `report.model is None`; `build_prediction_section`,
  `_prediction_fallback`; `AnalysisPanel(..., model_present=False)`; `render_analysis` hỏi
  `model_available(config)` **một lần** (chỉ khi báo cáo có khối mô hình) rồi truyền xuống.
- `tests/unit/test_dashboard_analysis_tab.py` — `SECTION_IDS` bốn mục đúng thứ tự; báo cáo `mot-phan`
  thiếu khối mô hình thì không có mục Dự đoán; dải tóm tắt vẫn bốn thẻ; cả tab chỉ một `aria-live`;
  thân mục ném ⇒ vẫn đủ bốn mục và tab không ném; `render_analysis` hỏi mô hình đúng một lần và
  truyền câu trả lời xuống.

### Ghi chú thi công (chỗ lệch so với tài liệu thiết kế, và vì sao)

1. **`aria-label` trên `dcc` không dùng được.** `dash` 4.4.1 từ chối `aria-label` trên
   `dcc.Dropdown`, `dcc.Input`, `dcc.Checklist` (`TypeError: unexpected keyword argument`). Mỗi ô
   được đặt trong một `html.Label` thật (nhãn hiển thị) bọc trong `html.Div(className="filter-field",
   data-field=<id ô>)`; BR3.12 vẫn thoả bằng nhãn ngữ nghĩa trong DOM, và test hình dạng của tab
   (không `tabIndex` dương, mọi vùng có `aria-label`) vẫn xanh.
2. **Hình dạng trả về của `build_prediction_body`.** Brief của đơn vị ghi `→ Fieldset ... và
   dcc.Loading bọc Div#du-doan-ket-qua`, nên hàm trả `html.Fieldset` chứa cả `dcc.Loading`; cây
   trong `frontend-components.md` vẽ `Loading` là anh em của `form`. Chọn theo brief.
3. **Chặng A không thêm lớp CSS nào** (`assets/style.css` để nguyên cho chặng B). Mọi `className`
   dùng lại lớp đã có: `filter-field`, `integration-action`, `integration-state`,
   `integration-state-message`, `empty-state` — test "mọi lớp đều có trong stylesheet" của tab vẫn xanh.
4. **`model_available` bắt đúng `ModelError`** và không bao giờ ném; khi có `logger` thì ghi thông
   điệp thô dưới `prediction.model_unavailable`, không ghi giá trị biểu mẫu.
5. **`render_analysis` chỉ hỏi mô hình khi báo cáo có khối mô hình** — vẫn là tối đa một lượt
   `load_model` mỗi lần dựng panel, và không đọc tệp mô hình cho trạng thái `rong`/`loi`.

### Chưa làm (thuộc chặng B và C)

Callback `register_prediction_callback` + `build_outcome_view` (bước 8–9), nối dây trong `app.py`
(bước 10), `callback_map` 9 → 10 và ba tệp hình dạng (bước 11), thẻ AUC theo cờ (bước 12), nhãn grain
(bước 13), câu chữ `model_caption`/README (bước 14), `.field-error` (bước 15), test `slow` mốc sàn và
hai danh sách khai tay của CI (bước 16–17), CHANGELOG + chuỗi xác nhận (bước 18).

## Chặng B

**Phạm vi đã làm:** callback của mục Dự đoán và mọi câu chữ đi kèm — `build_outcome_view`,
`build_error_view`, `read_prediction_report`, `load_prediction_model`, `predict_outcome`,
`register_prediction_callback`; nối dây trong `app.py`; hình dạng 10 callback; thẻ AUC đọc cờ; nhãn
grain ở khối mô hình; câu chữ `model_caption` + README; lớp `.field-error`.

### Lệnh và mốc (đỏ → xanh, từng bước)

| Bước | Lệnh | Kết quả |
|---|---|---|
| 8 — Callback, Red | `... -m pytest tests/unit/test_u3_prediction_section.py -q` | **16 failed, 40 passed in 2.65s** — `AttributeError: module 'src.dashboard.prediction_section' has no attribute 'register_prediction_callback'`; thiếu `build_outcome_view`, `read_prediction_report`, `load_prediction_model`, `INPUT_FIELDS`, `TOKEN_RESULT`, `TOKEN_INVALID` |
| 9 — Green | cùng lệnh | 2 failed, 54 passed → sửa fixture của test (đủ **9** khoá `counts`, `unit`, và báo cáo chỉ có khối mô hình là `mot-phan`) → **56 passed in 1.76s** |
| 10–11 — Hình dạng, Red | `... -m pytest tests/unit/test_dashboard_smoke.py -q` | **1 failed, 9 passed in 5.89s** — `assert len(app.callback_map) == 10` → `assert 9 == 10` |
| 10–11 — Green | cùng lệnh | **10 passed in 6.42s** (`build_dashboard_outputs` vẫn **9**) |
| 12 — Thẻ AUC, Red | `... -m pytest tests/unit/test_dashboard_analysis_tab.py -q` | **1 failed, 44 passed in 2.52s** — `assert '0,65' in 'không đạt mốc 0,70'` (nhãn còn literal) |
| 12 — Green | cùng lệnh | **45 passed in 2.54s** |
| 13 — Nhãn grain, Red | `... -m pytest tests/unit/test_dashboard_analysis_tab.py -q -k model_figures` | **1 failed, 45 deselected** — `assert 0 == 3` (không dòng nào còn nhãn "dòng hàng") |
| 13 — Green | `... -m pytest tests/unit/test_dashboard_analysis_tab.py -q` | **46 passed in 2.27s** |
| 14 — Câu chữ, Red | `... -m pytest tests/unit/test_u3_prediction_section.py tests/unit/test_dashboard_analysis_tab.py -q -k "readme or caption"` | **2 failed, 1 passed, 101 deselected** — caption còn "chỉ đọc", README còn câu chỉ đọc |
| 14 — Green | cùng lệnh | **3 passed, 101 deselected in 1.85s** |
| 15 — CSS, Red | `... -m pytest tests/unit/test_analysis_tab_contrast.py -q` | **1 failed, 3 passed in 0.22s** — `assets/style.css thiếu luật .field-error` |
| 15 — Green | cùng lệnh | **4 passed in 0.05s** |

### Xác nhận sau chặng B

| Lệnh | Kết quả |
|---|---|
| `... -m pytest tests/unit/test_u3_prediction_section.py tests/unit/test_dashboard_analysis_tab.py tests/unit/test_dashboard_smoke.py tests/unit/test_analysis_tab_contrast.py -q` | **118 passed in 6.65s** (60 + 47 + 10 + 4) |
| `... -m pytest -m "not slow" -q` | **691 passed, 14 deselected in 22.85s** (chặng A: 670 → +21) |
| `... -m ruff check .` | **All checks passed!** |
| `... -m ruff format --check` trên 8 tệp đã sửa | **8 files already formatted** |
| `python -X utf8 -c "...create_app(load_config())..."` | `callbacks 10`; `callback_map["du-doan-ket-qua.children"]` có **12** `inputs`, `state == []`, `prevent_initial_call is True` |

Số test của từng tệp sau chặng B: `test_u3_prediction_section.py` **40 → 60**, `test_dashboard_analysis_tab.py`
**44 → 47** (xoá 1, thêm 4), `test_dashboard_smoke.py` **10** (sửa một khẳng định 9 → 10),
`test_analysis_tab_contrast.py` **3 → 4**. Số đếm bề mặt: **10 callback**, **4 mục**, **5 tab**,
Output của callback KPI vẫn **9**, `build_dashboard_outputs` vẫn **9**.

### `src/dashboard/prediction_section.py` — thêm

- Hằng: `TOKEN_RESULT = "day-du"`, `TOKEN_INVALID = "loi"`, `VERDICT_ABOVE`, `INPUT_FIELDS` (11 trường
  theo thứ tự đọc), `FLAG_FIELDS`, ba tên sự kiện `prediction.model_unavailable` / `prediction.scored` /
  `prediction.input_rejected`.
- `TEXTS3` thêm bảy câu: `probability`, `comparison_above`, `comparison_below`, `verdict_above`,
  `verdict_below`, `contributions` (nguyên văn "Ba đóng góp lớn nhất (log-odds, không phải tổng)"),
  `invalid`, `score_failed`.
- `build_outcome_view(outcome, threshold)` — xác suất qua `format_percent(probability * 100)`, câu so
  ngưỡng (ngưỡng định dạng `format_number(threshold, 2)`), câu kết luận nêu **dòng hàng**, ba dòng
  đóng góp với `FIELD_LABELS` + `format_number(log_odds, MODEL_DIGITS)`; gốc cây mang `data-state`.
- `build_error_view(errors)` — mỗi lỗi một `html.P(className="field-error", role="alert", data-field=<id ô>)`.
- `read_prediction_report(config)` bọc `read_report(report_path(config))`;
  `load_prediction_model(config, logger=None)` bọc `load_model`, `ModelError` → `None` + nhật ký;
  `model_available` nay gọi lại `load_prediction_model` (một đường nạp duy nhất).
- `predict_outcome(config, values, logger=None)` — thứ tự đúng `frontend-components.md` §4: đọc báo cáo →
  `report.model is None` ⇒ trạng thái thiếu mô hình (không đọc `None.threshold`) → kiểm biểu mẫu → nạp
  mô hình → `score_item(..., threshold=report.model.threshold)` → dựng thẻ kết quả.
- `register_prediction_callback(app, config, logger=None)` — **một** `Output("du-doan-ket-qua", "children")`,
  **12** `Input` (nút + 11 giá trị), `prevent_initial_call=True`, không `State`.
- `_notice`/`_result_area` dùng chung một khuôn thông báo; `_warning`/`_info` nhận **cả** logger lẫn
  factory nên `app.py` truyền được `_integration_logger` mà không mở tệp nhật ký lúc khởi động.

### Tệp sửa

- `src/dashboard/app.py` — `register_prediction_callback(app, config, _integration_logger)` ngay sau
  `register_analysis_callback`; 9 `Output` của callback KPI không đổi.
- `src/dashboard/analysis_tab.py` — `_auc_note` đọc **chỉ** `counts["auc_below_target"]` và dựng nhãn từ
  `format_number(AUC_TARGET, 2)` (`TEXTS["auc_below"]/["auc_meets"]` thành khuôn `{target}`, xoá nhánh tự
  suy cờ); `_model_figures` đọc trực tiếp `split['train_n']`, `split['test_n']`, `counts['flagged']` và
  ghi "dòng hàng"; `TEXTS["model_caption"]` bỏ câu "Chỉ đọc…", nêu grain dòng hàng của mục Dự đoán.
- `assets/style.css` — `.analysis-tab .field-error` dùng `var(--text-2)`, 14px, không mã màu mới.
- `README.md` (mục Dashboard) — bỏ câu chỉ đọc, thêm mục **Dự đoán** và ghi chú `data/models/` do
  `run --stage stats` sinh, không nằm trong git.
- `tests/unit/test_u3_prediction_section.py` (+17), `tests/unit/test_dashboard_analysis_tab.py` (xoá 1,
  thêm 4), `tests/unit/test_dashboard_smoke.py` (9 → 10), `tests/unit/test_analysis_tab_contrast.py` (+1),
  `tests/integration/test_u3_end_to_end.py` (10 callback; bỏ chỗ ghim "0,70").

### Ghi chú thi công (chỗ lệch so với tài liệu, và vì sao)

1. **"12 `Input` (nút + 11 giá trị)" và "10 thành phần" là hai phép đếm khác nhau, cả hai đều đúng.**
   `INPUT_FIELDS` có 11 trường; hai cờ `has_items`/`has_payment` cùng trỏ `o-co-hang`, nên `_value_inputs`
   khai `Input("o-co-hang", "value")` hai lần — Dash nhận **12** `Input` và truyền tham số thứ 11, 12 cùng
   một danh sách đã chọn. Test
   `test_callback_declares_one_output_and_twelve_inputs_without_state` ghim cả hai con số: **12** `Input`
   nhưng chỉ **11** cặp `(id, prop)` phân biệt. Không thêm thành phần thứ mười một.
2. **Lỗi tại ô hiện trong vùng kết quả, không tiêm vào biểu mẫu.** Callback chỉ có **một** `Output`
   (`du-doan-ket-qua.children`), nên `build_error_view` dựng các `html.P.field-error` mang
   `data-field=<id ô>` **ngay trong vùng kết quả** — đúng ô theo `data-field`, đúng lớp `.field-error`
   như `frontend-components.md` §5, và `role="alert"` để trình đọc màn hình đọc lên. Muốn chèn lỗi vào
   từng ô thì phải có 10 Output nữa, trái BR3.27.
3. **`logger` nhận cả đối tượng lẫn factory.** `app.py` chỉ có `_integration_logger` (factory) chứ không
   giữ một `JsonLogger` sẵn; tạo nó ngay trong `create_app` sẽ mở tệp nhật ký mỗi lần dựng app, kể cả
   trong test. `_warning`/`_info` gọi `logger()` khi `callable`, nên `create_app` truyền factory mà không
   có tác dụng phụ lúc khởi động. Test truyền đối tượng `Recorder` như cũ.
4. **Tên sự kiện dùng dấu chấm, không dùng gạch dưới.** `monitoring-design.md` MON3.5–MON3.7 ghi
   `prediction_model_unavailable` / `prediction_scored` / `prediction_input_rejected`; chặng A đã đặt
   `prediction.model_unavailable` theo thói quen của repo (`integration.log.no_pipeline_run`,
   `model.saved`). Chặng B giữ dấu chấm cho cả ba (`prediction.model_unavailable`, `prediction.scored`,
   `prediction.input_rejected`) và ghi lại đây là chỗ cần sửa **tài liệu**, không phải mã.
5. **`ModelError` lúc chấm điểm hiện nguyên văn trong khối** (BR3.19), không thay bằng câu cố định;
   chỉ nhánh **nạp** mô hình mới dùng câu cố định, vì `str(error)` ở đó chứa đường dẫn tuyệt đối
   (`SR3.10`). Nhật ký vẫn nhận thông điệp thô ở cả hai nhánh.
6. **Báo cáo chỉ có khối mô hình là `mot-phan`, không phải `day-du`.** Test của `read_prediction_report`
   khẳng định đúng điều đó; callback vẫn chấm được vì nó cần `report.model`, không cần khối thống kê.

### Chưa làm (thuộc chặng C)

Test `slow` mốc sàn `test_u3_floor_end_to_end.py` (bước 16), hai danh sách khai tay `ci.yml:35` +
`NEW_FILES` của `test_ci_config.py` (bước 17), `CHANGELOG.md` mốc `v0.5.0` và chuỗi xác nhận bốn bước
(bước 18).

## Chặng C

**Phạm vi đã làm:** cổng mốc sàn trên báo cáo thật, ba đường dẫn vào hai danh sách khai tay của CI, mốc
`v0.5.0` trong `CHANGELOG.md`, mục **Test**/**CI** của `README.md`, và chuỗi xác nhận bốn bước. Không thêm
bước CI nào, không hạ `--cov-fail-under=80`, không đụng `src/analytics/*`.

### Lệnh và mốc (đỏ → xanh, từng bước)

| Bước | Lệnh | Kết quả |
|---|---|---|
| 16 — Mốc sàn | `.\.venv\Scripts\python.exe -X utf8 -m pytest -m slow tests/integration/test_u3_floor_end_to_end.py -q` | **1 passed in 24.47s** (28,09 s cả tiến trình) trên báo cáo vừa sinh: `auc = 0,6482`, `baseline_auc = 0,5297`, mốc sàn `MODEL_AUC_FLOOR = 0,55` → `beats_floor` **True** |
| 16 — Cổng không rỗng | `.\.venv\Scripts\python.exe -X utf8 -c "... beats_floor(auc, baseline, 0.99) ..."` | `floor=0.99 → False` — khẳng định phân biệt được, không phải test luôn xanh |
| 17 — CI | `.\.venv\Scripts\python.exe -X utf8 -m pytest tests/unit/test_ci_config.py -q` | **8 passed in 0.10s**; danh sách khai tay **47 → 50** mục |
| 17 — Lint/format | `ruff check .` và `ruff format --check` trên **cả** danh sách khai tay | **All checks passed!** / **62 files already formatted** |
| 18 — Chuỗi xác nhận, lần 1 | `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify_intent.ps1` | 1/4 **xanh** (691 passed), 2/4 **xanh**, 3/4 **xanh**, 4/4 **đỏ**: `test_linkage_score.py::test_scoring_two_hundred_thousand_pairs_stays_under_sixty_seconds` — `assert 69.6055869999982 < 60.0` → `THAT BAI o buoc: 4/4 … (ma 1)` |
| 18 — Chẩn đoán ca đỏ | `.\.venv\Scripts\python.exe -X utf8 -m pytest tests/unit/test_linkage_score.py -q --cov=src` | **16 passed in 11.11s** — chạy riêng thì xanh, tức ca đỏ là **ngưỡng thời gian có sẵn** của `linkage`, không phải hồi quy của đơn vị này |
| 18 — Chuỗi xác nhận, lần 2 | cùng lệnh `verify_intent.ps1` | **cả bốn bước xanh**: 1/4 691 passed (29,78 s) → 2/4 pipeline `success=True` (6 tầng) → 3/4 `stats` `success=True` → 4/4 **706 passed in 461.02s (0:07:41)**, phủ **92,71%** ≥ 80% |

**Về ca đỏ ở lần chạy đầu:** `test_scoring_two_hundred_thousand_pairs_stays_under_sixty_seconds` đo đồng hồ
thực trên 200.000 cặp khi bộ test chạy **dưới `--cov`** (máy đo được tải 59% từ chính tiến trình harness).
Chạy riêng với cùng cờ phủ, tệp đó xanh trong 11,11 s; lần chạy lại cả chuỗi cũng xanh. Đây là **ngưỡng
thời gian có sẵn** của tầng `linkage` (không thuộc đơn vị này, không sửa tệp đó) — ghi lại chứ **không** nới
ngưỡng, đúng `team.md` `## Deployment`.

### Tệp tạo mới

- `tests/integration/test_u3_floor_end_to_end.py` — một test `@pytest.mark.slow`: dựng lại
  ingest → clean → integrate trên `dataset/` rồi `run_stage(config, "stats")`, đọc
  `data/reports/analysis.json` và khẳng định `view.status == "day-du"`, `report.model is not None`, và
  `beats_floor(model.auc, model.baseline_auc) is True` trên **chính** hai con số của tệp. Không fixture, không
  báo cáo tổng hợp. Đây là **ngoại lệ có chủ đích duy nhất** của quy ước "không ghim một giá trị AUC": nó
  khẳng định mốc sàn, không khẳng định mô hình phải giỏi tới đâu.

### Tệp sửa

- `.github/workflows/ci.yml` — thêm **ba** đường dẫn vào danh sách khai tay của `ruff format --check`:
  `src/dashboard/prediction_section.py`, `tests/unit/test_u3_prediction_section.py`,
  `tests/integration/test_u3_floor_end_to_end.py` (**47 → 50** mục). Không thêm bước, không đổi
  `--cov-fail-under=80`.
- `tests/unit/test_ci_config.py` — ba đường dẫn đó vào `NEW_FILES`, thêm **sau khi** tệp tồn tại (tệp này
  khẳng định mỗi đường dẫn phải có thật trên đĩa).
- `CHANGELOG.md` — mốc **`v0.5.0` — 2026-11-13** theo ba nhóm Thêm / Sửa / Nội bộ: mục Dự đoán và sáu trạng
  thái, test cổng mốc sàn; thẻ AUC đọc cờ, nhãn "dòng hàng", bỏ câu "chỉ đọc"; 10 callback so với 9 `Output`
  của callback KPI, `prediction_section.py`, `.field-error`, danh sách format 50 mục.
- `README.md` — mục **Test** nói đúng số đo (bộ nhanh **691 test**, bộ `slow` **mười lăm** test gồm test cổng
  mốc sàn, các tệp nhanh tự dựng dữ liệu); mục **CI** thêm một câu rằng bộ `slow` chạy trong chính bước đo phủ,
  nên test mốc sàn chạy trong CI mà không cần bước mới.
- `unit-test-instructions.md` — sửa số cũ: tệp test mới là **60 test**, không phải "14–16".

### Tổng kết cuối đơn vị

| Hạng mục | Số đo | Nguồn |
|---|---|---|
| Bộ nhanh | **691 passed**, 15 deselected | `pytest -m "not slow" -q` |
| Bộ `slow` | **15 test** (1 test mới của U3) | `pytest -m slow` |
| Toàn bộ + cổng phủ | **706 passed**, phủ **92,71%** (ngưỡng 80%) | `verify_intent.ps1` bước 4/4 |
| `tests/unit/test_u3_prediction_section.py` | **60 test** | chặng A 40 → chặng B 60 |
| `tests/unit/test_dashboard_analysis_tab.py` | **47 test** (xoá 1, thêm 4) | chặng B |
| `tests/unit/test_dashboard_smoke.py` | **10 test** (9 → 10 callback) | chặng B |
| `tests/unit/test_analysis_tab_contrast.py` | **4 test** (+1 cho `.field-error`) | chặng B |
| `tests/integration/test_u3_floor_end_to_end.py` | **1 test** `slow` | chặng C |
| Callback / Output của callback KPI | **10** / **9** | `test_dashboard_smoke.py` |
| Tab / mục của tab phân tích / thẻ tóm tắt | **5** / **4** / **4** | `test_dashboard_analysis_tab.py` |
| Danh sách `ruff format --check` | **50** mục | `.github/workflows/ci.yml` |
| AUC trên báo cáo thật (chỉ đọc, không phải cổng) | **0,6482** (baseline **0,5297**, mốc sàn **0,55**) | `data/reports/analysis.json` |

### Ghi chú thi công (chặng C)

1. **"Red" của bước 16 là một cổng xác nhận, không phải một tính năng mới.** `beats_floor` và trường
   `baseline_auc` đã có từ U2 (đúng như kế hoạch ghi: hai nhánh đã có test ở
   `test_analytics_baseline_block.py`), nên tệp mới xanh ngay lần chạy đầu — không có pha đỏ hành vi để ghi.
   Để chứng minh khẳng định **không rỗng**, tôi chạy thêm một phép thử phân biệt: cùng hai con số thật nhưng
   `floor=0,99` cho **False**. Đây là chỗ lệch so với khuôn TDD của các bước trước, ghi lại thay vì dựng một
   pha đỏ giả.
2. **Test `slow` mới đặt cạnh `test_u2_model_end_to_end.py`, không gộp vào nó.** Hai tệp đo hai thứ khác
   nhau: U2 đo cấu trúc khối và ngân sách huấn luyện, U3 đo **cổng mốc sàn đọc từ tệp**. Gộp sẽ làm tệp U2
   dài thêm mà không đổi điều nó khẳng định.
3. **Danh sách khai tay của `ci.yml` là 50 mục, không phải 34 như `team.md` ghi.** Con số 34 là mốc của đợt
   trước; ba đợt sau đã nối thêm. Không sửa `team.md` ở đây (việc đó thuộc nghi thức learnings) — ghi lại làm
   dữ kiện cho lần cập nhật tới.
4. **`README.md` mục Test nay nói cả bộ `slow`.** Bản cũ chỉ kể ba tệp end-to-end; nay bộ đó có mười lăm test
   nên câu cũ đã sai từ trước đợt này, không phải do chặng C làm sai đi.

### Chưa làm (ngoài ba bước của chặng C, ghi để người sau quyết)

- **PR3.1–PR3.4 trong `nfr-requirements/performance-requirements.md` chưa có test.** `PR3.5` (mỗi lần bấm ≤ 1
  `read_report` + ≤ 1 `load_model`) đã có test; ba ngưỡng đồng hồ còn lại (`score_item` < 200 ms, `load_model`
  < 2 s, dựng cây < 300 ms) và phép đo tay `PR3.4` (thời gian mở tab +20%) **không** nằm trong 18 bước của kế
  hoạch nên tôi không tự thêm. Đây là khoảng trống của đơn vị, không phải của riêng chặng C.

## Bổ sung sau chặng C — ba test ngân sách (PR3.1–PR3.3)

Khoảng trống ở mục trên đã được đóng ngay sau chặng C: thêm **3 test** vào `tests/unit/test_u3_prediction_section.py` (57 → **60**), đo bằng `time.perf_counter()` với ngưỡng đặt rộng — `score_item` < 200 ms, `load_model` < 2 s, `build_prediction_body` < 300 ms. Đo thật trên máy: **10,5 ms / 0,3 ms / ~2 ms**.

- `python -X utf8 -m pytest tests/unit/test_u3_prediction_section.py -q` → **74 passed**
- `python -X utf8 -m pytest -m "not slow" -q` → **708 passed, 15 deselected**
- `python -X utf8 -m ruff check .` → All checks passed

Thêm vào lúc vá sau soát: `FIELD_LABELS` phủ **đủ 14** đặc trưng (trước đó thiếu 6, nên đóng góp thứ ba có thể
hiện `purchase_weekday` thay vì "Thứ trong tuần"), một test tham số hoá canh đủ 14 nhãn, và `except` của bước
chấm mở rộng sang `ValueError`/`KeyError` để payload nạp được nhưng rỗng không thoát khỏi callback.

Riêng `PR3.4` (thời gian mở tab +20%) vẫn là **đo tay**, không phải test, đúng như `performance-design.md` ghi. Bảng số ở `## Chặng C` phía trên ghi lượt `verify_intent.ps1` chạy **trước** ba test này (706 passed, phủ 92,71%); lượt xác nhận chính thức của Bolt sẽ chạy lại trên cây cuối.

