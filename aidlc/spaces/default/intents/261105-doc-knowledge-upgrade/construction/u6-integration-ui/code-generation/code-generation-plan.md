# Code Generation Plan — u6-integration-ui

## Summary

- Builds: tab "Tích hợp" với màn hình tổng quan bốn thẻ, bốn màn hình chi tiết, năm trạng thái và **sáu** callback (gồm callback của vùng kết quả `don-theo-thang`)
- Touches: `src/integration/tab.py` (mới), `src/dashboard/app.py`, `src/integration/card.py`, `config/integration-tab.yaml`, `requirements.txt`, `tests/unit/test_integration_tab.py` (mới), `tests/unit/test_dashboard_smoke.py`, `tests/unit/test_integration_card.py`, `tests/integration/test_u3_end_to_end.py`, `.github/workflows/ci.yml`
- Tests: 1 tệp test mới, khoảng 20–26 hàm test; cập nhật 4 tệp test hiện có

## Nguồn vào

`construction/u6-integration-ui/{functional-design,nfr-requirements,nfr-design,infrastructure-design}/`; `inception/contract-design/contract-summary.md` (C3–C9); `inception/units-generation/unit-of-work.md` §U6; `inception/requirements-analysis/requirements.md` (FR5.1–FR5.6, NFR1, NFR4).

## Testing Contract

```json
{
  "version": 1,
  "methodology": "tdd",
  "source": "team",
  "ordering": "Với mỗi lớp chạy được của một Unit, chúng tôi viết test trước cho hành vi mong muốn và chạy nó để thấy đỏ, rồi mới viết mã cho tới khi test đó xanh, rồi chuyển sang lớp kế tiếp và chạy lại toàn bộ bộ nhanh trước khi coi Unit là xong.",
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
      "text": "- **Methodology**: tdd\n- **Methodology evidence**: Người làm chốt ở phỏng vấn Q1 = B — \"viết test trước rồi mới viết code\".\n  Bằng chứng tĩnh trong repo **không** phân biệt được thứ tự: lịch sử git chỉ có 6 commit và mã nguồn\n  cùng test của U3 được đưa vào **cùng một commit** (`b384da4 feat: Add U3 feature`, có cả `src/**` và\n  `tests/**`). Vì vậy giá trị `tdd` ở đây đến từ quyết định của người làm, không phải từ git; nó thay\n  cho mặc định `test-after` của `org.md` mà bản nháp trước đang dùng tạm.\n- **Ordering**: Với mỗi lớp chạy được của một Unit, chúng tôi viết test trước cho hành vi mong muốn và\n  chạy nó để thấy đỏ, rồi mới viết mã cho tới khi test đó xanh, rồi chuyển sang lớp kế tiếp và chạy lại\n  toàn bộ bộ nhanh trước khi coi Unit là xong.\n- **Ngưỡng phủ tối thiểu 80%** (phỏng vấn Q3 = C), áp cho `src/`. Đây là ngưỡng **đặt ra**, không phải\n  ngưỡng đang được cưỡng chế: `pytest-cov` đã có trong `requirements.txt` và `README.md` có lệnh\n  `--cov=src`, nhưng `pytest.ini` chưa có `--cov-fail-under` và repo chưa có CI. Chúng tôi đo bằng\n  `pytest --cov=src` trên bộ nhanh + bộ `slow` trước khi coi một đơn vị công việc là xong.\n- **Mọi module mới đều phải có test riêng** (phỏng vấn Q5 = A) — kể cả module \"chỉ nối dây\". Đây là\n  chỗ chúng tôi **thắt chặt** so với hiện trạng: `src/analytics/service.py`, `src/integrate/validate.py`,\n  `reconcile.py`, `catalog.py`, `connections.py`, `src/pipeline/micro_batch.py`, `stages.py` hiện không\n  có unit test trực tiếp, và khoảng trống đó không còn được chấp nhận cho mã mới.\n- **`ruff` là cổng lint + format** (phỏng vấn Q4 = B): `ruff check` và `ruff format --check` phải sạch\n  trước khi một thay đổi được coi là xong. Chúng tôi chọn ruff đơn lẻ, **không** thêm `mypy`; type hint\n  vẫn giữ theo quy ước hiện có chứ chưa bị kiểm tra kiểu tự động.\n- **Loại test đang có** (bằng chứng: `code-quality-assessment.md` §3.1, `pytest.ini`):\n  - unit — 21 mô-đun, 37 hàm, dùng fixture DataFrame nhỏ trong `tests/conftest.py` (320 dòng);\n  - integration end-to-end — 3 hàm, `@pytest.mark.slow`, chạy toàn pipeline trên `dataset/` thật;\n  - data-quality baseline — 3 hàm, `@pytest.mark.slow`, khẳng định hằng số dị thường trên CSV thật\n    (19.015 mã bưu chính sau gộp, 610 sản phẩm thiếu danh mục, 8.427 outlier giá).\n- **Khối lượng hiện tại**: 25 mô-đun test, 47 hàm test, 6 hàm `slow`. Dưới TDD + yêu cầu test cho mọi\n  module mới + ngưỡng 80%, khối lượng này sẽ tăng đáng kể trong đợt nâng cấp — rủi ro đã ghi ở\n  `evidence.md` mục \"Interview decisions\".\n- **Bộ nhanh và bộ chậm tách bằng marker**, không tách bằng thư mục riêng: `-m \"not slow\"` là bộ nhanh,\n  `-m slow` là bộ cần dữ liệu thật/sinh ra.\n- **Bộ test nhanh hiện chưa hermetic** (`TD-09`): 5 test trong `tests/unit/test_dashboard_smoke.py` và\n  `tests/unit/test_cli.py::test_main_analyze_stage` gọi `load_config()` của repo, nên cần\n  `warehouse/olist.duckdb` và `data/marts/` đã tồn tại — hai thư mục bị `.gitignore`. Trên máy mới clone,\n  bộ \"nhanh\" sẽ đỏ. Phỏng vấn chưa chốt có sửa `TD-09` trong đợt này hay không, nên tạm thời chúng tôi\n  vẫn chấp nhận: bộ nhanh chỉ được coi là xanh trên máy đã chạy `--stage all` ít nhất một lần.\n- **Test là chốt hồi quy dữ liệu, không chỉ chốt mã.** Mọi thay đổi cleaning/ghép bản ghi có chủ đích\n  phải cập nhật đồng thời `src/quality/allowlist.py`, `src/integrate/reconcile.py`, `README.md` và test\n  tích hợp — nếu không, chế độ `quality full` và `KpiReconciler` sẽ đỏ (`TD-15`, `TD-02`).\n- **Test áp đặt cả hình dạng UI**: `tests/unit/test_dashboard_smoke.py` khẳng định 3 tab, 2 callback,\n  9 output; `tests/integration/test_u3_end_to_end.py` khẳng định lại 2 callback. Thêm tab \"Tích hợp\"\n  là thay đổi có chủ đích, phải sửa test trong cùng thay đổi (§7.1 của `code-quality-assessment.md`)."
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
  "input_sha256": "sha256:92d6ca72d976e45ea44b682da48c3cdb183308d3258ad377db6e027165ec25c4",
  "contract_sha256": "sha256:1a431764a66e871bea7d3cc1cb9f106951561be21dd44470a8dd7cd6e8fa10d5"
}
```

## Kế hoạch thực hiện (TDD, Standard)

Lớp áp dụng: **giao diện (frontend behavior)** theo `plan_profile`. Ba lớp dữ liệu/truy cập/nghiệp vụ đã thuộc các đơn vị khác; U6 chỉ đọc hợp đồng và vẽ.

### Bước 0 — Chuẩn bị

- [x] 1. Cài `dash-mantine-components` vào `.venv`, đọc phiên bản thực (`pip show`), ghim đúng số đó vào `requirements.txt`; sửa câu "không thêm thư viện UI mới" trong `functional-spec.md` thành "không thêm ngoài DMC".
- [x] 2. Giữ `card_ids` trong `TabConfig` (`src/integration/card.py`) — đã có từ C9 — thêm `result_region_ids`, bỏ `result_block_ids`; cập nhật `config/integration-tab.yaml` và năm test của `test_integration_card.py`.

### Bước 1 — Runner

- [x] 3. Ghi lệnh chạy vào `unit-test-instructions.md`: `.venv\Scripts\python.exe -X utf8 -m pytest tests/unit/test_integration_tab.py tests/unit/test_dashboard_smoke.py`.

### Bước 2 — Khung tab (frontend Red/Green/Refactor)

- [x] 4. **Red** — test cho `build_layout`: bốn tab, tab "Tích hợp" có bốn thẻ với `data-state="rong"`, bốn màn hình chi tiết ẩn, tổng **8** callback; dựng layout khi C5/C6/C7 đều vắng vẫn xanh (SR-U6-8).
- [x] 5. **Green** — `src/integration/tab.py` với `IntegrationTab`, `OverviewScreen`, `DetailScreen`, `StateBlock`; `app.py` dựng tab mới, giữ hai callback cũ.
- [x] 6. **Refactor** — tách hàm dựng mỗi thẻ.

### Bước 3 — Sáu callback (gồm callback của vùng kết quả)

- [x] 7. **Red** — test: `load_overview` điền hai dòng số liệu bốn thẻ; `route` đổi màn hình và giữ trạng thái; `reload` không đọc lại khi không bấm; lỗi hợp đồng chỉ hỏng màn hình của nó; mỗi callback một Output riêng.
- [x] 8. **Green** — cài **sáu** callback (thêm callback của vùng kết quả `don-theo-thang`), mỗi callback bắt lỗi của hợp đồng mình dùng.
- [x] 9. **Refactor** — gom phần dựng bảng dùng chung.

### Bước 4 — Bốn màn hình chi tiết

- [x] 10. **Red** — test: `schema` có ba cột ánh xạ + nhãn `GAV`; `queries` có hai bản SQL, kế hoạch, bảng kết quả, `kpi_definitions` kèm `revenue_definition`, trạng thái chạy; `linkage` có ngưỡng 0,85, tỉ lệ đúng kèm mẫu số, dòng "Bỏ qua", chuyển khách/người bán; `sources` có bảng nguồn và lý do.
- [x] 11. **Green** — cài bốn panel; `run_query` gọi U5 rồi U3; `suggest_source` gọi U5.
- [x] 12. **Refactor** — chạy lại toàn bộ bộ nhanh.

### Bước 5 — CI và tài liệu

- [x] 13. `ci.yml`: thêm `src/dashboard/app.py`, `src/integration/tab.py`, `tests/unit/test_integration_tab.py` vào danh sách `ruff format --check`.
- [ ] 14. Viết `code-summary.md` (kèm rà WCAG 2.1 AA và số đo callback) và `source-manifest.json`.
- [ ] 15. Chạy `aidlc engine sensor-traceability --stage code-generation ...` và điền `traceability.json`.

## Truy vết câu chuyện → bước

| Câu chuyện / quy tắc | Bước |
|---|---|
| US5.1 (AC5.1.1–AC5.1.3) | 4–6 |
| US5.2 (AC5.2.1–AC5.2.4) | 7–9 |
| US5.3 (AC5.3.1–AC5.3.3) | 10–12 |
| US1.1–US1.2, US2.1–US2.2, US3.1–US3.3, US4.1–US4.2 | 10–11 |
| BR6.1–BR6.12 | 4–12 |
| NFR1.x, NFR4.1, NFR5.1/NFR5.2, NFR3.1 | 13–14 |

## Rủi ro

| # | Rủi ro | Cách xử lý |
|---|---|---|
| R1 | Hai callback cùng Output làm Dash không khởi động | Mỗi callback một `Output` riêng; test khẳng định |
| R2 | DMC không tương thích `dash==4.4.1` | Cài trong `.venv`, chạy thử dựng layout trước khi ghim |
| R3 | Đổi `card_ids` làm đỏ năm test cũ | Sửa cùng thay đổi |
| R4 | Layout đọc hợp đồng lúc dựng | Chỉ `load_overview` đọc; test dựng layout khi hợp đồng vắng |
