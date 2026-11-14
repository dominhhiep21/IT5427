# CI Configuration — intent `261111-model-feature-improvemen`

## 1. Công cụ và lý do

**GitHub Actions**, đã có trong repo từ trước đợt này (`.github/workflows/ci.yml`). Không đổi công cụ: pipeline đang chạy xanh, đổi CI là thay hạ tầng không có yêu cầu nào.

## 2. Trigger và nhánh

| Hạng mục | Hiện trạng |
|---|---|
| `on.push.branches` | `main`, `feature/update-ui-ux`, `feature/analysis-and-models` |
| `on.pull_request.branches` | cùng ba nhánh |
| Runner | `windows-2022` (ghim image, không dùng `-latest`) |
| Python | 3.13, cache pip |
| Nhánh làm việc của đợt | `feature/analysis-and-models` — **đã** có trong **cả hai** danh sách |

Luật của team (`team.md` `## Way of Working`): mở nhánh mới là việc hai bước — tạo nhánh **và** thêm nhánh vào cả hai danh sách trigger. Đợt này không mở nhánh mới nên không phải sửa trigger.

## 3. Các bước (9 bước, không thêm bước nào)

| # | Bước | Lệnh | Vai trò |
|---|---|---|---|
| 1 | checkout | — | |
| 2 | setup-python | Python 3.13 + cache pip | |
| 3 | cài phụ thuộc | `pip install -r requirements.txt` | 12 gói ghim |
| 4 | lint | `ruff check .` | chặn mã bẩn |
| 5 | format | `ruff format --check` trên **danh sách khai tay 50 mục** | `TD-20` |
| 6 | tầng dữ liệu | `python -X utf8 -m src.pipeline run --stage all` | dựng mart, chạy `QualityGate` + `KpiReconciler` |
| 7 | tầng `stats` | `python -X utf8 -m src.pipeline run --stage stats` | sinh `analysis.json` v3 + `data/models/` |
| 8 | bộ nhanh | `python -X utf8 -m pytest -m "not slow"` | 708 test |
| 9 | cổng phủ | `python -X utf8 -m pytest --cov=src --cov-fail-under=80` | **723 test** (gồm 15 `slow`), phủ **92,71%** |
| 10 | smoke cấu hình | nạp `config/integration-sources.yaml` | chặn cấu hình hỏng |

(Ghi chú: danh sách ở trên đánh số theo thứ tự thực thi; workflow có 9 `step` vì bước cài đặt gộp setup.)

## 4. Thay đổi của đợt này

| Việc | Chi tiết |
|---|---|
| Thêm đường dẫn vào danh sách format | `src/dashboard/prediction_section.py`, `tests/unit/test_u3_prediction_section.py`, `tests/integration/test_u3_floor_end_to_end.py` (47 → **50** mục), khai đồng thời trong `tests/unit/test_ci_config.py::NEW_FILES` |
| Không thêm bước | đợt này không có bước CI mới, không biến môi trường, không secret |
| Không đổi cổng phủ | `--cov-fail-under=80` giữ nguyên, chạy trên **toàn bộ** bộ test |

## 5. Artifact và versioning

| Hạng mục | Quyết định |
|---|---|
| Artifact repository | **không có** — không ECR/CodeArtifact/S3; repo chạy từ mã nguồn |
| Artefact sinh ra | `data/`, `warehouse/`, `logs/`, `data/models/` — bị `.gitignore`, máy khác sinh lại |
| Versioning | commit hash + mốc `CHANGELOG.md` (nay `v0.5.0`); không có git tag |
| Bí mật | không có |

## 6. Thời gian chạy (đo trên máy này)

| Phần | Thời gian |
|---|---|
| Bộ nhanh | ~25 s |
| `--stage all` | ~90 s |
| `--stage stats` | ~30 s |
| Toàn bộ + phủ | ~7 phút |
