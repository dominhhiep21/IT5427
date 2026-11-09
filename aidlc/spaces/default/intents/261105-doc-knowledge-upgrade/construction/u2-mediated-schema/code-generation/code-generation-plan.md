# Code Generation Plan — u2-mediated-schema

## Summary

- Builds: bộ nạp và kiểm lược đồ trung gian **nạp và kiểm lược đồ ba thực thể do U1 bàn giao** theo C8, kèm kiểm tiêu đề nguồn, kênh "một phần", đo thời lượng, và hai hợp đồng C1/C2
- Touches: `src/integration/schema.py`, `src/integration/models.py`, `tests/unit/test_integration_schema.py` (mới), `.github/workflows/ci.yml`
- Tests: 1 tệp test mới, khoảng 22-26 hàm test đơn vị (TDD), không thêm test tích hợp

## Nguồn vào

| Tài liệu | Dùng để |
|---|---|
| `construction/u2-mediated-schema/functional-design/functional-spec.md` | Workflow 1–4, A1–A2, Q1–Q2 |
| `construction/u2-mediated-schema/functional-design/rules.md` | BR2.1–BR2.9 |
| `construction/u2-mediated-schema/functional-design/entities.md` | Bốn kiểu dữ liệu và ràng buộc |
| `inception/contract-design/contract-summary.md` | C1, C2, C6, C8 (đã cộng thêm `ConfigurationError`, `elapsed_ms`, `partial`) |
| `construction/u2-mediated-schema/nfr-design/security-design.md` | ADR-U2-S1..S6 |
| `construction/u2-mediated-schema/nfr-design/logical-components.md` | L1–L6, phạm vi hỏng |
| `construction/u2-mediated-schema/infrastructure-design/cicd-pipeline.md` | G2: danh sách format của `ci.yml` |
| `inception/units-generation/unit-of-work.md` | Biên giới U2: không sinh SQL, không gọi DuckDB, không hiển thị |
| `inception/requirements-analysis/requirements.md` | FR1.1–FR1.4, NFR1–NFR6 |

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

Bốn lớp chạy được áp dụng: **mô hình dữ liệu**, **truy cập dữ liệu (tiêu đề CSV)**, **logic nghiệp vụ**
(kiểm + dựng view). Hai lớp **API/endpoint** và **giao diện** không áp dụng — đơn vị này không có endpoint
và không hiển thị gì (`unit-of-work.md` §U2, `functional-spec.md` "Không nằm trong đơn vị này").

### Bước 0 — Cấu trúc dự án và cấu hình sẵn sàng

- [x] 1. Xác nhận khung hiện có: `src/integration/schema.py` (bản một thực thể của U1), `src/integration/models.py`, `src/common/exceptions.py` (`SchemaError`, `ConfigurationError`), `src/common/logging.py` (`Logger`, `NullLogger`, `ERROR_CODES`, `normalise_error_code`), `src/ingest/schemas.py` (`TABLE_SPECS`). Không tạo gói mới (TS-U2-1).

### Bước 1 — Xác nhận runner và lệnh chạy của đơn vị

- [x] 2. Xác nhận `pytest.ini` + `pytest-cov` sẵn có; ghi đúng lệnh chạy của đơn vị vào `unit-test-instructions.md`: `.venv\Scripts\python.exe -X utf8 -m pytest tests/unit/test_integration_schema.py`.

### Bước 2 — Lớp mô hình dữ liệu

- [x] 3. **Red** — viết test thất bại cho kiểu dữ liệu mới trong `tests/unit/test_integration_schema.py`: `MediatedSchemaView` có `elapsed_ms: int` và `partial: tuple[PartialEntity, ...]`; `MediatedFieldCatalogue` có `fields_by_entity`; `PartialEntity` giữ `name` + `reason`; tất cả là dataclass bất biến (`frozen=True`). Ghi lại đầu ra đỏ.
- [x] 4. **Green** — thêm ba kiểu vào `src/integration/models.py` (TS-U2-5); `tuples` giữ thứ tự, không `dict` cho danh sách trường (TS-U2-8).
- [x] 5. **Refactor** — dọn chú thích một dòng theo quy ước repo; giữ nguyên `MediatedSchema`, `EntityMapping`, `FieldMapping` đang dùng.

### Bước 3 — Lớp truy cập dữ liệu: kiểm tiêu đề nguồn

- [x] 6. **Red** — test thất bại cho L3: đọc đúng dòng đầu tệp CSV bằng `csv.reader` với `utf-8-sig`; cột có thật → qua; cột không có trong tiêu đề → `SchemaError` nêu `field_name` và `source_column`; tệp CSV nguồn không có → `ConfigurationError`; tệp không đọc được (mã hoá hỏng) → `SchemaError`; **không** đọc dòng dữ liệu (test dùng tệp có dòng dữ liệu sai kiểu mà nạp vẫn thành công).
- [x] 7. **Green** — cài L3 trong `schema.py` (TS-U2-3, ADR-U2-S3, SR-U2-6).
- [x] 8. **Refactor** — gom việc dựng đường dẫn tệp nguồn vào một hàm nhỏ nhận `csv_dir: Path`, để fixture `tmp_path` dùng được mà không cần `dataset/`.

### Bước 4 — Lớp logic nghiệp vụ: chuỗi kiểm và dựng view

- [x] 9. **Red** — test thất bại cho L1/L2/L4:
  - BR2.1: thiếu một thực thể → view vẫn trả, `partial` nêu tên thực thể thiếu và lý do; đủ ba → `partial` rỗng
  - BR2.2: `source_table` không nằm trong `TABLE_SPECS` → `SchemaError`; cột không có trong tiêu đề → `SchemaError`
  - BR2.3: định danh sai hình dạng (`"Orders";DROP`, `don hang`, `A_B`, 65 ký tự) → `SchemaError`
  - BR2.4: `schema_kind` khác `GAV` → `SchemaError`
  - BR2.5: `data_type` ngoài tập kín → `SchemaError`
  - BR2.6: trùng `field_name` trong một thực thể → `SchemaError`; thứ tự trường giữ theo tệp
  - BR2.7: `fields_by_entity` = `"<entity>.<field>"` đúng thứ tự, không có mục cho thực thể thiếu
  - BR2.8: câu lỗi chứa `field_name` và `source_column`
  - TS-U2-7: `loaded` vắng mặt → `True`; `loaded` không phải bool → `SchemaError`
  - SR-U2-7: gọi nạp không truyền logger → không có dòng log nào
  - SR-U2-11/NFR1.1: `view.elapsed_ms` là số nguyên dương và `<= 2000` trên fixture
- [x] 10. **Green** — cài L1/L2/L4 theo thứ tự cố định của ADR-U2-S1 (định danh trước, mở tệp sau); hàm `load_schema(path, csv_dir, logger=None)` trả `MediatedSchemaView`; hàm dựng catalogue từ view (BR2.7, ADR-U2-S2).
- [x] 11. **Refactor** — tách các hàm kiểm thuần (`_checked_name`, `_parse_field`, …) cho dễ đọc; không đổi chữ ký công khai; chạy lại toàn bộ bộ nhanh.

### Bước 5 — Cấu hình môi trường và build

- [x] 12. Thêm `tests/unit/test_integration_schema.py` vào danh sách `ruff format --check` của `.github/workflows/ci.yml` (G2). Không sửa `requirements.txt`, `stages.py`, `micro_batch`, `config.yaml`.

### Bước 6 — Tài liệu và truy vết

- [x] 13. Viết `code-summary.md` (tệp đã tạo/sửa, quyết định, độ phủ, test viết nhưng chưa chạy) và `source-manifest.json`.
- [x] 14. Chạy `aidlc engine sensor-traceability --stage code-generation ...` và điền `traceability.json`: mỗi `OK` trỏ tới một tệp có thật.

## Truy vết câu chuyện → bước

| Câu chuyện / quy tắc | Bước |
|---|---|
| US1.2 — lược đồ trung gian ba thực thể; AC1.2.x | 3–5, 9–11 |
| US1.3 — ánh xạ trường và kiểm cột nguồn; AC1.3.x | 6–11 |
| FR1.1, FR1.2, FR1.3, FR1.4 | 3–11 |
| BR2.1–BR2.9 | 9–11 |
| NFR1.1 (≤ 2 giây), SR-U2-11 | 9–11 |
| NFR2.2 (test riêng), NFR3.1 (ruff) | 2, 12 |
| NFR6.1 (không mạng) | 6–11 |
| NFR5.1/NFR5.2 (không hồi quy) | 12–14 |

## Rủi ro và cách xử lý

| # | Rủi ro | Cách xử lý |
|---|---|---|
| R1 | Thêm kiểm tiêu đề làm hỏng test U1 đang xanh (`test_load_schema_rejects_a_missing_file`, các test dựng lược đồ trong `tmp_path`) | Giữ `path` là tham số đầu; `csv_dir` có giá trị mặc định suy ra từ `AppConfig` khi không truyền, và test U1 hiện có không đi qua nhánh đọc CSV nếu lược đồ của nó không khai bảng nguồn có thật — kiểm lại bằng cách chạy toàn bộ bộ nhanh ở bước 11 |
| R2 | `elapsed_ms` đo trên fixture gần như luôn 0, nên test ngưỡng 2 giây gần như rỗng nghĩa | Test khẳng định kiểu và cận trên; giá trị thật đo trên `dataset/` ghi vào `elapsed_ms` khi consumer chạy — nêu rõ trong `unit-test-instructions.md`, không tuyên bố đã đo hiệu năng thật |
| R3 | `partial` bị dùng lẫn với lỗi | Chỉ thiếu thực thể mới sinh `partial`; thiếu tệp là `ConfigurationError`, ánh xạ sai là `SchemaError` (Q3 = A, ADR-U2-S4) |
| R4 | Mã cũ chưa sạch `ruff` bị format lây | Chỉ format hai tệp của đơn vị và tệp test mới; không format toàn repo |
