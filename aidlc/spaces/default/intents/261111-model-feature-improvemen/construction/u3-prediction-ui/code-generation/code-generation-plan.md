# Code Generation Plan — u3-prediction-ui

Đơn vị: `u3-prediction-ui` (kind `ui`, gắn vào dashboard). Truyện: **US2.1–US2.5, US3.1, US3.2** (29 tiêu chí — xem `../functional-design/traceability.json`).
Nguồn: `../functional-design/{functional-spec,rules,frontend-components}.md`, `../nfr-design/{performance-design,security-design,logical-components}.md`, `../nfr-requirements/{performance,security}-requirements.md` + `tech-stack-decisions.md`, `../infrastructure-design/{infrastructure-specification,monitoring-design,cicd-pipeline}.md`, `../../../inception/contract-design/contract-summary.md` (C2, C2b, C3).

## Phạm vi

Đơn vị `ui`: **không** có lớp API, **không** có truy cập dữ liệu mới. Bốn lớp áp dụng: **cấu hình/hằng** (LC3.7), **logic giao diện thuần** (LC3.1–LC3.3), **tích hợp** (LC3.4–LC3.6 gọi C2/C2b/C3), **hình dạng bề mặt** (10 callback, 4 mục).

Hai điểm chệch đã ghi trong `functional-spec.md` §0 và phải theo:

- **D-1:** trạng thái "có kết quả chưa có ngưỡng" **không dựng được** dưới C2 — `report.py::_model_block` bắt buộc `threshold`, và `score_item(..., *, threshold)` không có mặc định. Không viết nhánh đó.
- **D-2:** con số "10 output" của FR3 = 9 Output của callback KPI + 1 Output mới; `build_dashboard_outputs` **giữ nguyên 9**.

## Testing Contract

```json
{
  "version": 1,
  "methodology": "tdd",
  "source": "team",
  "ordering": "Với mỗi lớp chạy được của một phần, chúng tôi viết test trước cho hành vi mong muốn và chạy nó để thấy đỏ, rồi mới viết mã cho tới khi test đó xanh, rồi mới chuyển sang lớp kế tiếp — và chỉ chuyển sang phần kế tiếp khi phần đang làm đã có test end-to-end riêng xanh trên dữ liệu thật và toàn bộ bộ nhanh vẫn xanh.",
  "scope": "feature",
  "test_strategy": "standard",
  "project_type": "brownfield",
  "applicable_notes": [
    {
      "layer": "org",
      "text": "We treat tests as a first-class deliverable in every Bolt. The specific\nmethodology (TDD, BDD, ATDD, or classic test-after) is affirmed at\npractices-discovery and recorded in `team.md` under this heading with explicit\n`Methodology` and `Ordering` fields; Code Generation resolves those fields\nindependently from coverage, tooling, and scope notes.\n\nWhen no posture has been affirmed, our default per scope is:\n- **Methodology**: test-after\n- **Ordering**: implement each applicable testable layer, then write and run\n  that layer's tests.\n- `mvp`, `enterprise`, `feature`, `infra`, `classic` add an 80% line-coverage\n  floor and CI execution before merge.\n- `bugfix`, `security-patch` add a targeted regression for the specific\n  bug/vulnerability and require the existing suite to remain green.\n- `express` uses the Minimal strategy: requirement-driven unit tests (one per\n  requirement, with a happy-path floor per component); existing tests remain\n  green.\n- `poc`, `refactor`, `workshop` add no extra new-test floor and require the\n  existing suite to remain green.\n\nThe active `Test Strategy` still applies in every scope and determines test\nvolume/types. Scope floors are additive; they never reduce or replace the\nselected strategy.\n\nBuild and Test verifies defined coverage floors and affirmed quality targets;\nthey may not be weakened to make a step pass.\n\nAffirm a stricter posture in `team.md` if the team commits to one."
    },
    {
      "layer": "team",
      "text": "- **Methodology**: tdd\n- **Ordering**: Với mỗi lớp chạy được của một phần, chúng tôi viết test trước cho hành vi mong muốn và chạy nó để thấy đỏ, rồi mới viết mã cho tới khi test đó xanh, rồi mới chuyển sang lớp kế tiếp — và chỉ chuyển sang phần kế tiếp khi phần đang làm đã có test end-to-end riêng xanh trên dữ liệu thật và toàn bộ bộ nhanh vẫn xanh.\n- **Methodology evidence**: git **không** đưa ra được bằng chứng thứ tự, và nay càng ít hơn trước — mã nguồn cùng test của U3 vào **cùng một commit** (`b384da4 feat: Add U3 feature` chứa cả `src/**` và\n  `tests/**`), còn toàn bộ tầng thống kê/mô hình/tab phân tích và chín mô-đun test của nó hiện **chưa\n  được commit** nên không có mốc thời gian nào để so. Giá trị `tdd` **kế thừa** từ lần phỏng vấn trước\n  (Q3 = A của đợt đó: giữ TDD cho cả phần mô hình, dù phần đó khó viết test trước hơn) và **đã được xác\n  nhận lại cho đợt này** (Q1 = A) sau khi nêu rõ rằng kết quả AUC chỉ biết sau khi chạy; nó thay cho mặc\n  định `test-after` của `org.md`. Người làm cũng nêu rõ **cách** giữ TDD ở lớp mô hình: test viết trước\n  khẳng định **hành vi** (cỡ mẫu, chia tập theo `order_id`, không rò rỉ), chứ không khẳng định một giá\n  trị AUC mục tiêu.\n- **Test của lớp mô hình khẳng định hành vi, không khẳng định một con số mục tiêu.** Cụ thể: cỡ mẫu huấn\n  luyện/kiểm định, việc chia tập theo **`order_id`** (không tách dòng hàng của cùng một đơn sang hai bên),\n  và việc không có cột nào trong `FORBIDDEN_COLUMNS` lọt vào ma trận đặc trưng. Chỉ số chất lượng (AUC,\n  precision, recall, ngưỡng) **được ghi ra và hiển thị**, không được biến thành giá trị kỳ vọng của một\n  test viết trước — nếu không, test sẽ đỏ vì mô hình \"chưa đủ giỏi\" chứ không phải vì mã sai, và người\n  làm sẽ bị đẩy vào việc chỉnh ngưỡng cho test xanh. (Q1 = A; xem `## Way of Working` — chỉ số mô hình\n  không thuộc baseline hợp đồng.)\n- **Ngưỡng phủ 80% đã được cưỡng chế trong CI, trên toàn bộ bộ test** (Q6 = A của đợt trước).\n  `ci.yml:53` chạy `python -X utf8 -m pytest --cov=src --cov-fail-under=80` cho **cả** bộ nhanh và bộ\n  `slow`, vì bảy mô-đun `src/` chỉ có phần phủ đến từ bộ `slow`. Chúng tôi không hạ ngưỡng và không tách\n  cổng sang bộ nhanh để cho một bước pass. `README.md` mục \"CI\" nay nói đúng điều này (chỗ trôi tài liệu\n  của đợt trước đã đóng); `tests/unit/test_ci_config.py` canh \"cổng phủ không bị hạ\" — thêm bước CI mới\n  thì phải **giữ** cổng đó.\n- **Mọi mô-đun mới đều phải có test riêng**, kể cả mô-đun \"chỉ nối dây\". Khoảng trống còn lại là nợ đã\n  biết, không phải mẫu để noi theo: năm phương thức KPI cũ của `src/analytics/service.py`\n  (`kpi_summary`, `revenue_by_period`, `revenue_by_dimension`, `top_entities`, `delivery_kpis`),\n  `src/integrate/validate.py`, `reconcile.py`, `catalog.py`, `connections.py`, `src/pipeline/micro_batch.py`\n  (nhánh lỗi), và đường `--stage all` (`run_all`). **Bốn** phương thức đọc mới phục vụ tầng `stats` thì\n  **đã** có test thật trên DuckDB tạm — đó là mẫu đúng. `src/analytics/service.py` lại là chỗ đợt này sẽ\n  mở rộng (khung huấn luyện ở grain dòng hàng), nên mô-đun mới **không** được lặp lại khoảng trống đó.\n- **Khối lượng hiện tại** (đo lại trên đĩa ngày 2026-11-11): **74** tệp Python trong `src/` (**11.333**\n  dòng), **54** tệp trong `tests/` (**49** mô-đun `test_*` với **499** hàm test, **12** hàm `slow`,\n  **10.086** dòng). Bộ test nay bằng **0,89 lần** khối lượng `src/`; bảy mô-đun test lớn nhất chiếm 48%\n  số dòng test (lớn nhất `test_integration_tab.py` 983 dòng). Dưới TDD + yêu cầu test cho mọi mô-đun mới\n  + không có lát cắt mỏng, khối lượng này còn tăng.\n- **Bộ nhanh và bộ chậm tách bằng marker**, không tách bằng thư mục: `-m \"not slow\"` là bộ nhanh,\n  `-m slow` là bộ cần dữ liệu thật/sinh ra (`pytest.ini`: `testpaths = tests`, marker `slow`,\n  `addopts = -ra`).\n- **Bộ nhanh chưa hermetic** (`TD-09`, mức Cao): **năm** test trong `tests/unit/test_dashboard_smoke.py`\n  và `tests/unit/test_cli.py::test_main_analyze_stage` gọi `load_config()` của repo nên cần\n  `warehouse/olist.duckdb` và `data/marts/` — hai thư mục bị `.gitignore`. CI che lỗ hổng này bằng cách\n  chạy `run --stage all` **và** `run --stage stats` trước bước test; trên máy mới clone bộ \"nhanh\" vẫn\n  đỏ. Điều **đáng noi theo**: năm mô-đun test mới của đợt trước (`test_analytics_report/statistics/model`,\n  `test_dashboard_analysis_tab`, `test_pipeline_stages`) tự dựng mart và tệp báo cáo trong `tmp_path`\n  nên **không** dính `TD-09`; test mới của đợt này phải theo đúng mẫu đó.\n- **Test là chốt hồi quy dữ liệu, không chỉ chốt mã.** Mọi thay đổi cleaning/ghép bản ghi có chủ đích phải\n  cập nhật đồng thời `src/quality/allowlist.py`, `src/integrate/reconcile.py`, `README.md` và test tích\n  hợp; nếu không, `quality` chế độ `full` và `KpiReconciler` sẽ đỏ. Việc này áp **ngay** cho đợt này:\n  thêm **cột** vào mart thì an toàn (không đổi số dòng), nhưng đổi **lọc** hay đổi **grain** thì không.\n- **Test áp đặt cả hình dạng giao diện và CLI.** Hiện có **5 tab, 9 callback, 9 output, 11 view, 3 lệnh\n  con CLI**, cộng **4 thẻ tóm tắt** và **3 mục** của tab phân tích. Các chốt tương ứng:\n  `tests/unit/test_dashboard_smoke.py` (5 tab/9 callback/9 output), `tests/integration/test_u3_end_to_end.py`\n  (9 callback, 5 tab), `tests/unit/test_integration_tab.py` (6 callback của riêng tab \"Tích hợp\"),\n  `tests/integration/test_u2_end_to_end.py` (`len(views) == 11`), `tests/unit/test_pipeline_stages.py`\n  (5 tên tầng, `choices` khớp `STAGES | {\"all\"}`, **3** lệnh con),\n  `tests/unit/test_dashboard_analysis_tab.py` (4 thẻ đúng thứ tự; khối mô hình **không** có ô nhập).\n  Hai điều đáng nhớ: (a) phép đếm lệnh con **đã chuyển** khỏi `tests/unit/test_cli.py` sang\n  `test_pipeline_stages.py`; (b) ràng buộc \"khối mô hình không có ô nhập\" (`TD-23`) **mâu thuẫn trực\n  tiếp** với hạng mục U3 của đợt này — nó là thay đổi có chủ đích phải sửa cả ba nơi: câu chữ\n  `TEXTS[\"model_caption\"]`, test `test_model_block_offers_no_input_control`, và `README.md` mục Dashboard.\n- **`STAGES` nay đã có test riêng** (`tests/unit/test_pipeline_stages.py`, 261 dòng): 5 tên tầng,\n  `choices` của CLI khớp `STAGES | {\"all\"}`, tầng `stats` chạy thật trên mart 730 dòng dựng bằng SQL.\n  Đây là chỗ đã đóng khoảng trống mà bản ghi trước ghi là \"chưa có test riêng\".\n- **`ruff` là cổng lint + format.** `ruff check .` chạy toàn repo; `ruff format --check` chỉ chạy trên\n  **danh sách khai tay 34 mục** trong `ci.yml:35` (`TD-20`), nên tệp nguồn mới **phải** được thêm vào\n  danh sách đó cùng lúc với việc tạo tệp. `tests/unit/test_ci_config.py:14-29` canh 14 tệp của đợt vừa\n  rồi — tiến bộ thật, nhưng danh sách kỳ vọng vẫn khai tay nên đợt sau vẫn phải tự thêm. Mã cũ chưa sạch\n  ruff được dọn theo từng tệp khi có người sửa tới.\n- **Không có kiểm tra kiểu tĩnh.** `mypy`/`pyright` không có trong `requirements.txt` và không có trong\n  CI; type hint vẫn giữ theo quy ước hiện có nhưng không phải cổng. Đây là quyết định đã chốt, không\n  phải thiếu sót.\n- **Scope `feature` áp thêm sàn phủ 80% và yêu cầu chạy trong CI trước khi hợp nhất** — trùng với thực\n  hành đã có, không mâu thuẫn."
    }
  ],
  "obligations": {
    "strategy": "standard",
    "strategy_volume": [
      "Five to eight tests per component.",
      "Unit tests plus integration tests for key boundaries.",
      "Add E2E, performance, or security tests when requirements demand them."
    ],
    "scope_floor": [
      "Meet an 80% line-coverage floor.",
      "Run the selected tests in CI before merge."
    ],
    "combination_rule": "Apply every selected-strategy obligation and every scope-floor obligation; neither replaces the other, and a targeted scope regression may add the narrowest necessary test type beyond the strategy default."
  },
  "plan_profile": {
    "methodology": "tdd",
    "runner_step": "Verify the existing test runner/configuration and record the exact unit-scoped command.",
    "runner_ready_before_first_test": true,
    "testable_layers": [
      "Data model / database behavior",
      "Repository / data access",
      "Business logic",
      "API / endpoint",
      "Frontend behavior"
    ],
    "steps": [
      "Project structure and production configuration skeleton.",
      "Verify the existing test runner/configuration and record the exact unit-scoped command.",
      "Data model / database behavior - Red: write the failing tests and record the failing command output.",
      "Data model / database behavior - Green: implement only enough behavior to pass.",
      "Data model / database behavior - Refactor: improve the implementation while tests stay green.",
      "Repository / data access - Red: write the failing tests and record the failing command output.",
      "Repository / data access - Green: implement only enough behavior to pass.",
      "Repository / data access - Refactor: improve the implementation while tests stay green.",
      "Business logic - Red: write the failing tests and record the failing command output.",
      "Business logic - Green: implement only enough behavior to pass.",
      "Business logic - Refactor: improve the implementation while tests stay green.",
      "API / endpoint - Red: write the failing tests and record the failing command output.",
      "API / endpoint - Green: implement only enough behavior to pass.",
      "API / endpoint - Refactor: improve the implementation while tests stay green.",
      "Frontend behavior - Red: write the failing tests and record the failing command output.",
      "Frontend behavior - Green: implement only enough behavior to pass.",
      "Frontend behavior - Refactor: improve the implementation while tests stay green.",
      "Environment/build configuration.",
      "Documentation and traceability."
    ]
  },
  "input_sha256": "sha256:cce8cd1b41b4a564b291c6292dfbc3e8b188120fa26ec46e67779caf0d9e4023",
  "contract_sha256": "sha256:0e6f593f6e43f32d40a40291230b7d3cc0752ba40e57827d136f24c195cae1ad"
}
```

## Ba chặng, ba điểm dừng

Kế hoạch 18 bước chia ba chặng. **Cuối mỗi chặng tôi dừng, báo cáo (lệnh đã chạy, đỏ→xanh, số đo), và chờ bạn xác nhận** rồi mới sang chặng sau. Đây là điểm dừng tự đặt theo yêu cầu của bạn, không phải cổng của engine (engine chỉ hỏi một lần cho cả Unit).

| Chặng | Bước | Xong khi |
|---|---|---|
| **A — Khối dựng cây thuần** | 1–7 | `prediction_section.py` có hằng + `validate_form` + `build_prediction_body` + `model_available`; tab có **bốn** mục đúng thứ tự; không có callback mới nên `callback_map` vẫn 9 |
| **B — Callback, kết quả, câu chữ** | 8–15 | bấm nút trả xác suất + so ngưỡng + ba đóng góp; lỗi tại ô; **10** callback, `build_dashboard_outputs` vẫn **9**; thẻ AUC đọc cờ; nhãn "dòng hàng"; bỏ câu "chỉ đọc" |
| **C — Cổng mốc sàn, CI, tài liệu** | 16–18 | test `slow` mốc sàn xanh trên báo cáo thật; ba tệp mới trong **cả hai** danh sách khai tay; CHANGELOG/README khớp; chuỗi xác nhận bốn bước xanh |

**Điều mỗi điểm dừng phải có:** lệnh đã chạy, kết quả đỏ đầu tiên (bằng chứng TDD), kết quả xanh sau khi sửa, và một dòng nói cái gì sẽ vỡ nếu chặng sau làm sai. Không có báo cáo thì không sang chặng.

## Ánh xạ truyện → bước

| Mục tiêu | Bước |
|---|---|
| `AC2.1.1`, `AC2.1.2`, `AC2.1.4`, `AC2.1.6` — bốn mục, `H3`, một `aria-live`, câu "một dòng hàng" | 6–7, 14 |
| `AC2.1.3` — 10 callback / 4 mục / 5 tab | 10–11 |
| `AC2.1.5` — bỏ câu "chỉ đọc", `--text-2` | 14–15 |
| `AC2.2.1`, `AC2.2.2` — xác suất + so ngưỡng; bốn trường mặc định sửa được | 2–3, 8–9 |
| `AC2.2.3` — lỗi tại ô | 2–3 |
| `AC2.3.1`–`AC2.3.3` — ba đóng góp gộp theo trường + nhãn | 8–9 |
| `AC2.4.1`, `AC2.4.2` — tất định, kể cả sau khởi động lại | 8–9, 16 |
| `AC2.5.1`, `AC2.5.2`, `AC2.5.4`, `AC2.5.5`, `AC2.5.6` — sáu trạng thái | 4–7 |
| `AC3.1.1`–`AC3.1.3` — thẻ AUC theo mốc đang áp | 12 |
| `AC3.2.1`, `AC3.2.2` — cổng mốc sàn | 16 |
| `NFR3.1`, `NFR5.1` — cổng phủ, mốc sàn trong CI | 16–17 |

## Các bước

### Chặng A — Khối dựng cây thuần

- [x] **Step 1 — Runner.** Chạy `python -X utf8 -m pytest -m "not slow" -q` trên cây chưa sửa, ghi mốc (623 passed) và lệnh vào `unit-test-instructions.md`.
- [x] **Step 2 — Hằng và validator — Red.** `tests/unit/test_u3_prediction_section.py`: `len(STATE_CODES) == 27`, `len(PAYMENT_TYPES) == 5`, `TEXTS3` có caption nêu "dòng hàng", `validate_form` trả lỗi đúng `id` cho 9 luật (bang lạ, ngày sai, giá âm/không phải số, số món 0, trả góp 0, ngày âm, ngày > 365, thanh toán lạ) và **không** lỗi khi 11 giá trị hợp lệ.
- [x] **Step 3 — Hằng và validator — Green.** Tạo `src/dashboard/prediction_section.py` với `STATE_CODES`, `PAYMENT_TYPES`, `TEXTS3`, `INPUT_IDS`, `validate_form(values) -> dict[str, str]`; miền số dùng đúng `MAX_DAYS = 365`/`STATE_CODE_LENGTH = 2` như U2.
- [x] **Step 4 — Sáu trạng thái — Red.** Cùng tệp test: `build_prediction_body(report, model_present=False)` hiện câu chứa **nguyên văn** `python -X utf8 -m src.pipeline run --stage stats` và `data/models/`, nút `disabled`; trạng thái `chua-chay` **không** có chữ số nào; cây con kết quả không chứa `workspace_root` và không chứa `\\`.
- [x] **Step 5 — Sáu trạng thái — Green.** `build_prediction_body` dựng `Fieldset` + 10 thành phần + `dcc.Loading` bọc `Div#du-doan-ket-qua`; `model_available(config, logger=None)` gọi `load_model` một lần, `None`/`ModelError` → `False`.
- [x] **Step 6 — Bốn mục — Red.** `tests/unit/test_dashboard_analysis_tab.py`: `SECTION_IDS` có **4** mục, thứ tự `tom-tat, thong-ke, mo-hinh, du-doan`; tiêu đề mục là `H3`; không `tabIndex` dương; không `aria-live` thứ hai; không thẻ tóm tắt thứ năm; `build_prediction_body` ném ⇒ `sections_for` vẫn trả đủ bốn mục và tab không ném.
- [x] **Step 7 — Bốn mục — Green.** Sửa `analysis_tab.py`: `SECTION_PREDICTION = "du-doan"` vào `SECTION_IDS`; `sections_for(view, model_present=False)` bọc **riêng** lời gọi `build_prediction_body` trong `try/except`; `render_analysis` gọi `model_available` một lần rồi truyền `model_present`.

### Chặng B — Callback, kết quả, câu chữ

- [x] **Step 8 — Callback — Red.** `tests/unit/test_u3_prediction_section.py`: `build_outcome_view(outcome, threshold)` hiện xác suất (`format_percent(p * 100)`), câu so ngưỡng, câu kết luận về **dòng hàng**, đúng **ba** dòng đóng góp với nhãn "Ba đóng góp lớn nhất (log-odds, không phải tổng)" và nhãn tiếng Việt của trường; gọi callback hai lần cùng đầu vào ⇒ cùng xác suất; đầu vào sai ⇒ lỗi tại ô và **không** gọi `score_item`; mỗi lần bấm ≤ 1 `read_report` + ≤ 1 `load_model`.
- [x] **Step 9 — Callback — Green.** Thêm `build_outcome_view`, `read_prediction_report`, `load_prediction_model`, `register_prediction_callback(app, config, logger=None)` — **một** `Output("du-doan-ket-qua", "children")`, 12 `Input`, `prevent_initial_call=True`; callback đọc lại báo cáo mỗi lần bấm, truyền `report.model.threshold`.
- [x] **Step 10 — Nối dây.** `app.py` gọi `register_prediction_callback(app, config, logger)` cạnh `register_callback` của tab; **không** đổi 9 `Output` của callback KPI.
- [x] **Step 11 — Hình dạng — Red/Green.** `test_dashboard_smoke.py`: `len(app.callback_map) == 10`, `build_dashboard_outputs` vẫn **9**; `test_u3_end_to_end.py`: 10 callback, 5 tab; **xoá** `test_auc_card_falls_back_to_the_value_when_the_flag_is_absent`.
- [x] **Step 12 — Thẻ AUC — Red/Green.** `analysis_tab._auc_note` chỉ đọc `counts["auc_below_target"]`; nhãn dùng `format_number(AUC_TARGET, 2)` thay literal "0,70"; test dùng `monkeypatch` đổi `AUC_TARGET` giả lập và khẳng định nhãn đổi theo; `test_u3_end_to_end.py:119` bỏ chỗ ghim chuỗi "0,70".
- [x] **Step 13 — Nhãn grain.** Đổi nhãn `split.train_n`/`split.test_n`/`counts.flagged` từ "đơn" sang "dòng hàng", đọc trực tiếp (không `.get`), kèm test chuỗi hiển thị.
- [x] **Step 14 — Câu chữ.** `TEXTS["model_caption"]` bỏ câu "Chỉ đọc: … không chọn lại được" → câu nêu khối dự đoán ở grain dòng hàng; `README.md` mục Dashboard bỏ câu chỉ đọc, thêm ghi chú `data/models/`; test đọc `README.md`.
- [x] **Step 15 — CSS.** `assets/style.css` thêm `.field-error` dùng `var(--text-2)`; `test_analysis_tab_contrast.py` khẳng định luật đó tồn tại và dùng token đúng.

### Chặng C — Cổng mốc sàn, CI, tài liệu

- [x] **Step 16 — Mốc sàn — Red/Green.** `tests/integration/test_u3_floor_end_to_end.py` (`slow`): chạy `run_stage(config, "stats")` rồi `read_report` và khẳng định `beats_floor(model.auc, model.baseline_auc) is True` trên **tệp thật**, không fixture. Hai nhánh của `beats_floor` đã có test ở `test_analytics_baseline_block.py` — không tạo tệp trùng.
- [x] **Step 17 — CI.** Thêm **ba** đường dẫn (`src/dashboard/prediction_section.py`, `tests/unit/test_u3_prediction_section.py`, `tests/integration/test_u3_floor_end_to_end.py`) vào `ci.yml:35` **và** `NEW_FILES` của `test_ci_config.py` **sau khi** tệp tồn tại (`test_ci_config.py` khẳng định mỗi đường dẫn phải tồn tại). Giữ `--cov-fail-under=80`.
- [x] **Step 18 — Tài liệu và xác nhận.** `CHANGELOG.md` thêm mốc `v0.5.0` (Thêm/Sửa/Nội bộ); `README.md` mục Test/CI khớp; chạy chuỗi bốn bước `scripts/verify_intent.ps1`; ghi `code-summary.md` + `traceability.json` + `source-manifest.json`. Hai việc **không** làm ở đây: sửa `project.md`/`team.md` (qua nghi thức learnings).

## Ghi chú thi công

- Không thêm phụ thuộc; chỉ `dash`, `dash_mantine_components`, `pandas`; `pickle` không đụng tới (U2 sở hữu).
- **Không** sửa `src/analytics/model.py`; chỉ `import` `score_item`, `beats_floor`, `MODEL_AUC_FLOOR`, `AUC_TARGET`.
- Không đọc `warehouse/`, không gọi `AnalyticsService` trong `prediction_section.py` (test canh).
- Test mới tự dựng báo cáo/mô hình trong `tmp_path` (`TD-09`); chỉ test `slow` chạm `dataset/`.
- Mọi lệnh `python -X utf8`.
- `ruff format --check` phải sạch trên ba tệp mới **và** các tệp sửa.
