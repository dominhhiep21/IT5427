# Code Generation Plan — u1-mart-and-baseline

Đơn vị: `u1-mart-and-baseline` (kind `library`). Truyện: **US1.1** — phần của U1 là `AC1.1.3` (mart giữ nguyên số dòng) và hàm baseline mà U2 gọi.
Nguồn: `../functional-design/{functional-spec,rules,entities}.md`, `../nfr-design/{security-design,logical-components}.md`, `../nfr-requirements/tech-stack-decisions.md`, `../../../inception/contract-design/contract-summary.md` (C1).

## Phạm vi

Đơn vị `library` nên **không** có lớp API/endpoint và **không** có lớp frontend. Ba lớp áp dụng: **dữ liệu/mart**, **truy cập dữ liệu** (nối `dim_seller`), **logic nghiệp vụ** (hàm baseline). Không có migration lược đồ: mart là Parquet dẫn xuất, dựng lại được.

## Ánh xạ truyện → bước

| Mục tiêu | Bước |
|---|---|
| `AC1.1.3` — ba cột, mart giữ số dòng | 3–8 |
| `BR1.1`, `BR1.6`, `BR1.7` — bất biến số dòng, kiểu cột, tên `seller_state` | 3–8 |
| `BR1.2` — `seller_state` chỉ từ `dim_seller` | 6–8 |
| `BR1.4`, `BR1.5` — hàm baseline thuần, kiểm `cut_date`, hai nhánh lỗi | 9–11 |
| `BR1.3` — mốc thời gian thô bị cấm làm đặc trưng | 12 (ghi nhận, cưỡng chế ở U2) |
| `NFR4.1` — không hồi quy 5 KPI và số dòng | 3–8, 19 |

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

## Các bước

- [x] **Step 1 — Cấu trúc và cấu hình sản xuất.** Không tạo tệp mới ở bước này; xác nhận `src/integrate/facts.py`, `src/analytics/model.py` là chỗ sửa, và `config.yaml` không cần khoá mới.

- [x] **Step 2 — Xác nhận runner và ghi lệnh.** Chạy `python -X utf8 -m pytest tests/unit -q` trên cây chưa sửa để có mốc xanh; ghi đúng lệnh vào `unit-test-instructions.md`. Lệnh phải chạy được **trước** bước Red đầu tiên.

- [x] **Step 3 — Dữ liệu/mart — Red.** Viết `tests/unit/test_integrate_facts_columns.py` khẳng định: `fact_orders` có `order_approved_at` và `order_delivered_carrier_date`; `fact_order_items` có `seller_state`; `seller_state` **không** tên `state`; số dòng bằng khung đầu vào. Chạy → đỏ.
- [x] **Step 4 — Dữ liệu/mart — Green.** Thêm hai cột vào `FactBuilder.build_orders` (lấy từ `cleaned["orders"]`) và một cột vào `build_order_items`. Chỉ đủ để Step 3 xanh.
- [x] **Step 5 — Dữ liệu/mart — Refactor.** Giữ ba cột ở đúng vị trí trong danh sách trả về; không đổi thứ tự cột cũ; test vẫn xanh.

- [x] **Step 6 — Truy cập dữ liệu — Red.** Viết `tests/unit/test_integrate_seller_state.py` khẳng định: `seller_state` đến từ `dim_seller.state` (so khớp trên một `seller_id` đã biết); `seller_id` không có trong `dim_seller` ⇒ null, **không** ném, **không** mất dòng.
- [x] **Step 7 — Truy cập dữ liệu — Green.** Nối `dims["dim_seller"][["seller_id", "state"]]` trong `build_order_items`, đổi tên `state` → `seller_state` ngay tại chỗ nối.
- [x] **Step 8 — Truy cập dữ liệu — Refactor.** Bảo đảm phép nối là `how="left"` và không nhân dòng; test vẫn xanh.

- [x] **Step 9 — Logic nghiệp vụ — Red.** Viết `tests/unit/test_analytics_baseline.py` cho `measure_state_baseline`: trả AUC trong (0,1) trên khung dựng trong `tmp_path`; `cut_date` khác `SPLIT_DATE` ⇒ `ModelError`; tập kiểm tra rỗng ⇒ `ModelError`; tập kiểm tra một lớp nhãn ⇒ `ModelError`; gọi hai lần cho cùng kết quả; không cột nào ngoài một đặc trưng được dùng.
- [x] **Step 10 — Logic nghiệp vụ — Green.** Viết `measure_state_baseline` trong `src/analytics/model.py`, hàm thuần, chia theo `date_key`, one-hot trên phạm trù tập huấn luyện.
- [x] **Step 11 — Logic nghiệp vụ — Refactor.** Tách phần mã hoá one-hot thành hàm nội bộ để test đọc được ma trận; giữ nguyên chữ ký C1 `-> float`.

- [x] **Step 12 — Ghi nhận `BR1.3`.** Không sửa `FORBIDDEN_COLUMNS` (thuộc U2); thêm một dòng docstring nêu rằng hai cột mốc chỉ được dùng dạng số ngày.

- [x] **Step 13 — Kiểm end-to-end `slow`.** Thêm/đổi `tests/integration/test_u1_mart_columns_end_to_end.py` (marker `slow`): chạy `run --stage all` trên `dataset/`, rồi khẳng định ba cột có mặt, 9 bảng mart + 11 view giữ số dòng, và 5 KPI xanh.

- [x] **Step 14 — Cấu hình môi trường/build.** Thêm **tệp mới** vào danh sách khai tay của `ruff format --check` (`ci.yml:35`); không đổi ngưỡng phủ, không thêm `per-file-ignores`.

- [x] **Step 15 — Tài liệu và truy vết.** `code-summary.md` + `traceability.json`; không sửa `README.md` (phần mô tả mart thuộc U2).

## Ghi chú thi công

- **Không** sửa câu SQL nào của view; chỉ ba cột.
- **Không** thêm phụ thuộc; `numpy` không được import trực tiếp.
- Test mới tự dựng dữ liệu trong `tmp_path` (`TD-09`); chỉ test `slow` chạm `dataset/`.
- Mọi lệnh chạy `python -X utf8`.
- Không commit gì trong bước này; commit là quyết định của người làm sau khi cổng duyệt.
