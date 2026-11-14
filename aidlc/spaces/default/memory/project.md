# Project-Level Rules

> Project-specific specialisation and corrections. Loaded after `org.md` and
> `team.md` as strict-additive guidance; contradictions with broader policy
> are rejected. Populated by practices-discovery and the self-learning loop.
>
> Use sparingly: most teams don't need a project layer. Reach for it
> only when this specific project needs stable, durable guidance beyond the
> team practice (for example, package-specific release checks or an additional
> regression suite for a legacy component).

## Way of Working

<!-- Project-specific specialisation. Example: -->
<!-- This monorepo requires package-scoped branch names and a package owner -->
<!-- review in addition to the team's normal merge policy. -->

## Walking Skeleton

<!-- Project-specific specialisation. Example: -->
<!-- The walking skeleton must exercise the legacy service adapter as well -->
<!-- as the new service boundary. -->

## Testing Posture

<!-- Project-specific specialisation. -->

## Guard Policy

<!-- Project-specific. Mode: strict, relaxed, or off. Strict here holds for every intent, whatever one person asks in chat; relaxed or off here applies to every intent whose policy came from its scope, unless the person sets another; changing this line changes it. A section under the retired Change Control heading, written by an earlier release, is still read. -->

## Deployment

<!-- Project-specific specialisation. -->

## Code Style

<!-- Project-specific specialisation. -->

## Tech Stack

<!-- Technology choices locked for this project. -->

## Decided

<!-- Decisions made in earlier stages that should not be re-asked. -->
<!-- Format: DECIDED: [decision] (Stage [slug], [date]) -->

## Scope Overrides

<!-- Custom scope rules for this project. -->

## Forbidden

<!-- Populated by practices-discovery affirmation gate. -->
<!-- Format: NEVER [behavior] (affirmed [date]) -->
<!-- Example: NEVER throw exceptions across service layer boundaries (affirmed 2026-05-17) -->

- NEVER sửa, ghi đè hay "làm sạch tại chỗ" bất kỳ tệp dữ liệu nào — không tệp nào trong `dataset/`, và không tệp CSV/Parquet trung gian nào trong `data/`; mọi tầng phải tái lập được từ 9 CSV gốc. (Nguồn: `AGENTS.md`; `README.md` mục "Lưu ý"; `architecture.md` §1; `.gitignore`) (affirmed 2026-11-12)

- NEVER join trực tiếp bảng geolocation thô vào customers/orders — phải gộp về đúng một dòng cho mỗi `zip_code_prefix` (một lat/lng, một city/state) trước. (Nguồn: `src/clean/geolocation.py`; `architecture.md` §4; `tests/data_quality/test_real_dataset.py` khẳng định 19.015 mã bưu chính sau gộp) (affirmed 2026-11-12)

- NEVER join payments hoặc reviews **chưa gộp** vào dữ liệu cấp dòng hàng — doanh thu và số đếm review sẽ bị nhân lên; gộp về một dòng mỗi `order_id` trước. (Nguồn: `src/ingest/reports.py` — `reconcile_payments`; `business-overview.md` §4) (affirmed 2026-11-12)

- NEVER commit `data/`, `warehouse/`, `logs/`, `inbox/`, `.venv/` hay `.coverage`. (Nguồn: `.gitignore`; `technology-stack.md` §5) (affirmed 2026-11-12)

- NEVER import một thư viện bên thứ ba chưa được ghim trong `requirements.txt` — kể cả `numpy` (chỉ có mặt gián tiếp qua `pandas` 2.2.3) hay `joblib` để tuần tự hóa mô hình. (`pickle` **không** thuộc nhóm này: nó là thư viện chuẩn và là cách lưu mô hình đã chốt — xem `## Mandated`.) (Nguồn: `requirements.txt:23-26`; `dependencies.md` §4.9; Q3 = A) (affirmed 2026-11-12)

- NEVER đưa `payment_value` vào một KPI doanh thu mà không nêu rõ định nghĩa doanh thu của chỉ số đó. (Nguồn: `src/common/kpis.py` — `validate_ledger` từ chối; 378 đơn lệch hơn 0,01 BRL) (affirmed 2026-11-12)

- NEVER đặt `--cov-fail-under` lên riêng bộ nhanh hay hạ ngưỡng phủ để cho một bước pass. (Nguồn: `ci.yml:50-53`; `tests/unit/test_ci_config.py`; `org.md` — "may not be weakened to make a step pass") (affirmed 2026-11-12)

- NEVER thêm phụ thuộc kiểm tra kiểu tĩnh (`mypy`, `pyright`) — đây là quyết định đã chốt, không phải thiếu sót. (Nguồn: `code-quality-assessment.md` §4; `technology-stack.md` §5) (affirmed 2026-11-12)

- NEVER dọn định dạng toàn repo trong một thay đổi chức năng; mã cũ dọn theo từng tệp khi có người sửa tới. (Nguồn: `ci.yml:31-33` kèm chú thích; `ruff.toml:24-25`) (affirmed 2026-11-12)

- NEVER hard-code id thẻ/vùng của tab "Tích hợp" trong mã khi hợp đồng YAML đã khai chúng. (Nguồn: `config/integration-tab.yaml`; `src/integration/card.py` — `load_tab_config`; `architecture.md` §2) (affirmed 2026-11-12)

- NEVER huấn luyện mô hình hay dựng đặc trưng trên cột chỉ biết được **sau** mốc dự đoán; mọi cột như vậy phải nằm trong `FORBIDDEN_COLUMNS` và có test canh. (Nguồn: `src/analytics/model.py` — `FORBIDDEN_COLUMNS`, `validate_features`; `code-quality-assessment.md` §7.3 mục 1; `TD-22`) (affirmed 2026-11-12)

- NEVER đổi `src/integrate/reconcile.py` `BASELINE` để chứa baseline của mô hình; baseline mô hình phải có bộ số riêng (số dòng, số nhãn dương, mốc cắt) đo lại theo đúng khung và đơn vị. (Nguồn: `TD-21` — `model.py:22-23` đang là chỗ khai thứ tư của 96.478/7.826) (affirmed 2026-11-12)

- NEVER thêm lệnh con CLI cho thống kê/mô hình/dự đoán — chúng đi qua `run --stage` (`STAGES` có 5 tên, CLI giữ 3 lệnh con). (Nguồn: `src/pipeline/stages.py:24`; `src/pipeline/cli.py:21,29,32`; `tests/unit/test_pipeline_stages.py:157-161`) (affirmed 2026-11-12)

- NEVER commit tệp mô hình hay bất kỳ tệp nào dưới `data/models/` — đó là sản phẩm sinh ra, mỗi checkout tự sinh lại. (Nguồn: `.gitignore` chặn `data/`; Q3 = A ngày 2026-11-12) (affirmed 2026-11-12)

- NEVER đặt một giá trị AUC (hay precision/recall/ngưỡng) làm **kỳ vọng** của một test viết trước; các chỉ số đó được **ghi ra và hiển thị**, không phải cổng — test đỏ vì mô hình "chưa đủ giỏi" sẽ đẩy người làm vào việc chỉnh ngưỡng cho test xanh thay vì sửa mã. (Nguồn: Q1 = A ngày 2026-11-12; `business-overview.md` §4 — chỉ số mô hình **không** thuộc `BASELINE`) (affirmed 2026-11-12)

- NEVER coi cờ `skeleton: on` của scope `feature` là căn cứ dựng một Unit lát cắt mỏng cho intent này khi chưa có quyết định mới của người làm; người làm đã chọn làm trọn từng Bolt và điểm lệch được **ghi lại**, không được lặng lẽ giải quyết theo hướng nào. (Nguồn: Q2 = A ngày 2026-11-12; `.aidlc/scopes/aidlc-feature.md` dòng 6; `## Walking Skeleton` trong `team-practices.md`) (affirmed 2026-11-12)

## Mandated

<!-- Populated by practices-discovery affirmation gate. -->
<!-- Format: ALWAYS [behavior] (affirmed [date]) -->
<!-- Example: ALWAYS use Result<T,E> for fallible operations in service layer (affirmed 2026-05-17) -->

- ALWAYS giữ `dataset/` nguyên trạng và ghi mọi dữ liệu dẫn xuất vào `data/`, `warehouse/`, `logs/`, `inbox/`; mọi tầng phải tái lập được từ 9 CSV gốc bằng một lần chạy. (Nguồn: `business-overview.md` §7; `.gitignore`; `architecture.md` §1) (affirmed 2026-11-12)

- ALWAYS chạy mọi lệnh Python bằng UTF-8 — `python -X utf8 ...` hoặc `PYTHONUTF8=1` — vì đường dẫn workspace có ký tự tiếng Việt và dữ liệu có ký tự Bồ Đào Nha. (Nguồn: `ci.yml:40,45,48,53,58`; `README.md` mọi khối lệnh; `docs/runbook.md`) (affirmed 2026-11-12)

- ALWAYS ghim mọi phụ thuộc trực tiếp vào `requirements.txt` (nay **12** gói) kèm lý do, và cài trong `.venv` của repo chứ không vào môi trường Python toàn cục. (Nguồn: `requirements.txt:1-27`; `technology-stack.md` §2) (affirmed 2026-11-12)

- ALWAYS giữ `ruff check .` và `ruff format --check` sạch, thêm tệp nguồn mới vào danh sách khai tay của `ruff format --check` (`ci.yml:35`, **34** mục) **cùng lúc** với việc tạo tệp, và không thêm `per-file-ignores` mới cho mã mới. (Nguồn: `ruff.toml:17-29`; `ci.yml:34-35`; `TD-20`; `tests/unit/test_ci_config.py` chỉ canh 14 tệp của đợt trước) (affirmed 2026-11-12)

- ALWAYS đo độ phủ trên **toàn bộ** bộ test bằng `pytest --cov=src --cov-fail-under=80` trong CI — không đặt cờ lên riêng bộ nhanh, không hạ ngưỡng để cho một bước pass. (Nguồn: `ci.yml:50-53` kèm chú thích; `README.md` mục "CI"; `tests/unit/test_ci_config.py` canh "cổng phủ không bị hạ") (affirmed 2026-11-12)

- ALWAYS nêu rõ **định nghĩa doanh thu** đang dùng (`price + freight_value` của đơn `delivered`, hay `payment_value`) mỗi khi thêm KPI hoặc truy vấn mới; KPI kiểu tiền thiếu định nghĩa bị `validate_ledger` từ chối. (Nguồn: `src/common/kpis.py` — `REVENUE_DEFINITION`; `business-overview.md` §4 — 378 đơn lệch hơn 0,01 BRL; `src/ingest/reports.py` — `reconcile_payments`) (affirmed 2026-11-12)

- ALWAYS nêu rõ grain (order / order-item / payment / review) trước mỗi lần merge, và kiểm lại số dòng + tính duy nhất của khoá sau khi merge. (Nguồn: `src/integrate/validate.py` — `EXPECTED`, 9 check unique, `J-01` join không nở; `AGENTS.md`) (affirmed 2026-11-12)

- ALWAYS cập nhật **đồng thời, trong cùng một thay đổi có chủ đích** mọi nơi khai cùng một sự thật: các tệp `src/ingest/schemas.py`, `src/quality/gate.py`, `src/quality/allowlist.py`, `src/integrate/validate.py`, `src/integrate/reconcile.py`, `src/integrate/catalog.py` (`VIEW_TABLES`), `README.md` và test tương ứng — kể cả các test khẳng định hình dạng bề mặt, hiện là **5 tab, 9 callback, 9 output, 11 view, 3 lệnh con CLI, 4 thẻ tóm tắt, 3 mục**. (Nguồn: `dependencies.md` §3 — bảng "cùng một sự thật khai ở 3–6 nơi"; `TD-02`; `code-quality-assessment.md` §7.1) (affirmed 2026-11-12)

- ALWAYS giữ `QualityGate` chế độ `full` và `KpiReconciler` xanh sau mỗi thay đổi cleaning/ghép bản ghi, hoặc cập nhật allowlist/baseline một cách có kiểm soát và ghi lại lý do. (Nguồn: `src/quality/allowlist.py` — 10 bộ đếm; `src/integrate/reconcile.py` — 5 KPI + 5 dung sai; `business-overview.md` §4) (affirmed 2026-11-12)

- ALWAYS đọc mart/DuckDB hiện có qua `AnalyticsService` cho phân tích mới, thay vì định nghĩa lại doanh thu hay KPI theo cách khác. (Nguồn: `architecture.md` §2 — "một nơi duy nhất chạm DuckDB"; `dependencies.md` §2.4 — fan-in 5; `TD-02`) (affirmed 2026-11-12)

- ALWAYS truyền tham số SQL qua placeholder `?` và lấy tên cột / `GROUP BY` từ dict hằng, không nối chuỗi từ đầu vào người dùng. (Nguồn: `src/analytics/service.py` — `_where` + 4 hằng SQL tĩnh; `code-quality-assessment.md` §1) (affirmed 2026-11-12)

- ALWAYS giữ mô-đun suy luận là **hàm thuần trên `DataFrame`/`dict`** và đặt mọi I/O ở `service.py` (đọc DuckDB) và `report.py` (ghi/đọc tệp); `stages.py` là nơi duy nhất ghép chúng lại. (Nguồn: `code-structure.md` §3.1; `architecture.md` §2) (affirmed 2026-11-12)

- ALWAYS khai danh sách đặc trưng như một hợp đồng có kiểm — `FEATURES` + `FORBIDDEN_COLUMNS` + `validate_features` — và cập nhật **tất cả** nơi khai cùng lúc (`model.py`, `TRAINING_FRAME_SQL` trong `service.py`, test đơn vị, test end-to-end, `README.md`). (Nguồn: `dependencies.md` §3 — dòng "Danh sách đặc trưng + danh sách cột cấm"; `TD-22`) (affirmed 2026-11-12)

- ALWAYS thêm nhánh đang làm vào **cả** `on.push.branches` và `on.pull_request.branches` của `.github/workflows/ci.yml` cùng lúc với việc tạo nhánh. (Nguồn: `ci.yml:5-13` — danh sách khai tay, hiện ba nhánh ở cả hai trigger; một nhánh ngoài danh sách không có cổng nào) (affirmed 2026-11-12)

- ALWAYS lưu tệp mô hình vào `data/models/` bằng **`pickle` của thư viện chuẩn** — không thêm `joblib` hay bất kỳ gói tuần tự hóa nào — và **chỉ** sinh nó qua `python -X utf8 -m src.pipeline run --stage stats`; không có lệnh con, không có bước build riêng. (Nguồn: Q3 = A ngày 2026-11-12; `requirements.txt` — 12 gói ghim, không có `joblib`; `TD-25`; `## Deployment` trong `team-practices.md`) (affirmed 2026-11-12)

- ALWAYS chạy `python -X utf8 -m src.pipeline run --stage stats` trên một checkout mới **trước khi** vùng dự đoán của tab phân tích được coi là dùng được — tệp mô hình không tồn tại cho tới bước đó, nên giao diện phải chịu được trạng thái "chưa có mô hình" chứ không được sập. (Nguồn: Q3 = A; `.gitignore` chặn `data/`; `## Deployment` bước 3 của `team-practices.md`) (affirmed 2026-11-12)

- ALWAYS viết test cho lớp mô hình **trước** khi viết mã, và cho test khẳng định **hành vi**: cỡ mẫu huấn luyện/kiểm định, việc chia tập theo `order_id` (không tách dòng hàng cùng một đơn sang hai bên), và không cột nào trong `FORBIDDEN_COLUMNS` lọt vào ma trận đặc trưng. Đây là cách TDD được giữ ở phần khó nhất của đợt. (Nguồn: Q1 = A ngày 2026-11-12; `src/analytics/model.py` — `validate_features`, `FORBIDDEN_COLUMNS`; `tests/unit/test_analytics_model.py`; `TD-22`) (affirmed 2026-11-12)

- ALWAYS chạy chuỗi xác nhận bốn bước, đúng thứ tự, trước khi coi một đơn vị công việc là xong: `python -X utf8 -m pytest -m "not slow"` → `python -X utf8 -m src.pipeline run --stage all` → `python -X utf8 -m src.pipeline run --stage stats` → mở dashboard; dừng ngay ở bước đỏ đầu tiên và để CI chạy phần còn lại sau khi push. (Nguồn: Q4 = A và Q5 = B của đợt trước; `README.md` mục "Test"; `ci.yml:40-46`; `pytest.ini`) (affirmed 2026-11-12)

## Corrections

<!-- Project-specific corrections from human feedback. -->
<!-- Format: NEVER/ALWAYS [behavior] (learned [date]) -->
- Ngoại lệ duy nhất của luật "NEVER đặt một giá trị AUC (hay precision/recall/ngưỡng) làm kỳ vọng của một test viết trước" là test `slow` của mốc sàn: nó khẳng định `beats_floor(model.auc, model.baseline_auc)` trên **báo cáo thật** do `--stage stats` sinh (NFR5), không dựng báo cáo giả, và khi đỏ thì phải điều tra mô hình/dữ liệu — không hạ `MODEL_AUC_FLOOR` và không nới ngưỡng. (learned 2026-11-14) <!-- cid:261111-model-feature-improvemen:feedback-optimization:1a355c6a4d2c69447412b318b4ae7c7569fe420f11ea0eb7046ec62183c6d8a8 -->
