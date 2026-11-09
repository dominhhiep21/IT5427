# Ràng buộc cứng đã phát hiện — Olist E-commerce Data Pipeline

> Chỉ ghi những ràng buộc **thật sự có bằng chứng trong repo này**: một chỉ thị tường minh trong
> `AGENTS.md`/`README.md`, một ràng buộc đã chốt trong `scope-document.md`, một điều mà bộ test
> hiện tại **cưỡng chế** (làm sai là test đỏ), hoặc một ràng buộc cứng do người quyết định tuyên bố
> trong buổi phỏng vấn. Không có ràng buộc nào dưới đây là mong muốn suông.
>
> Phần lớn quy tắc đến từ bằng chứng tĩnh. Hai quy tắc cuối của `## Mandated` đến từ **phỏng vấn
> Practices Discovery ngày 2026-11-05** (`practices-discovery-questions.md`, Q3 và Q4) — người làm
> tuyên bố chúng như **ràng buộc cứng**, không phải khẩu vị. Các câu trả lời còn lại của buổi phỏng vấn
> là **thực hành** (nhánh làm việc, TDD, lát cắt mỏng, lệnh xác nhận) nên nằm ở `team-practices.md`,
> không nằm ở đây.
>
> Nguồn được viết ngay sau mỗi quy tắc để người đọc kiểm lại được.

## Mandated

- ALWAYS giữ `dataset/` nguyên trạng và ghi mọi dữ liệu dẫn xuất vào `data/`, `warehouse/`, `logs/`, `inbox/`. (nguồn: `AGENTS.md` dòng 7; `README.md` mục "Lưu ý"; ràng buộc `TC-05` trong `ideation/scope-definition/scope-document.md`)
- ALWAYS chạy Python bằng UTF-8 — `python -X utf8 ...` hoặc `PYTHONUTF8=1` — vì đường dẫn workspace có ký tự tiếng Việt và dữ liệu có ký tự Bồ Đào Nha. (nguồn: `AGENTS.md` dòng 17; `README.md` mục "Cài đặt"; `docs/runbook.md`)
- ALWAYS gộp `olist_geolocation_dataset.csv` về đúng một dòng cho mỗi `zip_code_prefix` (một lat/lng, một city/state) **trước** khi join vào customers/orders. (nguồn: `AGENTS.md` dòng 35 — 52,6 dòng mỗi zip, join thẳng làm 99.441 dòng nổ thành 15.083.455; `tests/data_quality/test_real_dataset.py` khẳng định 19.015 dòng sau gộp)
- ALWAYS gộp payments và reviews về một dòng cho mỗi `order_id` trước khi join vào dữ liệu cấp dòng hàng. (nguồn: `AGENTS.md` dòng 36; `src/ingest/reports.py` hàm `reconcile_payments`; `business-overview.md` §4)
- ALWAYS nêu rõ grain (order / order-item / payment / review) trước mỗi lần merge và kiểm lại số dòng + tính duy nhất của khoá sau khi merge. (nguồn: `AGENTS.md` dòng 45; `src/integrate/validate.py` — `StarSchemaValidator` có 9 check số dòng, 9 check khoá, check join không nở; `tests/integration/test_u2_end_to_end.py` khẳng định lại từng con số)
- ALWAYS nêu rõ định nghĩa doanh thu đang dùng (`price + freight_value` của đơn `delivered`, hay `payment_value`) mỗi khi thêm KPI hoặc truy vấn mới. (nguồn: `AGENTS.md` dòng 37 — 378 đơn lệch > 0,01 BRL; `business-overview.md` §4; `src/integrate/reconcile.py` dùng `price + freight_value`)
- ALWAYS lọc trạng thái đơn một cách tường minh cho mọi phân tích doanh thu/giao vận, không dựa vào mặc định ngầm. (nguồn: `AGENTS.md` dòng 40; `KpiFilters.order_status = "delivered"` trong `src/common/types.py`; `business-overview.md` §7; `TD-12` mô tả cái giá của việc lọc ngầm)
- ALWAYS cập nhật **tất cả** nơi khai báo cùng một sự thật dữ liệu trong cùng một thay đổi có chủ đích — `src/ingest/schemas.py`, `src/quality/gate.py`, `src/quality/allowlist.py`, `src/integrate/validate.py`, `src/integrate/reconcile.py`, `src/integrate/catalog.py` (`VIEW_TABLES`), `README.md` và test tương ứng. (nguồn: `dependencies.md` §3 — mỗi sự thật đang khai ở 3–6 nơi; `TD-02`; `TD-15`)
- ALWAYS cập nhật đồng thời test khẳng định hình dạng dashboard khi đổi dashboard: 3 tab, 2 callback, 9 output, 11 view. (nguồn: `tests/unit/test_dashboard_smoke.py` dòng 14–26; `tests/integration/test_u3_end_to_end.py` dòng 46–48; `tests/integration/test_u2_end_to_end.py` dòng 44; `code-quality-assessment.md` §7.1)
- ALWAYS ghim mọi phụ thuộc trực tiếp vào `requirements.txt`, cài nó trong `.venv` của repo (không cài vào môi trường Python toàn cục), và ghi rõ lý do khi thêm một thư viện mới. (nguồn: `AGENTS.md` dòng 16; `README.md` mục "Cài đặt"; `requirements.txt` 8 gói ghim; ràng buộc `TC-03` trong `ideation/feasibility/constraint-register.md`; `dependencies.md` §1.1)
- ALWAYS truyền tham số SQL qua placeholder `?` và lấy tên cột / `GROUP BY` từ dict hằng, không nối chuỗi từ đầu vào người dùng. (nguồn: `src/analytics/service.py` hàm `_where`; `code-quality-assessment.md` §1 — "Kiểm soát SQL an toàn"; `code-structure.md` §3.1)
- ALWAYS giữ cho `quality` chế độ `full` và `KpiReconciler` xanh sau mỗi thay đổi cleaning/ghép bản ghi, hoặc cập nhật allowlist/baseline một cách có kiểm soát và ghi lại lý do; chạy test trước và sau khi thêm phần mới. (nguồn: `src/quality/allowlist.py`, `src/integrate/reconcile.py`; `code-quality-assessment.md` §7.3 mục 1; ràng buộc `TC-06` trong `constraint-register.md` — "Phải chạy test trước và sau khi thêm phần mới")
- ALWAYS giữ **độ phủ test tối thiểu 80%** cho mã trong `src/` — đo bằng `pytest --cov=src`, không hạ ngưỡng để cho một bước pass. (nguồn: phỏng vấn `practices-discovery-questions.md` Q3 = C, 2026-11-05; `pytest-cov` đã có trong `requirements.txt`, lệnh `--cov=src` có trong `README.md`; ngưỡng hiện **chưa** được cưỡng chế tự động — `pytest.ini` chưa có `--cov-fail-under`)
- ALWAYS chạy `ruff check` và `ruff format --check` sạch trước khi coi một thay đổi là xong; mã chưa qua ruff không được merge. (nguồn: phỏng vấn `practices-discovery-questions.md` Q4 = B, 2026-11-05; hiện repo chưa có `ruff.toml`/`pyproject.toml` — cấu hình và ghim phiên bản `ruff` sẽ được thêm trong đợt này, theo quy tắc ghim phụ thuộc ở trên)

## Forbidden

- NEVER sửa, ghi đè hay "làm sạch tại chỗ" bất kỳ tệp nào trong `dataset/`. (nguồn: `AGENTS.md` dòng 7; `README.md` mục "Lưu ý" — "`dataset/` là dữ liệu gốc, không sửa")
- NEVER join trực tiếp bảng geolocation thô vào customers/orders — luôn gộp về một dòng mỗi `zip_code_prefix` trước. (nguồn: `AGENTS.md` dòng 35)
- NEVER join payments/reviews chưa gộp vào dữ liệu cấp dòng hàng, vì doanh thu và số đếm review sẽ bị nhân lên. (nguồn: `AGENTS.md` dòng 36)
- NEVER chỉnh tay tệp CSV trung gian; mọi tầng phải tái lập được từ CSV gốc. (nguồn: `AGENTS.md` dòng 46)
- NEVER commit `data/`, `warehouse/`, `logs/`, `inbox/`, `.venv/` hay `.coverage` — chúng là sản phẩm sinh ra và đã bị `.gitignore`. (nguồn: `.gitignore` dòng 1–10)
- NEVER đổi một con số KPI baseline, một số dòng kỳ vọng hay một danh sách bảng ở đúng một chỗ — cùng một sự thật đang được khai ở 3–6 nơi và sẽ lệch âm thầm. (nguồn: `dependencies.md` §3; `TD-02`)
- NEVER import một thư viện bên thứ ba chưa được ghim trong `requirements.txt` (ví dụ `pyspark`, `scikit-learn`, `rapidfuzz` — đều không có trong tệp). (nguồn: `requirements.txt`; `technology-stack.md` §2 — 8 gói ghim là toàn bộ phụ thuộc bên thứ ba; `code-quality-assessment.md` §7.2 — ghép bản ghi mờ sẽ cần gói mới. Lưu ý: danh sách "chưa cài" trong `AGENTS.md` dòng 15 **đã lỗi thời**, xem `evidence.md` §4)
- NEVER đưa `payment_value` vào một KPI doanh thu mà không nêu rõ định nghĩa doanh thu của chỉ số đó. (nguồn: `AGENTS.md` dòng 37; `business-overview.md` §4)
