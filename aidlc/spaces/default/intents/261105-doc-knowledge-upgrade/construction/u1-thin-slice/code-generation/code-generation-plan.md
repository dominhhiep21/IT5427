# Code Generation Plan — u1-thin-slice

## Summary

- Builds: lát cắt xuyên suốt — nạp `don_hang` từ CSV, một truy vấn viết lại đếm đơn theo tháng trên DuckDB in-memory, một thẻ trên tab "Tích hợp".
- Touches: `src/integration/` (mới), `config/mediated-schema.yaml` + `config/integration-tab.yaml` (mới), `src/dashboard/app.py` (thêm tab + 1 callback), `tests/unit/` (4 tệp mới + sửa test hình dạng dashboard), `requirements.txt`, `.github/workflows/ci.yml`, `README.md`, `docs/runbook.md`, `CHANGELOG.md`.
- Tests: 4 tệp unit mới (khoảng 32–36 test) theo TDD, cộng cập nhật 2 test hiện có cho hình dạng dashboard trong cùng thay đổi.
- **Revision 2 (2026-11-08):** thêm bước 20–24 để đáp hai phát hiện Major của vòng phản biện `nfr-requirements` — **NFR5.5** (số trên vùng phải khớp một phép tính độc lập từ `dataset/`, sai lệch 0) và **TS-U1-2** (một đường dữ liệu duy nhất: vùng đọc kết quả truy vấn in-memory của chính lần chạy).
- **Revision 3 (2026-11-09):** người làm chọn hướng "nối số của lát cắt vào tab", nên hình dạng dashboard chốt ở **4 tab, 8 callback, 4 thẻ + 1 vùng**; bước 25–30 thi công việc đó (xem mục "Revision 3").

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

Đơn vị `u1-thin-slice` (Bolt 1, lát cắt mỏng) theo `unit-of-work.md` §U1: một thực thể `don_hang` → một truy vấn viết lại → một thẻ trên tab "Tích hợp". Thiết kế đã chốt ở `functional-spec.md` (Workflow 1–3, bảng trạng thái thẻ), `rules.md` (BR1.1–BR1.8), `entities.md` (thực thể + ánh xạ), `performance-design.md`/`security-design.md`/`reliability-design.md`/`observability-design.md`/`logical-components.md` (NFR), `infrastructure-specification.md` (Q1 = C, Q2 = B, Q3 = B) và `contract-summary.md` (C8, C9).

Các lớp áp dụng cho đơn vị này, theo `plan_profile.testable_layers`:

| Lớp | Áp dụng? | Ghi chú |
|---|---|---|
| Data model / database behavior | Có | `DonHang`, tệp lược đồ, kiểm ánh xạ |
| Repository / data access | Có | bộ nạp CSV, thử lại, gắn cờ bản ghi hỏng |
| Business logic | Có | kiểm điều kiện trạng thái, kế hoạch viết lại, truy vấn, tổng + phần thiếu |
| API / endpoint | **Không** | không có HTTP API; đầu vào duy nhất là callback Dash, kiểm ở lớp Frontend. Bước 12–14 vì vậy đánh dấu N/A thay vì bịa ra một endpoint |
| Frontend behavior | Có | thẻ, năm trạng thái, tab mới, callback riêng |

Một điểm phải chốt trước khi viết mã vì hai tài liệu nói khác nhau: `rules.md` BR1.8 (bản cũ) nói trạng thái rỗng hiện "hướng dẫn chạy pipeline", còn `reliability-design.md` ADR-U1-R5 định nghĩa rỗng là "truy vấn chạy được nhưng không có dòng" và đặt nút "Chạy truy vấn". Cách hoà giải dùng trong đơn vị này: trạng thái rỗng hiện **"Chưa chạy truy vấn lần nào" + nút "Chạy truy vấn"** — thống nhất với TS-U1-2 (thẻ đọc kết quả truy vấn in-memory của chính lần chạy, nên chạy pipeline không sinh ra số liệu cho thẻ). BR1.8 và Workflow 3 đã được sửa theo nghĩa này.

## Truy vết câu chuyện → bước

| Câu chuyện / yêu cầu | Nội dung | Bước trong kế hoạch |
|---|---|---|
| US1.1 / FR1.2 | Nạp đơn từ nguồn vào thực thể `don_hang` với kiểm tra | 3–8 |
| US2.1 / FR2.1 | Truy vấn đếm đơn theo tháng tách theo trạng thái | 9–11 |
| US2.2 / FR2.2 | Viết lại truy vấn trung gian thành SQL nguồn | 9–11 |
| US6.1 / FR5.2, FR5.5 | Thẻ trên tab "Tích hợp" với đủ trạng thái | 15–17 |
| NFR5.3 | Cập nhật test hình dạng dashboard trong cùng thay đổi | 15–17 |
| NFR2.1, NFR2.2, NFR3.1 | Phủ ≥ 80%, test riêng từng mô-đun, ruff sạch | mọi bước; cổng ở 18 |
| C8, C9 | Bàn giao tệp lược đồ và tệp cấu hình tab | 1, 3–5 |
| Q1 = C, Q2 = B, Q3 = B | Tag + CHANGELOG; workflow CI; dọn nhật ký 10 tệp | 5, 7, 18, 19 |

## Steps

### Bước 1 — Khung gói và cấu hình sản phẩm

- [ ] Tạo gói `src/integration/__init__.py`.
- [ ] Viết `config/mediated-schema.yaml` đúng hình dạng ở `logical-components.md` §2.1: một thực thể `don_hang`, năm ánh xạ, `loaded` true cho bốn trường của bảng đơn và `false` cho `bang_giao`.
- [ ] Viết `config/integration-tab.yaml` đúng C9: `tab_id: tich-hop`, nhãn, bốn `card_ids`, `result_block_ids: [don-theo-thang]`, `callback_ids: [tich-hop-cap-nhat]`.
- [ ] Thêm đường dẫn hai tệp cấu hình vào `config.yaml` và `AppConfig` (không hardcode trong mã).

### Bước 2 — Xác nhận runner và lệnh chạy của đơn vị

- [ ] Chạy `python -X utf8 -m pytest --version` và xác nhận `pytest.ini` đã khai `testpaths` và marker `slow`; không sửa `pytest.ini` trừ khi buộc.
- [ ] Ghi lệnh unit-scoped vào `unit-test-instructions.md` và chạy thử để thấy nó chạy được (khi chưa có tệp test thì pytest báo không thu thập được — đó là trạng thái đúng trước bước Red đầu tiên).

### Bước 3 — Data model, Red

- [ ] Viết `tests/unit/test_integration_model.py` trước: dựng `DonHang` từ một dict; ngày đặt sai định dạng bị từ chối; trạng thái ngoài tám giá trị bị từ chối; `ma_don` rỗng bị từ chối; tệp lược đồ nạp được và `bang_giao` có `loaded: false`.
- [ ] Chạy lệnh unit-scoped, ghi lại đầu ra đỏ.

### Bước 4 — Data model, Green

- [ ] `src/integration/models.py`: dataclass `DonHang` (năm trường), `LoadResult` (`orders`, `rows_in`, `rows_dropped`, `drop_reasons`, `elapsed_ms`), `QueryRunResult` (theo C4 + `total_orders`, `months`, `partial`).
- [ ] `src/integration/schema.py`: đọc YAML bằng `yaml.safe_load`, `checked_identifier` theo `security-design.md` ADR-U1-S2, trả danh sách cột cần đọc (chỉ trường `loaded: true`).
- [ ] Chạy lại lệnh, xanh.

### Bước 5 — Data model, Refactor

- [ ] Gom hằng số tám trạng thái và tập kiểu dữ liệu đóng vào một chỗ; thêm `QueryExecutionError` vào `src/common/exceptions.py` (C4 yêu cầu).
- [ ] Chạy lại lệnh, xanh; chạy `ruff check` trên các tệp mới.

### Bước 6 — Repository / data access, Red

- [ ] Viết `tests/unit/test_integration_load.py`: đọc đúng bốn cột của bảng đơn; `bang_giao` chỉ kiểm tiêu đề `customer_state`; thiếu cột → `SchemaError` nêu tên trường và cột; tên cột/bảng không hợp lệ → `SchemaError` **trước khi** mở DuckDB; lỗi đọc lần 1 rồi thành công lần 2 → có `integration.load.retried` và nạp xong; lỗi cả hai lần → `SchemaError` và **đúng hai** lần thử; bản ghi trùng `ma_don` bị loại và đếm; ngày rỗng/trạng thái lạ bị loại và đếm.
- [ ] Chạy lệnh, ghi đầu ra đỏ.

### Bước 7 — Repository / data access, Green

- [ ] `src/integration/load.py`: `load_don_hang(config, logger)`, `usecols` từ lược đồ, `dtype=str`, thử lại một lần sau 100 ms chỉ cho `OSError`/`UnicodeDecodeError`, gắn cờ rồi loại bản ghi hỏng theo BR1.1/BR1.2, trả `LoadResult`.
- [ ] Cache cấp tiến trình (`performance-design.md` ADR-U1-P1) khoá theo đường dẫn + mtime.
- [ ] Chạy lại lệnh, xanh.

### Bước 8 — Repository / data access, Refactor

- [ ] Tách hàm thuần `clean_rows(frame) -> (rows, dropped, reasons)` khỏi phần đọc tệp; giữ nguyên chữ ký `clean_<table>` theo quy ước repo.
- [ ] Dọn nhật ký còn 10 tệp ở cuối lần chạy pipeline (`infrastructure-specification.md` §5), có `integration.logs.pruned` / `integration.logs.prune_failed`.
- [ ] Chạy lại lệnh, xanh.

### Bước 9 — Business logic, Red

- [ ] Viết `tests/unit/test_integration_query.py`: truy vấn thiếu điều kiện trạng thái bị từ chối (BR1.4); chưa có kế hoạch viết lại thì không thực thi (BR1.6); kế hoạch ánh xạ `don_hang → olist_orders_dataset` ba trường, không join; kết quả một dòng cho mỗi cặp (tháng, trạng thái) (BR1.5); `total_orders` bằng tổng các dòng; 12 tháng gần nhất tính từ tháng mới nhất; thiếu tháng/trạng thái → `partial` nêu phần thiếu (BR1.8); `elapsed_ms` và `row_count` có mặt; test hiệu năng ngưỡng cứng 2.000 ms (NFR1.4).
- [ ] Chạy lệnh, ghi đầu ra đỏ.

### Bước 10 — Business logic, Green

- [ ] `src/integration/query.py`: `rewrite_plan()` + `run_monthly_orders(frame, ...)`, DuckDB in-memory, đóng trong `finally`, SQL tham số hoá, tên cột từ dict hằng.
- [ ] Chạy lại lệnh, xanh.

### Bước 11 — Business logic, Refactor

- [ ] Tách hằng số `MEDIATED_TO_SOURCE` và mẫu SQL khỏi thân hàm; ghi `integration.query.*` theo danh mục sự kiện.
- [ ] Chạy lại lệnh, xanh.

### Bước 12 — API / endpoint

- [ ] **N/A** — đơn vị không có HTTP API. Không tạo tệp nào cho lớp này; đầu vào duy nhất là callback Dash, kiểm ở bước 15–17. Ghi rõ lý do vào `code-summary.md`.

### Bước 13 — (N/A, xem bước 12)

- [ ] **N/A**.

### Bước 14 — (N/A, xem bước 12)

- [ ] **N/A**.

### Bước 15 — Frontend, Red

- [ ] Viết `tests/unit/test_integration_card.py`: đủ năm trạng thái (rỗng, đang tải, đầy đủ, một phần, lỗi); rỗng **không** hiện 0; "một phần" nêu phần thiếu; "kết quả lần trước" kèm giờ; mọi phần tử tương tác nhận tiêu điểm (`tabIndex`/`html.Button`); nhãn trạng thái có chữ + biểu tượng.
- [ ] Cập nhật `tests/unit/test_dashboard_smoke.py`: 4 tab, 3 callback, 10 output; và `tests/integration/test_u3_end_to_end.py` nếu nó khẳng định số callback.
- [ ] Chạy lệnh, ghi đầu ra đỏ.

### Bước 16 — Frontend, Green

- [ ] `src/integration/card.py`: `build_integration_card(result, state)` dựng cây Dash lõi (không `dmc` ở Bolt này), id thẻ lấy từ `config/integration-tab.yaml`.
- [ ] `src/dashboard/app.py`: thêm `dcc.Tab(label="Tích hợp", value="tich-hop")` và **một callback riêng** nối `tich-hop-cap-nhat`; không đổi callback 9 output hiện có.
- [ ] Chạy lại lệnh, xanh.

### Bước 17 — Frontend, Refactor

- [ ] Dồn chuỗi hiển thị tiếng Việt vào một chỗ trong `card.py`; dùng `src/dashboard/formatting.py` cho số.
- [ ] Chạy lại lệnh, xanh; chạy `ruff check` + `ruff format --check`.

### Bước 18 — Cấu hình môi trường và build

- [ ] Ghim `ruff` vào `requirements.txt` kèm lý do; thêm cấu hình ruff ở gốc repo.
- [ ] Tạo `.github/workflows/ci.yml` đúng `cicd-pipeline.md` §2 (windows-2022, sáu bước, có bước chạy pipeline vì `TD-09`).
- [ ] Thêm `CHANGELOG.md` với mục `v0.1.0` (Q1 = C).
- [ ] Cập nhật `README.md` (mục CI, dọn nhật ký) và `docs/runbook.md` (dọn nhật ký, giữ 10 tệp).

### Bước 19 — Tài liệu và truy vết

- [ ] `code-summary.md`: tệp đã tạo/sửa, quyết định chính, phạm vi test, test viết nhưng chưa chạy (bộ `slow` — lý do), điểm lệch kế hoạch.
- [ ] `source-manifest.json` liệt kê mọi đường dẫn nguồn đã tạo/sửa.
- [ ] `traceability.json` qua `aidlc engine sensor-traceability --stage code-generation --write-upstream`, mỗi `OK` trỏ tới một tệp có thật.

## Ngoài phạm vi (không làm ở đơn vị này)

| Không làm | Vì sao |
|---|---|
| `dmc` (Dash Mantine Components) | `tech-stack-decisions.md` TS-U1-1..4: Bolt này dùng thành phần Dash lõi; `dmc` thuộc U6 |
| Ba thẻ tổng quan còn lại, bốn màn hình chi tiết | Thuộc U6 (C9 chỉ khai id) |
| Ghép bản ghi, chọn nguồn, lớp ngữ nghĩa KPI | Thuộc U4, U5, U3 |
| Sửa `TD-09` (bộ nhanh hermetic) | Ngoài phạm vi lát cắt; CI chạy pipeline thay thế (`cicd-pipeline.md` §2) |
| Chuyển `ibge_dir` ra khỏi `dataset/` | Ngoài phạm vi; đã ghi ở `infrastructure-specification.md` §3 và `memory.md` |

## Revision 2 — cổng đúng đắn dữ liệu (NFR5.5) và một đường dữ liệu (TS-U1-2)

Lý do: vòng phản biện `nfr-requirements` (iteration 3) để lại hai phát hiện Major. Bản sửa yêu cầu đã ghi NFR5.4–NFR5.6 trong `nfr-requirements/tech-stack-decisions.md` và chốt TS-U1-2. Các bước 1–19 đã xong và giữ nguyên; năm bước dưới đây đóng hai phát hiện đó.

### Bước 20 — Đỏ: test đối chiếu số trên thẻ với phép tính độc lập (NFR5.5)

- [ ] Viết `tests/unit/test_integration_correctness.py`, đánh dấu `@pytest.mark.slow` (đọc dữ liệu thật), theo đúng ba bước:
  1. Tính lại **độc lập bằng pandas** từ `dataset/olist_orders_dataset.csv`: bỏ dòng trùng `order_id` (giữ dòng đầu), loại dòng có `order_purchase_timestamp` rỗng/không đọc được hoặc ở tương lai, loại dòng có `order_status` ngoài tám giá trị (`BR1.1`/`BR1.2`); gộp theo `(tháng '%Y-%m', order_status)`; lấy 12 tháng tính từ tháng mới nhất.
  2. Chạy đường của lát cắt: `load_schema` → `rewrite_plan` → `load_don_hang` → `run_monthly_orders` trên `config.yaml` thật.
  3. So **từng nhóm (tháng, trạng thái)** và **tổng toàn kỳ**; lệch một đơn là test đỏ. Thông điệp lỗi nêu tháng, trạng thái, hai con số.
- [ ] Chạy `-m slow` trên tệp mới, ghi lại đầu ra đỏ.

### Bước 21 — Xanh: sửa đường truy vấn, không sửa kỳ vọng của test

- [ ] Nếu lệch, sửa `load.py`/`query.py` cho khớp BR1.1/BR1.2 (ví dụ cửa sổ 12 tháng, cách loại bản ghi) — **không** nới test và không đổi phép tính độc lập.
- [ ] Chạy lại tệp mới, xanh; chạy lại toàn bộ `-m slow`, xanh.

### Bước 22 — Một đường dữ liệu duy nhất (TS-U1-2)

- [ ] `TEXTS["empty_hint"]` chỉ còn nghĩa "chưa chạy truy vấn lần nào" + nút "Chạy truy vấn"; bỏ câu hướng dẫn `python -m src.pipeline run --stage all` (đường in-memory không đọc thứ pipeline sinh ra).
- [ ] Xác nhận bằng test: `render_integration_card` lấy số từ `run_monthly_orders` của chính lần chạy, không đọc `data/marts` hay `warehouse/`; thêm khẳng định trạng thái rỗng không hiện số 0.
- [ ] Cập nhật `tests/unit/test_integration_card.py` cho câu chữ rỗng mới.

### Bước 23 — Sổ sách của lần chạy lại

- [ ] Cập nhật `unit-test-instructions.md` (thêm lệnh `-m slow` cho tệp đối chiếu), `code-summary.md` (mục Revision 2), `source-manifest.json`, `traceability.json` (NFR5.5 và NFR5.6 trỏ `tests/unit/test_integration_correctness.py`).

### Bước 24 — Cổng của đơn vị

- [ ] `.venv\Scripts\python.exe -X utf8 -m pytest -m "not slow"` xanh.
- [ ] `.venv\Scripts\python.exe -X utf8 -m pytest -m slow` xanh (gồm test đối chiếu mới).
- [ ] `.venv\Scripts\python.exe -X utf8 -m pytest --cov=src --cov-fail-under=80` xanh — đây cũng là lệnh xác nhận của cổng nghiệm thu lát cắt.
- [ ] `ruff check` và `ruff format --check` sạch trên các tệp đã sửa.

### Kết quả chạy của Revision 2 (2026-11-08)

| Cổng | Lệnh | Kết quả |
|---|---|---|
| Bộ nhanh | `pytest -m "not slow"` | **368 passed, 9 deselected** |
| Bộ chậm | `pytest -m slow` | **9 passed, 368 deselected** |
| Cổng đúng đắn | `pytest tests/unit/test_integration_correctness.py -m slow` | **2 passed** — từng nhóm `(tháng, trạng thái)` và tổng toàn kỳ khớp phép tính độc lập, sai lệch 0 |
| Phủ + ngưỡng | `pytest --cov=src --cov-fail-under=80` | **377 passed**, phủ **90,82%** (card.py 100%, query.py 100%) |
| Lint/định dạng | `ruff check` + `ruff format --check` | sạch |

## Revision 3 — nối vùng số liệu vào tab theo C9 (2026-11-09)

Người làm từ chối cổng nghiệm thu và chọn hướng "nối số của lát cắt vào tab". C9 nay có `result_region_ids: [don-theo-thang]`; vùng cần callback riêng nên hình dạng đích là **4 tab, 8 callback, 4 thẻ + 1 vùng**.

| Bước | Việc | Tệp |
|---|---|---|
| 25 | Thêm khoá `result_region_ids: [don-theo-thang]` vào cấu hình tab theo C9 | `config/integration-tab.yaml` |
| 26 | `TabConfig` mang thêm `result_region_ids`; `load_tab_config` từ chối cấu hình thiếu khoá hoặc thiếu `don-theo-thang` (`ConfigurationError`) | `src/integration/card.py` |
| 27 | Khung tab dựng vùng `don-theo-thang` (trạng thái "Chưa chạy" + nút "Chạy truy vấn") phía trên lưới bốn thẻ | `src/integration/tab.py` |
| 28 | Callback thứ sáu của tab: `Output("don-theo-thang", "children")` ← `Input("tich-hop-cap-nhat", "n_clicks")`, gọi `render_integration_card` | `src/integration/tab.py` |
| 29 | Đường dự phòng khi cấu hình hỏng cũng khai vùng, để tab vẫn có số liệu | `src/dashboard/app.py` |
| 30 | Test: hình dạng thành **8 callback**, tab có vùng `don-theo-thang`, `TabConfig` có `result_region_ids`, callback của tab thành **6** | `tests/unit/test_dashboard_smoke.py`, `test_integration_card.py`, `test_integration_tab.py` |

### Kết quả chạy của Revision 3

| Cổng | Lệnh | Kết quả |
|---|---|---|
| Bộ nhanh | `pytest -m "not slow"` | **369 passed, 9 deselected** |
| Lint / định dạng | `ruff check` + `ruff format --check` trên sáu tệp đã sửa | sạch |



