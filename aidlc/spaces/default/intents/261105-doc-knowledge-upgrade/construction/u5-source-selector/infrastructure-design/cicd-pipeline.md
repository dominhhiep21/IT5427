# CI/CD Pipeline — u5-source-selector

Nguồn: `nfr-design/security-design.md` (ADR-U5-S1..S8), `nfr-design/logical-components.md` (L1–L5, §3 phạm vi hỏng), `nfr-requirements/tech-stack-decisions.md` (TS-U5-1..15, NFR1.1–NFR6.2), `nfr-requirements/security-requirements.md` (SR-U5-1..16), `functional-design/functional-spec.md` (W1–W4), `inception/domain-design/components.md` (thành phần `SourceSelector`), `inception/contract-design/contract-summary.md` (C2, C3, C7). Hiện trạng lấy từ `.github/workflows/ci.yml`, `requirements.txt`, `ruff.toml`, `pytest.ini`.

Đơn vị này là **thư viện thuần, không có hạ tầng triển khai**. Tài liệu này vì vậy không mô tả máy chủ, vùng mạng hay tài nguyên đám mây — nó mô tả **đường đi từ mã tới "coi như xong"**, tức CI đang có thật trong repo và cổng xác nhận của đơn vị.

## 1. Đường ống hiện có

| Bước | Lệnh | Chặn khi | Nguồn |
|---|---|---|---|
| Kích hoạt | `push` / `pull_request` lên `main` và `feature/update-ui-ux` | — | `ci.yml` dòng 3–11 |
| Máy chạy | `windows-2022` (ghim, không dùng nhãn trôi) | — | `ci.yml` dòng 16 |
| Cài đặt | `pip install -r requirements.txt` | Cài lỗi | `ci.yml` dòng 26 |
| Lint + định dạng | `ruff check .` và `ruff format --check` trên danh sách tệp tường minh | Một vi phạm | `ci.yml` dòng 28–33 |
| Dựng dữ liệu | `python -X utf8 -m src.pipeline run --stage all` | `QualityGate` hoặc `KpiReconciler` đỏ | `ci.yml` dòng 35–38 |
| Test nhanh | `python -X utf8 -m pytest -m "not slow"` | Một test đỏ | `ci.yml` dòng 40–41 |

Không có bước build, đóng gói, deploy: sản phẩm chạy trực tiếp từ mã nguồn, nên "artefact" là chính cây mã tại một commit.

**Sự thật về ngưỡng phủ:** CI hiện **không** cưỡng chế `--cov-fail-under`. `ci.yml` dòng 41 chạy `pytest -m "not slow"` không có cờ coverage; `pytest.ini` chỉ có `-ra`. Ngưỡng 80% hiện chỉ được đo khi có người chạy lệnh có `--cov`, đúng như `team.md` đã ghi ("ngưỡng đặt ra, chưa được cưỡng chế tự động"). Đơn vị này sửa điều đó ở §2.

## 2. Đơn vị này thêm gì vào đường ống

| Thay đổi | Vì sao | Ở đâu |
|---|---|---|
| **Không** thêm gói vào `requirements.txt` | TS-U5-5: chỉ dùng `yaml`, `pathlib`, `dataclasses` — đều đã ghim | `requirements.txt` không đổi |
| **Không** thêm bước pipeline mới | Đơn vị là thư viện; U6 quyết định khi nào gọi (TS-U5-13), không có lời gọi nào trong `stages.py` | `src/pipeline/stages.py` không đổi |
| Thêm `tests/unit/test_integration_selector.py` vào danh sách format của CI | `ruff format --check` trong `ci.yml` liệt kê **từng tệp test**, không theo thư mục | `ci.yml` dòng 33 |
| Thêm một bước **đo phủ toàn bộ** vào CI: `python -X utf8 -m pytest --cov=src --cov-fail-under=80` (dùng Python của runner, chạy cả bộ `slow`) | `team.md` và `verification-command.txt` định nghĩa ngưỡng 80% trên **toàn bộ** bộ test; bảy mô-đun `src/` không có unit test trực tiếp nên phần phủ của chúng chỉ đến từ bộ `slow`. Đặt cờ lên bộ nhanh sẽ đỏ ngay lần chạy đầu | `ci.yml` — bước mới sau bước test nhanh |
| Thêm bước smoke nạp cấu hình thật: `python -X utf8 -c "..."` (Python của runner) | Không có bước nào khác chứng minh `config/integration-sources.yaml` đã commit nạp được. **Dùng `python` của runner, không dùng `.venv`**: `ci.yml` cài bằng `pip install -r requirements.txt` vào Python của runner và không tạo venv | `ci.yml` — bước mới sau bước đo phủ |
| `src/integration/` đã nằm trong phạm vi format | `selector.py` và `models.py` được kiểm tự động | `ci.yml` dòng 33 |
| `config/integration-sources.yaml` là tệp dữ liệu | Không lint, không format; được nạp thật ở bước smoke của đơn vị (§4 bước 6) | `config/` (mới) |
| `config.yaml` thêm một khoá | Trường `integration_sources_path` trong `AppConfig` (R-07 của NFR Requirements) | `config.yaml` + `src/config.py` |

## 3. Cổng chất lượng của đơn vị

| Chỉ tiêu | Cổng | Chạy ở đâu | Ghi chú |
|---|---|---|---|
| NFR3.1 (lint/format) | `ruff check` + `ruff format --check` trên **đúng năm tệp Python** của TS-U5-15: `src/integration/selector.py`, `src/integration/models.py`, `src/common/exceptions.py`, `src/config.py`, `tests/unit/test_integration_selector.py` | §4 bước 3–4 và CI bước 4 | Hai tệp YAML không thuộc phạm vi ruff; tệp ngoài danh sách (ví dụ `src/common/io.py`) không bị format lây |
| NFR2.2 (mỗi mô-đun có test riêng) | `pytest tests/unit/test_integration_selector.py --cov=src.integration.selector --cov-fail-under=90` — ngưỡng riêng của đơn vị trên chính mô-đun mới | §4 bước 4; rà thêm trong review | Tệp rỗng hoặc test hình thức sẽ trượt ngưỡng, khác với chỉ đếm sự tồn tại của tệp |
| NFR2.1 (phủ ≥ 80%) | `pytest --cov=src --cov-fail-under=80` trên **toàn bộ** bộ test (nhanh + `slow`) | §4 bước 5 và CI (bước mới ở §2) | Đúng định nghĩa trong `team.md` và `verification-command.txt`; không hạ ngưỡng để cho qua |
| NFR5.1 (5 KPI lệch 0) | `python -X utf8 -m src.pipeline run --stage all` (QualityGate + KpiReconciler) | CI bước "Dựng dữ liệu"; §4 bước 3 khi chạy tay | Đơn vị không ghi vào `data/`/`warehouse/` |
| NFR5.2 (số dòng 11 view) | `pytest -m slow` — `tests/integration/test_u2_end_to_end.py` khẳng định số dòng 11 view | Bước đo phủ toàn bộ ở §2 (chạy cả bộ `slow`) và Build and Test | Từ khi §2 thêm bước đo phủ toàn bộ, bộ `slow` chạy trong CI; trước thay đổi đó nó không chạy |
| NFR6.1 (không mạng) | Rà mã: không `urllib`/`requests`/`socket`/`httpx` trong `selector.py` (SR-U5-3) | Rà trong review — không phải một bước §4, vì lint không bắt được | Ghi ở ADR-U5-S5 |
| SR-U5-15 | Test âm: `has_data: "false"`, `latency_ms: "800"`, `latency_ms: -1` | Bộ test của đơn vị | Ba ca âm bắt buộc |
| SR-U5-14 | Test âm: `tables: [olist_khong_ton_tai]` | Bộ test của đơn vị | Một ca âm |

## 4. Cổng xác nhận của đơn vị (đúng thứ tự)

Mọi bước ghim đúng đường dẫn Python của venv, không dùng `python` trần. Thứ tự theo `ci.yml`: **dựng dữ liệu trước khi chạy test**, vì bộ test nhanh chưa hermetic (`TD-09`) và cần `warehouse/` + `data/marts/` có sẵn.

1. Lint: `.venv\Scripts\python.exe -X utf8 -m ruff check src/integration/selector.py src/integration/models.py src/common/exceptions.py src/config.py tests/unit/test_integration_selector.py`
2. Định dạng: `.venv\Scripts\python.exe -X utf8 -m ruff format --check src/integration/selector.py src/integration/models.py src/common/exceptions.py src/config.py tests/unit/test_integration_selector.py`
3. Dựng dữ liệu: `.venv\Scripts\python.exe -X utf8 -m src.pipeline run --stage all` — xác nhận `QualityGate` và `KpiReconciler` vẫn xanh sau khi thêm đơn vị.
4. Test của riêng đơn vị và ngưỡng phủ của mô-đun: `.venv\Scripts\python.exe -X utf8 -m pytest tests/unit/test_integration_selector.py --cov=src.integration.selector --cov-fail-under=90`.
5. Bộ nhanh và ngưỡng phủ **toàn bộ**: `.venv\Scripts\python.exe -X utf8 -m pytest --cov=src --cov-fail-under=80` (không có `-m "not slow"` — ngưỡng 80% tính trên cả bộ `slow`).
6. Smoke nạp cấu hình thật: `.venv\Scripts\python.exe -X utf8 -c "from pathlib import Path; from src.integration.selector import load_source_catalogue; from src.integration.schema import load_schema, build_field_catalogue; c=load_schema(Path('config/mediated-schema.yaml')); cat=load_source_catalogue(Path('config/integration-sources.yaml'), build_field_catalogue(c)); print(len(cat.sources), len(cat.query_fields))"` — in ra `3 3`. Đây là bước duy nhất chứng minh tệp cấu hình đã commit thật sự nạp được; nó cũng là bước mới được thêm vào CI ở §2.
7. NFR5.2 (số dòng 11 view) không phải một bước riêng: bước 5 đã chạy cả bộ `slow`, và đó là nơi `test_u2_end_to_end.py` đo nó. Ở **Build and Test**, chạy lại riêng nếu cần chẩn đoán: `.venv\Scripts\python.exe -X utf8 -m pytest -m slow`.

Chuỗi này khớp `team.md` (`## Deployment`): chạy từng bước, dừng ngay khi một bước đỏ; không bỏ bước nào vì "lần trước vẫn chạy được".

## 5. Hoàn nguyên

Đơn vị không có trạng thái triển khai, nên hoàn nguyên là thao tác trên mã và cấu hình, không phải trên hạ tầng:

| Thay đổi | Cách hoàn nguyên |
|---|---|
| `src/integration/selector.py`, `tests/unit/test_integration_selector.py` | Xoá hai tệp; **trước khi xoá, gỡ lời gọi ở U6** (`load_source_catalogue`, `select_source`) và ở U3 (đọc `SourceSelection`) — hai đơn vị này là consumer duy nhất |
| Bốn kiểu mới trong `src/integration/models.py` | Xoá bốn lớp sau khi U6/U3 thôi import; C1/C2/C6 không phụ thuộc chúng |
| `NoSourceAvailableError` trong `src/common/exceptions.py` | Xoá lớp sau khi U3/U6 thôi bắt nó |
| `integration_sources_path` trong `AppConfig`/`config.yaml` | Xoá trường và khoá; `load_config` không có trường này trước đó |
| `config/integration-sources.yaml` | Xoá tệp |
| Bước đo phủ toàn bộ trong `ci.yml` | Xoá bước mới (không còn `--cov-fail-under=80` trong CI); ngưỡng quay lại chỉ còn ở lệnh xác nhận của ý định |
| Bước smoke trong `ci.yml` | Xoá bước mới; tệp cấu hình khi đó chỉ còn được kiểm bởi bộ unit test dùng fixture |

## 6. Không có gì để triển khai

| Hạng mục | Trạng thái | Vì sao |
|---|---|---|
| Máy chủ, container, dịch vụ đám mây | Không có | Đơn vị là thư viện trong tiến trình dashboard |
| Môi trường staging/production | Không có | Cả dự án chạy local (`team.md` — Deployment) |
| Bí mật, biến môi trường | Không có | SR-U5-2: không token, không API key |
| Sao lưu, khôi phục | Không áp dụng | Không có trạng thái nào do đơn vị sở hữu; tệp cấu hình đi qua git |
| Giám sát hạ tầng | Không áp dụng | Không có tài nguyên để giám sát; log của đơn vị là log ứng dụng (ADR-U5-S5) |
