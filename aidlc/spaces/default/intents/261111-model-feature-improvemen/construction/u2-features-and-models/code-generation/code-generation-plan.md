# Code Generation Plan — u2-features-and-models

Đơn vị: `u2-features-and-models` (kind `library`). Truyện: **US1.1, US1.2, US1.3, US2.2, US2.3, US2.4, US3.1** (24 tiêu chí — xem `../functional-design/traceability.json`).
Nguồn: `../functional-design/{functional-spec,rules,entities}.md`, `../nfr-design/{security-design,logical-components}.md`, `../nfr-requirements/tech-stack-decisions.md`, `../../../inception/contract-design/contract-summary.md` (C1, C2, C2b, C3).

## Phạm vi

Đơn vị `library`: **không** có lớp API, **không** có frontend. Ba lớp áp dụng: **cấu hình**, **truy cập dữ liệu** (`TRAINING_FRAME_SQL`), **logic nghiệp vụ** (đặc trưng, chia tập, mô hình, ngưỡng, baseline, đóng góp) + **lưu trữ/hợp đồng** (pickle, báo cáo v3).

**Hai điểm chệch phải theo, đã ghi trong `../nfr-design/logical-components.md`:** `feature_names` là danh sách **đã mở rộng** (`list(train_matrix.columns)`), và phép so ở chỗ chấm điểm so **toàn bộ danh sách cột**, không so số cột.

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

## Bốn chặng, bốn điểm dừng (theo yêu cầu của người làm)

Kế hoạch 30 bước ở dưới được chia thành bốn chặng. **Cuối mỗi chặng tôi dừng, báo cáo kết quả (lệnh đã chạy, test đỏ→xanh, số đo), và chờ bạn xác nhận** rồi mới sang chặng sau. Đây là điểm dừng tự đặt theo yêu cầu của bạn, không phải cổng của engine (engine chỉ hỏi một lần cho cả Unit).

| Chặng | Bước | Xong khi |
|---|---|---|
| **A — Nền dữ liệu** | 1–5 | `models_dir` có trong `AppConfig`/`config.yaml`; `training_frame()` trả grain dòng hàng kèm bốn bộ đếm; test dữ liệu xanh |
| **B — Đặc trưng và chia tập** | 6–14 | 14 đặc trưng có hợp đồng kiểm được; chia theo `order_id`; ngưỡng và chỉ số tính trên tập kiểm tra |
| **C — Baseline, báo cáo, lưu trữ** | 15–23 | `baseline_auc`/`beats_baseline`/`auc_below_target` đúng; `analysis.json` v3 đủ 11 trường + 9 khoá; `pickle` nạp lại khớp trạng thái tiền xử lý |
| **D — Chấm điểm, ngân sách, end-to-end** | 24–30 | `score_item` tất định + ba đóng góp gộp theo trường; ngân sách 300/240 đo được; test `slow` xanh trên `dataset/` |

**Điều mỗi điểm dừng phải có:** lệnh đã chạy, kết quả đỏ đầu tiên (bằng chứng TDD), kết quả xanh sau khi sửa, và một dòng nói cái gì sẽ vỡ nếu chặng sau làm sai. Không có báo cáo thì không sang chặng.

## Ánh xạ truyện → bước

| Mục tiêu | Bước |
|---|---|
| `AC1.1.1`, `AC1.1.2` — quần thể + bốn bộ đếm | 3–6 |
| `AC2.4.4` — chia tập theo `order_id`, giao rỗng | 9–12 |
| `AC2.4.5`, `AC1.2.3` — 14 đặc trưng, cột cấm, hai mô hình cùng seed | 7–10 |
| `AC1.2.1`, `AC1.2.2`, `AC1.3.2` — `auc` vs `baseline_auc`, `beats_baseline`, `auc_below_target` | 13–16 |
| `AC1.2.4`, `AC2.4.3` — báo cáo v3, `unit`, `pickle` + trạng thái tiền xử lý | 17–22 |
| `AC2.2.1`, `AC2.3.1`, `AC2.3.3`, `AC2.4.1`, `AC2.4.2` — `score_item`, ba đóng góp gộp theo trường, tất định | 23–26 |
| `AC2.4.6` — `auc_tree` tất định qua hai lần chạy | 27 |
| `NFR1.1`, `NFR2.1`, `NFR3.1`, `NFR4.1` — ngân sách, cổng phủ, không đổi mart | 28–30 |

## Các bước

- [ ] **Step 1 — Cấu hình.** Thêm `models_dir` vào `AppConfig` (`src/config.py`), `_resolve` từ khoá `models_dir` trong `config.yaml` (mặc định `data/models`), và vào vòng `mkdir` của `load_config`.
- [ ] **Step 2 — Runner.** Chạy `python -X utf8 -m pytest tests/unit -q` trên cây chưa sửa để có mốc; ghi lệnh vào `unit-test-instructions.md`.

- [ ] **Step 3 — Truy cập dữ liệu — Red.** `tests/unit/test_analytics_training_frame.py`: khung trả về có **một dòng mỗi cặp `(order_id, order_item_id)`**, `order_id` **không** duy nhất, có `seller_state`/`handling_days`/`approval_days`, bốn bộ đếm trả kèm đúng 110195/96476/8713/2 trên mart tạm dựng bằng SQL.
- [ ] **Step 4 — Truy cập dữ liệu — Green.** Viết lại `TRAINING_FRAME_SQL` ở grain dòng hàng (join `v_fact_order_items`), tính hai cột ngày bằng `date_diff('day', ...)`, trả `(frame, counts)`; đổi kiểm duy nhất của `training_frame()` sang khoá ghép.
- [ ] **Step 5 — Truy cập dữ liệu — Refactor.** Giữ nguyên chặn số dòng; docstring nêu grain.

- [ ] **Step 6 — Đặc trưng — Red.** `tests/unit/test_analytics_features.py`: đúng **14** tên theo thứ tự, 6 phân loại + 6 số + 2 cờ, `forbidden` có cả hai cột mốc thô, và ma trận mã hoá xếp cột theo `numeric → flags → one-hot`.
- [ ] **Step 7 — Đặc trưng — Green.** Mở rộng `CATEGORICAL_FEATURES` (+`seller_state`), `NUMERIC_FEATURES` (+`handling_days`, `approval_days`), `FEATURES` (14), `FORBIDDEN_COLUMNS` (+`order_approved_at`, `order_delivered_carrier_date`), `validate_features` kiểm 14 tên + thứ tự.
- [ ] **Step 8 — Đặc trưng — Refactor.** `feature_names = list(train_matrix.columns)`; ghi rõ trong docstring.

- [ ] **Step 9 — Chia tập — Red.** `tests/unit/test_analytics_split.py`: chia theo `order_id`, giao rỗng, đơn rơi đúng mốc thuộc tập kiểm tra, và mọi dòng hàng của một đơn nằm cùng phía.
- [ ] **Step 10 — Chia tập — Green.** `split_frame` chia trên tập `order_id` rồi gán cả dòng hàng; ném `ModelError` khi giao khác rỗng.
- [ ] **Step 11 — Chia tập — Refactor.** `split_summary` đổi nhãn "đơn" → "dòng hàng"; `expected_total` mặc định 110.195.

- [ ] **Step 12 — Ngưỡng và chỉ số — Red.** `tests/unit/test_analytics_threshold.py`: ngưỡng trên `THRESHOLD_GRID`, ngoài (0,1) ⇒ `ModelError`, precision/recall tính trên tập kiểm tra, làm tròn 4 chữ số.
- [ ] **Step 13 — Ngưỡng và chỉ số — Green.** Giữ `choose_threshold`/`build_model_block` hiện có, đổi `expected_*` và nhãn grain.
- [ ] **Step 14 — Ngưỡng và chỉ số — Refactor.** Docstring nêu rõ đơn vị dòng hàng.

- [ ] **Step 15 — Baseline và cờ — Red.** `tests/unit/test_analytics_baseline_block.py`: gọi `measure_state_baseline` của U1 với `SPLIT_DATE`; `beats_baseline` khớp `auc > baseline_auc` trên giá trị đã làm tròn; `auc_below_target` khớp `auc < AUC_TARGET`; `counts` **chín** khoá, `flagged + not_flagged == total == split["test_n"]`.
- [ ] **Step 16 — Baseline và cờ — Green.** Lắp `BaselineMeasurement`, thêm `MODEL_AUC_FLOOR = 0.55` và hàm thuần `beats_floor(auc, baseline_auc, floor)`.
- [ ] **Step 17 — Baseline và cờ — Refactor.** Tách hằng mới cạnh `AUC_TARGET`.

- [ ] **Step 18 — Báo cáo v3 — Red.** `tests/unit/test_analytics_report_v3.py`: `REPORT_VERSION == 3`; khối `model` đủ **11** trường, `split` giữ **sáu** khoá v2; `counts` chín khoá; đọc tệp v2 ⇒ `loi` có thông điệp; `assemble_report` giữ khối `model` cũ khi không truyền khối mới.
- [ ] **Step 19 — Báo cáo v3 — Green.** `ModelBlock` + `_model_block` + `_verify_pending` nhận 11 trường và chín khoá; thêm `assemble_report`; `_model_block` **kiểm đủ** trường (thiếu ⇒ `loi`).
- [ ] **Step 20 — Báo cáo v3 — Refactor.** `statistics.build_analysis_report` và `stages.py` gọi `assemble_report`; `collect_stats` nhận `DataFrame` (ADR-008).

- [ ] **Step 21 — Lưu mô hình — Red.** `tests/unit/test_analytics_persistence.py`: `save` rồi `load` trả đúng `feature_names`, `categories`, `scaler_means/scales`; vắng tệp ⇒ `None`; tệp rác ⇒ `ModelError`; không khớp lại trên dữ liệu mới.
- [ ] **Step 22 — Lưu mô hình — Green.** Thêm `src/analytics/persistence.py` (`ModelPersistence`, `MODEL_FILE_NAME`, `MODEL_META_FILE_NAME`, `load_model(models_dir)`), dùng `pickle` + JSON metadata.
- [ ] **Step 23 — Lưu mô hình — Refactor.** `stages.py` gọi `save` sau khi ghi báo cáo; docstring nêu `pickle` không phải định dạng trao đổi.

- [ ] **Step 24 — Chấm điểm — Red.** `tests/unit/test_analytics_score_item.py`: 11 giá trị nhập → xác suất trong [0,1] + **ba** đóng góp gộp theo trường (không hai dòng cùng trường); tất định qua hai lần gọi; thiếu trường ⇒ `ModelError` nêu **tên trường**; so **toàn bộ danh sách cột** với `feature_names` ⇒ lệch thứ tự phải ném.
- [ ] **Step 25 — Chấm điểm — Green.** `score_item(model, item, *, threshold)` dựng 14 đặc trưng từ 11 giá trị nhập, gộp log-odds theo trường.
- [ ] **Step 26 — Chấm điểm — Refactor.** Tách hàm gộp đóng góp để test đọc được.

- [ ] **Step 27 — Ngân sách và CI.** Hạ `STAGE_BUDGET_SECONDS` về 300 trong `test_u2_model_end_to_end.py`, đặt `TRAIN_BUDGET_SECONDS = 240` đo riêng bước mô hình; thêm tệp mới vào `ci.yml:35` **và** `NEW_FILES` của `test_ci_config.py`.
- [ ] **Step 28 — Số liệu baseline mới.** Thay 96.478/7.826 ở các nơi của **mô hình** (`model.py`, test đơn vị, test `slow`) bằng 110.195/8.713; **không** chạm `reconcile.py BASELINE`.
- [ ] **Step 29 — Tài liệu.** `README.md` (14 đặc trưng, phiên bản 3, grain dòng hàng); ghi hai ngân sách vào `team.md` qua đường learnings (không sửa tay — theo `CP2.3`).
- [ ] **Step 30 — Test `slow` end-to-end.** Viết lại `tests/integration/test_u2_model_end_to_end.py`: 110.195/96.476/8.713/2, `auc > baseline_auc`, `auc_tree` tất định, báo cáo v3, tệp mô hình nạp lại được.

## Ghi chú thi công

- Không thêm phụ thuộc; không import `numpy` trực tiếp; `pickle` là thư viện chuẩn.
- Không sửa mart (U1 đã xong); `src/integrate/` không bị chạm.
- Test mới tự dựng mart trong `tmp_path` (`TD-09`); chỉ test `slow` chạm `dataset/`.
- Mọi lệnh `python -X utf8`.
