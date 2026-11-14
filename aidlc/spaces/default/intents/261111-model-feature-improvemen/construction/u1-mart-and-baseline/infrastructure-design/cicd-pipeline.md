# CI/CD Pipeline — u1-mart-and-baseline

Đơn vị: `u1-mart-and-baseline` (kind `library`). Nguồn: `../nfr-design/security-design.md`, `../nfr-design/logical-components.md`, `../../../inception/domain-design/components.md` (MartIntegration), `../functional-design/functional-spec.md`, `.github/workflows/ci.yml`, `team.md` `## Deployment`.

**Kết luận ngắn: không có hạ tầng nào để dựng, và pipeline đã tồn tại.** Dự án chạy từ mã nguồn trên máy một người; không có staging, không production, không container, không scheduler. Vì vậy tài liệu này **không** thiết kế hạ tầng — nó ghi đơn vị này **chạm vào pipeline hiện có ở đâu**, và chỗ nào phải sửa cùng lúc với mã.

## Pipeline hiện có — 9 bước, bất biến với đơn vị này

`.github/workflows/ci.yml`, chạy trên `windows-2022` (ghim image), Python 3.13, cache pip, trigger `push` **và** `pull_request` trên ba nhánh `main`, `feature/update-ui-ux`, `feature/analysis-and-models`.

| # | Bước | Đơn vị này có đổi? |
|---|---|---|
| 1 | checkout | Không |
| 2 | setup-python 3.13 | Không |
| 3 | cài phụ thuộc từ `requirements.txt` | Không — không thêm gói |
| 4 | `ruff check .` + `ruff format --check` | **Có** — xem CP1 |
| 5 | `run --stage all` | **Có** — giờ có thêm ba cột |
| 6 | `run --stage stats` | Không (tầng stats thuộc U2) |
| 7 | bộ nhanh `pytest -m "not slow"` | **Có** — thêm test mới |
| 8 | `pytest --cov=src --cov-fail-under=80` | Không — cổng giữ nguyên |
| 9 | smoke nạp `config/integration-sources.yaml` | Không |

## CP0 — Bước 5 là nơi CI cưỡng chế bất biến của đơn vị này

**Vấn đề:** bảng trên chỉ ghi "bước 5 giờ có thêm ba cột" — nhưng bước đó còn là chỗ **CI thật sự cưỡng chế** điều đơn vị này tồn tại để bảo vệ.

**Thiết kế:** `run --stage all` chạy `integrate_all`, tức chạy `StarSchemaValidator.enforce` (9 check số dòng) và `KpiReconciler.enforce` (5 KPI). Nếu thêm ba cột làm lệch một dòng hay một KPI, **bước 5 đỏ** — không phải bước 7 hay 8. Đây là cổng mạnh nhất mà CI có cho đơn vị này, và nó chạy trên **dữ liệu thật** trong repo.

**Hệ quả:** một thay đổi làm hỏng mart sẽ đỏ ở bước 5, trước khi bất kỳ test nào chạy. Đọc log ở bước 5 là cách nhanh nhất để biết hỏng ở đâu.

## CP1 — Tệp nguồn mới phải vào danh sách khai tay của `ruff format --check`

**Vấn đề:** bước 4 chỉ chạy `ruff format --check` trên **danh sách khai tay** trong `ci.yml:35` (`TD-20`), không phải toàn repo. Một tệp mới không có trong danh sách sẽ **không được kiểm định dạng** — im lặng, không đỏ.

**Yêu cầu:** mọi tệp `.py` mới của đơn vị này phải được thêm vào danh sách đó **trong cùng thay đổi** tạo tệp. Đây là bẫy đã ghi trong `project.md` `## Mandated` và `team.md` `## Testing Posture`, và `tests/unit/test_ci_config.py` chỉ canh 14 tệp của đợt trước — nó **không** canh tệp mới.

**Hệ quả nếu quên:** CI xanh nhưng tệp chưa được format, và lần sau ai thêm tệp đó vào danh sách sẽ thấy đỏ ở một thay đổi không liên quan.

## CP2 — Thêm tệp test thì thêm dòng vào danh sách, không đổi ngưỡng phủ

**Vấn đề:** cổng phủ 80% chạy trên **toàn bộ** bộ test (bước 8). Test mới của đơn vị này làm tăng cả tử số lẫn mẫu số.

**Yêu cầu:** không hạ `--cov-fail-under`, không đặt cờ lên riêng bộ nhanh, không thêm `per-file-ignores` mới. Nếu độ phủ tụt, sửa bằng cách viết test chứ không bằng cách nới cổng.

## CP3 — Không có bước deploy nào, và điều đó là đúng

**Vấn đề:** một pipeline không deploy trông như thiếu bước.

**Thiết kế:** cố ý không có. "Phát hành" của dự án này là **chạy từ mã nguồn trên máy local sau khi CI xanh**, theo chuỗi xác nhận bốn bước: bộ nhanh → `run --stage all` → `run --stage stats` → **mở dashboard bằng mắt**. `scripts/verify_intent.ps1` (đã được duyệt làm lệnh xác nhận của intent) tự động hoá **ba** bước đầu và cộng thêm `pytest --cov=src --cov-fail-under=80`; bước thứ tư **không** tự động hoá được — script chỉ in câu nhắc mở dashboard khi thoát. Nói đúng chỗ đó quan trọng, vì "script đã chạy hết chuỗi" là một kết luận sai dễ mắc.

**Vì sao không thêm deploy:** không có môi trường thứ hai để deploy tới. Thêm một bước deploy giả sẽ là bước luôn xanh và không kiểm gì — tệ hơn không có.

## CP4 — Nhánh làm việc phải có trong danh sách trigger

**Vấn đề:** danh sách nhánh khai tay ở `ci.yml:5-13`. Nhánh ngoài danh sách **không có cổng nào**.

**Trạng thái hiện tại:** ba nhánh đã khai, gồm `feature/analysis-and-models` — nhánh đợt này. **Không cần sửa** cho đơn vị này.

**Nếu mở nhánh mới:** phải thêm vào **cả** `on.push.branches` **và** `on.pull_request.branches` cùng lúc với việc tạo nhánh.

## CP5 — Thứ tự bước 5 → 7 → 8 là có lý do, đừng đảo

**Vấn đề:** bộ "nhanh" không hermetic (`TD-09`): một phần test trong `test_dashboard_smoke.py` và `test_main_analyze_stage` gọi `load_config()` nên cần `warehouse/olist.duckdb` và `data/marts/` — hai thư mục bị `.gitignore`. Con số "năm test" mà `team.md` nêu là ước lượng của đợt trước; đọc mã thì chỉ khoảng **ba** test gọi `build_dashboard_outputs` mới thật sự cần dữ liệu, vì `_options` trong `src/dashboard/app.py:65-94` bọc `ConnectionFactory` trong `try/except`.

**Thiết kế:** CI chạy `run --stage all` **trước** bộ nhanh để bù đúng lỗ hổng đó. Đảo thứ tự sẽ làm bộ nhanh đỏ trên máy mới clone, vì lý do không liên quan tới thay đổi.

**Hệ quả cho test mới của đơn vị này:** test phải tự dựng dữ liệu trong `tmp_path` (như năm mô-đun test của đợt trước), **không** dựa vào `warehouse/` — nếu không sẽ làm `TD-09` nặng thêm.

## Điều tài liệu này không thiết kế

Không VPC, không IAM, không container registry, không môi trường staging/production, không giám sát hạ tầng. Không có gì để đặt chúng lên. `monitoring-design.md` và `infrastructure-specification.md` không được sinh cho đơn vị này vì `kind: library` — và đó là câu trả lời đúng, không phải thiếu sót.
