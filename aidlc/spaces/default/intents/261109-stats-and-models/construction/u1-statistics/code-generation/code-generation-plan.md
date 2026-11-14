# Code Generation Plan — u1-statistics

Nguồn: `../functional-design/{functional-spec.md,rules.md,entities.md}`, `../../../inception/contract-design/contract-summary.md` (C1, C2 — phiên bản 2), `../nfr-requirements/*`, `../nfr-design/*`, `../infrastructure-design/*`, `../../../inception/units-generation/unit-of-work.md`, `../../../inception/requirements-analysis/requirements.md`.

## Phạm vi

Đơn vị U1 giao bốn thứ: kiểu báo cáo dùng chung và hai hàm ghi/đọc (`report.py`), năm phép kiểm định, tầng `stats` trong pipeline, và các thay đổi CI/README/CHANGELOG mà FR5 đòi. Không đụng tới mô hình (U2) hay giao diện (U3).

## Source manifest

| # | Tệp | Việc | Blast radius |
|---|---|---|---|
| S1 | `src/analytics/report.py` | **Mới** — `REPORT_VERSION = 2`, `SkipEntry`, `ProportionResult`, `ComparisonResult`, `CorrelationResult`, `GroupTestResult`, `SeasonalResult`, `StatsBlock`, `ModelBlock`, `AnalysisReport`, `ReportView`, `write_report`, `read_report` | Mới, không có consumer cũ |
| S2 | `src/analytics/statistics.py` | **Mới** — BR1.1–BR1.8: năm phép và bộ gom `skipped`, dựng `StatsBlock` | Mới |
| S3 | `src/analytics/service.py` | **Sửa** — thêm `late_rates_by_state`, `price_freight_pairs`, `late_rates_by_region`, dùng lại `_connect`/`_where` | Lớp dùng chung: 5 phương thức cũ **không đổi chữ ký**; test hiện có của `cli analyze` phải vẫn xanh |
| S4 | `src/pipeline/stages.py` | **Sửa** — thêm `"stats"` vào `STAGES`; thêm nhánh `stats` trong `run_stage` | Danh sách tầng bị test hình dạng CLI/`STAGES` ràng buộc |
| S5 | `src/pipeline/cli.py` | **Sửa** — thêm `"stats"` vào `choices` của `--stage` | Không thêm lệnh con: CLI vẫn 3 lệnh con |
| S6 | `requirements.txt` | **Sửa** — ghim `scipy` kèm lý do; **không** thêm `statsmodels` | Ảnh hưởng mọi môi trường cài từ tệp |
| S7 | `.github/workflows/ci.yml` | **Sửa** — nhánh vào cả hai trigger; tệp mới vào danh sách `ruff format --check`; bước `--stage stats` sau `--stage all` | Cổng CI |
| S8 | `README.md` | **Sửa** — mục CI và mục Test khớp `ci.yml`, thêm tầng `stats` | Tài liệu |
| S9 | `CHANGELOG.md` | **Sửa** — mốc mới theo ba nhóm Thêm/Sửa/Nội bộ | Tài liệu |
| S10 | `tests/unit/test_analytics_report.py` | **Mới** — sáu mẫu đọc, ghi nguyên tử, phiên bản | Mới |
| S11 | `tests/unit/test_analytics_statistics.py` | **Mới** — mỗi BR một ca, gồm các nhánh bỏ qua | Mới |
| S12 | `tests/unit/test_pipeline_stages.py` | **Mới** — `STAGES` và `choices` cùng có `stats` | Mới |
| S13 | `tests/unit/test_ci_config.py` | **Mới** — `ci.yml` có nhánh, có tệp mới trong danh sách ruff | Mới |
| S14 | `tests/integration/test_u1_stats_end_to_end.py` | **Mới** — chạy `--stage stats` trên dữ liệu thật, kiểm tệp, kiểm KPI không đổi | Mới |

Tệp không được sửa: `dataset/**`, `config/*.yaml`, `src/dashboard/**`, `src/integrate/**`.

## Thứ tự thi công (TDD)

Theo `## Testing Posture` của nhóm: viết test trước, thấy đỏ, rồi viết mã.

1. S10 + S1 — kiểu và hai hàm, sáu mẫu đọc.
2. S11 + S2 — năm phép; bắt đầu bằng BR1.1 rồi tới bốn phép còn lại.
3. S3 — ba phương thức đọc; test dùng DuckDB tạm hoặc dữ liệu thật ở bộ `slow`.
4. S4 + S5 + S12 — tầng `stats`; chạy `run --stage stats` thật.
5. S6 — ghim `scipy`, cài trong `.venv`, chạy lại toàn bộ bộ test (kiểm `numpy` không bị nâng).
6. S7 + S8 + S9 + S13 — CI và tài liệu.
7. S14 — test end-to-end trên dữ liệu thật, gắn marker `slow`.

## Kiểm chứng

Lệnh nghiệm thu của đợt (đã chốt ở Delivery Planning): `python -X utf8 -m pytest --cov=src --cov-fail-under=80`.

Trước khi coi là xong, chạy thêm chuỗi bốn bước của nhóm: `pytest -m "not slow"` → `run --stage all` → `run --stage stats` → mở dashboard.

## Rủi ro đã biết, phải xử lý trong lúc viết

| Rủi ro | Cách xử lý |
|---|---|
| `--stage stats` bị argparse từ chối nếu chỉ sửa `STAGES` | Sửa cả S4 và S5; S12 khẳng định cả hai |
| `numpy` bị nâng khi cài `scipy`, làm lệch KPI baseline | Sau S6 chạy lại bộ `slow`; nếu lệch, ghim lại `numpy` theo bản `pandas` đang dùng và ghi lý do |
| Test đọc `data/reports/analysis.json` làm bộ nhanh phụ thuộc CI (dạng `TD-09`) | Mọi test tự dựng tệp trong `tmp_path`; không test nào đọc tệp thật của repo |
| `write_json` không đọc lại | Bước kiểm BR1.11 nằm trong `report.py`, không dựa vào `AtomicWriter` |
| Làm tròn phá hằng đẳng thức mùa vụ | Làm tròn **khi ghi**, không làm tròn giá trị dùng để kiểm; test kiểm hằng đẳng thức trên giá trị chưa làm tròn |

## Ngoài phạm vi

Khối mô hình (U2), tab kết quả (U3), phân vùng dữ liệu, bất kỳ thay đổi nào trong `src/integrate/`.

## Testing Contract

```json
{
  "version": 1,
  "methodology": "tdd",
  "source": "team",
  "ordering": "Với mỗi lớp chạy được của một phần, chúng tôi viết test trước cho hành vi mong muốn và chạy nó để thấy đỏ, rồi mới viết mã cho tới khi test đó xanh, rồi mới chuyển sang lớp kế tiếp — và chỉ chuyển sang **phần** kế tiếp (thống kê → mô hình → hiển thị) khi phần đang làm đã có test end-to-end riêng xanh trên dữ liệu thật và toàn bộ bộ nhanh vẫn xanh.",
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
      "text": "- **Methodology**: tdd\n- **Ordering**: Với mỗi lớp chạy được của một phần, chúng tôi viết test trước cho hành vi mong muốn và chạy nó để thấy đỏ, rồi mới viết mã cho tới khi test đó xanh, rồi mới chuyển sang lớp kế tiếp — và chỉ chuyển sang **phần** kế tiếp (thống kê → mô hình → hiển thị) khi phần đang làm đã có test end-to-end riêng xanh trên dữ liệu thật và toàn bộ bộ nhanh vẫn xanh.\n- **Bằng chứng cho `tdd` là quyết định của người làm, không phải git.** Lịch sử chỉ có 14 commit và mã\n  nguồn cùng test của U3 vào **cùng một commit** (`b384da4 feat: Add U3 feature` có cả `src/**` và\n  `tests/**`), nên bằng chứng tĩnh không phân biệt được thứ tự. Giá trị `tdd` kế thừa từ lần phỏng vấn\n  trước và **đã được xác nhận lại ở đợt này** (Q3 = A: giữ TDD cho cả phần mô hình, dù phần đó khó viết\n  test trước hơn). Nó thay cho mặc định `test-after` của `org.md`.\n- **Ngưỡng phủ 80% đã được cưỡng chế trong CI, và phạm vi đo đã chốt là \"giữ nguyên như CI\"** (phỏng vấn\n  Q6 = A). `ci.yml:46` chạy `python -X utf8 -m pytest --cov=src --cov-fail-under=80` trên **toàn bộ** bộ\n  test (nhanh + `slow`), vì bảy mô-đun `src/` chỉ có phần phủ đến từ bộ `slow`. Chúng tôi không hạ ngưỡng\n  và không tách cổng sang bộ nhanh để cho một bước pass. `README.md` mục \"CI\" đang nói ngược lại (rằng bộ\n  `slow` và cổng phủ không chạy trong CI) — đó là **trôi tài liệu** và README là bên phải sửa, không phải\n  `ci.yml`.\n- **Mọi mô-đun mới đều phải có test riêng**, kể cả mô-đun \"chỉ nối dây\". Khoảng trống còn lại\n  (`src/analytics/service.py`, `src/integrate/validate.py`, `reconcile.py`, `catalog.py`, `connections.py`,\n  `src/pipeline/micro_batch.py`, `stages.py`) là nợ đã biết, không phải mẫu để noi theo — và\n  `src/analytics/service.py` đúng là chỗ đợt này sẽ mở rộng, nên mô-đun thống kê mới không được lặp lại\n  khoảng trống đó.\n- **Khối lượng hiện tại** (đo trên đĩa): 70 tệp Python trong `src/` (9.444 dòng), 40 mô-đun test với\n  **353** hàm test (9 hàm `slow`), 7.358 dòng test — tương đương 78% khối lượng `src/`. Dưới TDD + yêu cầu\n  test cho mọi mô-đun mới + không có lát cắt mỏng, khối lượng này còn tăng trong đợt này.\n- **Bộ nhanh và bộ chậm tách bằng marker**, không tách bằng thư mục: `-m \"not slow\"` là bộ nhanh,\n  `-m slow` là bộ cần dữ liệu thật/sinh ra (`pytest.ini`).\n- **Bộ nhanh chưa hermetic** (`TD-09`): 5 test trong `tests/unit/test_dashboard_smoke.py` và\n  `tests/unit/test_cli.py::test_main_analyze_stage` gọi `load_config()` của repo nên cần\n  `warehouse/olist.duckdb` và `data/marts/` — hai thư mục bị `.gitignore`. CI che lỗ hổng này bằng bước\n  dựng dữ liệu trước khi test; trên máy mới clone, bộ \"nhanh\" vẫn đỏ. Chưa chốt có sửa `TD-09` trong đợt này.\n- **Test là chốt hồi quy dữ liệu, không chỉ chốt mã.** Mọi thay đổi cleaning/ghép bản ghi có chủ đích phải\n  cập nhật đồng thời `src/quality/allowlist.py`, `src/integrate/reconcile.py`, `README.md` và test tích hợp;\n  nếu không, `quality` chế độ `full` và `KpiReconciler` sẽ đỏ.\n- **Test áp đặt cả hình dạng giao diện và CLI.** Hiện có **4 tab, 8 callback, 9 output, 11 view** và **3\n  lệnh con CLI**; `tests/unit/test_dashboard_smoke.py` khẳng định số tab/callback/output,\n  `tests/integration/test_u3_end_to_end.py` khẳng định lại số callback,\n  `tests/integration/test_u2_end_to_end.py` khẳng định `len(views) == 11`, và `tests/unit/test_cli.py` khẳng\n  định parser có 3 lệnh con. Thêm tab/thẻ/output/lệnh là thay đổi có chủ đích và phải sửa các test đó\n  **trong cùng thay đổi**. Việc thống kê là **tầng thứ năm của `run --stage`** (không phải lệnh con thứ tư)\n  nên con số 3 lệnh con giữ nguyên; cái thay đổi là `STAGES` trong `src/pipeline/stages.py` — và vì danh\n  sách đó hiện **không có test riêng**, việc thêm test cho nó nằm trong yêu cầu \"mọi mô-đun mới có test\n  riêng\" ở trên, không phải tuỳ chọn.\n- **`ruff` là cổng lint + format.** `ruff check .` chạy toàn repo; `ruff format --check` chỉ chạy trên danh\n  sách tệp khai tay trong `ci.yml:33` (`TD-20`), nên tệp mới **phải** được thêm vào danh sách đó cùng lúc\n  với việc tạo tệp. Mã cũ chưa sạch ruff được dọn theo từng tệp khi có người sửa tới.\n- **Không có kiểm tra kiểu tĩnh.** `mypy`/`pyright` không có trong phụ thuộc và không có trong CI; type\n  hint vẫn giữ theo quy ước hiện có nhưng không phải cổng.\n- **Scope `feature` áp thêm sàn phủ 80% và yêu cầu chạy trong CI trước khi hợp nhất** — trùng với thực hành\n  đã có, không mâu thuẫn."
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
  "input_sha256": "sha256:c4202e8db772d9e058187d1477b07d3f94d3d892f3c84556a9144871d695dfe2",
  "contract_sha256": "sha256:c6029e50ecfaa8290a19359ae0be09255f024696b238b15be37fc81fedc1f7de"
}
```

