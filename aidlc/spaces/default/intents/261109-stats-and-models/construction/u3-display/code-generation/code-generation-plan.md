# Code Generation Plan — u3-display

Nguồn: `../functional-design/{functional-spec.md,rules.md,entities.md}`, `../nfr-requirements/*`, `../nfr-design/{logical-components.md,security-design.md,performance-design.md}`, `../infrastructure-design/*`, `../../../inception/contract-design/contract-summary.md` (C2), `../../../inception/domain-design/components.md`.

## Phạm vi

Thêm tab thứ năm vào dashboard, đọc báo cáo qua `read_report` và dựng nội dung. Không tính toán, không ghi tệp, không sửa tầng dữ liệu.

## Source manifest

| # | Tệp | Việc |
|---|---|---|
| S1 | `src/dashboard/analysis_tab.py` | **Mới** — tám thành phần của `logical-components.md` |
| S2 | `src/dashboard/app.py` | **Sửa** — thêm tab thứ năm, nối callback |
| S3 | `assets/style.css` | **Sửa** — chỉ nếu cần lớp cho tab mới; **không** thêm token màu mới (BR3.9) |
| S4 | `tests/unit/test_dashboard_analysis_tab.py` | **Mới** — năm trạng thái, bốn thẻ, mục null, skipped, thứ tự, nhãn, `tabIndex`, đọc một lần |
| S5 | `tests/unit/test_dashboard_smoke.py` | **Sửa** — tab 4→5, callback 8→9, **output giữ 9**; thay `tabs.children[-1]` bằng tra theo `id` |
| S6 | `tests/integration/test_u3_end_to_end.py` | **Sửa** — số callback; dựng tab từ báo cáo thật |
| S7 | `.github/workflows/ci.yml` | **Sửa** — tệp nguồn **và** tệp test mới vào danh sách `ruff format --check` |
| S8 | `tests/unit/test_ci_config.py` | **Sửa** — hai tệp trên vào `NEW_FILES` |
| S9 | `README.md`, `CHANGELOG.md` | **Sửa** — mục Test, "4 tab" thành 5, mốc CHANGELOG |

Tệp không được sửa: `dataset/**`, `config/*.yaml`, `src/integrate/**`, `src/analytics/**`.

## Thứ tự thi công (TDD)

1. **S4 trước** — test cho năm trạng thái và bốn quy tắc dễ sai nhất.
2. S1 — dựng tab tới khi S4 xanh.
3. S2 — nối vào `app.py`; chạy S5 ngay, nó sẽ đỏ ở `children[-1]`.
4. S5 + S6 — test hình dạng và end-to-end.
5. S7 + S8 + S9 — CI và tài liệu.

## Kiểm chứng

`python -X utf8 -m pytest --cov=src --cov-fail-under=80`, cộng chuỗi bốn bước; bước 4 xem tab ở **1280px** và ghi kết quả vào `code-summary.md`.

## Rủi ro đã biết

| Rủi ro | Cách xử lý |
|---|---|
| `tabs.children[-1]` đọc nhầm tab | Tra theo `id` trước khi thêm tab |
| Số output bị sửa nhầm thành 10 | Assert đó đo tuple của callback KPI; **giữ 9** |
| `dmc.Title` lỗi vì thiếu provider | Tab tự bọc `dmc.MantineProvider` |
| `late_rate.rate` là 0–1 | Nhân 100 trong `formatter`; test khẳng định 8,11 |
| Đọc tệp hai lần | Chỉ `tab-callback` mở tệp, một lần; test đếm bằng stub |
| Tệp test lọt cổng định dạng | S7 và S8 nêu **cả** tệp nguồn và tệp test |

## Ngoài phạm vi

`src/analytics/**`, `src/integrate/**`; bộ chọn ngưỡng (đã bỏ — Q1 = A).

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
