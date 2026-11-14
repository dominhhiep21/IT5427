# CI/CD Pipeline — u3-prediction-ui

Nguồn: `.github/workflows/ci.yml`, `tests/unit/test_ci_config.py`, `../../../../memory/team.md` (`## Deployment`, `## Testing Posture`), `../nfr-requirements/tech-stack-decisions.md` (TS3.11–TS3.14), `../nfr-design/security-design.md`.

## 1. Đường ống hiện có, không thay đổi cấu trúc

GitHub Actions, `windows-2022` (ghim image), Python 3.13, cache pip, trigger `push` **và** `pull_request` trên **ba** nhánh `main`, `feature/update-ui-ux`, `feature/analysis-and-models`. Không có bước deploy — đúng mô hình "phát hành = chạy từ mã nguồn".

| ID | Bước | Lệnh | Vai trò |
|---|---|---|---|
| CI3.1 | lint/format | `ruff check .` + `ruff format --check <danh sách khai tay>` | chặn mã bẩn |
| CI3.2 | cổng phủ | `pytest --cov=src --cov-fail-under=80` | NFR3.1 — không hạ |
| CI3.3 | tầng dữ liệu | `run --stage all` rồi `run --stage stats` | sinh mart/báo cáo/mô hình thật trước khi test |
| CI3.4 | bộ nhanh | `pytest -m "not slow"` | phản hồi nhanh |
| CI3.5 | smoke cấu hình | nạp `config/integration-sources.yaml` | chặn cấu hình hỏng |
| CI3.6 | bộ `slow` | nằm trong bước cổng phủ (toàn bộ bộ test) | NFR5.1 — mốc sàn chạy trên báo cáo thật |

## 2. Thay đổi của đơn vị này

| Việc | Chi tiết | Vì sao |
|---|---|---|
| CI3.7 | Thêm **ba** đường dẫn mới vào **cả hai** danh sách khai tay — `ci.yml:35` và `NEW_FILES` của `tests/unit/test_ci_config.py`: `src/dashboard/prediction_section.py`, `tests/unit/test_u3_prediction_section.py`, `tests/integration/test_u3_floor_end_to_end.py` | `ruff format --check` chỉ quét danh sách khai tay (TD-20); thiếu tệp là cổng format không thấy nó |
| CI3.8 | Không thêm bước CI mới, không thêm biến môi trường, không thêm secret | không có hạ tầng mới; bí mật là bề mặt không cần thiết |
| CI3.9 | Giữ nguyên `--cov-fail-under=80` trên **toàn bộ** bộ test | NFR3.1; cấm đặt cờ lên riêng bộ nhanh |
| CI3.10 | Không thêm `continue-on-error` cho bước nào | một bước đỏ phải chặn hợp nhất |

## 3. Lệnh xác nhận của intent (chạy tay, không phải CI)

`powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify_intent.ps1` — bốn bước, dừng ở bước đỏ đầu tiên:

1. `python -X utf8 -m pytest -m "not slow"` — bộ nhanh;
2. `python -X utf8 -m src.pipeline run --stage all` — pipeline thật qua `QualityGate` + `KpiReconciler`;
3. `python -X utf8 -m src.pipeline run --stage stats` — sinh báo cáo **và** tệp mô hình;
4. `pytest --cov=src --cov-fail-under=80` — toàn bộ bộ test.

Bước 5 (mở dashboard) là kiểm bằng mắt, không tự động. Với đơn vị này, bước 5 có thêm một việc: mở tab Kết quả phân tích, bấm Dự đoán một lần với giá trị mặc định.

## 4. Hợp nhất

Một người làm, một nhánh dài hơi (`feature/analysis-and-models`), CI là cổng duy nhất; không review chéo, không pull request bắt buộc. Hợp nhất vào `main` khi CI xanh và lệnh xác nhận xanh.

## 5. Rollback

| Tình huống | Cách lùi |
|---|---|
| Khối dự đoán lỗi sau hợp nhất | `git revert` commit của đơn vị; `analysis_tab.py` trở lại ba mục, callback mới biến mất |
| Tệp mô hình hỏng | xoá `data/models/`, chạy lại `--stage stats` |
| Báo cáo hỏng | xoá `data/reports/analysis.json`, chạy lại `--stage stats` |
| Mart hỏng | xoá `data/`, `warehouse/`, chạy `--stage all` rồi `--stage stats` |

Không có bước deploy nên không có rollback hạ tầng.

## 6. Rủi ro đường ống

| Rủi ro | Ảnh hưởng | Giảm thiểu |
|---|---|---|
| Danh sách format khai tay bị quên cập nhật | tệp mới không được kiểm format | CI3.7 + `test_ci_config.py` canh danh sách |
| Máy CI chậm làm PR3.1–PR3.3 nhiễu | test đỏ giả | ngưỡng rộng 10–150 lần so với đo thật; ghi số đo khi mở ngưỡng |
| `--stage stats` chạy hai lần (CI3.3 + CI3.6) | +~30 s | chấp nhận: cổng phủ cần báo cáo thật cho test `slow` |
| Nhánh mới không có trong danh sách trigger | không có cổng nào | thêm nhánh vào **cả** `push` và `pull_request` cùng lúc (luật `team.md`) |
