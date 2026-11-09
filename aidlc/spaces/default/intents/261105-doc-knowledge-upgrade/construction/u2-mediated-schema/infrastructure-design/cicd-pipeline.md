# CI/CD Pipeline — u2-mediated-schema

Nguồn: `nfr-design/security-design.md` (ADR-U2-S1..S6), `nfr-design/logical-components.md` (L1–L6, §3 phạm vi
hỏng), `inception/domain-design/components.md` (thành phần `MediatedSchema`), `functional-design/functional-spec.md`
(Workflow 1–4), `inception/contract-design/contract-summary.md` (C1, C2, C6, C8). Hiện trạng lấy từ
`.github/workflows/ci.yml` (5 bước), `requirements.txt` (9 gói ghim, có `ruff`), `ruff.toml`, `pytest.ini`.

Đơn vị này là **thư viện thuần, không có hạ tầng triển khai**. Tài liệu này vì vậy không mô tả máy chủ,
vùng mạng hay tài nguyên đám mây — nó mô tả **đường đi từ mã tới "coi như xong"**, tức CI đang có thật
trong repo và cổng xác nhận của đơn vị.

## 1. Đường ống hiện có

| Bước | Lệnh | Chặn khi | Nguồn |
|---|---|---|---|
| Kích hoạt | `push` / `pull_request` lên `main` và `feature/update-ui-ux` | — | `ci.yml` dòng 3–11 |
| Máy chạy | `windows-2022` (ghim, không dùng nhãn trôi) | — | `ci.yml` dòng 16 |
| Cài đặt | `pip install -r requirements.txt` | Cài lỗi | `ci.yml` dòng 26 |
| Lint + định dạng | `ruff check .` và `ruff format --check src/integration src/linkage <danh sách test tường minh>` | Một vi phạm | `ci.yml` dòng 28–33 |
| Dựng dữ liệu | `python -X utf8 -m src.pipeline run --stage all` | `QualityGate` hoặc `KpiReconciler` đỏ | `ci.yml` dòng 35–38 |
| Test nhanh | `python -X utf8 -m pytest -m "not slow"` | Một test đỏ | `ci.yml` dòng 40–41 |

Không có bước build, đóng gói, deploy: sản phẩm chạy trực tiếp từ mã nguồn (`python -m ...`), nên
"artefact" là chính cây mã tại một commit.

## 2. Đơn vị này thêm gì vào đường ống

| Thay đổi | Vì sao | Ở đâu |
|---|---|---|
| **Không** thêm gói vào `requirements.txt` | TS-U2-6: chỉ dùng `yaml`, `csv`, `re`, `pathlib`, `dataclasses` — đều đã có | `requirements.txt` không đổi |
| **Không** thêm bước pipeline mới | Đơn vị là thư viện; bên gọi quyết định khi nào nạp, và không có lời gọi nào trong `stages.py` | `src/pipeline/stages.py` không đổi |
| Thêm tệp test mới vào danh sách format của CI | `ruff format --check` trong `ci.yml` liệt kê **từng tệp test**, không theo thư mục; tệp `tests/unit/test_integration_schema.py` sẽ không được kiểm định dạng nếu không thêm | `ci.yml` dòng 33 (sửa cùng thay đổi sinh mã) |
| `src/integration/` đã nằm trong phạm vi format | `schema.py` và `models.py` được kiểm tự động, không cần thêm dòng | `ci.yml` dòng 33 |

## 3. Cổng chất lượng của đơn vị

| Chỉ tiêu | Cổng | Chạy ở đâu | Ghi chú |
|---|---|---|---|
| NFR3.1 (lint/format) | `ruff check .` + `ruff format --check` | CI, bước 4 | Mã mới phải sạch ngay; mã cũ dọn theo từng tệp khi sửa tới |
| NFR2.2 (mỗi mô-đun có test riêng) | Sự tồn tại của `tests/unit/test_integration_schema.py` | Rà trong review + CI chạy nó | L1–L4 dùng chung một tệp nguồn nên một tệp test là đủ theo NFR2.2 |
| NFR2.1 (phủ ≥ 80%) | `pytest --cov=src --cov-fail-under=80` | **Cục bộ**, trong Construction Verification Command | Xem §7: CI **không** chạy cổng này |
| NFR1.1 (≤ 2 giây) | Test khẳng định `view.elapsed_ms <= 2000` | Test nhanh | Đo trên fixture nhỏ; giá trị thật ghi vào `elapsed_ms` khi chạy trên `dataset/` |
| NFR6.1 (không mạng) | `--stage all` chạy không gọi mạng (chỉ đọc cache IBGE) | CI, bước 5 | Không có `urllib`/`requests` trong `src/integration/` |
| NFR5.1/NFR5.2 (không hồi quy) | `QualityGate` + `KpiReconciler` | CI, bước 5 | Đơn vị không ghi vào mart/view nên chỉ cần giữ nguyên |

## 4. Triển khai và quay lui

| Khía cạnh | Lựa chọn | Lý do |
|---|---|---|
| Mô hình chạy | Một tiến trình trên máy local, không container, không đám mây | `technology-stack.md` §1; NFR6 |
| Chiến lược "triển khai" | **Recreate**: dừng tiến trình, cập nhật mã, chạy lại | Không có nhiều phiên bản chạy song song, không có lưu lượng để chia |
| Blue-green / canary | **Không áp dụng** | Một người dùng, một tiến trình, không có bộ cân bằng tải |
| Môi trường | Một môi trường duy nhất (máy người làm) | Không có staging/production (`team.md` — Deployment) |
| Quay lui | `git checkout <commit trước>` rồi chạy lại chuỗi xác nhận | Phiên bản = commit hash; không có artefact đóng gói để quay lui |
| Dữ liệu sinh ra | Xoá `data/`, `warehouse/`, `logs/`, `inbox/` rồi chạy `--stage all` | Bốn thư mục là sản phẩm, bị `.gitignore` |
| Kiểm tra khói | `QualityGate` (chế độ `full`) + `KpiReconciler` | Hai cổng đã có, đóng vai trò smoke test |

**Chuỗi xác nhận của một đơn vị** (team đã chốt, đúng thứ tự): `pytest -m "not slow"` → `python -X utf8 -m
src.pipeline run --stage all` → mở dashboard xem bằng mắt. Riêng đơn vị này không có mặt trên dashboard
nên bước 3 chỉ để giữ thói quen của đợt.

## 5. Bí mật trong CI/CD

| Hạng mục | Trạng thái |
|---|---|
| Bí mật của sản phẩm | **Không có.** Không API key, không token, không mật khẩu; nguồn là CSV cục bộ và cache IBGE đã commit |
| Biến môi trường | Chỉ `PYTHONUTF8`/`-X utf8` cho mã hoá; không có biến bí mật (SR-U2-2) |
| Nếu sau này cần bí mật | Dùng secrets của GitHub Actions, không bao giờ đặt trong repo (luật của `org.md`) |
| Tệp cấu hình | `config/mediated-schema.yaml` là cấu hình công khai, không phải bí mật; sửa nó đi qua git |

## 6. Phiên bản và artefact

- **Phiên bản = commit hash**, không có tag hay số phát hành (thói quen hiện tại). OQ2 của
  `requirements.md` vẫn mở: có cần tag/CHANGELOG cho mốc nộp hay không.
- **Artefact = cây mã nguồn** tại commit đó; không có bước đóng gói nên không có artefact nhị phân.
- `data/`, `warehouse/`, `logs/`, `inbox/`, `.venv/`, `.coverage` bị `.gitignore` — không phải artefact phát hành.

## 7. Khoảng trống đã biết

| # | Khoảng trống | Ảnh hưởng | Đề xuất |
|---|---|---|---|
| G1 | CI **không** chạy `--cov-fail-under=80`; ngưỡng phủ chỉ nằm trong Construction Verification Command | Hồi quy độ phủ không chặn merge | Thêm bước đo phủ vào `ci.yml`; ngoài phạm vi đơn vị này nên chỉ ghi lại, không tự sửa |
| G2 | `ruff format --check` liệt kê tay từng tệp test | Tệp test mới có thể lọt khỏi kiểm định dạng | Thêm `tests/unit/test_integration_schema.py` vào danh sách trong cùng thay đổi sinh mã (§2) |
| G3 | Bộ test nhanh chưa hermetic (TD-09): cần `warehouse/` và `data/marts/` | Máy mới clone sẽ đỏ cho tới khi chạy `--stage all` một lần | CI đã xử lý bằng cách dựng dữ liệu trước; cục bộ vẫn là điều kiện đã biết |
| G4 | Test `slow` (dữ liệu thật) không chạy trong CI | Hồi quy dữ liệu chỉ bắt được khi chạy tay | Giữ nguyên: CI đã chạy `--stage all` nên `QualityGate`/`KpiReconciler` vẫn là cổng dữ liệu |
| G5 | Không có môi trường thứ hai để thử trước | Sai sót chỉ lộ trên máy người làm | Chấp nhận: sản phẩm một người, dữ liệu bất biến, quay lui bằng commit |

## 8. Việc cần làm ở bước sinh mã

- Thêm `tests/unit/test_integration_schema.py` vào danh sách `ruff format --check` của `ci.yml` (G2).
- Không sửa `requirements.txt`, `stages.py`, `micro_batch` hay `config.yaml`.
- Chạy đủ chuỗi xác nhận của đơn vị trước khi coi là xong: `pytest -m "not slow"`, rồi `--stage all`, rồi
  `pytest --cov=src --cov-fail-under=80`.
