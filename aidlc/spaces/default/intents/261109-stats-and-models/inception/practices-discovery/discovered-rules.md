# Quy tắc phát hiện được — Olist E-commerce Data Pipeline

> Chỉ những ràng buộc cứng **đã có bằng chứng trong repo** tại commit
> `ea77bdf88d1431de11c36e1b739972bd594063f0` **hoặc do người làm tuyên bố** tại buổi phỏng vấn
> (`practices-discovery-questions.md`, Q1–Q6). Không có quy tắc nào ở đây là đề xuất mới của agent;
> quyết định mô tả *cách làm* (không dựng lát cắt mỏng, hình dạng tầng `stats`, giữ TDD) nằm ở
> `team-practices.md`, không phải ở đây, vì chúng không phải ràng buộc cứng áp lên mã.
> Nguồn ghi trong ngoặc sau mỗi quy tắc; bản nháp, chưa qua cổng xác nhận.

## Mandated

- ALWAYS giữ `dataset/` nguyên trạng và ghi mọi dữ liệu dẫn xuất vào `data/`, `warehouse/`, `logs/`, `inbox/`. (nguồn: `README.md` mục "Lưu ý"; `AGENTS.md`; `.gitignore`; `ideation/scope-definition/scope-document.md` §3 — "Không sửa dữ liệu gốc trong `dataset/`")
- ALWAYS chạy Python bằng UTF-8 — `python -X utf8 ...` hoặc `PYTHONUTF8=1` — vì đường dẫn workspace có ký tự tiếng Việt và dữ liệu có ký tự Bồ Đào Nha. (nguồn: `README.md` mọi khối lệnh; `docs/runbook.md`; `ci.yml:38,41,46,51`; `technology-stack.md` §1)
- ALWAYS gộp `olist_geolocation_dataset.csv` về đúng một dòng cho mỗi `zip_code_prefix` (một lat/lng, một city/state) **trước** khi join vào customers/orders. (nguồn: `AGENTS.md`; `src/clean/geolocation.py`; `tests/data_quality/test_real_dataset.py` khẳng định 19.015 mã bưu chính sau gộp)
- ALWAYS gộp payments và reviews về một dòng cho mỗi `order_id` trước khi join vào dữ liệu cấp dòng hàng. (nguồn: `AGENTS.md`; `src/ingest/reports.py` — `reconcile_payments`; `business-overview.md` §4)
- ALWAYS nêu rõ grain (order / order-item / payment / review) trước mỗi lần merge và kiểm lại số dòng + tính duy nhất của khoá sau khi merge. (nguồn: `AGENTS.md`; `src/integrate/validate.py` — `StarSchemaValidator`; `tests/integration/test_u2_end_to_end.py`)
- ALWAYS nêu rõ định nghĩa doanh thu đang dùng (`price + freight_value` của đơn `delivered`, hay `payment_value`) mỗi khi thêm KPI hoặc truy vấn mới. (nguồn: `AGENTS.md` — 378 đơn lệch > 0,01 BRL; `src/common/kpis.py` — `REVENUE_DEFINITION` và `validate_ledger` **từ chối** KPI tiền thiếu định nghĩa; `business-overview.md` §4)
- ALWAYS lọc trạng thái đơn một cách tường minh cho mọi phân tích doanh thu/giao vận, không dựa vào mặc định ngầm. (nguồn: `AGENTS.md`; `KpiFilters.order_status` trong `src/common/types.py`; `business-overview.md` §7; `TD-12`)
- ALWAYS cập nhật **tất cả** nơi khai báo cùng một sự thật dữ liệu trong cùng một thay đổi có chủ đích — `src/ingest/schemas.py`, `src/quality/gate.py`, `src/quality/allowlist.py`, `src/integrate/validate.py`, `src/integrate/reconcile.py`, `src/integrate/catalog.py` (`VIEW_TABLES`), `README.md` và test tương ứng. (nguồn: `dependencies.md` §3 — mỗi sự thật đang khai ở 3–6 nơi; `TD-02`; `TD-15`)
- ALWAYS cập nhật đồng thời test khẳng định hình dạng giao diện/CLI khi đổi hình dạng đó: `tests/unit/test_dashboard_smoke.py`, `tests/integration/test_u3_end_to_end.py`, `tests/integration/test_u2_end_to_end.py` (11 view), `tests/unit/test_cli.py` (3 lệnh con) — hiện là 4 tab, 8 callback, 9 output. (nguồn: `code-quality-assessment.md` §7.1 liệt kê từng dòng assert; `ci.yml` chạy bộ nhanh nên lệch là đỏ ngay)
- ALWAYS ghim mọi phụ thuộc trực tiếp vào `requirements.txt`, cài trong `.venv` của repo (không cài vào môi trường Python toàn cục) và ghi rõ lý do khi thêm một thư viện mới. (nguồn: `README.md` mục "Cài đặt"; `requirements.txt` 10 gói ghim kèm chú thích lý do; `technology-stack.md` §2; `dependencies.md` §1.1)
- ALWAYS thêm tệp nguồn mới vào danh sách `ruff format --check` trong `ci.yml:33` cùng lúc với việc tạo tệp. (nguồn: `ci.yml:32-33` — danh sách khai tay; `TD-20`; `code-quality-assessment.md` §4)
- ALWAYS giữ `ruff check .` và `ruff format --check` sạch trước khi coi một thay đổi là xong; mã mới không được thêm `per-file-ignores` mới. (nguồn: `ruff.toml`; `ci.yml:32-33`; `requirements.txt` — `ruff==0.17.4`; `README.md` mục "Lint và định dạng")
- ALWAYS truyền tham số SQL qua placeholder `?` và lấy tên cột / `GROUP BY` từ dict hằng, không nối chuỗi từ đầu vào người dùng. (nguồn: `src/analytics/service.py` — `_where`; `src/integration/rewrite.py`; `code-quality-assessment.md` §1)
- ALWAYS giữ `quality` chế độ `full` và `KpiReconciler` xanh sau mỗi thay đổi cleaning/ghép bản ghi, hoặc cập nhật allowlist/baseline một cách có kiểm soát và ghi lại lý do. (nguồn: `src/quality/allowlist.py`, `src/integrate/reconcile.py`; `ideation/scope-definition/scope-document.md` §5 — "Không hồi quy"; `TC-06` đợt trước)
- ALWAYS giữ độ phủ test tối thiểu 80% cho mã trong `src/`, đo bằng `pytest --cov=src`, và đo trên **toàn bộ** bộ test (nhanh + `slow`) — không đặt `--cov-fail-under` lên riêng bộ nhanh, không hạ ngưỡng để cho một bước pass. (nguồn: người làm chốt ở phỏng vấn Q6 = A — "giữ như CI hiện tại: phủ tính trên toàn bộ, chạy trong CI"; `ci.yml:43-46` kèm chú thích giải thích vì sao tính trên toàn bộ; `pytest-cov==7.1.0`; `technology-stack.md` §5)
- ALWAYS đọc mart/DuckDB hiện có cho phân tích mới thay vì định nghĩa lại doanh thu hay KPI theo cách khác. (nguồn: `code-quality-assessment.md` §7.3 mục 3 — "Kiểm định/mô hình nên **đọc** mart hiện có"; `src/common/kpis.py`; `TD-02`)
- ALWAYS thêm nhánh đang làm vào **cả** `on.push.branches` và `on.pull_request.branches` của `.github/workflows/ci.yml` cùng lúc với việc tạo nhánh. (nguồn: người làm chốt ở phỏng vấn Q1 = A; `ci.yml:3-11` khai tay đúng hai nhánh `main` và `feature/update-ui-ux`, nên nhánh ngoài danh sách không có cổng nào)
- ALWAYS cập nhật `README.md` mục "CI" trong cùng thay đổi với `ci.yml` — README hiện nói bộ `slow` và cổng phủ 80% **không** chạy trong CI, trái với `ci.yml:43-46`; hướng đã chốt là giữ `ci.yml` và sửa README. (nguồn: phỏng vấn Q6 = A; `ci.yml:43-46` so với `README.md` mục "CI"; `evidence.md` §2)
- ALWAYS chạy chuỗi xác nhận bốn bước, đúng thứ tự, trước khi coi một đơn vị công việc là xong: `python -X utf8 -m pytest -m "not slow"` → `python -X utf8 -m src.pipeline run --stage all` → `python -X utf8 -m src.pipeline run --stage stats` → mở dashboard; dừng ngay ở bước đỏ đầu tiên và để CI chạy phần còn lại sau khi push. (nguồn: người làm chốt ở phỏng vấn Q4 = A và Q5 = B — tầng `stats` là bước thứ ba, trước dashboard; `README.md` mục "Test"; `ci.yml:40-46`; `pytest.ini`)

## Forbidden

- NEVER sửa, ghi đè hay "làm sạch tại chỗ" bất kỳ tệp nào trong `dataset/`. (nguồn: `README.md` mục "Lưu ý"; `AGENTS.md`; `ideation/scope-definition/scope-document.md` §3)
- NEVER join trực tiếp bảng geolocation thô vào customers/orders — luôn gộp về một dòng mỗi `zip_code_prefix` trước. (nguồn: `AGENTS.md` — 52,6 dòng mỗi zip, join thẳng làm 99.441 dòng nổ thành 15.083.455; `src/clean/geolocation.py`)
- NEVER join payments/reviews chưa gộp vào dữ liệu cấp dòng hàng, vì doanh thu và số đếm review sẽ bị nhân lên. (nguồn: `AGENTS.md`; `business-overview.md` §4)
- NEVER chỉnh tay tệp CSV trung gian; mọi tầng phải tái lập được từ CSV gốc. (nguồn: `AGENTS.md`; `README.md`; `architecture.md` §1 — pipeline chạy lại từ `dataset/`)
- NEVER commit `data/`, `warehouse/`, `logs/`, `inbox/`, `.venv/` hay `.coverage`. (nguồn: `.gitignore:1-10`)
- NEVER đổi một con số KPI baseline, một số dòng kỳ vọng hay một danh sách bảng ở đúng một chỗ — cùng một sự thật đang được khai ở 3–6 nơi và sẽ lệch âm thầm. (nguồn: `dependencies.md` §3; `TD-02`)
- NEVER import một thư viện bên thứ ba chưa được ghim trong `requirements.txt` — kể cả gói thống kê/học máy (`scipy`, `statsmodels`, `scikit-learn`) và `numpy`, vốn chỉ có mặt gián tiếp qua `pandas`. (nguồn: `requirements.txt`; `technology-stack.md` §2 và §6.3; `dependencies.md` §4.1)
- NEVER đưa `payment_value` vào một KPI doanh thu mà không nêu rõ định nghĩa doanh thu của chỉ số đó. (nguồn: `AGENTS.md` — 378 đơn lệch > 0,01 BRL; `src/common/kpis.py` — `validate_ledger`)
- NEVER đặt `--cov-fail-under` lên riêng bộ nhanh hay hạ ngưỡng phủ để một bước pass. (nguồn: phỏng vấn Q6 = A; `ci.yml:43-46`; `org.md` — "Build and Test ... may not be weakened to make a step pass")
- NEVER thêm phụ thuộc kiểm tra kiểu tĩnh (`mypy`, `pyright`) — đây là quyết định đã chốt, không phải thiếu sót. (nguồn: `code-quality-assessment.md` §4; `technology-stack.md` §5)
- NEVER dọn định dạng toàn repo trong một thay đổi chức năng; mã cũ dọn theo từng tệp khi có người sửa tới. (nguồn: `ci.yml:29-30`; `ruff.toml:24-25`; `README.md` mục "Lint và định dạng")
- NEVER hard-code id thẻ/vùng của tab "Tích hợp" trong mã khi hợp đồng YAML đã khai chúng. (nguồn: `config/integration-tab.yaml`; `src/integration/card.py` — `load_tab_config`; `architecture.md` §2 bảng "Phương án đã cân nhắc")
