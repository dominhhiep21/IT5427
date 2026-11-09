# Code Generation Plan — u5-source-selector

## Summary

- Builds: bộ chọn nguồn dữ liệu — nạp hồ sơ ba nguồn từ tệp cấu hình, dựng danh mục, xếp hạng và chọn nguồn cho một truy vấn, kèm lý do chọn/loại bằng chữ; hai payload C3 (cho U3) và C7 (cho U6)
- Touches: `src/integration/selector.py` (mới), `src/integration/models.py`, `src/common/exceptions.py`, `src/config.py`, `config.yaml`, `config/integration-sources.yaml` (mới), `tests/unit/test_integration_selector.py` (mới), `.github/workflows/ci.yml`
- Tests: 1 tệp test mới, 20–26 hàm test đơn vị (TDD); không thêm test tích hợp

## Nguồn vào

| Tài liệu | Dùng để |
|---|---|
| `construction/u5-source-selector/functional-design/functional-spec.md` | W1–W4, máy trạng thái, ba truy vấn mẫu và trường cần |
| `construction/u5-source-selector/functional-design/rules.md` | BR5.1–BR5.11 |
| `construction/u5-source-selector/functional-design/entities.md` | Bốn kiểu dữ liệu, bề mặt lỗi, ràng buộc |
| `construction/u5-source-selector/nfr-requirements/security-requirements.md` | SR-U5-1..16, bảng ánh xạ lỗi §1.1, ánh xạ `error_code` §1.2 |
| `construction/u5-source-selector/nfr-requirements/tech-stack-decisions.md` | TS-U5-1..15, NFR1.1–NFR6.2 |
| `construction/u5-source-selector/nfr-design/security-design.md` | ADR-U5-S1..S8 |
| `construction/u5-source-selector/nfr-design/logical-components.md` | L1–L5, phạm vi hỏng |
| `construction/u5-source-selector/infrastructure-design/cicd-pipeline.md` | Cổng xác nhận §4, thay đổi CI §2 |
| `inception/contract-design/contract-summary.md` | C2 (đầu vào), C3 và C7 (đầu ra, các trường cộng thêm 2026-11-08) |
| `inception/units-generation/unit-of-work.md` | Biên giới U5: không sinh SQL, không gọi mạng |
| `inception/requirements-analysis/requirements.md` | FR2.1, FR4.1–FR4.3, NFR1–NFR6 |

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

Ba lớp chạy được áp dụng: **mô hình dữ liệu**, **truy cập dữ liệu (đọc và kiểm tệp cấu hình)**, **logic nghiệp vụ (xếp hạng và chọn nguồn)**. Hai lớp **API/endpoint** và **giao diện** không áp dụng — đơn vị này không có endpoint và không render gì (`unit-of-work.md` §U5, `functional-spec.md` "Không nằm trong đơn vị này").

### Bước 0 — Cấu trúc dự án và cấu hình sẵn sàng

- [x] 1. Xác nhận khung hiện có: `src/integration/models.py` (C1/C2/C6), `src/common/exceptions.py` (`PipelineError` và các lớp con), `src/config.py` (`AppConfig`, `mediated_schema_path`), `src/integration/schema.py` (`SOURCE_TABLES`, `MediatedSchemaView`, `build_field_catalogue`). Không tạo gói mới (TS-U5-1).
- [x] 2. Thêm `NoSourceAvailableError(PipelineError)` vào `src/common/exceptions.py` (TS-U5-7).
- [x] 3. Thêm `integration_sources_path` vào `AppConfig` trong `src/config.py` và khoá tương ứng vào `config.yaml`, theo mẫu `mediated_schema_path`; đường dẫn được phân giải tuyệt đối một lần như các trường khác (R-07, SR-U5-2).

### Bước 1 — Xác nhận runner và lệnh chạy của đơn vị

- [x] 4. Xác nhận `pytest.ini` + `pytest-cov` sẵn có; ghi đúng lệnh chạy của đơn vị vào `unit-test-instructions.md`: `.venv\Scripts\python.exe -X utf8 -m pytest tests/unit/test_integration_selector.py`.

### Bước 2 — Lớp mô hình dữ liệu

- [x] 5. **Red** — viết test thất bại cho bốn kiểu mới: `SourceProfile` (tám trường, `frozen=True`), `SourceChoice` (`reason` bắt buộc), `SourceCatalogue` (`sources`, `choices`, `query_fields`, `partial_reason`, `pending_query_id`; không có `generated_at`), `SourceSelection` (`catalogue` bắt buộc). Ghi lại đầu ra đỏ.
- [x] 6. **Green** — thêm bốn kiểu vào `src/integration/models.py` (TS-U5-8); danh sách là `tuple`, không `dict`.
- [x] 7. **Refactor** — docstring một dòng theo quy ước repo; giữ nguyên các kiểu C1/C2/C6 đang có.

### Bước 3 — Lớp truy cập dữ liệu: đọc và kiểm tệp cấu hình

- [x] 8. **Red** — test thất bại cho L1/L2: tệp thiếu → `ConfigurationError`; khoá thiếu/sai kiểu (`has_data: "false"`, `latency_ms: "800"`, `latency_ms: -1`, `cost_level: 9`) → `ConfigurationError`; `source_name` lạ/trùng → `SchemaError`; số nguồn mô phỏng khác 1 → `SchemaError`; mã trường lạ trong `covered_fields` **và trong ánh xạ truy vấn** → `SchemaError`; `tables` ngoài `SOURCE_TABLES` → `SchemaError`; `tables` rỗng mà `covered_fields` khác rỗng → `ConfigurationError`; ánh xạ truy vấn khác ba `query_id` của FR2.1 → `SchemaError`. Ghi lại đầu ra đỏ.
- [x] 9. **Green** — cài `load_source_catalogue(path, field_catalogue, pending_query_id=None, logger=None)` (TS-U5-11, TS-U5-13): `safe_load`, kiểm kiểu (ADR-U5-S7), `SOURCE_TABLES` (ADR-U5-S2), dựng `SourceProfile` + câu `coverage`, mang `query_fields`, đặt `partial_reason`/`pending_query_id` (BR5.9).
- [x] 10. **Refactor** — tách các hàm kiểm thuần (`_checked_profile`, `_checked_tables`, `_checked_query_fields`) cho dễ đọc; không đổi chữ ký công khai.

### Bước 4 — Lớp logic nghiệp vụ: xếp hạng và chọn nguồn

- [x] 11. **Red** — test thất bại cho L3: vị từ ứng viên loại nguồn mô phỏng (BR5.11) và nguồn không có dữ liệu; xếp hạng theo `(cost_level, latency_ms, source_name)` và tất định khi đảo thứ tự khai báo (BR5.4, SR-U5-12); kết quả kỳ vọng cho ba truy vấn mẫu đều là `olist_csv`; sáu nhánh lý do loại theo thứ tự ưu tiên (BR5.5); nhánh không nguồn nào đủ trường ném `NoSourceAvailableError` mang `missing_fields` **và** `catalogue` (BR5.6, ADR-U5-S4); `select_source` trả `SourceSelection` mang `catalogue` mới và xoá `partial_reason`/`pending_query_id` (BR5.9, W2 bước 8); `tables` của nguồn thắng lấy nguyên từ hồ sơ (R-01).
- [x] 12. **Green** — cài `select_source(catalogue, query_id, logger=None)`; đọc `required_fields` từ `catalogue.query_fields` (ADR-U5-S8).
- [x] 13. **Refactor** — tách hàm dựng `SourceChoice` cho mỗi nguồn; chạy lại toàn bộ bộ nhanh.

### Bước 5 — Dữ liệu cấu hình thật

- [x] 14. Viết `config/integration-sources.yaml` với đúng ba nguồn của BR5.2 (`olist_csv` 3/800, `ibge_cache` 2/200 với `tables: []`, `partner_simulated` 1/50 `is_simulated: true`) và ba ánh xạ truy vấn của `functional-spec.md` W2.
- [x] 15. Thêm test đọc **chính tệp cấu hình đang phát hành** và khẳng định nạp được, ba nguồn, ba truy vấn (cổng smoke của `cicd-pipeline.md` §4 bước 6).

### Bước 6 — Cấu hình môi trường và build

- [x] 16. `.github/workflows/ci.yml`: thêm `tests/unit/test_integration_selector.py` vào danh sách `ruff format --check`; thêm bước đo phủ toàn bộ `python -X utf8 -m pytest --cov=src --cov-fail-under=80`; thêm bước smoke nạp `config/integration-sources.yaml` bằng `python -X utf8 -c "..."` (dùng Python của runner, không `.venv`). Không sửa `requirements.txt`, `stages.py`, `micro_batch`.

### Bước 7 — Tài liệu và truy vết

- [ ] 17. Viết `code-summary.md` (tệp đã tạo/sửa, quyết định, độ phủ, đầu ra đỏ, test viết nhưng chưa chạy) và `source-manifest.json`.
- [ ] 18. Chạy `aidlc engine sensor-traceability --stage code-generation ...` và điền `traceability.json`: mỗi `OK` trỏ tới một tệp có thật; FR1.3/FR1.4 và AC4.1.1 vẫn `Deferred`/`N/A` sang `u6-integration-ui` như thiết kế chức năng đã chốt.

## Truy vết câu chuyện → bước

| Câu chuyện / quy tắc | Bước |
|---|---|
| US4.1 — bảng nguồn ứng viên (AC4.1.2, AC4.1.3; AC4.1.1 do U6 hiển thị) | 3, 5–10 |
| US4.2 — đề xuất nguồn cho một truy vấn (AC4.2.1, AC4.2.2) | 8–13 |
| FR4.1, FR4.2, FR4.3 | 5–15 |
| FR2.1 (ba truy vấn mẫu) | 8, 11, 14 |
| BR5.1–BR5.11 | 8–13 |
| NFR1.1 (≤ 2 giây), SR-U5-12 | 11 |
| NFR2.2 (test riêng), NFR3.1 (ruff) | 4, 16 |
| NFR6.1 (không mạng) | 8–13 |
| NFR5.1/NFR5.2 (không hồi quy) | 16–18 |

## Rủi ro và cách xử lý

| # | Rủi ro | Cách xử lý |
|---|---|---|
| R1 | Thêm `integration_sources_path` vào `AppConfig` làm đỏ test cấu hình hiện có | Trường có giá trị suy ra từ `config.yaml` như `mediated_schema_path`; chạy lại toàn bộ bộ nhanh sau bước 3 |
| R2 | `SOURCE_TABLES` nhập từ `schema.py` gây vòng import | `selector.py` import `SOURCE_TABLES` từ `src/integration/schema.py`; `schema.py` không import `selector.py`, nên không có vòng |
| R3 | Chuỗi `coverage` không tất định nếu dựng từ `dict` | Dựng từ `tuple` theo thứ tự khai báo; test khẳng định giá trị chính xác (SR-U5-12) |
| R4 | Bước smoke trong CI dùng `.venv` (không tồn tại trên runner) | Bước CI dùng `python` của runner; bước local dùng `.venv\Scripts\python.exe` (`cicd-pipeline.md` §2) |
