# Code Generation Plan — u3-query-rewriter

## Summary

- Builds: ba truy vấn mẫu viết lại từ lược đồ trung gian sang SQL nguồn, kế hoạch từng bước, đối chiếu KPI với `src/analytics`, và sổ KPI dùng chung
- Touches: `src/integration/rewrite.py` (mới), `src/integration/models.py`, `src/common/kpis.py` (mới), `src/common/exceptions.py`, `src/integration/card.py`, `src/dashboard/app.py`, `config/integration-tab.yaml`, `config/mediated-schema.yaml`, `config/integration-sources.yaml`, `tests/unit/test_integration_rewrite.py` (mới), `tests/unit/test_common_kpis.py` (mới), ba test hiện có của U1/U3 cũ, `.github/workflows/ci.yml`
- Tests: 2 tệp test mới, khoảng 30 hàm test (TDD); không thêm test tích hợp

## Nguồn vào

Thiết kế chức năng, NFR requirements, NFR design và Infrastructure design của `construction/u3-query-rewriter/`; `inception/contract-design/contract-summary.md` (C1, C3, C4 — các trường cộng thêm 2026-11-08); `inception/units-generation/unit-of-work.md` §U3; `inception/requirements-analysis/requirements.md` (FR2.1–FR2.5, FR6.1–FR6.2).

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

Ba lớp áp dụng: **mô hình dữ liệu**, **truy cập dữ liệu (nạp CSV + DuckDB trong bộ nhớ)**, **logic nghiệp vụ (viết lại + đối chiếu)**. Không có endpoint, không tự render.

### Bước 0 — Chuẩn bị

- [x] 1. Thêm `KpiMismatchError(PipelineError)` (mang `groups: tuple[tuple[str, str, float], ...]` = `(kpi_id, group_key, delta)`) vào `src/common/exceptions.py`.
- [x] 2. Bổ sung lược đồ: thêm `mat_hang.gia_van_chuyen`, `don_hang.ngay_giao_thuc_te`, `don_hang.ngay_giao_du_kien`; xác nhận `don_hang.bang_giao` và `san_pham.ten_danh_muc` đã `loaded: true` (chỉ thêm trường mới nếu thiếu); cập nhật `config/integration-sources.yaml` và test U2 tương ứng.

### Bước 1 — Runner

- [x] 3. Ghi lệnh chạy vào `unit-test-instructions.md`: `.venv\Scripts\python.exe -X utf8 -m pytest tests/unit/test_integration_rewrite.py tests/unit/test_common_kpis.py`.

### Bước 2 — Mô hình dữ liệu

- [x] 4. **Red** — test cho `QueryTemplate`, `RewriteStep`, `KpiComparison` (thêm `group_key`, `delta`), `QueryRunResult` (thêm `total_orders`, `months`, `partial`).
- [x] 5. **Green** — thêm/ sửa các kiểu trong `src/integration/models.py`.
- [x] 6. **Refactor** — docstring một dòng.

### Bước 3 — Truy cập dữ liệu

- [x] 7. **Red** — test nạp: `duckdb.connect()` trong bộ nhớ, `register()` khung dữ liệu từ CSV, ngày parse đúng; thiếu tệp → `QueryExecutionError`; cột không có trong tiêu đề → `SchemaError`.
- [x] 8. **Green** — cài hàm nạp trong `src/integration/rewrite.py`.
- [x] 9. **Refactor** — tách hàm nạp theo bảng.

### Bước 4 — Logic nghiệp vụ

- [x] 10. **Red** — test ba mẫu: SQL đúng, kế hoạch 3/2/2 bước, tham số chứa `'`/`;` không lỗi, `elapsed_ms`/`load_ms`, `integration.query.slow`.
- [x] 11. **Red** — test đối chiếu: từng nhóm, `__all__`, dung sai 0,01/0/0,01, lệch 0,02 → `KpiMismatchError`, nhóm thiếu → `partial`.
- [x] 12. **Green** — cài `run_template`, `latest_sql`, đối chiếu; `src/common/kpis.py` với ba KPI.
- [x] 13. **Refactor** — chạy lại toàn bộ bộ nhanh.

### Bước 5 — Đăng ký tab và dọn đường cũ

- [x] 14. Thêm ba vùng bên cạnh `don-theo-thang` trong `config/integration-tab.yaml` (`result_region_ids`); sửa `src/integration/card.py`, `src/dashboard/app.py` (callback của vùng kết quả), và ba test `test_integration_query.py`, `test_integration_card.py`, `test_dashboard_smoke.py`.

### Bước 6 — CI và tài liệu

- [x] 15. `.github/workflows/ci.yml`: thêm `src/common/kpis.py`, `src/common/exceptions.py`, `tests/unit/test_integration_rewrite.py`, `tests/unit/test_common_kpis.py` vào danh sách `ruff format --check`.
- [ ] 16. Viết `code-summary.md`, `source-manifest.json`.
- [ ] 17. Chạy `aidlc engine sensor-traceability --stage code-generation ...` và điền `traceability.json`.

## Truy vết câu chuyện → bước

| Câu chuyện / quy tắc | Bước |
|---|---|
| US2.1 (AC2.1.1, AC2.1.3) | 10, 12 |
| US2.2 (AC2.2.1–AC2.2.3) | 4, 5, 10 |
| US2.3 (AC2.3.1–AC2.3.2) | 11, 12 |
| US6.2 (AC6.2.1–AC6.2.2) | 12 |
| FR2.1–FR2.5, FR6.1 | 4–14 |
| BR3.1–BR3.12 | 7–14 |
| NFR1.1, NFR2.2, NFR3.1 | 3, 10, 15 |

## Rủi ro

| # | Rủi ro | Cách xử lý |
|---|---|---|
| R1 | Thêm vùng làm đỏ test hình dạng dashboard | Sửa cùng thay đổi, không để lại test đỏ |
| R2 | Thêm trường lược đồ làm đỏ test U2 | Cập nhật test U2 trong cùng thay đổi |
| R3 | Nạp CSV mỗi lần chạy chậm | Đo `load_ms`, chỉ đọc cột cần; ghi số thật vào `code-summary.md` |
| R4 | Dung sai ba nguồn ba số | Chỉ dùng hằng 0,01 / 0 / 0,01 đã chốt ở ADR-U3-S3 và C4 |
