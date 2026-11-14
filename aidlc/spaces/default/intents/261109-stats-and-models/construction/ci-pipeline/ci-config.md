# CI Configuration

Nguồn: `.github/workflows/ci.yml`, `tests/unit/test_ci_config.py`, `aidlc/spaces/default/memory/project.md` (`## Way of Working`, `## Deployment`), `../build-and-test/test-results.md`.

## Hiện trạng

Một workflow, một job, `windows-2022`, Python 3.13, cache pip. Trigger `push` và `pull_request` trên **ba** nhánh khai tay: `main`, `feature/update-ui-ux`, `feature/analysis-and-models`.

Thứ tự bước:

1. `ruff check .`
2. `ruff format --check` trên danh sách tệp khai tay
3. `python -X utf8 -m src.pipeline run --stage all` — dựng mart, qua `QualityGate` và `KpiReconciler`
4. `python -X utf8 -m src.pipeline run --stage stats` — sinh báo cáo
5. `pytest -m "not slow"` — bộ nhanh
6. `pytest --cov=src --cov-fail-under=80` — toàn bộ bộ test, cổng phủ
7. smoke nạp `config/integration-sources.yaml`

## Thay đổi đợt này đã đưa vào

| Mục | Trạng thái |
|---|---|
| Nhánh `feature/analysis-and-models` trong cả hai danh sách trigger | có |
| `stats` trong `STAGES` **và** trong `choices` của `--stage` | có, canh bởi `test_pipeline_stages.py` |
| Bước `--stage stats` sau `--stage all`, trước test | có |
| Tệp mới của cả ba đơn vị trong danh sách `ruff format --check` | có, canh bởi `test_ci_config.py` |
| `NEW_FILES` trong `tests/unit/test_ci_config.py` khớp danh sách trên | có, gồm cả tệp test |
| `scikit-learn==1.6.1` ghim trong `requirements.txt` | có |

## Hai cái bẫy của danh sách khai tay

`ruff format --check` dùng danh sách viết tay, nên **hai** danh sách phải cùng đúng: danh sách trong `ci.yml` và tuple `NEW_FILES` trong `test_ci_config.py`. Chỉ thêm tệp nguồn mà quên tệp test thì cổng định dạng không bảo vệ tệp test, mà test canh vẫn xanh.

`STAGES` và `choices` cũng là hai nơi khai cùng một danh sách tầng. Thiếu một nơi thì `run --stage stats` bị argparse từ chối với `invalid choice`, và bước CI mới đỏ ngay lần đầu.

## Điều không có

- Không có bước deploy: không có môi trường để deploy tới.
- Không có ma trận đa hệ điều hành: dự án chạy Windows, và đường dẫn có ký tự tiếng Việt nên nhân bản sang Linux chỉ tạo lỗi giả.
- Không có quét phụ thuộc CVE hay SAST: không có bề mặt mạng, và hai thứ đó thêm thời gian chờ mà không thêm tín hiệu.
- Không có trình duyệt trong CI: repo chỉ có `pytest`; mốc 1280px kiểm bằng mắt.
