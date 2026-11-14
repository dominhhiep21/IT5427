# Code Generation Plan — u2-model

Nguồn: `../functional-design/{functional-spec.md,rules.md,entities.md}`, `../nfr-requirements/tech-stack-decisions.md`, `../nfr-design/{security-design.md,logical-components.md}`, `../infrastructure-design/cicd-pipeline.md`, `../../../inception/contract-design/contract-summary.md` (C1, C3), `../../../inception/units-generation/unit-of-work.md`.

## Phạm vi

U2 dựng đặc trưng, huấn luyện một bộ phân loại đơn trễ, chọn ngưỡng và **trả về** một `ModelBlock`. U2 **không** đọc và không ghi `data/reports/analysis.json` — việc ghép vào báo cáo thuộc `stats-stage` của U1.

## Source manifest

| # | Tệp | Việc |
|---|---|---|
| S1 | `src/analytics/model.py` | **Mới** — 11 cột đặc trưng, 10 cột bị cấm, dựng bảng, chia tập tại 2018-04-01, mã hoá, huấn luyện, chọn ngưỡng, dựng `ModelBlock` |
| S2 | `src/analytics/service.py` | **Sửa** — thêm `training_frame()` trả bảng đã gộp về grain đơn |
| S3 | `src/pipeline/stages.py` | **Sửa** — nhánh `stats` gọi bước mô hình sau bước thống kê và ghép khối |
| S4 | `requirements.txt` | **Sửa** — ghim `scikit-learn==1.6.1` kèm lý do |
| S5 | `.github/workflows/ci.yml` | **Sửa** — thêm `src/analytics/model.py` vào danh sách `ruff format --check` |
| S6 | `README.md`, `CHANGELOG.md` | **Sửa** — mục Test và mốc mô hình |
| S7 | `tests/unit/test_analytics_model.py` | **Mới** — mỗi BR một ca, cộng hai ca rò rỉ nhãn |
| S8 | `tests/integration/test_u2_model_end_to_end.py` | **Mới** — chạy `--stage stats` trên dữ liệu thật, khối `model` có mặt và tái lập được (marker `slow`) |

Tệp không được sửa: `dataset/**`, `config/*.yaml`, `src/dashboard/**`, `src/integrate/**`, `src/analytics/report.py`.

## Thứ tự thi công (TDD)

1. **S4 trước tiên** — ghim `scikit-learn`, cài trong `.venv`, chạy `pip show numpy scipy joblib threadpoolctl`, ghim lại `numpy==2.2.1` nếu bị nâng, rồi chạy lại bộ `slow` của U1. Không đạt bước này thì không viết `import sklearn`.
2. S7 + S1 — dựng đặc trưng và rò rỉ nhãn trước, vì đó là ràng buộc bảo mật.
3. S2 — phương thức đọc.
4. S1 — chia tập, mã hoá, huấn luyện, chọn ngưỡng, dựng khối.
5. S3 — nối vào tầng `stats`.
6. S5 + S6 + S8 — CI, tài liệu, test end-to-end.

## Kiểm chứng

`python -X utf8 -m pytest --cov=src --cov-fail-under=80`, cộng chuỗi bốn bước của nhóm. Bộ `slow` phải xanh **trước** khi thêm mô hình và **sau** khi cài `scikit-learn`, để biết số U1 không lệch.

## Rủi ro đã biết

| Rủi ro | Cách xử lý |
|---|---|
| `numpy` bị nâng khi cài `scikit-learn` | Ghim lại 2.2.1, chạy lại bộ `slow` của U1; lệch baseline là chặn |
| Mã hoá trước khi chia tập → rò rỉ tương lai | Chia trước, mã hoá sau; phạm trù và tham số chuẩn hoá khớp **chỉ** trên tập huấn luyện |
| `has_review` lọt vào đặc trưng | Hằng số tập cấm + test trên khung đặc trưng thật |
| Bỏ dòng thiếu làm lệch cỡ mẫu | Không bỏ dòng: `unknown` cho phân loại, 0 + cờ cho số |
| Ngưỡng không hội tụ hoặc ra 0/1 | `max_iter=1000`, chuẩn hoá, cảnh báo không hội tụ là lỗi, kiểm ngưỡng sau làm tròn |

## Ngoài phạm vi

Ghi tệp báo cáo (U1), giao diện (U3), mọi thay đổi trong `src/integrate/`.

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

