# Code Generation Plan — u4-record-linkage

## Summary

- Builds: ghép bản ghi khách/người bán bằng hai bằng chứng (địa lý + hành vi mua), ngưỡng 0,85, ghi hai tệp JSON theo C5.
- Touches: `src/linkage/` (mới), `src/pipeline/stages.py` (gọi một lần), `config.yaml` + `src/config.py` (`paths.integration_dir`), `.github/workflows/ci.yml` (mở rộng phạm vi định dạng), `tests/unit/` (4 tệp mới).
- Tests: 4 tệp unit mới theo TDD (khoảng 28–34 test), gồm một test hiệu năng riêng cho phần chấm điểm.

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

## Phạm vi và nguồn

Đơn vị `u4-record-linkage` theo `unit-of-work.md` §U4: ghép khách hàng và người bán bằng khoá chặn và điểm tương đồng ở ngưỡng 0,85; ghi cặp ghép, cặp xem lại, cặp bị bỏ qua kèm lý do. Thiết kế đã chốt ở `functional-spec.md` (Workflow 1–4), `rules.md` (BR4.1–BR4.10), `entities.md`, `security-design.md` (ADR-U4-S1..S4), `logical-components.md` (L1–L5), `performance-requirements.md` (NFR1.1–NFR6.1) và `contract-summary.md` C5.

| Lớp | Áp dụng? | Ghi chú |
|---|---|---|
| Data model / database behavior | Có | `BlockingRule`, `MatchPair`, `SkippedPair`, `LinkageResult`, chuẩn hoá thành phố |
| Repository / data access | Có | Dựng chỉ mục bằng chứng từ 4 bảng nguồn, kiểm cột, xử lý thiếu đơn |
| Business logic | Có | Chặn, chấm điểm, ngưỡng, tổng hợp, trần, `correct_rate` |
| API / endpoint | **Không** | không có HTTP API; đầu vào là lời gọi từ pipeline |
| Frontend behavior | **Không** | đơn vị không hiển thị gì; U6 đọc tệp |

Ba lớp N/A được đánh dấu N/A trong kế hoạch thay vì bịa ra tệp.

## Truy vết câu chuyện → bước

| Câu chuyện / yêu cầu | Nội dung | Bước |
|---|---|---|
| AC3.1.1 / FR3.1 | Số cặp vượt ngưỡng, số nhóm trùng, ngưỡng 0,85 | 9–11 |
| AC3.1.2 / FR3.1 | Hai đối tượng, hai tệp | 6–8, 9–11 |
| AC3.2.1 / FR3.2 | Điểm và quyết định trên bảng cặp | 9–11 |
| AC3.2.2 / FR3.2 | Đúng bằng ngưỡng là "Xem lại" | 3–5, 9–11 |
| AC3.2.3 / FR3.3 | `correct_rate` theo `customer_unique_id`, kèm cỡ mẫu | 9–11 |
| AC3.3.1 / FR3.4 | Cặp bị bỏ qua và lý do | 6–8 |
| AC3.3.2 / FR3.4 | `skipped` luôn có mặt | 3–5, 9–11 |
| NFR1.1, NFR1.2 | ≤ 60 giây cho cả lượt; tệp ≤ 5 MB (cả `pairs` lẫn `skipped`) | 9–11, 15 (test hiệu năng) |
| NFR2.1, NFR2.2, NFR3.1 | Phủ ≥ 80%, test riêng, ruff sạch | mọi bước; 18 |
| NFR5.1, NFR5.2 | Không chạm mart/view | 18 |
| NFR6.1 | Không mạng, không cổng | 1, 18 |
| C5 | Payload tệp kết quả | 3–5, 9–11 |

## Steps

### Bước 1 — Khung gói và cấu hình

- [x] Tạo `src/linkage/__init__.py`.
- [x] Thêm `paths.integration_dir: data/integration` vào `config.yaml`; thêm `integration_dir` vào `AppConfig` và đọc khoá đó trong `load_config` (cùng kiểu `_resolve` như các đường dẫn khác).

### Bước 2 — Xác nhận runner

- [x] Chạy `.venv\Scripts\python.exe -X utf8 -m pytest --version`; xác nhận `pytest.ini` có `testpaths` và marker `slow`.
- [x] Ghi lệnh unit-scoped vào `unit-test-instructions.md` và chạy thử.

### Bước 3 — Data model, Red

- [x] `tests/unit/test_linkage_models.py`: `normalize_city` bỏ dấu và gộp khoảng trắng; `MatchPair` từ chối `record_a >= record_b`; `decision` chỉ nhận `Ghép`/`Xem lại`; `LinkageResult` dựng được với `summary` rỗng và `skipped` rỗng; `score` ghi 4 chữ số.
- [x] Chạy lệnh, ghi đầu ra đỏ.

### Bước 4 — Data model, Green

- [x] `src/linkage/models.py`: `BlockingRule`, `MatchPair`, `SkippedPair`, `LinkageResult`, `normalize_city`, hằng số `THRESHOLD = 0.85`, `GEO_WEIGHT = 0.40`, `ORDER_WEIGHT = 0.60`, `MAX_PAIRS = 10_000`.
- [x] Chạy lại lệnh, xanh.

### Bước 5 — Data model, Refactor

- [x] Gom tập trạng thái và trọng số vào một chỗ; chạy `ruff check` trên tệp mới; chạy lại lệnh, xanh.

### Bước 6 — Repository / data access, Red

- [x] `tests/unit/test_linkage_index.py`: dựng chỉ mục từ CSV nhỏ trong `tmp_path`; cột thiếu → `SchemaError` nêu tên; khách không có đơn → entry vẫn tồn tại với tập sản phẩm rỗng; mã bưu chính mất số 0 đầu được giữ; `payment_value` gom theo đơn.
- [x] Chạy lệnh, ghi đầu ra đỏ.

### Bước 7 — Repository / data access, Green

- [x] `src/linkage/index.py`: `build_index(config, target)` đọc đủ bộ cột của `TableSpec` rồi chọn cột con; dựng `dict[id → Evidence]`; đếm `records_missing_match_fields`.
- [x] Chạy lại lệnh, xanh.

### Bước 8 — Repository / data access, Refactor

- [x] Tách hàm thuần `evidence_for(frame_orders, frame_items, frame_payments)` để test không cần đĩa; chạy lại lệnh, xanh.

### Bước 9 — Business logic, Red

- [x] `tests/unit/test_linkage_score.py`: chặn 5 chữ số (hai bản ghi khác nhóm không sinh cặp); cặp bị bỏ qua khi thiếu đơn hoặc thiếu city; `score = 0.4·geo + 0.6·order`; `> 0,85` là Ghép, đúng 0,85 là Xem lại, `< 0,85` không ghi; `pairs_scored`/`pairs_matched`/`pairs_review`/`pairs_skipped` đúng; `duplicate_groups`; `correct_rate` + `correct_rate_sample`; trần 10.000 cặp đặt `pairs_truncated` và `pairs_total`; test hiệu năng: 200.000 cặp tổng hợp chấm dưới 60 giây.
- [x] Chạy lệnh, ghi đầu ra đỏ.

### Bước 10 — Business logic, Green

- [x] `src/linkage/score.py`: `score_pairs(index, rule)`, `decide(score)`, `summarise(...)`, `cap(...)`.
- [x] Chạy lại lệnh, xanh.

### Bước 11 — Business logic, Refactor

- [x] Tách `SequenceMatcher` ra sau một hàm nhỏ để thay được bằng test; chạy lại lệnh, xanh.

### Bước 12 — API / endpoint

- [x] **N/A** — không có HTTP API.

### Bước 13 — (N/A, xem bước 12)

- [x] **N/A**.

### Bước 14 — (N/A, xem bước 12)

- [x] **N/A**.

### Bước 15 — Frontend / ghi kết quả (thay cho lớp Frontend)

- [x] `tests/unit/test_linkage_result.py`: ghi tệp bằng `AtomicWriter` vào `tmp_path`; đọc lại thấy `summary` và `len(pairs) == min(pairs_total, 10_000)`; tệp không chứa `customer_unique_id`; `skipped` rỗng vẫn có mặt; lỗi đọc lại → ném lỗi.
- [x] Chạy lệnh, ghi đầu ra đỏ.

### Bước 16 — Ghi kết quả, Green

- [x] `src/linkage/result.py`: `write_result(config, result)` dùng `AtomicWriter.write_json` rồi đọc lại kiểm; `src/pipeline/stages.py` gọi một lần trong `run_all` (sau `integrate`) và trong `run_stage("integrate")`, mỗi đối tượng độc lập, ghi ba sự kiện `integration.linkage.*`.
- [x] Chạy lại lệnh, xanh.

### Bước 17 — Refactor

- [x] Dồn chuỗi sự kiện/số đếm vào một chỗ; chạy `ruff check` + `ruff format --check` trên `src/linkage` và các test mới.

### Bước 18 — Cấu hình môi trường và build

- [x] Mở rộng phạm vi `ruff format --check` trong `.github/workflows/ci.yml` cho `src/linkage` và các test mới của đơn vị.
- [x] Thêm một dòng vào `README.md` (mục dữ liệu sinh ra) nêu hai tệp `data/integration/linkage-*.json` và cách sinh lại; thêm một dòng vào `docs/runbook.md` (sự cố tệp kết quả cũ) nói chạy lại `--stage all`.
- [x] Không thêm gói nào vào `requirements.txt`.

### Bước 19 — Tài liệu và truy vết

- [x] `code-summary.md` và `source-manifest.json` do orchestrator viết sau khi xong — không tạo ở bước này; báo lại danh sách tệp đã tạo/sửa.

## Ngoài phạm vi

| Không làm | Vì sao |
|---|---|
| Hiển thị bảng cặp, màn hình D | Thuộc U6 |
| Học ngưỡng, đổi trọng số theo dữ liệu | Ngưỡng và trọng số là hằng số đã chốt |
| Sửa `requirements.txt` | Không thêm thư viện (TS-U4-7) |
| Sửa `inception/*` (FR3, AC3.2.3, mockup) | Thay đổi phạm vi; đã ghi ở `functional-spec.md` §Hệ quả |
